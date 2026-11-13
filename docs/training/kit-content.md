# Copilot kit: content reference

This file lists what is in the Copilot kit, taken from the files in `kit/`. It is the source for the training deck. It adds no features that the files do not have. Where the files leave something open, this file says so.

Last checked against the repo on 2026-11-13 (commit `1eb6858` and later, including uncommitted changes to the six agents, the working rules and the README).

## Terms used in this file

- **Agent (custom agent):** a Markdown file ending in `.agent.md`. It has a name, a one-line description, a list of tools, and written instructions. You pick it for a job, and it works with only the tools listed.
- **Tool:** something an agent is allowed to do. The tool names used here are `read` (read files), `edit` (change or create files), `execute` (run shell commands) and `search` (search files). No kit agent has a web tool, because web search is off in the organization.
- **Skill:** a folder with one file, `SKILL.md`. It has a name, a description, and numbered steps. Copilot can use it when your request matches its description.
- **Working rules:** a plain Markdown file of instructions that Copilot reads at the start of a session. In a repo, the kit's rules are installed as `.github/instructions/kit.instructions.md`, and the project's own rules go in `AGENTS.md`; Copilot reads both. In your own Copilot config it is called `copilot-instructions.md`.
- **Hook:** a small command that Copilot runs at a set moment. The kit's hook runs before every tool call and can refuse the call.
- **Task note:** the written task you hand to an agent. It is plain text, with no fixed fields. It says the goal, the context (files, constraints, what is already ruled out), what the agent may do, and what to send back. The agent cannot see your conversation, so the note is all it has to start from.

## 1. What the kit is and why

The kit is a folder of optional files for GitHub Copilot. The README describes it as "Optional agents, skills, working rules and a safety hook for GitHub Copilot."

- It is optional. "Each developer chooses whether to install them."
- It pushes nothing. "Nothing is pushed to any repo." The install script only copies files on your own machine, into your Copilot config or into a repo you point it at. You decide whether to commit anything.
- It has these parts:

| Path in `kit/` | What it is |
|---|---|
| `agents/*.agent.md` | 6 custom agents: worker, kit-researcher, reader, verifier, kit-reviewer, builder. The two `kit-` names keep them apart from Copilot CLI's built-in `research` and `code-review` agents. |
| `skills/*/SKILL.md` | 3 skills: draft-from-examples, spec-interview, session-capture. |
| `templates/AGENTS.md` | Working rules: the task, claims, changes, handing work to agents, git, instruction files. |
| `templates/project/AGENTS.md` | Starter rules for one project. Not installed. |
| `templates/research/AGENTS.md` | Starter rules for a research folder. Not installed. |
| `templates/.github/hooks/deny.json` | A safety hook that refuses a short list of risky actions. |
| `install.py` | Copies the installable files to where Copilot reads them. |

Why it exists, as far as the files say: the working rules ask for a finished task with a stated scope, for claims of done only about what was run and seen working, for changes that match the code around them, and for no force-push or reset of work that is not yours. The agents and skills put those habits into reusable form. The README does not give a company-level reason beyond that. The presenter should add the company's own reason.

What changed on 2026-11-12 (commit `c95c3f2`, "Port worker, researcher, skills and starter templates into the kit; drop project scaffolding and tests"):

- Added: the `worker` and `researcher` agents, the three skills, and the two starter templates.
- Changed: the `reader`, `reviewer`, `verifier` and `builder` agents, `templates/AGENTS.md`, `README.md`, and `install.sh` (it now installs the skills too).
- Removed: the project scaffolding around the kit, and the kit's own automated tests: `kit/tests/test_deny_hook.py`, `kit/tests/live_check.sh` and `kit/.github/workflows/live-check.yml`. The hook now has no automated tests in the repo.

## 2. Install

Run `install.py` from the `kit/` folder of a clone of this repo. It needs Python 3.8 or later and nothing else, so it runs on Windows, macOS and Linux; start it with `python`, `python3` or `py`, whichever your machine uses. The usage is `install.py user | repo [dir] [--update] [--agents NAME,NAME] [--skills NAME,NAME]`. A missing or wrong argument prints the usage and exits with code 2.

