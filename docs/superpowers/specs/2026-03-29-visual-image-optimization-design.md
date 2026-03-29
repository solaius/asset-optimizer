# Visual Image Optimization Loop — Design Spec

## Overview

Extend the asset-optimizer engine to generate actual images during optimization, evaluate them with a multimodal AI judge, and feed visual feedback back into prompt improvement. Today the engine optimizes prompt text but never renders an image or evaluates it visually. This feature closes that loop.

## Scope

Full stack: engine, providers, scoring, storage, API, and UI. Single feature branch (`feature/visual-image-optimization`).

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Architecture | Extend existing Engine (optional `image_provider`) | Follows existing patterns, minimal new abstractions |
| Provider support | All three (OpenAI, Anthropic, Gemini) | Full coverage from day one |
| Image storage | Experiment-scoped dirs: `data/images/{experiment_id}/{iteration}.{fmt}` | Easy to browse and clean up |
| Cost tracking | Track per-iteration, display in UI, warn before start | Full transparency given $1-5/run costs |
| Image gen failure | Retry once, then stop and return best result so far | Fail-safe — don't burn budget on broken prompts |
| UI image viewer | Best image + score history; expandable iterations | Simple observability tool, not part of the loop |

## 1. Data Model Changes

### CriterionConfig (`core/evaluation.py`)

```python
@dataclass
class CriterionConfig:
    name: str
    description: str
    max_score: float = 10.0
    rubric: str = ""
    requires_image: bool = False  # NEW
```

### Criterion (`providers/base.py`)

```python
@dataclass
class Criterion:
    name: str
    description: str
    max_score: float = 10.0
    rubric: str = ""
    requires_image: bool = False  # NEW
```

### IterationResult (`core/engine.py`)

```python
@dataclass
class IterationResult:
    iteration: int
    input_content: str
    output_content: str
    input_score: float
    output_score: float
    scores: list[ScoreResult]
    improvement_prompt: str
    accepted: bool
    duration_ms: float
    image_data: bytes | None = None       # NEW
    image_format: str = ""                # NEW
    image_cost: float | None = None       # NEW
```

### OptimizationResult (`core/engine.py`)

```python
@dataclass
class OptimizationResult:
    best_content: str
    best_score: float
    initial_score: float
    total_iterations: int
    iterations: list[IterationResult]
    best_image: bytes | None = None       # NEW
    best_image_format: str = ""           # NEW
    total_cost: float | None = None       # NEW
    stopped_early: bool = False           # NEW
    stop_reason: str = ""                 # NEW
```

### ScoreResult (`scoring/base.py`)

```python
@dataclass
class ScoreResult:
    criterion: str
    value: float
    max_value: float = 10.0
    scorer_type: str = "heuristic"
    details: dict[str, object] = field(default_factory=dict)
    cost: float | None = None             # NEW
```

### Storage (`storage/models.py`)

No schema changes. `AssetVersion.file_path` stores image path. `AssetVersion.metadata_` JSON stores:
```json
{
  "image_format": "png",
  "image_width": 1024,
  "image_height": 1024,
  "file_size_bytes": 245000
}
```

`Score.details` JSON stores per-score cost when available.

## 2. Provider Changes — Multimodal Judge

### TextProvider base (`providers/base.py`)

```python
class TextProvider(ABC):
    @abstractmethod
    async def judge(
        self,
        content: str,
        criteria: list[Criterion],
        image: bytes | None = None,         # NEW
        image_format: str = "png",          # NEW
    ) -> JudgmentResult: ...
```

### OpenAI implementation (`openai_provider.py`)

When `image` is provided, include a base64 data URI `image_url` content block in the user message alongside the text. Uses `detail: "high"` for quality evaluation.

Raises `ValueError("Model {model} does not support vision")` if the model isn't in the vision-capable list (gpt-4o, gpt-4o-mini).

### Anthropic implementation (`anthropic_provider.py`)

When `image` is provided, include a base64 `image` content block per Anthropic's multimodal API format.

Raises `ValueError` for non-vision models.

### Gemini implementation (`gemini_provider.py`)

When `image` is provided, include an `inline_data` part with the image bytes and MIME type.

