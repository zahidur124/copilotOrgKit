---
name: sbt-and-play
description: Work in Scala services built with sbt - multi-module builds, Play Framework apps, Akka or Apache Pekko actors and streams, and Cats Effect or ZIO code - by reading what the repo already uses and matching it. Use when editing build.sbt or files under project/, adding a dependency or sub-project, cross-building Scala 2.13 and 3, or writing Play routes, controllers, JSON formats, actors, streams or effect code in a Scala repo.
---

# sbt-and-play

A Scala service rests on a few choices made once: the sbt and Scala versions, Akka or Pekko, Guice or compile-time DI, Futures or an effect system. Code that mixes two of them fails to compile or fails at startup, so read what the repo uses first and match it. Code style is in the `scala` rules file (`.github/instructions/scala.instructions.md`, which loads for Scala and sbt files when the repo has it), running builds and tests in `build-and-test`, writing tests in `write-tests`, and version bumps in `dependency-upgrade`.

Rules that hold for every step:
- **Match the repo.** Same actor library, DI style, JSON library and effect system as the module you are in. Never add a second of any of these.
- **Do not change the sbt version (`project/build.properties`), `scalaVersion`, `crossScalaVersions`, or the Play, Akka or Pekko version unless the user asked.** Say which change you think is needed, and why, and stop.
- **Reload after a build change.** An open sbt shell or `sbt --client` server keeps the old build until you run `reload`. Do that after editing `build.sbt` or anything in `project/`, before you compile.
- **Never block a shared pool.** No `Await.result`, `Thread.sleep`, or blocking JDBC, file or HTTP call on Play's default execution context, an actor's default dispatcher, or the compute pool of Cats Effect or ZIO.

## 1. Read the build

