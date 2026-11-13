# Copilot kit: content reference

This file lists what is in the Copilot kit, taken from the files in `kit/`. It is the source for the training deck. It adds no features that the files do not have. Where the files leave something open, this file says so.

Last checked against the repo on 2026-11-12 (commit `c95c3f2` and later, including uncommitted changes to the working rules, `worker`, `kit-researcher`, the research template and the README).

## Terms used in this file

- **Agent (custom agent):** a Markdown file ending in `.agent.md`. It has a name, a one-line description, a list of tools, and written instructions. You pick it for a job, and it works with only the tools listed.
- **Tool:** something an agent is allowed to do. The tool names used here are `read` (read files), `edit` (change or create files), `execute` (run shell commands) and `search` (search files). No kit agent has a web tool, because web search is off in the organization.
- **Skill:** a folder with one file, `SKILL.md`. It has a name, a description, and numbered steps. Copilot can use it when your request matches its description.
- **Working rules:** a plain Markdown file of instructions that Copilot reads at the start of a session. In a repo it is called `AGENTS.md`. In your own Copilot config it is called `copilot-instructions.md`.
- **Hook:** a small command that Copilot runs at a set moment. The kit's hook runs before every tool call and can refuse the call.
- **Brief:** the written task you hand to an agent. Most kit agents expect a brief with named fields (Goal, Done when, Context, Files, Report path).
- **Done when:** a command plus the output it must print. It is how a task proves it is finished.

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

Run `install.py` from the `kit/` folder of a clone of this repo. It needs Python 3.8 or later and nothing else, so it runs on Windows, macOS and Linux; start it with `python`, `python3` or `py`, whichever your machine uses. The usage is `install.py user | repo [dir] [--update]`. A missing or wrong argument prints the usage and exits with code 2.

### Two modes

| | `python install.py user` | `python install.py repo [dir]` |
|---|---|---|
| Applies to | Every repo you open | One repo only |
| Target folder | `~/.copilot`, or `$COPILOT_HOME` if set | `dir`, default is the current directory |
| Working rules | `~/.copilot/copilot-instructions.md` | `<dir>/AGENTS.md` |
| Hook | `~/.copilot/hooks/deny.json` | `<dir>/.github/hooks/deny.json` |
| Agents | `~/.copilot/agents/<name>.agent.md` | `<dir>/.github/agents/<name>.agent.md` |
| Skills | `~/.copilot/skills/<name>/SKILL.md` | `<dir>/.github/skills/<name>/SKILL.md` |
| Committed? | Nothing is committed anywhere | You decide whether to commit the new files |

Both modes copy the same set: the working rules, the hook, all 6 agents and all 3 skills. The two starter templates are never installed. Copy one by hand when you want it.

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

Every agent file starts with a header giving `name`, `description` and `tools`. Five of the six expect a brief with named fields. `worker` takes a free-form brief. All six say "Never commit" and none can spawn another agent.

Two things hold for all of them. First, an instruction in the agent's text is a request, not a lock. The README says this about `reader`: its "no advice" rule "is only an instruction. Asked directly, it still gave advice in testing." Second, the tool list is what actually limits the agent. Even so, several agents are told not to edit files but still have the `edit` tool (see "Where the files are unclear" at the end).

The example requests below are written for this reference. They are not in the kit files.

### worker

- **Purpose:** catch-all delegate. It reads, edits and runs commands; its description says it has no web access.
- **When to use:** when only the result of the work is needed afterwards. `templates/AGENTS.md` (Handing work to agents) lists the cases: reading across many files or logs, a batch of small sub-tasks, or a change a brief can state in full.
- **Tools:** `read`, `edit`, `execute`, `search`.
- **How it works:** does what the brief asks and nothing beyond it. Reads only the files the brief names when the brief names them. For a question, it searches the repository, installed packages and command output. If a fact is missing, it stops and names it. If a fact the brief relies on is false, it says so in the first line of its reply. Its final message is the report: what it produced, the evidence for each claim (path, line and quoted text, or the command and its output), and the output of any check. It writes a file only if the brief names a path.
- **Limits:** never commits; never spawns another agent; never runs a job in the background or with `&`. Before `rm -r`, `git reset --hard`, `git branch -D`, `DROP`, `DELETE`, `TRUNCATE`, a service restart, or overwriting a file it did not create, it stops and names the command.
- **Example request:** "Use the worker agent. Goal: find every place in `src/` that reads the `TIMEOUT_MS` setting, so I can decide whether to rename it. Done when: you list each file and line with the exact text. Do not edit anything."