### Two modes

| | `python install.py user` | `python install.py repo [dir]` |
|---|---|---|
| Applies to | Every repo you open | One repo only |
| Target folder | `~/.copilot`, or `$COPILOT_HOME` if set | `dir`, default is the current directory |
| Working rules | `~/.copilot/copilot-instructions.md` | `<dir>/.github/instructions/kit.instructions.md` |
| Hook | `~/.copilot/hooks/deny.json` | `<dir>/.github/hooks/deny.json` |
| Agents | `~/.copilot/agents/<name>.agent.md` | `<dir>/.github/agents/<name>.agent.md` |
| Skills | `~/.copilot/skills/<name>/SKILL.md` | `<dir>/.github/skills/<name>/SKILL.md` |
| Committed? | Nothing is committed anywhere | You decide whether to commit the new files |

Both modes copy the same set: the working rules, the hook, all 6 agents and all 3 skills. To install only some agents or skills, name them with `--agents` or `--skills`, for example `--agents worker,reader --skills spec-interview`. An unknown name stops the script and lists the valid names. Leaving out `worker` prints a note, because the working rules fall back to it when the agent for a job is not installed. The two starter templates are never installed. Copy one by hand when you want it.

### Existing files: left alone unless you ask to update

For each file the script prints one line:

- `installed: <path>` when the file was missing and it copied it.
- `unchanged: <path>` when the file is already identical to the kit's copy.
- `skipped, differs from the kit: <path>` when the file is there but different. It is left alone, and the run ends by saying how many files differ.
- `replaced: <path> (old file kept as <name>.bak)` when you ran with `--update` and the file differed.

So running the script twice is safe. Without `--update`, an existing `AGENTS.md` or `copilot-instructions.md` is never replaced.

### Update and remove

- **Update:** run the same install command with `--update`. Each installed file that differs from the kit is replaced, and the old one is kept beside it as `<name>.bak`, so any lines you added can be copied back.
- **Remove:** "delete the installed files it listed." That means the paths on the `installed:` lines. There is no uninstall command.

## 3. The six agents

Every agent file starts with a header giving `name`, `description` and `tools`. Each description starts "Use when ..." and names the kind of job the agent is for. All six take a plain task note (goal, context, what it may do, what to send back) rather than fields to fill in. An agent does not stop because a field is missing. It stops only when it lacks a fact it needs that the files cannot settle (`worker`, `builder`), or, for `worker`, `builder`, `reader` and `kit-researcher`, says so in the first line of its reply when a fact the note relies on is false. Every agent answers in its final message and writes a file only when the note names a path (`reader`, `verifier` and `kit-reviewer` never write one). Each agent carries its own safety rules: never commit or push, never hand work to another agent, keep secrets, tokens, customer data and internal hostnames out of its output, stop and name the command before a risky one (all but `reader`, which runs only read-only commands), put a denied tool call first in its reply and stop, and never run a job in the background.

Two things hold for all of them. First, an instruction in the agent's text is a request, not a lock. The README says this about `reader`: its "no advice" and "read-only commands" rules are "only instructions. Asked directly, it still gave advice in testing." Second, the tool list is what actually limits the agent. `reader`, `verifier` and `kit-reviewer` have no `edit` tool, but each keeps `execute`, so only their written instruction stops a shell command that writes (see "Where the files are unclear" at the end).

The example requests below are written for this reference. They are not in the kit files.

### worker

