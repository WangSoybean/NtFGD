#!/usr/bin/env bash
# =====================================================================
# 2.run_interproscan.sh  —  Protein domain annotation with InterProScan
# =====================================================================
# Runs InterProScan in protein mode, requesting GO terms, InterPro
# lookups and pathway annotations, and writing TSV output.
#
# Inputs
#   ${PROTEIN_DIR}/*.pep.fasta      one protein FASTA per assembly
#
# Outputs
#   ${OUTPUT_DIR}/<name>.tsv        InterProScan TSV
#
# Usage
#   bash 2.run_interproscan.sh
# =====================================================================
set -euo pipefail

# ------------------------- user configuration ------------------------
IPR_DIR="${IPR_DIR:-software/interproscan-5.76-107.0}"
PROTEIN_DIR="${PROTEIN_DIR:-data/annotation}"
OUTPUT_DIR="${OUTPUT_DIR:-work/interproscan_out}"
THREADS="${THREADS:-22}"
# ---------------------------------------------------------------------

mkdir -p "${OUTPUT_DIR}"

for path in "${PROTEIN_DIR}"/*.pep.fasta; do
    [ -e "${path}" ] || continue
    n="$(basename "${path}")"
    echo "[interproscan] ${n}"
    "${IPR_DIR}/interproscan.sh" \
        -i "${path}" \
        -t p \
        -cpu "${THREADS}" \
        -f tsv \
        -goterms \
        -iprlookup \
        -pa \
        -dp \
        -d "${OUTPUT_DIR}"
done

echo "[interproscan] done."