- `project/build.properties` gives the sbt version; `project/plugins.sbt` the plugins (Play's `sbt-plugin`, scalafmt, packaging). `project/*.scala` files such as `Dependencies.scala` hold shared versions and dependency lists: when one exists, add dependencies there and refer to them from `build.sbt`.
- Each `lazy val api = (project in file("api"))` in `build.sbt` is a sub-project. Run a task on one with `api/compile` or `api/test`.
- `.dependsOn(core)` puts `core`'s classes on the classpath; `.dependsOn(core % "compile->compile;test->test")` also shares its test helpers. `.aggregate(core, api)` only runs a task on those projects too (`root/test` tests them all) and adds nothing to the classpath.
- Scopes: `ThisBuild / scalaVersion` applies to every project, `Compile / scalacOptions` to main code only, `Test / fork := true` to tests only. Put a setting at the narrowest scope that works, next to the repo's similar settings.
- sbt 2.x (a `2.` version in `build.properties`) changes this: build files are Scala 3, bare settings in `build.sbt` apply to all sub-projects in place of `ThisBuild`, and root-only settings use `LocalRootProject / name := ...`. Write the form the repo's sbt version uses.
- Integration tests: the `IntegrationTest` configuration is deprecated since sbt 1.9 and removed in sbt 2. Keep using it where the repo does; set up new ones as a sub-project with ordinary tests, `lazy val integration = (project in file("integration")).dependsOn(core)`.

## 2. Add a dependency or a Scala version

```scala
"org.playframework" %% "play-json"  % Versions.playJson        // Scala library: %% adds _2.13 or _3
"org.postgresql"     % "postgresql" % Versions.postgres        // Java library: plain %
"org.scalatestplus.play" %% "scalatestplus-play" % Versions.scalatestPlay % Test
```

- Use a version the repo already pins for that group (all Play, all Akka or all Pekko modules share one version). A new library's version comes from the user or `dependency-upgrade`, not from memory.
- Cross-building: `crossScalaVersions := Seq(...)` lists the versions. `sbt +test` runs on all of them; `sbt "++<version>" test` on one from that list. Code that differs per version goes in `src/main/scala-2.13/` and `src/main/scala-3/`. A 2.13-only library used from Scala 3 needs `.cross(CrossVersion.for3Use2_13)`; add it only where the repo already does this.

## 3. Play Framework

The plugin in `plugins.sbt` gives the version. Play 2.9 uses Akka and the `com.typesafe.play` group; Play 3.x uses Pekko and `org.playframework`; otherwise they have the same features. Code lives in `app/` (`app/controllers/`, `app/views/` for Twirl), config and routes in `conf/application.conf` and `conf/routes`, tests in `test/`.

```
GET   /users/:id    controllers.UserController.show(id: Long)
POST  /users        controllers.UserController.create()
```

Routes compile to code and match top-down, first match wins. Link and redirect with reverse routes, `Redirect(routes.UserController.show(id))`, never a hard-coded path.

```scala
@Singleton
class UserController @Inject() (cc: ControllerComponents, users: UserService)(implicit ec: ExecutionContext)
    extends AbstractController(cc) {

  def show(id: Long): Action[AnyContent] = Action.async {
    users.find(id).map(_.fold(NotFound: Result)(u => Ok(Json.toJson(u))))
  }

  def create(): Action[JsValue] = Action.async(parse.json) { request =>
    request.body.validate[NewUser].fold(
      errors => Future.successful(BadRequest(JsError.toJson(errors))),
      user   => users.create(user).map(u => Created(Json.toJson(u))))
  }
}
```

- The injected `ExecutionContext` is Play's default pool, for non-blocking work only. Run blocking calls on the repo's existing custom context, or add one: `class DbContext @Inject() (system: ActorSystem) extends CustomExecutionContext(system, "contexts.db")`, with `contexts.db { executor = "thread-pool-executor", thread-pool-executor.fixed-pool-size = 16 }` in `application.conf`.
- DI: Guice by default, with `@Inject()` constructors and bindings in a module listed in `play.modules.enabled`. If `application.conf` sets `play.application.loader`, the repo uses compile-time DI: wire new classes in its `BuiltInComponentsFromContext` subclass (often with MacWire), and do not add Guice.
- JSON (play-json): put `implicit val format: OFormat[User] = Json.format[User]` in the companion object; write a `Reads` with combinators when field names or validation differ. Use `validate` on request input, never `as`, which throws.
- Config: inject `Configuration` and read `config.get[String]("payments.url")` or `getOptional`. A new key goes in `application.conf` with a default and an `${?ENV_VAR}` override; secrets never go in the file.
- Tests use ScalaTestPlus-Play (7.0.x for Play 3.0, 6.0.x for Play 2.9): `PlaySpec` with `GuiceOneAppPerSuite` (or `OneAppPerSuiteWithComponents` for compile-time DI), `route(app, FakeRequest(GET, "/users/1"))`, `status(result) mustBe OK`. A controller can be built directly with `stubControllerComponents()`.

## 4. Akka or Apache Pekko

- Tell which one from the imports (`akka.` or `org.apache.pekko.`), the group (`com.typesafe.akka` or `org.apache.pekko`) and the config block (`akka { }` or `pekko { }`). Never mix them, and keep every module of one at the same version.
- Akka 2.7 and later are under the Business Source License, which can require a paid licence; Pekko is the Apache-licensed fork of Akka 2.6. That is why many projects moved to Pekko. Do not move Akka past 2.6, or switch to Pekko, without the user: it is a licence and migration decision.
- Typed (`Behaviors`, `ActorRef[T]`) or classic (`Actor`, `Props`, `receive`): write what the module around you uses.
- Blocking work in an actor runs on a dedicated dispatcher defined in config, not the default one: `context.spawn(behavior, "db", DispatcherSelector.fromConfig("blocking-dispatcher"))` (typed), `Props[A]().withDispatcher("blocking-dispatcher")` (classic).
- Ask needs an explicit `implicit val timeout: Timeout = 3.seconds`, and the reply `Future` can fail with a timeout: handle it. Inside an actor use `context.ask` or `pipeToSelf` (typed) or `pipe` (classic), never `Await`.
- Streams (`Source`, `Flow`, `Sink`) are back-pressured: a slow stage slows its producer. Call Future-returning code with `mapAsync(n)` (or `mapAsyncUnordered`) for bounded parallelism; never `Await` inside `map`. Give any `buffer` or `Source.queue` a bound and an explicit `OverflowStrategy`, and don't collect an unbounded stream with `Sink.seq`.

## 5. Cats Effect or ZIO

If the repo uses one, follow its patterns and do not bring in the other, or new `Future` code, in the same module. Acquire resources with `Resource` (Cats Effect) or `ZLayer`/`ZIO.scoped` (ZIO); wrap blocking calls in `IO.blocking` or `ZIO.attemptBlocking`; turn a `Future` into an effect with `IO.fromFuture` or `ZIO.fromFuture`. `unsafeRun*` and `Unsafe.unsafe` belong only at the program's edge (`IOApp`, `ZIOAppDefault`, a framework adapter), never in business code.

## 6. Metals MCP (optional)

If the organization allows MCP and the editor runs Metals 1.5.3 or later with `metals.startMcpServer` set to `true`, Metals offers tools such as `compile-file`, `compile-module`, `test` and `import-build`. Use them instead of starting sbt, and call `import-build` after a build change.
