#!/usr/bin/env bash
# =====================================================================
# 5.plot_karyotype.sh  —  Synteny karyotype figure (jcvi.graphics)
# =====================================================================
# Renders the multi-genome synteny karyotype from the `seqids` and
# `layout` files.
#
# Inputs
#   seqids     list of chromosomes to draw, one per line
#   layout     jcvi layout file (see jcvi docs)
#   *.anchors.simple , *.anchors   produced by 2.run_jcvi_synteny.sh
#
# Output
#   karyotype.pdf / karyotype.png
#
# Usage
#   bash 5.plot_karyotype.sh
# =====================================================================
set -euo pipefail

# ------------------------- user configuration ------------------------
WORK_DIR="${WORK_DIR:-work/jcvi}"
# ---------------------------------------------------------------------

cd "${WORK_DIR}"
python -m jcvi.graphics.karyotype seqids layout
echo "[jcvi] karyotype figure written."
