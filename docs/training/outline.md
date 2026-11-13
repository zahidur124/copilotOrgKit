# Training session outline: the Copilot kit

Audience: company developers who use GitHub Copilot and are new to custom agents and skills.
Length: about 45 minutes, 18 slides, with a live demo.
Source for every fact below: `docs/training/kit-content.md`. Paths and command names are exact.

How to read each slide entry: **On the slide** is the short text that goes on the slide. **Speaker notes** are for the presenter. **Visual** is what the slide should show.

Time plan (minutes): 1, 2, 2, 3, 1, 3, 3, 2, 2, 2, 2, 7, 3, 2, 3, 2, 1, 4. Total 45.

A short glossary the deck should define the first time each word appears:
- **Agent:** a file that sets a name, a list of allowed tools and instructions for one kind of job.
- **Skill:** a file of numbered steps that Copilot follows when your request matches its description.
- **Hook:** a small command that runs before a tool call and can refuse it.
- **Working rules:** a Markdown file Copilot reads at the start of a session.

---

## Slide 1. The Copilot kit: agents, skills and rules (1 min)

**On the slide**
- A set of optional files for GitHub Copilot.
- 45 minutes: what is in it, how to install it, how to use it.
- One live demo.

**Speaker notes**
Say that nothing here is required. You will show what the kit contains, how to install it on your own machine, and one skill working live. By the end, each person should know which parts they want to try.

**Visual**
Title slide. Simple agenda strip with six steps: Why, What, Install, Agents and skills, Rules and guardrails, Start.

---

## Slide 2. Why the kit exists (2 min)

**On the slide**
- Copilot works better with clear instructions and a clear way to check results.
- The kit packages habits: show evidence, stay in scope, prove it is done.
- Optional. Per developer. Nothing is pushed to any repo.

**Speaker notes**
The README says the kit is optional and that each developer chooses whether to install it. It also says nothing is pushed to any repo. Add the company's own reason here in one or two sentences, because the kit files do not state one. Be clear that this is a set of defaults you can read, change or ignore.

**Visual**
Three-part before and after: "Before: each person writes their own prompts and rules" and "After: shared files you can read and edit". Keep it plain, no logos. Presenter fills in the company reason.

---

## Slide 3. What is in the kit (2 min)

**On the slide**
- 6 agents, 3 skills
- Working rules (`templates/AGENTS.md`)
- 2 starter templates: project and research
- 1 safety hook (`deny.json`)
- `install.py` copies it all into place

**Speaker notes**
This is the map for the rest of the session. Agents are for handing off a job. Skills are step-by-step procedures. The working rules set how Copilot behaves in a repo. The hook refuses a short list of risky actions. The two starter templates are not installed. You copy them by hand when you want them.

**Visual**
Table of the kit contents, one row per part, with the folder path in a code font: `agents/*.agent.md`, `skills/*/SKILL.md`, `templates/AGENTS.md`, `templates/project/AGENTS.md`, `templates/research/AGENTS.md`, `templates/.github/hooks/deny.json`, `install.py`.

---

## Slide 4. Install: user mode or repo mode (3 min)

**On the slide**
- `python install.py user` : your Copilot config (`~/.copilot`), every repo you open
- `python install.py repo [dir]` : one repo, your choice whether to commit
- Same files either way; `--agents` and `--skills` install only the ones you name

**Speaker notes**
Run the script from the `kit/` folder of a clone. User mode puts the rules in `~/.copilot/copilot-instructions.md`, agents in `~/.copilot/agents/`, skills in `~/.copilot/skills/`, and the hook in `~/.copilot/hooks/`. Repo mode puts the rules in `.github/instructions/kit.instructions.md`, and the hook, agents and skills under `.github/`; the repo's own `AGENTS.md` is left alone. Nothing is committed for you in either mode. If `COPILOT_HOME` is set, user mode uses it instead of `~/.copilot`.

**Visual**
Two-column table: rows for rules, hook, agents, skills; columns for user and repo mode, with the exact paths. Below it, the two commands in a code block.

---

## Slide 5. Install: what it skips, how to update and remove (1 min)

**On the slide**
- Existing files are skipped and listed, never overwritten by default
- Update: run it again with `--update`; old files are kept as `.bak`
- Remove: delete the files the script listed

**Speaker notes**
The script prints `installed: <path>` or `skipped, already exists: <path>` for each file. That output is your list for removing later. There is no uninstall command. Mention that the starter templates are never installed.

