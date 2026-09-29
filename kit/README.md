# Org Copilot kit

One folder that ships to all 3 Copilot surfaces: the cloud agent on GitHub, VS Code, and Copilot CLI.

| File | What it does |
|---|---|
| `copilot-instructions.md` | Working rules: facts, scope, code, verify, git. |
| `agents/*.agent.md` | 4 custom agents: builder, reader, verifier, reviewer. |
| `hooks/hooks.json` | A `preToolUse` hook that denies force-push, `git reset --hard`, `rm -rf` on a root, home or whole directory, and `.env` or private key files. |
| `plugin.json` | Makes this folder a Copilot CLI plugin. |

## Roll out

1. Instructions: an org owner pastes `copilot-instructions.md` into Organization settings, Copilot, Custom instructions. A repo can also copy it to `.github/copilot-instructions.md`.
2. Agents for the whole org: copy `agents/` to the root of the org's `.github-private` repository (`/agents/*.agent.md`). They then appear in the cloud agent, VS Code and the CLI for every repo in the org.
3. Hook for the cloud agent: copy `hooks/hooks.json` into each repo as `.github/hooks/org-deny.json`. The cloud agent reads hooks only from the repo it works in.
4. Hook and agents for the CLI: each developer runs `copilot plugin install <path or repo of this folder>`. For a whole fleet, IT can install `hooks/hooks.json` as a policy hook in `/etc/github-copilot/policy.d/`, which users cannot turn off.

## Limits

- A hook that times out (5 s here) lets the tool call through. A hook that crashes denies it.
- The hook matches text, so a rename such as `cat $(echo .e)nv` gets past it. It stops mistakes, not an attacker.
- It also blocks editing `.env` files, not only reading them.
