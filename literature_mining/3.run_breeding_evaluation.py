#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# 3.run_breeding_evaluation.py  —  LLM-based breeding-relevance curation
# ---------------------------------------------------------------------
# For every record in `meraged_plant_gene_function.tsv`, queries a large
# language model (an OpenAI-style chat endpoint) with the tobacco
# breeding-target prompt and asks it to decide whether the study is
# relevant to tobacco breeding, and to extract the matched targets with
# evidence. Valid results are stored in `breeding_results.db`.
#
# Inputs
#   meraged_plant_gene_function.tsv                       (from step 2)
#   config/Prompt.txt                                     (prompt template)
#   config/StructuredTobaccoBreedingTargetSystem.json     (target list)
#
# Outputs
#   breeding_results.db          curated results (SQLite)
#   logs/progress.tsv            per-PMID status log
#   logs/bad_lines.log           unparsable input lines
#   logs/runtime_error.log       per-record runtime errors
#
# ---------------------------------------------------------------------
# SECURITY — READ THIS FIRST
#   An API key must NOT be committed to the repository. Provide it
#   through the environment instead:
#
#       export BREEDING_API_KEY="<your key>"
#       export BREEDING_API_URL="https://<host>/api/v1/run/<flow-id>"
#
#   (A key was previously hard-coded in this file; if that key is still
#    live it MUST be revoked and rotated — see SECURITY.md.)
# ---------------------------------------------------------------------
import sqlite3
import json
import requests
import uuid
import pandas as pd
from time import sleep
import csv
import re
import os


def build_prompt(prompt_template_path, all_tertiary):
    with open(prompt_template_path, "r", encoding="utf-8") as f:
        template = f.read()
    return template.replace("{{STRUCTURED_SYSTEM}}", "\n".join(all_tertiary))


