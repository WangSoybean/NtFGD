#!/usr/bin/env bash
# =====================================================================
# 1.run_star.sh  —  Read alignment (STAR, two-pass genome loading)
# =====================================================================
# Aligns the fastp-trimmed reads against one or more pre-built STAR
# indices using the shared-memory genome-load mechanism (LoadAndExit /
# LoadAndKeep / Remove) so that large genomes are loaded only once.
#
# Inputs
#   ${CLEAN_DIR}/${sample}.clean_1.fastq.gz
#   ${CLEAN_DIR}/${sample}.clean_2.fastq.gz
#   ${INDEX_ROOT}/${index}/            pre-built STAR index
#   name                               one sample ID per line
#
# Outputs (per index, per sample)
#   ${WORK_DIR}/${index}/${sample}Aligned.sortedByCoord.out.bam
#   ${WORK_DIR}/${index}/${sample}Log.final.out
#
# Usage
#   bash 1.run_star.sh
#   # or override the indices to run:
#   INDICES="NtSR1Index149 NtZY300Index149" bash 1.run_star.sh
# =====================================================================
set -euo pipefail

# ------------------------- user configuration ------------------------
CLEAN_DIR="${CLEAN_DIR:-work/clean}"
WORK_DIR="${WORK_DIR:-work}"
INDEX_ROOT="${INDEX_ROOT:-data/star_index}"
SAMPLE_LIST="${SAMPLE_LIST:-name}"

INDICES="${INDICES:-NtSR1Index149 NtZY300Index149}"
THREADS="${THREADS:-22}"
LIMIT_BAM_SORT_RAM="${LIMIT_BAM_SORT_RAM:-20000000000}"
# ---------------------------------------------------------------------

ulimit -n 65535 || true

for m in ${INDICES}; do
    echo "[STAR] loading genome: ${m}"
    STAR --genomeDir "${INDEX_ROOT}/${m}" --genomeLoad LoadAndExit

    mkdir -p "${WORK_DIR}/${m}"
    while read -r n; do
        [ -z "${n}" ] && continue
        echo "[STAR] ${m}_${n}"
        STAR \
            --runThreadN "${THREADS}" \
            --genomeDir "${INDEX_ROOT}/${m}" \
            --genomeLoad LoadAndKeep \
            --readFilesIn "${CLEAN_DIR}/${n}.clean_1.fastq.gz" \
                          "${CLEAN_DIR}/${n}.clean_2.fastq.gz" \
            --outFileNamePrefix "${WORK_DIR}/${m}/${n}" \
            --outSAMtype BAM SortedByCoordinate \
            --readFilesCommand zcat \
            --limitBAMsortRAM "${LIMIT_BAM_SORT_RAM}"
    done < "${SAMPLE_LIST}"

    STAR --genomeDir "${INDEX_ROOT}/${m}" --genomeLoad Remove
done

echo "[STAR] done."
