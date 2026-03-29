# Asset Optimizer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-oriented Python framework that formalizes the autoimprove pattern for automatically optimizing prompts, skills, and images — usable as a library, CLI, REST API, and web UI.

**Architecture:** Single Python package (`asset_optimizer`) with four entry points: importable library, Typer CLI, FastAPI REST API + WebSocket, and a React dashboard served by the API. SQLAlchemy 2.0 with async sessions provides storage (SQLite local, PostgreSQL production). The core engine runs an async optimize loop: load asset, score via composite scorers, improve via AI provider, repeat until convergence.

**Tech Stack:** Python 3.12, UV, FastAPI, SQLAlchemy 2.0, Alembic, Typer, Pydantic v2, httpx, React 18, TypeScript, Vite, Tailwind CSS, Recharts

**Spec:** `docs/superpowers/specs/2026-03-29-asset-optimizer-design.md`

---

## Phase 1: Foundation

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/asset_optimizer/__init__.py`
- Create: `src/asset_optimizer/py.typed`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Modify: `CLAUDE.md`
- Create: `dev-reports/TEMPLATE.md`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "asset-optimizer"
version = "0.1.0"
description = "Automatic asset optimization using the autoimprove pattern"
readme = "README.md"
requires-python = ">=3.12"
license = { text = "MIT" }
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "aiosqlite>=0.20.0",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "pyyaml>=6.0",
    "typer>=0.12.0",
    "rich>=13.0.0",
    "httpx>=0.27.0",
    "openai>=1.50.0",
    "anthropic>=0.40.0",
    "google-generativeai>=0.8.0",
    "websockets>=13.0",
]

[project.optional-dependencies]
dev = [
    "ruff>=0.8.0",
    "mypy>=1.13.0",
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
]

[project.scripts]
asset-optimizer = "asset_optimizer.cli.main:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/asset_optimizer"]

[tool.ruff]
target-version = "py312"
src = ["src"]

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "A", "SIM", "TCH"]

[tool.mypy]
strict = true
python_version = "3.12"
mypy_path = "src"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- [ ] **Step 2: Create package init and marker files**

`src/asset_optimizer/__init__.py`:
```python
"""Asset Optimizer — automatic asset optimization using the autoimprove pattern."""

__version__ = "0.1.0"
```

`src/asset_optimizer/py.typed`: (empty marker file for PEP 561)

`tests/__init__.py`: (empty)

- [ ] **Step 3: Create test conftest**

`tests/conftest.py`:
```python
from pathlib import Path

import pytest


@pytest.fixture
def tmp_asset_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for test assets."""
    assets = tmp_path / "assets"
    assets.mkdir()
    return assets


@pytest.fixture
def sample_prompt(tmp_asset_dir: Path) -> Path:
    """Create a sample prompt file for testing."""
    prompt_file = tmp_asset_dir / "test-prompt.txt"
    prompt_file.write_text("You are a helpful assistant.")
    return prompt_file
```

- [ ] **Step 4: Create dev reports template**

`dev-reports/TEMPLATE.md`:
```markdown
# Dev Report: {title}
**Date**: {date}
**Author**: {author}

## Summary
{1-2 sentence summary}

## Changes
{Bulleted list of what changed and why}

## Decisions
{Key decisions made and rationale}

## Metrics
{Tests added/modified, coverage changes, files changed}

## Next Steps
{What comes next}
```

- [ ] **Step 5: Update CLAUDE.md with build commands**

Replace the full contents of `CLAUDE.md` with:

```markdown
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
```

- [ ] **Step 6: Initialize UV and verify tooling**

Run: `uv sync`
Expected: Dependencies installed, `.venv` created.

Run: `uv run python -c "import asset_optimizer; print(asset_optimizer.__version__)"`
Expected: `0.1.0`

- [ ] **Step 7: Verify lint and type check pass on empty package**

Run: `uv run ruff check src/ tests/`
Expected: No errors.

Run: `uv run mypy src/asset_optimizer/`
Expected: Success.

- [ ] **Step 8: Commit**

```bash
git add pyproject.toml src/ tests/ dev-reports/ CLAUDE.md
git commit -m "feat: scaffold project with UV, pytest, ruff, mypy"
```

---

### Task 2: Configuration System

**Files:**
- Create: `src/asset_optimizer/config.py`
- Create: `tests/unit/__init__.py`
- Create: `tests/unit/test_config.py`
- Create: `asset-optimizer.yaml.example`

- [ ] **Step 1: Write failing tests for configuration**

`tests/unit/__init__.py`: (empty)

`tests/unit/test_config.py`:
```python
from pathlib import Path

import pytest
import yaml

from asset_optimizer.config import (
    AppConfig,
    DefaultsConfig,
    ServerConfig,
    StorageConfig,
    load_config,
)


def test_default_config_values() -> None:
    config = AppConfig()
    assert config.storage.backend == "sqlite"
    assert config.storage.sqlite_path == Path("./data/optimizer.db")
    assert config.server.host == "0.0.0.0"
    assert config.server.port == 8000
    assert config.defaults.max_iterations == 20
    assert config.defaults.min_improvement == 0.01
    assert config.defaults.convergence_strategy == "greedy"
    assert config.defaults.stagnation_limit == 5


def test_load_config_from_yaml(tmp_path: Path) -> None:
    config_data = {
        "storage": {"backend": "postgres", "postgres_url": "postgresql+asyncpg://localhost/test"},
        "server": {"port": 9000},
        "defaults": {"max_iterations": 50},
    }
    config_file = tmp_path / "asset-optimizer.yaml"
    config_file.write_text(yaml.dump(config_data))

    config = load_config(config_file)
    assert config.storage.backend == "postgres"
    assert config.storage.postgres_url == "postgresql+asyncpg://localhost/test"
    assert config.server.port == 9000
    assert config.defaults.max_iterations == 50


def test_load_config_missing_file_uses_defaults() -> None:
    config = load_config(Path("/nonexistent/config.yaml"))
    assert config.storage.backend == "sqlite"
    assert config.server.port == 8000


def test_storage_config_sqlite_defaults() -> None:
    config = StorageConfig()
    assert config.backend == "sqlite"
    assert config.sqlite_path == Path("./data/optimizer.db")
    assert config.postgres_url is None


def test_server_config_defaults() -> None:
    config = ServerConfig()
    assert config.host == "0.0.0.0"
    assert config.port == 8000


def test_defaults_config() -> None:
    config = DefaultsConfig(max_iterations=100, convergence_strategy="target")
    assert config.max_iterations == 100
    assert config.convergence_strategy == "target"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'asset_optimizer.config'`

- [ ] **Step 3: Implement configuration module**

`src/asset_optimizer/config.py`:
```python
"""Application configuration with YAML file and environment variable support."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


def _resolve_env_vars(value: str) -> str:
    """Replace ${VAR_NAME} patterns with environment variable values."""
    def replacer(match: re.Match[str]) -> str:
        var_name = match.group(1)
        return os.environ.get(var_name, match.group(0))
    return re.sub(r"\$\{(\w+)\}", replacer, value)


def _resolve_env_vars_in_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Recursively resolve environment variables in a config dict."""
    resolved: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, str):
            resolved[key] = _resolve_env_vars(value)
        elif isinstance(value, dict):
            resolved[key] = _resolve_env_vars_in_dict(value)
        else:
            resolved[key] = value
    return resolved


class StorageConfig(BaseModel):
    """Database storage configuration."""

    backend: str = "sqlite"
    sqlite_path: Path = Path("./data/optimizer.db")
    postgres_url: str | None = None


class ProviderEntry(BaseModel):
    """Single provider configuration entry."""

    api_key: str | None = None
    model: str | None = None
    base_url: str | None = None
    endpoint: str | None = None


class ProvidersConfig(BaseModel):
    """AI provider configuration."""

    text: dict[str, Any] = {}
    image: dict[str, Any] = {}


class ServerConfig(BaseModel):
    """API server configuration."""

    host: str = "0.0.0.0"
    port: int = 8000


class DefaultsConfig(BaseModel):
    """Default optimization parameters."""

    max_iterations: int = 20
    min_improvement: float = 0.01
    convergence_strategy: str = "greedy"
    stagnation_limit: int = 5


class AppConfig(BaseModel):
    """Root application configuration."""

    storage: StorageConfig = StorageConfig()
    providers: ProvidersConfig = ProvidersConfig()
    server: ServerConfig = ServerConfig()
    defaults: DefaultsConfig = DefaultsConfig()


def load_config(path: Path | None = None) -> AppConfig:
    """Load configuration from a YAML file, falling back to defaults.

    Supports ${ENV_VAR} interpolation in string values.
    """
    if path is None:
        path = Path("asset-optimizer.yaml")

    if not path.exists():
        return AppConfig()

    raw = yaml.safe_load(path.read_text()) or {}
    resolved = _resolve_env_vars_in_dict(raw)
    return AppConfig(**resolved)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_config.py -v`
Expected: All 6 tests PASS.

- [ ] **Step 5: Create example config file**

`asset-optimizer.yaml.example`:
```yaml
# Asset Optimizer Configuration
# Copy to asset-optimizer.yaml and customize.
# Supports ${ENV_VAR} interpolation for secrets.

storage:
  backend: sqlite                    # sqlite | postgres
  sqlite_path: ./data/optimizer.db
  # postgres_url: ${DATABASE_URL}

providers:
  text:
    default: claude
    claude:
      api_key: ${ANTHROPIC_API_KEY}
      model: claude-sonnet-4-20250514
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o
    # vllm:
    #   base_url: http://localhost:8000/v1
    #   model: meta-llama/Llama-3-70B
    # ollama:
    #   base_url: http://localhost:11434/v1
    #   model: llama3
  image:
    default: openai_image
    openai_image:
      api_key: ${OPENAI_API_KEY}
      model: image-01
    # nano_banana:
    #   api_key: ${NANO_BANANA_API_KEY}
    #   endpoint: https://api.nanobanana.com/v1

server:
  host: 0.0.0.0
  port: 8000

defaults:
  max_iterations: 20
  min_improvement: 0.01
  convergence_strategy: greedy       # greedy | target | budget
  stagnation_limit: 5
```

- [ ] **Step 6: Run lint and type check**

Run: `uv run ruff check src/ tests/ && uv run mypy src/asset_optimizer/`
Expected: No errors.

- [ ] **Step 7: Commit**

```bash
git add src/asset_optimizer/config.py tests/unit/ asset-optimizer.yaml.example
git commit -m "feat: add configuration system with YAML and env var support"
```

---

### Task 3: Database Models & Storage

**Files:**
- Create: `src/asset_optimizer/storage/__init__.py`
- Create: `src/asset_optimizer/storage/models.py`
- Create: `src/asset_optimizer/storage/database.py`
- Create: `src/asset_optimizer/storage/repository.py`
- Create: `tests/unit/test_models.py`
- Create: `tests/unit/test_repository.py`

- [ ] **Step 1: Write failing tests for SQLAlchemy models**

`tests/unit/test_models.py`:
```python
import uuid
from datetime import datetime, timezone

from asset_optimizer.storage.models import (
    AssetVersion,
    AssetVersionRole,
    Evaluation,
    Experiment,
    ExperimentStatus,
    Iteration,
    IterationStatus,
    Score,
    ScorerType,
)


def test_experiment_model_fields() -> None:
    exp_id = uuid.uuid4()
    eval_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    exp = Experiment(
        id=exp_id,
        name="Test Experiment",
        description="A test",
        asset_type="prompt",
        evaluation_id=eval_id,
        provider_config={"text": {"default": "openai"}},
        status=ExperimentStatus.PENDING,
        config={"max_iterations": 10},
        best_score=None,
        created_at=now,
        updated_at=now,
    )
    assert exp.name == "Test Experiment"
    assert exp.status == ExperimentStatus.PENDING
    assert exp.asset_type == "prompt"


def test_iteration_model_fields() -> None:
    it = Iteration(
        id=uuid.uuid4(),
        experiment_id=uuid.uuid4(),
        number=1,
        status=IterationStatus.IMPROVED,
        strategy_used="default",
        improvement_prompt="Improve clarity",
        feedback="Better structure",
        created_at=datetime.now(timezone.utc),
        duration_ms=1500,
    )
    assert it.number == 1
    assert it.status == IterationStatus.IMPROVED


def test_asset_version_model_fields() -> None:
    av = AssetVersion(
        id=uuid.uuid4(),
        iteration_id=uuid.uuid4(),
        role=AssetVersionRole.OUTPUT,
        content="Improved prompt text",
        file_path=None,
        metadata_={},
        created_at=datetime.now(timezone.utc),
    )
    assert av.role == AssetVersionRole.OUTPUT
    assert av.content == "Improved prompt text"


def test_evaluation_model_fields() -> None:
    ev = Evaluation(
        id=uuid.uuid4(),
        name="prompt-clarity",
        asset_type="prompt",
        criteria=[{"name": "clarity", "max_score": 10}],
        scorer_config={"type": "composite"},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    assert ev.name == "prompt-clarity"
    assert len(ev.criteria) == 1


def test_score_model_fields() -> None:
    sc = Score(
        id=uuid.uuid4(),
        iteration_id=uuid.uuid4(),
        criterion_name="clarity",
        value=7.5,
        max_value=10.0,
        scorer_type=ScorerType.AI_JUDGE,
        details={"reasoning": "Clear and specific"},
        created_at=datetime.now(timezone.utc),
    )
    assert sc.value == 7.5
    assert sc.scorer_type == ScorerType.AI_JUDGE


def test_experiment_status_enum() -> None:
    assert ExperimentStatus.PENDING.value == "pending"
    assert ExperimentStatus.RUNNING.value == "running"
    assert ExperimentStatus.COMPLETED.value == "completed"
    assert ExperimentStatus.FAILED.value == "failed"
    assert ExperimentStatus.CANCELLED.value == "cancelled"
    assert ExperimentStatus.PAUSED.value == "paused"


def test_iteration_status_enum() -> None:
    assert IterationStatus.RUNNING.value == "running"
    assert IterationStatus.IMPROVED.value == "improved"
    assert IterationStatus.NO_IMPROVEMENT.value == "no_improvement"
    assert IterationStatus.ERROR.value == "error"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement SQLAlchemy models**

`src/asset_optimizer/storage/__init__.py`:
```python
"""Storage layer — database models, sessions, and repository."""
```

`src/asset_optimizer/storage/models.py`:
```python
"""SQLAlchemy ORM models for all persistent entities."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, Enum, Float, Integer, String, Text, Uuid
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    type_annotation_map = {
        dict[str, Any]: JSON,
        list[dict[str, Any]]: JSON,
    }


class ExperimentStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IterationStatus(str, enum.Enum):
    RUNNING = "running"
    IMPROVED = "improved"
    NO_IMPROVEMENT = "no_improvement"
    ERROR = "error"


class AssetVersionRole(str, enum.Enum):
    INPUT = "input"
    OUTPUT = "output"


class ScorerType(str, enum.Enum):
    HEURISTIC = "heuristic"
    AI_JUDGE = "ai_judge"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_uuid() -> uuid.UUID:
    return uuid.uuid4()


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_new_uuid)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    asset_type: Mapped[str] = mapped_column(String(50))
    evaluation_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    provider_config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[ExperimentStatus] = mapped_column(
        Enum(ExperimentStatus), default=ExperimentStatus.PENDING
    )
    config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    best_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class Iteration(Base):
    __tablename__ = "iterations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_new_uuid)
    experiment_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    number: Mapped[int] = mapped_column(Integer)
    status: Mapped[IterationStatus] = mapped_column(Enum(IterationStatus))
    strategy_used: Mapped[str] = mapped_column(String(100), default="default")
    improvement_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)


class AssetVersion(Base):
    __tablename__ = "asset_versions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_new_uuid)
    iteration_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    role: Mapped[AssetVersionRole] = mapped_column(Enum(AssetVersionRole))
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_new_uuid)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    asset_type: Mapped[str] = mapped_column(String(50))
    criteria: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    scorer_config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_new_uuid)
    iteration_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    criterion_name: Mapped[str] = mapped_column(String(100))
    value: Mapped[float] = mapped_column(Float)
    max_value: Mapped[float] = mapped_column(Float, default=10.0)
    scorer_type: Mapped[ScorerType] = mapped_column(Enum(ScorerType))
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
```

- [ ] **Step 4: Run model tests to verify they pass**

Run: `uv run pytest tests/unit/test_models.py -v`
Expected: All 7 tests PASS.

- [ ] **Step 5: Write failing tests for database session and repository**

`tests/unit/test_repository.py`:
```python
import uuid

import pytest

from asset_optimizer.storage.database import create_engine_from_config, get_session_factory
from asset_optimizer.storage.models import (
    Evaluation,
    Experiment,
    ExperimentStatus,
    Iteration,
    IterationStatus,
    Score,
    ScorerType,
)
from asset_optimizer.storage.repository import Repository


@pytest.fixture
async def repo(tmp_path):
    db_path = tmp_path / "test.db"
    engine = create_engine_from_config("sqlite", sqlite_path=db_path)
    session_factory = get_session_factory(engine)

    from asset_optimizer.storage.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        yield Repository(session)

    await engine.dispose()


async def test_create_and_get_evaluation(repo: Repository) -> None:
    evaluation = Evaluation(
        name="test-eval",
        asset_type="prompt",
        criteria=[{"name": "clarity", "max_score": 10}],
        scorer_config={"type": "composite"},
    )
    created = await repo.create_evaluation(evaluation)
    assert created.id is not None

    fetched = await repo.get_evaluation(created.id)
    assert fetched is not None
    assert fetched.name == "test-eval"