**Visual**
Code snippet of sample output: two `installed:` lines and one `skipped, already exists:` line.

---

## Slide 6. Agents: what they are and the six in the kit (3 min)

**On the slide**
- An agent is a file with a name, a tool list and instructions
- Use one when you want to hand off a job and read only the result
- worker, researcher, reader, verifier, reviewer, builder

**Speaker notes**
Define tools: `read`, `edit`, `execute` (run commands) and `search`. No kit agent has a web tool, because web search is off in the organization. The tool list is the real limit on an agent. The written instructions are only requests. The README shows this: the reader agent's "no advice" rule is an instruction, and in testing it still gave advice when asked directly. Also say that none of the six agents commit or spawn other agents.

**Visual**
Table with one row per agent: name, one-line purpose, tools. Use the quick comparison table from `kit-content.md` section 3. Highlight that `reader` has no `edit` tool.

---

## Slide 7. Which agent should I pick? (3 min)

**On the slide**
- Gather facts, no opinions: reader
- Research with sources: researcher
- Make a known change with a check: builder
- Run the checks independently: verifier
- Review a diff: reviewer
- Anything else: worker

**Speaker notes**
Walk through the table by asking one question: what do you need back? Facts only, a sourced report, a finished change, a pass or fail, or a verdict. If none of those fit, use `worker`. Point out the flow: reader gathers facts, builder makes the change, verifier runs the checks, reviewer checks the diff.

**Visual**
Decision table with three columns: "I need...", "Pick", "Because". Add a small left-to-right flow below it: reader, builder, verifier, reviewer. Rows:
- facts about code, files or logs, no advice | reader | read-only tools, reports facts
- a researched answer from the repo and installed packages | researcher | no `web`, cites a file and line or a command and its output for each claim
- a fixed change with a command that proves it | builder | stops if a field is missing, never edits `*.md`
- PASS or FAIL on my Done when commands | verifier | fixes nothing
- APPROVE or REJECT on a diff | reviewer | assumes the diff is wrong until shown right
- something that fits none of these | worker | catch-all

---

## Slide 8. How to brief an agent (2 min)

**On the slide**
- A brief is the written task. Give it in full.
- Fields: Goal, Done when, Context, Files, Report path
- Done when = a command and the output it must print
- A missing field makes the agent stop and ask

**Speaker notes**
Most agents in the kit stop and name what is missing instead of guessing. Say this is on purpose. Show one good example brief for `builder`. Note that `worker` takes a looser brief: what the work is for, what done looks like, what is ruled out.

**Visual**
Code snippet of a filled-in brief, for example:
```
Use the builder agent.
Goal: change the default page size in config/app.json from 20 to 50.
Done when: `jq .pageSize config/app.json` prints 50.
Context: no other file reads this value.
Files: config/app.json
Report path: docs/builder-pagesize.md
```
Next to it, a screenshot placeholder: "Selecting an agent in your Copilot client" (presenter to capture; the kit does not document how an agent is picked).

---

## Slide 9. Skill: draft-from-examples (2 min)

**On the slide**
- Writes a new document in the same format and voice as finished ones
- Starts when you point at a folder of examples and give a new topic
- Never guesses a fact: leaves `[TODO: ...]`

**Speaker notes**
First define a skill: a folder with one `SKILL.md` file, with a name, a description and numbered steps. The steps here: read the examples, write down the pattern, gather facts, draft in the same folder, report with any `[TODO]` left. The `[TODO]` rule exists because a believable invented fact in a finished-looking draft is hard to catch.

**Visual**
Five-step horizontal flow. Below it an example request: "Draft a new incident report for the March payment outage, in the same format as the ones in `docs/incidents/`."

---

## Slide 10. Skill: spec-interview (2 min)

**On the slide**
- Turns a rough idea into a written spec
- Gets real examples first, works out the steps itself, asks only what it must
- Up to four questions at a time, recommended option first
- Writes `docs/spec.md` by default

**Speaker notes**
This is the skill you will demo next. Explain the order: it reads the repo first so it only asks questions that only you can answer. Then it asks for real examples, then works out the steps backwards from the answer, then asks about choices that are yours. It ends by writing the spec and listing open questions.

**Visual**
Flow diagram of six boxes: Read the repo, Get examples, Work out steps, Ask only what the steps need, Write the spec, Report. Mark the "Ask" box as the only place the user is questioned.

---

## Slide 11. Skill: session-capture (2 min)

