#!/usr/bin/env python3
# =====================================================================
# 4.format_featurecounts_summary.py
# ---------------------------------------------------------------------
# Reshape the featureCounts `<counts>.txt.summary` table so that samples
# are rows and the assignment categories are columns, then write it to
# `gene_counts_for_db.csv` (used by step 5 and by the web database).
#
# Input :  gene_counts.txt.summary
# Output:  gene_counts_for_db.csv
# =====================================================================
import pandas as pd

# ===== 1. Read the featureCounts summary =====
summary_file = "gene_counts.txt.summary"

df = pd.read_csv(
    summary_file,
    sep=r"\s+",
    index_col=0
)

# ===== 2. Transpose so that samples are rows =====
df_t = df.T
df_t.index.name = "Sample"

# ===== 3. Rename the categories we care about =====
rename_map = {
    "Unassigned_MultiMapping": "MultiMapping",
    "Unassigned_NoFeatures": "NoFeatures",
    "Unassigned_Ambiguity": "Ambiguity"
}
df_t.rename(columns=rename_map, inplace=True)

# ===== 4. Keep only the key columns =====
keep_cols = [
    "Assigned",
    "MultiMapping",
    "NoFeatures",
    "Ambiguity"
]
df_t = df_t[keep_cols]

# ===== 5. Total reads per sample =====
df_t["Total"] = df_t.sum(axis=1)

# ===== 6. Fraction of reads assigned to genes =====
df_t["AssignedRate"] = (df_t["Assigned"] / df_t["Total"]).round(4)

# ===== 7. Reset index so the table can be loaded into a database =====
df_t.reset_index(inplace=True)
df_t["Sample"] = [
    x.replace("Aligned.sortedByCoord.out.bam", "") for x in df_t["Sample"]
]

# ===== 8. Write output =====
df_t.to_csv("gene_counts_for_db.csv", index=False)

print("OK: wrote gene_counts_for_db.csv")