async def test_list_evaluations(repo: Repository) -> None:
    for i in range(3):
        await repo.create_evaluation(
            Evaluation(name=f"eval-{i}", asset_type="prompt", criteria=[], scorer_config={})
        )
    evaluations = await repo.list_evaluations()
    assert len(evaluations) == 3


async def test_create_and_get_experiment(repo: Repository) -> None:
    eval_id = uuid.uuid4()
    experiment = Experiment(
        name="test-exp",
        asset_type="prompt",
        evaluation_id=eval_id,
        config={"max_iterations": 10},
    )
    created = await repo.create_experiment(experiment)
    assert created.status == ExperimentStatus.PENDING

    fetched = await repo.get_experiment(created.id)
    assert fetched is not None
    assert fetched.name == "test-exp"


async def test_update_experiment_status(repo: Repository) -> None:
    experiment = Experiment(
        name="status-test",
        asset_type="prompt",
        evaluation_id=uuid.uuid4(),
    )
    created = await repo.create_experiment(experiment)
    updated = await repo.update_experiment_status(created.id, ExperimentStatus.RUNNING)
    assert updated.status == ExperimentStatus.RUNNING


async def test_list_experiments_with_status_filter(repo: Repository) -> None:
    for i, status in enumerate([ExperimentStatus.PENDING, ExperimentStatus.RUNNING, ExperimentStatus.PENDING]):
        exp = Experiment(
            name=f"exp-{i}", asset_type="prompt", evaluation_id=uuid.uuid4(), status=status
        )
        await repo.create_experiment(exp)

    pending = await repo.list_experiments(status=ExperimentStatus.PENDING)
    assert len(pending) == 2

    running = await repo.list_experiments(status=ExperimentStatus.RUNNING)
    assert len(running) == 1


async def test_create_and_list_iterations(repo: Repository) -> None:
    exp_id = uuid.uuid4()
    for i in range(3):
        await repo.create_iteration(
            Iteration(experiment_id=exp_id, number=i + 1, status=IterationStatus.IMPROVED)
        )
    iterations = await repo.list_iterations(exp_id)
    assert len(iterations) == 3
    assert iterations[0].number == 1


async def test_create_and_list_scores(repo: Repository) -> None:
    iter_id = uuid.uuid4()
    await repo.create_score(
        Score(iteration_id=iter_id, criterion_name="clarity", value=7.5, max_value=10.0, scorer_type=ScorerType.AI_JUDGE)
    )
    await repo.create_score(
        Score(iteration_id=iter_id, criterion_name="specificity", value=6.0, max_value=10.0, scorer_type=ScorerType.HEURISTIC)
    )
    scores = await repo.list_scores(iter_id)
    assert len(scores) == 2
```

- [ ] **Step 6: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_repository.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 7: Implement database session management**

`src/asset_optimizer/storage/database.py`:
```python
"""Database engine and session factory management."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_engine_from_config(
    backend: str = "sqlite",
    sqlite_path: Path | None = None,
    postgres_url: str | None = None,
) -> AsyncEngine:
    """Create an async SQLAlchemy engine from configuration."""
    if backend == "postgres" and postgres_url:
        url = postgres_url
    else:
        path = sqlite_path or Path("./data/optimizer.db")
        path.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite+aiosqlite:///{path}"

    return create_async_engine(url, echo=False)


def get_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create a session factory bound to the given engine."""
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

- [ ] **Step 8: Implement repository**

`src/asset_optimizer/storage/repository.py`:
```python
"""Data access layer — all database operations go through this class."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from asset_optimizer.storage.models import (
    AssetVersion,
    Evaluation,
    Experiment,
    ExperimentStatus,
    Iteration,
    Score,
)


class Repository:
    """Unified data access layer for all storage operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # --- Evaluations ---

    async def create_evaluation(self, evaluation: Evaluation) -> Evaluation:
        self._session.add(evaluation)
        await self._session.commit()
        await self._session.refresh(evaluation)
        return evaluation

    async def get_evaluation(self, evaluation_id: uuid.UUID) -> Evaluation | None:
        return await self._session.get(Evaluation, evaluation_id)

    async def get_evaluation_by_name(self, name: str) -> Evaluation | None:
        stmt = select(Evaluation).where(Evaluation.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_evaluations(self, asset_type: str | None = None) -> list[Evaluation]:
        stmt = select(Evaluation).order_by(Evaluation.created_at.desc())
        if asset_type:
            stmt = stmt.where(Evaluation.asset_type == asset_type)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_evaluation(self, evaluation: Evaluation) -> Evaluation:
        evaluation.updated_at = datetime.now(timezone.utc)
        await self._session.commit()
        await self._session.refresh(evaluation)
        return evaluation

    async def delete_evaluation(self, evaluation_id: uuid.UUID) -> bool:
        evaluation = await self.get_evaluation(evaluation_id)
        if evaluation is None:
            return False
        await self._session.delete(evaluation)
        await self._session.commit()
        return True

    # --- Experiments ---

    async def create_experiment(self, experiment: Experiment) -> Experiment:
        self._session.add(experiment)
        await self._session.commit()
        await self._session.refresh(experiment)
        return experiment

    async def get_experiment(self, experiment_id: uuid.UUID) -> Experiment | None:
        return await self._session.get(Experiment, experiment_id)

    async def list_experiments(
        self,
        status: ExperimentStatus | None = None,
        asset_type: str | None = None,
    ) -> list[Experiment]:
        stmt = select(Experiment).order_by(Experiment.created_at.desc())
        if status:
            stmt = stmt.where(Experiment.status == status)
        if asset_type:
            stmt = stmt.where(Experiment.asset_type == asset_type)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_experiment_status(
        self, experiment_id: uuid.UUID, status: ExperimentStatus
    ) -> Experiment:
        experiment = await self.get_experiment(experiment_id)
        if experiment is None:
            raise ValueError(f"Experiment {experiment_id} not found")
        experiment.status = status
        experiment.updated_at = datetime.now(timezone.utc)
        await self._session.commit()
        await self._session.refresh(experiment)
        return experiment

    async def update_experiment_best_score(
        self, experiment_id: uuid.UUID, score: float
    ) -> Experiment:
        experiment = await self.get_experiment(experiment_id)
        if experiment is None:
            raise ValueError(f"Experiment {experiment_id} not found")
        experiment.best_score = score
        experiment.updated_at = datetime.now(timezone.utc)
        await self._session.commit()
        await self._session.refresh(experiment)
        return experiment

    async def delete_experiment(self, experiment_id: uuid.UUID) -> bool:
        experiment = await self.get_experiment(experiment_id)
        if experiment is None:
            return False
        await self._session.delete(experiment)
        await self._session.commit()
        return True

    # --- Iterations ---

    async def create_iteration(self, iteration: Iteration) -> Iteration:
        self._session.add(iteration)
        await self._session.commit()
        await self._session.refresh(iteration)
        return iteration

    async def get_iteration(
        self, experiment_id: uuid.UUID, number: int
    ) -> Iteration | None:
        stmt = select(Iteration).where(
            Iteration.experiment_id == experiment_id,
            Iteration.number == number,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_iterations(self, experiment_id: uuid.UUID) -> list[Iteration]:
        stmt = (
            select(Iteration)
            .where(Iteration.experiment_id == experiment_id)
            .order_by(Iteration.number)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_iteration(self, iteration: Iteration) -> Iteration:
        await self._session.commit()
        await self._session.refresh(iteration)
        return iteration

    # --- Asset Versions ---

    async def create_asset_version(self, asset_version: AssetVersion) -> AssetVersion:
        self._session.add(asset_version)
        await self._session.commit()
        await self._session.refresh(asset_version)
        return asset_version

    async def list_asset_versions(self, iteration_id: uuid.UUID) -> list[AssetVersion]:
        stmt = (
            select(AssetVersion)
            .where(AssetVersion.iteration_id == iteration_id)
            .order_by(AssetVersion.role)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # --- Scores ---

    async def create_score(self, score: Score) -> Score:
        self._session.add(score)
        await self._session.commit()
        await self._session.refresh(score)
        return score

    async def list_scores(self, iteration_id: uuid.UUID) -> list[Score]:
        stmt = (
            select(Score)
            .where(Score.iteration_id == iteration_id)
            .order_by(Score.criterion_name)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
```

- [ ] **Step 9: Run repository tests to verify they pass**

Run: `uv run pytest tests/unit/test_repository.py -v`
Expected: All 7 tests PASS.

- [ ] **Step 10: Run full test suite, lint, and type check**

Run: `uv run pytest tests/ -v && uv run ruff check src/ tests/ && uv run mypy src/asset_optimizer/`
Expected: All tests pass, no lint or type errors.

- [ ] **Step 11: Commit**

```bash
git add src/asset_optimizer/storage/ tests/unit/test_models.py tests/unit/test_repository.py
git commit -m "feat: add database models and repository layer"
```

---

## Phase 2: Domain Layer

### Task 4: Asset Type System

**Files:**
- Create: `src/asset_optimizer/assets/__init__.py`
- Create: `src/asset_optimizer/assets/base.py`
- Create: `src/asset_optimizer/assets/registry.py`
- Create: `src/asset_optimizer/assets/prompt.py`
- Create: `src/asset_optimizer/assets/skill.py`
- Create: `src/asset_optimizer/assets/image.py`
- Create: `tests/unit/test_assets.py`

- [ ] **Step 1: Write failing tests for asset type system**

`tests/unit/test_assets.py`:
```python
from pathlib import Path

from asset_optimizer.assets.base import AssetContent
from asset_optimizer.assets.image import ImageAssetType
from asset_optimizer.assets.prompt import PromptAssetType
from asset_optimizer.assets.registry import AssetRegistry
from asset_optimizer.assets.skill import SkillAssetType


class TestAssetContent:
    def test_text_content(self) -> None:
        content = AssetContent(text="Hello world")
        assert content.text == "Hello world"
        assert content.file_path is None

    def test_file_content(self) -> None:
        content = AssetContent(file_path=Path("/tmp/image.png"))
        assert content.text is None
        assert content.file_path == Path("/tmp/image.png")

    def test_metadata(self) -> None:
        content = AssetContent(text="test", metadata={"key": "value"})
        assert content.metadata["key"] == "value"


class TestPromptAssetType:
    def test_name_and_extensions(self) -> None:
        asset_type = PromptAssetType()
        assert asset_type.name == "prompt"
        assert ".txt" in asset_type.file_extensions
        assert ".md" in asset_type.file_extensions

    def test_load_and_save(self, tmp_path: Path) -> None:
        asset_type = PromptAssetType()
        path = tmp_path / "prompt.txt"
        path.write_text("You are a helpful assistant.")

        content = asset_type.load(path)
        assert content.text == "You are a helpful assistant."

        new_path = tmp_path / "prompt2.txt"
        asset_type.save(content, new_path)
        assert new_path.read_text() == "You are a helpful assistant."

    def test_validate_nonempty(self) -> None:
        asset_type = PromptAssetType()
        errors = asset_type.validate(AssetContent(text="Valid prompt"))
        assert errors == []

    def test_validate_empty(self) -> None:
        asset_type = PromptAssetType()
        errors = asset_type.validate(AssetContent(text=""))
        assert len(errors) > 0

    def test_render_for_prompt(self) -> None:
        asset_type = PromptAssetType()
        content = AssetContent(text="Test prompt")
        rendered = asset_type.render_for_prompt(content)
        assert "Test prompt" in rendered

    def test_default_evaluation(self) -> None:
        asset_type = PromptAssetType()
        eval_config = asset_type.default_evaluation()
        assert eval_config["asset_type"] == "prompt"
        assert len(eval_config["criteria"]) > 0


class TestSkillAssetType:
    def test_name_and_extensions(self) -> None:
        asset_type = SkillAssetType()
        assert asset_type.name == "skill"
        assert ".md" in asset_type.file_extensions

    def test_load_skill_with_frontmatter(self, tmp_path: Path) -> None:
        skill_content = "---\nname: test-skill\ndescription: A test\n---\n\n# Skill Body\nDo things."
        path = tmp_path / "skill.md"
        path.write_text(skill_content)

        asset_type = SkillAssetType()
        content = asset_type.load(path)
        assert content.text is not None
        assert "Skill Body" in content.text
        assert content.metadata.get("name") == "test-skill"

    def test_validate_missing_frontmatter(self) -> None:
        asset_type = SkillAssetType()
        content = AssetContent(text="No frontmatter here")
        errors = asset_type.validate(content)
        assert len(errors) > 0


class TestImageAssetType:
    def test_name_and_extensions(self) -> None:
        asset_type = ImageAssetType()
        assert asset_type.name == "image"
        assert ".txt" in asset_type.file_extensions

    def test_load_image_prompt(self, tmp_path: Path) -> None:
        path = tmp_path / "image-prompt.txt"
        path.write_text("A sunset over mountains, oil painting style")

        asset_type = ImageAssetType()
        content = asset_type.load(path)
        assert content.text == "A sunset over mountains, oil painting style"

    def test_validate_nonempty(self) -> None:
        asset_type = ImageAssetType()
        errors = asset_type.validate(AssetContent(text="A cat"))
        assert errors == []


class TestAssetRegistry:
    def test_register_and_get(self) -> None:
        registry = AssetRegistry()
        prompt_type = PromptAssetType()
        registry.register_type(prompt_type)
        assert registry.get("prompt") is prompt_type

    def test_get_unknown_returns_none(self) -> None:
        registry = AssetRegistry()
        assert registry.get("unknown") is None

    def test_list_registered(self) -> None:
        registry = AssetRegistry()
        registry.register_type(PromptAssetType())
        registry.register_type(SkillAssetType())
        names = registry.list_types()
        assert "prompt" in names
        assert "skill" in names

    def test_decorator_registration(self) -> None:
        registry = AssetRegistry()

        @registry.register_decorator("custom")
        class CustomType:
            name = "custom"
            file_extensions = [".custom"]
            def load(self, path):
                return AssetContent(text=path.read_text())
            def save(self, content, path):
                path.write_text(content.text or "")
            def validate(self, content):
                return []
            def default_evaluation(self):
                return {"asset_type": "custom", "criteria": []}
            def render_for_prompt(self, content):
                return content.text or ""

        assert registry.get("custom") is not None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_assets.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement base types**

`src/asset_optimizer/assets/__init__.py`:
```python
"""Asset type system — protocols, registry, and built-in types."""

from asset_optimizer.assets.base import AssetContent
from asset_optimizer.assets.registry import AssetRegistry

__all__ = ["AssetContent", "AssetRegistry"]
```

`src/asset_optimizer/assets/base.py`:
```python
"""Base types and protocol for asset types."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass
class AssetContent:
    """Content container for any asset type."""

    text: str | None = None
    file_path: Path | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AssetTypeProtocol(Protocol):
    """Protocol that all asset types must implement."""

    name: str
    file_extensions: list[str]

    def load(self, path: Path) -> AssetContent: ...
    def save(self, content: AssetContent, path: Path) -> None: ...
    def validate(self, content: AssetContent) -> list[str]: ...
    def default_evaluation(self) -> dict[str, Any]: ...
    def render_for_prompt(self, content: AssetContent) -> str: ...
```

- [ ] **Step 4: Implement registry**

`src/asset_optimizer/assets/registry.py`:
```python
"""Asset type registry for discovering and managing asset types."""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from asset_optimizer.assets.base import AssetTypeProtocol

T = TypeVar("T")


class AssetRegistry:
    """Registry for asset type implementations."""

    def __init__(self) -> None:
        self._types: dict[str, AssetTypeProtocol] = {}

    def register_type(self, asset_type: AssetTypeProtocol) -> None:
        """Register an asset type instance."""
        self._types[asset_type.name] = asset_type

    def register_decorator(self, name: str) -> Callable[[type[T]], type[T]]:
        """Decorator for registering asset type classes."""
        def decorator(cls: type[T]) -> type[T]:
            instance: Any = cls()
            self._types[name] = instance
            return cls
        return decorator

    def get(self, name: str) -> AssetTypeProtocol | None:
        """Get an asset type by name."""
        return self._types.get(name)

    def list_types(self) -> list[str]:
        """List all registered asset type names."""
        return list(self._types.keys())


# Global default registry with built-in types
default_registry = AssetRegistry()
```

- [ ] **Step 5: Implement prompt asset type**

`src/asset_optimizer/assets/prompt.py`:
```python
"""Prompt asset type — optimizes text prompts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from asset_optimizer.assets.base import AssetContent


class PromptAssetType:
    """Asset type for text prompts (system prompts, user prompts, templates)."""

    name: str = "prompt"
    file_extensions: list[str] = [".txt", ".md", ".prompt"]

    def load(self, path: Path) -> AssetContent:
        return AssetContent(text=path.read_text(encoding="utf-8"))

    def save(self, content: AssetContent, path: Path) -> None:
        path.write_text(content.text or "", encoding="utf-8")

    def validate(self, content: AssetContent) -> list[str]:
        errors: list[str] = []
        if not content.text or not content.text.strip():
            errors.append("Prompt content must not be empty")
        return errors

    def default_evaluation(self) -> dict[str, Any]:
        return {
            "asset_type": "prompt",
            "criteria": [
                {
                    "name": "clarity",
                    "description": "Is the prompt unambiguous and easy to understand?",
                    "max_score": 10,
                    "rubric": (
                        "1-3: Vague, multiple interpretations possible\n"
                        "4-6: Mostly clear but some ambiguity\n"
                        "7-9: Clear and specific\n"
                        "10: Crystal clear, no room for misinterpretation"
                    ),
                },
                {
                    "name": "specificity",
                    "description": "Does the prompt include specific, actionable instructions?",
                    "max_score": 10,
                    "rubric": (
                        "1-3: Generic instructions, no concrete guidance\n"
                        "4-6: Some specifics but leaves gaps\n"
                        "7-9: Detailed, actionable instructions\n"
                        "10: Exhaustively specific with examples"
                    ),
                },
                {
                    "name": "effectiveness",
                    "description": "Would this prompt reliably produce the desired output?",
                    "max_score": 10,
                    "rubric": (
                        "1-3: Unreliable, inconsistent results expected\n"
                        "4-6: Sometimes produces desired output\n"
                        "7-9: Reliably produces good output\n"
                        "10: Consistently produces excellent output"
                    ),
                },
            ],
            "scorer_config": {
                "type": "composite",
                "heuristic_weight": 0.2,
                "ai_judge_weight": 0.8,
            },
        }

    def render_for_prompt(self, content: AssetContent) -> str:
        return f"```\n{content.text}\n```"
