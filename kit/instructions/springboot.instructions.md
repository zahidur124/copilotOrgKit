---
applyTo: '**/*.java'
description: 'Coding guidelines for Java code in Spring Boot services: layering, injection, configuration, transactions, data access, errors, logging and security.'
---

# Spring Boot code

These rules cover Java code in a Spring Boot service. In Java code that does not use Spring, apply only the plain Java rules.

## The repo comes first
- Match what the repo already does: its Spring Boot and Java versions, libraries, package layout, naming, error format, test style and formatter config. These guidelines apply only where the repo has no convention of its own.
- Use only language features the repo's Java release allows; the build file says which (`maven.compiler.release`, `<java.version>` or the Gradle toolchain).
- Use the `jakarta.*` or `javax.*` imports the repo already uses. Never mix the two.
- Never add a dependency or starter unless the user asked. If the task seems to need one, say which and why, and stop.
- Use Lombok only where the repo already does, with the same annotations.
- Running the build and tests is in the `build-and-test` skill, writing tests in `write-tests`, version bumps in `dependency-upgrade`.

## Structure
- Keep the repo's layering, usually controller, service, repository. Controllers translate HTTP to a service call and back; business rules live in services.
- A new class goes in the package of the feature it belongs to, beside its neighbours.
- Controllers take and return DTOs, often records, never JPA entities. An entity in a response leaks fields and triggers lazy loading during serialization.
- Map between entities and DTOs the way the repo does (MapStruct, static factory methods, hand-written mappers). Do not add a mapper library.
- Keep `@Configuration` classes for wiring beans. No business logic in them.

## Dependency injection
- Inject through the constructor into `private final` fields. A class with one constructor needs no `@Autowired`.
- No field injection and no setter injection: they hide dependencies and make the class hard to build in a test.
- A class that needs many collaborators is doing too much; say so rather than adding another.
- Never call `ApplicationContext.getBean` from business code.
- Fix a circular dependency by moving the shared logic into a third bean, not with `@Lazy`.

## Configuration and secrets
- Group related settings in a `@ConfigurationProperties` class or record, with `@Validated` and constraints so a bad value fails at startup. Use `@Value` only for a single isolated value, as the repo does.
- A new property goes in the repo's `application.yml` or `application.properties` with a safe default, and is documented where the repo documents config.
- Secrets come from environment variables or the repo's secret store, never from a committed config file, code or a test fixture.
- Put environment differences in profile files (`application-<profile>.yml`). Do not set `spring.profiles.active` in the committed main config.
- Use `@Profile` on beans sparingly; profile-specific beans are code paths that tests rarely cover.

## Validation
- Validate request bodies with `@Valid` and Bean Validation annotations on the DTO (`@NotBlank`, `@Size`, `@Positive`).
- Put `@Validated` on the class to validate `@PathVariable` and `@RequestParam` constraints.
- Check business rules that need the database in the service, not in annotations.

## Errors
- Throw a specific exception for each domain failure (`OrderNotFoundException`), not a bare `RuntimeException`.
- Turn exceptions into HTTP responses in one `@RestControllerAdvice`, in the error format the repo already returns (for example `ProblemDetail`).
- Never send stack traces, SQL or internal class names to the client.
- Catch an exception only to add context, recover or translate it. Never catch and ignore, and never catch `Exception` or `Throwable` in business code.
- Use `Optional` as a return type for "may be absent", not for fields or parameters. Never call `Optional.get()` without a check; use `orElseThrow`.

## Transactions
- Put `@Transactional` on public service methods, not on controllers or repositories you write.
- The annotation works through a proxy, so a call from one method to another in the same class skips it. Move the transactional method to another bean, or put the boundary on the outer method.
- Use `@Transactional(readOnly = true)` for methods that only read.
- By default only unchecked exceptions roll back. If a checked exception must roll back, set `rollbackFor`.
- Keep remote calls, file I/O and long work out of a transaction; it holds a database connection the whole time.
- `@Async`, `@Cacheable` and `@Retryable` go through the same kind of proxy and share the self-call trap.

## Data access
- Use the repo's data access style: Spring Data repositories, `JdbcTemplate`, `JdbcClient`, jOOQ or MyBatis. Do not add a second.
- Never build SQL or JPQL by joining strings with input. Use bound parameters or derived query methods.
- Watch for N+1 queries when a loop touches a lazy association. Load what is needed with a fetch join, `@EntityGraph` or a projection.
- Page any query that can return many rows (`Pageable`). No unbounded `findAll()` on a large table.
- Do not use Lombok `@Data` or `@EqualsAndHashCode` on entities; generated equality over lazy fields breaks with proxies and in sets.
- Schema changes go in a new Flyway or Liquibase migration, as the repo does. Never edit a migration that has already run.
- Do not rely on open-session-in-view to load data in a controller. Load it in the service.

## Concurrency and HTTP clients
- Beans are singletons shared by all requests. Keep no request state in their fields.
- A Spring MVC service and a WebFlux service are written differently. Write the style the module uses and never block inside a reactive chain.
- Run `@Async` and scheduled work on the repo's configured executor, not on a new thread pool you create.
- Call other services with the HTTP client the repo uses (`RestClient`, `RestTemplate`, `WebClient`, an HTTP interface or Feign), with timeouts set.

## Logging
- Use SLF4J through a `private static final Logger`, or Lombok `@Slf4j` where the repo does. Never `System.out`.
- Write parameterized messages (`log.info("Order {} shipped", id)`), not string concatenation.
- Pass the exception as the last argument so the stack trace is kept, and log it once, where it is handled.
- Never log secrets, tokens, passwords or personal data.

## Security
- Add new endpoints to the repo's existing Spring Security configuration (`SecurityFilterChain` bean) and state who may call them. A new endpoint is never public by default.
- Check authorization the way the repo does: URL rules or `@PreAuthorize` method security.
- Keep CSRF protection on for browser sessions with cookies. Turn it off only for stateless token APIs, as the repo already does.
- Do not expose actuator endpoints beyond what the repo already exposes.
- Never allow `*` origins in CORS together with credentials.
