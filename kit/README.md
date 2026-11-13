# Copilot kit

Optional agents, skills, working rules, language rules files and a safety hook for GitHub Copilot. Each developer chooses whether to install them; nothing is pushed to any repo.

| Path | What it is |
|---|---|
| `agents/*.agent.md` | 8 custom agents: worker, kit-researcher, reader, verifier, kit-reviewer, builder, data-analyst, document-reviewer. The two `kit-` names keep them apart from Copilot CLI's built-in `research` and `code-review` agents. |
| `skills/*/SKILL.md` | 14 skills: draft-from-examples, spec-interview, session-capture, setup-project, read-documents, csv-analysis, pptx, docx, pdf, build-and-test, write-tests, api-contract-check, dependency-upgrade, sbt-and-play. The install scripts offer them in packs (see Install). A skill's other files (such as `csv-analysis/profile_csv.py` and `read-documents/to_markdown.py`) are installed beside its `SKILL.md`. |
| `skills/build-and-test/SKILL.md` | Finds the build, test, lint and format commands a repo itself uses (its `AGENTS.md`, README and CI config first, then its build files, wrapper and lockfile) for Node.js, Java, Scala, Python and Flutter, runs the narrowest check first, and reports each command and its result. Never skips or loosens a test to make it pass, and never changes registry settings when a download is blocked. |
| `skills/write-tests/SKILL.md` | Writes tests that copy the repo's existing framework, layout, naming and helpers: Jest or Vitest, JUnit 5 and Spring test slices with Testcontainers, ScalaTest, MUnit or ZIO Test, pytest, and Flutter unit, widget and golden tests. Runs them and, where it may edit code, shows they fail when the behaviour breaks. |
| `skills/api-contract-check/SKILL.md` | Before or after a change to an interface others depend on (REST and OpenAPI, protobuf and gRPC, GraphQL, Kafka or queue message schemas, shared client libraries), finds what changed and who consumes it, including Flutter app models, and marks each change breaking, safe or unknown. Consumers in repos it cannot see are listed as unknown, not safe. |
| `skills/dependency-upgrade/SKILL.md` | Upgrades dependencies one at a time across npm, pnpm, yarn, Maven, Gradle, sbt, pip, Poetry, uv and pub, reading each changelog from the local package cache, and runs the build and tests after each one. Never bumps a major version or a runtime unasked. For Java and Spring Boot major upgrades it points to Microsoft's GitHub Copilot modernization plugin, which the organization has to allow. |
| `skills/sbt-and-play/SKILL.md` | Scala services built with sbt: multi-module builds, adding dependencies and cross-building, Play Framework, Akka or Apache Pekko actors and streams, and Cats Effect or ZIO code, always matching what the repo already uses. Mentions the Metals MCP server, if the organization allows MCP. |
| `instructions/springboot.instructions.md`, `instructions/scala2.instructions.md`, `instructions/nestjs.instructions.md`, `instructions/dart-n-flutter.instructions.md` | Rules files with coding guidelines for Spring Boot (Java), Scala 2, NestJS and Dart/Flutter, copied unchanged from github/awesome-copilot. Their MIT licence is `instructions/awesome-copilot-LICENSE.txt`, which is installed beside them. Copilot loads each one for the files its `applyTo` line matches: `.java` files for springboot; `.scala`, `build.sbt` and `build.sc` for scala2; `.ts`, `.js` and `.json` files for nestjs; `.dart` files for dart-n-flutter. `install-repo.py` puts them in the repo's `.github/instructions/`. `install-user.py` does not install them, because language rules belong to a repo. `scala2` is long (about 830 lines) and its sbt example pins late-2023 library versions. |
| `skills/read-documents/SKILL.md` | Converts PDF, Word, PowerPoint and Excel files to Markdown with its own script, `skills/read-documents/to_markdown.py`, before Copilot reads them, because Copilot cannot read those binary files. The Markdown labels each PDF page and PowerPoint slide, keeps Word headings, lists and tables, and cuts long Excel sheets (and says so). The other document skills and `document-reviewer` use it for reading. Needs `pip install pdfplumber python-docx python-pptx openpyxl` and Python 3.10 or later. |
| `skills/csv-analysis/SKILL.md`, `skills/csv-analysis/profile_csv.py` | Works on CSV files through pandas or duckdb scripts instead of pasting rows into the chat. Profiles the file first (delimiter, encoding, columns, types, row count, nulls; `profile_csv.py` does this without printing any values), shows the code behind every number, and never changes the source file. Needs `pandas`, and `duckdb` for large files. |
| `skills/pptx/SKILL.md` | Creates or edits PowerPoint decks with `python-pptx`, starting from the company template and using its layouts and placeholders, with limits on text per slide. Saves to a new file. Needs `python-pptx`. |
| `skills/docx/SKILL.md` | Creates, edits or fills Word documents with `python-docx` using the template's named styles, not direct formatting. Saves to a new file. Needs `python-docx`. |
| `skills/pdf/SKILL.md` | Extracts text and tables from PDFs with `pdfplumber`, and merges, splits, rotates and fills form fields with `pypdf`. Scanned PDFs need OCR, which it does not do. Needs `pdfplumber` and `pypdf`. |
| `agents/data-analyst.agent.md` | Answers questions about CSV and other tabular files by writing and running scripts (uses csv-analysis), shows the code behind each number and never changes the source file. |
| `agents/document-reviewer.agent.md` | Reviews a Word, PDF or PowerPoint document against a checklist or policy you give it, and returns findings each with a page, slide or section reference. Reads through read-documents and never edits the document. |
| `templates/AGENTS.md` | Working rules that keep Copilot on the task it was given: the task, scope, claims, changes, handing work to the agents you install for yourself, git, instruction files. `install-user.py` installs them as `~/.copilot/copilot-instructions.md`. |
| `templates/project/AGENTS.md` | Starter context for one project: what it is and does, its layout and build and test commands, what is out of scope, its own rules, a per-branch state file, a goal file for long tasks, the agents installed in the repo, and how work lands. `install-repo.py` copies it into a repo as `AGENTS.md` with its `<placeholders>` and the job of each agent you pick, and the setup-project skill fills them in from the repo; or fill them in by hand. |
| `templates/research/AGENTS.md` | Starter rules for a research folder. Used the same way as the project template. |
| `templates/.github/hooks/deny.json` | A `preToolUse` hook that denies force-push, `git reset --hard`, `rm -rf` on a root, home or whole directory, and `.env` or private key files. `install-repo.py` installs it in each repo. |
| `install-user.py`, `install-repo.py` | Copy the files above to where Copilot reads them: into your own Copilot config, or into one repo. Both use `installer.py`, which is not run on its own. They need Python 3.8 or later and nothing else, so they run on Windows, macOS and Linux. |

