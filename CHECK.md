# Checking the kit works

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
| A document skill says a library is missing | Run the `pip install` line in [kit/skills/README.md](kit/skills/README.md#documents-and-data-documents-pack). |
| `pip install` is blocked | Use the company's internal package mirror. |
| The repo's notes still contain `<placeholders>` | Ask Copilot: "set up this repo for Copilot". |