- **Purpose:** catch-all delegate. It reads, edits and runs commands; its description says it has no web access and returns the result in its final message.
- **When to use:** when only the result of the work is needed afterwards and no other agent fits. `templates/AGENTS.md` (Handing work to agents) lists the cases: an investigation across many files or logs, a batch of small sub-tasks, a change in several steps, or a draft. It is also the fallback when the agent for a job is not installed.
- **Tools:** `read`, `edit`, `execute`, `search`.
- **How it works:** does what the task note asks and nothing beyond it. Where the note names files or a command, it uses those. For a question, it finds the answer in the repository, installed packages and command output, and stops once it is answered. If it needs a fact the note lacks and the files cannot settle, it stops and names it. If a fact the note relies on is false, it says so in the first line of its final message and stops. The final message leads with the result, then the evidence for each claim (path, line and quoted text, or the command and its output), the output of any check the note asked for, and anything it did not do or check. It writes a file only if the note names a path.
- **Limits:** never commits or pushes; never hands work to another agent; never runs a job in the background or with `&`. Keeps secrets, tokens, customer data and internal hostnames out of files, logs and its final message. Before `rm -r`, `git reset --hard`, `git branch -D`, `DROP`, `DELETE`, `TRUNCATE`, a service restart, or overwriting a file it did not create, it stops and names the command.
- **Example request:** "Use the worker agent. Find every place in `src/` that reads the `TIMEOUT_MS` setting, because I am deciding whether to rename it. List each file and line with the exact text. Do not edit anything."

### kit-researcher

- **Purpose:** answers a question about a library, package, API or tool from sources on this machine: the repository, installed packages and their bundled docs, lockfiles, and the tools' own output.
- **When to use:** when a fact has to be checked rather than recalled, such as what the installed version supports, which flags a CLI has, or how two installed libraries compare.
- **Tools:** `read`, `edit`, `execute`, `search`. No `web`. Its text limits `edit` to creating a file at a path the note names.
- **How it works:** answers the question asked. It names anything closely related that it found, but does not widen the research to it. It confirms every library, API or version fact against its source as installed: the package's code, type definitions, README and CHANGELOG (for example under `node_modules/` or `site-packages/`), the lockfile, and the tool's own `--help` or `--version` output. It never states a version or API shape from memory. A fact no local source settles is an open question, not a finding. If a fact the note relies on is false, it says so in the first line of its final message. The final message leads with the answer, then each claim with its source (a path and line, or a command and its output), then the open questions.
- **Report file:** none by default. It writes a file only when the note names a path.
- **Limits:** never commits or pushes; never installs anything; never hands work to another agent; no background jobs. Keeps secrets, tokens, customer data and internal hostnames out of its final message. Stops and names the command before `rm -r`, `git reset --hard`, `git branch -D`, `DROP`, `DELETE`, `TRUNCATE`, a service restart, or overwriting a file. A denied tool call goes first in its final message, and it stops.
- **Example request:** "Use the kit-researcher agent. We use Node 20 and want to add retry logic to our HTTP client. Compare the two ways the installed libraries support, citing a file and line or a command and its output for each claim. Write the result to `docs/research/retry-options.md`."

### reader

- **Purpose:** answers a question about this repository's own code, logs or command output, with facts only. No recommendations, and it writes no file.
- **When to use:** to gather facts before a design, such as who calls a function, where a setting is defined, what a log says, an inventory or a count.
- **Tools:** `read`, `search`, `execute`. It has no `edit` tool.
- **How it works:** where the note names no files, it finds them with `rg`, `grep -rn`, `find` or `git log`. The whole answer is its final message: the answer first, then the evidence for each claim, which is the exact excerpt or output with its path and line numbers or the command that produced it. A file it cannot read is named with the error. It names anything it was asked to check but did not. If a fact the note relies on is false, it says so in the first line.
- **Limits:** runs only read-only commands such as `cat`, `grep`, `find`, `git log`, `git diff`, `git show` or a `SELECT`. It never writes, installs, or calls a paid API. Never commits or pushes; never hands work to another agent. Describes secrets, customer data and internal hostnames instead of quoting them.
- **Honest limit (from the README):** the "no advice" and "read-only commands" rules are only instructions, and it gave advice in testing when asked directly. The tool list has no edit tool, but it keeps the shell, so nothing but the instruction stops a command that writes.
- **Example request:** "Use the reader agent. List every API route in `src/routes/` with its HTTP method and file, as a table with one row per route."

### verifier