### kit-researcher

- **Purpose:** research with a written report, for a build, a new project or a library comparison, from what is on this machine: the repository, installed packages and their bundled docs, lockfiles, and the tools' own output.
- **When to use:** when a decision depends on a library, API, version or tool fact that has to be checked rather than recalled, such as which version is installed or what an option does.
- **Tools:** `read`, `edit`, `execute`, `search`. No `web`.
- **How it works:** confirms every library, API or version fact against its source on the machine: the installed package's code, type definitions, README and CHANGELOG (for example under `node_modules/` or `site-packages/`), the lockfile, and the tool's own `--help` or `--version` output. It cites a file path and line, or a command and its output, and never states a version from memory. A fact no local source settles goes in the report as an open question, not as a finding. Before comparing options, it opens the subject's own primary source as installed (README, CHANGELOG, release notes) and lists every option found, even those the brief left out. If a claim names a package, CLI or version, it runs it where it can (a resolver, a dry-run install against the organization's package registry, `--help`). The report is a table with columns `claim | what was run | output | source`, with a summary at the top. It starts the report file first and adds each finding as it goes, so a partial run still leaves a usable report.
- **Report path:** the brief's `Report path:`. If none is given, `docs/research/kit-researcher-<task-slug>.md` in the current project.
- **Limits:** the same list as `worker` (never commits, no background jobs, stops before risky commands). A denied tool call, an unreadable path or a missing prerequisite goes first in the report, and it stops.
- **Example request:** "Use the kit-researcher agent. Goal: compare two ways to add retry logic to our HTTP client, using the installed libraries' source and changelogs. Done when: the report has a table of claims, each citing a file and line or a command and its output. Context: we use Node 20. Report path: `docs/research/retry-options.md`."

### reader

- **Purpose:** reads a named set of files, code paths, logs or command outputs and reports facts only. No recommendations.
- **When to use:** to gather facts before a design, such as an inventory, verbatim excerpts, counts, or which file defines something.
- **Tools:** `read`, `search`, `execute`. It has no `edit` tool, so it cannot change files.
- **How it works:** it writes no file. The whole report is its final message: the answer in at most 5 lines, then one row per claim with the exact excerpt or output and its path and line numbers. A file it cannot read becomes one line `MISSING <path> — <error>`. It records `git rev-parse HEAD` of each repo it reads.
- **Limits:** runs only read-only commands such as `cat`, `grep`, `find`, `git log`, `git diff`, `git show` or a `SELECT`. It never writes, installs, or calls a paid API. Never commits.
- **Honest limit (from the README):** the "no advice" rule is only an instruction, and it gave advice in testing when asked directly. The read-only tool list is what holds.
- **Example request:** "Use the reader agent. Goal: list every API route in `src/routes/` with its HTTP method and file. Done when: a table with one row per route. Files: `src/routes/`."

### verifier

- **Purpose:** runs the Done when commands of a finished change and reports PASS or FAIL with the exact output. It never fixes anything.
- **When to use:** after a change, when you want an independent run of the checks.
- **Tools:** `read`, `edit`, `execute`, `search`.
- **How it works:** for each Done when line it runs the command once, pastes the first 5 lines of output, and writes PASS or FAIL with the expected and actual line. A command that cannot run is a FAIL with the error text. It stops without running anything if Done when is missing. With a Report path it writes one PASS or FAIL block per line to that file. With none, the whole report is its final message and no file is written.
- **Limits:** fixes nothing; edits no file except its report. Never commits; no background jobs.
- **Example request:** "Use the verifier agent. Done when: `npm test` prints `Tests: 42 passed`. And `npm run lint` prints no errors."

### kit-reviewer

- **Purpose:** reviews a diff or pull request against the task that produced it. Mechanical checks only. It assumes the diff is wrong until shown right.
- **When to use:** before you merge a change, to check it against the brief and the rules.
- **Tools:** `read`, `edit`, `execute`, `search`.
- **How it works:** the brief names the checks from the agent's own table:

