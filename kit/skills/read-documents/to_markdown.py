#!/usr/bin/env python3
"""Convert a PDF, Word (.docx), PowerPoint (.pptx) or Excel (.xlsx) file to Markdown so it can be read as text.

  python to_markdown.py report.docx                 Markdown to standard output
  python to_markdown.py report.docx -o report.md    Markdown to a file
  python to_markdown.py data.xlsx --max-rows 500    Excel only: rows shown per sheet (default 200)

The source file is only read, never changed. Needs Python 3.10 or later. Each format needs one package, which is
imported only when a file of that type is converted:
  .pdf   pdfplumber      .docx  python-docx      .pptx  python-pptx      .xlsx  openpyxl
No OCR: a PDF page that is a picture of text comes out empty and is labelled as such.
"""
from __future__ import annotations

import argparse
import datetime
import importlib
import sys
from pathlib import Path

PACKAGES = {
    ".pdf": ("pdfplumber", "pdfplumber"),
    ".docx": ("docx", "python-docx"),
    ".pptx": ("pptx", "python-pptx"),
    ".xlsx": ("openpyxl", "openpyxl"),
}
LEGACY = {".doc": ".docx", ".ppt": ".pptx", ".xls": ".xlsx"}
MAX_COLUMNS = 50
NO_TEXT = ("_No text found on this page. It may be scanned (a picture of a page) and need OCR, "
           "which this skill does not do._")


class ConversionError(Exception):
    pass


def load(module, pip_name):
    """Import a package when it is first needed; say which one to install when it is missing."""
    try:
        return importlib.import_module(module)
    except ImportError:
        raise ConversionError(f"this file type needs the package {pip_name}, which is not installed. "
                              f"Install it with: python -m pip install {pip_name}") from None


# ---------- shared helpers ----------

