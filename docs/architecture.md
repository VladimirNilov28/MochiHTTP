# MochiHTTP — Architecture Specification (v0.1)

> Status: design baseline. No implementation exists yet. Changes should be recorded before implementation when they affect public behavior or module boundaries.

## 1. Product and scope

MochiHTTP is a friendly, human-readable HTTP client for the terminal, invoked with `mochi`. It will also expose a small Python API later.

- Language: Python 3.13+.
- Project and dependency manager: **uv**.
- Runtime dependencies: Python standard library + **Rich** for terminal presentation.
- Protocol target for MVP: **HTTP/1.1**, implemented by us using `socket` and `ssl`.
- Supported development and execution platforms: Windows, Linux, and macOS; WSL2 is an optional Linux workflow on Windows.
- Visual language: restrained, readable terminal output with soft pastel accents.
- Learning principle: implement components in small steps; avoid supplying complete solutions in beginner issues.

### Initial user experience (illustrative, not implemented)

```console
mochi https://example.com
mochi GET https://example.com
mochi POST https://example.com/api name=Mochi
mochi GET https://example.com Authorization:"Bearer TOKEN"
mochi --verbose GET https://example.com
```

For the first milestones, support explicit `GET URL` and simple arguments before adopting shorthand `name=value` and `Header:value` conventions. Do not let CLI sugar complicate the network engine.

## 2. Architectural style

**Modular monolith / layered architecture**, with clear dependencies:

```text
                       CLI (argument parsing)
                                 |
                       Application / Client
                                 |
                        HTTP/1.1 Protocol
                                 |
                         TCP/TLS Transport
                                 |
                         OS / socket APIs

Core: Request, Response, URL, Headers, errors, configuration
Presentation: formats responses; used only by CLI, never by protocol/transport
```

Rules:
1. Transport only moves bytes; it never parses HTTP or prints terminal output.
2. Protocol serializes and parses HTTP/1.1; it does not own presentation.
3. Client owns a request's lifecycle and coordinates transport/protocol.
4. CLI converts user input into requests; it does not open sockets.
5. Presentation receives structured results, not raw sockets.
6. No cyclic imports. Depend on simple models and minimal interfaces rather than framework-style dependency injection.

## 3. Proposed modules

```text
src/mochi/
  __init__.py
  __main__.py
  api.py                  # later: public convenience API
  cli/
    main.py
    parser.py
  core/
    models.py
    headers.py
    url.py
    errors.py
  client/
    client.py
    builder.py
  protocol/
    http11/
      serializer.py
      parser.py
      framing.py
  transport/
    tcp.py
    tls.py
  presentation/
    renderer.py
    themes.py
tests/
  unit/
  integration/
  fixtures/
```

This is a *target layout*, not a request to create empty files immediately. Grow the structure when a task needs it.

## 4. Core contracts (design, not code)

| Model | Responsibility |
| --- | --- |
| `Request` | Method, URL, ordered headers, optional bytes body |
| `Response` | HTTP version, status, headers, response body, timing |
| `URL` | Scheme, host, port, path, query; validates supported schemes |
| `Headers` | Case-insensitive lookup, preserves duplicates and necessary ordering |
| `ClientConfig` | Timeouts, TLS settings, output-independent size limits |
| `MochiError` | Base for meaningful CLI-facing errors |

**Bytes-first:** request/response bodies remain bytes in the protocol and client layers; parsing JSON, decoding text and syntax highlighting belong outside transport and HTTP framing. HTTP headers must not be modeled with a plain dictionary that discards duplicates.

For v0.1 a buffered `Response.body` is acceptable with a strict maximum body size. Streaming can be introduced later without exposing sockets to CLI users.

## 5. Request lifecycle

1. CLI parses options, method, URL and user-supplied fields.
2. Request builder creates a validated `Request`.
3. Client chooses TCP or TLS transport and connects to the server.
4. HTTP serializer emits valid HTTP/1.1 bytes.
5. Transport writes all bytes (handle partial writes).
6. Transport reads chunks of bytes from the connection.
7. Incremental response parser reads status line and headers; framing determines the body boundary.
8. Client closes resources and returns a `Response`.
9. Presentation renders readable terminal output; exit code reflects CLI/process failure, not automatically an HTTP 4xx/5xx.

A TCP `recv()` call is **not** an HTTP message. A response may arrive in fragments; parsers must be independent of chunk boundaries.

## 6. HTTP/1.1 correctness boundaries

- Use CRLF delimiters and a valid request-target (path + query).
- Include a correct `Host` header and handle explicit ports and IPv6 literals properly.
- Distinguish status codes with no response body, HEAD responses, `Content-Length`, `Transfer-Encoding: chunked`, and close-delimited bodies.
- Handle informational (1xx) responses correctly; do not confuse their headers with the final response. Protocol upgrades are out of scope for MVP.
- Parse headers defensively; reject malformed framing and ambiguous/conflicting length metadata rather than guessing.
- Enforce line/header/body size limits to prevent unlimited memory use.
- Read until the declared body boundary, **not** necessarily until connection close.
- Initial client policy: one request per connection, with `Connection: close`; keep-alive/pooling comes later.
- Content encoding (gzip/deflate) and redirect following are separate later client features.

