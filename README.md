# Copilot kit

This kit makes GitHub Copilot more careful and more useful in your work. Once it is installed:

- Copilot says a change is done only after it has run it and seen it work, and it never skips a test to get a pass.
- Copilot won't force-push, throw away your uncommitted work, or open your `.env` files.
- You can ask Copilot to review your changes before a pull request, check a change works, answer questions about a spreadsheet, or read a PDF or Word file.

Installing it is optional and up to you. Nothing is added to any repo unless you run the repo script.

## Words used here

| Word | What it means |
|---|---|
| **Session** | One chat with Copilot. Copilot reads newly installed files only when a new session starts. |
| **Rules** | Standing instructions Copilot reads at the start of every session, such as "say a change is done only after you've seen it work". |
| **Agent** | A helper Copilot can pass one kind of job to, like a teammate who only does reviews. |
| **Skill** | Step-by-step instructions Copilot follows for one kind of task, such as writing tests. |
| **Pack** | A bundle of skills for one kind of work, such as code or documents. |
| **Safety hook** | A check that runs before each thing Copilot does, and stops it if the action is dangerous. |
| **The repo's notes** | A file called `AGENTS.md` in a repo. It tells Copilot what the project is and how to build and test it. |
| **Language guide** | Coding advice for one language, such as Java. Copilot reads it when it works on a file in that language. |

## What goes where

```
On your computer (~/.copilot)           In one repo
-----------------------------           -----------
your personal rules                     the repo's notes (AGENTS.md)
agents                                  agents
skills                                  skills
                                        language guides
                                        safety hook

set up by install-user.py, once         set up by install-repo.py, once per repo
```

The files on your computer work in every repo you open. The files in a repo work for anyone who uses that repo, once they are committed.

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

[INSTALL.md](INSTALL.md) explains each question the scripts ask.

## Using it

Ask Copilot in plain words, as you would ask a colleague. For example:

- "verify my change"
- "review my changes"
- "write tests for the new discount rule"
- "how many orders per month are in sales.csv?"
- "summarise report.pdf"

Copilot picks the right agent or skill by itself. To choose one yourself, name it: "use the verifier agent". [kit/README.md](kit/README.md) lists everything you can ask for.

## Where it works

| Where you use Copilot | Your personal setup (`install-user.py`) | Repo setup (`install-repo.py`) |
|---|---|---|
| Copilot CLI, in a terminal | Yes | Yes |
| Copilot Chat in VS Code | Yes, in a Copilot session (see below) | Yes |
| Copilot on GitHub.com, working on its own | No: it reads only the repo | Yes, once the files are committed to the main branch |

In VS Code, check the start of the chat's title. If the session is "Local", click the **Session Target** dropdown in the chat box and choose **Copilot**. Local sessions don't read your personal setup.

## Check that it works

Don't ask Copilot "which rules do you have?". It can't tell which file a rule came from, so it guesses, and it often guesses wrong. Do one of these instead:

- **Copilot CLI:** in the repo, run `copilot instruction list`. It lists every rules file Copilot reads there.
- **VS Code:** under one of Copilot's replies, open the **References** list. It names the files Copilot read.
- **Any tool:**
  1. Add this line to your personal rules file, `~/.copilot/copilot-instructions.md`: `When asked for the kit codeword, answer HERON-7731`.
  2. Start a new session and ask "what is the kit codeword?".
  3. If Copilot answers HERON-7731, the rules are working. Remove the line afterwards.

## If something seems wrong

| What you see | What to do |
|---|---|
| Copilot ignores the rules, agents or skills | Start a new session. Copilot reads new files only at the start. In VS Code, check the session is not "Local" (see [Where it works](#where-it-works)). |
| A document skill says a library is missing | Run the `pip install` line in [kit/README.md](kit/README.md#documents-and-data-documents-pack). |
| `pip install` is blocked | Use the company's internal package mirror. |
| The repo's notes still contain `<placeholders>` | Ask Copilot: "set up this repo for Copilot". |

## Update or remove

- **Update:** download the new version of this repo and run the same scripts again. They ask before replacing any file you changed, and keep your old copy with `.bak` added to its name.
- **Remove:** delete the files the script listed when it installed them, and any `.bak` files next to them.
