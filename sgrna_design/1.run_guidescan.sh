#!/usr/bin/env bash
# =====================================================================
# 1.run_guidescan.sh  —  run the sgRNA design pipeline
# =====================================================================
# Example invocation of sgrna_pipeline.py for one target FASTA and one
# GuideScan genome index.
#
# Usage
#   bash 1.run_guidescan.sh
# =====================================================================
set -euo pipefail

# ------------------------- user configuration ------------------------
INPUT_FASTA="${INPUT_FASTA:-Input.fasta}"
GENOME_INDEX="${GENOME_INDEX:-data/annotation/Ntab_ZY300-CAAS-2024-chromosome-v1.genome.fasta.index}"
PREFIX="${PREFIX:-sgRNA}"
PAM="${PAM:-NGG}"
MISMATCH="${MISMATCH:-1}"
# ---------------------------------------------------------------------

python sgrna_pipeline.py "${INPUT_FASTA}" "${GENOME_INDEX}" \
    "${PREFIX}" "${PAM}" "${MISMATCH}"

# For the database-ready JSON, run (after the per-genome SQLite DB exists):
#   python sgrna_pipeline_for_geneID.py --GenomeName <assembly>