Reference: [RFC 9112 — HTTP/1.1](https://www.rfc-editor.org/rfc/rfc9112.html), [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html).

## 7. Transport and TLS

- TCP transport: DNS resolution via OS, connect, read, write, close, clear exceptions.
- TLS transport: uses Python's standard-library `ssl` over a TCP socket, validates certificate chain and hostname by default.
- Do **not** implement TLS encryption manually.
- Timeouts: connect timeout and read timeout initially; a complete-request deadline is a later enhancement.
- Transport owns its sockets; close them on success **and** failure.
- No automatic retry of methods that may change server state.

References: [Python socket](https://docs.python.org/3/library/socket.html), [Python ssl](https://docs.python.org/3/library/ssl.html).

## 8. Cross-platform support (ADR-009)

**Goal:** the same `mochi` CLI and Python client core must work natively on Windows, Linux, and macOS. WSL2 is a supported development option, not a requirement. Use Python's portable APIs first; add OS-specific handling only for verified differences.

- Keep protocol parsing, request serialization, URL models, and presentation independent of the operating system.
- Use `socket` for DNS/TCP and `ssl` for HTTPS; do not import Windows-specific Winsock interfaces or Linux-only `epoll` directly in MVP code.
- The MVP uses synchronous blocking sockets. `asyncio`, `epoll`, `kqueue`, and IOCP are **not** part of the MVP; a future async feature needs its own design decision.
- Use `pathlib` for paths and portable file handling; avoid shell-specific assumptions in application code and tests.
- Handle ordinary socket/TLS/timeout exceptions consistently. OS error codes and wording may differ; avoid assertions on exact platform-specific error messages.
- Preserve secure TLS verification defaults on every platform. System trust stores and certificate availability may differ; tests must not rely on public internet endpoints or a particular machine's trusted CAs.
- Avoid relying on Unix-only signals, `fork`, `SO_REUSEPORT`, or other optional OS facilities in core client behavior.
- Network integration tests should bind to loopback using an ephemeral port and clean up all sockets. Do not assume port 8080 is available.
- Cross-platform CI target: GitHub Actions matrix with `ubuntu-latest`, `windows-latest`, and `macos-latest`, using the project's supported Python version and uv. Run unit, local integration and CLI tests plus Ruff on each runner. CI setup will be implemented in a roadmap task; it does not exist yet.
- Platform-specific deviations require a documented reason, an isolated implementation, and tests where feasible. Linux may be the primary deployment target, but native Windows and macOS remain supported.

**Acceptance target:** `uv sync`, `uv run mochi --help`, `uv run pytest`, and `uv run ruff check .` work on each supported OS once their corresponding setup milestones have been completed.

References: [Python socket](https://docs.python.org/3/library/socket.html), [Python ssl](https://docs.python.org/3/library/ssl.html), [Python pathlib](https://docs.python.org/3/library/pathlib.html), [GitHub Actions runner images](https://docs.github.com/en/actions/reference/runners/github-hosted-runners).

## 9. Errors and CLI behavior

Proposed families:
- `RequestError`: invalid user input, URL or arguments.
- `TransportError`: DNS/socket/connect failures.
- `TimeoutError`: network operation timed out.
- `TLSVerificationError`: failed TLS trust/hostname check.
- `HTTPProtocolError`: malformed HTTP/1.1 response.
- `ResponseLimitError`: size limit exceeded.

A valid HTTP 404 or 500 is still a `Response`, not a protocol error. A later `--check-status` option may make HTTP error statuses return nonzero CLI exit codes.

Errors go to stderr; ordinary result data goes to stdout. Avoid ANSI sequences when stdout is not a TTY or when `--no-color` is selected. `--output` should save unmodified response bytes, not highlighted text.

## 10. Presentation and CLI design

- Friendly pastel accents, restrained terminal layout, clear status and optional timing.
- Rich only in `presentation/` or the terminal-facing CLI; never in the protocol/transport.
- Simple commands should work without ASCII mascots or decorative banners.
- JSON prettification is optional and must not corrupt binary output.
- Exit status and pipe behavior should be deterministic.

## 11. Testing approach

- Unit tests: URL, headers, serializer, parser, framing and error mapping.
- Test responses split into many arbitrarily sized chunks; deliberately malformed responses.
- Integration tests: a local HTTP server that we control, no internet required.
- TLS tests: trusted local test certificate vs invalid/untrusted certificate.
- CLI tests: commands, stdout/stderr and exit codes.
- Test each protocol component before adding more convenience features.

`pytest` and `ruff` will be **development-only** dependencies managed by uv; this does not change the minimal runtime dependency policy.

## 12. Explicit non-goals for MVP

HTTP/2, HTTP/3, proxy support, HTTP connection pooling, WebSockets, HTTP pipelining, plugin systems, TUI, asynchronous requests, and a dependency-injection framework.

## 13. Architecture decision record

| ID | Decision | Why |
| --- | --- | --- |
| ADR-001 | Modular monolith | Small understandable boundaries |
| ADR-002 | Own HTTP/1.1 on socket + ssl | Learn network programming |
| ADR-003 | uv + stdlib + Rich at runtime | Reproducibility and few dependencies |
| ADR-004 | Sync first | Easier debugging |
| ADR-005 | CLI now, Python API later | Reusable core |
| ADR-006 | Bytes-first | Binary correctness |
| ADR-007 | Secure defaults and strict parser | Avoid unsafe protocol ambiguity |
| ADR-008 | Subtle pastel terminal theme | Recognizable but usable |
| ADR-009 | Native Windows, Linux and macOS support | Portable Python APIs, OS-independent HTTP core, three-OS CI |

See [roadmap](roadmap.md) for work order and [learning workflow](learning-workflow.md) for how to tackle issues.
