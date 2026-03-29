# Product Roadmap

## Use Case: Visual Image Optimization Loop

### Description

The engine should be able to take an image generation prompt (with optional context like style references, brand guidelines, or target audience), generate an actual image from it, visually evaluate the generated image using a multimodal AI judge, improve the prompt based on visual feedback, and repeat until the image meets quality thresholds — then output both the final prompt and the final image.

### Current State

Today the engine treats image prompts as plain text. It scores the **words** of the prompt (clarity, specificity, style guidance) but never:

1. Calls an image provider to **generate an image**
2. Sends the generated image to a **multimodal AI judge** for visual evaluation
3. Uses **visual feedback** (composition, color, relevance to intent) to guide prompt improvement
4. Stores or returns the **generated image artifacts** alongside the optimized prompt

The image providers (`OpenAIImageProvider`, `GeminiImageProvider`, `NanoBananaProvider`) exist and can generate images, but the `Engine.optimize()` loop never calls them. The `AIJudgeScorer` only accepts text, not images.

### Target Behavior

```
1. User provides: image prompt + evaluation criteria + context
2. Engine scores the prompt text (heuristic: length, keywords)
3. Engine generates an image using the configured image provider
4. Engine sends the generated image to a multimodal AI judge
5. Judge scores: image quality, relevance to prompt, composition, style match
6. Engine combines text scores + visual scores into composite score
7. Engine builds improvement prompt incorporating visual feedback
   ("The mountains lack depth — add atmospheric perspective" not just "improve specificity")
8. Engine improves the text prompt based on visual + text feedback
9. Repeat from step 3 until convergence
10. Return: optimized prompt + best generated image + score history
```

### Required Changes

#### 1. Engine: Add image provider support

**File:** `src/asset_optimizer/core/engine.py`

The `Engine.__init__()` needs an optional `image_provider` parameter:

```python
def __init__(
    self,
    provider: TextProvider,
    judge_provider: TextProvider | None = None,
    image_provider: ImageProvider | None = None,  # NEW
) -> None:
```

The `optimize()` loop needs a branch: when `image_provider` is set and the asset type is `image`, generate an image after each prompt improvement and pass it to the judge alongside the prompt text.

The `OptimizationResult` needs to carry image artifacts:

```python
@dataclass
class OptimizationResult:
    best_content: str
    best_score: float
    initial_score: float
    total_iterations: int
    iterations: list[IterationResult]
    best_image: bytes | None = None      # NEW
    best_image_format: str = ""          # NEW
```

`IterationResult` similarly needs the generated image per iteration for history.

#### 2. Multimodal AI Judge

**File:** `src/asset_optimizer/scoring/ai_judge.py`

The `AIJudgeScorer.score()` currently accepts only `content: str`. It needs to also accept an optional image:

```python
async def score(
    self,
    content: str,
    image: bytes | None = None,
    image_format: str = "png",
) -> list[ScoreResult]:
```

When an image is provided, the judge prompt must include both the text prompt and the image, asking the multimodal model to evaluate the **generated image** against visual criteria (not just the prompt text).

#### 3. TextProvider: Multimodal judge method

**File:** `src/asset_optimizer/providers/base.py`

The `TextProvider.judge()` method currently only accepts text. It needs an optional image parameter:

```python
@abstractmethod
async def judge(
    self,
    content: str,
    criteria: list[Criterion],
    image: bytes | None = None,
) -> JudgmentResult:
```

Each provider implementation (OpenAI, Anthropic, Gemini) needs to handle the image by encoding it as base64 and including it in the multimodal message. Not all providers support vision — the implementations should raise a clear error if image judging is requested but the model doesn't support it.

**Providers with vision support:**
- OpenAI: gpt-4o, gpt-4o-mini (via image_url content blocks)
- Anthropic: claude-sonnet-4, claude-opus-4 (via base64 image content blocks)
- Gemini: gemini-2.5-pro, gemini-2.0-flash (via inline_data parts)