- **Purpose:** runs the checks that show whether a finished change works and reports PASS or FAIL for each, with the output. It never fixes anything.
- **When to use:** after a change, when you want an independent run of the checks ("check it", "verify", "does it work").
- **Tools:** `read`, `search`, `execute`. It has no `edit` tool.
- **How it works:** the note gives what changed and the checks. It runs each check once and gives PASS or FAIL, the expected and actual result, and the few output lines that show it. A check that cannot run is a FAIL with the error text. It does not retry a failing check until it passes. With no checks in the note, it finds the tests that cover the changed files (`git diff --name-only`, then the matching tests), runs those, and says which it chose. The final message leads with the overall result (all PASS, or which checks failed), then one line per check, and names any check it did not run. It writes no file.
- **Limits:** fixes nothing and edits no file. Never commits or pushes; never hands work to another agent; no background jobs. Keeps secrets, tokens, customer data and internal hostnames out of its final message. Stops and names the command before `rm -r`, `git reset --hard`, `git branch -D`, `DROP`, `DELETE`, `TRUNCATE` or a service restart.
- **Example request:** "Use the verifier agent. I changed the retry count in `src/client.js`. Check that `npm test` prints `Tests: 42 passed` and that `npm run lint` prints no errors."

### kit-reviewer

- **Purpose:** reviews a diff, branch or pull request against what the change was meant to do. It checks each claim about the change against the code rather than trusting it, and never edits the code under review.
- **When to use:** before you merge a change ("review this", "review my changes").
- **Tools:** `read`, `search`, `execute`. It has no `edit` tool. It sees the change with `git diff`, `git show` or `git log`.
- **How it works:** the note says what the change was meant to do and where the change is (a diff, a branch, a pull request or the uncommitted changes). With no stated aim, it reviews for the points below and says the aim was not given. It looks for:
  - the change does what it was meant to do, and nothing outside that;
  - every caller of a changed function, flag or path still works;
  - no swallowed errors, unchecked return values or empty catch blocks;
  - no insecure code, and no secrets, tokens, customer data or internal hostnames in code, tests, logs or commit messages;
  - the tests cover the change, and the commit message or description matches what the code does.

  It runs the tests that cover the change where that settles a point. The final message leads with `APPROVE` or `CHANGES NEEDED`, then each problem with its file and line, why it is a problem, and the fix in one line. It does not apply the fix. It names anything it did not check.
- **Limits:** never edits the code under review; never commits or pushes; never hands work to another agent; no background jobs. Keeps secrets, tokens, customer data and internal hostnames out of its final message. Stops and names the command before `rm -r`, `git reset --hard`, `git branch -D`, `DROP`, `DELETE`, `TRUNCATE` or a service restart.
- **Example request:** "Use the kit-reviewer agent. Review my branch (`main..HEAD`). It was meant to add a timeout to `fetchUser` and nothing else."

### builder

- **Purpose:** makes a change that is fully specified, where a command can show it worked: a code edit, a config change, an install or a script run. Not for design or open-ended work.
- **When to use:** when you know exactly what the change is and how to check it.
- **Tools:** `read`, `edit`, `execute`, `search`.
- **How it works:** the note gives the change in full. Before editing, it reads the lines it is about to change; if the text has moved or does not match what the note says, it stops and reports what is there. If it needs a fact the note lacks and the files cannot settle, it stops and names it. After the change it runs the command the note gives and the tests that cover the files it changed. With no command in the note, it says which check it ran and why that check shows the change works. The final message leads with what changed, file by file, then the check and its output line, and names anything it did not do or check. It writes a report file only when the note names a path.
- **Limits:** never commits or pushes; never hands work to another agent; no background jobs. Keeps secrets, tokens, customer data and internal hostnames out of code, tests, logs and its final message, and does not write insecure code. Stops and names the command before `rm -r`, `git reset --hard`, `git branch -D`, `DROP`, `DELETE`, `TRUNCATE`, a service restart, or overwriting a file it did not create.
- **Example request:** "Use the builder agent. Change the default page size in `config/app.json` from 20 to 50. No other file reads this value. Check with `jq .pageSize config/app.json`, which should print `50`."

