# <project name>

<What it is, who uses it, where it runs, and what the user sees when it works. Cite the `docs/spec.md` lines that say so; leave the citation out until they exist.>

## Start
- Read the repo's task list, if it has one, and `git log --oneline -5`. The next row is the first that is neither done nor parked.
- Scope: all work stays inside <project name>/; nothing outside it is edited.

## Commands
- The repo's check command: `<check command>`. After each change: the quick check and the tests the change touches.
- End-to-end gate: `<end-to-end command>` (<what it walks>).
- <Host steps, e.g. "a migration is applied to <host> before the push".>

## Records
- State: the repo's task list, if it has one, and `git log`. Product `docs/spec.md`, design `docs/design.md`, and a decisions file, if the repo has one.
- Known facts: the repo's findings file, if it has one, not loaded at launch. Before changing code, a config or a deployment, grep it for the file, service or vendor name and read the matching rows.

## Work sizes
Every ask is one of these; the size picks the steps.
- Bug: branch `fix-<slug>`; a test that fails on it first, the cause in one sentence, the smallest fix, then that test and the quick check.
- Small change (the diff fits in one sentence): branch; edit, update the tests it touches, run them and the quick check.
- Feature: one `F<N>` line in `docs/spec.md` in the user's words and, if the repo has a task list, one row in it; branch `f<N>-<slug>`; tests under `tests/`, then the code.
- Docs-only (`*.md`, not `docs/spec.md`): commit on main, push.

At session end, merge each finished branch (its tests and the quick check pass) to main with `--ff-only`, push to <remote>, delete the branch; never rewrite pushed history. Work done in a worktree lands with `git fetch`, `git rebase <remote>/main`, `git push <remote> HEAD:main`, then, back in the main folder, `git pull --ff-only`, `git worktree remove <worktree path>` and `git branch -d <worktree branch>`. <Worktree: yes or no.> <Release: CI / install line / none.>

A Feature, or any task that runs past one sitting, opens by writing `docs/goal.md`: the goal in the user's words, the check that shows it is done, what is out of scope, and one progress line per finished step. Read it again after a compaction or a resume, because an instruction given only in chat can drop out of the compaction summary.

## Delegation
<Which agent does each kind of work, what the session does itself, and which agents commit or push. State whether this replaces the global `worker` and `researcher` lines in the user-level working rules.>

## Rules
<Rules fixing failures the user named.>
