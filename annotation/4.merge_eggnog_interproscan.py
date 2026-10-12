#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# 4.merge_eggnog_interproscan.py
# ---------------------------------------------------------------------
# Merge the eggNOG-mapper and InterProScan outputs of one protein set
# into a single per-gene functional-annotation table.
#
# eggNOG-mapper contributes: seed ortholog, COG category, description,
# preferred gene name, GO terms, EC numbers, KEGG KO/pathway and PFAMs.
# InterProScan contributes: InterPro domains, GO terms and pathways.
# GO terms from the two sources are combined and de-duplicated.
#
# Usage
#   python 4.merge_eggnog_interproscan.py \
#       -e work/emapper_out/<name>.emapper \
#       -i work/interproscan_out/<name>.tsv \
#       -o <name>.annotation
#
# Arguments
#   -e / --eggnog       eggNOG-mapper output prefix or *.emapper.annotations
#   -i / --interproscan InterProScan TSV (from 2.run_interproscan.sh)
#   -o / --output       output annotation table (TSV)
#
# Output columns
#   gene_id, seed_ortholog, evalue, score, eggNOG_OGs, max_annot_lvl,
#   COG_category, Description, Preferred_name, GOs, EC, KEGG_ko,
#   KEGG_Pathway, KEGG_Module, KEGG_Reaction, KEGG_rclass, BRITE,
#   KEGG_TC, CAZy, BiGG_Reaction, PFAMs,
#   ipr_acc, ipr_domains, ipr_pathways, ipr_go, GO_combined
# =====================================================================
import argparse
import os

import pandas as pd

# Column names of the InterProScan TSV (v5.x, 15 fields)
IPR_COLS = [
    "protein_accession", "md5", "seq_length", "analysis",
    "signature_accession", "signature_description", "start", "stop",
    "score", "status", "date", "interpro_accession",
    "interpro_description", "go_annotation", "pathway_annotation",
]

# Columns that should be aggregated per gene with ";" separators
IPR_AGG = {
    "interpro_accession": "ipr_acc",
    "interpro_description": "ipr_domains",
    "pathway_annotation": "ipr_pathways",
    "go_annotation": "ipr_go",
}


def find_emapper_file(prefix):
    """Return the *.emapper.annotations path for a given prefix/path."""
    if prefix.endswith(".annotations"):
        return prefix
    if os.path.exists(prefix + ".annotations"):
        return prefix + ".annotations"
    if os.path.exists(prefix):
        return prefix
    raise FileNotFoundError(
        f"Cannot locate eggNOG annotations for '{prefix}' "
        f"(tried '{prefix}.annotations')"
    )


def read_emapper(path):
    """Read an eggNOG-mapper *.emapper.annotations table."""
    with open(path) as f:
        for line in f:
            if line.startswith("#query"):
                header = line.lstrip("#").strip().split("\t")
                break
        else:
            raise ValueError(f"No '#query' header found in {path}")
    df = pd.read_csv(path, sep="\t", comment="#", names=header,
                     dtype=str).fillna("")
    return df.rename(columns={"query": "gene_id"})


def _join_unique(series):
    vals = set()
    for v in series:
        if isinstance(v, str):
            vals.update(x for x in v.split(";") if x and x != "-")
    return ";".join(sorted(vals))


def read_interproscan(path):
    """Read an InterProScan TSV and aggregate it per gene."""
    df = pd.read_csv(path, sep="\t", header=None, names=IPR_COLS,
                     dtype=str).fillna("")
    grouped = (
        df.groupby("protein_accession")
          .agg(**{dst: pd.NamedAgg(column=src, aggfunc=_join_unique)
                  for src, dst in IPR_AGG.items()})
          .reset_index()
          .rename(columns={"protein_accession": "gene_id"})
    )
    return grouped


def merge(emapper_prefix, ipr_path):
    emapper = read_emapper(find_emapper_file(emapper_prefix))
    ipr = read_interproscan(ipr_path)

    merged = pd.merge(emapper, ipr, on="gene_id", how="outer")

    # Combine GO terms from the two sources.
    go_sources = [c for c in ("GOs", "ipr_go") if c in merged.columns]
    if go_sources:
        merged["GO_combined"] = merged[go_sources].apply(_join_unique, axis=1)

    return merged.sort_values("gene_id").reset_index(drop=True)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-e", "--eggnog", required=True,
                    help="eggNOG-mapper output prefix or *.emapper.annotations")
    ap.add_argument("-i", "--interproscan", required=True,
                    help="InterProScan TSV file")
    ap.add_argument("-o", "--output", required=True,
                    help="output annotation table (TSV)")
    args = ap.parse_args()

    merged = merge(args.eggnog, args.interproscan)
    merged.to_csv(args.output, sep="\t", index=False)
    print(f"OK: wrote {args.output} ({merged.shape[0]} genes)")


if __name__ == "__main__":
    main()