### Quick comparison

| Agent | Tools | Writes files? | Output goes to |
|---|---|---|---|
| worker | read, edit, execute, search | Only if the note names a path | Final message |
| kit-researcher | read, edit, execute, search | Only at a path the note names | Final message |
| reader | read, search, execute | No | Final message |
| verifier | read, search, execute | No | Final message |
| kit-reviewer | read, search, execute | No | Final message |
| builder | read, edit, execute, search | Yes, the change itself; a report file only if the note names a path | Final message |

## 4. The three skills

Each skill is one file, `skills/<name>/SKILL.md`, with a `name` and a `description`. The description ends with "Use when ..." and lists the kinds of request that should start it. The files do not describe how Copilot decides to load a skill, so a trigger here means the situations the description names.

### draft-from-examples

- **What it does:** drafts a new document that matches the structure and voice of finished ones in a folder you point at, such as assessments, policies, reports, posts or letters.
- **Triggers:** you ask for a new document "like the ones in" a folder, "in the same format as" past examples, or name a folder of finished documents and a new topic.
- **Steps:**
  1. Read the examples: every finished document in the folder, or the five most recent if there are more than ten. Skip drafts and templates unless you point at them.
  2. Write down the pattern before drafting: sections and order, length, headings, tables or lists, fixed boilerplate. For voice: person, tense, formality, sentence length, repeated phrases. Also note what changes from one example to the next.
  3. Gather the facts for the new topic from the sources you named, the repo and earlier documents. A fact it cannot find is written as `[TODO: what is needed]`, never guessed.
  4. Draft it. Save it in the same folder, named the way the examples are named. Change only the parts that vary with the topic.
  5. Report: the file path, which examples it follows, and each `[TODO]` left in it.
- **Example:** "Draft a new incident report for the March payment outage, in the same format as the ones in `docs/incidents/`."

### spec-interview

- **What it does:** turns a rough feature idea into a written spec. It gets real examples from you, works out the steps itself, asks you only what the steps cannot settle, then writes the spec file.
- **Triggers:** you want a spec, requirements or a PRD (product requirements document) for a feature; or you say "interview me" about an idea.
- **Steps:**
  1. Read before asking: the project's `AGENTS.md`, its existing spec and design files, and the code the feature touches. It answers what the repo can answer, so every question is one only you can settle.
  2. Get examples first: before any other question, real cases from you. A time the feature would have helped, what came in, and what you would have wanted to see. It offers cases found in the repo, its data or its history for you to confirm or correct, and writes each in your words.
  3. Work out the steps itself, in plain words: what each step takes in and what it works out. It works backwards from the example's answer. Where it does not know how a step is done, it finds out how it is done today. It shows you the steps with the first example walked through them, and you correct them.
  4. Ask only where a step needs you: up to four questions at a time, each option says what it implies, the recommended option comes first, and each question names the step it belongs to. Anything with a usual default gets that default, stated. It stops when the first example walks through every step with no gap that is yours to fill.
  5. Write the spec where the project keeps specs. By default `docs/spec.md` (and `docs/design.md` for implementation answers). With no spec file, it writes `docs/spec.md`. Anything still open is marked as an open question with the step it blocks.
  6. Report: the file path, the steps with the first example walked through them, and the open questions.
- **Example:** "Interview me about this idea: let customers download their order history as a CSV file."

### session-capture

