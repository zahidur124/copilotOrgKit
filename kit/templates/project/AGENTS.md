# <project name>

<What the project is and does, who uses it and where it runs, in two or three sentences.>

## Start
- If this branch has a state file (`.copilot/state/<branch>.md`, see Session state), read it before starting, because it says where the last session on this branch stopped and what comes next.

## Layout
- <Language, framework and build tool, for example "Java 21, Spring Boot, Gradle".>
- <Each main folder and what it holds, one line each.>
- Build: `<build command>`. Tests: `<test command>`.

## Out of scope
- <What a session leaves alone in this repo, for example generated code (regenerate it instead), vendored code, another team's module, or migrations that are already applied.>

## Rules
- <How this code base does things a newcomer would get wrong, such as error handling, logging or where tests go.>
- <Traps that cost time, such as a slow step, a flaky test, or a setting that must stay as it is, and why.>

## Session state
`.copilot/state/<branch>.md`, one file per branch, named from `git branch --show-current` with each `/` replaced by `-`. It stays out of git, so developers sharing the repo never overwrite each other's file and a session on one branch never reads another branch's next step. Before writing the first file, add `.copilot/state/` to the repo's `.gitignore` if it is not there. At the end of a task, or when the user wraps up, rewrite the file with where the work on this branch stands and the next step. Rewrite it rather than adding to it, and delete it once the branch is merged, because a session acts on whatever the file says.

## Long tasks
A task that runs past one sitting opens by writing `docs/goal.md`: the goal in the user's words, the check that shows it is done, what is out of scope, and one progress line per finished step. Read it again after a compaction or a resume, because an instruction given only in chat can drop out of the compaction summary.

## Delegation
- Hand work to an agent when only its result is needed back. Keep in this session a file you are about to edit and a lookup one search settles, because everything read here fills this session's context.
- Pick the agent by the job:
  - a fully specified change that a command can show worked → `builder`
  - facts about this repository's own code, logs or command output, with no advice → `reader`
  - a library, package, API or tool fact checked against what is installed → `kit-researcher`
  - checking that a finished change works → `verifier`
  - reviewing a diff or pull request before it is merged → `kit-reviewer`
  - questions about CSV or other tabular data files → `data-analyst`
  - reviewing a Word, PDF or PowerPoint document against a checklist or policy → `document-reviewer`
  - anything else where only the result is needed, such as an investigation across many files, a batch of small sub-tasks, a change in several steps or a draft → `worker`
  - If the agent for a job is not installed, use `worker`.
- The agent cannot see this conversation. Its task note gives the goal, the context it needs (files, constraints, what is already ruled out), what it may do, and what to send back. These rules may not reach the agent, so the note carries any rule the work depends on.
- A long job (migration, backfill, bulk update) writes its results and prints progress as it goes. Check on it and keep working; do not wait on it in a loop.

## Landing work
- When the user asks to commit or push: <for example "a branch and a pull request for review", or "a commit on main">. Never rewrite pushed history.
