# Repository Guidelines

## Project Structure & Module Organization

- `app/` contains the Python application: FastAPI entrypoints in `app/main.py`, configuration in `app/config.py`, conversation orchestration in `app/conversation/`, and integrations for LLM, speech-to-text, text-to-speech, audio, and realtime behavior in their respective subpackages.
- `frontend/` contains the browser clients: `participant/`, `human/`, `display/`, and `host/`, each with its own HTML, JavaScript, and CSS.
- `tests/` contains pytest unit and integration tests. `scripts/` contains startup, environment-check, and manual hardware/service smoke-test utilities.
- `models/` stores local Piper voice assets. Keep secrets in `.env`; do not commit credentials, recordings, or generated temporary files.

## Build, Test, and Development Commands

Use Python 3.12 and the repository environment. Install/sync dependencies with `uv sync` (or `uv sync --dev`). Run the test suite with:

```bash
uv run pytest
```

Run the setup checks before exercising hardware or external services:

```bash
source scripts/env.sh
uv run python scripts/check_setup.py
```

Start the local server with `./scripts/start.sh`, or directly with `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000`. The startup path expects CUDA, a configured microphone, Piper models, `DEEPSEEK_API_KEY`, and a running Cloudflare Tunnel.

## Coding Style & Naming Conventions

Follow standard Python style with four-space indentation, type hints, and `snake_case` for functions, variables, and modules; use `PascalCase` for classes and uppercase names for constants. Keep frontend JavaScript and CSS scoped to their page where practical. No formatter or linter is configured, so keep changes consistent with nearby code and ensure imports remain clean.

## Testing Guidelines

Tests use pytest and are discovered under `tests/` via `pyproject.toml`. Name files `test_*.py` and test functions `test_*`. Mark tests requiring external services with `@pytest.mark.integration`; run focused tests with, for example, `uv run pytest tests/test_conversation.py`. Some configuration tests require local models and `.env` values.

## Commit & Pull Request Guidelines

Existing commits are short, imperative-style descriptions (for example, `Display messages text-width`). Keep commits focused and describe the behavior changed. Pull requests should explain the user-visible or operational impact, list validation commands, identify hardware/external-service assumptions, and include screenshots for frontend changes. Never include API keys or private tunnel configuration.

## Security & Configuration Tips

Review `.env` and `scripts/env.sh` locally before running the app. Treat `/participant` as an operator-only interface because it can invoke the DeepSeek API. Use `/api/health` and `/docs` for local verification, and avoid exposing development credentials or debug artifacts through the public tunnel.
