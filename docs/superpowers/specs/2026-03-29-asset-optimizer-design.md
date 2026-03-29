# Asset Optimizer — Design Specification

**Date**: 2026-03-29
**Status**: Approved

## 1. Overview

Asset Optimizer is a production-oriented Python application that formalizes the autoimprove pattern into a reusable framework for automatically optimizing different asset types. It supports prompts, skills, and images out of the box, with an extensible architecture for adding new asset types.

The system operates as both a standalone service (CLI + web UI + REST API) and an embeddable Python library, deployable on OpenShift or any container platform.

### Stated Assumptions

1. **Package manager**: UV — fastest, most modern Python tooling
2. **Web framework**: FastAPI — async-native, auto-generates OpenAPI docs, easy to embed
3. **UI framework**: React 18+ with TypeScript, Vite, Tailwind CSS
4. **Database**: SQLite for local/dev (zero-config), PostgreSQL for production, both via SQLAlchemy 2.0 + Alembic migrations
5. **Task execution**: Python asyncio with background task runner (no Celery unless horizontal scaling needed — interface is pluggable)
6. **Image optimization**: Optimizes the generation prompt, not the image pixels — generates, scores, refines the prompt, re-generates
7. **Autoimprove pattern**: Formalized as Target (what to improve) + Measure (how to score) + Improve (AI-driven iteration) loop
8. **Deployment**: Single container serves both API and built UI assets
9. **Nano Banana**: Accessed via HTTP API; OpenAI Image 01 via OpenAI SDK
10. **Dual-use**: The application is both a standalone service AND an importable Python library from day one

## 2. Architecture

### Entry Points

| Entry Point | Purpose |
|---|---|
| **Library** | `from asset_optimizer import Engine` — embed in any Python app |
| **CLI** | `asset-optimizer optimize ...` — command-line usage |
| **API Server** | `asset-optimizer serve` — RESTful API + WebSocket |
| **Web UI** | Served by the API server, built React dashboard |

Single package, not microservices. This is an optimization tool, not a platform. Users need to install it fast, run it locally, and optionally deploy it.

### Core Abstraction: The Optimization Engine

The engine formalizes the autoimprove pattern into three primitives:

```
+--------------------------------------------------+
|                    Engine                         |
|                                                   |
|   +----------+    +----------+    +----------+   |
|   |  Asset   |--->| Evaluate |--->| Improve  |   |
|   | (Target) |    | (Measure)|    |  (Act)   |   |
|   +----------+    +----------+    +----------+   |
|        ^                               |          |
|        +-------------------------------+          |
|              Loop until converged                 |
+--------------------------------------------------+
```

**One iteration:**

1. Load current asset version
2. Score it against evaluation criteria (baseline on first iteration)
3. Generate improvement prompt incorporating: current content, evaluation criteria, previous scores, history of what worked/didn't
4. Send to AI provider for improvement
5. Score the improved version
6. If score improved beyond `min_improvement` threshold: accept, record, continue
7. If not: try a different improvement strategy (up to `max_retries_per_iteration`)
8. Stop when: target score reached, max iterations hit, or no improvement for N consecutive iterations

**Convergence strategies:**

- `greedy` — accept any improvement, stop when no improvement for N iterations
- `target` — stop when target score is reached
- `budget` — run exactly N iterations, keep the best

## 3. Project Structure

