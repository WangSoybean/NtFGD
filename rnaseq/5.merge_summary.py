#!/usr/bin/env python3
# =====================================================================
# 5.merge_summary.py
# ---------------------------------------------------------------------
# Merge the per-sample gene-counting table, the STAR mapping summary and
# the sample label file into a single QC table used by the web database.
#
# Input :  gene_counts_for_db.csv     (from step 4)
#          STAR_mapping_summary.csv   (from step 3)
#          rename                     (<sample_id>\t<Tissue#Species>)
# Output:  RNAseq_QC.csv
# =====================================================================
import pandas as pd

# 1. Read the three tables
counts_df = pd.read_csv("gene_counts_for_db.csv")
star_df = pd.read_csv("STAR_mapping_summary.csv")
name = pd.read_csv("rename", sep="\t", header=None)
name.columns = ["Sample", "Info"]
name["Tissue"] = [x.split("#")[0] for x in list(name["Info"])]
name["Species"] = [x.split("#")[1] for x in list(name["Info"])]

# 2. Merge on Sample (inner joins)
merged = pd.merge(counts_df, star_df, on="Sample", how="inner")
merged = pd.merge(merged, name, on="Sample", how="inner")

# 3. Columns shown on the website
display_cols = [
    "Sample",
    "Tissue",
    "Species",
    # Sequencing / alignment quality
    "Input_reads",
    "Uniquely_mapped_reads",
    "Uniquely_mapping_rate",
    "Multi_mapping_rate",
    # Gene-quantification quality
    "Assigned",
    "AssignedRate",
    "MultiMapping",
    "NoFeatures",
    "Ambiguity"
]

display_df = merged[display_cols]

# 4. Uniform rounding for the rate columns (front-end friendly)
rate_cols = ["Uniquely_mapping_rate", "Multi_mapping_rate", "AssignedRate"]
display_df[rate_cols] = display_df[rate_cols].round(2)

# 5. Save for the database / API
display_df.to_csv("RNAseq_QC.csv", index=False)
print(display_df.head())