**On the slide**
- Run it at the end of a session
- Proposes the lines a new session would need
- Writes nothing until you pick lines

**Speaker notes**
It summarises the session, then lists what a new session would need that is not already in the code, `git log` or `AGENTS.md`. Each candidate comes with the exact line, the file it belongs in, and one sentence on why. It leaves out rules that come from a single failure. After you pick, it writes the lines word for word.

**Visual**
Mock-up of the proposal list: three rows, each with columns "Exact line", "File", "Why". Placeholder content is fine. Add the trigger phrase "That's it for today. What should go in AGENTS.md from this session?"

---

## Slide 12. Live demo: spec-interview (7 min)

**On the slide**
- Rough idea in. Spec out.
- Watch: what it reads, what it asks first, what it leaves to you
- Result: `docs/spec.md`

**Speaker notes**
Use a small sample repo, not a real one, so no company data is shown. Have an `AGENTS.md` and a few source files in it. Follow the demo script below. If the skill does not start, say the trigger phrase more directly: "Interview me about this idea." Keep a finished `docs/spec.md` from a practice run as a fallback.

**Visual**
Live terminal or editor. Add a side panel with the "What to notice" list for the audience.

### Demo script

Before the session: install in user mode or repo mode (`python install.py repo <sample repo>`). Open Copilot in the sample repo. Check once that the skill starts.

1. **Type the rough idea** (keep it loose on purpose):
   > Interview me about this idea: let customers download their order history as a CSV file.
2. **Notice: it reads before it asks.** It looks at `AGENTS.md`, any existing spec and design files, and the code the feature touches. Say out loud: "It is answering what the repo can answer."
3. **Notice: the first question is for real examples,** not "what do you want?". Answer with one real case, in your own words, for example: "Last month a customer asked for every order since January so she could do her tax return. She wanted date, order number, items and total."
4. **Notice: it works out the steps itself.** It shows the steps from the order data to the CSV, with your example walked through them. Correct one step on purpose, for example: "Totals must include delivery."
5. **Notice: the questions are few and specific.** At most four at a time, each tied to a step, each option says what it implies, and the recommended option is first. Pick the recommended one for two, and pick a different one for one.
6. **Notice: defaults are stated, not asked.** For things with a usual default (for example, empty-result behaviour), it says what it chose.
7. **Notice: it stops when the example walks through every step.** It does not ask for the sake of asking.
8. **Open `docs/spec.md`.** Point out the example in your words, the steps, and any item marked as an open question with the step it blocks.

What the audience should take away: the skill does the thinking about steps and asks for decisions only. The spec uses their words. Anything not settled is marked open, not guessed.

---

## Slide 13. Writing rules: `templates/AGENTS.md` (3 min)

**On the slide**
- Working rules Copilot reads at the start of a session
- Six groups: The task, Claims, Changes, Handing work to agents, Git, Instruction files
- Installed as `kit.instructions.md` (repo) or `copilot-instructions.md` (user)

**Speaker notes**
Define working rules: a plain Markdown file of instructions. Go through the groups in one line each. The task: finish what was asked, and name extras as "Also: ..." instead of doing them; take the likeliest reading and act, and ask only when the readings lead to different work. Claims: say done, fixed or passing only about what you ran and saw work, and never make a failure look resolved. There is no web search, so check against the code, the lockfile or the installed package, and say you do not know if it is not there. Changes: new code reads like the code around it, and keep secrets and customer data out of code, logs and commits. Handing work to agents: hand work to `worker` when you only need the result, and put any rule it must follow in the brief. Git: review what is staged, never force-push a shared branch or reset away work that is not yours. Instruction files: change a rule only when the user asks for it.

**Visual**
Table with two columns, "Group" and "One-line rule", six rows, taken from section 5 of `kit-content.md`. Highlight the Claims row's rule that "done" is said only about what was run and seen work, with a short before-and-after example: "Fixed" with no check run, against "I changed X; I did not run the tests".

---

## Slide 14. Starter templates: project and research (2 min)

**On the slide**
- `templates/project/AGENTS.md`: rules for one project
- `templates/research/AGENTS.md`: rules for a research folder
- Not installed. Copy by hand, fill in the `<placeholders>`

**Speaker notes**
The project template covers: how to start, the check commands, where records live, four work sizes (bug, small change, feature, docs-only), how work lands when you ask to commit or push, and a goal file for long tasks. The research template covers where reports go, the task shape using the `researcher` agent, with the `Source:` line listing the files and commands the report used. To adopt one, copy it to `AGENTS.md` in the repo or folder, then replace every `<placeholder>`. A repo-mode install does not use `AGENTS.md`, so the template and the kit's rules sit side by side and Copilot reads both.

