# Skills

A skill is a set of step-by-step instructions Copilot follows for one kind of task, such as writing tests. Each skill is a folder here with a `SKILL.md` file and any scripts it uses. Skills come in packs: you get a skill by picking its pack when you install (see [INSTALL.md](../../INSTALL.md#packs)).

You don't need to name a skill. Copilot uses the right one when your request matches it.

## Working on code (`code` pack)

The `code` pack's skills also come with every language pack.

| Skill | Ask Copilot, for example | You get back |
|---|---|---|
| `build-and-test` | "build and test this" | Each command run and its result. It never skips or weakens a test to make it pass. |
| `write-tests` | "write tests for the new discount rule" | Tests in the repo's existing style, run, and shown to fail if the rule breaks |
| `api-contract-check` | "is my change to the orders API breaking?" | Each change marked breaking, safe or unknown, and who uses it |
| `dependency-upgrade` | "upgrade our dependencies" | One upgrade at a time, built and tested after each. No major versions unless you ask. |
| `sbt-and-play` (`scala` pack only) | "add a health-check route" | Code for a Scala service that matches the libraries the repo already uses |

## Documents and data (`documents` pack)

| Skill | Ask Copilot, for example | You get back |
|---|---|---|
| `read-documents` | "summarise report.pdf" | A summary, with page or slide numbers. Works for PDF, Word, PowerPoint and Excel files. |
| `csv-analysis` | "how many orders per month are in sales.csv?" | The numbers, and the script that produced them. Your file is never changed. |
| `pptx` | "make five slides from this summary using template.pptx" | A new `.pptx` file |
| `docx` | "fill in this form template with these details" | A new `.docx` file. The original is untouched. |
| `pdf` | "pull the table on page 4 out of invoice.pdf" | The text or table, or a merged, split or filled-in PDF |

These skills need Python 3.10 or later and some Python libraries. Install them once:

```
pip install pdfplumber pypdf python-docx python-pptx openpyxl pandas duckdb
```

If `pip` is blocked, use the company's internal package mirror. A scanned PDF (a photo of pages, with no real text) can't be read.

## Planning and writing (`planning` pack)

| Skill | Ask Copilot, for example | You get back |
|---|---|---|
| `spec-interview` | "interview me about the export feature" | A spec file, after it asks you for examples of the result |
| `draft-from-examples` | "write a risk assessment like the ones in docs/assessments" | A draft in the same structure and tone |
| `session-capture` | "wrap up" | Suggested lines for the repo's notes. Only the ones you pick are saved. |
| `setup-project` | "set up this repo for Copilot" | The repo's notes (`AGENTS.md`) filled in from the repo, after asking you only what the code can't tell it. It never overwrites notes your team already wrote. |
