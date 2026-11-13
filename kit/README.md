# Copilot kit

Optional agents, skills, working rules and a safety hook for GitHub Copilot. Each developer chooses whether to install them; nothing is pushed to any repo.

| Path | What it is |
|---|---|
| `agents/*.agent.md` | 6 custom agents: worker, kit-researcher, reader, verifier, kit-reviewer, builder. The two `kit-` names keep them apart from Copilot CLI's built-in `research` and `code-review` agents. |
| `skills/*/SKILL.md` | 3 skills: draft-from-examples, spec-interview, session-capture. |
| `templates/AGENTS.md` | Working rules: the task, claims, changes, handing work to agents, git, instruction files. |
| `templates/project/AGENTS.md` | Starter rules for one project. Not installed: copy it into a repo as `AGENTS.md` and fill in the `<placeholders>`. |
| `templates/research/AGENTS.md` | Starter rules for a research folder. Not installed: copy it into the folder as `AGENTS.md` and fill in the `<placeholders>`. |
| `templates/.github/hooks/deny.json` | A `preToolUse` hook that denies force-push, `git reset --hard`, `rm -rf` on a root, home or whole directory, and `.env` or private key files. |
| `install.py` | Copies the files above to where Copilot reads them. Needs Python 3.8 or later and nothing else, so it runs on Windows, macOS and Linux. |

## Install

Clone this repo, then run one of these from its `kit/` folder (use `python3` or `py` if that is how Python is started on your machine):

- `python install.py user` copies everything into your Copilot config (`~/.copilot`, or `$COPILOT_HOME`). It applies in every repo you open, and nothing is committed anywhere. The rules go in `~/.copilot/copilot-instructions.md`, the hook in `~/.copilot/hooks/deny.json`, the agents in `~/.copilot/agents/` and the skills in `~/.copilot/skills/`.
- `python install.py repo [dir]` copies everything into one repo (default: the current directory, which must be the repo root): `AGENTS.md`, `.github/hooks/`, `.github/agents/` and `.github/skills/`. You decide whether to commit them.

| Where you use Copilot | `user` install | `repo` install |
|---|---|---|
| Copilot CLI | Yes | Yes |
| VS Code Copilot Chat, with the Copilot harness (the default for new sessions) | Yes | Yes |
| Copilot cloud agent on GitHub.com | No: it reads only the repo | Yes, once the files are merged into the default branch |

VS Code's older Local harness reads agents and instructions from the VS Code profile, not from `~/.copilot`, and is removed in February 2027. Use the Copilot harness.

A file identical to the kit's copy is left alone. A file that differs is skipped and listed, and the run ends by saying how many differ. To update, run the same command with `--update`: each file that differs is replaced, and the old one is kept beside it as `<name>.bak`.

The two starter templates are not installed. Copy one into a repo by hand when you want it.

To remove, delete the installed files it listed.

## Limits

- A hook that times out (5 s here) lets the tool call through. A hook that crashes denies it.
- The hook matches text. It stops mistakes, not a determined person.
- It checks the git and `rm` rules only on commands, so editing a file that mentions `git reset --hard` is allowed. The `.env` and key rules apply to every tool, so it also blocks editing `.env` files, not only reading them.
- The hook has a `bash` command, which runs on macOS, Linux and the cloud agent, and a `powershell` command with the same rules, which Copilot runs on Windows. The `powershell` command is written for Windows PowerShell 5.1 and PowerShell 7 but has not yet been run on Windows, so test it there before relying on it. The cloud agent ignores `powershell` entries.
- The reader agent's "no advice" and "read-only commands" rules are only instructions. Asked directly, it still gave advice in testing. Its tool list has no edit tool, but it keeps the shell, so nothing but the instruction stops a command that writes.
- No agent here has a web tool, because web search is off in the organization. `kit-researcher` and `worker` work from the repository, installed packages and command output.
- Every agent here sets `include-custom-instructions: true`, so when the main agent hands it work in Copilot CLI it still reads the repo's own `AGENTS.md` and `.github/copilot-instructions.md`. Copilot's reference names only repository instruction files, so after a `user` install the rules in `~/.copilot/copilot-instructions.md` may not reach a handed-off agent, and a session started with `--no-custom-instructions` gives no agent any rules. In those cases the brief has to carry what the agent needs.
