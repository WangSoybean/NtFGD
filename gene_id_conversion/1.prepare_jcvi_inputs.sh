#!/usr/bin/env bash
# =====================================================================
# 1.prepare_jcvi_inputs.sh  —  Build .bed and .cds files for jcvi/MCScan
# =====================================================================
# For each assembly, derive the two files required by jcvi's synteny
# tools from the GFF3 and the CDS FASTA:
#   <asm>.bed   gene coordinates (chr  start  end  gene_id)
#   <asm>.cds   CDS sequences with transcript suffixes stripped from the
#               headers so that gene IDs match the .bed file
#
# Chromosome-name prefixes (chr/Chr/Nt/...) are removed so that the same
# chromosome numbering is used across assemblies.
#
# Inputs
#   ${ANNOT_DIR}/<asm>.gff3
#   ${ANNOT_DIR}/<asm>.cds.fasta
#
# Outputs
#   ${WORK_DIR}/jcvi/<asm>.bed
#   ${WORK_DIR}/jcvi/<asm>.cds
#
# Usage
#   bash 1.prepare_jcvi_inputs.sh
# =====================================================================
set -euo pipefail

# ------------------------- user configuration ------------------------
ANNOT_DIR="${ANNOT_DIR:-data/annotation}"
WORK_DIR="${WORK_DIR:-work/jcvi}"
SAMPLE_LIST="${SAMPLE_LIST:-name}"     # one assembly name per line
# ---------------------------------------------------------------------

mkdir -p "${WORK_DIR}"
cd "${WORK_DIR}"

while read -r asm; do
    [ -z "${asm}" ] && continue
    echo "[jcvi-prep] ${asm}"

    gff="${ANNOT_DIR}/${asm}.gff3"
    cds="${ANNOT_DIR}/${asm}.cds.fasta"

    # Gene coordinates: keep only "gene" features, drop the ID= prefix,
    # and strip the leading chromosome prefix / zero padding.
    awk -F'\t' '$3=="gene" {
            split($9, a, ";");
            gsub("ID=", "", a[1]);
            chr = $1; sub("^(chr|Chr|Nt)", "", chr); sub("^0+", "", chr);
            print chr, $4, $5, a[1]
        }' "${gff}" > "${asm}.bed"

    # CDS: strip the .t1 (transcript) suffix so headers match gene IDs.
    sed '/^>/s/\.t1//' "${cds}" > "${asm}.cds"
done < "${SAMPLE_LIST}"

echo "[jcvi-prep] done."
