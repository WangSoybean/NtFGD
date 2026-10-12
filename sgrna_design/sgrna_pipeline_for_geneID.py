#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# sgrna_pipeline_for_geneID.py  —  sgRNA JSON for the web database
# ---------------------------------------------------------------------
# For a gene-centred input table (Input.xls), query the pre-computed
# sgRNA database and assemble the per-gene JSON (gDNA sequence, CDS and
# sgRNA annotations) consumed by the website.
#
# Inputs
#   Input.xls          per-gene table with columns:
#                        Chr, Gene, UpStart, EndStart, SeqName, CDSInfo
#   Input.fasta        target sequences (keyed by SeqName)
#   <GenomeName>.db    SQLite database with a `sgrna` table
#
# Outputs
#   sgRNA.json         per-gene annotations (JSON)
#   sgRNA.table.csv    flat sgRNA table
#
# Usage
#   python sgrna_pipeline_for_geneID.py --GenomeName <assembly>
# =====================================================================
import pandas as pd
import sqlite3
import json
import ast
import argparse


INPUT_FILE = "Input.xls"
OUTPUT_JSON = "sgRNA.json"
INPUT_FASTA = "Input.fasta"


def query_sgrna(conn, chrom, start, end):
    """Return the sgRNAs located within [start, end] on `chrom`."""
    sql = """
    SELECT id, sgRNA, mm0_count, mm1_count, specificity, Chr, Pos, direction
    FROM sgrna
    WHERE Chr = ?
      AND Pos BETWEEN ? AND ?
    ORDER BY Pos
    """
    return pd.read_sql_query(sql, conn, params=(chrom, start, end))


# ================== FASTA reading ==================
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


def build_json(genome_name):
    db_path = "../{}.db".format(genome_name)
    seqs = read_fasta_multi(INPUT_FASTA)
    df = pd.read_csv(INPUT_FILE, sep='\t')
    conn = sqlite3.connect(db_path)
    results = {}
    all_table = []

    for _, row in df.iterrows():
        chrom = row['Chr']
        gene = row['Gene']
        up = int(row['UpStart'])
        down = int(row['EndStart'])
        seq_name = row['SeqName']

        # ===== query sgRNAs =====
        sgrna_df = query_sgrna(conn, chrom, up, down)

        # ===== parse CDS =====
        cds_list = ast.literal_eval(row['CDSInfo'])
        annotations = []
        table = []

        # ===== CDS annotations =====
        for cds in cds_list:
            cds_chr, cds_start, cds_end, cds_direction = cds
            annotations.append({
                "type": "CDS",
                "start": cds_start - up - 1,
                "end": cds_end - up,
                "strand": 1 if cds_direction == '+' else -1,
                "id": '{}-CDS'.format(gene),
                "mm0": '0',
                "specificity": 1,
                "seq": 'seq',
            })

        # ===== sgRNA annotations =====
        for _, sg in sgrna_df.iterrows():
            pos = int(sg['Pos'])
            seq = sg['sgRNA']
            strand = 1 if sg['direction'] == '+' else -1
            if strand == 1:
                sgrna_start = pos - up - 1
            else:
                sgrna_start = pos - up + 2
            sgrna_end = sgrna_start + 20

            annotations.append({
                "type": "sgRNA",
                "start": sgrna_start,
                "end": sgrna_end,
                "strand": strand,
                "id": sg['id'],
                "mm0": str(sg['mm0_count']),
                "specificity": sg['specificity'],
                "seq": seq,
            })

            table.append({
                "gene": gene,
                "id": sg['id'],
                "sgRNA": seq,
                "start": sgrna_start,
                "end": sgrna_end,
                "strand": strand,
                "mm0": sg['mm0_count'],
                "mm1": sg['mm1_count'],
                "bulge": 0,
                "specificity": sg['specificity']
            })

        # ===== gDNA =====
        gDNA = seqs[seq_name]
        results[gene] = {
            "gDNA": gDNA,
            "annotations": annotations,
            "mismatches": []
        }
        all_table.extend(table)

    if all_table:
        pd.DataFrame(all_table).to_csv("sgRNA.table.csv", index=False)
    else:
        print("WARNING: sgRNA table is empty")
    conn.close()

    with open(OUTPUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)

    print("OK: wrote {}".format(OUTPUT_JSON))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate sgRNA JSON from genome database"
    )
    parser.add_argument("--GenomeName", required=True,
                        help="Genome database name (without .db suffix)")
    args = parser.parse_args()
    build_json(args.GenomeName)
