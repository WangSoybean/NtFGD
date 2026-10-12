#!/usr/bin/env bash
# =====================================================================
# 1.run_eggnog_mapper.sh  —  Functional annotation with eggNOG-mapper
# =====================================================================
# Annotates predicted protein sets against the eggNOG database using the
# DIAMOND search mode with Pfam realignment and ortholog reporting,
# restricted to the Viridiplantae taxonomic scope.
#
# Inputs
#   ${PROTEIN_DIR}/*.pep.fasta      one protein FASTA per assembly
#
# Outputs (per input, in ${OUTPUT_DIR})
#   <name>.emapper.annotations      main annotation table (TSV)
#   <name>.emapper.hits             DIAMOND hits
#   <name>.emapper.seed_orthologs   seed orthologs
#
# Usage
#   bash 1.run_eggnog_mapper.sh
#   PROTEIN_DIR=data/annotation THREADS=22 bash 1.run_eggnog_mapper.sh
# =====================================================================
set -euo pipefail

# ------------------------- user configuration ------------------------
EGGNOG_DIR="${EGGNOG_DIR:-software/eggnog-mapper-2.1.13}"
PROTEIN_DIR="${PROTEIN_DIR:-data/annotation}"
OUTPUT_DIR="${OUTPUT_DIR:-work/emapper_out}"
THREADS="${THREADS:-22}"
TAX_SCOPE="${TAX_SCOPE:-Viridiplantae}"
# ---------------------------------------------------------------------

export PATH="${EGGNOG_DIR}:${EGGNOG_DIR}/eggnogmapper/bin:${PATH}"
export EGGNOG_DATA_DIR="${EGGNOG_DATA_DIR:-${EGGNOG_DIR}/data}"

mkdir -p "${OUTPUT_DIR}"

for path in "${PROTEIN_DIR}"/*.pep.fasta; do
    [ -e "${path}" ] || continue
    n="$(basename "${path}")"
    echo "[eggnog] ${n}"
    emapper.py \
        -i "${path}" \
        --itype proteins \
        -m diamond \
        --cpu "${THREADS}" \
        --tax_scope "${TAX_SCOPE}" \
        --go_evidence all \
        --pfam_realign realign \
        --report_orthologs \
        --target_orthologs all \
        --output_dir "${OUTPUT_DIR}" \
        -o "${n}"
    rm -rf emappertmp_*
done

echo "[eggnog] done."
