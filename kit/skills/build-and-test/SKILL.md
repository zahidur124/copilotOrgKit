---
name: build-and-test
description: Find and run the repo's own build, test, lint and format commands - from its AGENTS.md, README and CI config first, then its build files, wrapper and lockfile - and report each command run and its result. Use when about to say a change is done, when asked to build, test, lint or check a repo, or when unsure which command a Node.js, Java, Scala, Python or Flutter repo uses.
---

# build-and-test

The commonest failure in these repos is running the wrong command: global `mvn` instead of `./mvnw`, `npm install` in a pnpm repo, a fresh `sbt` per command, `pytest` outside the venv. A wrong command passes or fails for reasons that have nothing to do with the change. So find what the repo itself runs, run that, and report what ran.

Rules that hold for every step:
- **The repo's own commands win.** A command in AGENTS.md, README, CONTRIBUTING, a Makefile or CI beats one worked out from build files.
- **Use the repo's wrapper and the tool its lockfile names**, never a global tool or another package manager. An install that changes the lockfile means the wrong tool or command: say so, and leave the lockfile out of your change.
- **Never make a failure go away** by skipping, deleting or loosening a test, raising a timeout, or adding `-DskipTests`, `-x test`, `--no-verify`, `.skip`, `@Disabled`, `@Ignore` or `pytest.mark.skip`. Fix the code, or report the failure.
- **Report only what ran.** A command you did not run is not passing.
- **Web search is off.** Work from the output, the repo and the installed packages.
- **Downloads go through the company mirror and may be blocked.** On a 401, 403, 407, timeout, certificate error or "could not resolve", stop and report the command and the error line, with internal hostnames left out. Do not edit `.npmrc`, `.yarnrc.yml`, `settings.xml`, `gradle.properties`, `init.gradle`, `pip.conf` or `uv.toml`, and do not add `--registry`, `--index-url`, `--trusted-host` or `strict-ssl=false`.