Raises `ValueError` for non-vision models.

## 3. Scoring Changes

### AIJudgeScorer (`scoring/ai_judge.py`)

```python
class AIJudgeScorer:
    async def score(
        self,
        content: str,
        image: bytes | None = None,         # NEW
        image_format: str = "png",          # NEW
    ) -> list[ScoreResult]:
```

Behavior:
- When `image` is provided: pass it to `provider.judge()` along with all criteria
- When `image` is None: only score criteria where `requires_image=False`; skip image-required criteria entirely (do not score them as 0)
- The judge prompt must instruct the model to evaluate the **generated image** against visual criteria, not just the prompt text

## 4. Engine Changes

### Constructor

```python
class Engine:
    def __init__(
        self,
        provider: TextProvider,
        judge_provider: TextProvider | None = None,
        image_provider: ImageProvider | None = None,  # NEW
    ) -> None:
```

### optimize() loop

When `image_provider` is set:

1. Score baseline text (text-only criteria)
2. **Generate baseline image** via `image_provider.generate(content)`
3. Score with image (all criteria including `requires_image=True`)
4. Loop:
   a. Build improvement prompt incorporating visual feedback from judge reasoning
   b. Improve prompt text via `provider.complete()`
   c. Generate new image via `image_provider.generate(new_content)`
   d. Score new content + new image
   e. Check convergence
   f. Track image data, format, and cost on `IterationResult`
5. Set `best_image` and `best_image_format` on `OptimizationResult` from the best-scoring iteration

### Image generation failure handling

- On transient error (timeout, rate limit): retry once
- On persistent failure (content policy, second retry failure): stop optimization, return `OptimizationResult` with best result so far. Add `stopped_early: bool = False` and `stop_reason: str = ""` fields to `OptimizationResult`

### Cost warning

Before entering the loop, if `image_provider` is set:
- Estimate total cost: `max_iterations * estimated_cost_per_iteration`
- Log a warning if estimated cost exceeds threshold (default $2)
- Cost estimation is rough — based on provider pricing constants, not exact

### _build_improvement_prompt()

When visual scores are available, include the judge's `reasoning` text for image-required criteria. Example improvement prompt addition:

> The judge observed: "The mountains lack depth and atmospheric perspective. The foreground subject is slightly off-center." Focus on addressing these visual issues in the prompt.

## 5. Evaluation Config

New file: `evaluations/image-visual.yaml`

```yaml
name: image-visual
asset_type: image
description: Evaluates image generation prompts by scoring both the prompt text and the generated image

criteria:
  - name: prompt_specificity
    description: "Does the prompt clearly and specifically describe the desired image?"
    max_score: 10
    rubric: |
      1-3: Vague description, missing key details about subject, style, or composition
      4-6: Describes the subject but lacks specifics on lighting, perspective, or mood
      7-9: Detailed prompt with clear subject, style, composition, and mood guidance
      10: Exhaustively specific with concrete visual references and technical direction

  - name: prompt_style
    description: "Does the prompt include clear artistic style and aesthetic direction?"
    max_score: 10
    rubric: |
      1-3: No style guidance or contradictory style instructions
      4-6: Names a style but doesn't elaborate on how it should manifest
      7-9: Clear style direction with specific references to techniques or artists
      10: Comprehensive style guide with medium, technique, color palette, and mood

  - name: visual_quality
    description: "Is the generated image sharp, well-composed, and free of artifacts?"
    max_score: 10
    requires_image: true
    rubric: |
      1-3: Blurry, distorted, or contains obvious AI artifacts (extra fingers, melted text)
      4-6: Acceptable quality but has minor issues (slightly soft focus, minor artifacts)
      7-9: Sharp, clean, well-composed image with good lighting and no visible artifacts
      10: Professional quality — could be used in production without editing

  - name: visual_relevance
    description: "Does the generated image accurately depict what the prompt asked for?"
    max_score: 10
    requires_image: true
    rubric: |
      1-3: Image bears little resemblance to the prompt description
      4-6: Captures the general idea but misses key details or adds unwanted elements
      7-9: Accurately depicts the prompt with most details correct
      10: Perfect match — every element described in the prompt is faithfully rendered

  - name: style_match
    description: "Does the image reflect the requested artistic style?"
    max_score: 10
    requires_image: true
    rubric: |
      1-3: Style is completely different from what was requested
      4-6: Some stylistic elements present but inconsistent or weak
      7-9: Clear match to the requested style with appropriate techniques visible
      10: Masterful execution of the requested style — immediately recognizable

scorer_config:
  type: composite
  heuristic_weight: 0.1
  ai_judge_weight: 0.9
```