- **What it does:** at the end of a session, summarises what was done and proposes the lines a new session would need. It writes only the lines you pick.
- **Triggers:** you are wrapping up ("that's it for today", "wrap up", "what did we learn"), or you ask what should go in `AGENTS.md` from this session.
- **Steps:**
  1. Summarise the session in a few sentences, from the conversation and the commits it made.
  2. List what a new session would need: what this session had to work out that is not in the code, `git log` or the `AGENTS.md` files. Examples: a command that works, where something lives, a convention, a trap that cost time. It leaves out what an existing line already says, what only mattered to this task, and any rule drawn from a single failure.
  3. Give each candidate a home: how to work in the project goes to the project's `AGENTS.md`; decisions and reasons go to the decisions file; facts about a file, service or vendor go to the findings file; open work or a bug goes to the task list. Where the project has no such file, that home is skipped. Nothing goes in the user-level rules file (`~/.copilot/copilot-instructions.md`).
  4. Propose, then stop: each candidate as the exact line, the file it goes in, and one sentence on why. Nothing is written until you pick.
  5. Write the lines you picked, word for word.
- **Example:** "That's it for today. What should go in AGENTS.md from this session?"

## 5. The working rules (`templates/AGENTS.md`)

Title: "How to work in this organization's repositories". An opening line says the rules apply in every Copilot CLI and VS Code agent session on this machine, and that where a repository's own `AGENTS.md` differs, you follow the repository. It then has six groups. Installed as `.github/instructions/kit.instructions.md` (repo mode, with an `applyTo: "**"` header so it applies to every file) or `~/.copilot/copilot-instructions.md` (user mode).

| Group | What it says, in short |
|---|---|
| **The task** | A task is the result the user asked for, finished: every step the repository's `AGENTS.md` says that kind of work includes, and anything the result does not work without. Anything it works without (an extra test, a refactor, a cleanup) is named at the end as `Also: <step> — <why>`, not done, because the user decides scope. Once the user has confirmed a plan, that plan is the task. When a request can be read more than one way, take the likeliest reading and act; ask first only when the readings lead to different work. If a request rests on something the code shows is not true, say so in one sentence and ask before doing the work. A question gets an answer, not an edit. |
| **Claims** | Say done, fixed or passing only about what you ran and saw work in this session; for anything else, say what you changed and that it was not checked. A fix changes what caused the fault; a change that only hides the symptom is reported as a workaround, with the cause still open. Never make a failure look resolved: no retrying until it passes, skipping a test or loosening an assertion to get green. There is no web search here: check an API, version or flag against the code, the lockfile or the installed package, and if it is not there, say you do not know. Never invent a function, flag, link or source. |
| **Changes** | New code reads like the code around it: its naming, structure and comment style. A comment explains a non-obvious why; the task, ticket and fix history go in the commit or pull request. When your change leaves code unused, remove it in the same change; report other dead code and leave it. Do not write insecure code, and fix it before you finish if you notice it. Keep secrets, tokens, customer data and internal hostnames out of code, tests, logs and commit messages. Before deleting or overwriting, look at what is there; prefer steps that can be undone, and never delete or reset your way past an error. |
| **Handing work to agents** | Hand work to an agent when only its result is needed back. Keep in the main session a file you are about to edit and a lookup one search settles, because everything read there fills the session's context. Pick the agent by the job: a fully specified change that a command can show worked goes to `builder`; facts about this repository's own code, logs or command output, with no advice, to `reader`; a library, package, API or tool fact checked against what is installed, to `kit-researcher`; checking that a finished change works, to `verifier`; reviewing a diff or pull request before it is merged, to `kit-reviewer`; anything else where only the result is needed (an investigation across many files, a batch of small sub-tasks, a change in several steps, a draft), to `worker`. If the agent is not installed, use `worker`. The agent cannot see the conversation. Its task note gives the goal, the context it needs (files, constraints, what is already ruled out), what it may do, and what to send back. The rules may not reach the agent, so the note carries any rule the work depends on. A long job (migration, backfill, bulk update) writes its results and prints progress as it goes; check on it and keep working, and do not wait on it in a loop. |
| **Git** | Review what is staged before each commit. A commit message says why, not only what. Never force-push a shared branch or reset away work that is not yours. |
| **Instruction files** | Change `AGENTS.md`, `copilot-instructions.md` or any instructions file only when the user asks for that rule. Fix an unwanted behaviour by changing the instruction that causes it, not by adding caps, counts or lists of banned words. |

The rules themselves do not mention the deny hook. The hook is a separate file, and the install script installs both together.

