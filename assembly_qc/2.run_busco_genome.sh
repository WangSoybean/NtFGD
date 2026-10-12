#!/usr/bin/env bash
# =====================================================================
# 2.run_busco_genome.sh  —  Genome completeness (BUSCO, genome mode)
# =====================================================================
# Assesses the completeness of each genome assembly against two BUSCO
# lineages (Embryophyta and eudicots) in offline mode.
#
# Inputs
#   ${GENOME_DIR}/*.genome.fasta
#   ${BUSCO_DB}/embryophyta_odb12
#   ${BUSCO_DB}/eudicotyledons_odb12
#
# Outputs
#   ${OUTPUT_DIR}/tobacco_genome_embryophyta/<name>
#   ${OUTPUT_DIR}/tobacco_genome_eudicotyledons/<name>
#
# Usage
#   bash 2.run_busco_genome.sh
# =====================================================================
set -euo pipefail

# ------------------------- user configuration ------------------------
GENOME_DIR="${GENOME_DIR:-data/annotation}"
OUTPUT_DIR="${OUTPUT_DIR:-results/busco}"
BUSCO_DB="${BUSCO_DB:-software/busco_db}"
BUSCO_BIN="${BUSCO_BIN:-busco}"
THREADS="${THREADS:-22}"
# ---------------------------------------------------------------------

export _JAVA_OPTIONS="-Xmx64g"

for n in "${GENOME_DIR}"/*.genome.fasta; do
    [ -e "${n}" ] || continue
    m="$(basename "${n}")"
    echo "[busco:genome:embryophyta] ${m}"
    "${BUSCO_BIN}" -i "${n}" -l "${BUSCO_DB}/embryophyta_odb12" \
        -m genome -o "tobacco_genome_embryophyta/${m}" \
        --cpu "${THREADS}" --offline -f

    echo "[busco:genome:eudicotyledons] ${m}"
    "${BUSCO_BIN}" -i "${n}" -l "${BUSCO_DB}/eudicotyledons_odb12" \
        -m genome -o "tobacco_genome_eudicotyledons/${m}" \
        --cpu "${THREADS}" --offline -f
done

echo "[busco:genome] done."
