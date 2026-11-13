---
applyTo: '**/*.scala, **/build.sbt, **/build.sc'
description: 'Coding guidelines for Scala 2 and Scala 3 code: immutability, types, Option and Either, implicits and givens, Futures and effect types, collections, logging and security.'
---

# Scala code

## The repo comes first
- Match what the repo already does: its Scala version (2.12, 2.13 or 3, or a cross-build), libraries, effect system, JSON library, package layout, naming and test style. These guidelines apply only where the repo has no convention of its own.
- Format to the repo's `.scalafmt.conf`, including its `runner.dialect`. Keep the compiler flags, scalafix and linter rules the repo sets; fix a warning rather than suppressing it.
- Never add a dependency unless the user asked. If the task seems to need one, say which and why, and stop.
- sbt builds, Play, Akka or Pekko, Cats Effect and ZIO are in the `sbt-and-play` skill. Running builds and tests is in `build-and-test`, writing tests in `write-tests`, version bumps in `dependency-upgrade`.

## Scala 2 or Scala 3
- Write the syntax of the Scala version the file compiles with. In cross-built code shared by both, write what both compilers accept, and put version-specific code in the version source folders the repo already has (such as `src/main/scala-2.13` and `src/main/scala-3`).
- Scala 3 files: keep the brace or indentation style the file and scalafmt use. Never mix both in one file.
- Imports: `import a.b._` in Scala 2, `import a.b.*` in Scala 3. In Scala 3 a wildcard does not bring in givens; add `import a.b.given` where needed.
- Write `def run(): Unit = { ... }`, not procedure syntax `def run() { ... }`, and call a method declared with `()` with `()`. Scala 3 dropped both shortcuts.
- In 2.13 and 3, `Seq` means `immutable.Seq`; in 2.12 it means `collection.Seq`. Code cross-built with 2.12 must not depend on which.
- Convert Java collections with the converter the repo imports: `scala.jdk.CollectionConverters` (2.13, 3) or `scala.collection.JavaConverters` (2.12).

## Immutability and data
- Use `val`. Use `var` only for a local accumulator in a hot loop where the repo already does, and never let it escape the method.
- Use immutable collections. A mutable collection stays local to the function that builds it.
- Model data with case classes and change it with `copy`.
- Model a closed set of cases with a `sealed trait` and case classes or objects in Scala 2, and with `enum` in Scala 3 where the repo does.
- Wrap ids and other easily swapped primitives where the repo does: value classes (`extends AnyVal`) in Scala 2, `opaque type` in Scala 3.
- Keep pattern matches on sealed types exhaustive, with no `case _` that would hide a newly added case.
- Do not use `isInstanceOf` or `asInstanceOf`. Match on types instead, and remember generic type arguments are erased at runtime, so `case xs: List[String]` checks nothing about the elements.

## Absence and errors
- Never use `null` in Scala code. Wrap a value from Java that may be null with `Option(value)` at the boundary.
- Do not call `.get` on `Option` or `Try`, or `.head` or `.last` on a collection that can be empty. Use `getOrElse`, `fold`, `headOption` or a match.
- Return `Either` with a sealed error type for failures the caller is expected to handle (not found, invalid input). Do not use bare `String` errors where the repo has error types.
- Throw only for bugs and broken infrastructure, or where the repo's effect type carries the error.
- Use `Try` to wrap Java or other code that throws, then turn it into the repo's error type.
- Catch with `case NonFatal(e)`, never `case e: Throwable`, which also catches interruptions and fatal JVM errors.
- Do not use `return`. Inside a lambda it escapes by throwing, which is easy to misread.

## Types and signatures
- Write the result type of every public method and every implicit or given definition. Inferred public types leak implementation types and change silently.
- Keep public methods small and named for what they return or do.
- Use default and named arguments over overloads with many parameters.
- Compare values with `==`. Arrays compare by reference, so use `sameElements` for them.

## Implicits and givens
- Use them for type class instances (encoders, `Ordering`, `Show`) and for context the repo already passes this way, such as `ExecutionContext`. Not for ordinary parameters.
- Scala 2: `implicit val`, `implicit def` and implicit parameter lists; extension methods as `implicit class`, as a value class where possible.
- Scala 3: `given` instances, `using` clauses and `extension` methods. Use `derives` where the library supports it and the repo does.
- Put a type class instance in the companion object of the type it is for, so it is found without an import.
- Do not write implicit conversions (`implicit def` from A to B in Scala 2, `Conversion` in Scala 3). They make code hard to follow; write an explicit method.

## Concurrency
- Match the repo's async model: `Future`, Cats Effect `IO`, ZIO, or actors. Never mix a second one into a module.
- A `Future` starts as soon as it is created; an effect runs only when executed. Build effects freely, but create a `Future` only where it should start.
- Pass the `ExecutionContext` in as the repo does. Do not import `ExecutionContext.Implicits.global` in application code.
- Never call `Await.result` outside a program's edge or a test. Run blocking calls on the repo's blocking pool, or inside `blocking { }` for `Future` code.
- Share mutable state only through the repo's tools (`Ref`, an actor, `AtomicReference`), never a plain `var` read by several threads.
- Combine independent `Future`s or effects in parallel with the library's own operators, not by awaiting each in turn.

## Collections
- Prefer `map`, `flatMap`, `filter`, `collect`, `foldLeft` and for-comprehensions over index loops.
- Choose the collection by access pattern: `Vector` or `List` for sequences, `Map` and `Set` for lookups. Do not call `apply(i)` on a `List` in a loop; it is linear each time.
- Do not call `.size` on a collection only to test for emptiness; use `isEmpty` or `nonEmpty`.

## Logging and security
- Use the repo's logger (SLF4J, scala-logging, log4cats or the effect library's logging). Never `println` in application code.
- Never log secrets, tokens, passwords or personal data.
- Never build SQL by joining strings with input. Use the database library's parameterized form (doobie or Slick interpolators, Anorm with named parameters).
- Secrets come from the environment or the repo's secret store through its config, never from code or a committed config file.