## 6. The two starter templates

Neither is installed by `install.py`. Both contain `<placeholders>` in angle brackets for you to fill in.

### `templates/project/AGENTS.md`: starter rules for one project

- **For:** a single project repo.
- **Adopt:** copy it into the repo as `AGENTS.md`, then replace each `<placeholder>`.
- **Sections:**
  - **Start:** the user's request is the task. The task list is read only when the user asks what is next or says to carry on. Work stays inside the project folder.
  - **Commands:** the repo's check command (`<check command>`), the end-to-end command (`<end-to-end command>`), and any host steps.
  - **Records:** where state, spec (`docs/spec.md`), design (`docs/design.md`), decisions and findings live, and the rule to grep the findings file before changing a config, a deployment or code that talks to an outside service.
  - **Work sizes:** an ask gets the steps of its size and nothing more. Small change or bug fix: edit, then the tests it touches and the quick check; a bug in tested code also gets a test that fails first. Feature: the code and its tests under `tests/`, plus one `F<N>` line in `docs/spec.md` where the repo keeps one. Docs-only: edit, with no tests to run.
  - **Landing work:** when the user asks to commit or push, do it the way this team's work lands (fill in, for example, a branch and a pull request, or a commit on main), and `<Release: CI / install line / none.>`. Never rewrite pushed history.
  - **Long tasks:** a task longer than one sitting opens by writing `docs/goal.md` (goal in the user's words, the check that shows it is done, what is out of scope, one progress line per finished step). Read it again after a compaction or resume, because "an instruction given only in chat can drop out of the compaction summary." (Compaction means the session shortens its own history to save room.)
  - **Delegation:** a blank for which agent does each kind of work, and what the session does itself.
  - **Rules:** a blank for rules fixing failures the user named.

### `templates/research/AGENTS.md`: starter rules for a research folder

- **For:** a folder of research from the code and documentation on this machine (prior art, library and tool comparisons), including feasibility work with no project folder. First line: `Kind: research`.
- **Adopt:** copy it into the folder as `AGENTS.md`, then replace each `<placeholder>` (the `<research folder>` and `<topic>` names).
- **Contents:**
  - **Record paths:** reports go in `research/<camelCase+DDMMYY>/report.md`. The `Ask:` line holds the user's words verbatim. The `Source:` line lists every file and command the report used.
  - **Task shape:** (1) run `grep -ril '<topic>' <research folder>` and reuse only a hit whose `Ask:` line equals the user's words verbatim; (2) hand the task to the `kit-researcher` agent with the user's words verbatim and the report path; (3) reply with the conclusion and never list the sources.

## 7. The safety hook (`templates/.github/hooks/deny.json`)

The hook is a `preToolUse` hook: it runs before Copilot uses any tool. The command is written inline in the JSON file. It does not call any other script. It has `"version": 1`, a `bash` command, and `"timeoutSec": 5`. The file has no `matcher` field, so it is not limited to one tool; the README confirms it also blocks editing `.env` files, "not only reading them".

How it works, step by step:

1. It reads the whole tool-call event from standard input.
2. It checks the text of that event against five patterns, in the order below.
3. On the first match, it prints a decision of `deny` with the reason `Blocked by the Copilot kit deny hook: <reason>` and stops.
4. If nothing matches, it prints nothing and exits 0, and Copilot carries on as normal.

### Exactly what it denies

| # | Denied | Reason shown |
|---|---|---|
| 1 | `git push` with `--force`, or with `-f` as a separate word | "force-push rewrites shared history; use --force-with-lease on your own branch" |
| 2 | `git reset` with `--hard` anywhere after it | "git reset --hard discards uncommitted work; commit or use git stash" |
| 3 | `rm` with a combined `rf` or `fr` flag (for example `-rf`, `-fr`) whose target is `/`, `~`, `~/`, `$HOME`, `$HOME/`, `.`, `./`, `..`, `../` or `*` | "rm -rf on a root, home or whole working directory" |
| 4 | The text `.env` followed by a quote mark, a space or the end of the text | "reading or writing .env files can leak secrets; use .env.example" |
| 5 | The text `.pem`, `.key`, `id_rsa`, `id_ed25519` or `id_ecdsa` followed by a quote mark, a space or the end of the text | "private key files are off limits" |

What the patterns let through, read from the patterns themselves:

- `git push --force-with-lease` (the reason text recommends it).
- `git reset --soft`.
- `rm -rf build/` or any target not in the list in row 3. `rm -rf /etc` and `rm -r -f /` are also not matched, because row 3 needs a combined `rf` or `fr` flag and the target must be exactly one of the listed values.
- `.env.example`, and also `.env.local`: row 4 needs a space, quote or end right after `.env`.
- `id_rsa.pub`: row 5 needs a space, quote or end right after the name.
- Row 5 matches any name ending `.pem` or `.key`, so a public certificate saved as `.pem` is blocked too.

## 8. Limits listed in the README

The README's own "Limits" section includes these points about the agents and the hook.

- A hook that times out (5 s here) lets the tool call through. A hook that crashes denies it.
- The hook matches text. It stops mistakes, not a determined person.
- It also blocks editing `.env` files, not only reading them.
- The reader agent's "no advice" and "read-only commands" rules are only instructions. Asked directly, it still gave advice in testing. Its tool list has no edit tool, but it keeps the shell, so nothing but the instruction stops a command that writes.
- Every agent sets `include-custom-instructions: true`, so in Copilot CLI it still reads the repo's instruction files. After a `user` install the rules in `~/.copilot/copilot-instructions.md` may not reach a handed-off agent, and a session started with `--no-custom-instructions` gives no agent any rules. In VS Code, a reported bug (microsoft/vscode#343696) means a handed-off custom agent may get no instruction files at all. So each agent carries its own safety rules, and the task note carries anything else the work depends on.

Also, from this review of the files:

- The kit's automated tests for the hook were removed on 2026-11-12, so nothing in the repo now checks that the hook behaves as described. Try it by hand before relying on it.
- The agent instructions that say "never edit", "fix nothing" or "read-only" are instructions. `reader`, `verifier` and `kit-reviewer` have no `edit` tool, but all three keep `execute` (see below).

## 9. Where the files are unclear or disagree

These are points a presenter may be asked about.

1. **`reader`, `verifier` and `kit-reviewer` have no `edit` tool, but they have `execute`.** The README says of `reader` that "nothing but the instruction stops a command that writes." The same holds for the other two. `execute` can run any shell command. The restriction to read-only commands (`reader`), to fixing nothing (`verifier`) and to never editing the code under review (`kit-reviewer`) is a written instruction in the agent text, the same kind of rule the README says is not reliable.
2. **`kit-researcher` has the `edit` tool.** Its text says to create a file only at a path the note names. That limit is an instruction, not the tool list. `worker` and `builder` also have `edit`, but they are meant to change files.
3. **The project template's Delegation blank.** `templates/project/AGENTS.md` (Delegation) is a blank for which agent does each kind of work, and asks the user to state whether it replaces "the Delegation lines in the user-level working rules". The user-level rules have no section called Delegation. The matching section is Handing work to agents, which already routes each job type to an agent.
4. **Repo installs from before November 2026 put the rules in `AGENTS.md`.** The script now writes them to `.github/instructions/kit.instructions.md` and never touches `AGENTS.md`, so the project template can be copied there. In a repo whose `AGENTS.md` still starts with the kit's rules title, the script prints a warning to delete it, because otherwise Copilot reads the rules twice.
5. **Who commits.** All six agents say "Never commit or push". No template or skill commits or pushes on its own; the project template's Landing work line applies only when the user asks to commit or push.
6. **The hook's `.env` rule and the rules text.** The deny reason says "use .env.example", which works because `.env.example` is allowed. A file named `.env.local` or `.env.production` is not matched.
7. **The hook has only a `bash` command.** The file has no `powershell` or `command` entry. The files do not say what happens on a Windows machine without bash.