def load_structured_system(json_path="config/StructuredTobaccoBreedingTargetSystem.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def derive_target_sets(structured_system: dict):
    all_primary = set()
    all_secondary = set()
    all_tertiary = set()
    for primary, pdata in structured_system.items():
        all_primary.add(primary)
        secondary_map = pdata.get("SecondaryTargets", {})
        for secondary, tertiary_list in secondary_map.items():
            all_secondary.add(secondary)
            for t in tertiary_list:
                all_tertiary.add(t)
    return all_primary, all_secondary, all_tertiary


def init_db(db_path="breeding_results.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode=WAL;")
    cur.execute("PRAGMA synchronous=NORMAL;")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS breeding_results (
        pmid TEXT PRIMARY KEY,
        breeding_relevance TEXT,
        target_evidence TEXT,
        biological_logic TEXT,
        overall_confidence TEXT,
        raw_model_output TEXT,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()


def save_result(pmid, result_dict, status, raw_text=None, db_path="breeding_results.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO breeding_results (
        pmid,
        breeding_relevance,
        target_evidence,
        biological_logic,
        overall_confidence,
        raw_model_output,
        status
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        pmid,
        result_dict.get("BreedingRelevance"),
        json.dumps(result_dict.get("TargetEvidence", []), ensure_ascii=False),
        result_dict.get("BiologicalLogic"),
        result_dict.get("OverallConfidence"),
        raw_text,
        status
    ))
    conn.commit()
    conn.close()


def extract_json_from_text(text: str):
    if not text:
        return None
    # ```json ... ```
    m = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1)
    # ``` ... ```
    m = re.search(r"```\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        return m.group(1)
    # otherwise: from the first "{" to the last "}"
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    return None


def validate_result(result: dict):
    br = result.get("BreedingRelevance")
    if br not in ("Yes", "No clear tobacco breeding relevance"):
        return False, "InvalidBreedingRelevance", br
    if "No clear tobacco breeding relevance" in br:
        return True, None, None
    targets = result.get("TargetEvidence")
    if not isinstance(targets, list) or len(targets) == 0:
        return False, "EmptyTargetEvidence", None
    for t in targets:
        target = t.get("Target")
        if target not in ALL_TERTIARY:
            return False, "InvalidTarget", target
        if not t.get("StudySpecies"):
            return False, "MissingStudySpecies", target
        if t.get("TobaccoValidation") not in ("Yes", "Not yet validated in tobacco"):
            return False, "InvalidTobaccoValidation", t.get("TobaccoValidation")
        if t.get("EvidenceType") not in ("Direct", "Indirect", "Suggestive"):
            return False, "InvalidEvidenceType", t.get("EvidenceType")
    return True, None, None


def log_progress(pmid, status, reason_code="", progress_log="logs/progress.tsv"):
    write_header = not os.path.exists(progress_log)
    with open(progress_log, "a", encoding="utf-8") as f:
        if write_header:
            f.write("PMID\tSTATUS\tREASON\n")
        reason_code = str(reason_code).replace("\n", "").replace("\t", "")
        f.write(f"{pmid}\t{status}\t{reason_code}\n")


def run_breeding_evaluation(pmid, prompt, abstract, api_key, url, timeout=3000):
    payload = {
        "input_type": "chat",
        "output_type": "chat",
        "input_value": f"{prompt}\n{abstract}",
        "session_id": str(uuid.uuid4())
    }
    headers = {"x-api-key": api_key}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        raw = response.json()
        model_text = raw["outputs"][0]["outputs"][0]["results"]["message"]["text"].strip()
        # ---- explicitly "no relevance" ----
        if "No clear tobacco breeding relevance" in model_text.strip():
            log_progress(pmid, 'OK', "No clear tobacco breeding relevance")
            print(pmid, "No clear tobacco breeding relevance")
            return
        json_text = extract_json_from_text(model_text)
        if not json_text:
            log_progress(pmid, "JSON_Extraction_Failed", model_text)
            print(pmid, "JSON extraction failed", model_text)
            return
        try:
            result = json.loads(json_text)
        except json.JSONDecodeError:
            log_progress(pmid, "JSON_Parse_Error", json_text)
            print(pmid, "JSON parse error", json_text)
            return
        ok, status, reason = validate_result(result)
        if not ok:
            log_progress(pmid, status, reason)
            print(pmid, status, reason)
            return
        # only genuinely valid results are stored
        save_result(pmid, result, "OK", json_text)
        log_progress(pmid, "OK", json_text)
        print(pmid, "OK", result)
    except requests.RequestException as e:
        log_progress(pmid, "REQUEST_ERROR", e)
        print(pmid, f"REQUEST_ERROR: {e}")


def load_processed_pmid_status(progress_log):
    pmid_status = {}
    if not os.path.exists(progress_log):
        return pmid_status
    with open(progress_log, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i == 0 and line.lower().startswith("pmid"):
                continue
            parts = line.strip().split("\t")
            if len(parts) < 2:
                continue
            pmid, status = parts[0], parts[1]
            pmid_status[pmid] = status
    return pmid_status


FileName = 'meraged_plant_gene_function.tsv'
progress_log = "logs/progress.tsv"
BAD_LINE_LOG = "logs/bad_lines.log"

# API credentials are read from the environment (never hard-code them).
API_KEY = os.environ.get("BREEDING_API_KEY")
URL = os.environ.get("BREEDING_API_URL")
if not API_KEY or not URL:
    raise SystemExit(
        "BREEDING_API_KEY and BREEDING_API_URL must be set in the environment.\n"
        "  export BREEDING_API_KEY='<your key>'\n"
        "  export BREEDING_API_URL='https://<host>/api/v1/run/<flow-id>'"
    )

STRUCTURED_SYSTEM = load_structured_system()
ALL_PRIMARY, ALL_SECONDARY, ALL_TERTIARY = derive_target_sets(STRUCTURED_SYSTEM)
Prompt = build_prompt(
    "config/Prompt.txt",
    ALL_TERTIARY
)


def main():
    os.makedirs("logs", exist_ok=True)
    init_db()
    processed_pmids = load_processed_pmid_status(progress_log)

    def bad_line_handler(bad_line):
        with open(BAD_LINE_LOG, "a", encoding="utf-8") as f:
            f.write("\t".join(bad_line) + "\n")
        return None  # skip the offending line

    chunks = pd.read_csv(
        FileName,
        sep="\t",
        chunksize=1000,          # 1000 rows at a time
        dtype=str,
        engine="python",
        quoting=csv.QUOTE_NONE,
        on_bad_lines=bad_line_handler
    )
    for chunk in chunks:
        for _, row in chunk.iterrows():
            try:
                pmid = str(row["PMID"]).strip()
                if not pmid:
                    continue
                # re-run only REQUEST_ERROR records (if desired):
                # if pmid in pmid_status and pmid_status[pmid] != "REQUEST_ERROR":
                if pmid in processed_pmids:
                    continue
                run_breeding_evaluation(
                    pmid=pmid,
                    prompt=Prompt,
                    abstract=f"Title:{row['Title']}\nAbstract:{row['Abstract']}",
                    api_key=API_KEY,
                    url=URL
                )
                sleep(0.3)
            except Exception as e:
                # a single bad record must not abort the whole run
                with open("logs/runtime_error.log", "a", encoding="utf-8") as f:
                    f.write(f"{pmid}\t{e}\n")


if __name__ == "__main__":
    main()
