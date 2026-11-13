---
name: docx
description: Create or edit Word (.docx) documents with python-docx, using the template's named styles instead of direct formatting, and fill in existing templates, saving to a new file so the original is untouched. Use when the user asks for a Word document, report, letter or form to be written, changed or filled from a template. To read an existing document, use the read-documents skill.
---

# docx

Needs: Python 3 with `python-docx` (`pip install python-docx`). To read an existing document you also need the `read-documents` skill, whose script uses the same `python-docx` package. If pip is blocked, use the company's internal package mirror (`pip install --index-url <url> python-docx`; ask the platform team for the URL).

The document is made by a script you show and run. The script opens the template or original, and saves to a new file. It never saves over the template or over the user's original.

1. **Find the template and the content.** Use the template or document the user names (`.docx`; python-docx cannot open `.dotx`, so ask the user to save a `.docx` copy from Word). With none named, look in the repo or the folder the user points at, and ask if there are several. With no company template, python-docx's default is plain; say so and do not invent a house style. A fact, name or figure you do not have goes in as `[TODO: what is needed]`, never a guess.

2. **Read an existing document first.** To edit or fill a document, convert it with the `read-documents` skill and read the Markdown, so you know its headings, tables and wording before you change anything.

3. **List the template's styles before writing.** Names differ from template to template, and a style that is not there makes python-docx raise `KeyError`.

   ```python
   from docx import Document
   from docx.enum.style import WD_STYLE_TYPE

   doc = Document("template.docx")
   for s in doc.styles:
       if s.type in (WD_STYLE_TYPE.PARAGRAPH, WD_STYLE_TYPE.CHARACTER, WD_STYLE_TYPE.TABLE) and not s.hidden:
           print(s.type, s.name)
   ```

4. **Use named styles, not direct formatting.** Headings, body text, lists, quotes, captions and tables get their look from a style, so the document follows the template and its table of contents, navigation pane and later restyling still work.

   ```python
   doc.add_paragraph("Quarterly report", style="Title")
   doc.add_heading("Summary", level=1)                       # uses the Heading 1 style
   doc.add_paragraph("Orders grew in Q3.", style="Normal")
   doc.add_paragraph("Online orders drove the rise", style="List Bullet")
   table = doc.add_table(rows=1, cols=3, style="Table Grid")  # a table style from step 3
   ```

   - Do not set fonts, sizes, colours, bold for headings or manual spacing on runs or paragraphs, and do not fake a heading with bold body text. If the template has no style for what you need, say so and ask, or use the closest and tell the user.
   - Use `run.bold` or `run.italic` only for emphasis inside a sentence. Set `run.style = "Strong"` or `"Emphasis"` when the template has those character styles.
   - A page break is `doc.add_page_break()`. Do not use empty paragraphs for spacing.
   - A table of contents, page numbers and cross-references are fields that Word fills in; python-docx cannot compute them. If the template has a table of contents, tell the user to right-click it and choose Update Field.

5. **Fill an existing template.** Find what to fill by reading the Markdown and walking the document: `doc.paragraphs`, `doc.tables`, section headers and footers (`doc.sections[0].header`). Text in Word is split into runs, so a placeholder like `{{client}}` may be spread over several. To replace it and keep its look, put the new text in the first run that holds part of it and empty the rest:

   ```python
   def replace_in_paragraph(par, old, new):
       if old not in par.text:
           return False
       runs = par.runs
       text = "".join(r.text for r in runs).replace(old, new)
       runs[0].text = text
       for r in runs[1:]:
           r.text = ""
       return True
   ```

   This keeps the first run's formatting for the whole paragraph, so check a paragraph that mixed formatting. Walk `doc.paragraphs`, every `table.cell(...).paragraphs` and the headers and footers, and count the replacements per placeholder. A placeholder with zero replacements is reported, not skipped. Content controls (form fields) and text boxes are not reached by `doc.paragraphs`; say so if the template has them.

6. **Save to a new file and check it.** `doc.save("output/report.docx")`, never the input path. Then convert the saved file with the `read-documents` skill and read it: every placeholder is filled, no `{{` or `[TODO` is left unmentioned, headings are in order, and tables have their rows. State what you could not check, such as page breaks and layout in Word.

7. **Report.** Give the output path, the template or original used, the styles used, the replacements made (count per placeholder), and every `[TODO]` or unfilled placeholder left.

Not covered: comments, tracked changes and content controls. python-docx has no support for them, so do not promise to add or resolve them.
