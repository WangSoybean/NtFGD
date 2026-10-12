#!/usr/bin/env bash
# =====================================================================
# run_pipeline.sh  —  End-to-end RNA-seq quantification pipeline
# =====================================================================
# Runs the reference-counting / expression workflow for ONE STAR index
# (i.e. ONE reference assembly). Steps 3-7 below are the downstream
# Python analyses; steps 0-2 (fastp / STAR / featureCounts) are run
# separately because they are computationally heavy.
#
# Expected working directory: a folder that contains
#   * gene_counts.txt                 (featureCounts output)
#   * gene_counts.txt.summary         (featureCounts summary)
#   * <sample>Log.final.out           (STAR logs)
#   * rename                          (sample-id -> label map; see below)
#
# `rename` is a two-column, whitespace-separated file:
#   <bam_prefix>   <label e.g. Tissue#Species>
#
# Usage
#   # 0) heavy steps (optional, run once per index):
#   bash 0.run_fastp.sh
#   bash 1.run_star.sh
#   bash 2.run_featurecounts.sh
#
#   # 1) downstream steps (from inside the featureCounts output dir):
#   cd work/<index>
#   bash /path/to/rnaseq/run_pipeline.sh
# =====================================================================
set -euo pipefail

# ---------------------------------------------------------------------
# Downstream analysis (run inside the folder holding gene_counts.txt)
# ---------------------------------------------------------------------

# 3. Parse STAR Log.final.out -> STAR_mapping_summary.csv
python 3.parse_star_log.py

# 4. Reformat featureCounts *.summary -> gene_counts_for_db.csv
python 4.format_featurecounts_summary.py

# 5. Merge counts + STAR mapping + sample labels -> RNAseq_QC.csv
python 5.merge_summary.py

# 6. Filter low-expression genes, PCA + sample-correlation QC figures
python 6.gene_counts_qc.py

# 7. Emit clean counts, FPKM and TPM matrices
python 7.count_tpm_fpkm.py

echo "[run_pipeline] all steps finished."
