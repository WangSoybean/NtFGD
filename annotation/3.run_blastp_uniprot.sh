#!/usr/bin/env bash
# =====================================================================
# 3.run_blastp_uniprot.sh  —  BLASTP against UniProt/Swiss-Prot
# =====================================================================
# Builds (if needed) a Swiss-Prot protein BLAST database and searches
# every predicted protein set against it.
#
# Inputs
#   ${PROTEIN_DIR}/*.pep.fasta      one protein FASTA per assembly
#
# Outputs
#   ${BLAST_DB}                     BLAST database (built on first run)
#   ${OUTPUT_DIR}/<name>.swissprot.blastp.tsv
#
# Usage
#   bash 3.run_blastp_uniprot.sh
# =====================================================================
set -euo pipefail

# ------------------------- user configuration ------------------------
PROTEIN_DIR="${PROTEIN_DIR:-data/annotation}"
OUTPUT_DIR="${OUTPUT_DIR:-work/blastp_out}"
DB_DIR="${DB_DIR:-software/blastdb}"
BLAST_DB="${BLAST_DB:-${DB_DIR}/swissprot}"
THREADS="${THREADS:-20}"
EVALUE="${EVALUE:-1e-5}"
MAX_TARGET_SEQS="${MAX_TARGET_SEQS:-1}"
# ---------------------------------------------------------------------

mkdir -p "${OUTPUT_DIR}" "${DB_DIR}"

# ---- 1. Download and prepare Swiss-Prot if the database is missing ----
if [ ! -e "${BLAST_DB}.phr" ]; then
    echo "[blastp] building Swiss-Prot database"
    (
        cd "${DB_DIR}"
        wget -q -N \
            https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz
        gunzip -f uniprot_sprot.fasta.gz
        makeblastdb -in uniprot_sprot.fasta -dbtype prot -out swissprot
    )
fi

# ---- 2. Search each protein set --------------------------------------
for path in "${PROTEIN_DIR}"/*.pep.fasta; do
    [ -e "${path}" ] || continue
    n="$(basename "${path}")"
    n="${n%.pep.fasta}"
    echo "[blastp] ${n}"
    blastp \
        -db "${BLAST_DB}" \
        -query "${path}" \
        -out "${OUTPUT_DIR}/${n}.swissprot.blastp.tsv" \
        -evalue "${EVALUE}" \
        -max_target_seqs "${MAX_TARGET_SEQS}" \
        -outfmt 6 \
        -num_threads "${THREADS}"
done

echo "[blastp] done."
