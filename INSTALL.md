# Installing the kit

Two scripts in the repo's root folder copy the kit's files to where Copilot reads them. Use both: one for you, one per repo.

| Script | When | Installs | Where |
|---|---|---|---|
| `python install-user.py` | Once per developer | The working rules, the agents you pick, the skills of the packs you pick | `~/.copilot` (or `$COPILOT_HOME`): `copilot-instructions.md`, `agents/`, `skills/`. Applies in every repo you open; nothing is committed anywhere. |
| `python install-repo.py <path>` | Once per repo | The safety hook, the agents you pick, the skills and language rules files of the packs you pick, and an `AGENTS.md` | That repo: `.github/hooks/`, `.github/agents/`, `.github/skills/`, `.github/instructions/`, and `AGENTS.md` at its root. You decide whether to commit them. |

`install-user.py` never installs the language rules files, because language rules belong to a repo. `install-repo.py` never installs the working rules, because each developer has them from `install-user.py`.

## Answering the questions

Each script asks which agents and which packs to install. Answer with Enter for the suggestion, numbers or names such as `1,3`, `all`, or `none`. Enter picks all agents, and:

- **`install-user.py`:** all packs.
- **`install-repo.py`:** code, documents, planning, and the pack of each stack it finds from the repo's build files. It shows the files it found.

## Packs

A pack is a set of skills and, for a language, its rules file.

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

## When a file already exists

- **Agent, skill, rules and hook files.** A file identical to the kit's copy is left alone. A file that differs is replaced only if you say yes when asked, or pass `--update`.
- **The rules file** (`copilot-instructions.md` for `install-user.py`, `AGENTS.md` for `install-repo.py`). When it differs from the kit's, the script asks whether to merge or overwrite. **Merge**, the default, keeps the file and updates only the section listing which job goes to each installed agent ("Handing work to agents" or "Agents in this repo"). **Overwrite** replaces it with the kit's version, so a repo's `AGENTS.md` goes back to the template with `<placeholders>`.

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
