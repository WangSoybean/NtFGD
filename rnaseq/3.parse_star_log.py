#!/usr/bin/env python3
# =====================================================================
# 3.parse_star_log.py
# ---------------------------------------------------------------------
# Parse every STAR `*Log.final.out` file in the current directory and
# summarise the key alignment metrics into `STAR_mapping_summary.csv`.
#
# Input :  <sample>Log.final.out          (STAR output, one per sample)
# Output:  STAR_mapping_summary.csv
#
# Columns of the output:
#   Sample, Input_reads, Avg_read_length, Uniquely_mapped_reads,
#   Multi_mapping_rate, Uniquely_mapping_rate
# =====================================================================
import pandas as pd
from pathlib import Path

# Fields extracted from the STAR log (STAR label -> output column name)
FIELDS = {
    "Number of input reads": "Input_reads",
    "Average input read length": "Avg_read_length",
    "Uniquely mapped reads number": "Uniquely_mapped_reads",
    "% of reads mapped to multiple loci": "Multi_mapping_rate"
}


def parse_star_log(log_file):
    """Parse a single STAR Log.final.out file."""
    result = {}
    with open(log_file) as f:
        for line in f:
            if "|" not in line:
                continue
            key, value = [x.strip() for x in line.split("|", 1)]
            if key in FIELDS:
                result[FIELDS[key]] = value.replace("%", "")
    return result


def main():
    rows = []
    for log in sorted(Path(".").glob("*Log.final.out")):
        sample = log.name.replace("Log.final.out", "")
        data = parse_star_log(log)
        data["Sample"] = sample
        rows.append(data)

    df = pd.DataFrame(rows)
    df = df[["Sample", "Input_reads", "Avg_read_length",
             "Uniquely_mapped_reads", "Multi_mapping_rate"]]
    # Type conversion (needed for the downstream calculations)
    df["Input_reads"] = df["Input_reads"].astype(int)
    df["Avg_read_length"] = df["Avg_read_length"].astype(float)
    df["Uniquely_mapped_reads"] = df["Uniquely_mapped_reads"].astype(int)
    df["Multi_mapping_rate"] = df["Multi_mapping_rate"].astype(float)
    df["Uniquely_mapping_rate"] = (
        df["Uniquely_mapped_reads"] / df["Input_reads"] * 100
    ).round(2)

    df.to_csv("STAR_mapping_summary.csv", index=False)
    print("OK: wrote STAR_mapping_summary.csv")


if __name__ == "__main__":
    main()
