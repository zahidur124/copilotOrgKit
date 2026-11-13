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
| `data-analyst` | Answers questions about CSV and other tabular files by writing and running pandas or duckdb scripts, with the code behind each number. Uses csv-analysis. Never changes the source file. |
| `document-reviewer` | Reviews a Word, PDF or PowerPoint document against a checklist or policy you give it, and returns findings with the page, slide or section and the quoted text. Reads through read-documents and never edits the document. |

The two `kit-` names keep them apart from Copilot CLI's built-in `research` and `code-review` agents.

**Limits**

- No agent has a web tool, because web search is off in the organization. `kit-researcher` and `worker` work from the repository, installed packages and command output.
- `reader`'s "no advice" and "read-only commands" rules are only instructions. Asked directly, it still gave advice in testing. Its tool list has no edit tool, but it keeps the shell, so nothing but the instruction stops a command that writes.
- Every agent sets `include-custom-instructions: true`, so when the main agent hands it work in Copilot CLI it still reads the repo's instruction files. Copilot's reference names only repository instruction files, so the rules in `~/.copilot/copilot-instructions.md` may not reach a handed-off agent. A session started with `--no-custom-instructions` gives no agent any rules. In VS Code, a reported bug (microsoft/vscode#343696) means a handed-off custom agent may get no instruction files at all. So each agent carries its own safety rules, and the main session's task note carries anything else the work depends on.

## Skills

In `skills/<name>/SKILL.md`. A skill's other files, such as `csv-analysis/profile_csv.py`, are installed beside its `SKILL.md`. The install scripts offer skills in packs.

### Code (`code` pack, and every language pack)

| Skill | What it does |
|---|---|
| `build-and-test` | Finds the build, test, lint and format commands the repo itself uses (its `AGENTS.md`, README and CI config first, then its build files, wrapper and lockfile) for Node.js, Java, Scala, Python and Flutter. Runs the narrowest check first and reports each command and its result. Never skips or loosens a test to make it pass, and never changes registry settings when a download is blocked. |
| `write-tests` | Writes tests that copy the repo's existing framework, layout, naming and helpers: Jest or Vitest, JUnit 5 and Spring test slices with Testcontainers, ScalaTest, MUnit or ZIO Test, pytest, and Flutter unit, widget and golden tests. Runs them and, where it may edit code, shows they fail when the behaviour breaks. |
| `api-contract-check` | Before or after a change to an interface others depend on (REST and OpenAPI, protobuf and gRPC, GraphQL, Kafka or queue message schemas, shared client libraries), finds what changed and who consumes it, including Flutter app models, and marks each change breaking, safe or unknown. Consumers in repos it cannot see are listed as unknown, not safe. |
| `dependency-upgrade` | Upgrades dependencies one at a time across npm, pnpm, yarn, Maven, Gradle, sbt, pip, Poetry, uv and pub, reading each changelog from the local package cache, and runs the build and tests after each one. Never bumps a major version or a runtime unasked. For Java and Spring Boot major upgrades it points to Microsoft's GitHub Copilot modernization plugin, which the organization has to allow. |
| `sbt-and-play` | Scala pack only. Scala services built with sbt: multi-module builds, adding dependencies and cross-building, Play Framework, Akka or Apache Pekko actors and streams, and Cats Effect or ZIO code, always matching what the repo already uses. Mentions the Metals MCP server, if the organization allows MCP. |

### Documents (`documents` pack)

| Skill | What it does | Needs |
|---|---|---|
| `read-documents` | Converts PDF, Word, PowerPoint and Excel files to Markdown with its own script, `to_markdown.py`, before Copilot reads them, because Copilot cannot read those binary files. Labels each PDF page and slide, keeps Word headings, lists and tables, and cuts long Excel sheets (and says so). The other document skills and `document-reviewer` use it for reading. | Python 3.10+, `pdfplumber`, `python-docx`, `python-pptx`, `openpyxl` |
| `csv-analysis` | Works on CSV files through pandas or duckdb scripts instead of pasting rows into the chat. Profiles the file first (delimiter, encoding, columns, types, row count, nulls; `profile_csv.py` does this without printing any values), shows the code behind every number, and never changes the source file. | `pandas`; `duckdb` for large files |
| `pptx` | Creates or edits PowerPoint decks, starting from the company template and using its layouts and placeholders, with limits on text per slide. Saves to a new file. | `python-pptx` |
| `docx` | Creates, edits or fills Word documents using the template's named styles, not direct formatting. Saves to a new file. | `python-docx` |
| `pdf` | Extracts text and tables from PDFs, and merges, splits, rotates and fills form fields. | `pdfplumber`, `pypdf` |

**Limits**

- The packages install with `pip`. If pip is blocked on your machine, use the company's internal package mirror.
- `to_markdown.py` imports only the package a file's type needs, so a missing package is named when that type is converted.
- These skills do no OCR, so a scanned PDF cannot be read with them.

### Planning and writing (`planning` pack)

| Skill | What it does |
|---|---|
| `spec-interview` | Turns a rough feature idea into a written spec by asking you for real examples of the result, working out the steps that produce them, and asking only what the steps cannot settle. |
| `draft-from-examples` | Drafts a new document that matches the structure and voice of finished ones in a folder you point at, such as assessments, policies, reports or letters. |
| `session-capture` | At the end of a session, summarizes what was done and proposes lines a new session would need in the project's `AGENTS.md`. Writes only the lines you pick. |
| `setup-project` | Fills in a repo's `AGENTS.md` from the repo itself. See below. |

### setup-project

Ask Copilot in a repo to "set up this repo for Copilot". The skill:

- reads the repo (README, build files, top-level folders, `git log`) to find out what the project is and does, and runs nothing;
- asks only what the repo cannot answer, usually who uses it, what is out of scope, and conventions the code does not show;
- fills in the `AGENTS.md` that `install-repo.py` wrote, or writes one, using the research template for a folder of research reports;
- never overwrites an `AGENTS.md` the team already wrote, and proposes lines to add instead;
- commits nothing and installs no agents; the install scripts do that.

It carries both starter templates in its own folder (`skills/setup-project/templates/`), so it works wherever it is installed. After pulling a new kit version, run the install script again and replace the files that differ, so the skill's copies match the kit.

## Language rules files

In `instructions/`. These are coding guidelines for one stack: structure, dependency injection, configuration and secrets, errors, validation, data access, async code, logging, security, and the stack's common traps. Each tells Copilot to follow the repo's own versions, libraries and conventions first, to add no dependency unasked, and to use the skills for builds, tests and upgrades.

| File | Stack | Copilot loads it for |
|---|---|---|
| `springboot.instructions.md` | Spring Boot (Java) | `.java` files |
| `scala.instructions.md` | Scala 2 and 3 | `.scala`, `build.sbt`, `build.sc` |
| `nestjs.instructions.md` | NestJS | `.ts`, `.js`, `.json` files |
| `flutter.instructions.md` | Dart and Flutter | `.dart` files |

`install-repo.py` puts them in the repo's `.github/instructions/`. `install-user.py` does not install them, because language rules belong to a repo.

## Working rules and templates

In `templates/`.

| File | What it is | Installed as |
|---|---|---|
| `AGENTS.md` | Working rules that keep Copilot on the task it was given: the task, scope, claims, changes, handing work to agents, git, instruction files. | `~/.copilot/copilot-instructions.md`, by `install-user.py` |
| `project/AGENTS.md` | Starter context for one project: what it is and does, its layout and build and test commands, what is out of scope, its own rules, a per-branch state file, a goal file for long tasks, the agents installed in the repo, and how work lands. | The repo's `AGENTS.md`, by `install-repo.py`, with `<placeholders>` that setup-project fills in |
| `research/AGENTS.md` | Starter rules for a research folder. | Used by setup-project for a folder of research reports |

## Safety hook

`templates/.github/hooks/deny.json` is a `preToolUse` hook: it runs before each tool call and can deny it. It denies force-push, `git reset --hard`, `rm -rf` on a root, home or whole directory, and any use of `.env` or private key files. `install-repo.py` installs it in each repo. A repo not set up with `install-repo.py` has no hook, so Copilot runs there without it.

**Limits**

- A hook that times out (5 s here) lets the tool call through. A hook that crashes denies it.
- The hook matches text. It stops mistakes, not a determined person.
- It checks the git and `rm` rules only on commands, so editing a file that mentions `git reset --hard` is allowed. The `.env` and key rules apply to every tool, so it also blocks editing `.env` files, not only reading them.
- It has a `bash` command, which runs on macOS, Linux and the cloud agent, and a `powershell` command with the same rules, which Copilot runs on Windows. The `powershell` command is written for Windows PowerShell 5.1 and PowerShell 7 but has not yet been run on Windows, so test it there before relying on it. The cloud agent ignores `powershell` entries.
