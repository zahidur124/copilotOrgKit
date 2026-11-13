# Copilot kit

This kit makes GitHub Copilot more careful and more useful in your work. Once it is installed:

- Copilot says a change is done only after it has run it and seen it work, and it never skips a test to get a pass.
- Copilot won't force-push, throw away your uncommitted work, or open your `.env` files.
- You can ask Copilot to review your changes before a pull request, check a change works, answer questions about a spreadsheet, or read a PDF or Word file.

Installing it is optional and up to you. Nothing is added to any repo unless you run the repo script.

## Quick start

You need Python 3.8 or later. In the commands below, type `python3` or `py` instead of `python` if that is how Python starts on your machine.

1. Download this repo and open a terminal in its main folder.
2. Set up Copilot for yourself. You only do this once. Press Enter at every question.
   ```
   python install-user.py
   ```
3. Set up a repo. Do this once for each repo, with the path to that repo. Press Enter at every question.
   ```
   python install-repo.py ~/code/my-service
   ```
4. Open that repo with Copilot and type: **set up this repo for Copilot**. Copilot fills in the repo's notes by reading its code, and asks you what it can't work out.
5. Start a new Copilot session, so Copilot reads the new files.
6. Commit the repo's new files if your team should have them too.

Then ask Copilot in plain words, as you would ask a colleague: "verify my change", "review my changes", "summarise report.pdf".

## Find your way around

| To find out | Read |
|---|---|
| What the words mean (agent, skill, pack, session) | [GLOSSARY.md](GLOSSARY.md) |
| What the install scripts ask, and how to update or remove the kit | [INSTALL.md](INSTALL.md) |
| Where the kit works, how to check it, and what to do if something seems wrong | [CHECK.md](CHECK.md) |
| What each agent does and what to ask it | [kit/agents/README.md](kit/agents/README.md) |
| What each skill does and what to ask it | [kit/skills/README.md](kit/skills/README.md) |
| The coding advice for Java, Scala, NestJS and Flutter | [kit/instructions/README.md](kit/instructions/README.md) |
| Your personal rules, the repo's notes and the safety hook | [kit/templates/README.md](kit/templates/README.md) |
