# MochiHTTP — Command-driven CLI design (ADR-010)

> **Status:** approved design direction, not implemented. This document defines the public-facing CLI contract and a lightweight declarative architecture. Keep implementation incremental and learning-first.

## 1. Goal

MochiHTTP is a quick API-testing tool with friendly, **explicit commands**. It is not a curl wrapper, HTTPie clone, or SaaS. The HTTP/1.1 implementation remains our own (Python `socket`/`ssl`) and stays independent of the CLI.

We favor readable invocations over implicit behavior: **`mochi get URL`**, not `mochi URL` or `mochi GET URL`. Command names are lowercase. There is **no implicit GET**.

## 2. Planned interface

| Invocation | Behavior |
| --- | --- |
| `mochi get <URL>` | Send GET; show response (JSON prettified when appropriate) |
| `mochi post <URL> --json '{"name":"Mochi"}'` | Send JSON provided inline |
| `mochi post <URL> --body request.json` | Send file bytes as body |
| `mochi put <URL> --body request.json` | Replace/update a resource |
| `mochi patch <URL> --json '{"enabled":true}'` | Partial update |
| `mochi delete <URL>` | Send DELETE |
| `mochi auth` | Interactive credential/profile setup wizard |
| `mochi list` | List saved profiles (no secret values) |
| `mochi use <PROFILE>` | Select active profile persistently |
| `mochi --help` / `mochi <command> --help` | Generated help |

Examples are **planned**, not claims about existing behavior.

### Input conventions

- `URL` is a required positional argument for HTTP commands, initially an absolute `http://` or `https://` URL.
- After profile `base_url` support exists, a path such as `/products` may resolve against the active profile. Without a configured base URL, a relative path must fail clearly.
- `--header "Name: value"` is repeatable; preserve duplicate headers and safely reject CR/LF injection. Header names are case-insensitive.
- `--json '<JSON>'` takes inline JSON and sets `Content-Type: application/json` unless explicitly overridden. Ensure JSON validity. Quoting is **shell-dependent**; document PowerShell and POSIX examples separately.
- `--body <FILE>` loads a file (via `pathlib`) as bytes. **Not** a literal inline string. Do not assume every body is JSON.
- `--json` and `--body` are mutually exclusive. Additional body formats are out of scope.
- Option names, exact error messages, and output style may evolve before implementation; this doc is the intended contract.
- HTTP commands are **non-interactive**, suitable for shell scripts and CI. Only setup/management commands (starting with `auth`) may launch wizards, and must fail gracefully when stdin is unavailable.

## 3. Profile workflow (planned)

```console
mochi auth
# Wizard: profile name = dot-com-retail; auth kind = bearer; token entered via hidden input
# Optional base URL = https://api.example.com
mochi list
mochi use dot-com-retail
mochi get /products
mochi post /products --body product.json --header "X-Request-ID: 123"
```

An active profile supplies defaults (e.g. base URL and Authorization); explicit per-request options override corresponding defaults where safe. Never print tokens in `list`, logs, help, exceptions, or debug output. Do not persist them as plaintext in the project directory. Favor OS credential storage (e.g. `keyring` after a separate dependency decision) with profile metadata stored in a user configuration location via `pathlib`. Do not assume `keyring` is already installed. MVP auth: bearer token; other types (API keys, basic auth, client certificates/SSH-related workflows) need separate design and tickets. SSH keys are not interchangeable with HTTP Authorization; no SSH authentication feature is promised.

Treat redirects to another origin cautiously: do not forward stored Authorization credentials to other origins by default. A profile is local configuration, not a remote session.

## 4. Declarative CLI definition

Rather than scattering hundreds of `add_argument` calls, define the command surface as data — optionally Python dataclasses/dicts. `ParserSpec` describes CLI behavior; it is **not** the parser itself.

Minimal conceptual model:

- `ParserSpec(description, commands)`
- `Command(name, description, arguments, handler_id)`
- `Argument(name, description, ...)`