def cell_text(value):
    if value is None:
        return ""
    if isinstance(value, datetime.datetime):
        return value.date().isoformat() if value.time() == datetime.time(0) else value.isoformat(sep=" ")
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def clean_cell(value):
    """One table cell as a single line: line breaks become <br>, and | is escaped."""
    parts = [p.strip() for p in cell_text(value).replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    return "<br>".join(p for p in parts if p).replace("|", "\\|")


def markdown_table(rows):
    """Rows of cell values -> Markdown table lines. The first row is the header. Empty rows are dropped."""
    rows = [[clean_cell(c) for c in row] for row in rows]
    rows = [r for r in rows if any(r)]
    if not rows:
        return []
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    lines = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
    lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return lines


# ---------- PDF ----------

def convert_pdf(path, options):
    pdfplumber = load(*PACKAGES[".pdf"])
    out = []
    try:
        pdf = pdfplumber.open(path)
    except Exception as exc:  # encrypted, damaged, not a PDF
        raise ConversionError(f"could not open the PDF ({type(exc).__name__}: {exc}). "
                              "A password-protected file needs its password removed first.") from None
    with pdf:
        for number, page in enumerate(pdf.pages, start=1):
            out += [f"## Page {number}", ""]
            tables = sorted(page.find_tables(), key=lambda t: t.bbox[1])
            boxes = [t.bbox for t in tables]

            def segment(index, boxes=boxes):
                """Text outside every table that lies below `index` tables and above the next one."""
                def keep(obj):
                    if obj.get("object_type") != "char":
                        return True
                    x = (obj["x0"] + obj["x1"]) / 2
                    y = (obj["top"] + obj["bottom"]) / 2
                    if any(x0 <= x <= x1 and top <= y <= bottom for x0, top, x1, bottom in boxes):
                        return False
                    return sum(1 for box in boxes if box[1] <= y) == index
                return (page.filter(keep).extract_text() or "").strip()

            blocks = []
            for index in range(len(tables) + 1):
                text = segment(index)
                if text:
                    blocks += [text, ""]
                if index < len(tables):
                    lines = markdown_table(tables[index].extract())
                    if lines:
                        blocks += lines + [""]
            out += blocks or [NO_TEXT, ""]
    return out


# ---------- DOCX ----------

def numbering_kinds(document):
    """Map (numId, ilvl) -> 'bullet' or 'number' from the document's numbering part."""
    kinds = {}
    try:
        root = document.part.numbering_part.element
    except Exception:
        return kinds
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    w = "{%s}" % ns["w"]
    abstract = {}
    for a in root.findall("w:abstractNum", ns):
        for lvl in a.findall("w:lvl", ns):
            fmt = lvl.find("w:numFmt", ns)
            abstract[(a.get(w + "abstractNumId"), lvl.get(w + "ilvl"))] = fmt.get(w + "val") if fmt is not None else "bullet"
    for num in root.findall("w:num", ns):
        ref = num.find("w:abstractNumId", ns)
        if ref is None:
            continue
        for (aid, ilvl), fmt in abstract.items():
            if aid == ref.get(w + "val"):
                kinds[(num.get(w + "numId"), ilvl)] = "bullet" if fmt == "bullet" else "number"
    return kinds


def docx_paragraph_lines(paragraph, kinds, counters):
    text = paragraph.text.strip()
    if not text:
        return []
    style = (paragraph.style.name if paragraph.style is not None else "") or ""
    lowered = style.lower()
    if lowered == "title":
        counters.clear()
        return ["# " + text, ""]
    if lowered.startswith("heading ") and lowered[8:].strip().isdigit():
        counters.clear()
        level = min(max(int(lowered[8:].strip()), 1), 6)
        return ["#" * level + " " + text, ""]
    w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    num_pr = paragraph._p.find(f"{w}pPr/{w}numPr")
    kind, level, num_id = None, 0, None
    if num_pr is not None:
        id_el, lvl_el = num_pr.find(w + "numId"), num_pr.find(w + "ilvl")
        num_id = id_el.get(w + "val") if id_el is not None else None
        ilvl = lvl_el.get(w + "val") if lvl_el is not None else "0"
        if num_id != "0":  # numId 0 means "no list"
            kind, level = kinds.get((num_id, ilvl), "bullet"), int(ilvl)
    if kind is None and lowered.startswith("list"):
        kind = "number" if "number" in lowered else "bullet"
        tail = lowered.split()[-1]
        level = int(tail) - 1 if tail.isdigit() else 0
    if kind is None:
        counters.clear()
        return [text, ""]
    indent = "  " * level
    if kind == "number":
        key = (num_id, level)
        counters[key] = counters.get(key, 0) + 1
        for deeper in [k for k in counters if k[1] > level and k[0] == num_id]:
            del counters[deeper]
        return [f"{indent}{counters[key]}. {text}"]
    return [f"{indent}- {text}"]


def convert_docx(path, options):
    docx = load(*PACKAGES[".docx"])
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    try:
        document = docx.Document(str(path))
    except Exception as exc:
        raise ConversionError(f"could not open the Word file ({type(exc).__name__}: {exc}).") from None
    kinds = numbering_kinds(document)
    counters = {}
    out = []
    in_list, last_marker = False, None
    for element in document.element.body.iterchildren():
        tag = element.tag.rsplit("}", 1)[-1]
        if tag == "p":
            lines = docx_paragraph_lines(Paragraph(element, document), kinds, counters)
            if not lines:
                continue
            is_item = lines[-1] != ""
            marker = lines[0].lstrip()[:1].isdigit() if is_item else None  # numbered or bulleted
            if (is_item != in_list or (is_item and marker != last_marker)) and out and out[-1] != "":
                out.append("")  # a blank line before a list starts, between lists of a different kind, and after one ends
            out += lines
            in_list, last_marker = is_item, marker
        elif tag == "tbl":
            if in_list:
                out.append("")
                in_list = False
            counters.clear()
            table = Table(element, document)
            rows = [[cell.text for cell in row.cells] for row in table.rows]
            lines = markdown_table(rows)
            if lines:
                out += lines + [""]
    if in_list:
        out.append("")
    return out


# ---------- PPTX ----------

def pptx_text_lines(shape, pptx_enums):
    """Lines for a shape's text frame. Body placeholders and paragraphs with a bullet become list items."""
    lines = []
    a = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    is_body = False
    if shape.is_placeholder:
        is_body = shape.placeholder_format.type in pptx_enums["body"]
    for paragraph in shape.text_frame.paragraphs:
        text = "".join(run.text for run in paragraph.runs).strip() or paragraph.text.replace("\v", " ").strip()
        text = text.replace("\v", " ")
        if not text:
            continue
        p_pr = paragraph._p.find(a + "pPr")
        explicit = p_pr is not None and (p_pr.find(a + "buChar") is not None or p_pr.find(a + "buAutoNum") is not None)
        none = p_pr is not None and p_pr.find(a + "buNone") is not None
        if (explicit or is_body) and not none:
            lines.append("  " * paragraph.level + "- " + text)
        elif paragraph.level:
            lines.append("  " * paragraph.level + "- " + text)
        else:
            lines.append(text)
    return lines


def pptx_shape_lines(shapes, title_shape, pptx_enums):
    out = []
    MSO = pptx_enums["MSO_SHAPE_TYPE"]
    for shape in shapes:
        if title_shape is not None and shape.shape_id == title_shape.shape_id:
            continue
        if shape.is_placeholder and shape.placeholder_format.type in pptx_enums["skip"]:
            continue
        if shape.shape_type == MSO.GROUP:
            out += pptx_shape_lines(shape.shapes, title_shape, pptx_enums)
        elif getattr(shape, "has_table", False) and shape.has_table:
            rows = [[cell.text for cell in row.cells] for row in shape.table.rows]
            table = markdown_table(rows)
            if table:
                out += table + [""]
        elif getattr(shape, "has_chart", False) and shape.has_chart:
            out += ["_[A chart is here; its picture was not read.]_", ""]
        elif shape.shape_type == MSO.PICTURE:
            alt = (shape._element.xpath("./p:nvPicPr/p:cNvPr/@descr") or [""])[0].strip()
            out += [f"_[A picture is here; it was not read. Alt text: {alt}]_" if alt else
                    "_[A picture is here; it was not read.]_", ""]
        elif getattr(shape, "has_text_frame", False) and shape.has_text_frame:
            lines = pptx_text_lines(shape, pptx_enums)
            if lines:
                out += lines + [""]
    return out


def convert_pptx(path, options):
    pptx = load(*PACKAGES[".pptx"])
    from pptx.enum.shapes import MSO_SHAPE_TYPE, PP_PLACEHOLDER

    enums = {
        "MSO_SHAPE_TYPE": MSO_SHAPE_TYPE,
        "body": {PP_PLACEHOLDER.BODY, PP_PLACEHOLDER.OBJECT},
        "skip": {PP_PLACEHOLDER.SLIDE_NUMBER, PP_PLACEHOLDER.DATE, PP_PLACEHOLDER.FOOTER},
    }
    try:
        presentation = pptx.Presentation(str(path))
    except Exception as exc:
        raise ConversionError(f"could not open the PowerPoint file ({type(exc).__name__}: {exc}).") from None
    out = []
    for number, slide in enumerate(presentation.slides, start=1):
        out += [f"## Slide {number}", ""]
        title_shape = slide.shapes.title
        title = title_shape.text_frame.text.strip().replace("\v", " ") if title_shape is not None else ""
        if title:
            out += [f"### {title}", ""]
        out += pptx_shape_lines(slide.shapes, title_shape, enums)
        if slide.has_notes_slide:
            notes = slide.notes_slide.notes_text_frame
            notes_text = notes.text.strip() if notes is not None else ""
            if notes_text:
                out += ["### Notes", "", notes_text, ""]
    return out


# ---------- XLSX ----------

def convert_xlsx(path, options):
    openpyxl = load(*PACKAGES[".xlsx"])
    limit = options.max_rows
    try:
        workbook = openpyxl.load_workbook(str(path), read_only=True, data_only=True)
    except Exception as exc:
        raise ConversionError(f"could not open the Excel file ({type(exc).__name__}: {exc}).") from None
    out = []
    try:
        for sheet in workbook.worksheets:
            out += [f"## Sheet {sheet.title}", ""]
            rows, truncated = [], False
            for row in sheet.iter_rows(values_only=True):
                if not any(v is not None and str(v).strip() != "" for v in row):
                    continue
                if len(rows) >= limit:
                    truncated = True
                    break
                rows.append(row)
            if not rows:
                out += ["_This sheet is empty._", ""]
                continue
            width = max(max((i for i, v in enumerate(r, start=1) if v is not None and str(v).strip() != ""), default=0)
                        for r in rows)
            cut_columns = width > MAX_COLUMNS
            width = min(width, MAX_COLUMNS)
            out += markdown_table([list(r[:width]) for r in rows]) + [""]
            if cut_columns:
                out += [f"_Only the first {MAX_COLUMNS} columns are shown._", ""]
            if truncated:
                out += [f"_Truncated: only the first {limit} non-empty rows are shown and the sheet has more. "
                        "Use pandas or duckdb (the csv-analysis approach) for the whole sheet, "
                        "or run this script again with a larger --max-rows._", ""]
    finally:
        workbook.close()
    return out


CONVERTERS = {".pdf": convert_pdf, ".docx": convert_docx, ".pptx": convert_pptx, ".xlsx": convert_xlsx}


def main():
    parser = argparse.ArgumentParser(description="Convert a PDF, .docx, .pptx or .xlsx file to Markdown.")
    parser.add_argument("file", help="the file to convert")
    parser.add_argument("-o", "--output", help="write the Markdown to this file (default: standard output)")
    parser.add_argument("--max-rows", type=int, default=200, metavar="N",
                        help="Excel only: most non-empty rows shown per sheet (default 200)")
    args = parser.parse_args()
    if args.max_rows < 1:
        parser.error("--max-rows must be at least 1")

    path = Path(args.file)
    ext = path.suffix.lower()
    try:
        if ext in LEGACY:
            raise ConversionError(f"{ext} is an old binary format this script cannot read. "
                                  f"Save the file as {LEGACY[ext]} in its own application and convert that.")
        if ext not in CONVERTERS:
            raise ConversionError(f"unsupported file type {ext or '(no extension)'!r}. "
                                  f"Supported: {', '.join(sorted(CONVERTERS))}.")
        if not path.is_file():
            raise ConversionError(f"no such file: {path}")
        lines = CONVERTERS[ext](path, args)
    except ConversionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    text = "\n".join(lines).rstrip() + "\n"
    if args.output:
        out_path = Path(args.output)
        if out_path.resolve() == path.resolve():
            print("error: the output path is the source file; choose a different -o path", file=sys.stderr)
            sys.exit(1)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {out_path} ({len(lines)} lines)", file=sys.stderr)
    else:
        sys.stdout.reconfigure(encoding="utf-8", newline="\n")
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