```
asset-optimizer/
├── src/
│   └── asset_optimizer/
│       ├── __init__.py              # Public API exports
│       ├── config.py                # Pydantic Settings configuration
│       ├── core/
│       │   ├── engine.py            # Optimization engine
│       │   ├── experiment.py        # Experiment lifecycle management
│       │   ├── iteration.py         # Single iteration logic
│       │   └── convergence.py       # Convergence strategies
│       ├── assets/
│       │   ├── base.py              # AssetType protocol/ABC
│       │   ├── prompt.py            # Prompt asset type
│       │   ├── skill.py             # Skill (markdown) asset type
│       │   ├── image.py             # Image generation asset type
│       │   └── registry.py          # Asset type registration
│       ├── providers/
│       │   ├── base.py              # Provider protocol/ABC
│       │   ├── openai.py            # OpenAI (text + image)
│       │   ├── anthropic.py         # Claude
│       │   ├── gemini.py            # Google Gemini
│       │   ├── vllm.py              # vLLM (OpenAI-compatible)
│       │   ├── ollama.py            # Ollama (OpenAI-compatible)
│       │   ├── image_providers/
│       │   │   ├── base.py          # ImageProvider protocol
│       │   │   ├── nano_banana.py   # Nano Banana
│       │   │   └── openai_image.py  # OpenAI Image 01
│       │   └── registry.py          # Provider registry
│       ├── scoring/
│       │   ├── base.py              # Scorer protocol/ABC
│       │   ├── heuristic.py         # Rule-based scorers
│       │   ├── ai_judge.py          # AI-judged scoring
│       │   └── composite.py         # Weighted composite scorer
│       ├── storage/
│       │   ├── base.py              # Storage protocol
│       │   ├── models.py            # SQLAlchemy ORM models
│       │   ├── repository.py        # Data access layer
│       │   └── migrations/          # Alembic migrations
│       ├── api/
│       │   ├── app.py               # FastAPI app factory
│       │   ├── deps.py              # Dependency injection
│       │   ├── routes/
│       │   │   ├── experiments.py   # CRUD + start/stop
│       │   │   ├── evaluations.py   # Evaluation management
│       │   │   ├── assets.py        # Asset browsing
│       │   │   ├── providers.py     # Provider config/test
│       │   │   └── health.py        # Health + readiness
│       │   ├── websocket.py         # Real-time experiment updates
│       │   └── schemas.py           # Pydantic request/response models
│       └── cli/
│           └── main.py              # Typer CLI
├── ui/                              # React frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── ExperimentList.tsx
│   │   │   ├── ExperimentDetail.tsx
│   │   │   ├── EvaluationBuilder.tsx
│   │   │   ├── ProviderSettings.tsx
│   │   │   └── AssetBrowser.tsx
│   │   ├── components/
│   │   │   ├── ScoreChart.tsx       # Score over iterations
│   │   │   ├── DiffViewer.tsx       # Before/after comparison
│   │   │   ├── IterationTimeline.tsx
│   │   │   └── StatusBadge.tsx
│   │   └── api/                     # Generated API client
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.ts
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── docs/
│   ├── architecture.md
│   ├── getting-started.md
│   ├── asset-types.md
│   ├── providers.md
│   ├── evaluations.md
│   ├── deployment.md
│   ├── api-reference.md
│   ├── library-usage.md
│   ├── extending.md
│   ├── development.md
│   └── superpowers/
│       └── specs/
├── dev-reports/
│   └── TEMPLATE.md
├── deploy/
│   ├── Dockerfile
│   ├── helm/
│   │   └── asset-optimizer/
│   │       ├── Chart.yaml
│   │       ├── values.yaml
│   │       └── templates/
│   └── openshift/
│       └── deployment.yaml
├── .claude/
│   ├── skills/
│   │   ├── create-evaluation.md
│   │   ├── score-and-review.md
│   │   ├── create-improvement-prompt.md
│   │   ├── register-asset-type.md
│   │   └── dev-report.md
│   ├── rules/
│   │   ├── development.md
│   │   └── usage.md
│   └── commands/
│       ├── create-asset-type.md
│       ├── create-evaluation.md
│       ├── dev-report.md
│       └── run-experiment.md
├── CLAUDE.md
├── pyproject.toml
├── README.md
└── asset-optimizer.yaml.example
```

## 4. Data Model

### Experiment

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| name | str | Human-readable name |
| description | str | Optional description |
| asset_type | str | Registered asset type name |
| evaluation_id | UUID FK | Reference to evaluation |
| provider_config | JSON | Provider configuration snapshot |
| status | enum | pending, running, paused, completed, failed, cancelled |
| config | JSON | Engine configuration (max_iterations, convergence, etc.) |
| best_score | float | Best composite score achieved |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |

### Iteration

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| experiment_id | UUID FK | Parent experiment |
| number | int | Iteration sequence number |
| status | enum | running, improved, no_improvement, error |
| strategy_used | str | Which improvement strategy was applied |
| improvement_prompt | text | The prompt sent to the AI for improvement |
| feedback | text | AI-generated feedback on the improvement |
| created_at | datetime | Creation timestamp |
| duration_ms | int | How long the iteration took |

