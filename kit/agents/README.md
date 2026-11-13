# Agents

An agent is a helper Copilot can pass one kind of job to, like a teammate who only does reviews. Each agent is one `.agent.md` file in this folder. The install scripts let you pick which ones to install.

You don't need to name an agent. Copilot picks the right one from your request. To pick one yourself, name it ("use the verifier agent"), or use `/agent` in Copilot CLI or the agents menu in VS Code.

| Agent | Ask Copilot, for example | You get back |
|---|---|---|
| `verifier` | "verify my change" | PASS or FAIL for each check, with the output. It never fixes anything. |
| `kit-reviewer` | "review my changes" | APPROVE, or a list of problems, each with its file and line. It never edits code. |
| `builder` | "add a `--dry-run` flag to the export script" | The change, and the command that shows it works. Only for changes you have fully described. |
| `reader` | "where is the timeout setting defined?" | The answer with file and line. No advice. |
| `kit-researcher` | "does the version of axios we use support retries?" | The answer, and where it was found in the installed library |
| `worker` | "go through these logs and list every distinct error" | The result of any larger job no other agent fits |
| `data-analyst` | "how many orders per month are in sales.csv?" | The numbers, and the script that produced them. Your file is never changed. |
| `document-reviewer` | "check contract.docx against policy.pdf" | Findings, each with its page or section and the quoted text. It never edits the document. |

The two `kit-` names keep them apart from Copilot CLI's own `research` and `code-review` agents.

## What agents won't do

- **No internet.** Web search is turned off in the organization, so agents work only from your code, installed libraries and command output.
- **Agents may not see your rules.** When Copilot passes a job to an agent, the agent may not get your personal rules or the repo's notes. Each agent has its own safety rules, but put everything else the job needs in your request.
- **`reader` only promises not to change things.** It has no tool for editing files, but it can still run commands. If you ask it directly, it may also give advice.