```

- [ ] **Step 6: Implement skill asset type**

`src/asset_optimizer/assets/skill.py`:
```python
"""Skill asset type — optimizes Claude Code skill files (markdown with frontmatter)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from asset_optimizer.assets.base import AssetContent


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse YAML frontmatter from markdown. Returns (frontmatter_dict, body)."""
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    frontmatter_raw = parts[1].strip()
    body = parts[2].strip()

    metadata: dict[str, str] = {}
    for line in frontmatter_raw.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            metadata[key.strip()] = value.strip()

    return metadata, body


class SkillAssetType:
    """Asset type for Claude Code skill files (markdown with YAML frontmatter)."""

    name: str = "skill"
    file_extensions: list[str] = [".md"]

    def load(self, path: Path) -> AssetContent:
        raw = path.read_text(encoding="utf-8")
        metadata, body = _parse_frontmatter(raw)
        return AssetContent(text=raw, metadata=metadata)

    def save(self, content: AssetContent, path: Path) -> None:
        path.write_text(content.text or "", encoding="utf-8")

    def validate(self, content: AssetContent) -> list[str]:
        errors: list[str] = []
        text = content.text or ""
        if not text.strip():
            errors.append("Skill content must not be empty")
            return errors
        if not text.startswith("---"):
            errors.append("Skill must have YAML frontmatter (start with ---)")
        else:
            metadata, _ = _parse_frontmatter(text)
            if "name" not in metadata:
                errors.append("Skill frontmatter must include 'name'")
            if "description" not in metadata:
                errors.append("Skill frontmatter must include 'description'")
        return errors

    def default_evaluation(self) -> dict[str, Any]:
        return {
            "asset_type": "skill",
            "criteria": [
                {
                    "name": "structure",
                    "description": "Does the skill have proper frontmatter and clear sections?",
                    "max_score": 10,
                },
                {
                    "name": "completeness",
                    "description": "Does the skill cover all necessary instructions and edge cases?",
                    "max_score": 10,
                },
                {
                    "name": "clarity",
                    "description": "Are instructions unambiguous and easy to follow?",
                    "max_score": 10,
                },
                {
                    "name": "actionability",
                    "description": "Can a developer follow the skill without additional context?",
                    "max_score": 10,
                },
            ],
            "scorer_config": {
                "type": "composite",
                "heuristic_weight": 0.3,
                "ai_judge_weight": 0.7,
            },
        }

    def render_for_prompt(self, content: AssetContent) -> str:
        return f"```markdown\n{content.text}\n```"
```

- [ ] **Step 7: Implement image asset type**

`src/asset_optimizer/assets/image.py`:
```python
"""Image asset type — optimizes image generation prompts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from asset_optimizer.assets.base import AssetContent


class ImageAssetType:
    """Asset type for image generation prompts.

    Optimizes the text prompt used to generate images.
    The generated image is stored as a side artifact for scoring.
    """

    name: str = "image"
    file_extensions: list[str] = [".txt", ".prompt"]

    def load(self, path: Path) -> AssetContent:
        return AssetContent(text=path.read_text(encoding="utf-8"))

    def save(self, content: AssetContent, path: Path) -> None:
        path.write_text(content.text or "", encoding="utf-8")

    def validate(self, content: AssetContent) -> list[str]:
        errors: list[str] = []
        if not content.text or not content.text.strip():
            errors.append("Image generation prompt must not be empty")
        if content.text and len(content.text) > 4000:
            errors.append("Image generation prompt exceeds 4000 character limit")
        return errors

    def default_evaluation(self) -> dict[str, Any]:
        return {
            "asset_type": "image",
            "criteria": [
                {
                    "name": "prompt_specificity",
                    "description": "Does the prompt clearly describe the desired image?",
                    "max_score": 10,
                },
                {
                    "name": "prompt_style",
                    "description": "Does the prompt include style, mood, and composition guidance?",
                    "max_score": 10,
                },
                {
                    "name": "image_quality",
                    "description": "Is the generated image high quality and visually appealing?",
                    "max_score": 10,
                },
                {
                    "name": "image_relevance",
                    "description": "Does the generated image match the prompt intent?",
                    "max_score": 10,
                },
            ],
            "scorer_config": {
                "type": "composite",
                "heuristic_weight": 0.1,
                "ai_judge_weight": 0.9,
            },
        }

    def render_for_prompt(self, content: AssetContent) -> str:
        return f"Image generation prompt:\n```\n{content.text}\n```"
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_assets.py -v`
Expected: All tests PASS.

- [ ] **Step 9: Run full suite, lint, type check**

Run: `uv run pytest tests/ -v && uv run ruff check src/ tests/ && uv run mypy src/asset_optimizer/`
Expected: All pass.

- [ ] **Step 10: Commit**

```bash
git add src/asset_optimizer/assets/ tests/unit/test_assets.py
git commit -m "feat: add asset type system with prompt, skill, and image types"
```

---

### Task 5: Provider System

**Files:**
- Create: `src/asset_optimizer/providers/__init__.py`
- Create: `src/asset_optimizer/providers/base.py`
- Create: `src/asset_optimizer/providers/registry.py`
- Create: `src/asset_optimizer/providers/openai_provider.py`
- Create: `src/asset_optimizer/providers/anthropic_provider.py`
- Create: `src/asset_optimizer/providers/openai_compat.py`
- Create: `src/asset_optimizer/providers/gemini_provider.py`
- Create: `src/asset_optimizer/providers/image_providers/__init__.py`
- Create: `src/asset_optimizer/providers/image_providers/base.py`
- Create: `src/asset_optimizer/providers/image_providers/openai_image.py`
- Create: `src/asset_optimizer/providers/image_providers/nano_banana.py`
- Create: `tests/unit/test_providers.py`

- [ ] **Step 1: Write failing tests for provider system**

`tests/unit/test_providers.py`:
```python
from dataclasses import dataclass

import pytest

from asset_optimizer.providers.base import (
    Criterion,
    ImageResult,
    JudgmentResult,
    JudgmentScore,
    Message,
    TextProvider,
)
from asset_optimizer.providers.image_providers.base import ImageProvider
from asset_optimizer.providers.registry import ProviderRegistry


class TestMessageTypes:
    def test_message_creation(self) -> None:
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_criterion_creation(self) -> None:
        c = Criterion(name="clarity", description="Is it clear?", max_score=10, rubric="1-10 scale")
        assert c.name == "clarity"
        assert c.max_score == 10

    def test_judgment_result(self) -> None:
        scores = [JudgmentScore(criterion="clarity", score=8.0, reasoning="Very clear")]
        result = JudgmentResult(scores=scores)
        assert result.scores[0].score == 8.0

    def test_image_result(self) -> None:
        result = ImageResult(image_data=b"fake", format="png", metadata={"width": 512})
        assert result.format == "png"
        assert result.metadata["width"] == 512


class FakeTextProvider(TextProvider):
    async def complete(self, messages: list[Message], **kwargs) -> str:
        return "fake response"

    async def judge(self, content: str, criteria: list[Criterion]) -> JudgmentResult:
        return JudgmentResult(
            scores=[JudgmentScore(criterion=c.name, score=5.0, reasoning="ok") for c in criteria]
        )


class FakeImageProvider(ImageProvider):
    async def generate(self, prompt: str, **kwargs) -> ImageResult:
        return ImageResult(image_data=b"fake-image", format="png")


class TestProviderProtocols:
    @pytest.mark.asyncio
    async def test_text_provider_complete(self) -> None:
        provider = FakeTextProvider()
        result = await provider.complete([Message(role="user", content="test")])
        assert result == "fake response"

    @pytest.mark.asyncio
    async def test_text_provider_judge(self) -> None:
        provider = FakeTextProvider()
        criteria = [Criterion(name="clarity", description="test", max_score=10)]
        result = await provider.judge("content", criteria)
        assert len(result.scores) == 1
        assert result.scores[0].score == 5.0

    @pytest.mark.asyncio
    async def test_image_provider_generate(self) -> None:
        provider = FakeImageProvider()
        result = await provider.generate("a cat")
        assert result.format == "png"


class TestProviderRegistry:
    def test_register_and_get_text_provider(self) -> None:
        registry = ProviderRegistry()
        provider = FakeTextProvider()
        registry.register_text("fake", provider)
        assert registry.get_text("fake") is provider

    def test_register_and_get_image_provider(self) -> None:
        registry = ProviderRegistry()
        provider = FakeImageProvider()
        registry.register_image("fake", provider)
        assert registry.get_image("fake") is provider

    def test_get_unknown_returns_none(self) -> None:
        registry = ProviderRegistry()
        assert registry.get_text("unknown") is None
        assert registry.get_image("unknown") is None

    def test_list_providers(self) -> None:
        registry = ProviderRegistry()
        registry.register_text("a", FakeTextProvider())
        registry.register_text("b", FakeTextProvider())
        registry.register_image("c", FakeImageProvider())
        assert set(registry.list_text()) == {"a", "b"}
        assert registry.list_image() == ["c"]

    def test_set_and_get_default(self) -> None:
        registry = ProviderRegistry()
        provider = FakeTextProvider()
        registry.register_text("main", provider)
        registry.set_default_text("main")
        assert registry.get_default_text() is provider
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_providers.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement provider base types**

`src/asset_optimizer/providers/__init__.py`:
```python
"""AI provider abstraction layer — text and image providers."""
```

`src/asset_optimizer/providers/base.py`:
```python
"""Base types and protocol for text AI providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Message:
    """A chat message."""

    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class Criterion:
    """A scoring criterion for AI-judged evaluation."""

    name: str
    description: str
    max_score: float = 10.0
    rubric: str = ""


@dataclass
class JudgmentScore:
    """Score for a single criterion from AI judge."""

    criterion: str
    score: float
    reasoning: str = ""


@dataclass
class JudgmentResult:
    """Complete judgment result from AI judge."""

    scores: list[JudgmentScore] = field(default_factory=list)


@dataclass
class ImageResult:
    """Result of an image generation request."""

    image_data: bytes = b""
    format: str = "png"
    metadata: dict[str, Any] = field(default_factory=dict)


class TextProvider(ABC):
    """Abstract base class for text AI providers."""

    @abstractmethod
    async def complete(self, messages: list[Message], **kwargs: Any) -> str:
        """Generate a text completion from messages."""
        ...

    @abstractmethod
    async def judge(self, content: str, criteria: list[Criterion]) -> JudgmentResult:
        """Judge content against criteria, returning scores with reasoning."""
        ...
```

- [ ] **Step 4: Implement image provider base and registry**

`src/asset_optimizer/providers/image_providers/__init__.py`:
```python
"""Image generation provider abstraction."""
```

`src/asset_optimizer/providers/image_providers/base.py`:
```python
"""Base class for image generation providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from asset_optimizer.providers.base import ImageResult


class ImageProvider(ABC):
    """Abstract base class for image generation providers."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> ImageResult:
        """Generate an image from a text prompt."""
        ...
```

`src/asset_optimizer/providers/registry.py`:
```python
"""Provider registry for managing text and image providers."""

from __future__ import annotations

from asset_optimizer.providers.base import TextProvider
from asset_optimizer.providers.image_providers.base import ImageProvider


class ProviderRegistry:
    """Registry for text and image AI providers."""

    def __init__(self) -> None:
        self._text: dict[str, TextProvider] = {}
        self._image: dict[str, ImageProvider] = {}
        self._default_text: str | None = None
        self._default_image: str | None = None

    def register_text(self, name: str, provider: TextProvider) -> None:
        self._text[name] = provider

    def register_image(self, name: str, provider: ImageProvider) -> None:
        self._image[name] = provider

    def get_text(self, name: str) -> TextProvider | None:
        return self._text.get(name)

    def get_image(self, name: str) -> ImageProvider | None:
        return self._image.get(name)

    def list_text(self) -> list[str]:
        return list(self._text.keys())

    def list_image(self) -> list[str]:
        return list(self._image.keys())

    def set_default_text(self, name: str) -> None:
        self._default_text = name

    def set_default_image(self, name: str) -> None:
        self._default_image = name

    def get_default_text(self) -> TextProvider | None:
        if self._default_text:
            return self._text.get(self._default_text)
        return None

    def get_default_image(self) -> ImageProvider | None:
        if self._default_image:
            return self._image.get(self._default_image)
        return None
```

- [ ] **Step 5: Implement OpenAI text provider**

`src/asset_optimizer/providers/openai_provider.py`:
```python
"""OpenAI text provider implementation."""

from __future__ import annotations

import json
from typing import Any

from openai import AsyncOpenAI

from asset_optimizer.providers.base import (
    Criterion,
    JudgmentResult,
    JudgmentScore,
    Message,
    TextProvider,
)

_JUDGE_SYSTEM_PROMPT = """You are an expert evaluator. Score the provided content against each criterion.
Return a JSON array where each element has: "criterion" (string), "score" (number), "reasoning" (string).
Be precise and justify each score based on the rubric provided."""


class OpenAITextProvider(TextProvider):
    """Text provider using the OpenAI API."""

    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: str | None = None) -> None:
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    async def complete(self, messages: list[Message], **kwargs: Any) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            **kwargs,
        )
        return response.choices[0].message.content or ""

    async def judge(self, content: str, criteria: list[Criterion]) -> JudgmentResult:
        criteria_text = "\n".join(
            f"- {c.name}: {c.description} (max: {c.max_score})\n  Rubric: {c.rubric}"
            for c in criteria
        )
        user_msg = f"Content to evaluate:\n{content}\n\nCriteria:\n{criteria_text}"

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": _JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or "[]"
        return _parse_judgment(raw, criteria)


def _parse_judgment(raw: str, criteria: list[Criterion]) -> JudgmentResult:
    """Parse JSON judgment response into JudgmentResult."""
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and "scores" in data:
            data = data["scores"]
        if not isinstance(data, list):
            data = [data]
    except json.JSONDecodeError:
        data = []

    max_scores = {c.name: c.max_score for c in criteria}
    scores = []
    for item in data:
        if isinstance(item, dict) and "criterion" in item:
            name = item["criterion"]
            raw_score = float(item.get("score", 0))
            capped = min(raw_score, max_scores.get(name, 10.0))
            scores.append(
                JudgmentScore(
                    criterion=name,
                    score=capped,
                    reasoning=item.get("reasoning", ""),
                )
            )
    return JudgmentResult(scores=scores)
```

- [ ] **Step 6: Implement Anthropic provider**

`src/asset_optimizer/providers/anthropic_provider.py`:
```python
"""Anthropic Claude text provider implementation."""

from __future__ import annotations

import json
from typing import Any

from anthropic import AsyncAnthropic

from asset_optimizer.providers.base import (
    Criterion,
    JudgmentResult,
    JudgmentScore,
    Message,
    TextProvider,
)

_JUDGE_SYSTEM_PROMPT = """You are an expert evaluator. Score the provided content against each criterion.
Return a JSON array where each element has: "criterion" (string), "score" (number), "reasoning" (string).
Be precise and justify each score based on the rubric provided."""


