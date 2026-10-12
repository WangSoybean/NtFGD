#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# 4.build_tobacco_breeding_db.py  —  Assemble the target knowledge base
# ---------------------------------------------------------------------
# Joins the LLM curation results (breeding_results.db, step 3) with the
# literature metadata (literature.db) and flattens the per-paper target
# evidence into a single `target_knowledge` table, then computes
# per-target paper counts by confidence level.
#
# Inputs
#   breeding_results.db        curated results (from step 3)
#   literature.db              literature metadata, table
#                              `literature_metadata` (pmid, doi, title,
#                              abstract, pub_date, journal)
#
# Outputs
#   tobacco_breeding_knowledge.db   target_knowledge table + indexes
#   target_statistics.json          per-target counts
#                                   {total, High, Moderate, Low}
#
# Usage
#   python 4.build_tobacco_breeding_db.py
# =====================================================================
import sqlite3
import json
from collections import defaultdict


BREEDING_DB = "breeding_results.db"
LITERATURE_DB = "literature.db"
OUTPUT_DB = "tobacco_breeding_knowledge.db"
OUTPUT_JSON = "target_statistics.json"


def init_output_db(conn):
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS target_knowledge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        target TEXT NOT NULL,

        pmid TEXT,
        doi TEXT,
        pub_date TEXT,
        journal TEXT,
        title TEXT,
        abstract TEXT,

        gene_names TEXT,
        study_species TEXT,
        tobacco_validation TEXT,
        evidence_type TEXT,
        supporting_sentences TEXT,

        overall_confidence TEXT,
        biological_logic TEXT
    )
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_target ON target_knowledge(target)")
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_target_confidence
        ON target_knowledge(target, overall_confidence)
    """)

    conn.commit()


def build_knowledge_base():

    # ===============================
    # Statistics structure (deduplicate papers)
    # ===============================
    target_stats = defaultdict(lambda: {
        "pmids": set(),
        "High": set(),
        "Moderate": set(),
        "Low": set()
    })

    # connect to the breeding database
    conn = sqlite3.connect(BREEDING_DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # attach the literature database
    cur.execute(f"ATTACH DATABASE '{LITERATURE_DB}' AS lit")

    # output database
    out_conn = sqlite3.connect(OUTPUT_DB)
    init_output_db(out_conn)
    out_cur = out_conn.cursor()

    cur.execute("""
        SELECT
            b.pmid,
            b.target_evidence,
            b.biological_logic,
            b.overall_confidence,

            l.doi,
            l.title,
            l.abstract,
            l.pub_date,
            l.journal
        FROM breeding_results b
        LEFT JOIN lit.literature_metadata l
        ON b.pmid = l.pmid
        WHERE b.status = 'OK' OR b.status IS NULL
    """)

    rows = cur.fetchall()
    inserted = 0

    for row in rows:

        pmid = row["pmid"]
        confidence = row["overall_confidence"]

        try:
            target_evidence_list = json.loads(row["target_evidence"])
        except Exception as e:
            print(f"[WARN] PMID {pmid} JSON parse failed: {e}")
            continue

        for ev in target_evidence_list:

            target_name = ev.get("Target")

            if not target_name:
                continue

            # ===============================
            # Insert into the database
            # ===============================
            out_cur.execute("""
                INSERT INTO target_knowledge (
                    target,
                    pmid, doi, pub_date, journal, title, abstract,
                    gene_names, study_species, tobacco_validation,
                    evidence_type, supporting_sentences,
                    overall_confidence, biological_logic
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                target_name,
                pmid,
                row["doi"],
                row["pub_date"],
                row["journal"],
                row["title"],
                row["abstract"],

                json.dumps(ev.get("GeneName", []), ensure_ascii=False),
                ev.get("StudySpecies"),
                ev.get("TobaccoValidation"),
                ev.get("EvidenceType"),
                json.dumps(ev.get("SupportingSentences", []), ensure_ascii=False),

                confidence,
                row["biological_logic"]
            ))

            inserted += 1

            # ===============================
            # Statistics (sets keep each paper unique)
            # ===============================
            target_stats[target_name]["pmids"].add(pmid)

            if confidence in ["High", "Moderate", "Low"]:
                target_stats[target_name][confidence].add(pmid)

    out_conn.commit()

    conn.close()
    out_conn.close()

    print(f"Tobacco breeding knowledge base built: {inserted} records")

    # ===============================
    # Write the statistics JSON
    # ===============================
    final_stats = {}

    for target, data in target_stats.items():
        final_stats[target] = {
            "total": len(data["pmids"]),
            "High": len(data["High"]),
            "Moderate": len(data["Moderate"]),
            "Low": len(data["Low"])
        }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(final_stats, f, indent=2, ensure_ascii=False)

    print(f"Target statistics JSON generated: {OUTPUT_JSON}")


if __name__ == "__main__":
    build_knowledge_base()
