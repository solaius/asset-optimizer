# Architecture

## System Components

Asset Optimizer is organized into eight layers. Each layer has a single
responsibility and communicates with adjacent layers through well-defined interfaces.

```
┌─────────────────────────────────────────────────────┐
│                     CLI (Typer)                     │
│          asset-optimizer serve / init               │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│                  Web UI (React)                     │
│      Experiment dashboard, evaluation builder       │
└────────────────────────┬────────────────────────────┘
                         │ HTTP
┌────────────────────────▼────────────────────────────┐
│               REST API (FastAPI)                    │
│  /api/v1/experiments  /api/v1/evaluations           │
│  /api/v1/providers    /api/v1/health                │
└────────────────────────┬────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
┌─────────▼────┐ ┌───────▼──────┐ ┌────▼──────────┐
│  Core Engine │ │   Scoring    │ │    Storage    │
│  autoimprove │ │ heuristic /  │ │ SQLAlchemy +  │
│     loop     │ │  ai_judge /  │ │ SQLite/Postgres│
└─────────┬────┘ │  composite   │ └───────────────┘
          │      └──────────────┘
          │
┌─────────▼────────────────────────┐
│           Providers              │
│  OpenAI / Anthropic / Gemini /   │
│  vLLM / Ollama / image providers │
└──────────────────────────────────┘
          │
┌─────────▼────────────────────────┐
│           Asset Types            │
│     prompt / skill / image       │
│     + custom via protocol        │
└──────────────────────────────────┘
```

## Data Flow

A single optimization run follows this sequence:

```
User supplies:
  content (string)  +  evaluation (YAML)
          │
          ▼
Engine.optimize()
  1. Score baseline content with AIJudgeScorer
  2. Loop until convergence:
       a. _build_improvement_prompt(content, scores, criteria)
       b. provider.complete(messages)  →  new_content
       c. scorer.score(new_content)    →  new_scores
       d. aggregate score = mean(scores)
       e. if new_score >= previous_score: accept new_content
       f. convergence_strategy.check() → should_continue?
  3. Return OptimizationResult
          │
          ▼
  best_content, best_score, initial_score,
  total_iterations, per-iteration history
```

The improvement prompt targets the **two weakest-scoring criteria** from the previous
iteration, including their rubric text. This focuses the provider on the highest-value
improvements rather than making generic edits.

## Key Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Async throughout | `asyncio` + `async/await` | Providers make HTTP calls; concurrency is essential for batching |
| Provider protocol | Abstract base class `TextProvider` | Swap models without changing engine code |
| Scoring separation | Scorers are independent of the engine | Heuristic, AI-judge, and composite scorers compose freely |
| Convergence strategies | Pluggable via `ConvergenceStrategy` | Greedy, target, and budget strategies cover most use cases |
| Storage backend | SQLAlchemy with SQLite/Postgres | SQLite for local development, Postgres for production |
| Asset types via protocol | `AssetTypeProtocol` | Custom types added without modifying core |
| Config interpolation | `${ENV_VAR}` in YAML | Keeps secrets out of committed config files |
| CLI framework | Typer + Rich | Type-safe CLI with automatic help generation |
| Web framework | FastAPI | Async-native, automatic OpenAPI schema generation |

## Module Map

```
src/asset_optimizer/
  __init__.py          Engine, OptimizationResult, EvaluationConfig, load_evaluation
  config.py            YAML config loading and validation
  core/
    engine.py          Engine class and autoimprove loop
    evaluation.py      EvaluationConfig, CriterionConfig, load_evaluation
    convergence.py     GreedyStrategy, TargetStrategy, BudgetStrategy
  assets/
    base.py            AssetContent, AssetTypeProtocol
    prompt.py          PromptAssetType
    skill.py           SkillAssetType
    image.py           ImageAssetType
    registry.py        AssetTypeRegistry
  providers/
    base.py            TextProvider ABC, Message, Criterion, JudgmentResult
    openai_provider.py OpenAITextProvider
    anthropic_provider.py AnthropicProvider
    gemini_provider.py GeminiProvider
    openai_compat.py   OpenAICompatProvider (vLLM, Ollama)
    image_providers/   ImageProvider ABC, OpenAIImageProvider, NanoBananaProvider
  scoring/
    base.py            Scorer ABC, ScoreResult
    heuristic.py       LengthScorer, StructureScorer, KeywordScorer, ReadabilityScorer
    ai_judge.py        AIJudgeScorer
    composite.py       CompositeScorer
  storage/
    models.py          Experiment, Iteration, AssetVersion, Evaluation, Score
    database.py        async engine setup, session factory
  api/
    app.py             create_app() FastAPI factory
    routes/            experiments, evaluations, providers, health
    schemas.py         Pydantic request/response models
    deps.py            FastAPI dependency injection
  cli/
    main.py            Typer app, serve, init commands
```