class AnthropicProvider(TextProvider):
    """Text provider using the Anthropic Claude API."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514") -> None:
        self._client = AsyncAnthropic(api_key=api_key)
        self._model = model

    async def complete(self, messages: list[Message], **kwargs: Any) -> str:
        system_msgs = [m.content for m in messages if m.role == "system"]
        non_system = [{"role": m.role, "content": m.content} for m in messages if m.role != "system"]

        response = await self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system="\n".join(system_msgs) if system_msgs else "",
            messages=non_system,
            **kwargs,
        )
        return response.content[0].text if response.content else ""

    async def judge(self, content: str, criteria: list[Criterion]) -> JudgmentResult:
        criteria_text = "\n".join(
            f"- {c.name}: {c.description} (max: {c.max_score})\n  Rubric: {c.rubric}"
            for c in criteria
        )
        user_msg = (
            f"Content to evaluate:\n{content}\n\n"
            f"Criteria:\n{criteria_text}\n\n"
            "Respond with a JSON array of scores."
        )

        response = await self._client.messages.create(
            model=self._model,
            max_tokens=2048,
            system=_JUDGE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )

        raw = response.content[0].text if response.content else "[]"
        return _parse_judgment(raw, criteria)


def _parse_judgment(raw: str, criteria: list[Criterion]) -> JudgmentResult:
    """Parse JSON judgment response into JudgmentResult."""
    # Extract JSON from possible markdown code blocks
    if "```" in raw:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            raw = raw[start:end]

    try:
        data = json.loads(raw)
        if not isinstance(data, list):
            data = [data]
    except json.JSONDecodeError:
        data = []

    max_scores = {c.name: c.max_score for c in criteria}
    scores = []
    for item in data:
        if isinstance(item, dict) and "criterion" in item:
            name = item["criterion"]
            raw_score = float(item.get("score", 0))
            capped = min(raw_score, max_scores.get(name, 10.0))
            scores.append(
                JudgmentScore(
                    criterion=name, score=capped, reasoning=item.get("reasoning", "")
                )
            )
    return JudgmentResult(scores=scores)
```

- [ ] **Step 7: Implement OpenAI-compatible provider (vLLM, Ollama)**

`src/asset_optimizer/providers/openai_compat.py`:
```python
"""OpenAI-compatible provider for vLLM, Ollama, and other compatible APIs."""

from __future__ import annotations

from asset_optimizer.providers.openai_provider import OpenAITextProvider


class OpenAICompatProvider(OpenAITextProvider):
    """Provider for OpenAI-compatible APIs (vLLM, Ollama, etc.).

    Reuses OpenAITextProvider with a custom base_url.
    """

    def __init__(self, base_url: str, model: str, api_key: str = "not-needed") -> None:
        super().__init__(api_key=api_key, model=model, base_url=base_url)
```

- [ ] **Step 8: Implement Gemini provider**

`src/asset_optimizer/providers/gemini_provider.py`:
```python
"""Google Gemini text provider implementation."""

from __future__ import annotations

import json
from typing import Any

from google import generativeai as genai

from asset_optimizer.providers.base import (
    Criterion,
    JudgmentResult,
    JudgmentScore,
    Message,
    TextProvider,
)

_JUDGE_PROMPT = """You are an expert evaluator. Score the provided content against each criterion.
Return a JSON array where each element has: "criterion" (string), "score" (number), "reasoning" (string).
Be precise and justify each score based on the rubric provided."""


class GeminiProvider(TextProvider):
    """Text provider using the Google Gemini API."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash") -> None:
        genai.configure(api_key=api_key)
        self._model_name = model

    async def complete(self, messages: list[Message], **kwargs: Any) -> str:
        model = genai.GenerativeModel(self._model_name)
        # Combine messages into a single prompt for Gemini
        prompt_parts: list[str] = []
        for m in messages:
            if m.role == "system":
                prompt_parts.append(f"[System]: {m.content}")
            elif m.role == "user":
                prompt_parts.append(m.content)
            elif m.role == "assistant":
                prompt_parts.append(f"[Assistant]: {m.content}")
        prompt = "\n\n".join(prompt_parts)

        response = await model.generate_content_async(prompt, **kwargs)
        return response.text or ""

    async def judge(self, content: str, criteria: list[Criterion]) -> JudgmentResult:
        criteria_text = "\n".join(
            f"- {c.name}: {c.description} (max: {c.max_score})\n  Rubric: {c.rubric}"
            for c in criteria
        )
        prompt = (
            f"{_JUDGE_PROMPT}\n\n"
            f"Content to evaluate:\n{content}\n\n"
            f"Criteria:\n{criteria_text}\n\n"
            "Respond with a JSON array of scores."
        )

        model = genai.GenerativeModel(self._model_name)
        response = await model.generate_content_async(prompt)
        raw = response.text or "[]"

        return _parse_judgment(raw, criteria)


def _parse_judgment(raw: str, criteria: list[Criterion]) -> JudgmentResult:
    """Parse JSON judgment response into JudgmentResult."""
    if "```" in raw:
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            raw = raw[start:end]

    try:
        data = json.loads(raw)
        if not isinstance(data, list):
            data = [data]
    except json.JSONDecodeError:
        data = []

    max_scores = {c.name: c.max_score for c in criteria}
    scores = []
    for item in data:
        if isinstance(item, dict) and "criterion" in item:
            name = item["criterion"]
            raw_score = float(item.get("score", 0))
            capped = min(raw_score, max_scores.get(name, 10.0))
            scores.append(
                JudgmentScore(criterion=name, score=capped, reasoning=item.get("reasoning", ""))
            )
    return JudgmentResult(scores=scores)
```

- [ ] **Step 9: Implement image providers**

`src/asset_optimizer/providers/image_providers/openai_image.py`:
```python
"""OpenAI Image provider (supports Image 01 and DALL-E models)."""

from __future__ import annotations

import base64
from typing import Any

from openai import AsyncOpenAI

from asset_optimizer.providers.base import ImageResult
from asset_optimizer.providers.image_providers.base import ImageProvider


class OpenAIImageProvider(ImageProvider):
    """Image generation using OpenAI's image API."""

    def __init__(self, api_key: str, model: str = "image-01") -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def generate(self, prompt: str, **kwargs: Any) -> ImageResult:
        size = kwargs.get("size", "1024x1024")
        response = await self._client.images.generate(
            model=self._model,
            prompt=prompt,
            n=1,
            size=size,
            response_format="b64_json",
        )

        image_data = base64.b64decode(response.data[0].b64_json or "")
        return ImageResult(
            image_data=image_data,
            format="png",
            metadata={"model": self._model, "size": size, "revised_prompt": response.data[0].revised_prompt},
        )
```

`src/asset_optimizer/providers/image_providers/nano_banana.py`:
```python
"""Nano Banana image generation provider."""

from __future__ import annotations

import base64
from typing import Any

import httpx

from asset_optimizer.providers.base import ImageResult
from asset_optimizer.providers.image_providers.base import ImageProvider


class NanoBananaProvider(ImageProvider):
    """Image generation using the Nano Banana API."""

    def __init__(self, api_key: str, endpoint: str = "https://api.nanobanana.com/v1") -> None:
        self._api_key = api_key
        self._endpoint = endpoint.rstrip("/")

    async def generate(self, prompt: str, **kwargs: Any) -> ImageResult:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self._endpoint}/generate",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={"prompt": prompt, **kwargs},
            )
            response.raise_for_status()
            data = response.json()

        image_data = base64.b64decode(data.get("image", ""))
        return ImageResult(
            image_data=image_data,
            format=data.get("format", "png"),
            metadata=data.get("metadata", {}),
        )
```

- [ ] **Step 10: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_providers.py -v`
Expected: All tests PASS.

- [ ] **Step 11: Run full suite, lint, type check**

Run: `uv run pytest tests/ -v && uv run ruff check src/ tests/ && uv run mypy src/asset_optimizer/`
Expected: All pass. (Note: mypy may need type stubs for google-generativeai — add `# type: ignore[import-untyped]` if needed.)

- [ ] **Step 12: Commit**

```bash
git add src/asset_optimizer/providers/ tests/unit/test_providers.py
git commit -m "feat: add provider system with OpenAI, Anthropic, Gemini, vLLM, Ollama, and image providers"
```

---

### Task 6: Scoring System

**Files:**
- Create: `src/asset_optimizer/scoring/__init__.py`
- Create: `src/asset_optimizer/scoring/base.py`
- Create: `src/asset_optimizer/scoring/heuristic.py`
- Create: `src/asset_optimizer/scoring/ai_judge.py`
- Create: `src/asset_optimizer/scoring/composite.py`
- Create: `tests/unit/test_scoring.py`

- [ ] **Step 1: Write failing tests for scoring system**

`tests/unit/test_scoring.py`:
```python
import pytest

from asset_optimizer.providers.base import Criterion, JudgmentResult, JudgmentScore
from asset_optimizer.scoring.base import ScoreResult, Scorer
from asset_optimizer.scoring.composite import CompositeScorer
from asset_optimizer.scoring.heuristic import (
    KeywordScorer,
    LengthScorer,
    ReadabilityScorer,
    StructureScorer,
)


class TestLengthScorer:
    def test_optimal_length(self) -> None:
        scorer = LengthScorer(min_length=10, max_length=100, optimal_length=50)
        result = scorer.score("A" * 50)
        assert result.value == 10.0

    def test_too_short(self) -> None:
        scorer = LengthScorer(min_length=10, max_length=100, optimal_length=50)
        result = scorer.score("Hi")
        assert result.value < 5.0

    def test_too_long(self) -> None:
        scorer = LengthScorer(min_length=10, max_length=100, optimal_length=50)
        result = scorer.score("A" * 200)
        assert result.value < 5.0

    def test_empty_string(self) -> None:
        scorer = LengthScorer(min_length=10, max_length=100)
        result = scorer.score("")
        assert result.value == 0.0


class TestStructureScorer:
    def test_has_all_sections(self) -> None:
        scorer = StructureScorer(required_sections=["# Header", "## Body"])
        text = "# Header\nSome content\n## Body\nMore content"
        result = scorer.score(text)
        assert result.value == 10.0

    def test_missing_sections(self) -> None:
        scorer = StructureScorer(required_sections=["# Header", "## Body", "## Footer"])
        text = "# Header\nSome content"
        result = scorer.score(text)
        assert result.value < 10.0


class TestKeywordScorer:
    def test_all_keywords_present(self) -> None:
        scorer = KeywordScorer(required_keywords=["hello", "world"])
        result = scorer.score("hello beautiful world")
        assert result.value == 10.0

    def test_some_keywords_missing(self) -> None:
        scorer = KeywordScorer(required_keywords=["hello", "world", "foo"])
        result = scorer.score("hello world")
        assert 5.0 < result.value < 10.0

    def test_no_keywords_present(self) -> None:
        scorer = KeywordScorer(required_keywords=["alpha", "beta"])
        result = scorer.score("nothing here")
        assert result.value == 0.0


class TestReadabilityScorer:
    def test_simple_text_scores_well(self) -> None:
        scorer = ReadabilityScorer()
        result = scorer.score("The cat sat on the mat. It was a good cat.")
        assert result.value > 0.0

    def test_empty_text(self) -> None:
        scorer = ReadabilityScorer()
        result = scorer.score("")
        assert result.value == 0.0


class TestCompositeScorer:
    def test_weighted_average(self) -> None:
        scorer1 = LengthScorer(min_length=1, max_length=100, optimal_length=10)
        scorer2 = KeywordScorer(required_keywords=["hello"])

        composite = CompositeScorer(
            scorers=[
                {"scorer": scorer1, "weight": 0.5, "criterion": "length"},
                {"scorer": scorer2, "weight": 0.5, "criterion": "keywords"},
            ]
        )
        results = composite.score_all("hello world")
        assert len(results) == 2
        total = composite.composite_score(results)
        assert 0.0 <= total <= 10.0

    def test_single_scorer(self) -> None:
        scorer = LengthScorer(min_length=5, max_length=50, optimal_length=20)
        composite = CompositeScorer(
            scorers=[{"scorer": scorer, "weight": 1.0, "criterion": "length"}]
        )
        results = composite.score_all("A" * 20)
        assert len(results) == 1
        assert results[0].value == 10.0


class TestScoreResult:
    def test_fields(self) -> None:
        result = ScoreResult(
            criterion="clarity",
            value=7.5,
            max_value=10.0,
            scorer_type="heuristic",
            details={"note": "good"},
        )
        assert result.criterion == "clarity"
        assert result.value == 7.5
        assert result.scorer_type == "heuristic"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_scoring.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement scorer base types**

`src/asset_optimizer/scoring/__init__.py`:
```python
"""Scoring system — heuristic, AI-judged, and composite scorers."""
```

`src/asset_optimizer/scoring/base.py`:
```python
"""Base types for the scoring system."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ScoreResult:
    """Result of scoring a single criterion."""

    criterion: str
    value: float
    max_value: float = 10.0
    scorer_type: str = "heuristic"
    details: dict[str, Any] = field(default_factory=dict)


class Scorer(ABC):
    """Abstract base for all scorers."""

    @abstractmethod
    def score(self, content: str) -> ScoreResult:
        """Score text content, returning a ScoreResult."""
        ...
```

- [ ] **Step 4: Implement heuristic scorers**

`src/asset_optimizer/scoring/heuristic.py`:
```python
"""Rule-based heuristic scorers — fast, deterministic, no API calls."""

from __future__ import annotations

import re

from asset_optimizer.scoring.base import ScoreResult, Scorer


class LengthScorer(Scorer):
    """Score based on text length relative to optimal range."""

    def __init__(
        self,
        min_length: int = 10,
        max_length: int = 5000,
        optimal_length: int | None = None,
    ) -> None:
        self.min_length = min_length
        self.max_length = max_length
        self.optimal_length = optimal_length or (min_length + max_length) // 2

    def score(self, content: str) -> ScoreResult:
        length = len(content)
        if length == 0:
            return ScoreResult(criterion="length", value=0.0, details={"length": 0})

        if length <= self.optimal_length:
            ratio = max(0.0, (length - self.min_length)) / max(1, (self.optimal_length - self.min_length))
        else:
            ratio = max(0.0, (self.max_length - length)) / max(1, (self.max_length - self.optimal_length))

        value = round(min(10.0, max(0.0, ratio * 10.0)), 2)
        return ScoreResult(
            criterion="length",
            value=value,
            details={"length": length, "optimal": self.optimal_length},
        )


class StructureScorer(Scorer):
    """Score based on presence of required sections/patterns."""

    def __init__(self, required_sections: list[str] | None = None) -> None:
        self.required_sections = required_sections or []

    def score(self, content: str) -> ScoreResult:
        if not self.required_sections:
            return ScoreResult(criterion="structure", value=10.0)

        found = sum(1 for section in self.required_sections if section in content)
        ratio = found / len(self.required_sections)
        value = round(ratio * 10.0, 2)
        return ScoreResult(
            criterion="structure",
            value=value,
            details={"found": found, "required": len(self.required_sections)},
        )


class KeywordScorer(Scorer):
    """Score based on presence of required keywords."""

    def __init__(self, required_keywords: list[str] | None = None) -> None:
        self.required_keywords = required_keywords or []

    def score(self, content: str) -> ScoreResult:
        if not self.required_keywords:
            return ScoreResult(criterion="keywords", value=10.0)

        content_lower = content.lower()
        found = sum(1 for kw in self.required_keywords if kw.lower() in content_lower)
        ratio = found / len(self.required_keywords)
        value = round(ratio * 10.0, 2)
        return ScoreResult(
            criterion="keywords",
            value=value,
            details={"found": found, "required": len(self.required_keywords)},
        )


class ReadabilityScorer(Scorer):
    """Score based on text readability (simplified Flesch-Kincaid)."""

    def score(self, content: str) -> ScoreResult:
        if not content.strip():
            return ScoreResult(criterion="readability", value=0.0)

        sentences = [s.strip() for s in re.split(r"[.!?]+", content) if s.strip()]
        words = content.split()
        syllables = sum(self._count_syllables(w) for w in words)

        num_sentences = max(1, len(sentences))
        num_words = max(1, len(words))

        # Flesch Reading Ease: higher = easier to read
        fre = 206.835 - 1.015 * (num_words / num_sentences) - 84.6 * (syllables / num_words)
        # Normalize to 0-10 scale (FRE typically 0-100, aim for 30-70 as good)
        value = round(min(10.0, max(0.0, fre / 10.0)), 2)
        return ScoreResult(
            criterion="readability",
            value=value,
            details={"flesch_reading_ease": round(fre, 2)},
        )

    @staticmethod
    def _count_syllables(word: str) -> int:
        """Rough syllable count heuristic."""
        word = word.lower().strip(".,!?;:'\"")
        if not word:
            return 0
        count = 0
        vowels = "aeiouy"
        prev_vowel = False
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel
        if word.endswith("e") and count > 1:
            count -= 1
        return max(1, count)
```

- [ ] **Step 5: Implement AI judge scorer**

`src/asset_optimizer/scoring/ai_judge.py`:
```python
"""AI-judged scoring using a text provider as evaluator."""

from __future__ import annotations

from asset_optimizer.providers.base import Criterion, TextProvider
from asset_optimizer.scoring.base import ScoreResult


class AIJudgeScorer:
    """Scorer that uses an AI provider to evaluate content against criteria."""

    def __init__(self, provider: TextProvider, criteria: list[Criterion]) -> None:
        self._provider = provider
        self._criteria = criteria

    async def score(self, content: str) -> list[ScoreResult]:
        """Score content using AI judge. Returns one ScoreResult per criterion."""
        judgment = await self._provider.judge(content, self._criteria)

        results: list[ScoreResult] = []
        scored_criteria = {s.criterion for s in judgment.scores}

        for js in judgment.scores:
            results.append(
                ScoreResult(
                    criterion=js.criterion,
                    value=js.score,
                    max_value=next(
                        (c.max_score for c in self._criteria if c.name == js.criterion), 10.0
                    ),
                    scorer_type="ai_judge",
                    details={"reasoning": js.reasoning},
                )
            )

        # Add zero scores for criteria the AI didn't score
        for c in self._criteria:
            if c.name not in scored_criteria:
                results.append(
                    ScoreResult(
                        criterion=c.name,
                        value=0.0,
                        max_value=c.max_score,
                        scorer_type="ai_judge",
                        details={"reasoning": "Not scored by judge"},
                    )
                )

        return results
```

- [ ] **Step 6: Implement composite scorer**

`src/asset_optimizer/scoring/composite.py`:
```python
"""Composite scorer combining multiple heuristic scorers with weights."""

from __future__ import annotations

from typing import Any

from asset_optimizer.scoring.base import ScoreResult, Scorer


class CompositeScorer:
    """Weighted combination of multiple scorers."""

    def __init__(self, scorers: list[dict[str, Any]]) -> None:
        """Initialize with list of {"scorer": Scorer, "weight": float, "criterion": str}."""
        self._scorers = scorers

    def score_all(self, content: str) -> list[ScoreResult]:
        """Score content with all scorers, returning individual results."""
        results: list[ScoreResult] = []
        for entry in self._scorers:
            scorer: Scorer = entry["scorer"]
            criterion: str = entry["criterion"]
            result = scorer.score(content)
            result.criterion = criterion
            results.append(result)
        return results

    def composite_score(self, results: list[ScoreResult]) -> float:
        """Calculate weighted average from individual scores."""
        total_weight = sum(e["weight"] for e in self._scorers)
        if total_weight == 0:
            return 0.0

        weighted_sum = 0.0
        result_map = {r.criterion: r for r in results}
        for entry in self._scorers:
            criterion: str = entry["criterion"]
            weight: float = entry["weight"]
            result = result_map.get(criterion)
            if result:
                normalized = result.value / result.max_value * 10.0
                weighted_sum += normalized * weight

        return round(weighted_sum / total_weight, 2)
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_scoring.py -v`
Expected: All tests PASS.

- [ ] **Step 8: Run full suite, lint, type check**

Run: `uv run pytest tests/ -v && uv run ruff check src/ tests/ && uv run mypy src/asset_optimizer/`
Expected: All pass.

- [ ] **Step 9: Commit**

```bash
git add src/asset_optimizer/scoring/ tests/unit/test_scoring.py
git commit -m "feat: add scoring system with heuristic, AI-judge, and composite scorers"
```

---

### Task 7: Evaluation System

**Files:**
- Create: `src/asset_optimizer/core/__init__.py`
- Create: `src/asset_optimizer/core/evaluation.py`
- Create: `tests/unit/test_evaluation.py`
- Create: `evaluations/prompt-clarity.yaml`

- [ ] **Step 1: Write failing tests**

`tests/unit/test_evaluation.py`:
```python
from pathlib import Path

import yaml

from asset_optimizer.core.evaluation import EvaluationConfig, load_evaluation


class TestEvaluationConfig:
    def test_from_dict(self) -> None:
        data = {
            "name": "test-eval",
            "asset_type": "prompt",
            "criteria": [
                {"name": "clarity", "description": "Is it clear?", "max_score": 10, "rubric": "1-10"},
            ],
            "scorer_config": {"type": "composite", "heuristic_weight": 0.3, "ai_judge_weight": 0.7},
        }
        config = EvaluationConfig(**data)
        assert config.name == "test-eval"
        assert config.asset_type == "prompt"
        assert len(config.criteria) == 1
        assert config.criteria[0].name == "clarity"
        assert config.scorer_config.type == "composite"

    def test_criteria_defaults(self) -> None:
        data = {
            "name": "minimal",
            "asset_type": "prompt",
            "criteria": [{"name": "quality", "description": "Overall quality"}],
        }
        config = EvaluationConfig(**data)
        assert config.criteria[0].max_score == 10.0
        assert config.criteria[0].rubric == ""


class TestLoadEvaluation:
    def test_load_from_yaml(self, tmp_path: Path) -> None:
        eval_data = {
            "name": "prompt-clarity",
            "asset_type": "prompt",
            "criteria": [
                {"name": "clarity", "description": "Is it clear?", "max_score": 10},
                {"name": "specificity", "description": "Is it specific?", "max_score": 10},
            ],
            "scorer_config": {"type": "composite"},
        }
        path = tmp_path / "eval.yaml"
        path.write_text(yaml.dump(eval_data))

        config = load_evaluation(path)
        assert config.name == "prompt-clarity"
        assert len(config.criteria) == 2

    def test_load_missing_file_raises(self) -> None:
        import pytest
        with pytest.raises(FileNotFoundError):
            load_evaluation(Path("/nonexistent/eval.yaml"))

    def test_validate_no_criteria_raises(self, tmp_path: Path) -> None:
        eval_data = {"name": "empty", "asset_type": "prompt", "criteria": []}
        path = tmp_path / "eval.yaml"
        path.write_text(yaml.dump(eval_data))

        import pytest
        with pytest.raises(ValueError, match="at least one criterion"):
            load_evaluation(path)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_evaluation.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement evaluation config and loader**

`src/asset_optimizer/core/__init__.py`:
```python
"""Core engine components — evaluation, iteration, convergence, experiment management."""
```

`src/asset_optimizer/core/evaluation.py`:
```python
"""Evaluation configuration — defines what 'good' looks like for an asset."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