### AssetVersion

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| iteration_id | UUID FK | Parent iteration |
| role | enum | input, output |
| content | text | Asset content (for text assets) |
| file_path | str | File path (for binary assets like images) |
| metadata | JSON | Asset-specific metadata |
| created_at | datetime | Creation timestamp |

### Evaluation

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| name | str | Evaluation name |
| asset_type | str | Which asset type this evaluates |
| criteria | JSON | List of criteria with rubrics |
| scorer_config | JSON | Scorer type and weight configuration |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |

### Score

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| iteration_id | UUID FK | Parent iteration |
| criterion_name | str | Which criterion was scored |
| value | float | Score value |
| max_value | float | Maximum possible score |
| scorer_type | enum | heuristic, ai_judge |
| details | JSON | Scorer-specific details/reasoning |
| created_at | datetime | Creation timestamp |

### Entity Relationships

```
Experiment 1--N Iteration
Iteration 1--N AssetVersion
Iteration 1--N Score
Experiment N--1 Evaluation
```

## 5. Asset Type System

Each asset type implements a protocol:

```python
class AssetType(Protocol):
    name: str
    file_extensions: list[str]

    def load(self, path: Path) -> AssetContent: ...
    def save(self, content: AssetContent, path: Path) -> None: ...
    def validate(self, content: AssetContent) -> list[str]: ...
    def default_evaluation(self) -> EvaluationConfig: ...
    def render_for_prompt(self, content: AssetContent) -> str: ...
```

### Built-in Asset Types

| Type | What it optimizes | Key scoring dimensions |
|---|---|---|
| `prompt` | Text prompts (system prompts, user prompts, templates) | Clarity, specificity, safety, effectiveness, instruction-following |
| `skill` | Claude Code skill files (markdown with frontmatter) | Structure, completeness, clarity, actionability, edge case coverage |
| `image` | Image generation prompts (generates image, scores both) | Prompt quality (heuristic) + generated image quality (AI-judged) |

### Registration

```python
from asset_optimizer.assets import registry

@registry.register("my_custom_type")
class MyAssetType:
    name = "my_custom_type"
    file_extensions = [".custom"]
    # ... implement protocol methods
```

## 6. AI Provider Abstraction

### Protocols

```python
class TextProvider(Protocol):
    async def complete(self, messages: list[Message], **kwargs) -> str: ...
    async def judge(self, content: str, criteria: list[Criterion]) -> JudgmentResult: ...

class ImageProvider(Protocol):
    async def generate(self, prompt: str, **kwargs) -> ImageResult: ...
```

### Supported Providers

| Provider | Type | SDK/Protocol |
|---|---|---|
| OpenAI | text + image | `openai` SDK |
| Anthropic (Claude) | text | `anthropic` SDK |
| Google Gemini | text | `google-generativeai` SDK |
| vLLM | text | OpenAI-compatible API (shares client with OpenAI, different base_url) |
| Ollama | text | OpenAI-compatible API (shares client with OpenAI, different base_url) |
| Nano Banana | image | HTTP API via `httpx` |
| OpenAI Image 01 | image | `openai` SDK |

### Configuration

```yaml
providers:
  text:
    default: claude
    claude:
      api_key: ${ANTHROPIC_API_KEY}
      model: claude-sonnet-4-20250514
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o
    vllm:
      base_url: http://localhost:8000/v1
      model: meta-llama/Llama-3-70B
    ollama:
      base_url: http://localhost:11434/v1
      model: llama3
    gemini:
      api_key: ${GEMINI_API_KEY}
      model: gemini-2.0-flash
  image:
    default: openai_image
    nano_banana:
      api_key: ${NANO_BANANA_API_KEY}
      endpoint: https://api.nanobanana.com/v1
    openai_image:
      api_key: ${OPENAI_API_KEY}
      model: image-01
```

## 7. Scoring System

### Heuristic Scorers

Fast, deterministic, no API calls:

- `length_scorer` — penalize too short/too long
- `structure_scorer` — check for required sections, formatting
- `readability_scorer` — Flesch-Kincaid or similar
- `keyword_scorer` — presence/absence of required terms
- `regex_scorer` — pattern matching rules
- `image_metadata_scorer` — resolution, file size, format checks

### AI-Judged Scorers

