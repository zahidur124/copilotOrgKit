---
name: setup-project
description: Set up the current repository or folder for Copilot work with the kit - find out what the project is and does, and write that context into its AGENTS.md from the kit's starter template. Use when the user asks to set up, onboard or bootstrap a repo or project for Copilot, or asks for an AGENTS.md in this repo.
---

# setup-project

The starter templates are in this skill's own folder: `templates/project-AGENTS.md` and `templates/research-AGENTS.md`. The folder is `.github/skills/setup-project/` in the repository, or `~/.copilot/skills/setup-project/` (`$COPILOT_HOME/skills/setup-project/` when `COPILOT_HOME` is set). If neither has them, stop and tell the user to install the kit again with `install-user.py` or `install-repo.py`, because writing the file from memory gives a different file from the kit's.

1. **Find the root and what is already there.** Run `git rev-parse --show-toplevel` and work at that root; outside a git repository, work in the current folder. Check for an existing `AGENTS.md`, `.github/copilot-instructions.md` and `.github/instructions/`, and read any that exist. List the agents in `.github/agents/`: these are the agents the user picked for this repository. An `AGENTS.md` whose lines are still `<placeholders>` is the unfilled project template, not the team's own file.

2. **Pick the template.** A folder of code uses `templates/project-AGENTS.md`. A folder that holds research reports and no code uses `templates/research-AGENTS.md`. If it is unclear which, ask.

3. **Find out what the project is and does.** Read the README, the package or build files (for example `package.json`, `pom.xml`, `build.gradle`, `build.sbt`, `pyproject.toml`, `pubspec.yaml`), the top-level folders, `CONTRIBUTING.md` and `git log --oneline -20`. From these, work out each `<placeholder>`: what the project does, its stack and layout, its build and test commands, and how work lands (merge commits and pull request numbers in `git log` mean pull requests). Run nothing.

4. **Ask only what the repository cannot settle.** In one message, show what step 3 found with the file each fact came from, and ask what is left: usually who uses the project, what a session should leave alone, and any convention or trap the code does not show. Wait for the answers.

5. **Write `AGENTS.md`.**
   - Fill each placeholder with the found or given fact, in plain words. Delete a placeholder line that has no answer, and a section left with nothing in it, because a session acts on whatever the file says, a literal `<placeholder>` included.
   - Under Delegation, keep the job line of each agent in `.github/agents/` and delete the others. The line "If the agent for a job is not installed, use `worker`" stays only when `worker` is there. With no agents there, delete the whole Delegation section.
   - If `AGENTS.md` is the project template still holding its `<placeholders>`, as `install-repo.py` writes it, fill it in place. If step 2 picked the research template instead, replace it with the filled-in research template.
   - If `AGENTS.md` already exists and is not the unfilled template, do not overwrite it. Show the lines the template would add or change, each next to the section it goes in, and write only the lines the user picks, because the file is the team's and every session there follows it.

6. **Report and stop.** List the lines written and each placeholder deleted for want of an answer. Do not commit: the user decides whether the team gets the file.
