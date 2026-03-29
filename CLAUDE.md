# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Asset Optimizer — uses the autoimprove pattern to automatically optimize different asset types (prompts, skills, images). Dual-use: importable Python library and standalone service (CLI + API + web UI).

## Tech Stack

- **Language**: Python 3.12
- **Package Manager**: UV
- **Web Framework**: FastAPI (async)
- **ORM**: SQLAlchemy 2.0 (async sessions)
- **Migrations**: Alembic
- **CLI**: Typer
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Linting**: ruff
- **Type Checking**: mypy --strict
- **Testing**: pytest with pytest-asyncio and coverage

## Build & Run Commands

```bash
# Install dependencies
uv sync

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=asset_optimizer --cov-report=term-missing

# Run single test file
uv run pytest tests/unit/test_config.py -v

# Lint
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/

# Type check
uv run mypy src/asset_optimizer/

# Start API server
uv run asset-optimizer serve

# Run CLI
uv run asset-optimizer --help
```

## Architecture

- `src/asset_optimizer/core/` — Engine, experiment, iteration, convergence
- `src/asset_optimizer/assets/` — Asset type protocol and implementations
- `src/asset_optimizer/providers/` — AI provider abstraction (text + image)
- `src/asset_optimizer/scoring/` — Heuristic, AI-judged, composite scorers
- `src/asset_optimizer/storage/` — SQLAlchemy models, repository, migrations
- `src/asset_optimizer/api/` — FastAPI REST API + WebSocket
- `src/asset_optimizer/cli/` — Typer CLI
- `ui/` — React frontend (built assets served by API in production)

## Conventions

- All public functions must have type annotations
- Use async/await throughout the core engine
- Database access only through the repository layer
- TDD: write tests before implementation
- Follow existing patterns — check before adding new ones
