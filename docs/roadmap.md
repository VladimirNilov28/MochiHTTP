# MochiHTTP — Learning-first Roadmap

We build **one small working slice at a time**. The goal is to learn Python while building a useful HTTP tool. Do not implement the complete target architecture up front.

## How to use this roadmap

1. Start with the **lowest-numbered open Issue**.
2. Read its short references *as needed*, then implement the task yourself.
3. Run its acceptance checks and tests.
4. Open a small PR, review, merge, and close the Issue.
5. Move to the next task. Do not skip straight to TLS or the full parser.

Each Issue should explain *why*, *what*, a checklist, observable success criteria, and links to official resources. Issues should **not** contain full solutions.

## Phase 0 — Development environment

- [ ] **01 — Initialize a uv package** (`pyproject.toml`, Python version, src layout).
- [ ] **02 — Add the `mochi` CLI entry point** (help and version; no networking).
- [ ] **03 — Add pytest and Ruff** (dev dependencies; simple automated checks).

**Milestone:** `uv run mochi --help`, `uv run pytest`, and `uv run ruff check .` work on the developer's chosen OS (Windows, Linux, or macOS). WSL2 is optional.

## Phase 1 — Minimal HTTP over TCP

- [ ] **04 — Parse and validate an HTTP URL**.
- [ ] **05 — Create and serialize a simple HTTP/1.1 GET request**.
- [ ] **06 — Connect to a local server with TCP sockets and read bytes**.
- [ ] **07 — Parse status line and headers**.
- [ ] **08 — Read the response body safely** (Content-Length, chunked, no-body and EOF framing).
- [ ] **09 — Join components into a usable `mochi GET URL` command**.

**Milestone:** a simple local HTTP GET works end-to-end with tests, without `requests` or `httpx`.

## Phase 2 — HTTPS and UX

- [ ] **10 — Add TLS with certificate and hostname verification**.
- [ ] **11 — Pretty-print response data using Rich**.
- [ ] **12 — Add request methods, headers, query parameters and JSON bodies**.
- [ ] **13 — Handle timeouts, limits and clear error messages**.

**Milestone:** a practical and reasonably robust HTTPS client with terminal-friendly output.

## Phase 3 — Polish

- [ ] Redirect handling with careful credential rules.
- [ ] Cookie/session behavior.
- [ ] Save raw body to file; safe binary and piped output.
- [ ] Compression and streaming.
- [ ] **Cross-platform CI:** add a GitHub Actions matrix for Windows, Linux and macOS; run uv setup, pytest, Ruff and local client integration tests on every OS. Document any genuine platform-specific behavior.
- [ ] Packaging/release documentation.
- [ ] Public Python `Client` API.

## Platform support throughout the roadmap

- Develop natively on Windows, Linux or macOS; on Windows, WSL2 is an optional alternative.
- Keep the first synchronous socket/ssl implementation portable. Do not add OS-specific backends or async event loops just for portability.
- Prefer loopback tests with ephemeral ports and no external network dependencies.
- Manually sanity-check platforms where available during early phases. The CI matrix becomes required for release readiness in Phase 3; adding it earlier is welcome once tests exist.

## Future, not MVP

Connection reuse, async/concurrent requests, proxy support, plugins, TUI, HTTP/2.

## Project commands (target; require implementing the setup issues)

```bash
uv sync
uv run mochi --help
uv run pytest
uv run ruff check .
```

These are **target commands**, not a claim that the repository is already set up.

## References

- [uv project guide](https://docs.astral.sh/uv/guides/projects/)
- [Python packaging / pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [Python argparse](https://docs.python.org/3/library/argparse.html)
- [Python socket](https://docs.python.org/3/library/socket.html)
- [RFC 9112](https://www.rfc-editor.org/rfc/rfc9112.html)
