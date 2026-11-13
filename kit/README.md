# What is in the kit

This page lists what you can ask Copilot to do once the kit is installed, and what each part is. The [README](../README.md) explains the words used here (agent, skill, pack). [INSTALL.md](../INSTALL.md) explains how to install.

## What you can ask for

Ask in plain words, as you would ask a colleague. You don't need to name an agent or skill: Copilot picks the right one from your request. To pick one yourself, name it ("use the verifier agent").

Agents are installed when you pick them. A skill is installed when you pick its pack.

### Working on code (`code` pack)

| You want to | Ask Copilot, for example | You get back | Done by |
|---|---|---|---|
| Check a change works | "verify my change" | PASS or FAIL for each check, with the output. It never fixes anything. | `verifier` agent |
| Get a review before merging | "review my changes" | APPROVE, or a list of problems, each with its file and line. It never edits code. | `kit-reviewer` agent |
| Make a change you have fully described | "add a `--dry-run` flag to the export script" | The change, and the command that shows it works | `builder` agent |
| Find something in the code or logs | "where is the timeout setting defined?" | The answer with file and line. No advice. | `reader` agent |
| Check how an installed library works | "does the version of axios we use support retries?" | The answer, and where it was found | `kit-researcher` agent |
| Hand off a larger job | "go through these logs and list every distinct error" | The result | `worker` agent |
| Build and run the tests | "build and test this" | Each command run and its result. It never skips or weakens a test to make it pass. | `build-and-test` skill |
| Add tests | "write tests for the new discount rule" | Tests in the repo's existing style, run, and shown to fail if the rule breaks | `write-tests` skill |
| Check an API change won't break other teams | "is my change to the orders API breaking?" | Each change marked breaking, safe or unknown, and who uses it | `api-contract-check` skill |
| Upgrade libraries | "upgrade our dependencies" | One upgrade at a time, built and tested after each. No major versions unless you ask. | `dependency-upgrade` skill |
| Work on a Scala service (`scala` pack) | "add a health-check route" | Code that matches the libraries the repo already uses | `sbt-and-play` skill |

### Documents and data (`documents` pack)

| You want to | Ask Copilot, for example | You get back | Done by |
|---|---|---|---|
| Answer a question about a spreadsheet | "how many orders per month are in sales.csv?" | The numbers, and the script that produced them. Your file is never changed. | `data-analyst` agent, `csv-analysis` skill |
| Read a PDF, Word, PowerPoint or Excel file | "summarise report.pdf" | A summary, with page or slide numbers | `read-documents` skill |
| Check a document against a checklist or policy | "check contract.docx against policy.pdf" | Findings, each with its page or section and the quoted text. It never edits the document. | `document-reviewer` agent |
| Make a slide deck | "make five slides from this summary using template.pptx" | A new `.pptx` file | `pptx` skill |
| Write or fill in a Word document | "fill in this form template with these details" | A new `.docx` file. The original is untouched. | `docx` skill |
| Work with PDFs | "pull the table on page 4 out of invoice.pdf" | The text or table, or a merged, split or filled-in PDF | `pdf` skill |

The document skills need Python 3.10 or later and some Python libraries. Install them once:

```
pip install pdfplumber pypdf python-docx python-pptx openpyxl pandas duckdb
```

### Planning and writing (`planning` pack)

| You want to | Ask Copilot, for example | You get back | Done by |
|---|---|---|---|
| Turn an idea into a written spec | "interview me about the export feature" | A spec file, after it asks you for examples of the result | `spec-interview` skill |
| Write a document like earlier ones | "write a risk assessment like the ones in docs/assessments" | A draft in the same structure and tone | `draft-from-examples` skill |
| Keep what you learned at the end of a chat | "wrap up" | Suggested lines for the repo's notes. Only the ones you pick are saved. | `session-capture` skill |
| Fill in the repo's notes | "set up this repo for Copilot" | `AGENTS.md` filled in from the repo, after asking you only what the code can't tell it. It never overwrites notes your team already wrote. | `setup-project` skill |

## Language guides

A language guide is coding advice for one language. Copilot reads it on its own whenever it works on a file of that type. Each guide tells Copilot to follow the repo's own versions and habits first, and not to add new libraries unless you ask.

| Guide | For | Read when Copilot works on |
|---|---|---|
| `springboot.instructions.md` | Spring Boot (Java) | `.java` files |
| `scala.instructions.md` | Scala 2 and 3 | `.scala`, `build.sbt`, `build.sc` |
| `nestjs.instructions.md` | NestJS | `.ts`, `.js`, `.json` files |
| `flutter.instructions.md` | Dart and Flutter | `.dart` files |

## The safety hook

The safety hook checks every action before Copilot takes it, and stops these:

- **Force-pushing,** which can overwrite other people's work on the server.
- **`git reset --hard`,** which throws away all uncommitted changes.
- **Deleting whole folders** with `rm -rf`.
- **Reading or editing `.env` files and private keys,** where passwords and keys are kept.

Only repos set up with `install-repo.py` have it.

## What it won't do

- **No internet.** Web search is turned off in the organization, so agents work only from your code, installed libraries and command output.
- **Agents may not see your rules.** When Copilot passes a job to an agent, the agent may not get your personal rules or the repo's notes. Each agent has its own safety rules, but put everything else the job needs in your request.
- **`reader` only promises not to change things.** It has no tool for editing files, but it can still run commands. If you ask it directly, it may also give advice.
- **No scanned PDFs.** A PDF that is a photo of pages, with no real text, can't be read.
- **The safety hook catches mistakes, not a determined person.** It looks for words in a command, so a reworded command can get past it. If it takes longer than 5 seconds, the action is allowed. If it crashes, the action is blocked.
- **The safety hook also blocks editing `.env` files,** not only reading them.
- **The safety hook is untested on Windows.** Its Windows version has not been run on Windows yet, so test it there before relying on it.

## Where the files are

| Part | Folder in `kit/` |
|---|---|
| Agents | `agents/` |
| Skills (each in its own folder, with any scripts it uses) | `skills/` |
| Language guides | `instructions/` |
| Your personal rules | `templates/AGENTS.md` (installed as `~/.copilot/copilot-instructions.md`) |
| Starter notes for a repo, and for a folder of research reports | `templates/project/AGENTS.md`, `templates/research/AGENTS.md` |
| Safety hook | `templates/.github/hooks/deny.json` |

The two `kit-` agent names keep them apart from Copilot CLI's own `research` and `code-review` agents.
