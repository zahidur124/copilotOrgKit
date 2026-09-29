# How to work in this organization's repositories

## Facts
- Back any claim someone will act on with the command you ran and its output.
- Prove an absence with one search plus a second search that must find something. An empty result can mean the search was too narrow.
- Read an existing report or design doc; do not re-derive it.

## Scope
- The task is the outcome the requester wants, not the literal steps they wrote.
- If you cannot state the change in one sentence, ask before editing. Offer 2 to 4 readings of the goal that lead to different work.
- Do only what the outcome needs. Ask before widening or narrowing it.
- Answer a question or a review with a proposal, not a change.

## Code
- Write the least code that meets the task.
- Add no config or options nobody asked for.
- Add no abstraction that is used in only one place.
- Every changed line traces to the task.
- Delete only code that your own change made unused. Report other dead code; do not change it.
- When fixing a bug, first state its cause in one sentence with the command and output that show it. Then write a test that fails on it. Then fix the cause, not the symptom.

## Verify
- Every task ends with a done-when: a command and the output it must print.
- Run it once, report its output, and stop. Re-run only after a further edit.
- Report a failure with its log. Never hide it with a retry.
- After 3 failed attempts at the same fix, name the assumption that is probably wrong and ask one question.

## Git
- Commit in small steps. Each commit message says why, not only what.
- Stage files by path, never `git add -A`.
- Never force-push a shared branch or run `git reset --hard`. An org hook blocks both.
