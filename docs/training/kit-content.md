# Copilot kit: content reference

This file lists what is in the Copilot kit, taken from the files in `kit/`. It is the source for the training deck. It adds no features that the files do not have. Where the files leave something open, this file says so.

Last checked against the repo on 2026-11-12 (commit `c95c3f2` and later).

## Terms used in this file

- **Agent (custom agent):** a Markdown file ending in `.agent.md`. It has a name, a one-line description, a list of tools, and written instructions. You pick it for a job, and it works with only the tools listed.
- **Tool:** something an agent is allowed to do. The tool names used here are `read` (read files), `edit` (change or create files), `execute` (run shell commands), `search` (search files) and `web` (search and fetch web pages).
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
| `agents/*.agent.md` | 6 custom agents: worker, researcher, reader, verifier, reviewer, builder. |
| `skills/*/SKILL.md` | 3 skills: draft-from-examples, spec-interview, session-capture. |
| `templates/AGENTS.md` | Working rules: facts, scope, code, verify, delegation, rules files, git. |
| `templates/project/AGENTS.md` | Starter rules for one project. Not installed. |
| `templates/research/AGENTS.md` | Starter rules for a research folder. Not installed. |
| `templates/.github/hooks/deny.json` | A safety hook that refuses a short list of risky actions. |
| `install.sh` | Copies the installable files to where Copilot reads them. |

Why it exists, as far as the files say: the working rules ask for evidence behind claims, for a stated scope, for a check that proves a task is done, and for no force-push or `git reset --hard`. The agents and skills put those habits into reusable form. The README does not give a company-level reason beyond that. The presenter should add the company's own reason.

What changed on 2026-11-12 (commit `c95c3f2`, "Port worker, researcher, skills and starter templates into the kit; drop project scaffolding and tests"):

- Added: the `worker` and `researcher` agents, the three skills, and the two starter templates.
- Changed: the `reader`, `reviewer`, `verifier` and `builder` agents, `templates/AGENTS.md`, `README.md`, and `install.sh` (it now installs the skills too).
- Removed: the project scaffolding around the kit, and the kit's own automated tests: `kit/tests/test_deny_hook.py`, `kit/tests/live_check.sh` and `kit/.github/workflows/live-check.yml`. The hook now has no automated tests in the repo.

## 2. Install

Run `install.sh` from the `kit/` folder of a clone of this repo. It needs `bash`. The usage line is `usage: ./install.sh user | repo [dir]`. Any other argument prints that line and exits with code 2.

### Two modes

| | `./install.sh user` | `./install.sh repo [dir]` |
|---|---|---|
| Applies to | Every repo you open | One repo only |
| Target folder | `~/.copilot`, or `$COPILOT_HOME` if set | `dir`, default is the current directory |
| Working rules | `~/.copilot/copilot-instructions.md` | `<dir>/AGENTS.md` |
| Hook | `~/.copilot/hooks/deny.json` | `<dir>/.github/hooks/deny.json` |
| Agents | `~/.copilot/agents/<name>.agent.md` | `<dir>/.github/agents/<name>.agent.md` |
| Skills | `~/.copilot/skills/<name>/SKILL.md` | `<dir>/.github/skills/<name>/SKILL.md` |
| Committed? | Nothing is committed anywhere | You decide whether to commit the new files |

The README does not list the user-mode hook path. It comes from `install.sh` (`hooks=$dest/hooks`).

Both modes copy the same set: the working rules, the hook, all 6 agents and all 3 skills. The two starter templates are never installed. Copy one by hand when you want it.

### Existing files are skipped, not overwritten

For each file the script prints one line:

- `installed: <path>` when it copied the file.
- `skipped, already exists: <path>` when the file was already there. It is left alone.

So running the script twice is safe. It also means that an existing `AGENTS.md` or `copilot-instructions.md` of yours is never replaced.

### Update and remove

- **Update:** delete the old file, then run the install again. Without the delete, the script skips it.
- **Remove:** "delete the installed files it listed." That means the paths on the `installed:` lines. There is no uninstall command.

## 3. The six agents

Every agent file starts with a header giving `name`, `description` and `tools`. Five of the six expect a brief with named fields. `worker` takes a free-form brief. All six say "Never commit" and none can spawn another agent.

Two things hold for all of them. First, an instruction in the agent's text is a request, not a lock. The README says this about `reader`: its "no advice" rule "is only an instruction. Asked directly, it still gave advice in testing." Second, the tool list is what actually limits the agent. Even so, several agents are told not to edit files but still have the `edit` tool (see "Where the files are unclear" at the end).

