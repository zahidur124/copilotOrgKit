---
applyTo: '**/*.dart'
description: 'Coding guidelines for Dart and Flutter code: widget composition, state management, null safety, async code and BuildContext, data and errors, logging and security.'
---

# Dart and Flutter code

These rules cover Dart code, and Flutter app code where the project depends on Flutter. In a pure Dart package or server, skip the widget sections.

## The repo comes first
- Match what the repo already does: its Flutter and Dart SDK constraints, state management, router, DI, HTTP client, model generation, folder layout, naming and test style. These guidelines apply only where the repo has no convention of its own.
- Keep to `analysis_options.yaml` and `dart format`. Fix a lint rather than silencing it; an `// ignore:` needs a comment saying why.
- Never add a package to `pubspec.yaml` unless the user asked. If the task seems to need one, say which and why, and stop.
- Use only language features the SDK constraint in `pubspec.yaml` allows.
- Running analyze, build and tests is in the `build-and-test` skill, writing tests in `write-tests`, version bumps in `dependency-upgrade`.

## Structure
- Keep the repo's layers: widgets show state and forward user actions; state classes (Bloc, Cubit, Notifier, ChangeNotifier, controller) hold logic; repositories and services do I/O.
- Never call HTTP, a database or platform storage from a widget's `build` or callbacks directly. Go through the repo's state and repository layers.
- Keep API (JSON) models apart from the models the UI uses where the repo does, and map between them in the data layer.
- Put a new file in the feature folder it belongs to, named in `snake_case.dart` like its neighbours.

## Widgets
- Build screens from small widgets. Extract a part into its own `StatelessWidget` class, not a method returning a widget, so Flutter can skip rebuilding it.
- Add `const` constructors to widgets and use `const` at call sites wherever possible; a const widget is not rebuilt.
- Keep `build` fast and free of side effects: no I/O, no creating futures or streams, no heavy computation. It can run every frame.
- Create the future or stream a `FutureBuilder` or `StreamBuilder` listens to outside `build` (in `initState` or the state layer). One created in `build` restarts on every rebuild.
- Give list items a stable `Key` from their data when items can be reordered, inserted or removed.
- Use builders (`ListView.builder`, `GridView.builder`) for long or unbounded lists.
- Use `StatefulWidget` only for local UI state such as a text controller or animation. App state belongs in the repo's state management.
- Dispose what you create in a `State`: controllers, focus nodes, animation controllers, stream subscriptions and timers.
- Take colours, text styles and spacing from the theme and the repo's design constants, not hard-coded values.
- Put user-visible text through the repo's localization setup where it has one.

## State management
- Use the state management the repo uses (Provider, Riverpod, Bloc, GetX, plain `ChangeNotifier`) and its patterns for scoping and reading state. Never add a second one.
- Keep state immutable where the repo does: emit a new state object instead of changing fields in place, using its `copyWith` or generated models.
- Rebuild as little as possible: listen to the part of state a widget needs, with the repo's selector or `buildWhen` equivalent.

## Null safety
- Prefer a null check, `?.`, `??` or an early return to `!`. Use `!` only where the value cannot be null at that point, with a comment if the reason is not obvious; otherwise it is a runtime crash waiting.
- Use `late` only when the value is always set before first use, as in `initState`. A `late` read before assignment throws at runtime.
- Make a field or parameter nullable only when absence is a real case; required named parameters use `required`.

## Async code and BuildContext
- Await every future, or wrap one you mean to leave running in `unawaited(...)` so the intent is clear.
- After an `await` in a widget, check `context.mounted` (or `mounted` in a `State`) before using the `BuildContext` or calling `setState`. The widget may be gone by then.
- Better still, read what you need from the context (navigator, messenger, theme) before the `await`.
- Cancel stream subscriptions and timers in `dispose`.
- Move heavy CPU work, such as parsing a large JSON payload, off the UI isolate with `compute` or `Isolate.run`, as the repo does.

## Errors
- Catch specific exceptions with `on SomeException catch (e)`. Do not catch `Error` subclasses; they mean a bug.
- Turn errors into a state the UI shows (an error message or retry), the way the repo models them. Never fail silently or leave a spinner running.
- Keep the stack trace when rethrowing or reporting: `catch (e, stackTrace)` and `rethrow`, or `Error.throwWithStackTrace`.
- Report uncaught errors through the hooks the repo already sets (`FlutterError.onError`, `PlatformDispatcher.instance.onError`, a crash reporter).

## Data and models
- Write models the way the repo does: hand-written with `fromJson` and `toJson`, or generated with json_serializable, freezed or built_value. After changing an annotated model, rerun the repo's code generation; do not edit `*.g.dart` or `*.freezed.dart` files by hand.
- Parse server data defensively. A missing or wrongly typed field should give a clear error, not a crash deep in the UI.
- Set timeouts on network calls through the client the repo uses.

## Logging and security
- Log through the repo's logger, or `debugPrint` and `dart:developer` `log`. Never `print` in app code.
- Never log tokens, passwords or personal data.
- Anything compiled into the app, including `--dart-define` values and bundled assets, can be extracted from it. Never put API secrets in the app; they belong on a server.
- Store tokens and credentials only with the secure storage the repo already uses, never in shared preferences or plain files.
- Validate deep link and route parameters before acting on them.