#### 4. Improvement prompt with visual context

**File:** `src/asset_optimizer/core/engine.py` (`_build_improvement_prompt`)

When visual scores are available, the improvement prompt must reference what the judge **saw** in the image, not just abstract criteria scores. The judge's reasoning (e.g., "the sky is overexposed and the subject is off-center") should be included in the improvement prompt so the text provider knows what to fix in the image generation prompt.

#### 5. Evaluation criteria for visual scoring

**File:** `evaluations/image-visual.yaml` (new)

A new evaluation config that includes both prompt-quality criteria (scored from text) and image-quality criteria (scored from the generated image):

```yaml
criteria:
  # Scored from the prompt text
  - name: prompt_specificity
    description: "Does the prompt clearly describe the desired image?"

  # Scored from the generated image (requires multimodal judge)
  - name: visual_quality
    description: "Is the generated image sharp, well-composed, and artifact-free?"
    requires_image: true   # NEW field

  - name: visual_relevance
    description: "Does the generated image match what the prompt asked for?"
    requires_image: true

  - name: style_match
    description: "Does the image reflect the requested artistic style?"
    requires_image: true
```

The `CriterionConfig` model needs a `requires_image: bool = False` field so the scorer knows which criteria need the generated image.

#### 6. Factory: Wire image provider into Engine

**File:** `src/asset_optimizer/providers/factory.py`

Add a convenience function that creates a fully-wired engine:

```python
def create_engine(
    text_provider: str | None = None,
    judge_provider: str | None = None,
    image_provider: str | None = None,
) -> Engine:
    """Create an Engine with all providers auto-configured."""
```

#### 7. Storage: Image artifacts

**File:** `src/asset_optimizer/storage/models.py`

The `AssetVersion` model already has `file_path` and `content` fields. Generated images should be saved to disk and referenced via `file_path`. The `metadata_` JSON field can store image dimensions, format, and file size.

#### 8. API: Image serving

**File:** `src/asset_optimizer/api/routes/assets.py`

Add an endpoint to serve generated image files so the web UI can display them:

```
GET /api/v1/assets/{id}/image → binary image response
```

#### 9. Web UI: Image comparison

**File:** `ui/src/pages/ExperimentDetail.tsx`

The experiment detail page needs a side-by-side image viewer showing the generated image at each iteration, so the user can visually see how the optimization improved the output.

### Implementation Order

1. `CriterionConfig.requires_image` field
2. `TextProvider.judge()` — add optional `image` param to base and all providers
3. `AIJudgeScorer.score()` — accept optional image, route to multimodal judge
4. `Engine` — add `image_provider`, generate image in loop, pass to judge
5. `OptimizationResult` / `IterationResult` — carry image artifacts
6. `evaluations/image-visual.yaml` — visual evaluation criteria
7. Storage — save generated images to disk
8. API — serve image files
9. UI — image comparison viewer
10. Factory — `create_engine()` convenience function

### Cost Considerations

Each iteration in the visual loop makes **three API calls** instead of one:
1. Text provider: improve the prompt (~fast, cheap)
2. Image provider: generate an image (~slow, moderate cost)
3. Multimodal judge: evaluate the image (~moderate speed, moderate cost)

At 10 iterations with DALL-E 3 + GPT-4o judging, a single optimization run could cost $1-5. With Gemini image generation + Gemini judging, costs would be significantly lower. Users should be warned about cost and encouraged to use low iteration counts or budget convergence strategy for image optimization.

### Success Criteria

- A user can run `engine.optimize()` with an image provider and get back both an optimized prompt and a generated image
- The judge evaluates the actual generated image, not just the prompt text
- Visual feedback ("the lighting is flat") appears in the improvement prompt
- The web UI shows generated images at each iteration
- Cost per iteration is transparent in the iteration results