The example requests below are written for this reference. They are not in the kit files.

### worker

- **Purpose:** catch-all delegate. Description in the file: "Catch-all delegate: read, edit, write, run, research."
- **When to use:** when only the result of the work is needed afterwards. `templates/AGENTS.md` lists the cases: reading across several files, pages or logs; a batch of small sub-tasks; or a change a brief can state in full that is more than a small edit.
- **Tools:** `read`, `edit`, `execute`, `search`, `web`.
- **How it works:** does what the brief asks and nothing beyond it. Reads only the files the brief names when the brief names them. For a question, it searches wherever it needs to. If a fact is missing, it stops and names it. If a fact the brief relies on is false, it says so in the first line of its reply. Its final message is the report: what it produced, the evidence for each claim, and the output of any check. It writes a file only if the brief names a path.
- **Limits:** never commits; never spawns another agent; never runs a job in the background or with `&`. Before `rm -r`, `git reset --hard`, `git branch -D`, `DROP`, `DELETE`, `TRUNCATE`, a service restart, or overwriting a file it did not create, it stops and names the command.
- **Example request:** "Use the worker agent. Goal: find every place in `src/` that reads the `TIMEOUT_MS` setting, so I can decide whether to rename it. Done when: you list each file and line with the exact text. Do not edit anything."

### researcher

- **Purpose:** research with a written report, for a build or a new project.
- **When to use:** when a decision depends on facts from official documentation or the web, such as a library version or an API shape.
- **Tools:** `read`, `edit`, `execute`, `search`, `web`.
- **How it works:** confirms every library, API or version fact by fetching official docs, and cites the URL and line numbers. It never states a version from memory. Before comparing options, it opens the subject's own primary source (README, model card, release notes) and lists every option found, even those the brief left out. If a claim names a package, CLI or version, it runs it where it can (a resolver, a dry-run install, `--help`). The report is a table with columns `claim | what was run | output | source`, with a summary at the top. It starts the report file first and adds each finding as it goes, so a partial run still leaves a usable report.
- **Report path:** the brief's `Report path:`. If none is given, `docs/research/researcher-<task-slug>.md` in the current project.
- **Limits:** the same list as `worker` (never commits, no background jobs, stops before risky commands). A denied tool call, an unreadable path or a missing prerequisite goes first in the report, and it stops.
- **Example request:** "Use the researcher agent. Goal: compare two ways to add retry logic to our HTTP client. Done when: the report has a table of claims, each with a source URL. Context: we use Node 20. Report path: `docs/research/retry-options.md`."

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

### reviewer

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
- **Example request:** "Use the reviewer agent. Goal: review my branch against the task 'add a timeout to fetchUser'. Done when: a verdict of APPROVE or REJECT with reasons. Context: none. Files: the diff of `main..HEAD`. Checks: scope, claims, silent-fail. Report path: `docs/review-fetchuser.md`."

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
| worker | read, edit, execute, search, web | Only if the brief names a path | Final message |
| researcher | read, edit, execute, search, web | Report file | Report path, plus summary in final message |
| reader | read, search, execute | No | Final message |
| verifier | read, edit, execute, search | Report only | Report path, or final message if none |
| reviewer | read, edit, execute, search | Report only | Report path, plus verdict in final message |
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

Title: "How to work in this organization's repositories". It has seven groups. Installed as `AGENTS.md` (repo mode) or `~/.copilot/copilot-instructions.md` (user mode).

