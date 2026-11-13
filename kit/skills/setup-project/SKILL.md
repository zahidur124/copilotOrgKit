---
name: setup-project
description: Set up the current repository or folder for Copilot work with the kit - write its AGENTS.md from the kit's starter template, filled in from what the repo shows, and copy the kit agents it needs into .github/agents/. Use when the user asks to set up, onboard or bootstrap a repo or project for Copilot, or asks for an AGENTS.md or the kit agents in this repo.
---

# setup-project

The kit files this skill copies are in this skill's own folder: `templates/project-AGENTS.md`, `templates/research-AGENTS.md` and `agents/*.agent.md`. The folder is `.github/skills/setup-project/` in the repository, or `~/.copilot/skills/setup-project/` (`$COPILOT_HOME/skills/setup-project/` when `COPILOT_HOME` is set). If neither has them, stop and tell the user to install the kit again with `install-user.py` or `install-repo.py`, because writing the files from memory gives a different file from the kit's.

1. **Find the root and what is already there.** Run `git rev-parse --show-toplevel` and work at that root; outside a git repository, work in the current folder. Check for an existing `AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/` and `.github/agents/`, and read any that exist.

2. **Pick the template.** A folder of code uses `templates/project-AGENTS.md`. A folder that holds research reports and no code uses `templates/research-AGENTS.md`. If it is unclear which, ask.

3. **Read the repository before asking anything.** Read the README, the package or build files (for example `package.json`, `pyproject.toml`, `pom.xml`, `*.csproj`, `go.mod`, `Makefile`), the CI workflows under `.github/workflows/`, `CONTRIBUTING.md`, the test folder, and `git log --oneline -20`. From these, work out each `<placeholder>` in the template: what the project is, the check and test commands, the end-to-end command, where `docs/spec.md` and `docs/design.md` are, and how work lands (merge commits and pull request numbers in `git log` mean pull requests). Take a command from a file that runs it, such as CI, a script entry or the README, and run the quick check once to see that it works, because a wrong command in AGENTS.md is followed by every session.

4. **Pick the agents.** Propose the agents this repository needs, with one reason each:
   - `worker`: always, because the working rules fall back to it when the agent for a job is not installed.
   - `builder` and `verifier`: when the repository has a check or test command.
   - `reader`: when the repository has code or logs to ask about.
   - `kit-reviewer`: when work lands by pull request.
   - `kit-researcher`: when the repository depends on libraries or outside tools, or is a research folder.

5. **Ask only what the repository cannot settle.** In one message, show the facts found in step 3 with the file each came from, the proposed agents, and the questions left: usually who uses the project and what they see when it works, and anything step 3 found two answers for. Wait for the answers. The user may also change the list of agents.

6. **Write `AGENTS.md`.**
   - Fill each placeholder with the found or given fact, in plain words. Delete a placeholder line that has no answer, such as host steps for a project with no host, and delete a section left with nothing in it, because a session acts on whatever the file says, a literal `<placeholder>` included.
   - Under Delegation, list the job of each chosen agent, taken from the "Pick the agent by the job" lines of the kit's working rules, end with "If the agent is not installed, use `worker`.", and say these lines apply in this repo whether or not the user-level working rules are installed, because the Copilot cloud agent and teammates without a user install never see those rules.
   - If `AGENTS.md` already exists, do not overwrite it. Show the lines the template would add or change, each next to the section it goes in, and write only the lines the user picks, because the file is the team's and every session there follows it.

7. **Copy the agents.** Copy each chosen `agents/<name>.agent.md` from this skill's folder into `.github/agents/`, unchanged. An identical file there is left alone. If a different file with that name is there, show the difference and ask before replacing it.

8. **Report and stop.** List each file written or changed and each placeholder deleted for want of an answer. Do not commit: the user decides whether the team gets these files. Say that the cloud agent on GitHub.com reads them only once they are merged into the default branch.