| Check | What it verifies |
|---|---|
| `fixture` | the failing-direction case F1..Fn runs and fails ahead of every passing case P1..Pn |
| `wiring` | every caller of a changed name (function, flag, path) still parses and resolves |
| `scope` | nothing in the diff is outside the brief / done_when |
| `claims` | commit message and report match what the code actually does |
| `silent-fail` | no swallowed errors, unchecked returns, empty catch blocks |
| `framework` | a new executable/tool names the existing framework considered and why rejected |

  It also fills in a four-line rule checklist (`repair-before-replace`, `scope = done_when`, `positive control`, `evidence`). Each line is `OK`, `REJECT` or `N/A` with evidence. The verdict is `APPROVE` or `REJECT` with a `file:line` reason for each point. A REJECT ends its turn. It names the fix and does not apply it.
- **Limits:** never edits the code under review; one review per brief (a second round needs a new brief); never commits; no background jobs. It stops without reviewing if a brief field is missing.
- **Example request:** "Use the kit-reviewer agent. Goal: review my branch against the task 'add a timeout to fetchUser'. Done when: a verdict of APPROVE or REJECT with reasons. Context: none. Files: the diff of `main..HEAD`. Checks: scope, claims, silent-fail. Report path: `docs/review-fetchuser.md`."

### builder

- **Purpose:** applies a fixed-spec change that has a machine-checkable Done when. Examples in the file: a single-file edit, a config change, an install or a script run. Not for design or open-ended work.
- **When to use:** when you know exactly what the change is and how to check it.
- **Tools:** `read`, `edit`, `execute`, `search`.
- **How it works:** the brief gives Goal, Done when, Context, Files and Report path, written out in full. It reads the files, makes the change, runs the repo's test command and the linter, and runs the Done when command and puts its output line in the report. It writes the report to the Report path as it goes. It stops without editing if a field is missing. It greps the lines that `Files:` describes first, and if the text is not as the brief says, it stops and reports what is there.
- **Limits:** never edits `*.md` files. Never commits. Stops and names the command before `rm -r`, `git reset --hard`, `git branch -D`, `DROP`, `DELETE`, `TRUNCATE`, a service restart, or overwriting a file it did not create. No background jobs.
- **Example request:** "Use the builder agent. Goal: change the default page size in `config/app.json` from 20 to 50. Done when: `jq .pageSize config/app.json` prints `50`. Context: no other file reads this value. Files: `config/app.json`. Report path: `docs/builder-pagesize.md`."

### Quick comparison

| Agent | Tools | Writes files? | Output goes to |
|---|---|---|---|
| worker | read, edit, execute, search | Only if the brief names a path | Final message |
| kit-researcher | read, edit, execute, search | Report file | Report path, plus summary in final message |
| reader | read, search, execute | No | Final message |
| verifier | read, edit, execute, search | Report only | Report path, or final message if none |
| kit-reviewer | read, edit, execute, search | Report only | Report path, plus verdict in final message |
| builder | read, edit, execute, search | Yes, the change and a report (not `*.md`) | Report path, plus summary in final message |

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
- **Triggers:** you want a spec, requirements or a PRD (product requirements document) for a feature; you say "interview me" about an idea; or you describe a feature too loosely to build from.
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
  5. Write the lines you picked, word for word. Then commit them.
- **Example:** "That's it for today. What should go in AGENTS.md from this session?"

## 5. The working rules (`templates/AGENTS.md`)

Title: "How to work in this organization's repositories". An opening line says the rules apply in every Copilot CLI and VS Code agent session on this machine, and that where a repository's own `AGENTS.md` differs, you follow the repository. It then has six groups. Installed as `AGENTS.md` (repo mode) or `~/.copilot/copilot-instructions.md` (user mode).