| Group | What it says, in short |
|---|---|
| **Facts** | Back any claim someone will act on with the command you ran and its output. To prove something is absent, run one search, then a second search that must find something, because an empty result can mean the search was too narrow. Read an existing report or design doc; do not re-derive it. |
| **Scope** | A task is the result the user asked for, finished: every step the project's `AGENTS.md` says that kind of work includes, and anything the result does not work without. Extras the result works without (an extra check, an example, a nicer build) are named at the end as `Also: <step> — <why>`, not done, because the user decides scope. If you cannot state the change in one sentence, ask before editing, and offer 2 to 4 readings of the goal. Do only what the outcome needs. Answer a question or a review with a proposal, not a change. |
| **Code** | Write the least code that meets the task. Add no config or options nobody asked for. Add no abstraction used in only one place. Every changed line traces to the task. Delete only code your own change made unused; report other dead code. To fix a bug: state its cause in one sentence with the command and output that show it, write a test that fails on it, then fix the cause, not the symptom. |
| **Verify** | Every task ends with a done-when: a command and the output it must print. Run it once, report its output, and stop. Re-run only after a further edit. Report a failure with its log, never hide it with a retry. After 3 failed attempts at the same fix, name the assumption that is probably wrong and ask one question. |
| **Delegation** | Hand work to the `worker` agent when only its result is needed afterwards: reading across several files, pages or logs; a batch of small sub-tasks; or a change a brief can state in full and that is more than a small edit. Decide before the first tool call. Keep in the main session: a file about to be edited, an answer whose place is already known, one search or command with a short result. The brief says what the work is for, what done looks like, what is ruled out, and the files, sources or command. Undoable actions are delegated like any other work. A long job writes results and prints progress per batch; check it once and keep working, never sleep-poll. |
| **Rules files** | Any file that loads into a session gets a new or changed rule only when the user asks for that rule, because rules written from single failures piled up and misfired. Fix a rule or style at the input that causes the behaviour, never by adding caps, counts or forbidden-phrase lists. |
| **Git** | Commit in small steps; each message says why, not only what. Stage files by path, never `git add -A`. Never force-push a shared branch or run `git reset --hard`. "An org hook blocks both." |

The last line of the Git group depends on the hook being installed. If a developer installs the rules but not the hook, the hook is not there to block anything. The install script installs both together.

## 6. The two starter templates

Neither is installed by `install.sh`. Both contain `<placeholders>` in angle brackets for you to fill in.

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

- **For:** a folder of web and docs research, prior art and vendor comparisons, including feasibility work with no project folder. First line: `Kind: research`.
- **Adopt:** copy it into the folder as `AGENTS.md`, then replace each `<placeholder>` (the `<research folder>` and `<topic>` names).
- **Contents:**
  - **Record paths:** reports go in `research/<camelCase+DDMMYY>/report.md`. The `Ask:` line holds the user's words verbatim. The `Source:` line lists every URL the report used.
  - **Task shape:** (1) run `grep -ril '<topic>' <research folder>` and reuse only a hit whose `Ask:` line equals the user's words verbatim; (2) dispatch `researcher` with the user's words verbatim and the report path; (3) reply with the conclusion and never list the sources.
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
2. **Agents told not to edit have the `edit` tool.** `verifier` ("You fix nothing and edit no file except your report") and `reviewer` ("You never edit the files under review") both list `edit`. They need it to write their report. The limit is an instruction. `builder` is told "Never edit `*.md`" and also has `edit`.
3. **The rules name `worker` only.** `templates/AGENTS.md` (Delegation) names the `worker` agent. `templates/project/AGENTS.md` (Delegation) refers to "the global `worker` and `researcher` lines in the user-level working rules". The user-level rules have no `researcher` line.
4. **Where the researcher writes its report.** The agent's description says the Report path is "a file under the project's docs/", and its text defaults to `docs/research/researcher-<task-slug>.md`. The research template puts reports in `research/<camelCase+DDMMYY>/report.md`, which is not under `docs/`. The template's path is given in the brief, so the two can work together, but the files do not say so.
5. **`researcher` says it stops if a field is missing, yet allows no Report path.** The description says it "stops without searching if a field is missing" and also allows "no Report path". The body supplies a default path, so a missing Report path does not stop it.
6. **Repo-mode install and the project template both want `AGENTS.md`.** `./install.sh repo` writes the working rules to `<dir>/AGENTS.md`. The README says to copy `templates/project/AGENTS.md` into a repo "as `AGENTS.md`". If the install already created the file, the template cannot be copied over it without overwriting. The files do not say how to combine them. User mode has no such clash.
7. **"Never commit" against commit steps.** All six agents say "Never commit". `session-capture` ends with "Then commit them", and the project template's Delegation section asks which agents "commit or push". Read together: the main session commits and the agents do not. The files never say this plainly.
8. **The README does not say how to pick an agent or call a skill in Copilot.** It does not name the command or menu. The removed test script `kit/tests/live_check.sh` used `copilot --agent <name>`, but that is a deleted file, not documentation.
9. **Terms the agents use without defining them.** The agent files mention a "findings file" with `@hash` rows, `done_when`, "the requester", and "Proposed decision:" lines. These come from a working style the kit does not explain. They only matter if the repo uses them.
10. **The hook's `.env` rule and the rules text.** The deny reason says "use .env.example", which works because `.env.example` is allowed. A file named `.env.local` or `.env.production` is not matched.
11. **The hook has only a `bash` command.** The file has no `powershell` or `command` entry. The files do not say what happens on a Windows machine without bash.