**Visual**
Two side-by-side code excerpts, each about six lines, with the placeholders highlighted: from the project template, "The repo's check command: `<check command>`", and from the research template, "Reports: `research/<camelCase+DDMMYY>/report.md`".

---

## Slide 15. Guardrails: the deny hook (3 min)

**On the slide**
- Runs before every tool call and can refuse it
- Denies: `git push --force` and `-f`, `git reset --hard`
- Denies: `rm -rf` on `/`, `~`, `$HOME`, `.`, `..`, `*`
- Denies: `.env` files, and `.pem`, `.key`, `id_rsa`, `id_ed25519`, `id_ecdsa`

**Speaker notes**
Define a hook: a small command Copilot runs at a set moment. This one is `templates/.github/hooks/deny.json`, a `preToolUse` hook with the command written inside the file. When it denies, the developer sees a reason, for example "force-push rewrites shared history; use --force-with-lease on your own branch". It allows `--force-with-lease`, `git reset --soft`, and `.env.example`. It also blocks editing `.env` files, not only reading them.

**Presenter note (read before the demo):** the hook's automated tests were removed from the repo today (2026-11-12): `kit/tests/test_deny_hook.py`, `kit/tests/live_check.sh` and `kit/.github/workflows/live-check.yml`. Nothing in the repo now proves the hook works. Try the hook by hand on the work machine before you demo it. Install it, then ask Copilot to run each of these and see that it is refused: `git push --force`, `git push origin main -f`, `git reset --hard`, `rm -rf ~`, `cat .env`, and reading a `.pem` file. Also check that these are allowed: `git push --force-with-lease`, `git reset --soft HEAD~1` and `cat .env.example`. Pay extra attention to the cases where the pattern needs a quote, space or the end of the text right after the match (`-f`, `rm -rf` targets, `.env`, `.pem`). The patterns assume a certain shape for the tool-call text that Copilot sends, and the removed tests only checked one shape. If a case you expect to be refused goes through, tell the kit owner and do not demo that case.

**Visual**
Table with three columns: "Blocked", "Allowed instead", "Reason shown". Add a screenshot placeholder: "Copilot showing a blocked tool call with the deny reason" (capture on the work machine after the manual test).

---

## Slide 16. The hook's honest limits (2 min)

**On the slide**
- It matches text. It stops mistakes, not a determined person.
- A timeout (5 s) lets the call through. A crash denies it.
- It also blocks editing `.env` files
- The `reader` agent's "no advice" rule is only an instruction

**Speaker notes**
Be direct. The hook is a safety net for accidents. For example, it does not match `rm -r -f /` written with split flags, or `rm -rf /etc`, and it does not match `.env.local`. Blocking `.pem` and `.key` also blocks public certificates with those names. The rule that holds is the tool list, not the written instruction. This is why the `reader` agent has no `edit` tool.

**Visual**
Two-column "Catches / Does not catch" table. Catches: `git push --force`, `rm -rf ~`, `cat .env`. Does not catch: `rm -r -f /`, `rm -rf /etc`, `cat .env.local`, a script that deletes the same files.

---

## Slide 17. Getting started checklist (1 min)

**On the slide**
- Clone the repo; run `python install.py user` or `python install.py repo`
- Try the hook by hand with one blocked and one allowed command
- Run one agent with a full brief; run one skill
- Copy a starter template into one repo and fill in the placeholders
- Tell the kit owner what was unclear

**Speaker notes**
Suggest the order: install in user mode, try the hook, try the `reader` agent on a question about your own repo, then try `spec-interview` or `draft-from-examples` on real work. Remind them the install never overwrites, so it is safe to try.

**Visual**
A checklist with checkboxes and the exact commands in a code font. A QR or link placeholder to the kit's repo.

---

## Slide 18. Questions (4 min)

**On the slide**
- Questions
- Where to find it: the kit repo, `kit/README.md`
- Who to tell about problems: <owner name or channel>

**Speaker notes**
Likely questions: how do I pick an agent in my client (check before the session; the kit does not document it), can I change the files (yes, they are plain text copied to your machine), does it send anything to my repos (no, nothing is pushed). Have the "unclear points" in section 9 of `kit-content.md` to hand.

**Visual**
Contact placeholder and the repo path. Keep the slide plain.
