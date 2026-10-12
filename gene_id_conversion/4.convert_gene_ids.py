#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# 4.convert_gene_ids.py  —  Cross-assembly gene-ID conversion
# ---------------------------------------------------------------------
# Builds a conversion table from one assembly's gene IDs to another's,
# using two independent evidence sources:
#   1. synteny anchors  (<pair>.lifted.anchors)   — highest priority
#   2. sequence alignment (<pair>.last.filtered)  — fallback, only for
#      genes not already covered by the synteny anchors
#
# Inputs (in the working directory, see --workdir)
#   name                       one assembly name per line
#   <a>.<b>.lifted.anchors     synteny anchors (jcvi)
#   <a>.<b>.last.filtered      best LAST hit per query (BLAST-tab)
#
# Outputs
#   <a>.<b>.gene_conversion.tsv
#     columns: query_gene, hit_gene, method, score, identity, aln_len
#
# Usage
#   python 4.convert_gene_ids.py                 # uses ./name
#   python 4.convert_gene_ids.py --list name --workdir work/jcvi
# =====================================================================
import argparse
import os

import pandas as pd

# Column names of a LAST "BlastTab" alignment file (12 fields; matches
# the output of 3.run_last.sh)
LAST_COLS = [
    "query", "target", "identity", "aln_len", "mismatch", "gapopen",
    "q_start", "q_end", "t_start", "t_end", "evalue", "bit_score",
]


def convert_one(pair):
    """Build the conversion table for a single '<a>.<b>' assembly pair."""
    out_file = f"{pair}.gene_conversion.tsv"
    if os.path.exists(out_file):
        return

    anchors_file = f"{pair}.lifted.anchors"
    if not os.path.exists(anchors_file):
        print(f"[skip] missing {anchors_file}")
        return

    # --- 1. Synteny anchors (primary evidence) ------------------------
    anchors_df = pd.read_csv(
        anchors_file, sep=r"\s+", comment="#", header=None
    )
    anchors_df = anchors_df.iloc[:, :3]
    anchors_df.columns = ["query_gene", "hit_gene", "synteny_score"]
    anchor_result_df = anchors_df.assign(
        method="synteny",
        score=lambda x: x["synteny_score"],
    )
    anchor_result_df["identity"] = "-"
    anchor_result_df["aln_len"] = "-"
    anchor_result_df = anchor_result_df[
        ["query_gene", "hit_gene", "method", "score", "identity", "aln_len"]
    ]

    # --- 2. Alignment fallback for genes without an anchor ------------
    last_file = f"{pair}.last.filtered"
    if os.path.exists(last_file):
        last_df = pd.read_csv(
            last_file, sep=r"\s+", header=None, names=LAST_COLS
        )
        last_df["blast_score"] = last_df["identity"] * last_df["aln_len"]
        last_result_df = (
            last_df
            .sort_values("blast_score", ascending=False)
            .drop_duplicates("query")
            .assign(
                query_gene=lambda x: x["query"],
                hit_gene=lambda x: x["target"],
                method="blast",
                score=lambda x: x["blast_score"],
            )[["query_gene", "hit_gene", "method", "score",
               "identity", "aln_len"]]
        )
        anchor_genes = set(anchor_result_df["query_gene"])
        last_filtered_df = last_result_df[
            ~last_result_df["query_gene"].isin(anchor_genes)
        ]
    else:
        last_filtered_df = anchor_result_df.iloc[0:0]

    # --- 3. Merge (anchors take precedence) ---------------------------
    final_result_df = pd.concat(
        [anchor_result_df, last_filtered_df], ignore_index=True
    )
    final_result_df = (
        final_result_df
        .drop_duplicates("query_gene")
        .set_index("query_gene")
        .sort_index()
    )
    final_result_df.to_csv(out_file, sep="\t")
    print(f"[ok] wrote {out_file} ({final_result_df.shape[0]} genes)")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", default="name",
                    help="file with one assembly name per line (default: name)")
    ap.add_argument("--workdir", default=".",
                    help="directory holding the anchors/last files (default: .)")
    args = ap.parse_args()

    os.chdir(args.workdir)
    names = pd.read_csv(args.list, sep="\t", header=None)[0].tolist()

    for n in names:
        for m in names:
            if n == m:
                continue
            print(f"{n}.{m}")
            convert_one(f"{n}.{m}")


if __name__ == "__main__":
    main()
