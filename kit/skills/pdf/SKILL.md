---
name: pdf
description: Work with PDF files in Python - extract text and tables page by page with pdfplumber, and merge, split, rotate pages or fill form fields with pypdf. Use when the user asks for text or a table from a PDF with page numbers, to combine, split or rotate PDFs, or to fill in a PDF form. Scanned PDFs need OCR, which this skill does not do. For a plain read of a PDF, use the read-documents skill.
---

# pdf

Needs: Python 3 with `pdfplumber` (text and tables) and `pypdf` (merge, split, rotate, forms): `pip install pdfplumber pypdf`. If pip is blocked, use the company's internal package mirror (`pip install --index-url <url> pdfplumber pypdf`; ask the platform team for the URL).

Rules that hold for every step:
- **The source PDF is never modified.** Every result is written to a new file with a new name.
- **Scanned PDFs need OCR, and this skill does not do OCR.** A scanned PDF has pictures of pages and no text. If a page gives no text (step 1 prints it), say the file looks scanned and that reading it needs an OCR tool, which the company must supply, then stop. Do not guess at the content, and do not describe what a page "probably" says.
- Page numbers shown to the user count from 1, as in a PDF viewer. `pypdf` and `pdfplumber` lists count from 0 (`reader.pages[0]` is page 1), so convert in one place and state which you used.
- Do not paste a whole document's text into the chat; quote the lines the answer needs. A PDF can hold personal or customer data.

1. **Check what the file is.** Page count, encryption, and which pages have a text layer:

   ```python
   import pdfplumber
   from pypdf import PdfReader

   path = "input.pdf"
   reader = PdfReader(path)
   print("pages:", len(reader.pages), "encrypted:", reader.is_encrypted)
   with pdfplumber.open(path) as pdf:
       for n, page in enumerate(pdf.pages, start=1):
           text = page.extract_text() or ""
           print(n, len(text), "characters" if text.strip() else "NO TEXT (scanned or image-only?)")
   ```

   An encrypted file needs the password from the user (`reader.decrypt(password)`); never try to guess or break one.

2. **Extract text with page numbers.** Keep the page with the text, so every quote can cite it:

   ```python
   with pdfplumber.open("input.pdf") as pdf:
       pages = {n: (p.extract_text() or "") for n, p in enumerate(pdf.pages, start=1)}
   ```

   Save the result to a text or Markdown file when it is long, and read the part you need. For the whole document as Markdown without page numbers, use the `read-documents` skill. Text from a multi-column page can come out in the wrong order; check against `page.extract_text(layout=True)` or crop to a column with `page.crop((x0, top, x1, bottom))`.

3. **Extract tables.** `page.extract_tables()` returns a list of tables, each a list of rows of cell strings (`None` for an empty cell). Load one into pandas for analysis (the `csv-analysis` skill's rules apply to the data), and check the row count and the header against the page:

   ```python
   import pandas as pd

   with pdfplumber.open("input.pdf") as pdf:
       rows = pdf.pages[2].extract_tables()[0]           # page 3, first table
   df = pd.DataFrame(rows[1:], columns=rows[0])
   df.to_csv("output/table-p3.csv", index=False)
   ```

   A table with no ruling lines may need `page.extract_tables({"vertical_strategy": "text", "horizontal_strategy": "text"})`. A table split across pages is extracted per page and joined by you. Say that table extraction is approximate and was checked against the page.

4. **Merge, split, rotate.** Write to new files:

   ```python
   from pypdf import PdfReader, PdfWriter

   # merge
   merged = PdfWriter()
   for f in ["a.pdf", "b.pdf"]:
       merged.append(f)
   merged.write("output/merged.pdf")

   # split: pages 3 to 5 (1-based) into their own file, rotated a quarter turn clockwise
   reader = PdfReader("input.pdf")
   part = PdfWriter()
   for i in range(2, 5):
       part.add_page(reader.pages[i])
   for page in part.pages:
       page.rotate(90)                                   # multiples of 90, clockwise
   part.write("output/part.pdf")
   ```

   Confirm afterwards that the new file's page count is what was asked for. Merging and splitting keep bookmarks and form fields unevenly; say so if the document has them. pypdf cannot redact: drawing a box over text leaves the text in the file, so do not offer it as redaction.

5. **Fill form fields.** List the fields first, then fill by name:

   ```python
   reader = PdfReader("form.pdf")
   for name, field in (reader.get_fields() or {}).items():
       print(name, field.get("/FT"), field.get("/V"))   # /Tx text, /Btn checkbox or button, /Ch choice

   writer = PdfWriter(clone_from=reader)
   writer.update_page_form_field_values(
       writer.pages[0], {"name": "Ada Lovelace", "agree": "/Yes"}, auto_regenerate=False)
   writer.set_need_appearances_writer(True)             # viewers redraw the filled values
   writer.write("output/form-filled.pdf")
   ```

   `get_fields()` returning nothing means the PDF has no fillable fields (it may be a flat form to print); say so and stop rather than drawing text at guessed positions. Checkbox "on" values differ per form: read the field's allowed states before using `/Yes`. Fill fields only with values the user gave; an unknown value stays blank. Reopen the saved file and print the values to check them.

6. **Report.** Give the output path, what was done, page numbers used (1-based), and anything not extracted, such as scanned pages, or tables or fields that could not be read.
