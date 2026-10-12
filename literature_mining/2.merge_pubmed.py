#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# 2.merge_pubmed.py  —  Merge and validate the yearly PubMed TSV files
# ---------------------------------------------------------------------
# Combines every `plant_gene_function_*.tsv` file produced by
# 1.get_pubmed.py into a single table, validating each file along the way:
#   * structurally malformed lines (wrong number of TSV columns) are
#     collected into an error table;
#   * records with empty / too-short titles or abstracts are treated as
#     incomplete and moved to the error table;
#   * the remaining (valid) records are concatenated.
#
# Outputs
#   plant_gene_function_ALL.xlsx     valid records (Excel)
#   meraged_plant_gene_function.tsv  valid records (TSV, input to step 3)
#   plant_gene_function_ERROR.xlsx   rejected records with error type
#
# Usage
#   pip install pandas openpyxl
#   python 2.merge_pubmed.py
# =====================================================================
import pandas as pd
import glob
import os

# =========================
# Configuration
# =========================
INPUT_PATTERN = "plant_gene_function_*.tsv"
REQUIRED_COLUMNS = ["Title", "Abstract"]

# =========================
# Containers
# =========================
all_records = []
error_records = []


# =========================
# Helper: read a TSV with per-line validation
# =========================
def read_tsv_with_validation(filepath):
    good_rows = []
    bad_rows = []
    with open(filepath, encoding="utf-8", errors="replace") as f:
        header = f.readline().rstrip("\n")
        columns = header.split("\t")
        expected_ncols = len(columns)
        for lineno, line in enumerate(f, start=2):
            fields = line.rstrip("\n").split("\t")
            if len(fields) != expected_ncols:
                bad_rows.append({
                    "SourceFile": os.path.basename(filepath),
                    "LineNumber": lineno,
                    "ErrorType": "BAD_TSV_FORMAT",
                    "Detail": f"Expected {expected_ncols} cols, got {len(fields)}",
                    "RawLine": line[:500]
                })
            else:
                good_rows.append(fields)

    df = pd.DataFrame(good_rows, columns=columns)
    return df, bad_rows


# =========================
# Process each input file
# =========================
for filepath in sorted(glob.glob(INPUT_PATTERN)):
    fname = os.path.basename(filepath)
    print(f"> Processing {fname}")
    try:
        df, bad_line_errors = read_tsv_with_validation(filepath)
    except Exception as e:
        error_records.append({
            "SourceFile": fname,
            "ErrorType": "FILE_READ_ERROR",
            "Detail": str(e)
        })
        continue
    # ---- Record TSV structure errors ----
    if bad_line_errors:
        error_records.extend(bad_line_errors)
    # ---- Check columns ----
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        error_records.append({
            "SourceFile": fname,
            "ErrorType": "MISSING_COLUMNS",
            "Detail": ",".join(missing_cols)
        })
        continue

    # ---- Tag source file ----
    df["SourceFile"] = fname

    # ---- Row-level completeness check ----
    df["Title"] = df["Title"].fillna("").str.strip()
    df["Abstract"] = df["Abstract"].fillna("").str.strip()

    bad_mask = (
        (df["Title"] == "") |
        (df["Abstract"] == "") |
        (df["Abstract"].str.len() < 20)
    )

    bad_rows = df[bad_mask].copy()
    good_rows = df[~bad_mask].copy()

    if not bad_rows.empty:
        bad_rows["ErrorType"] = "INCOMPLETE_CONTENT"
        error_records.append(bad_rows)

    if not good_rows.empty:
        all_records.append(good_rows)


# =========================
# Write outputs
# =========================
print("Writing output files...")

# ---- Valid records ----
if all_records:
    final_df = pd.concat(all_records, ignore_index=True)
    final_df.drop(columns=["SourceFile"], inplace=True)
    final_df.to_excel("plant_gene_function_ALL.xlsx", index=False)
    final_df.to_csv("meraged_plant_gene_function.tsv", sep='\t', index=False)
    print(f"  Saved {len(final_df)} records to plant_gene_function_ALL.xlsx")
else:
    print("  No valid records to save")

# ---- Rejected records ----
if error_records:
    error_df = pd.concat(
        [pd.DataFrame([r]) if isinstance(r, dict) else r for r in error_records],
        ignore_index=True
    )
    error_df.to_excel("plant_gene_function_ERROR.xlsx", index=False)
    print(f"  Saved {len(error_df)} records to plant_gene_function_ERROR.xlsx")
else:
    print("  No error records")

print("Done")
