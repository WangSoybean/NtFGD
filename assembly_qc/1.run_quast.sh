#!/usr/bin/env bash
# =====================================================================
# 1.run_quast.sh  —  Assembly contiguity statistics (QUAST)
# =====================================================================
# Runs QUAST (large-genome mode) on every genome FASTA and writes one
# report folder per assembly.
#
# Inputs
#   ${GENOME_DIR}/*.genome.fasta
#
# Outputs
#   ${OUTPUT_DIR}/<basename>        QUAST report (report.tsv, report.txt, ...)
#
# Usage
#   bash 1.run_quast.sh
# =====================================================================
set -euo pipefail

# ------------------------- user configuration ------------------------
GENOME_DIR="${GENOME_DIR:-data/annotation}"
OUTPUT_DIR="${OUTPUT_DIR:-results/quast}"
QUAST_BIN="${QUAST_BIN:-quast.py}"
# ---------------------------------------------------------------------

mkdir -p "${OUTPUT_DIR}"

for n in "${GENOME_DIR}"/*.genome.fasta; do
    [ -e "${n}" ] || continue
    m="$(basename "${n}")"
    echo "[quast] ${m}"
    "${QUAST_BIN}" "${n}" -o "${OUTPUT_DIR}/${m}" --large
done

# Aggregate QUAST reports together with the fastp/STAR QC reports.
if command -v multiqc >/dev/null 2>&1; then
    multiqc .
fi

echo "[quast] done."
