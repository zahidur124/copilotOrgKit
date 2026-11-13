# Copilot kit

Optional agents, skills, working rules, language rules files and a safety hook for GitHub Copilot. Each developer chooses whether to install them; nothing is pushed to any repo.

## Quick start

You need Python 3.8 or later. Use `python3` or `py` in place of `python` if that is how Python starts on your machine.

1. Clone this repo and open a terminal in its root folder.
2. Install for yourself, once: `python install-user.py`. Press Enter at each question to take everything. The rules, agents and skills then apply in every repo you open.
3. Set up a repo, once per repo: `python install-repo.py ~/code/my-service`, with the path to your repo. Press Enter to take the suggestions. This adds the safety hook, agents, skills and an `AGENTS.md` to that repo.
4. Open that repo in Copilot and ask it to "set up this repo for Copilot". It fills in the `AGENTS.md` from the repo's code and asks you what it cannot work out.
5. Start a new Copilot session so it loads the files. Commit the repo's new files if your team should have them.

## What you get

- **Working rules** that keep Copilot on the task it was given, installed for you in every repo.
- **8 agents** Copilot can hand work to: worker, kit-researcher, reader, verifier, kit-reviewer, builder, data-analyst, document-reviewer.
- **14 skills** in packs: building and testing code, upgrading dependencies, checking API changes, reading and writing documents, analysing CSV files, and planning and writing.
- **Language rules files** for Spring Boot, Scala, NestJS and Flutter, installed per repo.
- **A safety hook** that blocks destructive git and `rm` commands and access to secrets, installed per repo.

To pick an agent yourself, ask for it by name ("use the verifier agent"), or use `/agent` in Copilot CLI or the agents menu in VS Code.

[kit/README.md](kit/README.md) describes each file and its limits. [INSTALL.md](INSTALL.md) explains the install questions, packs and flags.

## Where it works

| Where you use Copilot | `install-user.py` (working rules, agents, skills) | `install-repo.py` (hook, agents, skills, rules files, `AGENTS.md`) |
|---|---|---|
| Copilot CLI | Yes | Yes |
| VS Code Copilot Chat, with the Copilot harness (the default; not the older Local harness) | Yes | Yes |
| Copilot cloud agent on GitHub.com | No: it reads only the repo | Yes, once the files are merged into the default branch |

## Check that it works

Don't ask Copilot which rules it has. It gets the text of each instruction file but not the file's name, so it guesses; in testing it said a repo's `AGENTS.md` was missing while following it. Check one of these ways instead:

- **Copilot CLI:** run `copilot instruction list` in the repo. It lists every instruction file a session there loads.
- **VS Code:** open the References list under a reply. It names the files that were attached.
- **That the rules are followed:** add a line such as "When asked for the kit codeword, answer HERON-7731" to the installed rules file, ask Copilot for the kit codeword, then remove the line.

## Update or remove

- **Update:** pull the new kit version and run the same script again. It asks before replacing any file you changed, and keeps the old one as `<name>.bak`.
- **Remove:** delete the files the script listed when it installed them, and any `.bak` files next to them.