| Group | What it says, in short |
|---|---|
| **The task** | A task is the result the user asked for, finished: every step the repository's `AGENTS.md` says that kind of work includes, and anything the result does not work without. Anything it works without (an extra test, a refactor, a cleanup) is named at the end as `Also: <step> — <why>`, not done, because the user decides scope. Once the user has confirmed a plan, that plan is the task. When a request can be read more than one way, take the likeliest reading and act; ask first only when the readings lead to different work. If a request rests on something the code shows is not true, say so in one sentence and ask before doing the work. A question gets an answer, not an edit. |
| **Claims** | Say done, fixed or passing only about what you ran and saw work in this session; for anything else, say what you changed and that it was not checked. A fix changes what caused the fault; a change that only hides the symptom is reported as a workaround, with the cause still open. Never make a failure look resolved: no retrying until it passes, skipping a test or loosening an assertion to get green. There is no web search here: check an API, version or flag against the code, the lockfile or the installed package, and if it is not there, say you do not know. Never invent a function, flag, link or source. |
| **Changes** | New code reads like the code around it: its naming, structure and comment style. A comment explains a non-obvious why; the task, ticket and fix history go in the commit or pull request. When your change leaves code unused, remove it in the same change; report other dead code and leave it. Do not write insecure code, and fix it before you finish if you notice it. Keep secrets, tokens, customer data and internal hostnames out of code, tests, logs and commit messages. Before deleting or overwriting, look at what is there; prefer steps that can be undone, and never delete or reset your way past an error. |
| **Handing work to agents** | Hand work to the `worker` agent when only its result is needed: reading across many files or logs, a batch of small sub-tasks, or a change a brief can state in full. Keep in the main session a file you are about to edit and a lookup one search settles, because everything read there fills the session's context. A brief says what the work is for, what done looks like, what is already ruled out, and the files or commands. The agent may not see these rules, so the brief carries any rule it must follow. A long job (migration, backfill, bulk update) writes its results and prints progress as it goes; check on it and keep working, and do not wait on it in a loop. |
| **Git** | Review what is staged before each commit. A commit message says why, not only what. Never force-push a shared branch or reset away work that is not yours. |
| **Instruction files** | Change `AGENTS.md`, `copilot-instructions.md` or any instructions file only when the user asks for that rule. Fix an unwanted behaviour by changing the instruction that causes it, not by adding caps, counts or lists of banned words. |

The rules themselves do not mention the deny hook. The hook is a separate file, and the install script installs both together.

## 6. The two starter templates

Neither is installed by `install.py`. Both contain `<placeholders>` in angle brackets for you to fill in.

### `templates/project/AGENTS.md`: starter rules for one project

