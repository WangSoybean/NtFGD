import pandas as pd
import glob
import os

# =========================
# 配置
# =========================
INPUT_PATTERN = "plant_gene_function_*.tsv"
REQUIRED_COLUMNS = ["Title", "Abstract"]

# =========================
# 容器
# =========================
all_records = []
error_records = []

# =========================
# 工具函数：逐行校验 TSV
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
# 逐文件处理
# =========================
for filepath in sorted(glob.glob(INPUT_PATTERN)):
    fname = os.path.basename(filepath)
    print(f"? Processing {fname}")
    try:
        df, bad_line_errors = read_tsv_with_validation(filepath)
    except Exception as e:
        error_records.append({
            "SourceFile": fname,
            "ErrorType": "FILE_READ_ERROR",
            "Detail": str(e)
        })
        continue
    # ---- 记录 TSV 结构错误行 ----
    if bad_line_errors:
        error_records.extend(bad_line_errors)
    # ---- 检查列 ----
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        error_records.append({
            "SourceFile": fname,
            "ErrorType": "MISSING_COLUMNS",
            "Detail": ",".join(missing_cols)
        })
        continue

    # ---- 标记来源文件 ----
    df["SourceFile"] = fname

    # ---- 行级完整性检查 ----
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
# 分文件输出
# =========================
print("? Writing Excel files...")

# ---- 正常数据 ----
if all_records:
    final_df = pd.concat(all_records, ignore_index=True)
    final_df.drop(columns=["SourceFile"], inplace=True)
    final_df.to_excel("plant_gene_function_ALL.xlsx", index=False)
    final_df.to_csv("meraged_plant_gene_function.tsv", sep='\t', index=False)
    print(f"  ? Saved {len(final_df)} records to plant_gene_function_ALL.xlsx")
else:
    print("  ? No valid records to save")

# ---- 异常数据 ----
if error_records:
    error_df = pd.concat(
        [pd.DataFrame([r]) if isinstance(r, dict) else r for r in error_records],
        ignore_index=True
    )
    error_df.to_excel("plant_gene_function_ERROR.xlsx", index=False)
    print(f"  ? Saved {len(error_df)} records to plant_gene_function_ERROR.xlsx")
else:
    print("  ? No error records")

print("? Done")
