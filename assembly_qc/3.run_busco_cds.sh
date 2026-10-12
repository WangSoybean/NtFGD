#!/usr/bin/env bash
# =====================================================================
# 3.run_busco_cds.sh  —  Transcriptome completeness (BUSCO, CDS mode)
# =====================================================================
# Assesses the completeness of each predicted CDS set against two BUSCO
# lineages (Embryophyta and eudicots) in transcriptome mode, offline.
#
# Inputs
#   ${CDS_DIR}/*.cds.fasta
#   ${BUSCO_DB}/embryophyta_odb12
#   ${BUSCO_DB}/eudicotyledons_odb12
#
# Outputs
#   ${OUTPUT_DIR}/tobacco_cds_embryophyta/<name>
#   ${OUTPUT_DIR}/tobacco_cds_eudicotyledons/<name>
#
# Usage
#   bash 3.run_busco_cds.sh
# =====================================================================
set -euo pipefail

# ------------------------- user configuration ------------------------
CDS_DIR="${CDS_DIR:-data/annotation}"
OUTPUT_DIR="${OUTPUT_DIR:-results/busco}"
BUSCO_DB="${BUSCO_DB:-software/busco_db}"
BUSCO_BIN="${BUSCO_BIN:-busco}"
THREADS="${THREADS:-22}"
# ---------------------------------------------------------------------

export _JAVA_OPTIONS="-Xmx64g"

for n in "${CDS_DIR}"/*.cds.fasta; do
    [ -e "${n}" ] || continue
    m="$(basename "${n}")"
    echo "[busco:cds:embryophyta] ${m}"
    "${BUSCO_BIN}" -i "${n}" -l "${BUSCO_DB}/embryophyta_odb12" \
        -m transcriptome -o "tobacco_cds_embryophyta/${m}" \
        --cpu "${THREADS}" --offline -f

    echo "[busco:cds:eudicotyledons] ${m}"
    "${BUSCO_BIN}" -i "${n}" -l "${BUSCO_DB}/eudicotyledons_odb12" \
        -m transcriptome -o "tobacco_cds_eudicotyledons/${m}" \
        --cpu "${THREADS}" --offline -f
done

echo "[busco:cds] done."
