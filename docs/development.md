# Development

## Prerequisites

- Python 3.12 or later
- [UV](https://github.com/astral-sh/uv) package manager
- Node.js 20 (for UI development)
- Git

## Setup

Clone the repository and install all dependencies including dev extras:

```bash
git clone https://github.com/your-org/asset-optimizer.git
cd asset-optimizer
uv sync
```

`uv sync` reads `pyproject.toml` and `uv.lock`, creates a virtual environment,
and installs both runtime and dev dependencies. No manual `pip install` or
`venv` creation required.

Copy the example env file and YAML config for local development:

```bash
cp .env.example .env
cp asset-optimizer.yaml.example asset-optimizer.yaml
```

Edit `.env` to add your API keys (preferred), or add them to `asset-optimizer.yaml`
using `${VAR}` interpolation.

## Running the Application

Start the API server with auto-reload:

```bash
uv run asset-optimizer serve --reload
```

Start the React UI in development mode (separate terminal):

```bash
cd ui
npm install
npm run dev
```

The UI dev server proxies API requests to `http://localhost:8000`.

## Running Tests

```bash
uv run pytest
```

Run with coverage:

```bash
uv run pytest --cov=asset_optimizer --cov-report=term-missing
```

Run a specific test file:

```bash
uv run pytest tests/unit/test_engine.py -v
uv run pytest tests/unit/test_config.py -v
```

Run tests matching a pattern:

```bash
uv run pytest -k "test_convergence" -v
```

Tests use `pytest-asyncio` with `asyncio_mode = "auto"` so async test functions
work without any decorator.

## Linting

```bash
uv run ruff check .
```

Auto-fix fixable issues:

```bash
uv run ruff check . --fix
```

Format code:

```bash
uv run ruff format .
```

The ruff configuration in `pyproject.toml` selects rules from: `E`, `F`, `I`
(isort), `N` (naming), `UP` (pyupgrade), `B` (bugbear), `A` (shadowing builtins),
`SIM` (simplify), `TCH` (type-checking imports).

## Type Checking

```bash
uv run mypy src/
```

Mypy runs in strict mode (`strict = true` in `pyproject.toml`). All public
functions must have fully annotated signatures. Use `TYPE_CHECKING` guards for
imports that are only needed for annotations.

## Project Conventions

### Test-Driven Development

New features and bug fixes must include tests written before the implementation.
The workflow is:

1. Write a failing test that captures the desired behavior
2. Implement the minimum code to make the test pass
3. Refactor if needed, keeping tests green
4. Run `uv run ruff check . && uv run mypy src/ && uv run pytest` before committing

### Running Example Scripts

The `examples/` directory contains runnable scripts that demonstrate the library:

```bash
# Image prompt enhancement (requires IMAGE_PROVIDER set in .env)
uv run python examples/img-prompt-enhancement/run_basic.py
```

### File Layout

- Source code lives in `src/asset_optimizer/`
- Tests mirror the source layout in `tests/`
- Evaluation YAML files go in `evaluations/`
- Asset files go in `assets/`
- Deployment files go in `deploy/`
- Example scripts go in `examples/`

### Import Style

- Use `from __future__ import annotations` at the top of every module
- Put type-only imports inside `if TYPE_CHECKING:` blocks
- Keep `__init__.py` files minimal — export only the public API surface

### Async

All I/O-bound code must be async. Use `asyncio.gather` for parallel operations.
Never use `time.sleep` in async code; use `asyncio.sleep` if needed.

### Error Handling

- Raise `ValueError` for invalid configuration or user input
- Raise `FileNotFoundError` for missing required files
- Let HTTP exceptions propagate from FastAPI route handlers using `HTTPException`
- Never swallow exceptions silently — log or re-raise

### Commit Style

Follow conventional commits:

```
feat: add Cohere text provider
fix: handle empty response from Gemini judge
docs: update provider configuration examples
test: add convergence strategy edge case tests
refactor: extract score aggregation into helper function
```

## Database Migrations

The project uses Alembic for schema migrations.

Generate a new migration after changing ORM models:

```bash
uv run alembic revision --autogenerate -m "add indexes to experiments table"
```

Apply pending migrations:

```bash
uv run alembic upgrade head
```

Rollback one migration:

```bash
uv run alembic downgrade -1
```

## Building the Docker Image

```bash
docker build -t asset-optimizer:dev .
```

The build runs `npm run build` for the UI and `uv sync --no-dev` for Python
dependencies. The final image is based on `python:3.12-slim`.

## CI Checks

Before opening a pull request, run the full check suite locally:

```bash
uv run ruff check . && \
uv run ruff format --check . && \
uv run mypy src/ && \
uv run pytest --cov=asset_optimizer
```

All four checks must pass with no errors or warnings.
