#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# 7.count_tpm_fpkm.py
# ---------------------------------------------------------------------
# Convert the raw featureCounts matrix into gene-level expression
# matrices: clean counts, FPKM and TPM.
#
# Input :  gene_counts.txt   (featureCounts output)
#          rename            (<sample_id>\t<label>)
# Output:  gene_counts.clean.txt
#          gene_fpkm.txt
#          gene_tpm.txt
# =====================================================================
import pandas as pd
import numpy as np

# ===============================
# Step 0. Read the featureCounts result
# ===============================

counts_file = "gene_counts.txt"

df = pd.read_csv(
    counts_file,
    sep="\t",
    comment="#"
)

meta_cols = ["Geneid", "Chr", "Start", "End", "Strand", "Length"]
count_cols = [c for c in df.columns if c not in meta_cols]

counts = df[count_cols].copy()
counts.index = df["Geneid"]

# Strip the trailing bam suffix
counts.columns = counts.columns.str.replace(
    "Aligned.sortedByCoord.out.bam", "", regex=False
)

# Rename samples using the `rename` map
rename_file = "rename"
rename_df = pd.read_csv(
    rename_file,
    sep=r"\s+",
    header=None,
    names=["old", "new"]
)
rename_dict = dict(zip(rename_df["old"], rename_df["new"]))
counts.columns = counts.columns.str.strip()
counts.rename(columns=rename_dict, inplace=True)
unmapped = set(counts.columns) - set(rename_dict.values())
if unmapped:
    print("WARNING: samples not found in the `rename` file:")
    print(unmapped)


gene_length_kb = df["Length"].values / 1000.0

print(f"Counts matrix: {counts.shape}")

# ===============================
# Step 1. Save the clean counts
# ===============================

counts.to_csv("gene_counts.clean.txt", sep="\t")

# ===============================
# Step 2. FPKM
# ===============================

library_size = counts.sum(axis=0)

fpkm = counts.div(gene_length_kb, axis=0)
fpkm = fpkm.div(library_size, axis=1) * 1e6

fpkm_rounded = fpkm.round(2)
fpkm_rounded.to_csv("gene_fpkm.txt", sep="\t")

# ===============================
# Step 3. TPM (recommended)
# ===============================

# RPK (reads per kilobase)
rpk = counts.div(gene_length_kb, axis=0)

# TPM (transcripts per million)
tpm = rpk.div(rpk.sum(axis=0), axis=1) * 1e6
tpm_rounded = tpm.round(2)
tpm_rounded.to_csv("gene_tpm.txt", sep="\t")

print("Finished generating Counts / FPKM / TPM")
