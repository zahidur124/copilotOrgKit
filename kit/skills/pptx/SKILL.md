---
name: pptx
description: Create or edit PowerPoint (.pptx) slide decks with python-pptx, starting from the company template when one is given and using its layouts and placeholders. Use when the user asks for a presentation, slides or a deck to be built, changed or filled from a template. To read an existing deck, use the read-documents skill.
---

# pptx

Needs: Python 3 with `python-pptx` (`pip install python-pptx`). To read an existing deck you also need the packages of the `read-documents` skill (`pip install pdfplumber python-docx python-pptx openpyxl`; only `python-pptx` is used for a deck). If pip is blocked, use the company's internal package mirror (`pip install --index-url <url> python-pptx`; ask the platform team for the URL).

The deck is made by a script you show and run. The script reads the template and saves to a new file. It never saves over the template or over the user's original deck.

1. **Find the template and the content.** Use the template the user names (a `.pptx` or `.potx`). With none named, look for one in the repo or in the folder the user points at, and ask if there are several. With no company template at all, say so and use python-pptx's default, which is plain; do not invent a house style. For the content, use what the user gave. A fact, figure or name you do not have goes in as `[TODO: what is needed]` on the slide, never a guess.

2. **Read an existing deck first.** To edit or build on a deck, convert it with the `read-documents` skill and read the Markdown (each slide is a `## Slide N` section with its title, text, tables and speaker notes). Then list its layouts as in step 3. Say what the deck holds before changing it.

3. **Look at the template's layouts and placeholders before writing.** python-pptx cannot open a `.potx`; if the template is one, ask the user to open it in PowerPoint and use File > Save As > PowerPoint Presentation, or convert a copy:

   ```python
   import zipfile

   def potx_to_pptx(src, dst):
       with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
           for item in zi.infolist():
               data = zi.read(item.filename)
               if item.filename == "[Content_Types].xml":
                   data = data.replace(b"presentationml.template.main+xml", b"presentationml.presentation.main+xml")
               zo.writestr(item, data)
   ```

   Then print what each layout offers, so the layout is chosen from facts:

   ```python
   from pptx import Presentation

   prs = Presentation("template.pptx")
   for i, layout in enumerate(prs.slide_layouts):
       print(i, layout.name)
       for ph in layout.placeholders:
           print("   ", ph.placeholder_format.idx, ph.placeholder_format.type, ph.name)
   ```

4. **Build slides from layouts, and fill placeholders.** Pick the layout whose name and placeholders fit the slide (title, content, two content, section header, picture). Put text in the placeholders, not in new text boxes, because placeholders carry the template's fonts, sizes, colours and positions, and a free-placed box drifts from the brand and from the outline view.

   ```python
   slide = prs.slides.add_slide(prs.slide_layouts[1])      # "Title and Content"
   slide.shapes.title.text = "Order volume grew 12% in Q3"
   body = slide.placeholders[1].text_frame
   body.text = "Online orders drove the rise"              # first paragraph
   sub = body.add_paragraph(); sub.text = "Stores were flat"; sub.level = 1
   slide.notes_slide.notes_text_frame.text = "Speaker notes go here."
   ```

   - A picture goes in a picture placeholder with `placeholder.insert_picture("chart.png")`. A table goes in a table placeholder with `insert_table(rows, cols)`. When the layout has no such placeholder, `shapes.add_table` or `shapes.add_picture` is allowed, placed inside the area of the layout's content placeholder, which you then delete.
   - Delete a placeholder the slide does not use (`ph._element.getparent().remove(ph._element)`), so no empty "Click to add text" box is left.
   - Do not set fonts, sizes or colours on runs. The template sets them. If something must differ, say so and ask.
   - Charts from data: make them with python-pptx's `shapes.add_chart` using the template's colours, or insert an image the user supplied.

5. **Keep text short.** These limits hold unless the user or template says otherwise; when the content does not fit, split the slide rather than shrink the text.
   - A title is a statement of the point in 12 words or fewer, on one or two lines.
   - At most 6 bullets per slide, each 15 words or fewer, with no more than two levels.
   - One message per slide. Detail that does not fit goes in the speaker notes.
   - A table of more than about 6 rows by 5 columns goes on its own slide or in an appendix.
   - Never turn a slide into a paragraph of text, and never paste a document's text onto slides.

6. **Edit an existing deck in place only in the copy.** Open the original, change it, and save under a new name (for example `deck-v2.pptx` or `deck-edited.pptx`). To change text but keep its look, set `run.text` on the existing runs rather than `text_frame.text`, which resets the formatting. To remove a slide:

   ```python
   def delete_slide(prs, index):
       sldIdLst = prs.slides._sldIdLst
       sldId = sldIdLst[index]
       prs.part.drop_rel(sldId.rId)
       sldIdLst.remove(sldId)
   ```

   To start a new deck from a template that has sample slides, delete those first (highest index first).

7. **Save to a new file and check it.** `prs.save("output/deck.pptx")`. Then reopen it, count the slides, and read it back with the `read-documents` skill to confirm every slide has its title and text and that no `[TODO` was left unmentioned. If LibreOffice is installed, `soffice --headless --convert-to pdf deck.pptx` shows how it renders; text running off a slide shows there. State what you could not check, such as how it looks in PowerPoint.

8. **Report.** Give the output path, the template used, a line per slide (layout and title), and every `[TODO]` left.
