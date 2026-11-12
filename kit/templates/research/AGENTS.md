# Research folder

## What this folder is for
Web and docs research, prior art and vendor comparisons. It covers `<research folder>` and feasibility work with no project folder.

## Record paths
- Reports: `research/<camelCase+DDMMYY>/report.md`.
- The `Ask:` line holds the user's words verbatim; the `Source:` line lists every URL the report used.

## Task shape
1. Run `grep -ril '<topic>' <research folder>`. Reuse only a hit whose `Ask:` line equals the user's words verbatim.
2. Hand the task to the `researcher` agent with the user's words verbatim and the report path.
3. Reply with the conclusion. Never list the sources.

## Git
Commit the report on main and push. No worktree.
