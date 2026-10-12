#!/usr/bin/env bash
# =====================================================================
# 2.run_featurecounts.sh  —  Gene-level read counting (featureCounts)
# =====================================================================
# Counts reads per gene (grouped by transcript_id, counting read pairs)
# from the coordinate-sorted BAM files produced by 1.run_star.sh.
#
# Inputs
#   ${WORK_DIR}/${index}/*Aligned.sortedByCoord.out.bam
#   ${GTF_DIR}/<gtf>            transcript-level GTF matching each index
#
# Outputs
#   ${WORK_DIR}/${index}/gene_counts.txt
#   ${WORK_DIR}/${index}/gene_counts.txt.summary
#
# The mapping from STAR index -> GTF is defined in the INDEX_GTF variable
# below (edit it for your own assemblies).
#
# Usage
#   bash 2.run_featurecounts.sh
# =====================================================================
set -euo pipefail

# ------------------------- user configuration ------------------------
WORK_DIR="${WORK_DIR:-work}"
GTF_DIR="${GTF_DIR:-data/star_index}"
THREADS="${THREADS:-22}"
FEATURE_TYPE="${FEATURE_TYPE:-exon}"        # -t
ATTRIBUTE="${ATTRIBUTE:-transcript_id}"     # -g

# index_name : path_to_gtf   (one line per index)
INDEX_GTF="
NtZY300Index149:${GTF_DIR}/Nicotiana_tabacum-ZY300.gtf
NtSR1Index149:${GTF_DIR}/Nicotiana_tabacum_SR1_annotation_1.0.gtf
"
# ---------------------------------------------------------------------

echo "${INDEX_GTF}" | while IFS= read -r line; do
    [ -z "${line}" ] && continue
    idx="${line%%:*}"
    gtf="${line#*:}"
    echo "[featureCounts] ${idx}"
    (
        cd "${WORK_DIR}/${idx}"
        featureCounts \
            -T "${THREADS}" \
            -p --countReadPairs \
            -F GTF \
            -t "${FEATURE_TYPE}" \
            -g "${ATTRIBUTE}" \
            --primary \
            -a "${gtf}" \
            -o gene_counts.txt \
            *Aligned.sortedByCoord.out.bam
    )
done

echo "[featureCounts] done."