The `...` should capture **only** what a first working parser needs (positional vs option, required/default, repeatable/action, aliases/choices, mutually exclusive body sources). Avoid prematurely mirroring every `argparse` field. `Group` is **optional**, for help organization within complex commands; commands are not groups.

`prog="mochi"` can be supplied once by the CLI entry point rather than stored in `ParserSpec`. Do not add `epilog`, source-file hints, manual-page metadata, plugins or reflection frameworks unless a real use case requires them.

### Data flow

```text
CLI definitions (single source of truth)
        |                    |
        v                    v
Parser builder           Help / Markdown generator
(argparse subparsers)
        |
   parsed arguments
        |
   command dispatch (handler_id -> function)
        |
HTTP request handler         Profile management handler
        |                               |
Request model -> HTTP client       Profile store / secret backend
        |
response renderer
```

Use `argparse.add_subparsers()` as the parsing engine rather than writing a token parser. A registry maps command/handler identifiers to Python callables; the declarative spec itself contains no network logic. Parser generation should be deterministic and testable. Docs/help are derived from the same definitions. No dynamic imports or eval from untrusted configuration.

## 5. Component responsibilities

- `cli/spec.py`: small typed declarations.
- `cli/definitions.py`: commands/arguments as data.
- `cli/parser.py`: convert declarations to `argparse` and parse.
- `cli/dispatch.py`: select handler using registry.
- `cli/handlers/`: thin adapters for HTTP and profile actions.
- `profiles/`: profile configuration and credential access, introduced only when implemented.
- `docs/` generator (later): render command definitions to Markdown.
- Existing `core/`, `client/`, `protocol/`, `transport/`, `presentation/` boundaries remain intact.

Paths are proposals, **not** folders to create immediately.

## 6. Incremental delivery

1. Declarative command and argument models with unit tests.
2. Parser builder and dispatch for `get`, help and invalid commands (without HTTP).
3. Wire `get` to existing request/client layers once those are ready.
4. Add HTTP verbs, repeatable headers, inline JSON and body-file input.
5. Build a separate Markdown documentation generator from the same definitions.
6. Add profile metadata, secure bearer-secret storage, interactive `auth`, `list`, `use`, and optional base URL support.

This order is intentionally **not** a demand to implement all capabilities in one PR. No end-to-end integration is claimed before the corresponding HTTP milestones are complete.

## 7. Testing and portability

- Unit tests assert generated `--help`, argument validation, dispatch and mutual exclusion.
- CLI tests exercise errors, exit codes, stdout/stderr and commands with no network dependencies.
- Test JSON quoting per shell as documentation examples, not by assuming Bash syntax works in PowerShell.
- Never make credential storage dependent on a Unix-only home-directory convention; use portable paths/OS facilities.
- Test that profile names are validated, active-profile selection persists, secret output is redacted and non-TTY wizard behavior is predictable.
- No live internet required for automated tests; use a local test server and mock secret store.
- Windows, Linux and macOS remain targets.

## 8. Decisions and non-goals

**Decided:** explicit lowercase subcommands; lightweight schema-driven CLI; `argparse` as an internal adapter; handler-based dispatch; independent HTTP/1.1 engine; setup wizard for auth; non-interactive HTTP requests; future docs from same schema.

**Not decided/implemented yet:** exact dataclass API, option aliases, secret backend dependency, response formatting switches, profile selection per invocation, shell completions, public Python API for CLI definitions. These are extension points, not MVP commitments.

**Not in scope:** curl subprocess wrapping, implicit GET, HTTPie-specific syntax, SaaS backend, plugin system, generic dynamic command framework.

## References

- [Python argparse: subcommands and argument groups](https://docs.python.org/3/library/argparse.html)
- [Python dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Python pathlib](https://docs.python.org/3/library/pathlib.html)
- [Python getpass](https://docs.python.org/3/library/getpass.html)
- [HTTP/1.1 RFC 9112](https://www.rfc-editor.org/rfc/rfc9112.html)
- [Main architecture](architecture.md) · [Roadmap](roadmap.md)
