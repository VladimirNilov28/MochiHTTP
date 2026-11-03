# How we work on MochiHTTP

MochiHTTP is both an open-source tool and a hands-on Python learning project.

## One issue at a time

- Read the goal and acceptance criteria first.
- Make a tiny experiment to understand a new Python concept before integrating it.
- Write a minimal implementation. Avoid designing for features that are not requested yet.
- Run tests and check expected terminal output.
- If stuck, ask for an **explanation or hint first**, not a complete answer.
- Finish with a small pull request linked to the issue.

## Issue template (for future tasks)

### 🎯 Goal
One or two simple sentences: what and why.

### 📚 You will learn
A short list of Python concepts, explained in familiar terms where possible.

### 🛠️ Tasks
Small checkbox steps, in logical order.

### ✅ Done when
Observable commands, tests, output and edge cases.

### 📖 References
Links to relevant Python/uv docs, specific sections of RFCs, or short tutorials.

### 💡 Hints
Useful pointers *without copying a full implementation*.

## Python translation notes for Java/TypeScript developers

- Python modules are files; packages are directories designed for imports.
- `pyproject.toml` declares project metadata and dependencies.
- `uv` manages the environment, lockfile and commands; no need to manually activate a virtualenv for `uv run`.
- Prefer plain functions initially. Add dataclasses/classes when they make responsibilities clearer.
- Python type hints help maintainability but do not enforce types at runtime.
- Standard library first: `argparse`, `socket`, `ssl`, `json`, `dataclasses`.

## Coding habits

- Work on Windows, Linux, or macOS. On Windows, either use native PowerShell or WSL2; if using WSL2, keep the repo in the Linux filesystem for best tooling behavior.
- Prefer cross-platform Python commands (`uv run ...`) over shell-specific scripts; check terminal commands against your chosen shell.
- Test networking against localhost with ephemeral ports; don't assume a fixed port or rely on a public website.
- Once CI is introduced, check the Windows, Linux, and macOS jobs before merging.
- Add tests for each behavior, including failure cases.
- Separate stdout (result) from stderr (errors).
- Never skip TLS certificate verification by default.
- Do not commit secrets, tokens or local `.venv` files.
- Keep documentation accurate; mark planned commands and APIs as planned.

## Recommended learning materials

- [The Python Tutorial](https://docs.python.org/3/tutorial/)
- [Python modules and packages](https://docs.python.org/3/tutorial/modules.html)
- [Python argparse](https://docs.python.org/3/library/argparse.html)
- [uv: Working on projects](https://docs.astral.sh/uv/guides/projects/)
- [pytest getting started](https://docs.pytest.org/en/stable/getting-started.html)
- [Rich documentation](https://rich.readthedocs.io/en/stable/)