- **For:** a single project repo.
- **Adopt:** copy it into the repo as `AGENTS.md`, then replace each `<placeholder>`.
- **Sections:**
  - **Start:** read the task list (if any) and `git log --oneline -5`; the next row is the first that is neither done nor parked. Work stays inside the project folder.
  - **Commands:** the repo's check command (`<check command>`), the end-to-end command (`<end-to-end command>`), and any host steps.
  - **Records:** where state, spec (`docs/spec.md`), design (`docs/design.md`), decisions and findings live, and the rule to grep the findings file before changing code, config or a deployment.
  - **Work sizes:** every ask is one of four. Bug: branch `fix-<slug>`, a test that fails first, cause in one sentence, smallest fix. Small change: branch, edit, update tests, run them and the quick check. Feature: one `F<N>` line in `docs/spec.md`, branch `f<N>-<slug>`, tests under `tests/` then code. Docs-only: commit on main, push.
  - **Session end:** merge each finished branch to main with `--ff-only`, push to `<remote>`, delete the branch, never rewrite pushed history. A worktree path is described. Fill in `<Worktree: yes or no.>` and `<Release: CI / install line / none.>`.
  - **Goal file:** a Feature, or any task longer than one sitting, opens by writing `docs/goal.md` (goal in the user's words, the check that shows it is done, what is out of scope, one progress line per finished step). Read it again after a compaction or resume, because "an instruction given only in chat can drop out of the compaction summary." (Compaction means the session shortens its own history to save room.)
  - **Delegation:** a blank for which agent does each kind of work, what the session does itself, and which agents commit or push.
  - **Rules:** a blank for rules fixing failures the user named.

### `templates/research/AGENTS.md`: starter rules for a research folder

- **For:** a folder of research from the code and documentation on this machine (prior art, library and tool comparisons), including feasibility work with no project folder. First line: `Kind: research`.
- **Adopt:** copy it into the folder as `AGENTS.md`, then replace each `<placeholder>` (the `<research folder>` and `<topic>` names).
- **Contents:**
  - **Record paths:** reports go in `research/<camelCase+DDMMYY>/report.md`. The `Ask:` line holds the user's words verbatim. The `Source:` line lists every file and command the report used.
  - **Task shape:** (1) run `grep -ril '<topic>' <research folder>` and reuse only a hit whose `Ask:` line equals the user's words verbatim; (2) hand the task to the `kit-researcher` agent with the user's words verbatim and the report path; (3) reply with the conclusion and never list the sources.
  - **Git:** commit the report on main and push. No worktree.

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

These four lines are the README's own "Limits" section.

- A hook that times out (5 s here) lets the tool call through. A hook that crashes denies it.
- The hook matches text. It stops mistakes, not a determined person.
- It also blocks editing `.env` files, not only reading them.
- The reader agent's "no advice" rule is only an instruction. Asked directly, it still gave advice in testing. Its read-only tool list is what holds.

Also, from this review of the files:

- The kit's automated tests for the hook were removed on 2026-11-12, so nothing in the repo now checks that the hook behaves as described. Try it by hand before relying on it.
- The agent instructions that say "never edit" or "fix nothing" are instructions. Several agents that are told not to edit still carry the `edit` tool (see below).

## 9. Where the files are unclear or disagree

These are points a presenter may be asked about.

1. **`reader` is called read-only, but has `execute`.** The README says "Its read-only tool list is what holds." The tool list is `read`, `search`, `execute`. `execute` can run any shell command. The restriction to read-only commands is a written instruction in the agent text, the same kind of rule the README says is not reliable.
2. **Agents told not to edit have the `edit` tool.** `verifier` ("You fix nothing and edit no file except your report") and `kit-reviewer` ("You never edit the files under review") both list `edit`. They need it to write their report. The limit is an instruction. `builder` is told "Never edit `*.md`" and also has `edit`.
3. **The rules name `worker` only.** `templates/AGENTS.md` (Handing work to agents) names the `worker` agent and no other. `templates/project/AGENTS.md` (Delegation) is a blank for which agent does each kind of work, and asks the user to state whether it replaces "the Delegation lines in the user-level working rules". The user-level rules no longer have a section called Delegation; the matching section is Handing work to agents.
4. **Where `kit-researcher` writes its report.** The agent's description says the Report path is "a file under the project's docs/", and its text defaults to `docs/research/kit-researcher-<task-slug>.md`. The research template puts reports in `research/<camelCase+DDMMYY>/report.md`, which is not under `docs/`. The template's path is given in the brief, so the two can work together, but the files do not say so.
5. **`kit-researcher` says it stops if a field is missing, yet allows no Report path.** The description says it "stops without searching if a field is missing" and also allows "no Report path". The body supplies a default path, so a missing Report path does not stop it.
6. **Repo-mode install and the project template both want `AGENTS.md`.** `python install.py repo` writes the working rules to `<dir>/AGENTS.md`. The README says to copy `templates/project/AGENTS.md` into a repo "as `AGENTS.md`". If the install already created the file, the template cannot be copied over it without overwriting, and a later `--update` would replace the filled-in template with the working rules (keeping it as `AGENTS.md.bak`). The files do not say how to combine them. User mode has no such clash.
7. **"Never commit" against commit steps.** All six agents say "Never commit". `session-capture` ends with "Then commit them", and the project template's Delegation section asks which agents "commit or push". Read together: the main session commits and the agents do not. The files never say this plainly.
8. **The README does not say how to pick an agent or call a skill in Copilot.** It does not name the command or menu. The removed test script `kit/tests/live_check.sh` used `copilot --agent <name>`, but that is a deleted file, not documentation.
9. **Terms the agents use without defining them.** The agent files mention a "findings file" with `@hash` rows, `done_when`, "the requester", and "Proposed decision:" lines. These come from a working style the kit does not explain. They only matter if the repo uses them.
10. **The hook's `.env` rule and the rules text.** The deny reason says "use .env.example", which works because `.env.example` is allowed. A file named `.env.local` or `.env.production` is not matched.
11. **The hook has only a `bash` command.** The file has no `powershell` or `command` entry. The files do not say what happens on a Windows machine without bash.
