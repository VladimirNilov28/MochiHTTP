# 🍡 MochiHTTP

**A sweet little HTTP client for your terminal.**

MochiHTTP is a learning-first, open-source HTTP client written in Python. The terminal command will be **`mochi`**.

> **Status: planning / not implemented yet.** The commands shown in the docs are goals, not currently working features.

## Project decisions

- Python 3.13+ on Windows, Linux, and macOS (WSL2 supported)
- **uv** for project, environment and dependency management
- Own **HTTP/1.1** implementation using Python `socket` and `ssl`
- Python standard library + **Rich** as runtime dependencies
- Simple command-line interface and restrained pastel output
- A reusable Python API planned after the CLI MVP
- Cross-platform behavior validated by automated tests on Windows, Linux, and macOS (CI planned)

## Documentation

- [Architecture specification](docs/architecture.md) — design, module boundaries, protocol and safety rules
- [Command-driven CLI design](docs/cli-design.md) — explicit commands, declarative parser, auth/profile workflows
- [Roadmap](docs/roadmap.md) — incremental learning and implementation plan
- [Learning workflow](docs/learning-workflow.md) — how to work through the issues

## Start here

**[Issue #1 — Initialize the Python project with uv](https://github.com/VladimirNilov28/MochiHTTP/issues/1)**

Follow the issues in order. Each task describes the goal, a small checklist, acceptance criteria, and reference material without giving away the entire solution.

[View all issues](https://github.com/VladimirNilov28/MochiHTTP/issues)