1. **Find the commands the repo already uses.** Read `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, any `Makefile`, `justfile` or `Taskfile.yml`, then the CI config: `.github/workflows/*.yml`, `Jenkinsfile`, `.gitlab-ci.yml`, `azure-pipelines.yml`, `bitbucket-pipelines.yml`. CI shows the exact steps, the tool versions (`java-version`, `node-version`, `flutter-version`) and the services tests need. A step that needs something you lack (a secret, a database, Docker) cannot run here: say so.

   ```
   rg -n "run:|sh |mvnw|gradlew|sbt|npm|pnpm|yarn|uv |poetry|pytest|ruff|flutter|dart " .github/workflows Jenkinsfile .gitlab-ci.yml 2>/dev/null | head -40
   ```

2. **Fill the gaps from the build files.** Only for what step 1 did not settle.

   **Node.js / TypeScript** (`package.json`). The lockfile names the tool: `package-lock.json` npm, `pnpm-lock.yaml` pnpm, `yarn.lock` Yarn (with `.yarnrc.yml` it is Yarn 2+), `bun.lock` or `bun.lockb` bun. The `packageManager` field gives the version. Run the scripts by their names in `package.json` (`test`, `lint`, `typecheck`, `build`, `format:check`); `npm run` lists them. In a workspace (`workspaces` in package.json, `pnpm-workspace.yaml`, `turbo.json`, `nx.json`), run them in the changed package: `npm test -w <pkg>`, `pnpm --filter <pkg> test`, `yarn workspace <pkg> test`. If the test script is a bare `vitest`, add `--run` so it does not wait in watch mode.
   ```
   npm ci                              # needs package-lock.json; npm install only when there is none
   pnpm install --frozen-lockfile
   yarn install --frozen-lockfile      # Yarn 1; Yarn 2+: yarn install --immutable
   ```

   **Java** (`pom.xml` Maven; `build.gradle`, `build.gradle.kts` Gradle). Use `./mvnw` or `./gradlew` when present (`mvnw.cmd`, `gradlew.bat` on Windows): they pin the version the repo expects. Run a format or lint check the build has (Spotless, Checkstyle, ktlint) with its check task; apply a formatter only to fix your own files.
   ```
   ./mvnw verify                       # test runs unit tests; verify also runs *IT integration tests
   ./mvnw -pl orders -am test -Dtest=OrderServiceTest -Dsurefire.failIfNoSpecifiedTests=false
   ./gradlew build                     # compile, test and every check task
   ./gradlew :orders:test --tests 'com.example.orders.OrderServiceTest'
   ```

   **Scala** (`build.sbt`; `project/build.properties` gives the sbt version). Each new sbt process starts a JVM and loads the build, often a minute, so never start one per command. Use the client, which reuses one server (sbt 1.4 and later; the default in sbt 2), or batch the commands in one quoted string. `projects` lists the sub-projects; prefix a task with one, as in `core/test`. In sbt 2, `test` reuses cached results; `testFull` runs everything.
   ```
   sbt --client "scalafmtCheckAll; compile; test"   # scalafmtCheckAll only with a .scalafmt.conf
   sbt --client "core/testOnly com.example.OrderSpec"
   sbt --client shutdown                            # stop the server when done
   ```

   **Python.** The lockfile names the tool: `uv.lock` uv, `poetry.lock` Poetry, `requirements*.txt` a venv and pip; with `pyproject.toml` alone, read its `[build-system]` and `[tool.*]` tables. Use `tox` or `nox` when CI does. Reuse an existing `.venv`. Run ruff or mypy only when the repo configures them (`[tool.ruff]`, `ruff.toml`, `[tool.mypy]`, `mypy.ini`, `.pre-commit-config.yaml`), through the same tool.
   ```
   uv sync && uv run pytest
   poetry install && poetry run pytest
   python3 -m venv .venv && .venv/bin/pip install -r requirements.txt -r requirements-dev.txt
   .venv/bin/python -m pytest          # Windows: .venv\Scripts\python -m pytest
   uv run ruff check . && uv run ruff format --check . && uv run mypy src
   ```

   **Flutter / Dart** (`pubspec.yaml`). With `flutter:` under `dependencies` it is Flutter; otherwise use `dart pub get`, `dart analyze`, `dart test`. With `.fvmrc` or `.fvm/`, put `fvm` in front of each `flutter` or `dart` command. With `melos.yaml` or a `workspace:` list in `pubspec.yaml`, run in the changed package or through the repo's melos scripts. When `build_runner` is in `dev_dependencies`, regenerate the `*.g.dart` and `*.freezed.dart` files before analyze and test, or both fail on stale code.
   ```
   flutter pub get
   dart run build_runner build         # build_runner before 2.6 also needs --delete-conflicting-outputs
   flutter analyze
   dart format --output=none --set-exit-if-changed .
   flutter test test/orders/order_service_test.dart
   ```

3. **Run the narrowest check first, then widen.** Find what changed with `git diff --name-only` and `git status --short`, then run the tests for those files only (one file, class or name filter). When they pass, run the module's or package's whole suite, then lint, format check, type check or analyze, then the full build CI runs. Name any wider step you left out and why (too slow, needs Docker or a service).

4. **Read the real failure.** Long output hides the cause, so write it to a log file in a temporary folder outside the repo and search it. The cause is the first error, not the last line: Maven's first `[ERROR]`, Gradle's `What went wrong`, sbt's first `[error]`, pytest's `short test summary info`, the `FAIL` block in Jest or Vitest, Flutter's `EXCEPTION CAUGHT`. Decide whether it comes from your change, from code you did not touch (it may have failed before your change: say so, with the output, and do not fix it unasked), or from the machine (wrong JDK or Node version, Docker not running, blocked download).

5. **Report.** For each command: the exact command, PASS or FAIL with the exit code, the counts (for example `212 passed, 1 failed`), and for a failure its first error lines. Then each check you did not run and why.
