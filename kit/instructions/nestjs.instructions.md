---
applyTo: '**/*.ts, **/*.js, **/*.json'
description: 'Coding guidelines for TypeScript and JavaScript in NestJS services: modules and providers, DTO validation, configuration, errors, data access, async code, logging and security.'
---

# NestJS code

These rules cover code in a NestJS service (`@nestjs/core` in `package.json`). In other TypeScript, JavaScript or JSON files, apply only the general rules under "The repo comes first" and "TypeScript and async code".

## The repo comes first
- Match what the repo already does: its NestJS and Node versions, HTTP adapter (Express or Fastify), ORM, validation and config libraries, folder layout, file naming, test style, and ESLint and Prettier config. These guidelines apply only where the repo has no convention of its own.
- Never add a dependency unless the user asked. If the task seems to need one, say which and why, and stop. Do not edit `package.json` dependencies or the lockfile by hand.
- Keep the module system and import style the repo uses (CommonJS or ESM, path aliases from `tsconfig.json`).
- Running the build, lint and tests is in the `build-and-test` skill, writing tests in `write-tests`, version bumps in `dependency-upgrade`.

## Modules and providers
- Group code by feature: each feature has its own module with its controller, services and DTOs, as the repo lays them out.
- Register a provider in the module that owns it, and export it only if another module needs it. Import that module rather than registering the provider twice, which creates a second instance.
- Mark a module `@Global()` only for app-wide infrastructure such as config or database, and only if the repo already does.
- Avoid circular imports between modules. Move the shared code into a module both can import; use `forwardRef` only as a last resort.
- Use `forRoot` or `forRootAsync` for dynamic modules the way the repo already configures them.

## Dependency injection
- Inject through the constructor as `private readonly` parameters. Never create a service with `new` inside another provider.
- TypeScript interfaces do not exist at runtime, so a dependency typed by an interface needs a token: register it with `provide: TOKEN` and inject it with `@Inject(TOKEN)`. Keep tokens in a constants file, as `Symbol`s or strings as the repo does.
- Providers are singletons by default and shared across requests. Keep no per-request state in their fields.
- A request-scoped provider makes every provider that depends on it request-scoped as well, created again on each request. Use it only where the repo already does.

## Controllers and DTOs
- Keep controllers thin: read the request, call a service, return the result. Business logic belongs in services.
- Write DTOs as classes, not interfaces or types, because validation reads decorators at runtime.
- Validate every input with class-validator decorators on the DTO. Nested objects need `@ValidateNested()` with `@Type(() => Child)` from class-transformer, or they are not checked.
- Rely on the global `ValidationPipe` set in `main.ts`. If it does not use `whitelist` and `transform`, mention it rather than changing it.
- Parse route and query parameters with the built-in pipes (`ParseIntPipe`, `ParseUUIDPipe`) or a DTO, never by hand.
- Derive update DTOs with `PartialType`, `PickType` or `OmitType` from the package the repo already imports them from.
- Return response DTOs or serialized classes, never ORM entities with every column. Hide internal fields the way the repo does (`ClassSerializerInterceptor` with `@Exclude`, or explicit mapping).
- Do not inject `@Res()` unless you must stream or set something Nest cannot. It switches off Nest's response handling, so interceptors and serialization stop applying.

## Errors
- Throw Nest's HTTP exceptions (`NotFoundException`, `BadRequestException`, `ConflictException`) where a status is meant, or the repo's own domain errors that its exception filter maps.
- Keep one consistent error body. Add new cases to the repo's existing exception filter rather than writing a second one.
- Never send stack traces, SQL or internal messages to the client. Log them on the server.
- Catch an error only to add context, recover or translate it. Never swallow it.

## Configuration and secrets
- Read config through `ConfigService` or the repo's typed config, not `process.env` scattered through the code.
- Validate config at startup with the schema the repo already uses, so a missing value fails at boot rather than on first use.
- Secrets come from the environment or the repo's secret store. Never put them in code, committed `.env` files or tests.

## Data access
- Use the repo's ORM or client (TypeORM, Prisma, Mongoose, MikroORM, Drizzle) and its existing repository pattern. Do not add a second.
- Never build SQL by joining strings with input. Use the ORM's query builder with parameters or bound parameters in raw queries.
- Run writes that must succeed together in one transaction, the way the repo does it.
- Change the schema with a new migration, as the repo does. Do not turn on `synchronize` outside local development, and never edit a migration that has already run.
- Page list endpoints. Do not load whole tables.

## TypeScript and async code
- Keep to the strictness `tsconfig.json` sets. Do not use `any` or `as` casts to silence the compiler; type the value properly or use `unknown` and narrow it.
- Await or return every promise. A floating promise loses its errors and can outlive the request.
- Run independent awaits together with `Promise.all`, not one after another.
- Never block the event loop in request code: no synchronous file or crypto calls, no heavy CPU loops. Each one stalls every request.
- Set a timeout on every outbound HTTP call, using the client the repo already uses.
- Clean up timers, connections and subscriptions in `onModuleDestroy` or the shutdown hooks the repo enables.

## Request pipeline
- Use each Nest building block for its job: guards decide whether a request may proceed, pipes validate and transform input, interceptors wrap the handler (mapping, timing, caching), exception filters shape errors, middleware handles raw HTTP concerns.
- Apply them at the narrowest level that fits (handler, controller, then global), and register global ones the way the repo already does.

## Logging
- Use the repo's logger (Nest's `Logger`, often `new Logger(ClassName.name)`, or nestjs-pino), never `console.log`.
- Log with context such as ids, not whole request bodies.
- Never log secrets, tokens, passwords or personal data.

## Security
- Protect new routes with the repo's existing auth guards and role checks. A new route is never public by default; if one must be, mark it the way the repo marks public routes.
- Check that the caller owns the resource they ask for, not only that they are logged in.
- Hash passwords with the library the repo already uses. Never write your own crypto or token handling.
- Keep the existing CORS, Helmet and rate-limit settings. Never allow `*` origins together with credentials.