Use an AI provider to evaluate quality:

- Sends the asset content + rubric to an AI judge
- Returns structured scores per criterion
- Uses a separate "judge" provider (can be different from the "improver")
- Includes chain-of-thought reasoning in the judgment

### Composite Scorer

Weighted combination of heuristic and AI-judged scores:

```yaml
scoring:
  weights:
    clarity: 0.3
    specificity: 0.25
    effectiveness: 0.25
    safety: 0.2
  scorers:
    clarity:
      - type: heuristic
        name: readability
        weight: 0.3
      - type: ai_judge
        weight: 0.7
    specificity:
      - type: ai_judge
        weight: 1.0
```

## 8. Evaluation System

An evaluation defines what "good" looks like for a specific optimization:

```yaml
name: prompt-clarity
asset_type: prompt
description: Evaluates prompt clarity and instruction quality

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

scorer:
  type: composite
  judge_provider: claude
  heuristic_weight: 0.2
  ai_judge_weight: 0.8
```

## 9. REST API

All endpoints are versioned under `/api/v1/`. OpenAPI schema is auto-generated by FastAPI.

### Experiments

```
POST   /api/v1/experiments              Create experiment
GET    /api/v1/experiments              List experiments (filterable by status, asset_type)
GET    /api/v1/experiments/{id}         Get experiment with summary stats
POST   /api/v1/experiments/{id}/start   Start optimization
POST   /api/v1/experiments/{id}/stop    Stop optimization
POST   /api/v1/experiments/{id}/pause   Pause optimization
DELETE /api/v1/experiments/{id}         Delete experiment and all data
```

### Iterations

```
GET    /api/v1/experiments/{id}/iterations          List iterations
GET    /api/v1/experiments/{id}/iterations/{num}     Get iteration detail with scores and asset versions
```

### Evaluations

```
POST   /api/v1/evaluations              Create evaluation
GET    /api/v1/evaluations              List evaluations
GET    /api/v1/evaluations/{id}         Get evaluation
PUT    /api/v1/evaluations/{id}         Update evaluation
DELETE /api/v1/evaluations/{id}         Delete evaluation
```

### Assets

```
GET    /api/v1/assets                   List managed assets
GET    /api/v1/assets/{id}/versions     Version history for an asset
```

### Providers

```
GET    /api/v1/providers                List configured providers
POST   /api/v1/providers/test           Test provider connectivity
```

### System

```
GET    /api/v1/health                   Health check (liveness)
GET    /api/v1/health/ready             Readiness check (database, providers)
```

### WebSocket

```
WS     /api/v1/ws/experiments/{id}      Real-time iteration updates (scores, status changes)
```

## 10. Web UI

### Tech Stack

- React 18+ with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- Recharts for data visualization
- React Router for navigation
- TanStack Query for server state management
- WebSocket for real-time experiment updates

### Pages

| Page | Purpose |
|---|---|
| **Dashboard** | Active experiments, recent results, system health, quick-start actions |
| **Experiment List** | Sortable/filterable list of all experiments, bulk actions, status filters |
| **Experiment Detail** | Score progression chart, iteration timeline, diff viewer (text) or side-by-side (images), improvement prompt viewer, feedback log |
| **Evaluation Builder** | Form-based evaluation creation, criteria editor, rubric editor, scorer configuration |
| **Provider Settings** | Configure API keys, test connectivity, set defaults |
| **Asset Browser** | Browse assets, view version history, compare versions |

### Key Components

- `ScoreChart` — line chart showing score over iterations per criterion (Recharts)
- `DiffViewer` — unified diff for text assets, side-by-side for images
- `IterationTimeline` — vertical timeline with expand/collapse for iteration details
- `ExperimentControls` — start/stop/pause with real-time status via WebSocket
- `EvaluationForm` — dynamic form for building evaluation configs with live preview

## 11. CLI

Built with Typer for auto-generated help, tab completion, and type-driven interface.

```bash
# Initialize a project
asset-optimizer init [directory]

# Run optimization
asset-optimizer optimize <asset-path> \
  --evaluation <name-or-file> \
  --provider <name> \
  --iterations 20 \
  --target-score 8.5

# List/manage experiments
asset-optimizer experiments list
asset-optimizer experiments show <id>
asset-optimizer experiments export <id> --format json

# Manage evaluations
asset-optimizer evaluations list
asset-optimizer evaluations create --interactive
asset-optimizer evaluations show <name>

# Start the web server
asset-optimizer serve --host 0.0.0.0 --port 8000

# Test provider connectivity
asset-optimizer providers test --provider claude
```

