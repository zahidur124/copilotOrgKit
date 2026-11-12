# Copilot kit

Optional agents, skills, working rules and a safety hook for GitHub Copilot. Each developer chooses whether to install them; nothing is pushed to any repo.

| Path | What it is |
|---|---|
| `agents/*.agent.md` | 6 custom agents: worker, researcher, reader, verifier, reviewer, builder. |
| `skills/*/SKILL.md` | 3 skills: draft-from-examples, spec-interview, session-capture. |
| `templates/AGENTS.md` | Working rules: facts, scope, code, verify, delegation, rules files, git. |
| `templates/project/AGENTS.md` | Starter rules for one project. Not installed: copy it into a repo as `AGENTS.md` and fill in the `<placeholders>`. |
| `templates/research/AGENTS.md` | Starter rules for a research folder. Not installed: copy it into the folder as `AGENTS.md` and fill in the `<placeholders>`. |
| `templates/.github/hooks/deny.json` | A `preToolUse` hook that denies force-push, `git reset --hard`, `rm -rf` on a root, home or whole directory, and `.env` or private key files. |
| `install.sh` | Copies the files above to where Copilot reads them. |

## Install

Clone this repo, then pick one:

- `./install.sh user` copies everything into your Copilot config (`~/.copilot`, or `$COPILOT_HOME`). It applies in every repo you open, and nothing is committed anywhere. The rules go in `~/.copilot/copilot-instructions.md`, the agents in `~/.copilot/agents/` and the skills in `~/.copilot/skills/`.
- `./install.sh repo [dir]` copies everything into one repo (default: the current directory): `AGENTS.md`, `.github/hooks/`, `.github/agents/` and `.github/skills/`. You decide whether to commit them.

A file that already exists is skipped and listed, never overwritten. To update, delete the old file and run the install again.

The two starter templates are not installed. Copy one into a repo by hand when you want it.

To remove, delete the installed files it listed.

## Limits

- A hook that times out (5 s here) lets the tool call through. A hook that crashes denies it.
- The hook matches text. It stops mistakes, not a determined person.
- It also blocks editing `.env` files, not only reading them.
- The reader agent's "no advice" rule is only an instruction. Asked directly, it still gave advice in testing. Its read-only tool list is what holds.
