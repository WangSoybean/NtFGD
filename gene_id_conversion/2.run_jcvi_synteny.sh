#!/usr/bin/env bash
# =====================================================================
# 2.run_jcvi_synteny.sh  —  Pairwise synteny with jcvi (MCScan)
# =====================================================================
# Runs all pairwise ortholog searches and anchor screening between the
# assemblies listed in `name`, producing the anchor files consumed by
# 4.convert_gene_ids.py and 5.plot_karyotype.sh.
#
# Inputs
#   work/jcvi/<asm>.bed , work/jcvi/<asm>.cds   (from step 1)
#   name                                        (one assembly per line)
#
# Outputs
#   <asm1>.<asm2>.anchors
#   <asm1>.<asm2>.anchors.simple
#   ... (one set per assembly pair)
#
# Usage
#   bash 2.run_jcvi_synteny.sh
# =====================================================================
set -euo pipefail

# ------------------------- user configuration ------------------------
WORK_DIR="${WORK_DIR:-work/jcvi}"
SAMPLE_LIST="${SAMPLE_LIST:-name}"
LAST_BIN="${LAST_BIN:-software/last/bin}"   # add LAST to PATH for jcvi
CSCORE="${CSCORE:-0.99}"
MINSPAN="${MINSPAN:-30}"
# ---------------------------------------------------------------------

export PATH="${LAST_BIN}:${PATH}"

cd "${WORK_DIR}"

# --- 1. Pairwise ortholog / anchor search -----------------------------
for n in $(cat "${SAMPLE_LIST}"); do
    for m in $(cat "${SAMPLE_LIST}"); do
        echo "[jcvi] ortholog ${n} ${m}"
        python -m jcvi.compara.catalog ortholog "${n}" "${m}" \
            --no_strip_names --cscore="${CSCORE}"
    done
done

# --- 2. Anchor screening (keep anchors spanning >= MINSPAN genes) -----
for n in $(cat "${SAMPLE_LIST}"); do
    for m in $(cat "${SAMPLE_LIST}"); do
        echo "[jcvi] screen ${n} ${m}"
        python -m jcvi.compara.synteny screen --minspan="${MINSPAN}" --simple \
            "${n}.${m}.anchors" "${n}.${m}.anchors.simple"
    done
done

echo "[jcvi] done."