## 12. Library API (Embedding)

```python
from asset_optimizer import Engine, Evaluation
from asset_optimizer.providers import AnthropicProvider
from asset_optimizer.scoring import CompositeScorer

# Configure
provider = AnthropicProvider(api_key="...", model="claude-sonnet-4-20250514")
evaluation = Evaluation.from_file("evaluations/prompt-clarity.yaml")

# Create engine
engine = Engine(
    provider=provider,
    scorer=CompositeScorer.from_evaluation(evaluation, judge_provider=provider),
)

# Run optimization
result = await engine.optimize(
    asset_path="prompts/system-prompt.txt",
    evaluation=evaluation,
    max_iterations=15,
    target_score=8.5,
    on_iteration=lambda it: print(f"Iteration {it.number}: {it.score:.2f}"),
)

print(f"Final score: {result.best_score}")
print(f"Iterations: {result.total_iterations}")
```

## 13. Configuration

Single config file `asset-optimizer.yaml` with env var interpolation:

```yaml
storage:
  backend: sqlite
  sqlite:
    path: ./data/optimizer.db
  postgres:
    url: ${DATABASE_URL}

providers:
  text:
    default: claude
    claude:
      api_key: ${ANTHROPIC_API_KEY}
      model: claude-sonnet-4-20250514
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o
  image:
    default: openai_image
    openai_image:
      api_key: ${OPENAI_API_KEY}
      model: image-01
    nano_banana:
      api_key: ${NANO_BANANA_API_KEY}

server:
  host: 0.0.0.0
  port: 8000

defaults:
  max_iterations: 20
  min_improvement: 0.01
  convergence_strategy: greedy
  stagnation_limit: 5
```

Loaded via Pydantic Settings — supports YAML file, environment variables, and CLI overrides in that priority order.

## 14. Deployment

### Dockerfile

Multi-stage build: Node for UI, Python for the application.

```dockerfile
# Stage 1: Build UI
FROM node:20-alpine AS ui-build
WORKDIR /app/ui
COPY ui/ .
RUN npm ci && npm run build

# Stage 2: Python app
FROM python:3.12-slim
RUN useradd -r -u 1001 optimizer
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --no-dev
COPY src/ src/
COPY --from=ui-build /app/ui/dist src/asset_optimizer/static/
USER 1001
EXPOSE 8000
HEALTHCHECK CMD curl -f http://localhost:8000/api/v1/health || exit 1
CMD ["uv", "run", "asset-optimizer", "serve"]
```

### OpenShift

- Non-root user (UID 1001) — required by OpenShift security context
- Helm chart in `deploy/helm/` with configurable values for resources, replicas, ingress
- `deploy/openshift/deployment.yaml` with OpenShift-specific annotations
- ConfigMap for `asset-optimizer.yaml`
- Secret for API keys
- Liveness probe: `GET /api/v1/health`
- Readiness probe: `GET /api/v1/health/ready`
- PersistentVolumeClaim for SQLite data, or use external PostgreSQL service

## 15. Skills

### create-evaluation

Guides systematic creation of evaluation criteria for any asset type. Process: understand asset type and purpose, identify relevant quality dimensions, write rubrics with concrete scoring anchors (not vague descriptions), configure scorer type and weights, output valid evaluation YAML. Uses sequential thinking to explore edge cases in criteria definition.

### score-and-review

Systematic scoring and feedback for asset improvements. Loads before/after versions, applies each criterion from the evaluation, generates detailed actionable feedback (specific line-level suggestions, not "make it better"), produces structured scores with reasoning. Used both by the engine internally and by developers reviewing optimization results.

### create-improvement-prompt

Creates high-quality prompts that drive the improvement loop. Analyzes current asset state and specific score breakdowns, generates focused improvement instructions targeting the lowest-scoring criteria, avoids over-fitting to any single criterion at the expense of others, includes anti-patterns to avoid (vague instructions, contradictory guidance, scope creep).

### register-asset-type

