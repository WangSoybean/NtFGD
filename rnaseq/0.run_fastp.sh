#!/usr/bin/env bash
# =====================================================================
# 0.run_fastp.sh  —  Read quality control (fastp)
# =====================================================================
# Trim adapters / low-quality bases for paired-end RNA-seq reads before
# alignment with STAR.
#
# Inputs
#   ${RAW_DIR}/${sample}_1.fastq.gz
#   ${RAW_DIR}/${sample}_2.fastq.gz
#   name                 a one-column file listing sample IDs (see below)
#
# Outputs
#   ${CLEAN_DIR}/${sample}.clean_1.fastq.gz
#   ${CLEAN_DIR}/${sample}.clean_2.fastq.gz
#   ${CLEAN_DIR}/${sample}_fastp.html
#   ${CLEAN_DIR}/${sample}_fastp.json
#
# Usage
#   bash 0.run_fastp.sh
#
# The sample list is a plain text file `name` with one sample ID per line,
# e.g.:
#   SRR0000001
#   SRR0000002
# =====================================================================
set -euo pipefail

# ------------------------- user configuration ------------------------
RAW_DIR="${RAW_DIR:-data/raw}"
CLEAN_DIR="${CLEAN_DIR:-work/clean}"
SAMPLE_LIST="${SAMPLE_LIST:-name}"

THREADS="${THREADS:-8}"
QUALIFIED_PHRED="${QUALIFIED_PHRED:-20}"     # fastp -q
UNQUALIFIED_PERCENT="${UNQUALIFIED_PERCENT:-40}"  # fastp -u
N_BASE_LIMIT="${N_BASE_LIMIT:-5}"            # fastp -n
LENGTH_REQUIRED="${LENGTH_REQUIRED:-50}"     # fastp -l
# ---------------------------------------------------------------------

mkdir -p "${CLEAN_DIR}"

while read -r n; do
    [ -z "${n}" ] && continue
    echo "[fastp] ${n}"
    fastp \
        -i "${RAW_DIR}/${n}_1.fastq.gz" \
        -I "${RAW_DIR}/${n}_2.fastq.gz" \
        -o "${CLEAN_DIR}/${n}.clean_1.fastq.gz" \
        -O "${CLEAN_DIR}/${n}.clean_2.fastq.gz" \
        -q "${QUALIFIED_PHRED}" \
        -u "${UNQUALIFIED_PERCENT}" \
        -n "${N_BASE_LIMIT}" \
        -l "${LENGTH_REQUIRED}" \
        -w "${THREADS}" \
        -h "${CLEAN_DIR}/${n}_fastp.html" \
        -j "${CLEAN_DIR}/${n}_fastp.json"
done < "${SAMPLE_LIST}"

# Aggregate all per-sample fastp reports into a single MultiQC report.
if command -v multiqc >/dev/null 2>&1; then
    multiqc "${CLEAN_DIR}" -o "${CLEAN_DIR}/multiqc"
fi

echo "[fastp] done."
