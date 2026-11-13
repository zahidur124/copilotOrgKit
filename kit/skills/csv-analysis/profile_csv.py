#!/usr/bin/env python3
"""Profile a CSV file without printing any of its cell values.

  python3 profile_csv.py data.csv [--delimiter ';'] [--encoding cp1252]

Prints the encoding, delimiter, row count, and per column: pandas type, null count,
distinct count, and for number and date columns the minimum and maximum.
Text values are never printed, because a CSV may hold personal or customer data.
Needs pandas. Never writes anything and never changes the file.
"""
import argparse
import csv
import sys

import pandas as pd

ENCODINGS = ["utf-8-sig", "utf-8", "cp1252", "latin-1"]  # latin-1 accepts any byte, so it is last


def detect_encoding(path):
    for enc in ENCODINGS:
        try:
            with open(path, encoding=enc) as f:
                while f.read(1 << 20):
                    pass
            return enc
        except UnicodeDecodeError:
            continue
    return "latin-1"


def detect_delimiter(path, encoding):
    with open(path, encoding=encoding, newline="") as f:
        head = f.read(64 * 1024)
    try:
        return csv.Sniffer().sniff(head, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def main():
    p = argparse.ArgumentParser(description="Profile a CSV file without printing its values.")
    p.add_argument("path")
    p.add_argument("--delimiter", help="override the detected delimiter; use \\t for tab")
    p.add_argument("--encoding", help="override the detected encoding")
    a = p.parse_args()

    enc = a.encoding or detect_encoding(a.path)
    delim = (a.delimiter or detect_delimiter(a.path, enc)).replace("\\t", "\t")
    try:
        df = pd.read_csv(a.path, sep=delim, encoding=enc, low_memory=False)
    except Exception as e:  # report the reason and stop; a profile of a wrong parse is worse than none
        sys.exit(f"could not read {a.path} (encoding {enc}, delimiter {delim!r}): {e}")

    print(f"file:       {a.path}")
    print(f"encoding:   {enc}")
    print(f"delimiter:  {delim!r}")
    print(f"rows:       {len(df)}")
    print(f"columns:    {df.shape[1]}")
    print(f"duplicate rows: {int(df.duplicated().sum())}")
    print()
    print(f"{'column':<30} {'type':<14} {'nulls':>8} {'distinct':>9}  range (number/date columns)")
    for col in df.columns:
        s = df[col]
        rng = ""
        if pd.api.types.is_numeric_dtype(s) and s.notna().any():
            rng = f"{s.min()} .. {s.max()}"
        print(f"{str(col)[:30]:<30} {str(s.dtype):<14} {int(s.isna().sum()):>8} {s.nunique(dropna=True):>9}  {rng}")
    unnamed = [c for c in df.columns if str(c).startswith("Unnamed:")]
    if unnamed:
        print(f"\nnote: {len(unnamed)} column(s) have no header; check the delimiter and that the first row is a header")
    if not all(pd.api.types.is_numeric_dtype(df[c]) for c in df.columns):
        print("\nnote: text columns show only null and distinct counts. A number or date read as text (type str or "
              "object) needs converting in your own script with pd.to_numeric or pd.to_datetime, and a decimal comma "
              "needs decimal=',' in read_csv")

if __name__ == "__main__":
    main()