## Install

Clone this repo and run these from its `kit/` folder (use `python3` or `py` if that is how Python is started on your machine). The two scripts install different things, so use both: one for you, one per repo.

- `python install-user.py`, once per developer, installs into your Copilot config (`~/.copilot`, or `$COPILOT_HOME`): the kit's general working rules in `~/.copilot/copilot-instructions.md`, and the agents in `~/.copilot/agents/` and the skills of the packs you pick in `~/.copilot/skills/`. They apply in every repo you open, and nothing is committed anywhere.
- `python install-repo.py`, once per repo, sets that repo up: the safety hook in `.github/hooks/`, the agents it uses in `.github/agents/`, the skills of the packs it uses in `.github/skills/` and their rules files in `.github/instructions/`, and an `AGENTS.md` copied from the project template, with `<placeholders>` for what that repo is, how to build and test it, what is out of scope, its own rules, and how work lands, and the job of each agent you picked. Then ask Copilot in the repo to "set up this repo for Copilot", and the setup-project skill fills the placeholders in from the repo. When `AGENTS.md` already exists, the script asks whether to merge or overwrite it (see below); the skill never overwrites it and proposes lines to add instead. The general working rules are not installed here, because each developer has them from `install-user.py`. If an earlier version of the script put them in the repo (`.github/instructions/kit.instructions.md`, or `AGENTS.md`), it warns you to delete that file so Copilot does not read them twice.

