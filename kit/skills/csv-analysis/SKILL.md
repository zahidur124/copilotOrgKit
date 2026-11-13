---
name: csv-analysis
description: Answer questions about CSV and other tabular files by profiling them and then running pandas or duckdb scripts, never by pasting the file into the chat. Use when the user asks for counts, totals, averages, trends, duplicates, outliers, joins, a cleaned copy or a summary of a CSV, TSV or similar data file.
---

# csv-analysis

A CSV can hold personal or customer data, and a model that reads rows by eye gets sums and counts wrong. So the data is worked on by code. The code is shown, and every number you report comes from its output.

Needs: Python 3 with `pandas`; `duckdb` for files too large for memory or for SQL-style questions (`pip install pandas duckdb`). If pip is blocked, use the company's internal package mirror (`pip install --index-url <url> pandas duckdb`; ask the platform team for the URL).

Rules that hold for every step:
- **Never paste file contents into the chat**, and never print rows to look at them. Print aggregates (counts, sums, min, max, distinct counts). A column of names, emails, ids or free text is not echoed; when a sample is truly needed, ask the user first and show as few rows as will do, with identifying columns left out.
- **Never modify the source file.** Read it only. Write any output (cleaned data, a result table, a chart) to a new file with a new name, in a folder the user names or an `output/` folder that is not committed, and never `to_csv` back to the input path.
- **Every number comes from shown code.** Show the script or query, run it, and report what it printed. A figure you worked out in your head, or from a few rows you saw, is not reported.
- A file the user did not name, or one under a `data/` folder that the repo ignores, is still the user's data. Do not copy it to a place that is committed or shared.

1. **Profile first.** Run the profiling script in this skill's folder. It prints the encoding, delimiter, row count, and for each column its type, null count, distinct count and number range, without printing any text values:

   ```
   python3 -I path/to/skills/csv-analysis/profile_csv.py data.csv
   ```

   The script is at `.github/skills/csv-analysis/profile_csv.py` in a repository, or `~/.copilot/skills/csv-analysis/profile_csv.py` after a user install. If it is not there, write the same checks yourself in pandas: `pd.read_csv(path, sep=None, engine="python", nrows=1000)` to sniff the delimiter, then `df.dtypes`, `len(df)`, `df.isna().sum()` and `df.nunique()`. For the delimiter, encoding or decimal comma it got wrong, pass `--delimiter`, `--encoding`, or `decimal=","` in your own script.

2. **State what the profile shows, and what looks wrong.** Report the shape and anything that needs a decision before analysis: a number or date read as text, a column mostly null, duplicate rows, a header row that is not the first, mixed formats in one column, or an id column with repeats. Ask the user only where the data cannot settle the choice (for example whether a blank means zero or unknown).

3. **Write the script for the question.** Keep it in a file (for example `analysis.py` in a scratch or `output/` folder), not a one-off in the shell, so the user can rerun it. Set types on load rather than guessing later:

   ```python
   import pandas as pd

   df = pd.read_csv("data.csv", sep=";", encoding="cp1252", decimal=",",
                    dtype={"customer_id": "string"}, parse_dates=["order_date"])
   print(len(df), "rows")
   print(df.groupby("region")["amount"].agg(["count", "sum", "mean"]).round(2))
   ```

   For a large file, or when SQL is clearer, query it in place with duckdb, which streams from disk:

   ```python
   import duckdb

   print(duckdb.sql("""
       SELECT region, count(*) AS orders, round(sum(amount), 2) AS total
       FROM read_csv('data.csv', delim=';', header=true)
       GROUP BY region ORDER BY total DESC
   """).df())
   ```

   Ids and codes (account numbers, postcodes) are read as strings, because they are labels and a number type drops leading zeros.

4. **Run it and check the result for sense.** Compare the row count after each filter or join with the count before it and say why it changed; a join that grows the row count means a repeated key. Count the rows a filter dropped. Missing values: say how they were handled (excluded, filled) in the same sentence as the number.

5. **Report.** For each figure: the number, the one-line definition (which rows, which column, which filter), and the code that produced it. Give the path of any output file written. Name what you did not check, such as a column you did not clean.
