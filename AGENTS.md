# Repository Guidelines

## Project Structure & Module Organization
- `app/main.py` composes the root FastMCP server and mounts tool namespaces.
- `app/core/` contains settings and shared configuration loading (`.env` + repo root `.env`).
- `app/clients/` holds backend HTTP client logic and auth header selection.
- `app/services/` implements analytics orchestration and response shaping.
- `app/tools/` registers MCP tools (`analysis_*`, `management_*`).
- `app/schemas/` defines structured payload models.
- `tests/` contains pytest suites for metadata, connectivity, and analytics behavior.
- `skills/` stores AI skill docs; keep runtime business logic in `app/`.

## Build, Test, and Development Commands
- `uv sync`: install/update dependencies into the local `.venv`.
- `uv run python -m app.main`: start the MCP service (default HTTP at `0.0.0.0:8090`).
- `MCP_TRANSPORT=stdio uv run python -m app.main`: run the service in stdio transport.
- `uv run pytest`: execute all tests.
- `uv run pytest tests/test_tool_metadata.py -q`: run a focused suite when changing tool definitions.

## Coding Style & Naming Conventions
- Target Python 3.12+, follow PEP 8, and use 4-space indentation.
- Keep lines within Ruff limit (`88` chars) and prefer small, single-responsibility functions.
- Use snake_case for files, functions, variables, and API/tool parameters (for example `top_limit`, `user_offset`).
- Keep tool naming consistent: namespace prefix + verb phrase (for example `analysis_get_daily_report_dataset`).

## Testing Guidelines
- Testing stack: `pytest` + `pytest-asyncio`.
- Name test files `test_*.py`; colocate assertions with the behavior under test.
- Add async coverage for tool contracts and parameter bounds (`ge`/`le` constraints).
- Integration-style tests require `BACKEND_ADMIN_API_KEY`; unit tests should mock HTTP calls with `monkeypatch`.

## Commit & Pull Request Guidelines
- This repository currently has no commit history; adopt Conventional Commits (`feat:`, `fix:`, `test:`, `docs:`).
- PRs should include: concise summary, affected modules, test evidence (`uv run pytest`), and env/config impact.
- Link related issues/tasks and include sample request/response when tool schemas or payloads change.

## Security & Configuration Tips
- Copy `.env.example` to `.env` for local setup; never commit real credentials.
- Prefer passing `BACKEND_ADMIN_API_KEY` / `BACKEND_GLOBAL_API_KEY` through MCP request headers.
- Use fallback env keys only for local direct-connect testing.