## 6. Factory

Add to `factory.py`:

```python
def create_engine(
    text_provider: str | None = None,
    judge_provider: str | None = None,
    image_provider: str | None = None,
    config_path: Path | None = None,
) -> Engine:
    """Create an Engine with all providers auto-configured from args/config/env."""
    text = create_text_provider(name=text_provider, config_path=config_path)
    judge = create_judge_provider(name=judge_provider, config_path=config_path)
    image = create_image_provider(name=image_provider, config_path=config_path) if image_provider else None
    return Engine(provider=text, judge_provider=judge, image_provider=image)
```

## 7. Image Storage

### Write path (via `ImageStorage` helper in `storage/image_storage.py`)

After each iteration that produces an image:
1. Create directory: `data/images/{experiment_id}/`
2. Write image: `data/images/{experiment_id}/{iteration_number}.{format}`
3. Create `AssetVersion` record with `file_path` pointing to the file and `metadata_` containing format, dimensions, file size

### Read path (API)

The API reads the `file_path` from `AssetVersion` and serves the file.

### Cleanup

When an experiment is deleted, its image directory is deleted along with the DB records.

## 8. API Changes

### New endpoint

```
GET /api/v1/assets/{asset_version_id}/image
```

- Looks up `AssetVersion` by ID
- Reads file from `file_path`
- Returns binary response with `Content-Type: image/{format}`
- Returns 404 if no file exists

### Schema additions

`IterationResponse` — add:
- `has_image: bool`
- `image_asset_version_id: str | None`
- `image_cost: float | None`

`ExperimentDetailResponse` — add:
- `best_image_asset_version_id: str | None`
- `total_cost: float | None`

## 9. UI Changes

### ExperimentDetail.tsx

When the experiment has image data:

- **Best image panel**: Show the best-scoring generated image prominently, loaded from `GET /api/v1/assets/{id}/image`
- **Score history chart**: Unchanged — shows score progression across iterations
- **Iteration list**: Each row shows iteration number, score, accepted/rejected, and cost. Rows with images are expandable — clicking reveals the generated image for that iteration (lazy-loaded)
- **Cost summary**: Show total estimated cost at the top of the experiment detail

When no image provider was used, the page renders exactly as it does today.

### API client (`api/client.ts`)

Add:
- `api.assets.getImageUrl(assetVersionId)` — returns the URL for the image endpoint
- Updated type definitions for iteration and experiment responses with image fields

## Cost Estimation

Rough per-iteration cost constants (defined as class-level `ESTIMATED_COST_PER_CALL: float` on each provider implementation, not hardcoded in engine):

| Provider | Image Generation | Vision Judging | Total/iteration |
|----------|-----------------|----------------|-----------------|
| OpenAI (DALL-E 3 + GPT-4o) | ~$0.04-0.08 | ~$0.01-0.03 | ~$0.05-0.11 |
| Gemini (Imagen + Gemini Pro) | ~$0.01-0.03 | ~$0.005-0.01 | ~$0.015-0.04 |

These are estimates for warning purposes only — actual costs depend on resolution, token counts, etc.

## Success Criteria

1. A user can run `engine.optimize()` with an image provider and get back both an optimized prompt and a generated image
2. The judge evaluates the actual generated image, not just the prompt text
3. Visual feedback ("the lighting is flat") appears in the improvement prompt
4. Per-iteration cost is tracked and displayed
5. The web UI shows the best generated image and allows expanding iterations to see per-iteration images
6. Cost warning fires before optimization starts when estimated cost exceeds threshold
7. On image generation failure, optimization stops gracefully and returns best result so far
8. All existing text-only optimization continues to work unchanged
