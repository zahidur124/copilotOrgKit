# Copilot kit

Optional agents, working rules and a safety hook for GitHub Copilot. Each developer chooses whether to install them; nothing is pushed to any repo.

| Path | What it is |
|---|---|
| `agents/*.agent.md` | 4 custom agents: builder, reader, verifier, reviewer. |
| `templates/AGENTS.md` | Working rules: facts, scope, code, verify, git. |
| `templates/.github/hooks/org-deny.json` | A `preToolUse` hook that denies force-push, `git reset --hard`, `rm -rf` on a root, home or whole directory, and `.env` or private key files. |
| `install.sh` | Copies the files above to where Copilot reads them. |
| `tests/live_check.sh` | Runs the latest Copilot CLI against these files: agents load, hook blocks, verifier reports FAIL. `.github/workflows/live-check.yml` runs it weekly. |

## Install

Clone this repo, then pick one:

- `./install.sh user` copies everything into your Copilot config (`~/.copilot`, or `$COPILOT_HOME`). It applies in every repo you open, and nothing is committed anywhere. The rules go in `~/.copilot/copilot-instructions.md`.
- `./install.sh repo [dir]` copies everything into one repo (default: the current directory): `AGENTS.md`, `.github/hooks/` and `.github/agents/`. You decide whether to commit them.

A file that already exists is skipped and listed, never overwritten. To update, delete the old file and run the install again.

To remove, delete the installed files it listed.

## Limits

- A hook that times out (5 s here) lets the tool call through. A hook that crashes denies it.
- The hook matches text. It stops mistakes, not a determined person.
- It also blocks editing `.env` files, not only reading them.
- The reader agent's "no advice" rule is only an instruction. Asked directly, it still gave advice in testing. Its read-only tool list is what holds.
