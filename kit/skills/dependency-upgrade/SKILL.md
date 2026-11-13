---
name: dependency-upgrade
description: Upgrade libraries one at a time across npm, pnpm, yarn, Maven, Gradle, sbt, pip, poetry, uv and pub (Flutter and Dart), reading each one's changelog from the local package cache, running the build and tests after every step, and reporting what moved from which version to which. Use when the user asks to upgrade, update or bump dependencies, fix a vulnerable dependency, or see what is outdated.
---

# dependency-upgrade

An upgrade that changes many packages at once fails in ways no one can trace back to a cause. Taking one step at a time, with the build and tests run after each, shows which upgrade broke what. Web search is off in the organization, so what changed in a version is read from the files that come with the package.

Rules that hold for every step:
- **One dependency, or one tightly coupled group, per step.** A group moves together by design: the Spring Boot parent or BOM with its starters, `@nestjs/*`, the Jackson modules, `freezed` with `freezed_annotation` and `build_runner`.
- **No major version and no runtime change unless the user asked for it.** The runtime is the JDK, Node, Python, or the Flutter or Dart SDK. List major updates and ask. That includes commands that bump majors on their own: `npm audit fix --force`, `flutter pub upgrade --major-versions`, `ncu -u`.
- **Build and test after each step**, with the commands the build-and-test skill finds. A step that fails is fixed or reverted before the next one starts.
- **Keep the lockfile changes** (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `poetry.lock`, `uv.lock`, `pubspec.lock`, `gradle.lockfile`). Never delete a lockfile to regenerate it.
- **Registry access may go through an internal mirror.** If a download is blocked or refused, stop and report the command and its error. Never change `.npmrc`, `settings.xml`, `pip.conf`, `PUB_HOSTED_URL`, or a build file's repositories.
- Never silence a peer or version conflict with `--force` or `--legacy-peer-deps`. Report the conflict.
- What changed in a version comes from files you read. If none ship with the package, say the notes were not found. Do not guess.

1. **Find the package managers and the runtime pins.** Lockfiles and build files show the managers. The runtime pins are `.nvmrc` or `engines`, `maven.compiler.release` or a Gradle toolchain, `scalaVersion`, `requires-python`, and the `environment:` block in `pubspec.yaml`. These stay as they are.

2. **List what is outdated.**

   ```
   npm outdated                    # pnpm outdated; yarn outdated (Yarn 1)
   mvn versions:display-dependency-updates versions:display-property-updates
   ./gradlew dependencyUpdates     # only with the com.github.ben-manes.versions plugin
   sbt dependencyUpdates           # only with the sbt-updates plugin
   pip list --outdated             # uv tree --outdated; poetry show --outdated
   flutter pub outdated            # dart pub outdated for a pure Dart package
   ```

   Gradle has no built-in report, and sbt has none without sbt-updates. Without the plugin, say so and work from the versions the user names. Do not add the plugin.

3. **Pick the steps.** Patch and minor updates first, one per step. List major updates apart, each with its current and latest version, for the user to decide. For a security fix, start from the audit:

   ```
   npm audit                       # pnpm audit; yarn audit (Yarn 1); yarn npm audit --recursive (Yarn 2+)
   mvn dependency-check:check      # OWASP; Gradle: ./gradlew dependencyCheckAnalyze; only if the build configures it
   pip-audit                       # only if installed
   ```

   When the vulnerable package is transitive, upgrade the direct dependency that brings it in. An override or forced pin (npm `overrides`, Maven `dependencyManagement`, Gradle `constraints`, pub `dependency_overrides`) is the user's choice; offer it, do not add it.

4. **Read what changed** between the two versions, after the new version is downloaded:
   - npm: `node_modules/<pkg>/CHANGELOG.md` (or `HISTORY.md`, `RELEASES.md`), and its `.d.ts` files for the APIs the code calls.
   - pub: `CHANGELOG.md` in `~/.pub-cache/hosted/<host>/<pkg>-<version>/` (`%LOCALAPPDATA%\Pub\Cache` on Windows; `$PUB_CACHE` if set).
   - Maven, Gradle, sbt: jars rarely carry notes. Fetch sources with `mvn dependency:sources -DincludeArtifactIds=<artifact>`, or find them in `~/.m2/repository`, `~/.gradle/caches/modules-2/files-2.1` or the Coursier cache, and read `@Deprecated` and the signatures the code calls.
   - Python: `<pkg>-<version>.dist-info/METADATA` in site-packages, which often carries the changelog.
   - The deprecation warnings the build prints after the upgrade.

5. **Upgrade and fix.** Change only that step's versions:

   ```
   npm install <pkg>@<version>     # pnpm add; yarn add (Yarn 1); yarn up (Yarn 2+)
   uv lock --upgrade-package <pkg> # poetry update <pkg>; pip: change the pin in requirements
   flutter pub upgrade <pkg>       # within the pubspec.yaml constraint
   ```

   Maven, Gradle and sbt: change the version, or its property, in `pom.xml`, `gradle/libs.versions.toml` or the build file, `build.sbt` or `project/*.scala`. For Spring Boot, change the parent or BOM version, not the single libraries it manages. Run `./gradlew dependencies --write-locks` if the repo locks Gradle dependencies. Then run the build and tests, and fix the code the new version breaks. If the fix grows past a few files, stop and ask.

6. **Java and Spring Boot major upgrades** (JDK 8 to 21, Spring Boot 2 to 3, `javax` to `jakarta`) are better done with Microsoft's GitHub Copilot modernization plugin for Copilot CLI (https://github.com/microsoft/github-copilot-modernization). Tell the user. It needs the organization to allow the plugin. Once installed, it is started with:

   ```
   copilot --agent=github-copilot-modernization:modernize
   ```

7. **Report.** For each step: the package, from and to version, the code changed because of it (file and why), and the build and test result. Then what was left and why: majors awaiting a decision, runtime updates, blocked downloads, conflicts, and notes not found.
