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

## Agents in this repo
<One line per agent installed in this repo and the job it gets; install-repo.py writes these lines.>

## Landing work
- When the user asks to commit or push: <for example "a branch and a pull request for review", or "a commit on main">. Never rewrite pushed history.