class CriterionConfig(BaseModel):
    """A single evaluation criterion."""

    name: str
    description: str
    max_score: float = 10.0
    rubric: str = ""


class ScorerConfig(BaseModel):
    """Configuration for how scoring is performed."""

    type: str = "composite"
    judge_provider: str | None = None
    heuristic_weight: float = 0.2
    ai_judge_weight: float = 0.8


class EvaluationConfig(BaseModel):
    """Complete evaluation configuration."""

    name: str
    asset_type: str
    description: str = ""
    criteria: list[CriterionConfig]
    scorer_config: ScorerConfig = ScorerConfig()


def load_evaluation(path: Path) -> EvaluationConfig:
    """Load an evaluation configuration from a YAML file."""
    if not path.exists():
        raise FileNotFoundError(f"Evaluation file not found: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    config = EvaluationConfig(**raw)

    if not config.criteria:
        raise ValueError(f"Evaluation '{config.name}' must have at least one criterion")

    return config
```

- [ ] **Step 4: Create built-in evaluation file**

`evaluations/prompt-clarity.yaml`:
```yaml
name: prompt-clarity
asset_type: prompt
description: Evaluates prompt clarity, specificity, and effectiveness

criteria:
  - name: clarity
    description: "Is the prompt unambiguous and easy to understand?"
    max_score: 10
    rubric: |
      1-3: Vague, multiple interpretations possible
      4-6: Mostly clear but some ambiguity
      7-9: Clear and specific
      10: Crystal clear, no room for misinterpretation

  - name: specificity
    description: "Does the prompt include specific, actionable instructions?"
    max_score: 10
    rubric: |
      1-3: Generic instructions, no concrete guidance
      4-6: Some specifics but leaves gaps
      7-9: Detailed, actionable instructions
      10: Exhaustively specific with examples

  - name: effectiveness
    description: "Would this prompt reliably produce the desired output?"
    max_score: 10
    rubric: |
      1-3: Unreliable, inconsistent results expected
      4-6: Sometimes produces desired output
      7-9: Reliably produces good output
      10: Consistently produces excellent output

scorer_config:
  type: composite
  heuristic_weight: 0.2
  ai_judge_weight: 0.8
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_evaluation.py -v`
Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
git add src/asset_optimizer/core/ tests/unit/test_evaluation.py evaluations/
git commit -m "feat: add evaluation system with YAML config loading"
```

---

## Phase 3: Core Engine

### Task 8: Optimization Engine

**Files:**
- Create: `src/asset_optimizer/core/convergence.py`
- Create: `src/asset_optimizer/core/iteration.py`
- Create: `src/asset_optimizer/core/engine.py`
- Create: `tests/unit/test_convergence.py`
- Create: `tests/unit/test_engine.py`

- [ ] **Step 1: Write failing tests for convergence strategies**

`tests/unit/test_convergence.py`:
```python
from asset_optimizer.core.convergence import (
    BudgetStrategy,
    ConvergenceResult,
    GreedyStrategy,
    TargetStrategy,
)


class TestGreedyStrategy:
    def test_should_continue_with_improvement(self) -> None:
        strategy = GreedyStrategy(stagnation_limit=3)
        result = strategy.check(
            iteration=1, current_score=5.0, previous_score=3.0, max_iterations=20
        )
        assert result.should_continue is True

    def test_should_stop_after_stagnation(self) -> None:
        strategy = GreedyStrategy(stagnation_limit=2)
        # Simulate no improvement for 2 iterations
        strategy.check(iteration=1, current_score=5.0, previous_score=5.0, max_iterations=20)
        result = strategy.check(iteration=2, current_score=5.0, previous_score=5.0, max_iterations=20)
        assert result.should_continue is False
        assert "stagnation" in result.reason.lower()

    def test_should_stop_at_max_iterations(self) -> None:
        strategy = GreedyStrategy(stagnation_limit=10)
        result = strategy.check(iteration=20, current_score=5.0, previous_score=4.0, max_iterations=20)
        assert result.should_continue is False

    def test_resets_stagnation_on_improvement(self) -> None:
        strategy = GreedyStrategy(stagnation_limit=2)
        strategy.check(iteration=1, current_score=5.0, previous_score=5.0, max_iterations=20)
        strategy.check(iteration=2, current_score=6.0, previous_score=5.0, max_iterations=20)  # improvement resets
        result = strategy.check(iteration=3, current_score=6.0, previous_score=6.0, max_iterations=20)
        assert result.should_continue is True  # only 1 stagnation, limit is 2


class TestTargetStrategy:
    def test_should_stop_when_target_reached(self) -> None:
        strategy = TargetStrategy(target_score=8.0)
        result = strategy.check(iteration=1, current_score=8.5, previous_score=0.0, max_iterations=20)
        assert result.should_continue is False
        assert "target" in result.reason.lower()

    def test_should_continue_below_target(self) -> None:
        strategy = TargetStrategy(target_score=8.0)
        result = strategy.check(iteration=1, current_score=6.0, previous_score=4.0, max_iterations=20)
        assert result.should_continue is True


class TestBudgetStrategy:
    def test_runs_exact_iterations(self) -> None:
        strategy = BudgetStrategy()
        result = strategy.check(iteration=5, current_score=5.0, previous_score=4.0, max_iterations=10)
        assert result.should_continue is True

    def test_stops_at_max(self) -> None:
        strategy = BudgetStrategy()
        result = strategy.check(iteration=10, current_score=5.0, previous_score=4.0, max_iterations=10)
        assert result.should_continue is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_convergence.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement convergence strategies**

`src/asset_optimizer/core/convergence.py`:
```python
"""Convergence strategies for the optimization loop."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ConvergenceResult:
    """Result of a convergence check."""

    should_continue: bool
    reason: str = ""


class ConvergenceStrategy(ABC):
    """Base class for convergence strategies."""

    @abstractmethod
    def check(
        self,
        iteration: int,
        current_score: float,
        previous_score: float,
        max_iterations: int,
    ) -> ConvergenceResult:
        ...

    def reset(self) -> None:
        """Reset internal state for a new experiment."""
        pass


class GreedyStrategy(ConvergenceStrategy):
    """Accept any improvement; stop after N consecutive non-improvements."""

    def __init__(self, stagnation_limit: int = 5, min_improvement: float = 0.01) -> None:
        self.stagnation_limit = stagnation_limit
        self.min_improvement = min_improvement
        self._stagnation_count = 0

    def check(
        self,
        iteration: int,
        current_score: float,
        previous_score: float,
        max_iterations: int,
    ) -> ConvergenceResult:
        if iteration >= max_iterations:
            return ConvergenceResult(should_continue=False, reason="Max iterations reached")

        improvement = current_score - previous_score
        if improvement >= self.min_improvement:
            self._stagnation_count = 0
        else:
            self._stagnation_count += 1

        if self._stagnation_count >= self.stagnation_limit:
            return ConvergenceResult(
                should_continue=False,
                reason=f"Stagnation limit reached ({self.stagnation_limit} iterations without improvement)",
            )

        return ConvergenceResult(should_continue=True)

    def reset(self) -> None:
        self._stagnation_count = 0


class TargetStrategy(ConvergenceStrategy):
    """Stop when target score is reached."""

    def __init__(self, target_score: float = 8.0) -> None:
        self.target_score = target_score

    def check(
        self,
        iteration: int,
        current_score: float,
        previous_score: float,
        max_iterations: int,
    ) -> ConvergenceResult:
        if iteration >= max_iterations:
            return ConvergenceResult(should_continue=False, reason="Max iterations reached")

        if current_score >= self.target_score:
            return ConvergenceResult(
                should_continue=False,
                reason=f"Target score {self.target_score} reached (current: {current_score})",
            )

        return ConvergenceResult(should_continue=True)


class BudgetStrategy(ConvergenceStrategy):
    """Run exactly max_iterations, keep the best result."""

    def check(
        self,
        iteration: int,
        current_score: float,
        previous_score: float,
        max_iterations: int,
    ) -> ConvergenceResult:
        if iteration >= max_iterations:
            return ConvergenceResult(should_continue=False, reason="Budget exhausted")
        return ConvergenceResult(should_continue=True)


def create_strategy(name: str, **kwargs: object) -> ConvergenceStrategy:
    """Factory function for convergence strategies."""
    strategies: dict[str, type[ConvergenceStrategy]] = {
        "greedy": GreedyStrategy,
        "target": TargetStrategy,
        "budget": BudgetStrategy,
    }
    cls = strategies.get(name)
    if cls is None:
        raise ValueError(f"Unknown convergence strategy: {name}. Options: {list(strategies.keys())}")
    return cls(**kwargs)  # type: ignore[arg-type]
```

- [ ] **Step 4: Run convergence tests**

Run: `uv run pytest tests/unit/test_convergence.py -v`
Expected: All tests PASS.

- [ ] **Step 5: Write failing tests for the engine**

`tests/unit/test_engine.py`:
```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from asset_optimizer.assets.base import AssetContent
from asset_optimizer.core.engine import Engine, OptimizationResult
from asset_optimizer.core.evaluation import CriterionConfig, EvaluationConfig, ScorerConfig
from asset_optimizer.providers.base import (
    Criterion,
    JudgmentResult,
    JudgmentScore,
    Message,
    TextProvider,
)
from asset_optimizer.scoring.base import ScoreResult


class MockProvider(TextProvider):
    """Provider that returns progressively better content."""

    def __init__(self) -> None:
        self.call_count = 0

    async def complete(self, messages: list[Message], **kwargs: Any) -> str:
        self.call_count += 1
        return f"Improved prompt version {self.call_count}. Clear, specific, and actionable instructions for the assistant."

    async def judge(self, content: str, criteria: list[Criterion]) -> JudgmentResult:
        # Score increases with length as a simple heuristic for "better"
        base = min(9.0, len(content) / 20.0)
        return JudgmentResult(
            scores=[
                JudgmentScore(criterion=c.name, score=min(base, c.max_score), reasoning="ok")
                for c in criteria
            ]
        )


class DegradingProvider(TextProvider):
    """Provider that returns worse content over time."""

    async def complete(self, messages: list[Message], **kwargs: Any) -> str:
        return "Bad"

    async def judge(self, content: str, criteria: list[Criterion]) -> JudgmentResult:
        return JudgmentResult(
            scores=[JudgmentScore(criterion=c.name, score=1.0, reasoning="poor") for c in criteria]
        )


@pytest.fixture
def eval_config() -> EvaluationConfig:
    return EvaluationConfig(
        name="test-eval",
        asset_type="prompt",
        criteria=[
            CriterionConfig(name="clarity", description="Is it clear?", max_score=10.0),
            CriterionConfig(name="specificity", description="Is it specific?", max_score=10.0),
        ],
        scorer_config=ScorerConfig(type="composite", ai_judge_weight=1.0, heuristic_weight=0.0),
    )


class TestEngine:
    @pytest.mark.asyncio
    async def test_optimize_improves_score(self, eval_config: EvaluationConfig) -> None:
        provider = MockProvider()
        engine = Engine(provider=provider, judge_provider=provider)

        result = await engine.optimize(
            content="You are a helpful assistant.",
            evaluation=eval_config,
            max_iterations=3,
        )

        assert isinstance(result, OptimizationResult)
        assert result.total_iterations >= 1
        assert result.best_score > 0.0
        assert result.best_content != "You are a helpful assistant."

    @pytest.mark.asyncio
    async def test_optimize_stops_at_max_iterations(self, eval_config: EvaluationConfig) -> None:
        provider = MockProvider()
        engine = Engine(provider=provider, judge_provider=provider)

        result = await engine.optimize(
            content="Short",
            evaluation=eval_config,
            max_iterations=2,
        )
        assert result.total_iterations <= 2

    @pytest.mark.asyncio
    async def test_optimize_with_target_score(self, eval_config: EvaluationConfig) -> None:
        provider = MockProvider()
        engine = Engine(provider=provider, judge_provider=provider)

        result = await engine.optimize(
            content="Short",
            evaluation=eval_config,
            max_iterations=10,
            target_score=3.0,
            convergence_strategy="target",
        )
        assert result.best_score >= 3.0

    @pytest.mark.asyncio
    async def test_optimize_callback(self, eval_config: EvaluationConfig) -> None:
        provider = MockProvider()
        engine = Engine(provider=provider, judge_provider=provider)

        iterations_seen: list[int] = []

        def on_iteration(info: dict[str, Any]) -> None:
            iterations_seen.append(info["iteration"])

        await engine.optimize(
            content="Test",
            evaluation=eval_config,
            max_iterations=2,
            on_iteration=on_iteration,
        )
        assert len(iterations_seen) >= 1

    @pytest.mark.asyncio
    async def test_optimize_with_stagnation(self, eval_config: EvaluationConfig) -> None:
        provider = DegradingProvider()
        engine = Engine(provider=provider, judge_provider=provider)

        result = await engine.optimize(
            content="Already good content that is clear and specific with great detail.",
            evaluation=eval_config,
            max_iterations=20,
            stagnation_limit=2,
        )
        # Should stop early due to stagnation
        assert result.total_iterations < 20
```

- [ ] **Step 6: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_engine.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 7: Implement the engine**

`src/asset_optimizer/core/engine.py`:
```python
"""Core optimization engine — the autoimprove loop."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from asset_optimizer.core.convergence import create_strategy
from asset_optimizer.core.evaluation import EvaluationConfig
from asset_optimizer.providers.base import Criterion, Message, TextProvider
from asset_optimizer.scoring.ai_judge import AIJudgeScorer
from asset_optimizer.scoring.base import ScoreResult


@dataclass
class IterationResult:
    """Result of a single optimization iteration."""

    iteration: int
    input_content: str
    output_content: str
    input_score: float
    output_score: float
    scores: list[ScoreResult]
    improvement_prompt: str
    accepted: bool
    duration_ms: int


@dataclass
class OptimizationResult:
    """Final result of an optimization run."""

    best_content: str
    best_score: float
    initial_score: float
    total_iterations: int
    iterations: list[IterationResult] = field(default_factory=list)


_IMPROVE_SYSTEM = """You are an expert optimizer. Your task is to improve the given content based on evaluation feedback.
Return ONLY the improved content, with no explanation or commentary."""


def _build_improvement_prompt(
    content: str,
    scores: list[ScoreResult],
    evaluation: EvaluationConfig,
    history: list[IterationResult],
) -> str:
    """Build a focused improvement prompt targeting the lowest-scoring criteria."""
    sorted_scores = sorted(scores, key=lambda s: s.value)
    weakest = sorted_scores[:2] if len(sorted_scores) >= 2 else sorted_scores

    criteria_feedback = []
    for s in weakest:
        criterion = next((c for c in evaluation.criteria if c.name == s.criterion), None)
        rubric_text = f"\n  Rubric: {criterion.rubric}" if criterion and criterion.rubric else ""
        criteria_feedback.append(
            f"- {s.criterion}: scored {s.value}/{s.max_value}{rubric_text}"
        )

    history_notes = ""
    if history:
        last = history[-1]
        if not last.accepted:
            history_notes = "\nThe previous attempt was not accepted. Try a different approach."

    return (
        f"Improve the following content. Focus on these weak areas:\n"
        f"{''.join(criteria_feedback)}\n"
        f"{history_notes}\n"
        f"Current content:\n{content}"
    )


class Engine:
    """Core optimization engine implementing the autoimprove loop."""

    def __init__(
        self,
        provider: TextProvider,
        judge_provider: TextProvider | None = None,
    ) -> None:
        self._provider = provider
        self._judge = judge_provider or provider

    async def optimize(
        self,
        content: str,
        evaluation: EvaluationConfig,
        max_iterations: int = 20,
        target_score: float | None = None,
        convergence_strategy: str = "greedy",
        stagnation_limit: int = 5,
        min_improvement: float = 0.01,
        on_iteration: Callable[[dict[str, Any]], None] | None = None,
    ) -> OptimizationResult:
        """Run the optimization loop."""
        # Build convergence strategy
        strategy_kwargs: dict[str, Any] = {}
        if convergence_strategy == "greedy":
            strategy_kwargs = {"stagnation_limit": stagnation_limit, "min_improvement": min_improvement}
        elif convergence_strategy == "target" and target_score is not None:
            strategy_kwargs = {"target_score": target_score}
        strategy = create_strategy(convergence_strategy, **strategy_kwargs)

        # Build scorer
        criteria = [
            Criterion(name=c.name, description=c.description, max_score=c.max_score, rubric=c.rubric)
            for c in evaluation.criteria
        ]
        scorer = AIJudgeScorer(provider=self._judge, criteria=criteria)

        # Score baseline
        baseline_scores = await scorer.score(content)
        baseline_score = self._composite_score(baseline_scores)

        best_content = content
        best_score = baseline_score
        current_content = content
        current_score = baseline_score
        iterations: list[IterationResult] = []

        for i in range(1, max_iterations + 1):
            start_time = time.monotonic()

            # Generate improvement prompt
            improvement_prompt = _build_improvement_prompt(
                current_content, baseline_scores if i == 1 else iterations[-1].scores, evaluation, iterations
            )

            # Get improved content from provider
            messages = [
                Message(role="system", content=_IMPROVE_SYSTEM),
                Message(role="user", content=improvement_prompt),
            ]
            improved_content = await self._provider.complete(messages)

            # Score improved content
            improved_scores = await scorer.score(improved_content)
            improved_score = self._composite_score(improved_scores)

            duration_ms = int((time.monotonic() - start_time) * 1000)

            accepted = improved_score > current_score + min_improvement
            iteration_result = IterationResult(
                iteration=i,
                input_content=current_content,
                output_content=improved_content,
                input_score=current_score,
                output_score=improved_score,
                scores=improved_scores,
                improvement_prompt=improvement_prompt,
                accepted=accepted,
                duration_ms=duration_ms,
            )
            iterations.append(iteration_result)

            if accepted:
                current_content = improved_content
                current_score = improved_score
                if current_score > best_score:
                    best_content = current_content
                    best_score = current_score

            if on_iteration:
                on_iteration({
                    "iteration": i,
                    "score": improved_score,
                    "accepted": accepted,
                    "best_score": best_score,
                })

            convergence = strategy.check(i, current_score, current_score if not accepted else current_score - (improved_score - current_score), max_iterations)
            if not convergence.should_continue:
                break

        return OptimizationResult(
            best_content=best_content,
            best_score=best_score,
            initial_score=baseline_score,
            total_iterations=len(iterations),
            iterations=iterations,
        )

    @staticmethod
    def _composite_score(scores: list[ScoreResult]) -> float:
        """Calculate simple average of all scores."""
        if not scores:
            return 0.0
        total = sum(s.value for s in scores)
        return round(total / len(scores), 2)
```

- [ ] **Step 8: Run engine tests**

Run: `uv run pytest tests/unit/test_engine.py -v`
Expected: All tests PASS.

- [ ] **Step 9: Update public API exports**

Update `src/asset_optimizer/__init__.py`:
```python
"""Asset Optimizer — automatic asset optimization using the autoimprove pattern."""

from asset_optimizer.core.engine import Engine, OptimizationResult
from asset_optimizer.core.evaluation import EvaluationConfig, load_evaluation

__all__ = ["Engine", "EvaluationConfig", "OptimizationResult", "load_evaluation"]
__version__ = "0.1.0"
```

- [ ] **Step 10: Run full suite, lint, type check**

Run: `uv run pytest tests/ -v && uv run ruff check src/ tests/ && uv run mypy src/asset_optimizer/`
Expected: All pass.

- [ ] **Step 11: Commit**

```bash
git add src/asset_optimizer/core/ src/asset_optimizer/__init__.py tests/unit/test_convergence.py tests/unit/test_engine.py
git commit -m "feat: add optimization engine with convergence strategies"
```

---

## Phase 4: API Layer

### Task 9: REST API

**Files:**
- Create: `src/asset_optimizer/api/__init__.py`
- Create: `src/asset_optimizer/api/app.py`
- Create: `src/asset_optimizer/api/deps.py`
- Create: `src/asset_optimizer/api/schemas.py`
- Create: `src/asset_optimizer/api/routes/__init__.py`
- Create: `src/asset_optimizer/api/routes/health.py`
- Create: `src/asset_optimizer/api/routes/evaluations.py`
- Create: `src/asset_optimizer/api/routes/experiments.py`
- Create: `src/asset_optimizer/api/routes/providers.py`
- Create: `tests/unit/test_api.py`

- [ ] **Step 1: Write failing tests for API**

`tests/unit/test_api.py`:
```python
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from asset_optimizer.api.app import create_app


@pytest.fixture
async def client(tmp_path):
    app = create_app(db_path=tmp_path / "test.db")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


class TestHealthRoutes:
    @pytest.mark.asyncio
    async def test_health(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_readiness(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/health/ready")
        assert resp.status_code == 200


class TestEvaluationRoutes:
    @pytest.mark.asyncio
    async def test_create_evaluation(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/evaluations", json={
            "name": "test-eval",
            "asset_type": "prompt",
            "criteria": [{"name": "clarity", "description": "Is it clear?"}],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "test-eval"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_list_evaluations(self, client: AsyncClient) -> None:
        await client.post("/api/v1/evaluations", json={
            "name": "eval-1", "asset_type": "prompt",
            "criteria": [{"name": "c1", "description": "d1"}],
        })
        resp = await client.get("/api/v1/evaluations")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_evaluation(self, client: AsyncClient) -> None:
        create_resp = await client.post("/api/v1/evaluations", json={
            "name": "eval-get", "asset_type": "prompt",
            "criteria": [{"name": "c1", "description": "d1"}],
        })
        eval_id = create_resp.json()["id"]
        resp = await client.get(f"/api/v1/evaluations/{eval_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "eval-get"

    @pytest.mark.asyncio
    async def test_get_evaluation_not_found(self, client: AsyncClient) -> None:
        resp = await client.get(f"/api/v1/evaluations/{uuid.uuid4()}")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_evaluation(self, client: AsyncClient) -> None:
        create_resp = await client.post("/api/v1/evaluations", json={
            "name": "eval-del", "asset_type": "prompt",
            "criteria": [{"name": "c1", "description": "d1"}],
        })
        eval_id = create_resp.json()["id"]
        resp = await client.delete(f"/api/v1/evaluations/{eval_id}")
        assert resp.status_code == 204

        resp = await client.get(f"/api/v1/evaluations/{eval_id}")
        assert resp.status_code == 404


class TestExperimentRoutes:
    @pytest.mark.asyncio
    async def test_create_experiment(self, client: AsyncClient) -> None:
        eval_resp = await client.post("/api/v1/evaluations", json={
            "name": "exp-eval", "asset_type": "prompt",
            "criteria": [{"name": "c1", "description": "d1"}],
        })
        eval_id = eval_resp.json()["id"]

        resp = await client.post("/api/v1/experiments", json={
            "name": "test-exp",
            "asset_type": "prompt",
            "evaluation_id": eval_id,
            "config": {"max_iterations": 5},
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "test-exp"
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_list_experiments(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/experiments")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_api.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement API schemas**

`src/asset_optimizer/api/__init__.py`:
```python
"""FastAPI REST API for Asset Optimizer."""
```

`src/asset_optimizer/api/schemas.py`:
```python
"""Pydantic schemas for API request/response models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


# --- Evaluations ---

class CriterionCreate(BaseModel):
    name: str
    description: str
    max_score: float = 10.0
    rubric: str = ""


class EvaluationCreate(BaseModel):
    name: str
    asset_type: str
    description: str = ""
    criteria: list[CriterionCreate]
    scorer_config: dict[str, Any] = {}


class EvaluationResponse(BaseModel):
    id: str
    name: str
    asset_type: str
    description: str
    criteria: list[dict[str, Any]]
    scorer_config: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Experiments ---

class ExperimentCreate(BaseModel):
    name: str
    description: str = ""
    asset_type: str
    evaluation_id: str
    provider_config: dict[str, Any] = {}
    config: dict[str, Any] = {}


class ExperimentResponse(BaseModel):
    id: str
    name: str
    description: str | None
    asset_type: str
    evaluation_id: str
    status: str
    config: dict[str, Any]
    best_score: float | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Iterations ---

class IterationResponse(BaseModel):
    id: str
    experiment_id: str
    number: int
    status: str
    strategy_used: str
    improvement_prompt: str | None
    feedback: str | None
    created_at: datetime
    duration_ms: int | None

    model_config = {"from_attributes": True}


# --- Health ---

class HealthResponse(BaseModel):
    status: str
    version: str
```

- [ ] **Step 4: Implement dependency injection**

`src/asset_optimizer/api/deps.py`:
```python
"""FastAPI dependency injection — database sessions and repositories."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from asset_optimizer.storage.database import create_engine_from_config, get_session_factory
from asset_optimizer.storage.models import Base
from asset_optimizer.storage.repository import Repository

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


async def init_db(db_path: Path | None = None) -> None:
    """Initialize the database engine and create tables."""
    global _engine, _session_factory
    _engine = create_engine_from_config("sqlite", sqlite_path=db_path)
    _session_factory = get_session_factory(_engine)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close the database engine."""
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None


async def get_repository() -> AsyncGenerator[Repository, None]:
    """Yield a Repository with a session that auto-closes."""
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    async with _session_factory() as session:
        yield Repository(session)
```

- [ ] **Step 5: Implement route modules**

`src/asset_optimizer/api/routes/__init__.py`:
```python
"""API route modules."""
```

`src/asset_optimizer/api/routes/health.py`:
```python
"""Health check endpoints."""

from fastapi import APIRouter

from asset_optimizer import __version__
from asset_optimizer.api.schemas import HealthResponse

router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)


@router.get("/ready", response_model=HealthResponse)
async def readiness() -> HealthResponse:
    return HealthResponse(status="ok", version=__version__)
```

`src/asset_optimizer/api/routes/evaluations.py`:
```python
"""Evaluation CRUD endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException

from asset_optimizer.api.deps import get_repository
from asset_optimizer.api.schemas import EvaluationCreate, EvaluationResponse
from asset_optimizer.storage.models import Evaluation
from asset_optimizer.storage.repository import Repository

router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])


def _to_response(e: Evaluation) -> EvaluationResponse:
    return EvaluationResponse(
        id=str(e.id),
        name=e.name,
        asset_type=e.asset_type,
        description=e.description or "",
        criteria=e.criteria,
        scorer_config=e.scorer_config,
        created_at=e.created_at,
        updated_at=e.updated_at,
    )


@router.post("", response_model=EvaluationResponse, status_code=201)
async def create_evaluation(
    body: EvaluationCreate,
    repo: Repository = Depends(get_repository),
) -> EvaluationResponse:
    evaluation = Evaluation(
        name=body.name,
        asset_type=body.asset_type,
        criteria=[c.model_dump() for c in body.criteria],
        scorer_config=body.scorer_config,
    )
    created = await repo.create_evaluation(evaluation)
    return _to_response(created)


@router.get("", response_model=list[EvaluationResponse])
async def list_evaluations(
    asset_type: str | None = None,
    repo: Repository = Depends(get_repository),
) -> list[EvaluationResponse]:
    evaluations = await repo.list_evaluations(asset_type=asset_type)
    return [_to_response(e) for e in evaluations]


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: str,
    repo: Repository = Depends(get_repository),
) -> EvaluationResponse:
    evaluation = await repo.get_evaluation(uuid.UUID(evaluation_id))
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return _to_response(evaluation)


@router.delete("/{evaluation_id}", status_code=204)
async def delete_evaluation(
    evaluation_id: str,
    repo: Repository = Depends(get_repository),
) -> None:
    deleted = await repo.delete_evaluation(uuid.UUID(evaluation_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Evaluation not found")
```

`src/asset_optimizer/api/routes/experiments.py`:
```python
"""Experiment CRUD and lifecycle endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException

from asset_optimizer.api.deps import get_repository
from asset_optimizer.api.schemas import ExperimentCreate, ExperimentResponse
from asset_optimizer.storage.models import Experiment
from asset_optimizer.storage.repository import Repository

router = APIRouter(prefix="/api/v1/experiments", tags=["experiments"])


def _to_response(e: Experiment) -> ExperimentResponse:
    return ExperimentResponse(
        id=str(e.id),
        name=e.name,
        description=e.description,
        asset_type=e.asset_type,
        evaluation_id=str(e.evaluation_id),
        status=e.status.value,
        config=e.config,
        best_score=e.best_score,
        created_at=e.created_at,
        updated_at=e.updated_at,
    )


@router.post("", response_model=ExperimentResponse, status_code=201)
async def create_experiment(
    body: ExperimentCreate,
    repo: Repository = Depends(get_repository),
) -> ExperimentResponse:
    experiment = Experiment(
        name=body.name,
        description=body.description or None,
        asset_type=body.asset_type,
        evaluation_id=uuid.UUID(body.evaluation_id),
        provider_config=body.provider_config,
        config=body.config,
    )
    created = await repo.create_experiment(experiment)
    return _to_response(created)


@router.get("", response_model=list[ExperimentResponse])
async def list_experiments(
    status: str | None = None,
    asset_type: str | None = None,
    repo: Repository = Depends(get_repository),
) -> list[ExperimentResponse]:
    from asset_optimizer.storage.models import ExperimentStatus
    status_filter = ExperimentStatus(status) if status else None
    experiments = await repo.list_experiments(status=status_filter, asset_type=asset_type)
    return [_to_response(e) for e in experiments]


@router.get("/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(
    experiment_id: str,
    repo: Repository = Depends(get_repository),
) -> ExperimentResponse:
    experiment = await repo.get_experiment(uuid.UUID(experiment_id))
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return _to_response(experiment)


@router.delete("/{experiment_id}", status_code=204)
async def delete_experiment(
    experiment_id: str,
    repo: Repository = Depends(get_repository),
) -> None:
    deleted = await repo.delete_experiment(uuid.UUID(experiment_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Experiment not found")
```

`src/asset_optimizer/api/routes/providers.py`:
```python
"""Provider information endpoints."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/providers", tags=["providers"])


@router.get("")
async def list_providers() -> dict[str, list[str]]:
    return {
        "text": ["openai", "claude", "gemini", "vllm", "ollama"],
        "image": ["openai_image", "nano_banana"],
    }
```

- [ ] **Step 6: Implement app factory**

`src/asset_optimizer/api/app.py`:
```python
"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from asset_optimizer.api.deps import close_db, init_db
from asset_optimizer.api.routes import evaluations, experiments, health, providers


def create_app(db_path: Path | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        await init_db(db_path=db_path)
        yield
        await close_db()

    app = FastAPI(
        title="Asset Optimizer",
        description="Automatic asset optimization using the autoimprove pattern",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(evaluations.router)
    app.include_router(experiments.router)
    app.include_router(providers.router)

    return app
```

- [ ] **Step 7: Run API tests**

Run: `uv run pytest tests/unit/test_api.py -v`
Expected: All tests PASS.

- [ ] **Step 8: Run full suite, lint, type check**

Run: `uv run pytest tests/ -v && uv run ruff check src/ tests/ && uv run mypy src/asset_optimizer/`
Expected: All pass.

- [ ] **Step 9: Commit**

```bash
git add src/asset_optimizer/api/ tests/unit/test_api.py
git commit -m "feat: add FastAPI REST API with evaluation and experiment endpoints"
```

---

## Phase 5: CLI

### Task 10: CLI Application

**Files:**
- Create: `src/asset_optimizer/cli/__init__.py`
- Create: `src/asset_optimizer/cli/main.py`
- Create: `tests/unit/test_cli.py`

- [ ] **Step 1: Write failing tests for CLI**

`tests/unit/test_cli.py`:
```python
from typer.testing import CliRunner

from asset_optimizer.cli.main import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Asset Optimizer" in result.stdout


def test_serve_help() -> None:
    result = runner.invoke(app, ["serve", "--help"])
    assert result.exit_code == 0
    assert "--port" in result.stdout


def test_evaluations_list_help() -> None:
    result = runner.invoke(app, ["evaluations", "list", "--help"])
    assert result.exit_code == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_cli.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement CLI**

`src/asset_optimizer/cli/__init__.py`:
```python
"""CLI interface for Asset Optimizer."""
```

`src/asset_optimizer/cli/main.py`:
```python
"""Typer CLI application for Asset Optimizer."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from asset_optimizer import __version__

app = typer.Typer(
    name="asset-optimizer",
    help="Asset Optimizer — automatic asset optimization using the autoimprove pattern.",
    no_args_is_help=True,
)
console = Console()

evaluations_app = typer.Typer(help="Manage evaluations")
experiments_app = typer.Typer(help="Manage experiments")
providers_app = typer.Typer(help="Manage AI providers")

app.add_typer(evaluations_app, name="evaluations")
app.add_typer(experiments_app, name="experiments")
app.add_typer(providers_app, name="providers")


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"asset-optimizer {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-v", callback=_version_callback, is_eager=True),
) -> None:
    """Asset Optimizer CLI."""
    pass


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(8000, help="Port to bind to"),
    reload: bool = typer.Option(False, help="Enable auto-reload for development"),
) -> None:
    """Start the web server."""
    import uvicorn
    from asset_optimizer.api.app import create_app

    console.print(f"Starting Asset Optimizer on {host}:{port}")
    app_instance = create_app()
    uvicorn.run(app_instance, host=host, port=port, reload=reload)


@app.command()
def init(
    directory: Path = typer.Argument(Path("."), help="Directory to initialize"),
) -> None:
    """Initialize a new Asset Optimizer project."""
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "assets").mkdir(exist_ok=True)
    (directory / "evaluations").mkdir(exist_ok=True)
    (directory / "data").mkdir(exist_ok=True)

    config_file = directory / "asset-optimizer.yaml"
    if not config_file.exists():
        config_file.write_text(
            "# Asset Optimizer Configuration\n"
            "# See asset-optimizer.yaml.example for full options.\n\n"
            "storage:\n  backend: sqlite\n  sqlite_path: ./data/optimizer.db\n\n"
            "server:\n  host: 0.0.0.0\n  port: 8000\n\n"
            "defaults:\n  max_iterations: 20\n  convergence_strategy: greedy\n"
        )

    console.print(f"[green]Initialized Asset Optimizer project in {directory}[/green]")


@evaluations_app.command("list")
def evaluations_list() -> None:
    """List all evaluations."""
    console.print("Evaluations listing requires a running server or database.")
    console.print("Use: asset-optimizer serve, then visit the web UI.")


@evaluations_app.command("show")
def evaluations_show(name: str = typer.Argument(..., help="Evaluation name")) -> None:
    """Show evaluation details."""
    console.print(f"Evaluation: {name}")


@experiments_app.command("list")
def experiments_list() -> None:
    """List all experiments."""
    console.print("Experiments listing requires a running server or database.")


@experiments_app.command("show")
def experiments_show(experiment_id: str = typer.Argument(..., help="Experiment ID")) -> None:
    """Show experiment details."""
    console.print(f"Experiment: {experiment_id}")


@providers_app.command("test")
def providers_test(
    provider: str = typer.Option("openai", help="Provider name to test"),
) -> None:
    """Test provider connectivity."""
    console.print(f"Testing provider: {provider}")
    console.print("[yellow]Provider testing not yet implemented[/yellow]")
```

- [ ] **Step 4: Run CLI tests**

Run: `uv run pytest tests/unit/test_cli.py -v`
Expected: All tests PASS.

- [ ] **Step 5: Verify CLI runs**

Run: `uv run asset-optimizer --version`
Expected: `asset-optimizer 0.1.0`

Run: `uv run asset-optimizer --help`
Expected: Shows help text.

- [ ] **Step 6: Commit**

```bash
git add src/asset_optimizer/cli/ tests/unit/test_cli.py
git commit -m "feat: add Typer CLI with serve, init, and management commands"
```

---

## Phase 6: Web UI

### Task 11: React Project Setup

**Files:**
- Create: `ui/package.json`
- Create: `ui/tsconfig.json`
- Create: `ui/vite.config.ts`
- Create: `ui/tailwind.config.ts`
- Create: `ui/postcss.config.js`
- Create: `ui/index.html`
- Create: `ui/src/main.tsx`
- Create: `ui/src/App.tsx`
- Create: `ui/src/index.css`
- Create: `ui/src/api/client.ts`

- [ ] **Step 1: Initialize React project with Vite**

Run from project root:
```bash
cd ui && npm create vite@latest . -- --template react-ts && npm install && npm install -D tailwindcss @tailwindcss/vite && npm install react-router-dom @tanstack/react-query recharts
```

- [ ] **Step 2: Configure Tailwind**

`ui/vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/ws': { target: 'ws://localhost:8000', ws: true },
    },
  },
})
```

`ui/src/index.css`:
```css
@import "tailwindcss";
```

- [ ] **Step 3: Set up routing and app shell**

`ui/src/App.tsx`:
```tsx
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient()

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-3">
        <div className="flex items-center gap-6">
          <Link to="/" className="text-lg font-semibold text-gray-900">Asset Optimizer</Link>
          <Link to="/experiments" className="text-gray-600 hover:text-gray-900">Experiments</Link>
          <Link to="/evaluations" className="text-gray-600 hover:text-gray-900">Evaluations</Link>
          <Link to="/providers" className="text-gray-600 hover:text-gray-900">Providers</Link>
        </div>
      </nav>
      <main className="p-6">{children}</main>
    </div>
  )
}

function Dashboard() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-4">Dashboard</h1>
      <p className="text-gray-600">Welcome to Asset Optimizer.</p>
    </div>
  )
}

function Placeholder({ title }: { title: string }) {
  return <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/experiments" element={<Placeholder title="Experiments" />} />
            <Route path="/evaluations" element={<Placeholder title="Evaluations" />} />
            <Route path="/providers" element={<Placeholder title="Providers" />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
```

- [ ] **Step 4: Create API client**

`ui/src/api/client.ts`:
```typescript
const BASE_URL = '/api/v1'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!resp.ok) {
    throw new Error(`API error: ${resp.status} ${resp.statusText}`)
  }
  if (resp.status === 204) return undefined as T
  return resp.json()
}

export interface Evaluation {
  id: string
  name: string
  asset_type: string
  description: string
  criteria: Array<{ name: string; description: string; max_score: number }>
  scorer_config: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface Experiment {
  id: string
  name: string
  description: string | null
  asset_type: string
  evaluation_id: string
  status: string
  config: Record<string, unknown>
  best_score: number | null
  created_at: string
  updated_at: string
}

export const api = {
  health: () => request<{ status: string; version: string }>('/health'),

  evaluations: {
    list: () => request<Evaluation[]>('/evaluations'),
    get: (id: string) => request<Evaluation>(`/evaluations/${id}`),
    create: (data: Partial<Evaluation>) => request<Evaluation>('/evaluations', { method: 'POST', body: JSON.stringify(data) }),
    delete: (id: string) => request<void>(`/evaluations/${id}`, { method: 'DELETE' }),
  },

  experiments: {
    list: () => request<Experiment[]>('/experiments'),
    get: (id: string) => request<Experiment>(`/experiments/${id}`),
    create: (data: Partial<Experiment>) => request<Experiment>('/experiments', { method: 'POST', body: JSON.stringify(data) }),
    delete: (id: string) => request<void>(`/experiments/${id}`, { method: 'DELETE' }),
  },

  providers: {
    list: () => request<{ text: string[]; image: string[] }>('/providers'),
  },
}
```

- [ ] **Step 5: Verify UI builds**

Run: `cd ui && npm run build`
Expected: Build succeeds, output in `ui/dist/`.

- [ ] **Step 6: Commit**

```bash
git add ui/
git commit -m "feat: scaffold React UI with routing, Tailwind, and API client"
```

---

### Task 12: UI Pages — Dashboard & Experiments

**Files:**
- Create: `ui/src/pages/Dashboard.tsx`
- Create: `ui/src/pages/ExperimentList.tsx`
- Create: `ui/src/pages/ExperimentDetail.tsx`
- Create: `ui/src/components/StatusBadge.tsx`
- Create: `ui/src/components/ScoreChart.tsx`
- Modify: `ui/src/App.tsx`

- [ ] **Step 1: Create StatusBadge component**

`ui/src/components/StatusBadge.tsx`:
```tsx
const colors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  running: 'bg-blue-100 text-blue-800',
  paused: 'bg-gray-100 text-gray-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  cancelled: 'bg-gray-100 text-gray-500',
}

export function StatusBadge({ status }: { status: string }) {
  const cls = colors[status] || 'bg-gray-100 text-gray-800'
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${cls}`}>
      {status}
    </span>
  )
}
```

- [ ] **Step 2: Create ScoreChart component**

`ui/src/components/ScoreChart.tsx`:
```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface ScoreDataPoint {
  iteration: number
  score: number
  [key: string]: number
}

export function ScoreChart({ data }: { data: ScoreDataPoint[] }) {
  if (!data.length) return <p className="text-gray-500">No data yet.</p>

  const keys = Object.keys(data[0]).filter(k => k !== 'iteration')
  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="iteration" />
        <YAxis domain={[0, 10]} />
        <Tooltip />
        <Legend />
        {keys.map((key, i) => (
          <Line key={key} type="monotone" dataKey={key} stroke={colors[i % colors.length]} strokeWidth={2} />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
```

- [ ] **Step 3: Create Dashboard page**

`ui/src/pages/Dashboard.tsx`:
```tsx
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api, Experiment } from '../api/client'
import { StatusBadge } from '../components/StatusBadge'

export function Dashboard() {
  const { data: experiments } = useQuery({ queryKey: ['experiments'], queryFn: api.experiments.list })
  const { data: health } = useQuery({ queryKey: ['health'], queryFn: api.health })

  const recent = experiments?.slice(0, 5) || []
  const active = experiments?.filter(e => e.status === 'running') || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <div className="text-sm text-gray-500">
          {health ? `v${health.version} — ${health.status}` : 'Connecting...'}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Total Experiments</div>
          <div className="text-2xl font-bold">{experiments?.length || 0}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Active</div>
          <div className="text-2xl font-bold text-blue-600">{active.length}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Completed</div>
          <div className="text-2xl font-bold text-green-600">
            {experiments?.filter(e => e.status === 'completed').length || 0}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg border">
        <div className="px-4 py-3 border-b">
          <h2 className="font-semibold">Recent Experiments</h2>
        </div>
        {recent.length === 0 ? (
          <p className="p-4 text-gray-500">No experiments yet. Create one to get started.</p>
        ) : (
          <ul className="divide-y">
            {recent.map(exp => (
              <li key={exp.id} className="px-4 py-3 flex items-center justify-between">
                <div>
                  <Link to={`/experiments/${exp.id}`} className="font-medium text-blue-600 hover:underline">
                    {exp.name}
                  </Link>
                  <span className="ml-2 text-sm text-gray-500">{exp.asset_type}</span>
                </div>
                <div className="flex items-center gap-3">
                  {exp.best_score !== null && (
                    <span className="text-sm font-mono">{exp.best_score.toFixed(2)}</span>
                  )}
                  <StatusBadge status={exp.status} />
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Create ExperimentList page**

`ui/src/pages/ExperimentList.tsx`:
```tsx
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { StatusBadge } from '../components/StatusBadge'

export function ExperimentList() {
  const { data: experiments, isLoading } = useQuery({ queryKey: ['experiments'], queryFn: api.experiments.list })

  if (isLoading) return <p>Loading...</p>

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Experiments</h1>
      </div>

      <div className="bg-white rounded-lg border">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Best Score</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {experiments?.map(exp => (
              <tr key={exp.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <Link to={`/experiments/${exp.id}`} className="text-blue-600 hover:underline font-medium">
                    {exp.name}
                  </Link>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">{exp.asset_type}</td>
                <td className="px-4 py-3"><StatusBadge status={exp.status} /></td>
                <td className="px-4 py-3 text-sm font-mono">
                  {exp.best_score !== null ? exp.best_score.toFixed(2) : '—'}
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {new Date(exp.created_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
```

- [ ] **Step 5: Create ExperimentDetail page**

`ui/src/pages/ExperimentDetail.tsx`:
```tsx
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { StatusBadge } from '../components/StatusBadge'
import { ScoreChart } from '../components/ScoreChart'

export function ExperimentDetail() {
  const { id } = useParams<{ id: string }>()
  const { data: experiment, isLoading } = useQuery({
    queryKey: ['experiment', id],
    queryFn: () => api.experiments.get(id!),
    enabled: !!id,
  })

  if (isLoading) return <p>Loading...</p>
  if (!experiment) return <p>Experiment not found.</p>

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <h1 className="text-2xl font-bold text-gray-900">{experiment.name}</h1>
        <StatusBadge status={experiment.status} />
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Asset Type</div>
          <div className="font-semibold">{experiment.asset_type}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Best Score</div>
          <div className="text-xl font-bold">
            {experiment.best_score !== null ? experiment.best_score.toFixed(2) : '—'}
          </div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Max Iterations</div>
          <div className="font-semibold">{(experiment.config as any)?.max_iterations || '—'}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Created</div>
          <div className="font-semibold">{new Date(experiment.created_at).toLocaleDateString()}</div>
        </div>
      </div>

      <div className="bg-white rounded-lg border p-4">
        <h2 className="font-semibold mb-4">Score Progression</h2>
        <ScoreChart data={[]} />
      </div>

      {experiment.description && (
        <div className="bg-white rounded-lg border p-4">
          <h2 className="font-semibold mb-2">Description</h2>
          <p className="text-gray-600">{experiment.description}</p>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 6: Update App.tsx with real pages**

Replace the content of `ui/src/App.tsx`:
```tsx
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Dashboard } from './pages/Dashboard'
import { ExperimentList } from './pages/ExperimentList'
import { ExperimentDetail } from './pages/ExperimentDetail'

const queryClient = new QueryClient()

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-3">
        <div className="flex items-center gap-6">
          <Link to="/" className="text-lg font-semibold text-gray-900">Asset Optimizer</Link>
          <Link to="/experiments" className="text-gray-600 hover:text-gray-900">Experiments</Link>
          <Link to="/evaluations" className="text-gray-600 hover:text-gray-900">Evaluations</Link>
          <Link to="/providers" className="text-gray-600 hover:text-gray-900">Providers</Link>
        </div>
      </nav>
      <main className="p-6">{children}</main>
    </div>
  )
}

function Placeholder({ title }: { title: string }) {
  return <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/experiments" element={<ExperimentList />} />
            <Route path="/experiments/:id" element={<ExperimentDetail />} />
            <Route path="/evaluations" element={<Placeholder title="Evaluations" />} />
            <Route path="/providers" element={<Placeholder title="Providers" />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
```

- [ ] **Step 7: Verify build**

Run: `cd ui && npm run build`
Expected: Build succeeds.

- [ ] **Step 8: Commit**

```bash
git add ui/src/
git commit -m "feat: add Dashboard, ExperimentList, and ExperimentDetail UI pages"
```

---

### Task 13: UI Pages — Evaluations & Providers

**Files:**
- Create: `ui/src/pages/EvaluationList.tsx`
- Create: `ui/src/pages/ProviderSettings.tsx`
- Modify: `ui/src/App.tsx`

- [ ] **Step 1: Create EvaluationList page**

`ui/src/pages/EvaluationList.tsx`:
```tsx
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

export function EvaluationList() {
  const { data: evaluations, isLoading } = useQuery({ queryKey: ['evaluations'], queryFn: api.evaluations.list })

  if (isLoading) return <p>Loading...</p>

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-900">Evaluations</h1>

      <div className="bg-white rounded-lg border">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Asset Type</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Criteria</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {evaluations?.map(ev => (
              <tr key={ev.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{ev.name}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{ev.asset_type}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{ev.criteria.length} criteria</td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {new Date(ev.created_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {(!evaluations || evaluations.length === 0) && (
          <p className="p-4 text-gray-500">No evaluations yet.</p>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Create ProviderSettings page**

`ui/src/pages/ProviderSettings.tsx`:
```tsx
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

export function ProviderSettings() {
  const { data: providers, isLoading } = useQuery({ queryKey: ['providers'], queryFn: api.providers.list })

  if (isLoading) return <p>Loading...</p>

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Providers</h1>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border p-4">
          <h2 className="font-semibold mb-3">Text Providers</h2>
          <ul className="space-y-2">
            {providers?.text.map(name => (
              <li key={name} className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-gray-300" />
                <span className="text-sm">{name}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white rounded-lg border p-4">
          <h2 className="font-semibold mb-3">Image Providers</h2>
          <ul className="space-y-2">
            {providers?.image.map(name => (
              <li key={name} className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-gray-300" />
                <span className="text-sm">{name}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Update App.tsx routes**

In `ui/src/App.tsx`, add imports and replace Placeholder routes:

Add imports:
```tsx
import { EvaluationList } from './pages/EvaluationList'
import { ProviderSettings } from './pages/ProviderSettings'
```

Replace the Placeholder routes:
```tsx
<Route path="/evaluations" element={<EvaluationList />} />
<Route path="/providers" element={<ProviderSettings />} />
```

- [ ] **Step 4: Verify build**

Run: `cd ui && npm run build`
Expected: Build succeeds.

- [ ] **Step 5: Commit**

```bash
git add ui/src/
git commit -m "feat: add Evaluations and Provider Settings UI pages"
```

---

## Phase 7: Operations & Polish

### Task 14: Deployment

**Files:**
- Create: `deploy/Dockerfile`
- Create: `deploy/helm/asset-optimizer/Chart.yaml`
- Create: `deploy/helm/asset-optimizer/values.yaml`
- Create: `deploy/helm/asset-optimizer/templates/deployment.yaml`
- Create: `deploy/helm/asset-optimizer/templates/service.yaml`
- Create: `deploy/openshift/deployment.yaml`

- [ ] **Step 1: Create Dockerfile**

`deploy/Dockerfile`:
```dockerfile
# Stage 1: Build UI
FROM node:20-alpine AS ui-build
WORKDIR /app/ui
COPY ui/package.json ui/package-lock.json ./
RUN npm ci
COPY ui/ ./
RUN npm run build

# Stage 2: Python application
FROM python:3.12-slim

# Create non-root user (required by OpenShift)
RUN useradd -r -u 1001 -m optimizer

WORKDIR /app

# Install UV and dependencies
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --no-dev --no-editable

# Copy application code
COPY src/ src/

# Copy built UI assets
COPY --from=ui-build /app/ui/dist src/asset_optimizer/static/

# Switch to non-root user
USER 1001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

CMD ["uv", "run", "asset-optimizer", "serve", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Create Helm chart**

`deploy/helm/asset-optimizer/Chart.yaml`:
```yaml
apiVersion: v2
name: asset-optimizer
description: Automatic asset optimization using the autoimprove pattern
type: application
version: 0.1.0
appVersion: "0.1.0"
```

`deploy/helm/asset-optimizer/values.yaml`:
```yaml
replicaCount: 1

image:
  repository: asset-optimizer
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8000

resources:
  limits:
    cpu: "1"
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

env: []
# - name: ANTHROPIC_API_KEY
#   valueFrom:
#     secretKeyRef:
#       name: asset-optimizer-secrets
#       key: anthropic-api-key

persistence:
  enabled: true
  size: 1Gi
  storageClass: ""

ingress:
  enabled: false
  host: ""
```

`deploy/helm/asset-optimizer/templates/deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}
  labels:
    app: {{ .Release.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
      containers:
        - name: asset-optimizer
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - containerPort: 8000
          env:
            {{- range .Values.env }}
            - name: {{ .name }}
              {{- if .value }}
              value: {{ .value | quote }}
              {{- end }}
              {{- if .valueFrom }}
              valueFrom:
                {{- toYaml .valueFrom | nindent 16 }}
              {{- end }}
            {{- end }}
          livenessProbe:
            httpGet:
              path: /api/v1/health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /api/v1/health/ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          {{- if .Values.persistence.enabled }}
          volumeMounts:
            - name: data
              mountPath: /app/data
          {{- end }}
      {{- if .Values.persistence.enabled }}
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: {{ .Release.Name }}-data
      {{- end }}
```

`deploy/helm/asset-optimizer/templates/service.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: 8000
      protocol: TCP
  selector:
    app: {{ .Release.Name }}
```

- [ ] **Step 3: Create OpenShift deployment**

`deploy/openshift/deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: asset-optimizer
  labels:
    app: asset-optimizer
spec:
  replicas: 1
  selector:
    matchLabels:
      app: asset-optimizer
  template:
    metadata:
      labels:
        app: asset-optimizer
    spec:
      securityContext:
        runAsNonRoot: true
      containers:
        - name: asset-optimizer
          image: asset-optimizer:latest
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: asset-optimizer-config
            - secretRef:
                name: asset-optimizer-secrets
          livenessProbe:
            httpGet:
              path: /api/v1/health
              port: 8000
            initialDelaySeconds: 10
          readinessProbe:
            httpGet:
              path: /api/v1/health/ready
              port: 8000
            initialDelaySeconds: 5
          resources:
            limits:
              cpu: "1"
              memory: 512Mi
            requests:
              cpu: 250m
              memory: 256Mi
---
apiVersion: v1
kind: Service
metadata:
  name: asset-optimizer
spec:
  ports:
    - port: 8000
      targetPort: 8000
  selector:
    app: asset-optimizer
```

- [ ] **Step 4: Commit**

```bash
git add deploy/
git commit -m "feat: add Dockerfile, Helm chart, and OpenShift deployment"
```

---

### Task 15: Skills, Rules, and Commands

**Files:**
- Create: `.claude/skills/create-evaluation.md`
- Create: `.claude/skills/score-and-review.md`
- Create: `.claude/skills/create-improvement-prompt.md`
- Create: `.claude/skills/register-asset-type.md`
- Create: `.claude/skills/dev-report.md`
- Create: `.claude/rules/development.md`
- Create: `.claude/rules/usage.md`
- Create: `.claude/commands/create-asset-type.md`
- Create: `.claude/commands/create-evaluation.md`
- Create: `.claude/commands/dev-report.md`
- Create: `.claude/commands/run-experiment.md`

- [ ] **Step 1: Create evaluation skill**

`.claude/skills/create-evaluation.md`:
```markdown
---
name: create-evaluation
description: Guide creation of well-structured evaluation criteria for any asset type
---

# Create Evaluation

## Process

1. **Identify the asset type** — What kind of asset will be evaluated? (prompt, skill, image, or custom)
2. **Define quality dimensions** — What aspects of quality matter? Use sequential thinking to explore dimensions.
3. **Write rubrics** — For each criterion, write concrete scoring anchors:
   - 1-3: Clearly failing (describe what this looks like)
   - 4-6: Acceptable but needs improvement (describe)
   - 7-9: Good quality (describe)
   - 10: Exceptional (describe)
4. **Configure scoring** — Set scorer type (heuristic, ai_judge, composite) and weights.
5. **Output YAML** — Write the evaluation to `evaluations/<name>.yaml`.

## Quality Checks

- Every rubric must have concrete, distinguishable levels (not just "good" vs "bad")
- Each criterion must be independently scorable
- Criteria should not overlap significantly
- The set of criteria should cover the key quality aspects for this asset type

## Template

```yaml
name: <evaluation-name>
asset_type: <prompt|skill|image|custom>
description: <what this evaluation measures>

criteria:
  - name: <criterion-name>
    description: "<what this measures>"
    max_score: 10
    rubric: |
      1-3: <failing description>
      4-6: <acceptable description>
      7-9: <good description>
      10: <exceptional description>

scorer_config:
  type: composite
  heuristic_weight: 0.2
  ai_judge_weight: 0.8
```
```

- [ ] **Step 2: Create score-and-review skill**

`.claude/skills/score-and-review.md`:
```markdown
---
name: score-and-review
description: Systematic scoring and feedback for asset improvements
---

# Score and Review

## Process

1. **Load both versions** — Read the before (input) and after (output) asset content
2. **Load evaluation** — Read the evaluation criteria and rubrics
3. **Score each criterion** — For each criterion in the evaluation:
   - Apply the rubric to the content
   - Assign a specific score with reasoning
   - Identify the specific parts of the content that justify the score
4. **Generate actionable feedback** — For each criterion:
   - Quote the specific part that needs improvement
   - Explain what's wrong and why it matters
   - Suggest a concrete fix (not vague "make it better")
5. **Produce structured output** — Return scores and feedback in structured format

## Rules

- Never give vague feedback like "improve clarity" — say exactly what's unclear and how to fix it
- Quote specific content when pointing out issues
- Score against the rubric levels, not on gut feeling
- Compare before/after to identify what improved and what regressed
```

- [ ] **Step 3: Create improvement prompt skill**

`.claude/skills/create-improvement-prompt.md`:
```markdown
---
name: create-improvement-prompt
description: Create high-quality prompts that drive the autoimprove loop
---

# Create Improvement Prompt

## Process

1. **Analyze current state** — Read the asset content and understand its purpose
2. **Review scores** — Identify the lowest-scoring criteria
3. **Target weaknesses** — Focus the improvement on the 2-3 weakest areas
4. **Write specific instructions** — Tell the improver exactly what to change
5. **Include anti-patterns** — List what NOT to do

## Anti-Patterns to Avoid

- "Make it better" — Too vague, no direction
- "Improve all criteria" — Unfocused, leads to mediocre changes
- Contradictory instructions — "Be more concise but add more detail"
- Scope creep — "Also add error handling and..." (stick to evaluation criteria)

## Template

```
Improve the following [asset type]. Focus on these weak areas:
- [criterion]: scored [X]/[max] — [specific feedback from rubric]
- [criterion]: scored [X]/[max] — [specific feedback from rubric]

Do NOT:
- [anti-pattern relevant to this asset]
- [anti-pattern relevant to this asset]

Current content:
[content]
```
```

- [ ] **Step 4: Create register-asset-type skill**

`.claude/skills/register-asset-type.md`:
```markdown
---
name: register-asset-type
description: Step-by-step guide for adding new asset types to the framework
---

# Register Asset Type

## Process (TDD)

1. **Write test file** — Create `tests/unit/test_<type>_asset.py` with tests for:
   - `name` and `file_extensions` attributes
   - `load()` from file
   - `save()` to file
   - `validate()` with valid and invalid content
   - `default_evaluation()` returns valid config
   - `render_for_prompt()` produces useful output

2. **Implement asset type** — Create `src/asset_optimizer/assets/<type>.py`:
   - Implement all methods from `AssetTypeProtocol`
   - Handle edge cases (empty files, invalid content)

3. **Create default evaluation** — Create `evaluations/<type>-default.yaml`:
   - Define 3-5 criteria specific to this asset type
   - Write rubrics with concrete scoring anchors

4. **Register in registry** — Add to `src/asset_optimizer/assets/registry.py` default_registry

5. **Run tests** — `uv run pytest tests/unit/test_<type>_asset.py -v`

6. **Update documentation** — Add to `docs/asset-types.md`
```

- [ ] **Step 5: Create dev-report skill**

`.claude/skills/dev-report.md`:
```markdown
---
name: dev-report
description: Generate standardized development work reports
---

# Dev Report

## Process

1. **Gather context:**
   - `git diff --stat HEAD~N` for files changed
   - `git log --oneline -N` for recent commits
   - Check test coverage changes

2. **Fill template** from `dev-reports/TEMPLATE.md`:
   - **Summary**: 1-2 sentences on what was accomplished
   - **Changes**: Bulleted list of changes with rationale
   - **Decisions**: Key decisions and why they were made
   - **Metrics**: Tests added, coverage delta, files changed count
   - **Next Steps**: What should happen next

3. **Save to** `dev-reports/YYYY-MM-DD-<topic>.md`

4. **Commit** the report

## Rules

- Keep it concise — the report supplements the git log, not replaces it
- Focus on decisions and rationale — the "why" behind changes
- Include metrics — numbers make progress tangible
```

- [ ] **Step 6: Create rules**

`.claude/rules/development.md`:
```markdown
# Development Rules

- All code must pass `uv run ruff check src/ tests/`, `uv run mypy src/asset_optimizer/`, and `uv run pytest` before committing
- TDD: write tests before implementation code
- Follow existing patterns in the codebase — check before adding new patterns
- Use UV for all dependency management (`uv add`, `uv sync`)
- All public functions must have type annotations
- Use `async/await` throughout the core engine
- Database access only through the repository layer (`storage/repository.py`)
- No direct SQL — use SQLAlchemy ORM
- Keep files focused — if a file grows beyond ~300 lines, consider splitting by responsibility
```

`.claude/rules/usage.md`:
```markdown
# Usage Rules

- Always validate provider connectivity before starting experiments
- Create baseline scores before optimization begins
- Warn if max_iterations > 50 (high cost potential)
- Never store API keys in config files — use environment variables (`${VAR_NAME}` syntax)
- All experiments must have an evaluation attached
- When creating evaluations, every rubric must have concrete scoring anchors at 4 levels
```

- [ ] **Step 7: Create commands**

`.claude/commands/create-asset-type.md`:
```markdown
---
name: create-asset-type
description: Scaffold a new asset type with tests, implementation, and evaluation
---

Invoke the `register-asset-type` skill to scaffold a new asset type. Ask for:
1. Asset type name (e.g., "config", "template", "script")
2. File extensions (e.g., [".yaml", ".yml"])
3. Key quality dimensions for evaluation

Then follow the skill's TDD process.
```

`.claude/commands/create-evaluation.md`:
```markdown
---
name: create-evaluation
description: Create a new evaluation configuration
---

Invoke the `create-evaluation` skill to build a new evaluation. Ask for:
1. What asset type this evaluation is for
2. What aspects of quality matter most
3. Whether to use heuristic scoring, AI-judged scoring, or both

Then follow the skill's process to output a YAML file.
```

`.claude/commands/dev-report.md`:
```markdown
---
name: dev-report
description: Generate a development work report
---

Invoke the `dev-report` skill. Gather recent git activity and produce a report following the template in `dev-reports/TEMPLATE.md`. Save to `dev-reports/` with today's date.
```

`.claude/commands/run-experiment.md`:
```markdown
---
name: run-experiment
description: Start an optimization experiment from the CLI
---

Guide the user through running an optimization:
1. Which asset file to optimize
2. Which evaluation to use (list available, or create new)
3. Which provider to use
4. Max iterations and convergence strategy

Then construct and run the CLI command:
```bash
asset-optimizer optimize <file> --evaluation <eval> --provider <provider> --iterations <N>
```
```

- [ ] **Step 8: Commit**

```bash
git add .claude/
git commit -m "feat: add skills, rules, and commands for development and usage workflows"
```

---

### Task 16: Documentation

**Files:**
- Create: `docs/getting-started.md`
- Create: `docs/architecture.md`
- Create: `docs/asset-types.md`
- Create: `docs/providers.md`
- Create: `docs/evaluations.md`
- Create: `docs/deployment.md`
- Create: `docs/api-reference.md`
- Create: `docs/library-usage.md`
- Create: `docs/extending.md`
- Create: `docs/development.md`

- [ ] **Step 1: Create getting-started guide**

`docs/getting-started.md`:
```markdown
# Getting Started

## Install

```bash
pip install asset-optimizer
# or with UV:
uv pip install asset-optimizer
```

## Quick Start

### 1. Initialize a project

```bash
asset-optimizer init my-project
cd my-project
```

This creates:
- `asset-optimizer.yaml` — configuration file
- `assets/` — place your assets here
- `evaluations/` — evaluation configurations
- `data/` — SQLite database (auto-created)

### 2. Configure a provider

Edit `asset-optimizer.yaml` and set your API key:

```yaml
providers:
  text:
    default: openai
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o
```

Set the environment variable:
```bash
export OPENAI_API_KEY=sk-...
```

### 3. Optimize a prompt

```bash
echo "You are a helpful assistant." > assets/prompt.txt
asset-optimizer optimize assets/prompt.txt --evaluation prompt-clarity --iterations 10
```

### 4. Use the web UI

```bash
asset-optimizer serve
# Open http://localhost:8000
```

## As a Python Library

```python
from asset_optimizer import Engine, load_evaluation
from asset_optimizer.providers.openai_provider import OpenAITextProvider

provider = OpenAITextProvider(api_key="sk-...", model="gpt-4o")
evaluation = load_evaluation("evaluations/prompt-clarity.yaml")
engine = Engine(provider=provider, judge_provider=provider)

result = await engine.optimize(
    content="You are a helpful assistant.",
    evaluation=evaluation,
    max_iterations=10,
)
print(f"Score: {result.initial_score} -> {result.best_score}")
print(result.best_content)
```
```

- [ ] **Step 2: Create remaining docs**

Create each doc file with content covering its topic. Each file should be 50-150 lines of practical documentation focused on "how to do X" rather than abstract descriptions.

`docs/architecture.md` — System components, data flow diagram, key design decisions.
`docs/asset-types.md` — Built-in types (prompt, skill, image), how to create custom types.
`docs/providers.md` — How to configure each provider with examples.
`docs/evaluations.md` — Creating evaluations, understanding scoring, rubric design.
`docs/deployment.md` — Docker build, Helm install, OpenShift deployment steps.
`docs/api-reference.md` — REST endpoint summary (supplements auto-generated OpenAPI).
`docs/library-usage.md` — Using as a Python library with code examples.
`docs/extending.md` — Adding asset types, providers, and scorers.
`docs/development.md` — Dev setup, testing, contributing conventions.

- [ ] **Step 3: Commit**

```bash
git add docs/
git commit -m "docs: add comprehensive documentation"
```

---

### Task 17: README & Final Polish

**Files:**
- Modify: `README.md`
- Modify: `src/asset_optimizer/__init__.py` (verify exports)
- Run: full test suite

- [ ] **Step 1: Write comprehensive README**

Replace `README.md` with a complete readme covering:
- Project description (2-3 sentences)
- Feature highlights (bulleted)
- Quick start (install + first optimization in 4 commands)
- Library usage example (5 lines of Python)
- Web UI screenshot placeholder
- Links to docs
- License

- [ ] **Step 2: Verify all exports work**

Run: `uv run python -c "from asset_optimizer import Engine, EvaluationConfig, OptimizationResult, load_evaluation; print('OK')"`
Expected: `OK`

- [ ] **Step 3: Run full test suite with coverage**

Run: `uv run pytest tests/ -v --cov=asset_optimizer --cov-report=term-missing`
Expected: All tests pass, reasonable coverage.

- [ ] **Step 4: Run lint and type check**

Run: `uv run ruff check src/ tests/ && uv run mypy src/asset_optimizer/`
Expected: No errors.

- [ ] **Step 5: Final commit**

```bash
git add README.md
git commit -m "docs: write comprehensive README"
```
