#!/usr/bin/env bash
# =====================================================================
# 3.run_last.sh  —  LAST whole-sequence alignment (gene-ID conversion
#                    fallback for genes without a synteny anchor)
# =====================================================================
# Aligns every assembly in `name` against every other assembly with LAST
# and reduces each pairwise alignment to the best hit per query gene.
# The result feeds the sequence-alignment fallback in
# 4.convert_gene_ids.py.
#
# For relatively close species (as here) nucleotide CDS alignment is
# sufficient and fast; set SEQTYPE=protein to align the protein sets
# instead (more sensitive but requires <asm>.pep).
#
# Inputs
#   work/jcvi/<asm>.cds   (SEQTYPE=dna, default)   — from step 1
#   work/jcvi/<asm>.pep   (SEQTYPE=protein)
#   name                  one assembly name per line
#
# Outputs
#   <query>.<target>.last.filtered   best hit per query gene
#     columns (LAST "BlastTab", 12 fields):
#       query target identity aln_len mismatch gapopen
#       q_start q_end t_start t_end evalue bit_score
#
# Usage
#   bash 3.run_last.sh
#   SEQTYPE=protein MIN_IDENTITY=30 bash 3.run_last.sh
# =====================================================================
set -euo pipefail

# ------------------------- user configuration ------------------------
WORK_DIR="${WORK_DIR:-work/jcvi}"
SAMPLE_LIST="${SAMPLE_LIST:-name}"
LAST_BIN="${LAST_BIN:-software/last/bin}"
SEQTYPE="${SEQTYPE:-dna}"           # dna | protein
THREADS="${THREADS:-20}"
MIN_IDENTITY="${MIN_IDENTITY:-0}"   # keep hits with %identity >= this
MIN_ALN_LEN="${MIN_ALN_LEN:-0}"     # keep hits with alignment length >= this
# ---------------------------------------------------------------------

export PATH="${LAST_BIN}:${PATH}"
cd "${WORK_DIR}"

if [ "${SEQTYPE}" = "protein" ]; then
    EXT="pep"; DBFLAG="-p"
else
    EXT="cds"; DBFLAG=""
fi

# ---- 1. Build a LAST database for each assembly ----------------------
for asm in $(cat "${SAMPLE_LIST}"); do
    echo "[lastdb] ${asm}"
    # shellcheck disable=SC2086
    lastdb ${DBFLAG} "${asm}" "${asm}.${EXT}"
done

# ---- 2. Align every ordered pair and keep the best hit per query -----
for n in $(cat "${SAMPLE_LIST}"); do
    for m in $(cat "${SAMPLE_LIST}"); do
        [ "${n}" = "${m}" ] && continue
        echo "[last] ${n} vs ${m}"
        raw="${n}.${m}.last"
        lastal -P "${THREADS}" -f BlastTab "${m}" "${n}.${EXT}" > "${raw}"

        # keep hits passing the identity / length thresholds, then retain
        # the highest bit-score hit ($12) for each query ($1)
        awk -v mi="${MIN_IDENTITY}" -v ml="${MIN_ALN_LEN}" \
                '($3+0) >= mi && ($4+0) >= ml' "${raw}" \
            | sort -k1,1 -k12,12gr \
            | awk '!seen[$1]++' \
            > "${n}.${m}.last.filtered"
    done
done

echo "[last] done."
