# Installing the kit

Two scripts in the repo's root folder copy the kit's files to where Copilot reads them. They need Python 3.8 or later and nothing else, so they run on Windows, macOS and Linux. Both use `installer.py`, which is not run on its own. Run them from the repo's root folder. Use `python3` or `py` in place of `python` if that is how Python starts on your machine.

The two scripts install different things, so use both: one for you, one per repo.

| Script | When | Installs | Where |
|---|---|---|---|
| `python install-user.py` | Once per developer | The working rules, the agents you pick, the skills of the packs you pick | `~/.copilot` (or `$COPILOT_HOME`): `copilot-instructions.md`, `agents/`, `skills/`. Applies in every repo you open; nothing is committed anywhere. |
| `python install-repo.py <path>` | Once per repo | The safety hook, the agents you pick, the skills and language rules files of the packs you pick, and an `AGENTS.md` | That repo: `.github/hooks/`, `.github/agents/`, `.github/skills/`, `.github/instructions/`, and `AGENTS.md` at its root. You decide whether to commit them. |

`install-user.py` never installs the language rules files, because language rules belong to a repo. `install-repo.py` never installs the working rules, because each developer has them from `install-user.py`. If an earlier version of `install-repo.py` put the working rules in the repo (`.github/instructions/kit.instructions.md`, or `AGENTS.md`), it warns you to delete that file so Copilot does not read them twice.

## What the scripts ask

The scripts ask these questions in order. Press Enter at each one to take the suggestion.

1. **Which repo** (`install-repo.py` only). It offers the repo you are in. Type the folder, drag it into the terminal, or give it on the command line. Given a folder inside a repo, it offers the repo's root, because Copilot reads `.github/` only there.
2. **Which agents.** It lists the 8 agents with what each is for. Press Enter for all, or type numbers or names such as `1,3`, or `none`.
3. **Which packs.** It lists the 8 packs. Answer the same way: Enter, numbers, names, `all` or `none`.
4. **Replace changed files?** It shows how many files are new, already up to date, or different from the kit, and asks whether to replace the different ones. It installs only when you say yes.
5. **Merge or overwrite the rules file?** Asked only when the rules file already exists and differs from the kit's (see [When a file already exists](#when-a-file-already-exists)).

## Packs

A pack is a set of skills and, for a language, its rules file. Picking several packs installs each skill and rules file once. An agent that works through a skill gets that skill even when no pack you picked holds it, and the script says so: `data-analyst` brings `csv-analysis`, and `document-reviewer` brings `read-documents`.

| Pack | Skills | Rules file (repo only) |
|---|---|---|
| `code`, for every stack | build-and-test, write-tests, dependency-upgrade, api-contract-check | none |
| `java` | the code pack's | springboot |
| `node` | the code pack's | nestjs |
| `scala` | the code pack's, and sbt-and-play | scala |
| `python` | the code pack's | none yet |
| `flutter` | the code pack's | flutter |
| `documents` | read-documents, csv-analysis, pptx, docx, pdf | none |
| `planning`, for planning and writing | spec-interview, draft-from-examples, session-capture, setup-project | none |

What Enter picks:

- **`install-user.py`:** all packs.
- **`install-repo.py`:** code, documents, planning, and the pack of each stack it finds in the repo. When it finds no stack, only documents and planning.

How `install-repo.py` finds the stack: it looks for build files at the repo's root and up to two folders down, and shows the files it found.

| File | Stack |
|---|---|
| `pom.xml`, `build.gradle`, `build.gradle.kts` | Java |
| `package.json` | Node |
| `build.sbt` | Scala |
| `pyproject.toml`, `requirements*.txt`, `setup.py` | Python |
| `pubspec.yaml` | Flutter |

It skips `.git`, `node_modules`, `build`, `target`, `.dart_tool` and other hidden, build and dependency folders. Next to a `pubspec.yaml` it also skips the Flutter platform folders (`android`, `ios`, `web` and the desktop ones), because the Gradle files in `android/` belong to the app, not to a Java service.

## Which agent does which job

The agents you pick decide the lines each script writes about handing work to them: one line per agent saying which job goes to it, and, when `worker` is among them, a line sending any job whose agent is not installed to `worker`. Agents already installed from an earlier run count as picked.

- **`install-user.py`** writes them, with the general rules for handing work to an agent, into the "Handing work to agents" section of `~/.copilot/copilot-instructions.md`. With no agents, that section is left out.
- **`install-repo.py`** writes them into the "Agents in this repo" section of the repo's `AGENTS.md`, as additions to your own list.

## The repo's AGENTS.md

`install-repo.py` copies the project template into the repo as `AGENTS.md`. It has `<placeholders>` for what the repo is, how to build and test it, what is out of scope, its own rules and how work lands, plus the job of each agent you picked.

Then ask Copilot in the repo to "set up this repo for Copilot". The setup-project skill fills in the placeholders from the repo. You can also fill them in by hand. See [setup-project](kit/README.md#setup-project) for what the skill reads and asks.

## When a file already exists

- **Agent, skill, rules and hook files.** A file identical to the kit's copy is left alone. A file that differs is replaced only if you say yes when asked, or pass `--update`.
- **The rules file** (`copilot-instructions.md` for `install-user.py`, `AGENTS.md` for `install-repo.py`). When it differs from the kit's, the script asks whether to merge or overwrite. **Merge**, the default, keeps the file and adds or updates only its agents section. **Overwrite** replaces it with the kit's version, so a repo's `AGENTS.md` goes back to the template with `<placeholders>`.

Every replaced file is kept beside the new one as `<name>.bak`.

## Flags

Flags answer the questions in advance, for scripts and CI. `--help` lists them.

| Flag | What it does |
|---|---|
| `--agents <names>` | Agents to install: names, `all` or `none`. |
| `--packs <names>` | Packs to install: names, `all` or `none`. |
| `--skills <names>` | Single skills: names, `all` or `none`. Given alone, it installs only those skills, with no pack and no rules file, and asks no pack question. Given with `--packs`, it adds those skills to the packs' skills. |
| `--update` | Replaces agent, skill, rules and hook files that differ from the kit's. |
| `--rules merge` or `--rules overwrite` | Answers the merge-or-overwrite question. Merge is used when it is not answered. |
| `--yes` | Asks nothing. Installs all agents and the packs Enter would pick, unless another flag says otherwise. |

When the script is not run in a terminal it asks nothing, as with `--yes`.

Examples:

```
python install-user.py --agents worker,reader --packs documents --yes
python install-repo.py . --packs java --skills csv-analysis --yes
```
