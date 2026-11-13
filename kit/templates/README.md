# Rules, notes and the safety hook

## Rules and notes

| File | What it is | Installed as |
|---|---|---|
| `AGENTS.md` | Your personal rules. They keep Copilot on the task you gave it. | `~/.copilot/copilot-instructions.md`, by `install-user.py` |
| `project/AGENTS.md` | A blank template for a repo's notes: what the project is, how to build and test it, what is out of scope. | The repo's `AGENTS.md`, by `install-repo.py`. Ask Copilot to "set up this repo for Copilot" to fill it in. |
| `research/AGENTS.md` | The same, for a folder of research reports. | Used by Copilot when you set up a research folder |

You can edit both installed files. When you install again, the script keeps your edits (see [INSTALL.md](../../INSTALL.md#if-you-have-installed-before)).

## The safety hook

The safety hook (`.github/hooks/deny.json`) checks every action before Copilot takes it, and stops these:

- **Force-pushing,** which can overwrite other people's work on the server.
- **`git reset --hard`,** which throws away all uncommitted changes.
- **Deleting whole folders** with `rm -rf`.
- **Reading or editing `.env` files and private keys,** where passwords and keys are kept.

Only repos set up with `install-repo.py` have it.

### What the safety hook won't do

- **It catches mistakes, not a determined person.** It looks for words in a command, so a reworded command can get past it.
- **A slow check lets the action through.** If the hook takes longer than 5 seconds, the action is allowed. If it crashes, the action is blocked.
- **It also blocks editing `.env` files,** not only reading them.
- **It is untested on Windows.** Its Windows version has not been run on Windows yet, so test it there before relying on it.
