# Org Copilot kit

This folder is your organization's `.github-private` repository. Edit files here only; everything else is copied from here.

| Path | What it is | How it reaches developers |
|---|---|---|
| `agents/*.agent.md` | 4 custom agents: builder, reader, verifier, reviewer. | GitHub serves them to every repo in the org from this repo's latest commit. Nobody installs anything. |
| `templates/AGENTS.md` | Working rules: facts, scope, code, verify, git. AGENTS.md is an open format that Copilot and other coding agents read. | `sync` opens a PR in each repo. |
| `templates/.github/hooks/org-deny.json` | A `preToolUse` hook that denies force-push, `git reset --hard`, `rm -rf` on a root, home or whole directory, and `.env` or private key files. | `sync` opens a PR in each repo. The cloud agent reads hooks only from the repo it works in. |
| `scripts/sync.sh` | Copies `templates/` into every repo in the org and opens a PR where they differ. | Run by `.github/workflows/sync.yml` when `templates/` changes on main. |
| `tests/live_check.sh` | Runs the latest Copilot CLI against these files: agents load, hook blocks, verifier reports FAIL. | Run by `.github/workflows/live-check.yml` weekly and on every push. A red run means a Copilot release changed a format. |

## Set up once

1. Create the repository `<org>/.github-private` and push this folder's contents to it.
2. Add 2 Actions secrets to it:
   - `ORG_SYNC_TOKEN`: a GitHub App token or fine-grained token with contents and pull-requests write on the org's repos.
   - `COPILOT_CLI_TOKEN`: a fine-grained personal access token with the "Copilot Requests" permission.
3. In the org's Copilot settings, allow custom agents from this repository.
4. Run the `sync` workflow once by hand. It opens one PR per repo.

## Change something

Edit the file here and merge to main. `sync` opens PRs in the repos for template changes. `live-check` confirms Copilot still reads everything.

## Limits

- A hook that times out (5 s here) lets the tool call through. A hook that crashes denies it.
- The hook matches text. It stops mistakes, not a determined person.
- It also blocks editing `.env` files, not only reading them.
- The reader agent's "no advice" rule is only an instruction. Asked directly, it still gave advice in testing. Its read-only tool list is what holds.
