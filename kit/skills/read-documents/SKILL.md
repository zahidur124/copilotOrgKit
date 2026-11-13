---
name: read-documents
description: Read PDF, Word (.docx), PowerPoint (.pptx) and Excel (.xlsx) files by converting them to Markdown with the to_markdown.py script in this skill's folder first. Use whenever the user points at one of these files and wants it read, summarized, searched, quoted or compared, or when another task needs the content of such a file. Copilot cannot read these binary files directly.
---

# read-documents

Copilot reads text. A `.pdf`, `.docx`, `.pptx` or `.xlsx` file is binary, so opening it as text gives noise or nothing, and an answer built on that is invented. Convert the file to Markdown with this skill's `to_markdown.py`, then read the Markdown.

Needs: Python 3.10 or later and four packages (`pip install pdfplumber python-docx python-pptx openpyxl`); the script uses only the one a file's type needs, and names the one that is missing. If pip is blocked or cannot reach PyPI, use the company's internal package mirror (ask the platform team for its index URL, then `pip install --index-url <url> pdfplumber python-docx python-pptx openpyxl`); do not look for another way round the block.

1. **Find the script and check the packages.** The script is at `.github/skills/read-documents/to_markdown.py` in a repository, or `~/.copilot/skills/read-documents/to_markdown.py` after a user install. Run it on the file (step 2). If it stops with "needs the package ...", run the `python3 -m pip install` line it prints (use `py -m pip` or `python -m pip` if that is how Python is started). Installation fails → say so and stop, with the error text, because a guess at the file's content is not a substitute. If the script is not installed, say so and stop; do not fall back to opening the binary file.

2. **Convert to a folder outside the repository, or an ignored one.** Do not write the Markdown next to the source and do not add it to the repo, because it may hold the same confidential content as the original.

   ```
   mkdir -p "${TMPDIR:-/tmp}/converted"
   python3 -I .github/skills/read-documents/to_markdown.py "path/to/report.docx" -o "${TMPDIR:-/tmp}/converted/report.md"
   ```

   On Windows PowerShell (for a user install, the script is at `$env:USERPROFILE\.copilot\skills\read-documents\to_markdown.py`):

   ```
   New-Item -ItemType Directory -Force "$env:TEMP\converted" | Out-Null
   py -3 -I ".github\skills\read-documents\to_markdown.py" "path\to\report.docx" -o "$env:TEMP\converted\report.md"
   ```

   Without `-o` the Markdown goes to standard output. Convert one file at a time and name each output after its source. The source file is never modified. An old `.doc`, `.ppt` or `.xls` file is not read: the script says to save it as `.docx`, `.pptx` or `.xlsx` first, which the user does in Word, PowerPoint or Excel.

3. **Read the Markdown in parts.** Check its size first (`wc -l`; `(Get-Content file).Count` in PowerShell), then read the range you need rather than the whole file when it is long. Search it with `rg` or `grep -n`.

4. **Know what the conversion loses.** Say so in the answer when it matters.
   - **PDF:** each page starts with `## Page N` (counted from 1, as in a PDF viewer), so a quote can cite its page. Tables that pdfplumber finds are Markdown tables, in their place between the text above and below them. A page with no text is labelled as possibly scanned: this skill does not do OCR, so tell the user which pages were not read. The Markdown is only as good as the PDF's text layer; columns, headers, footers and tables without ruling lines can come out in the wrong order or as plain text. For finer control (table settings, cropping a column) use the `pdf` skill.
   - **DOCX:** headings (`#` for Title and Heading 1, down to `######`), paragraphs, lists and tables are kept, in document order. Page numbers, headers, footers, footnotes, comments, text boxes, pictures and tracked changes are not, and the script does not say where a page ends, so refer to a section by its heading.
   - **PPTX:** each slide starts with `## Slide N`, then its title as `###`, its text, tables, and speaker notes under `### Notes`. Pictures and charts are not described; the script marks where one is, so say that a slide's picture was not read.
   - **XLSX:** each sheet becomes a Markdown table under `## Sheet <name>`, from its saved values. A formula arrives as its last saved result (empty if the file was never calculated in Excel), and dates as `YYYY-MM-DD`. Only the first 200 non-empty rows (and 50 columns) of a sheet are shown, and the script says when it cut a sheet; add `--max-rows N` to see more. A large sheet is better read through the `csv-analysis` skill's approach (pandas or duckdb) than as Markdown.

5. **Quote what the Markdown says.** Cite the page, slide number, sheet, the heading, or the line in the converted file. Do not fill a gap, such as a table that came out empty, from memory; say the content was not extracted.

6. **Report.** Give the converted file's path, what was read, and anything the conversion lost or could not read.

Do not paste a whole converted document into the chat. Quote the lines the answer needs.
