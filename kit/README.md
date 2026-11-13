# What is in the kit

Every file the install scripts copy is in this folder. [INSTALL.md](../INSTALL.md) says how they are installed.

## Agents

In `agents/*.agent.md`. Copilot hands work to an agent when the job matches its description, or you ask for it by name.

| Agent | What it does |
|---|---|
| `worker` | Any job where only the result is needed and no other agent fits: an investigation across many files or logs, a batch of small tasks, a change in several steps, a draft. Reads, edits and runs commands. |
| `kit-researcher` | Checks a fact about a library, package, API or tool against what is installed: package code and docs, lockfiles, the tool's own `--help`. Returns the answer with its sources. |
| `reader` | Finds facts in this repo's code, logs or command output, with no advice: who calls a function, where a setting is defined, what a log says. Read-only; returns file and line evidence. |
| `verifier` | Checks a finished change by running the commands that show whether it works, and reports PASS or FAIL for each. Never fixes anything. |
| `kit-reviewer` | Reviews a diff, branch or pull request against what it was meant to do, and returns APPROVE or CHANGES NEEDED with each problem at its file and line. Never edits code. |
| `builder` | Makes a fully specified change, runs the command that shows it worked and the tests it touches, and returns the result. Not for design or open-ended work. |
| `data-analyst` | Answers questions about CSV and other tabular files by writing and running pandas or duckdb scripts, with the code behind each number. Never changes the source file. |
| `document-reviewer` | Reviews a Word, PDF or PowerPoint document against a checklist or policy you give it, and returns findings with the page, slide or section and the quoted text. Never edits the document. |

The two `kit-` names keep them apart from Copilot CLI's built-in `research` and `code-review` agents.

**Limits**

- No agent has a web tool, because web search is off in the organization. They work from the repository, installed packages and command output.
- `reader` is read-only by instruction only: it has no edit tool but keeps the shell. Asked directly, it still gave advice in testing.
- An agent Copilot hands work to may not get your rules or the repo's instruction files (in VS Code, a bug means it may get none). Each agent carries its own safety rules; put anything else the task needs in your request.

## Skills

In `skills/<name>/SKILL.md`, with any scripts the skill uses beside it. The install scripts offer skills in packs.

### Code (`code` pack, and every language pack)

| Skill | What it does |
|---|---|
| `build-and-test` | Finds and runs the build, test, lint and format commands the repo itself uses, narrowest first, and reports each result. Never skips or loosens a test to make it pass. |
| `write-tests` | Writes tests in the repo's existing framework, layout and style, runs them, and shows they fail when the behaviour breaks. |
| `api-contract-check` | Finds what changed in an interface others depend on (REST, gRPC, GraphQL, message schemas, client libraries) and who consumes it, and marks each change breaking, safe or unknown. |
| `dependency-upgrade` | Upgrades dependencies one at a time, reading each changelog and running the build and tests after each. Never bumps a major version or a runtime unasked. |
| `sbt-and-play` | Scala pack only. Scala services built with sbt, Play, Akka or Pekko, and Cats Effect or ZIO, matching what the repo already uses. |

### Documents (`documents` pack)

| Skill | What it does | Needs |
|---|---|---|
| `read-documents` | Converts PDF, Word, PowerPoint and Excel files to Markdown before Copilot reads them, because Copilot cannot read those files. The other document skills and `document-reviewer` use it. | Python 3.10+, `pdfplumber`, `python-docx`, `python-pptx`, `openpyxl` |
| `csv-analysis` | Works on CSV files through pandas or duckdb scripts instead of pasting rows into the chat, shows the code behind every number, and never changes the source file. | `pandas`; `duckdb` for large files |
| `pptx` | Creates or edits PowerPoint decks from the company template. Saves to a new file. | `python-pptx` |
| `docx` | Creates, edits or fills Word documents using the template's styles. Saves to a new file. | `python-docx` |
| `pdf` | Extracts text and tables from PDFs, and merges, splits, rotates and fills form fields. | `pdfplumber`, `pypdf` |

**Limits**

- The packages install with `pip`. If pip is blocked on your machine, use the company's internal package mirror.
- These skills do no OCR, so a scanned PDF cannot be read with them.

### Planning and writing (`planning` pack)

| Skill | What it does |
|---|---|
| `spec-interview` | Turns a rough feature idea into a written spec by asking you for real examples of the result and only what the examples cannot settle. |
| `draft-from-examples` | Drafts a new document that matches the structure and voice of finished ones in a folder you point at. |
| `session-capture` | At the end of a session, proposes lines a new session would need in the project's `AGENTS.md`, and writes only the lines you pick. |
| `setup-project` | Fills in a repo's `AGENTS.md` from the repo's README, build files and history, and asks you only what the repo cannot answer. Runs nothing, commits nothing, and never overwrites an `AGENTS.md` the team already wrote. |

## Language rules files

In `instructions/`. Coding guidelines for one stack. Each tells Copilot to follow the repo's own versions, libraries and conventions first and to add no dependency unasked.

| File | Stack | Copilot loads it for |
|---|---|---|
| `springboot.instructions.md` | Spring Boot (Java) | `.java` files |
| `scala.instructions.md` | Scala 2 and 3 | `.scala`, `build.sbt`, `build.sc` |
| `nestjs.instructions.md` | NestJS | `.ts`, `.js`, `.json` files |
| `flutter.instructions.md` | Dart and Flutter | `.dart` files |

## Working rules and templates

In `templates/`.

| File | What it is | Installed as |
|---|---|---|
| `AGENTS.md` | Working rules that keep Copilot on the task it was given. | `~/.copilot/copilot-instructions.md`, by `install-user.py` |
| `project/AGENTS.md` | Starter context for one project, with `<placeholders>` that setup-project fills in. | The repo's `AGENTS.md`, by `install-repo.py` |
| `research/AGENTS.md` | Starter rules for a research folder. | Used by setup-project for a folder of research reports |

## Safety hook

`templates/.github/hooks/deny.json` runs before each tool call and can deny it. It denies force-push, `git reset --hard`, `rm -rf` on a root, home or whole directory, and any use of `.env` or private key files. Only repos set up with `install-repo.py` have it.

**Limits**

- A hook that times out (5 s here) lets the tool call through. A hook that crashes denies it.
- The hook matches text. It stops mistakes, not a determined person.
- It checks the git and `rm` rules only on commands, so editing a file that mentions `git reset --hard` is allowed. The `.env` and key rules apply to every tool, so it also blocks editing `.env` files, not only reading them.
- Its `powershell` command, which Copilot runs on Windows, has not yet been run on Windows, so test it there before relying on it. The cloud agent ignores `powershell` entries and uses the `bash` command.