Step-by-step guide for adding new asset types to the framework. Generates the protocol implementation with all required methods, creates a default evaluation with sensible criteria, produces test fixtures for the new type, updates the registry, and adds documentation. Follows TDD — tests first.

### dev-report

Generates standardized development work reports. Gathers git diff, commit history, and files changed since the last report. Summarizes what was done, key decisions and rationale, metrics (tests, coverage), and next steps. Follows template in `dev-reports/TEMPLATE.md`. Outputs to `dev-reports/YYYY-MM-DD-<topic>.md`.

## 16. Rules and Commands

### Development Rules (`.claude/rules/development.md`)

- All code must pass `ruff check`, `mypy --strict`, and `pytest` before committing
- TDD: write tests before implementation
- Follow existing patterns — check before adding new patterns
- Use UV for all dependency management
- All public functions require type annotations
- Use `async/await` throughout the core engine
- Database access only through the repository layer
- No direct SQL — use SQLAlchemy ORM

### Usage Rules (`.claude/rules/usage.md`)

- Always validate provider connectivity before starting experiments
- Create baseline scores before optimization begins
- Warn if max_iterations > 50
- Never store API keys in config files — use environment variables
- All experiments must have an evaluation attached

### Commands

- **`/create-asset-type`** — scaffolds a new asset type (invokes register-asset-type skill)
- **`/create-evaluation`** — creates a new evaluation config (invokes create-evaluation skill)
- **`/dev-report`** — generates a development report (invokes dev-report skill)
- **`/run-experiment`** — starts an optimization run from the CLI context

## 17. Documentation

```
docs/
├── getting-started.md       # Install, configure, run first optimization in <5 min
├── architecture.md          # System design, data flow, component relationships
├── asset-types.md           # Built-in types, how to create custom types
├── providers.md             # Configuring each AI provider
├── evaluations.md           # Creating evaluations, scoring concepts, rubric design
├── deployment.md            # Docker, Helm, OpenShift deployment guides
├── api-reference.md         # REST API documentation (supplements auto-generated OpenAPI)
├── library-usage.md         # Using asset-optimizer as a Python library
├── extending.md             # Adding asset types, providers, scorers
└── development.md           # Contributing, dev setup, testing, repo conventions
```

## 18. Dev Reports

Template at `dev-reports/TEMPLATE.md`:

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

## 19. Quick Start Experience

```bash
# 1. Install
pip install asset-optimizer
# or: uv pip install asset-optimizer

# 2. Initialize
asset-optimizer init my-project && cd my-project

# 3. Configure (creates asset-optimizer.yaml with guided prompts)
asset-optimizer configure

# 4. Optimize a prompt
echo "You are a helpful assistant." > prompt.txt
asset-optimizer optimize prompt.txt --evaluation prompt-clarity --iterations 10

# 5. Or use the web UI
asset-optimizer serve
# Open http://localhost:8000
```

`init` creates a project directory with:
- `asset-optimizer.yaml` (config template)
- `evaluations/` (built-in evaluation templates copied in)
- `assets/` (where user assets go)
- `data/` (SQLite database, auto-created on first run)

## 20. Development Process

The project uses these superpowers and conventions during development:

1. **Brainstorming** — for all new features/designs
2. **Writing Plans** — for implementation plans from specs
3. **TDD** — write tests before implementation code
4. **Sequential Thinking** — for complex algorithmic decisions (convergence strategies, scoring algorithms)
5. **Code Simplifier** — after each implementation phase
6. **Verification Before Completion** — before claiming any task is done
7. **Code Review** — after major implementation phases
8. **Dev Reports** — after each significant implementation milestone

## 21. Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Monorepo vs microservices | Monorepo | Single install, simple deployment, library embedding |
| SQLite vs Postgres-only | Both via SQLAlchemy | Zero-config local dev, production-ready with Postgres |
| Celery vs asyncio | asyncio (pluggable interface) | No infra dependency, sufficient for single-node |
| REST vs GraphQL | REST + WebSocket | Simpler, better tooling, WS for real-time only |
| UV vs Poetry | UV | Faster, modern, better developer experience |
| Typer vs Click | Typer | Better DX, auto-completion, type-driven |
| React vs HTMX | React | Richer interactivity needed for dashboards and charts |
