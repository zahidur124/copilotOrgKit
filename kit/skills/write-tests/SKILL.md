---
name: write-tests
description: Write unit and integration tests that match the repo's existing tests - same framework, layout, naming and helpers - for Node.js/TypeScript, Java and Spring, Scala, Python and Flutter/Dart code, then run them and show they catch a break. Use when asked to add, write or extend tests, to cover a change or a bug fix with tests, or to raise test coverage.
---

# write-tests

A test that ignores the repo's conventions is missed by the runner (wrong folder or name), brings in a second framework, or repeats a helper that already exists. A test that checks how code works instead of what it does breaks on every refactor and still misses real bugs. So copy the repo's own tests, and test behaviour.

Rules that hold for every step:
- **Do not change production code** unless the user asked. If the code cannot be tested as it is (no way to replace a clock, client or database), stop and say which change would make it testable.
- **Test behaviour, not implementation.** Assert on what callers see: return values, saved state, events sent, HTTP responses, what is on screen. Not private methods, call order or internal fields. Mock only at the edges (I/O, other services), never the class under test.
- **One reason to fail per test.** One behaviour per test, named for it (`rejects an order with no items`), laid out as arrange, act, assert. Several asserts are fine when they check one result.
- **No network or real services in unit tests**: no HTTP calls, real database, broker or cloud SDK. Use the repo's fakes or mocks. Real services belong only in the integration tests the repo already keeps apart.
- **Same result every run**: no sleeps, a fixed clock, seeded randomness, no dependence on test order.
- **No new test library** unless the user agrees; use what the build file has. Fixtures hold made-up data, never secrets, customer data or internal hostnames.

1. **Find the existing tests and copy them.** List the tests near the code (`rg --files | rg -i 'test|spec' | head -40`), read two or three, and read the shared helpers: `conftest.py`, `test/helpers`, `testutil`, fixture builders, mock folders, a `pumpApp` extension. Note the framework and its version, where files go and how they are named, how tests are grouped and named, the assertion and mock libraries, and which helpers exist. Use all of them. If the repo has no tests, use the framework its build file names and ask before adding one.

2. **List the behaviours to cover**: the normal case, the edges (empty, null or None, boundary values) and the error paths. For a bug fix, first a test that reproduces the bug. Show the list in your reply.

3. **Write the tests in the stack's style.**
   - **Jest, Vitest or `node:test`**: use the runner in `package.json` and its config (`jest.config.*`, `vitest.config.*`, `test` in `vite.config.*`). Put files where existing ones are (`*.test.ts` beside the source, or `__tests__/`). Vitest needs `import { describe, it, expect, vi } from 'vitest'` unless its config sets `globals: true`. Mock with `jest.fn()` and `jest.mock()`, or `vi.fn()` and `vi.mock()`; fake time with `useFakeTimers()`. Stub HTTP with the repo's tool (msw, nock), or pass in a fake.
   - **Java**: JUnit Jupiter (`org.junit.jupiter.api.Test`, in JUnit 5 and 6). Never JUnit 4's `org.junit.Test` in a Jupiter repo: without the vintage engine it is silently not run. AssertJ `assertThat(...)` and Mockito (`@ExtendWith(MockitoExtension.class)`, `@Mock`, `@InjectMocks`) where the repo uses them; `@ParameterizedTest` with `@CsvSource` for table cases. Name files so the runner finds them: Surefire runs `*Test`, `*Tests`, `Test*`, `*TestCase`; Failsafe runs `*IT`; check the build file for overrides.
   - **Spring Boot**:
     - Prefer a slice to `@SpringBootTest`: `@WebMvcTest(OrderController.class)` with `MockMvc` for a controller, `@DataJpaTest` for a repository. Replace beans with `@MockitoBean` (Boot 3.4 and later; `@MockBean` before that, removed in Boot 4).
     - For a real database, use Testcontainers in an integration test: `@Testcontainers`, a `static` `@Container` field and `@ServiceConnection` (Boot 3.1 and later); with `@DataJpaTest` before Boot 3.4, also `@AutoConfigureTestDatabase(replace = Replace.NONE)`. Containers need Docker and an image pulled through the company mirror; if either is missing, report it.
     - Boot 4 moved the slice annotations, and Testcontainers 2 the container classes, to new packages, so copy imports from an existing test, not from memory.
   - **Scala**: use the repo's library and the same style class. ScalaTest: `AnyFunSuite`, `AnyFlatSpec` or `AnyWordSpec` with `Matchers`. MUnit: `munit.FunSuite` with `assertEquals(obtained, expected)`, `CatsEffectSuite` for `IO`. ZIO Test: `object OrderSpec extends ZIOSpecDefault` with `suite(...)(test(...)(assertTrue(...)))`, and `TestClock` for time. Files go in `src/test/scala` under the same package, named `*Spec`, `*Suite` or `*Test` as the repo does.
   - **Python (pytest)**: `test_*.py` in the repo's tests folder. Reuse fixtures from the nearest `conftest.py` before adding one. `@pytest.mark.parametrize` for table cases, `pytest.raises` for errors, the built-in `tmp_path` and `monkeypatch` for files and environment. Stub HTTP with the repo's tool (responses, respx, pytest-httpx) or monkeypatch the client. If the repo writes `unittest` classes, write those.
   - **Flutter / Dart**:
     - Files go under `test/`, mirroring `lib/`, ending `_test.dart`. `test()` and `group()` for plain logic; `testWidgets` with `pumpWidget` for widgets, wrapped in the same app, theme and providers as the repo's widget tests. `pumpAndSettle` times out while an animation repeats (a spinner); use `pump(duration)` there.
     - Mock with whichever the repo uses: mocktail (`class MockOrderRepo extends Mock implements OrderRepo {}`, `when(() => ...)`, `registerFallbackValue` before `any()` on your own types) or mockito (`@GenerateNiceMocks([MockSpec<OrderRepo>()])`, then `dart run build_runner build`).
     - Golden tests only where the repo has them: `matchesGoldenFile`, with the images made by `flutter test --update-goldens <file>`. Fonts render differently on each operating system, so say which one made the images.
     ```dart
     testWidgets('shows an error when saving fails', (tester) async {
       when(() => repo.save()).thenAnswer((_) async => throw Exception('offline'));
       await tester.pumpWidget(MaterialApp(home: OrderPage(repo: repo)));
       await tester.tap(find.text('Save'));
       await tester.pump();
       expect(find.text('Could not save'), findsOneWidget);
     });
     ```

4. **Run them** with the build-and-test skill: the new test file first, then the module's suite. A test that fails because the code is wrong is a finding to report, not something to loosen until it passes.

5. **Show that they catch a break, where practical.** Make one small temporary edit to the code under test (flip a condition, return a wrong value), run the new tests and see them fail with a clear message, then undo the edit and check that `git diff -- <file>` shows nothing left. For a bug fix, the new test fails on the code before the fix. If you may not edit the code, say this check was not done.

6. **Report**: each test file written and the behaviours it covers, the commands run with their results, the break check and what it showed, and what is still not covered.
