# <project name>

<What it is, who uses it, where it runs, and what the user sees when it works. Cite the `docs/spec.md` lines that say so; leave the citation out until they exist.>

## Start
- The user's request is the task. Read the repo's task list only when the user asks what is next or says to carry on; the next task is then its first row that is neither done nor parked.
- Scope: all work stays inside <project name>/; nothing outside it is edited.

## Commands
- The repo's check command: `<check command>`. After each change: the quick check and the tests the change touches.
- End-to-end gate: `<end-to-end command>` (<what it walks>).
- <Host steps, e.g. "a migration is applied to <host> before the push".>

## Records
- State: the repo's task list, if it has one, and `git log`. Product `docs/spec.md`, design `docs/design.md`.
- Deliberate choices: when the user keeps a choice that would look like a mistake to someone reading the code, add a short comment beside it saying why, e.g. `# Pinned to 2.x: 3.x drops SSO support`, because the next session reads that code before it changes it.
- Known facts: the repo's findings file, if it has one, not loaded at launch. Before changing a config, a deployment or code that talks to an outside service, grep it for the file, service or vendor name and read the matching rows.

## Work sizes
An ask gets the steps of its size and nothing more.
- Small change or bug fix (the diff fits in one sentence): make the edit, then run the tests it touches and the quick check. A bug in code that has tests also gets a test that fails on it before the fix.
- Feature: the code and its tests under `tests/`. Where the repo keeps `docs/spec.md`, add one `F<N>` line there in the user's words.
- Docs-only (`*.md`, not `docs/spec.md`): edit; there are no tests to run.

## Landing work
- When the user asks to commit or push, do it the way this team's work lands: <for example "a branch and a pull request for review", or "a commit on main">. Never rewrite pushed history.
- <Release: CI / install line / none.>

## Long tasks
A task that runs past one sitting opens by writing `docs/goal.md`: the goal in the user's words, the check that shows it is done, what is out of scope, and one progress line per finished step. Read it again after a compaction or a resume, because an instruction given only in chat can drop out of the compaction summary.

## Delegation
<Which agent does each kind of work and what the session does itself. State whether this replaces the Delegation lines in the user-level working rules (`~/.copilot/copilot-instructions.md`).>

## Rules
<Rules fixing failures the user named.>