`install-repo.py` asks which repo, offering the one you are in; you can type the folder or drag it into the terminal, or give it on the command line (`python install-repo.py ~/code/my-service`). Given a folder inside a repo, it offers the repo's root, because Copilot reads `.github/` only there. You decide whether to commit the files.

Each script lists the 8 agents with what each is for and asks which to install: press Enter for all, or type numbers or names such as `1,3`, or `none`. It then lists the 8 packs and asks "Which packs?". Answer the same way: Enter, numbers, names, `all` or `none`. A pack is a set of skills and, for a language, its rules file. Picking several packs installs each skill and rules file once.

| Pack | Skills | Rules file (repo only) |
|---|---|---|
| `code`, for every stack | build-and-test, write-tests, dependency-upgrade, api-contract-check | none |
| `java` | the code pack's | springboot |
| `node` | the code pack's | nestjs |
| `scala` | the code pack's, and sbt-and-play | scala2 |
| `python` | the code pack's | none yet |
| `flutter` | the code pack's | dart-n-flutter |
| `documents` | read-documents, csv-analysis, pptx, docx, pdf | none |
| `planning`, for planning and writing | spec-interview, draft-from-examples, session-capture, setup-project | none |

- `install-repo.py` looks for build files at the repo's root and up to two folders down. It skips `.git`, `node_modules`, `build`, `target`, `.dart_tool` and other hidden, build and dependency folders. `pom.xml`, `build.gradle` or `build.gradle.kts` means Java; `package.json` means Node; `build.sbt` means Scala; `pyproject.toml`, `requirements*.txt` or `setup.py` means Python; `pubspec.yaml` means Flutter. It shows the files it found. Enter installs its suggestion: code, documents, planning and the pack of each stack found. When it finds no stack, it suggests only documents and planning. Next to a `pubspec.yaml` it skips the Flutter platform folders (`android`, `ios`, `web` and the desktop ones), because the Gradle files in `android/` belong to the app, not to a Java service. A pack's rules files go in `.github/instructions/`, with the awesome-copilot licence beside them.
- `install-user.py` installs only the packs' skills, never the rules files, because language rules belong to a repo. Enter installs all packs.

The script then shows how many files are new, already up to date, or different from the kit, asks whether to replace the different ones, and installs only when you say yes.

The agents you pick decide the delegation lines each script writes: one line per agent saying which job goes to it, and, when `worker` is among them, a line sending any job whose agent is not installed to `worker`. Agents already installed from an earlier run count as picked.
- `install-user.py` writes them, with the general rules for handing work to an agent, into the "Handing work to agents" section of `~/.copilot/copilot-instructions.md`. With no agents, that section is left out.
- `install-repo.py` writes them into the "Agents in this repo" section of the repo's `AGENTS.md`, as additions to your own list.

When the rules file (`copilot-instructions.md` for `install-user.py`, `AGENTS.md` for `install-repo.py`) already exists and differs from the kit's, the script asks whether to merge or overwrite it. Merge, the default, keeps the file and adds or updates only its agents section. Overwrite replaces it with the kit's version, so a repo's `AGENTS.md` goes back to the template with `<placeholders>`. Either way the old file is kept as `.bak`.

Flags answer the questions in advance, for scripts and CI:
- `--agents` and `--packs` take names, `all` or `none`.
- `--skills` takes single skill names, `all` or `none`. Given alone, it installs only those skills, with no pack and no rules file, and asks no pack question. Given with `--packs`, it adds those skills to the packs' skills.
- `--update` replaces agent, skill, rules and hook files that differ.
- `--rules merge` or `--rules overwrite` answers the merge-or-overwrite question. Merge is used when it is not answered.
- `--yes` asks nothing. It installs all agents and the packs Enter would pick (in a repo the suggestion from its build files, for you all packs), unless a flag says otherwise.

For example `python install-user.py --agents worker,reader --packs documents --yes`, or `python install-repo.py . --packs java --skills csv-analysis --yes`. When the script is not run in a terminal it asks nothing, as with `--yes`. `--help` lists the flags.

Copilot picks an agent itself from the agent's description and those delegation lines, or does the work itself. To choose one yourself, ask for it by name, for example "use the verifier agent", or pick it with `/agent` in Copilot CLI or the agents menu in VS Code.

