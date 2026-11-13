# Language guides

A language guide is coding advice for one language. Copilot reads it on its own whenever it works on a file of that type. Each guide tells Copilot to follow the repo's own versions and habits first, and not to add new libraries unless you ask.

The guides are installed only into repos, by `install-repo.py`, when you pick that language's pack.

| Guide | For | Pack | Read when Copilot works on |
|---|---|---|---|
| `springboot.instructions.md` | Spring Boot (Java) | `java` | `.java` files |
| `scala.instructions.md` | Scala 2 and 3 | `scala` | `.scala`, `build.sbt`, `build.sc` |
| `nestjs.instructions.md` | NestJS | `node` | `.ts`, `.js`, `.json` files |
| `flutter.instructions.md` | Dart and Flutter | `flutter` | `.dart` files |
