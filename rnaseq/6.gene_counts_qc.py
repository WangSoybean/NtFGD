#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# 6.gene_counts_qc.py
# ---------------------------------------------------------------------
# Sample-level quality control for the RNA-seq expression matrix:
#   1. filter low-expression genes (CPM >= 1 in >= 1 sample)
#   2. log2(CPM + 1) transformation
#   3. PCA of samples
#   4. Pearson-correlation clustered heatmap
#
# Input :  gene_counts.txt   (featureCounts output)
#          rename            (<sample_id>\t<label>)
# Output:  QC_PCA_logCPM.png
#          QC_Correlation_Clustermap_logCPM.png
# =====================================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA

# ===============================
# Step 0. Read the featureCounts result
# ===============================

counts_file = "gene_counts.txt"

# Skip comment lines (starting with "#")
df = pd.read_csv(
    counts_file,
    sep="\t",
    comment="#"
)

# Metadata columns
meta_cols = ["Geneid", "Chr", "Start", "End", "Strand", "Length"]

# Expression matrix
count_df = df.drop(columns=meta_cols)
count_df.index = df["Geneid"]

# Strip the trailing bam suffix that featureCounts appends to column names
count_df.columns = count_df.columns.str.replace(
    "Aligned.sortedByCoord.out.bam", "", regex=False
)

print(f"Raw count matrix shape: {count_df.shape}")

# Rename samples using the `rename` map
rename_file = "rename"
rename_df = pd.read_csv(
    rename_file,
    sep=r"\s+",
    header=None,
    names=["old", "new"]
)
rename_dict = dict(zip(rename_df["old"], rename_df["new"]))
count_df.columns = count_df.columns.str.strip()
count_df.rename(columns=rename_dict, inplace=True)
unmapped = set(count_df.columns) - set(rename_dict.values())
if unmapped:
    print("WARNING: samples not found in the `rename` file:")
    print(unmapped)


# ===============================
# Step 1. Filter low-expression genes
# ===============================
# Criterion: CPM >= 1 in at least one sample

library_sizes = count_df.sum(axis=0)              # library size per sample
cpm = count_df.div(library_sizes, axis=1) * 1e6   # CPM

cpm_filtered = cpm[(cpm >= 1).sum(axis=1) >= 1]

print(f"Genes after filtering: {cpm_filtered.shape[0]}")

# ===============================
# Step 2. log2(CPM + 1)
# ===============================

log_cpm = np.log2(cpm_filtered + 1)

# ===============================
# Step 3. PCA (core sample QC)
# ===============================

pca = PCA(n_components=2)
pca_result = pca.fit_transform(log_cpm.T)

pca_df = pd.DataFrame(
    pca_result,
    columns=["PC1", "PC2"],
    index=log_cpm.columns
)

explained = pca.explained_variance_ratio_ * 100

plt.figure(figsize=(7, 6))
pca_df["Tissue"] = pca_df.index.str.split("-").str[0]
sns.scatterplot(
    x="PC1",
    y="PC2",
    hue="Tissue",
    data=pca_df,
    s=80
)

for sample in pca_df.index:
    plt.text(
        pca_df.loc[sample, "PC1"],
        pca_df.loc[sample, "PC2"],
        sample,
        fontsize=8
    )

plt.xlabel(f"PC1 ({explained[0]:.1f}%)")
plt.ylabel(f"PC2 ({explained[1]:.1f}%)")
plt.title("PCA of RNA-seq Samples (log2 CPM)")
plt.tight_layout()
plt.savefig("QC_PCA_logCPM.png", dpi=300)
plt.show()

# ===============================
# Step 4. Sample correlation + hierarchical-clustering heatmap
# ===============================

# Pearson correlation
corr_matrix = log_cpm.corr(method="pearson")

sns.set(font_scale=0.8)
sns.set_style("white")

g = sns.clustermap(
    corr_matrix,
    metric="correlation",   # key: 1 - Pearson
    method="average",
    cmap="coolwarm",
    figsize=(10, 9),
    cbar_kws={"shrink": 0.75},
    linewidths=0.3
)

g.fig.suptitle(
    "Sample Clustering Based on Pearson Correlation (log2 CPM)",
    fontsize=14
)
plt.savefig("QC_Correlation_Clustermap_logCPM.png", dpi=300)
plt.show()

print("QC analysis finished.")
