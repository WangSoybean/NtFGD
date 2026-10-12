#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# sgrna_pipeline.py  —  sgRNA design via GuideScan
# ---------------------------------------------------------------------
# End-to-end sgRNA design for a set of target sequences:
#   1. generate candidate kmers (generate_kmers.py)
#   2. filter candidates (GC content, homopolymers, repeats, seed GC)
#   3. enumerate off-targets (guidescan enumerate)
#   4. summarise off-target counts per sgRNA
#   5. emit a JSON annotation file + a CSV table
#
# Usage
#   python sgrna_pipeline.py <input.fasta> <genome.index> <prefix> <pam> <mismatch>
#   e.g.
#   python sgrna_pipeline.py Input.fasta genome.fasta.index sgRNA NGG 1
#
# Configure the tool paths in the CONFIG block below.
# =====================================================================
import os
import sys
import csv
import json
import re
import subprocess

# ================== CONFIG: tool paths ==================
GUIDESCAN_BIN = os.path.expanduser("~/NtExpDB/NtExpAtlas/guidescan/bin/guidescan")
GENERATE_KMERS = os.path.expanduser("~/NtExpDB/NtExpAtlas/guidescan/scripts/generate_kmers.py")


# ================== Step 1: sgRNA filtering ==================
poly_pattern = re.compile(r'(A{4,}|T{4,}|C{4,}|G{4,})')
dinuc_pattern = re.compile(r'((AT|TA|CG|GC){4,})')
tttt_pattern = re.compile(r'T{4}')


def gc_content(seq):
    return sum(1 for c in seq if c in "GC") / len(seq)


def seed_gc_ok(seq):
    seed = seq[-12:]
    gc = (seed.count('G') + seed.count('C')) / 12
    return 0.2 <= gc <= 0.8


def pass_filter(seq):
    seq = seq.upper()
    if len(seq) != 20:
        return False
    if 'N' in seq:
        return False
    if not (0.2 <= gc_content(seq) <= 0.8):
        return False
    if poly_pattern.search(seq):
        return False
    if dinuc_pattern.search(seq):
        return False
    if tttt_pattern.search(seq):
        return False
    if not seed_gc_ok(seq):
        return False
    return True


def filter_sgrna(infile, outfile):
    with open(infile) as f, open(outfile, "w") as out:
        out.write("id,sequence,pam,chromosome,position,sense\n")
        next(f)
        for line in f:
            seq = line.strip().split(',')[1]
            if pass_filter(seq):
                out.write(line)


# ================== Step 2: off-target counting ==================
def safe_int(x):
    try:
        return int(x)
    except Exception:
        return 0


def summarize_offtarget(infile, outfile):
    current_id = None
    mm0 = mm1 = bulge = 0
    current_seq = ""
    spec = 0

    with open(infile) as f, open(outfile, "w") as out:
        next(f)
        out.write("id,sgRNA,mm0_count,mm1_count,bulge_count,specificity\n")

        for line in f:
            parts = line.strip().split(',')
            if "NA" in parts:
                continue
            if "specificity" in parts:
                continue

            sg_id = parts[0]
            sgRNA = parts[1]
            dist = safe_int(parts[5])
            rna_b = safe_int(parts[7])
            dna_b = safe_int(parts[8])
            spec = parts[9]

            if current_id is None:
                current_id = sg_id
                current_seq = sgRNA
                current_spec = spec

            if sg_id != current_id:
                out.write(f"{current_id},{current_seq},{mm0},{mm1},{bulge},{current_spec}\n")
                current_id = sg_id
                current_seq = sgRNA
                current_spec = spec
                mm0 = mm1 = bulge = 0

            if dist == 0:
                mm0 += 1
            elif dist == 1:
                mm1 += 1

            if rna_b > 0 or dna_b > 0:
                bulge += 1

        if current_id:
            out.write(f"{current_id},{current_seq},{mm0},{mm1},{bulge},{spec}\n")


# ================== Step 3: FASTA reading ==================
def read_fasta_multi(fasta):
    seqs = {}
    current = None
    with open(fasta) as f:
        for line in f:
            if line.startswith(">"):
                current = line[1:].split()[0]
                seqs[current] = ""
            else:
                seqs[current] += line.strip()
    return seqs


def parse_id(s):
    gene = s.replace("sgRNA", "").split(":")[0]
    pos = int(s.split(":")[1])
    strand = s.split(":")[2]
    return gene, pos, strand


# ================== Step 4: JSON + CSV ==================
def build_outputs(fasta, sgrna_csv, out_json, out_csv, pam):
    seqs = read_fasta_multi(fasta)
    result = {}
    table = []

    with open(sgrna_csv) as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader):
            sg_id = row["id"]
            seq = row["sgRNA"]

            gene, pos, strand = parse_id(sg_id)
            if gene not in seqs:
                continue

            if gene not in result:
                result[gene] = {"gDNA": seqs[gene], "annotations": []}

            if strand == '+':
                start = pos - 1
                end = start + len(seq.replace(pam, ""))
            else:
                start = pos - 1 + 3
                end = start + len(seq.replace(pam, ""))

            result[gene]["annotations"].append({
                "type": "sgRNA",
                "start": start,
                "end": end,
                "strand": 1 if strand == "+" else -1,
                "id": f"{gene}_{i}",
                "mm0": row["mm0_count"],
                "seq": seq
            })

            table.append({
                "gene": gene,
                "id": f"{gene}_{i}",
                "sgRNA": seq,
                "start": start,
                "end": end,
                "strand": strand,
                "mm0": row["mm0_count"],
                "mm1": row["mm1_count"],
                "bulge": row["bulge_count"],
                "specificity": row["specificity"]
            })

    json.dump(result, open(out_json, "w"), indent=2)

    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=table[0].keys())
        writer.writeheader()
        writer.writerows(table)


# ================== Main pipeline ==================
def run_pipeline(fasta, genome_index, prefix, pam, mismatch):

    print("[step 1] generate kmers")
    subprocess.run(
        f"python {GENERATE_KMERS} --pam {pam} --kmer-length 20 --prefix {prefix} {fasta} > {prefix}.csv",
        shell=True, check=True
    )

    print("[step 2] filter sgRNA")
    filter_sgrna(f"{prefix}.csv", f"{prefix}.filtered.csv")

    print("[step 3] guidescan enumerate")
    subprocess.run(
        f"{GUIDESCAN_BIN} enumerate -m {mismatch} --max-off-targets 10 "
        f"--mode complete --format csv -n 6 "
        f"--output {prefix}.filtered.csv.enumerate {genome_index} "
        f"--kmers-file {prefix}.filtered.csv",
        shell=True, check=True
    )

    print("[step 4] summarize")
    summarize_offtarget(
        f"{prefix}.filtered.csv.enumerate",
        f"{prefix}.final.csv"
    )

    print("[step 5] build outputs")
    build_outputs(
        fasta,
        f"{prefix}.final.csv",
        f"{prefix}.json",
        f"{prefix}.table.csv",
        pam
    )

    print("ALL DONE")


# ================== CLI ==================
if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python sgrna_pipeline.py input.fasta genome.index prefix pam mismatch")
        sys.exit(1)

    run_pipeline(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
