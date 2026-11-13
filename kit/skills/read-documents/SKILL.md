---
name: read-documents
description: Read PDF, Word (.docx), PowerPoint (.pptx) and Excel (.xlsx) files by converting them to Markdown with Microsoft's markitdown first. Use whenever the user points at one of these files and wants it read, summarized, searched, quoted or compared, or when another task needs the content of such a file. Copilot cannot read these binary files directly.
---

# read-documents

Copilot reads text. A `.pdf`, `.docx`, `.pptx` or `.xlsx` file is binary, so opening it as text gives noise or nothing, and an answer built on that is invented. Convert the file to Markdown, then read the Markdown.

Needs: Python 3.10 to 3.14 and `markitdown` (`pip install 'markitdown[all]'`). If pip is blocked or cannot reach PyPI, use the company's internal package mirror (ask the platform team for its index URL, then `pip install --index-url <url> 'markitdown[all]'`); do not look for another way round the block.

1. **Check the tool is there.** Run `markitdown --help`. If the command is missing, run `python3 -m pip install 'markitdown[all]'` (use `py -m pip` or `python` if that is how Python is started). Installation fails → say so and stop, with the error text, because a guess at the file's content is not a substitute.

2. **Convert to a folder outside the repository, or an ignored one.** Do not write the Markdown next to the source and do not add it to the repo, because it may hold the same confidential content as the original.

   ```
   mkdir -p "${TMPDIR:-/tmp}/converted"
   markitdown "path/to/report.docx" > "${TMPDIR:-/tmp}/converted/report.md"
   ```

   On Windows PowerShell: `markitdown "path\to\report.docx" -o "$env:TEMP\report.md"`. Convert one file at a time and name each output after its source. The source file is never modified.

3. **Read the Markdown in parts.** Check its size first (`wc -l`), then read the range you need rather than the whole file when it is long. Search it with `rg` or `grep -n`.

4. **Know what the conversion loses.** Say so in the answer when it matters.
   - **PDF:** text comes out with no page breaks, so the Markdown cannot tell you the page. For a page number, extract page by page with the `pdf` skill. A scanned PDF (pages that are pictures) converts to an empty or near-empty file: this skill does not do OCR, so tell the user the file is scanned and stop. The Markdown is also only as good as the PDF's text layer; columns, headers, footers and tables can come out in the wrong order.
   - **DOCX:** headings, lists and tables are kept. Page numbers, headers, footers, comments and tracked changes are not, and the tool does not say where a page ends, so refer to a section by its heading.
   - **PPTX:** each slide starts with `<!-- Slide number: N -->`, and speaker notes follow a `### Notes:` heading. Pictures and charts are not described unless an image description is set up; say that a slide's picture was not read.
   - **XLSX:** each sheet becomes a Markdown table under its name. Formulas arrive as their last saved values, and a large sheet is better read through the `csv-analysis` skill's approach (pandas or duckdb) than as Markdown.

5. **Quote what the Markdown says.** Cite the slide number, the heading, or the line in the converted file. Do not fill a gap, such as a table that came out empty, from memory; say the content was not extracted.

6. **Report.** Give the converted file's path, what was read, and anything the conversion lost or could not read.

Do not paste a whole converted document into the chat. Quote the lines the answer needs.