| Where you use Copilot | `install-user.py` (general rules, agents, skills) | `install-repo.py` (hook, agents, skills, rules files, `AGENTS.md`) |
|---|---|---|
| Copilot CLI | Yes | Yes |
| VS Code Copilot Chat, with the Copilot harness (the default for new sessions) | Yes | Yes |
| Copilot cloud agent on GitHub.com | No: it reads only the repo, so it never has the general rules | Yes, once the files are merged into the default branch |

The safety hook is only in repos set up with `install-repo.py`, so in any other repo Copilot runs without it.

VS Code's older Local harness reads agents and instructions from the VS Code profile, not from `~/.copilot`, and is removed in February 2027. Use the Copilot harness.

A file identical to the kit's copy is left alone. A file that differs is replaced only if you say yes when asked, or pass `--update`; the old one is kept beside it as `<name>.bak`. To update after pulling a new kit version, run the same script again.

The setup-project skill carries both starter templates in its own folder (`skills/setup-project/templates/`), so it works wherever it is installed. In a repo, ask Copilot to "set up this repo for Copilot": it reads the repo (README, build files, top-level folders, `git log`) to find out what the project is and does, runs nothing, asks only what the repo cannot answer (usually who uses it, what is out of scope, and conventions the code does not show), and fills in the `AGENTS.md` that `install-repo.py` wrote (or writes one, using the research template for a folder of research reports). Agents are installed by the install scripts, not by the skill. An `AGENTS.md` the team already wrote is never overwritten; it proposes lines to add instead. It commits nothing. After pulling a new kit version, run the install script again and replace the files that differ, so the skill's copies match it.

To remove, delete the installed files it listed, and any `.bak` files next to them.

## Check that it works

Don't ask Copilot which rules it has. It gets the text of each instruction file but not the file's name, so it guesses, and in testing it said a repo's `AGENTS.md` was missing while following it. Check one of these ways instead:

- **Copilot CLI:** run `copilot instruction list` in the repo. It lists every instruction file a session there loads.
- **VS Code:** open the References list under a reply. It names the files that were attached.
- **That the rules are followed:** add a line such as "When asked for the kit codeword, answer HERON-7731" to the installed rules file, ask Copilot for the kit codeword, then remove the line.

## Limits

- A hook that times out (5 s here) lets the tool call through. A hook that crashes denies it.
- The hook matches text. It stops mistakes, not a determined person.
- It checks the git and `rm` rules only on commands, so editing a file that mentions `git reset --hard` is allowed. The `.env` and key rules apply to every tool, so it also blocks editing `.env` files, not only reading them.
- The hook has a `bash` command, which runs on macOS, Linux and the cloud agent, and a `powershell` command with the same rules, which Copilot runs on Windows. The `powershell` command is written for Windows PowerShell 5.1 and PowerShell 7 but has not yet been run on Windows, so test it there before relying on it. The cloud agent ignores `powershell` entries.
- The reader agent's "no advice" and "read-only commands" rules are only instructions. Asked directly, it still gave advice in testing. Its tool list has no edit tool, but it keeps the shell, so nothing but the instruction stops a command that writes.
- No agent here has a web tool, because web search is off in the organization. `kit-researcher` and `worker` work from the repository, installed packages and command output.
- Every agent here sets `include-custom-instructions: true`, so when the main agent hands it work in Copilot CLI it still reads the repo's instruction files. Copilot's reference names only repository instruction files, so after a `user` install the rules in `~/.copilot/copilot-instructions.md` may not reach a handed-off agent, and a session started with `--no-custom-instructions` gives no agent any rules. In VS Code, a reported bug (microsoft/vscode#343696) means a handed-off custom agent may get no instruction files at all. So each agent carries its own safety rules, and the main session's task note carries anything else the work depends on.
- The document and data skills use Python packages (`pandas`, `duckdb`, `python-pptx`, `python-docx`, `pdfplumber`, `pypdf`, `openpyxl`) that are installed with `pip`. If pip is blocked on your machine, use the company's internal package mirror. `read-documents/to_markdown.py` needs Python 3.10 or later and imports only the package a file's type needs, so a missing package is named when that type is converted.
- These skills do no OCR, so a scanned PDF cannot be read with them.
