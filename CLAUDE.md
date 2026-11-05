# copilotOrgKit

How work is done here: the general rules in `~/Desktop/Projects/CLAUDE.md`, and the steps below.
State lives in `features.json`, `git log` and `records/`. At the start of every session read `features.json` and `git log --oneline -5`; the next row is the first that is neither done nor parked.

## Pick the size first
- One-sentence change (you can say the diff in one sentence): branch, change, `./run check`, push,
  `ci-wait`, merge to main, push. No spec, no new feature row.
- Anything bigger: the stages below, in order. A stage is done when its output exists.

## 1. Plan (owner and agent, one sitting)
- Interview the owner with AskUserQuestion: goal, who uses it, what is out of scope, how they will judge it.
- Write `docs/spec.md` in their words. Write product-level rows in `features.json`, all `todo`.
- Each row has `kind`: `code` (a test decides), `result` (a number the owner judges: a strategy, a model),
  or `live` (behaviour over time; add `observe: {cmd, need, hours}`).
- F1 is always the walking skeleton: the thinnest path through every part, deployed, with a health check.
- Output: the owner says yes to `docs/spec.md` and `features.json`. Commit both.

## 2. Design (agent drafts, owner decides interfaces)
- Fill `docs/design.md`: boring stack, parts, public interfaces and what each data field means,
  invariants, deploy target, health path.
- Each invariant becomes a test under `tests/`. Paths where a mistake is costly go in `features.json` `risky`.
- Fill every command in `./run` and every value in `deploy.env`.
- Output: the owner says yes to the interfaces section. Commit.

## 3. Build, one feature at a time
1. Read `features.json` and `git log --oneline -5`, then `./run smoke` once F1 is done. Fix a red smoke before anything else.
2. Branch `f<N>-<slug>`.
3. Tests first, in a fresh context: dispatch a subagent with only the row's `accept` text and
   `docs/design.md`. It writes tests under `tests/`.
4. Write the code, building until `./run test <the row's test files>` passes.
5. Push, then `ci-wait`. It waits for the CI run of that exact commit.
6. Edit `features.json` to set the row's status to done, then commit `done: F<N> <title>`.
   A `live` row has its observations first; a `result` row is given `--owner`.
7. Push, merge to main with `--ff-only`, push main, delete the branch.
- A `result` row: build the pipeline that produces the number, record each run's numbers in `records/`,
  show them to the owner. Do not tune toward a target number.
- A `live` row: run its `observe.cmd` on the schedule in its row, until the row is marked done.
- If the same fix is corrected twice, stop and start a fresh session.

## 4. Release
- `./run deploy` is the release step and rolls back on a failed health check; a session does not run it.
- The owner tries the released product. A problem they find becomes a new `todo` row with a failing test.
