# Copilot kit

Optional agents, skills, working rules and a safety hook for GitHub Copilot. Each developer chooses whether to install them; nothing is pushed to any repo.

| Path | What it is |
|---|---|
| `agents/*.agent.md` | 8 custom agents: worker, kit-researcher, reader, verifier, kit-reviewer, builder, data-analyst, document-reviewer. The two `kit-` names keep them apart from Copilot CLI's built-in `research` and `code-review` agents. |
| `skills/*/SKILL.md` | 9 skills: draft-from-examples, spec-interview, session-capture, setup-project, read-documents, csv-analysis, pptx, docx, pdf. A skill's other files (such as `csv-analysis/profile_csv.py` and `read-documents/to_markdown.py`) are installed beside its `SKILL.md`. |
| `skills/read-documents/SKILL.md` | Converts PDF, Word, PowerPoint and Excel files to Markdown with its own script, `skills/read-documents/to_markdown.py`, before Copilot reads them, because Copilot cannot read those binary files. The Markdown labels each PDF page and PowerPoint slide, keeps Word headings, lists and tables, and cuts long Excel sheets (and says so). The other document skills and `document-reviewer` use it for reading. Needs `pip install pdfplumber python-docx python-pptx openpyxl` and Python 3.10 or later. |
| `skills/csv-analysis/SKILL.md`, `skills/csv-analysis/profile_csv.py` | Works on CSV files through pandas or duckdb scripts instead of pasting rows into the chat. Profiles the file first (delimiter, encoding, columns, types, row count, nulls; `profile_csv.py` does this without printing any values), shows the code behind every number, and never changes the source file. Needs `pandas`, and `duckdb` for large files. |
| `skills/pptx/SKILL.md` | Creates or edits PowerPoint decks with `python-pptx`, starting from the company template and using its layouts and placeholders, with limits on text per slide. Saves to a new file. Needs `python-pptx`. |
| `skills/docx/SKILL.md` | Creates, edits or fills Word documents with `python-docx` using the template's named styles, not direct formatting. Saves to a new file. Needs `python-docx`. |
| `skills/pdf/SKILL.md` | Extracts text and tables from PDFs with `pdfplumber`, and merges, splits, rotates and fills form fields with `pypdf`. Scanned PDFs need OCR, which it does not do. Needs `pdfplumber` and `pypdf`. |
| `agents/data-analyst.agent.md` | Answers questions about CSV and other tabular files by writing and running scripts (uses csv-analysis), shows the code behind each number and never changes the source file. |
| `agents/document-reviewer.agent.md` | Reviews a Word, PDF or PowerPoint document against a checklist or policy you give it, and returns findings each with a page, slide or section reference. Reads through read-documents and never edits the document. |
| `templates/AGENTS.md` | Working rules: the task, claims, changes, handing work to agents, git, instruction files. Installed as `~/.copilot/copilot-instructions.md` (user) or `.github/instructions/kit.instructions.md` (repo). |
| `templates/project/AGENTS.md` | Starter rules for one project. The setup-project skill writes it into a repo as `AGENTS.md`, filled in from the repo; or copy it by hand and fill in the `<placeholders>`. |
| `templates/research/AGENTS.md` | Starter rules for a research folder. Used the same way as the project template. |
| `templates/.github/hooks/deny.json` | A `preToolUse` hook that denies force-push, `git reset --hard`, `rm -rf` on a root, home or whole directory, and `.env` or private key files. |
| `install-user.py`, `install-repo.py` | Copy the files above to where Copilot reads them: into your own Copilot config, or into one repo. Both use `installer.py`, which is not run on its own. They need Python 3.8 or later and nothing else, so they run on Windows, macOS and Linux. |

## Install

Clone this repo, then run one of these from its `kit/` folder (use `python3` or `py` if that is how Python is started on your machine). Pick one: with both, Copilot reads the kit's rules twice in that repo.

- `python install-user.py` installs into your Copilot config (`~/.copilot`, or `$COPILOT_HOME`). It applies in every repo you open, and nothing is committed anywhere. The rules go in `~/.copilot/copilot-instructions.md`, the hook in `~/.copilot/hooks/deny.json`, the agents in `~/.copilot/agents/` and the skills in `~/.copilot/skills/`.
- `python install-repo.py` installs into one repo: the rules in `.github/instructions/kit.instructions.md`, and `.github/hooks/`, `.github/agents/` and `.github/skills/`. It asks which repo, offering the one you are in; you can type the folder or drag it into the terminal, or give it on the command line (`python install-repo.py ~/code/my-service`). Given a folder inside a repo, it offers the repo's root, because Copilot reads `.github/` only there. You decide whether to commit the files. The repo's own `AGENTS.md` is never touched, so the project template can live there; Copilot reads both. If an earlier install put the kit's rules in `AGENTS.md`, the script warns you to delete it, so Copilot does not read the rules twice.

Each script lists the 8 agents and 9 skills with what each is for and asks which to install: press Enter for all, or type numbers or names such as `1,3`, or `none`. It then shows how many files are new, already up to date, or different from the kit, asks whether to replace the different ones, and installs only when you say yes. The working rules send work to an agent by the kind of job and fall back to `worker` when that agent is not installed, so the script tells you if you leave `worker` out.

Flags answer the questions in advance, for scripts and CI: `--agents` and `--skills` take names, `all` or `none`; `--update` replaces files that differ; `--yes` asks nothing and installs everything not limited by a flag. For example `python install-user.py --agents worker,reader --skills none --yes`. When the script is not run in a terminal it asks nothing, as with `--yes`. `--help` lists the flags.

Copilot picks an agent itself from the agent's description and the working rules, or does the work itself. To choose one yourself, ask for it by name, for example "use the verifier agent", or pick it with `/agent` in Copilot CLI or the agents menu in VS Code.

| Where you use Copilot | `user` install | `repo` install |
|---|---|---|
| Copilot CLI | Yes | Yes |
| VS Code Copilot Chat, with the Copilot harness (the default for new sessions) | Yes | Yes |
| Copilot cloud agent on GitHub.com | No: it reads only the repo | Yes, once the files are merged into the default branch |

VS Code's older Local harness reads agents and instructions from the VS Code profile, not from `~/.copilot`, and is removed in February 2027. Use the Copilot harness.

A file identical to the kit's copy is left alone. A file that differs is replaced only if you say yes when asked, or pass `--update`; the old one is kept beside it as `<name>.bak`. To update after pulling a new kit version, run the same script again.

The two starter templates are not installed on their own. The setup-project skill carries them, with a copy of all 8 agents, in its own folder (`skills/setup-project/templates/` and `skills/setup-project/agents/`), so it works wherever it is installed. Those copies are not loaded as agents. In a repo, ask Copilot to "set up this repo for Copilot": it reads the repo (README, build files, CI, `git log`), runs the check command once, asks only what the repo cannot answer, writes `AGENTS.md` and copies the agents that repo needs into `.github/agents/`. It never overwrites an existing `AGENTS.md`; it proposes lines to add instead. It commits nothing. After pulling a new kit version, run the install script again and replace the files that differ, so the skill's copies match it.

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
