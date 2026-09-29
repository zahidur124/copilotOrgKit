# copilotOrgKit

How work is done here: `~/Desktop/Projects/claude/workflow/WORKFLOW.md` (the why behind each step).
State lives in `features.json`, `git log` and `records/`. Run `wf status` at the start of every session.

## Pick the size first
- One-sentence change (you can say the diff in one sentence): branch, change, `./run check`, push,
  `wf ci`, merge to main, push, `wf release`. No spec, no new feature row.
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
1. `wf status`, then `./run smoke` once F1 is done. Fix a red smoke before anything else.
2. Branch `f<N>-<slug>`.
3. Tests first, in a fresh context: dispatch a subagent with only the row's `accept` text and
   `docs/design.md`. It writes tests under `tests/`. Then run `wf red F<N> <test files>`: it refuses tests
   that already pass, then locks them in `tests.lock`.
4. Write the code. Never edit a locked test; CI fails the push if you do.
5. Push, then `wf ci`. It waits for the CI run of that exact commit.
6. If the diff touches a `risky` path, run `wf review F<N>` (a fresh `claude -p` reviewer).
7. `wf done F<N>`. It refuses unless the tests were locked, CI is green on HEAD, the review passed where
   needed, a `live` row has its observations, and a `result` row carries `--owner '<owner's words>'`.
8. Push, merge to main with `--ff-only`, push main, delete the branch.
- A `result` row: build the pipeline that produces the number, record each run's numbers in `records/`,
  show them to the owner. Do not tune toward a target number.
- A `live` row: `wf observe F<N>` on the schedule in its row, until `wf done` accepts it.
- If the same fix is corrected twice, stop and start a fresh session.

## 4. Release
- `wf release` on main: CI green on HEAD, then `./run deploy`. A failed health check rolls back and the
  command fails. Every release is written to `records/releases.jsonl`.
- The owner tries the released product. A problem they find becomes a new `todo` row with a failing test.

## Records
- `wf metrics` writes one row per session to `records/sessions.jsonl`: time, owner wait, CI results.
  Run it at the end of a session and commit `records/`.
