# Installing the kit

The kit comes with two install scripts. They copy files to the places Copilot looks for them. Run both: one sets up Copilot for you, the other sets up one repo.

| Script | Run it | What it sets up | Where the files go |
|---|---|---|---|
| `install-user.py` | Once, on your computer | Your personal rules, agents and skills | Your Copilot folder, `~/.copilot`. Works in every repo you open. Nothing is committed. |
| `install-repo.py` | Once for each repo | The repo's notes (`AGENTS.md`), language guides, agents, skills and the safety hook | Inside that repo, in `AGENTS.md` and `.github/`. You decide whether to commit them. |

```
On your computer (~/.copilot)           In one repo
-----------------------------           -----------
your personal rules                     the repo's notes (AGENTS.md)
agents                                  agents
skills                                  skills
                                        language guides
                                        safety hook

set up by install-user.py, once         set up by install-repo.py, once per repo
```

Language guides go only into repos, because they belong to a repo's code. Your personal rules go only into your Copilot folder, because they are yours.

## What you will see

Each script lists what it can install and asks you to choose. **If you are unsure, press Enter at every question.** Enter takes the suggested answer.

A shortened example of `install-repo.py`:

```
$ python install-repo.py ~/code/my-service
Copilot kit: install into one repository.

Agents in the kit:
   1. builder              Use when a change is fully specified ...
   2. data-analyst         Use when a question about a CSV ...
   ...
Which agents? Enter for all, numbers or names such as 1,3 for some, or none:     <- press Enter

Packs in the kit:
   1. code         ...
   ...
Which packs? Enter for code, java, documents, planning; or numbers or names such as 1,3; or all; or none:     <- press Enter

Into /Users/you/code/my-service:
  31 new file(s) to install
  0 file(s) already up to date
Install now? [Y/n]     <- press Enter

Done.
```

Ways to answer the "Which ...?" questions:

- **Enter** takes the suggestion.
- **Numbers or names**, such as `1,3` or `worker,reader`, pick only those.
- **`all`** or **`none`**.

What Enter picks:

- **Agents:** all of them.
- **Packs, in `install-user.py`:** all of them.
- **Packs, in `install-repo.py`:** code, documents, planning, and the language pack for each language it finds in the repo. It shows the files it used to decide.

## Packs

A pack is a bundle of skills for one kind of work. A language pack also adds that language's guide to the repo.

| Pack | Skills | Language guide (repo only) |
|---|---|---|
| `code`, for any language | build-and-test, write-tests, dependency-upgrade, api-contract-check | none |
| `java` | the code pack's | Spring Boot |
| `node` | the code pack's | NestJS |
| `scala` | the code pack's, and sbt-and-play | Scala |
| `python` | the code pack's | none yet |
| `flutter` | the code pack's | Flutter |
| `documents` | read-documents, csv-analysis, pptx, docx, pdf | none |
| `planning`, for planning and writing | spec-interview, draft-from-examples, session-capture, setup-project | none |

[kit/skills/README.md](kit/skills/README.md) says what each skill does.

## If you have installed before

The script compares each file with the kit's copy:

- **Same as the kit:** left alone.
- **Different** (you edited it, or it is from an older kit): the script asks before replacing it.

Your personal rules (`copilot-instructions.md`) and the repo's notes (`AGENTS.md`) are files you are meant to edit. If yours differs from the kit's, the script asks you to choose:

- **Merge** (the default): keeps your file and updates only the section that lists the installed agents.
- **Overwrite:** replaces your file with the kit's. For a repo, that means a blank template again.

Whenever a file is replaced, the old one is kept next to it with `.bak` added to its name.

## Update or remove

- **Update:** download the new version of this repo and run the same scripts again.
- **Remove:** delete the files the script listed when it installed them, and any `.bak` files next to them.

## Running without questions

Add flags to answer the questions in advance, for example in a script or a CI job. Run a script with `--help` to list them.

| Flag | What it does |
|---|---|
| `--agents <names>` | Which agents to install: names, `all` or `none`. |
| `--packs <names>` | Which packs to install: names, `all` or `none`. |
| `--skills <names>` | Single skills, by name. On its own, installs only those skills, with no pack and no language guide. With `--packs`, adds them to the packs' skills. |
| `--update` | Replaces files that differ from the kit's without asking. |
| `--rules merge` or `--rules overwrite` | Answers the merge-or-overwrite question. Merge is used if you leave it out. |
| `--yes` | Asks nothing and takes every suggestion, except where another flag says otherwise. |

A script run outside a terminal (for example by another program) also asks nothing, as with `--yes`.

Examples:

```
python install-user.py --agents worker,reader --packs documents --yes
python install-repo.py . --packs java --skills csv-analysis --yes
```
