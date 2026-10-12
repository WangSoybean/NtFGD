#!/usr/bin/env bash
# =====================================================================
# 1.extract_gene_locations.sh  —  Gene-location tables from GFF3
# =====================================================================
# Extracts a compact "chr  start  end  strand  gene_id" table for every
# assembly, stripping the chromosome-name prefix (chr/Chr/Nt/...) and
# any zero padding so chromosome numbering is comparable across
# assemblies.
#
# Inputs
#   ${ANNOT_DIR}/<asm>.gff3      (one per assembly)
#   name                         (one assembly name per line)
#
# Outputs
#   ${OUTPUT_DIR}/<asm>.genelocation
#
# Usage
#   bash 1.extract_gene_locations.sh
# =====================================================================
set -euo pipefail

# ------------------------- user configuration ------------------------
ANNOT_DIR="${ANNOT_DIR:-data/annotation}"
OUTPUT_DIR="${OUTPUT_DIR:-results/gene_location}"
SAMPLE_LIST="${SAMPLE_LIST:-name}"
# ---------------------------------------------------------------------

mkdir -p "${OUTPUT_DIR}"

while read -r asm; do
    [ -z "${asm}" ] && continue
    echo "[genelocation] ${asm}"
    gff="${ANNOT_DIR}/${asm}.gff3"
    awk -F'\t' '$3=="gene" {
            split($9, a, ";");
            gsub("ID=", "", a[1]);
            chr = $1; sub("^(chr|Chr|Nt)", "", chr); sub("^0+", "", chr);
            print chr, $4, $5, $7, a[1]
        }' "${gff}" > "${OUTPUT_DIR}/${asm}.genelocation"
done < "${SAMPLE_LIST}"

echo "[genelocation] done."
