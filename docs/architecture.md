# Architecture

## System Components

Asset Optimizer is organized into nine layers. Each layer has a single
responsibility and communicates with adjacent layers through well-defined interfaces.

```
┌─────────────────────────────────────────────────────┐
│                     CLI (Typer)                     │
│          asset-optimizer serve / init               │
└────────────────────────┬────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────┐
│                  Web UI (React)                     │
│  Score charts, iteration cards with images,         │
│  score bars with reasoning, evaluation viewer       │
└────────────────────────┬────────────────────────────┘
                         │ HTTP
┌────────────────────────▼────────────────────────────┐
│               REST API (FastAPI)                    │
│  /api/v1/experiments  /api/v1/evaluations           │
│  /api/v1/experiments/{id}/iterations                │
│  /api/v1/assets/{id}/image  /api/v1/health          │
└────────────────────────┬────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
┌─────────▼────┐ ┌───────▼──────┐ ┌────▼──────────┐
│  Core Engine │ │   Scoring    │ │    Storage    │
│  autoimprove │ │ heuristic /  │ │ SQLAlchemy +  │
│  loop + visual│ │  ai_judge /  │ │ SQLite/Postgres│
│  image loop  │ │  composite   │ │ + ImageStorage│
└─────────┬────┘ └──────────────┘ └───────────────┘
          │
┌─────────▼────────────────────────────────────────┐
│           Providers                               │
│  Text: OpenAI / Anthropic / Gemini /              │
│         vLLM / Ollama                             │
│  Image: OpenAIImage / GeminiImage / NanoBanana    │
│  Factory: create_text_provider()                  │
│           create_judge_provider()                 │
│           create_image_provider()                 │
│           create_engine()                         │
└─────────┬────────────────────────────────────────┘
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
       c. [if image_provider set]:
            image_provider.generate(new_content)  →  image_bytes
            judge_provider.judge(new_content, criteria, image=image_bytes)
              →  visual_scores  (requires_image criteria scored here)
       d. scorer.score(new_content)    →  text_scores
       e. aggregate score = mean(all scores)
       f. if new_score >= previous_score: accept new_content
       g. convergence_strategy.check() → should_continue?
  3. Return OptimizationResult
          │
          ▼
  best_content, best_score, initial_score,
  total_iterations, total_cost, stopped_early, stop_reason,
  best_image, best_image_format, per-iteration history
```

The improvement prompt targets the **two weakest-scoring criteria** from the previous
iteration, including their rubric text and (when available) the judge's visual
reasoning. This focuses the provider on the highest-value improvements rather than
making generic edits.

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
  __init__.py          Engine, OptimizationResult, EvaluationConfig, load_evaluation,
                       create_text_provider, create_judge_provider,
                       create_image_provider, create_engine
  config.py            YAML config loading and validation
  core/
    engine.py          Engine class, autoimprove loop, visual image loop
    evaluation.py      EvaluationConfig, CriterionConfig (+ requires_image), load_evaluation
    convergence.py     GreedyStrategy, TargetStrategy, BudgetStrategy
  assets/
    base.py            AssetContent, AssetTypeProtocol
    prompt.py          PromptAssetType
    skill.py           SkillAssetType
    image.py           ImageAssetType
    registry.py        AssetTypeRegistry
  providers/
    base.py            TextProvider ABC, Message, Criterion, JudgmentResult
                       (judge() accepts optional image: bytes)
    factory.py         create_text_provider(), create_judge_provider(),
                       create_image_provider(), create_engine()
    openai_provider.py OpenAITextProvider (multimodal judge support)
    anthropic_provider.py AnthropicProvider (multimodal judge support)
    gemini_provider.py GeminiProvider (multimodal judge support, google-genai SDK)
    openai_compat.py   OpenAICompatProvider (vLLM, Ollama)
    image_providers/
      base.py          ImageProvider ABC
      openai_image.py  OpenAIImageProvider (DALL-E)
      gemini_image.py  GeminiImageProvider (google-genai SDK)
      nano_banana.py   NanoBananaProvider
  scoring/
    base.py            Scorer ABC, ScoreResult
    heuristic.py       LengthScorer, StructureScorer, KeywordScorer, ReadabilityScorer
    ai_judge.py        AIJudgeScorer (accepts optional image bytes)
    composite.py       CompositeScorer
  storage/
    models.py          Experiment, Iteration, AssetVersion, Evaluation, Score
    database.py        async engine setup, session factory
    image_storage.py   ImageStorage — saves generated images to disk by experiment/iteration
  api/
    app.py             create_app() FastAPI factory
    routes/
      experiments.py   experiments CRUD + /iterations sub-resource
      assets.py        /assets/{id}/image image serving
      evaluations.py   evaluations CRUD
      providers.py     provider listing
      health.py        liveness + readiness
    schemas.py         Pydantic request/response models
    deps.py            FastAPI dependency injection
  cli/
    main.py            Typer app, serve, init commands

evaluations/
  prompt-clarity.yaml       Text prompt quality (clarity, specificity, effectiveness)
  image-visual.yaml         Mixed text + visual criteria (requires_image on visual criteria)
  luminth-hero-strict.yaml  Strict visual evaluation for Luminth hero images

examples/
  img-prompt-enhancement/   Runnable scripts for image prompt optimization
```
