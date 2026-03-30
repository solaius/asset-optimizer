# Library Usage

Asset Optimizer can be used as a Python library without the CLI or web server.
Import `Engine`, `load_evaluation`, and a provider to run optimizations directly
in your code.

## Installation

```bash
uv pip install asset-optimizer
# or
pip install asset-optimizer
```

## Basic Usage (factory functions)

The simplest approach — factory functions auto-configure from `.env`:

```python
import asyncio
from asset_optimizer import create_engine, load_evaluation

async def main():
    engine = create_engine()   # reads TEXT_PROVIDER, JUDGE_PROVIDER from .env
    evaluation = load_evaluation("evaluations/prompt-clarity.yaml")
    result = await engine.optimize(
        content="You are a helpful assistant.",
        evaluation=evaluation,
        max_iterations=10,
    )
    print(f"Initial score: {result.initial_score:.2f}")
    print(f"Final score:   {result.best_score:.2f}")
    print(f"Iterations:    {result.total_iterations}")
    print(f"Cost:          ${result.total_cost:.4f}")
    print(f"Stopped early: {result.stopped_early}  ({result.stop_reason})")
    print()
    print(result.best_content)

asyncio.run(main())
```

## Basic Usage (manual construction)

```python
import asyncio
from pathlib import Path
from asset_optimizer import Engine, load_evaluation
from asset_optimizer.providers.openai_provider import OpenAITextProvider

async def main():
    provider = OpenAITextProvider(api_key="sk-...", model="gpt-4o")
    evaluation = load_evaluation(Path("evaluations/prompt-clarity.yaml"))
    engine = Engine(provider=provider, judge_provider=provider)
    result = await engine.optimize(
        content="You are a helpful assistant.",
        evaluation=evaluation,
        max_iterations=10,
    )
    print(f"Initial score: {result.initial_score:.2f}")
    print(f"Final score:   {result.best_score:.2f}")
    print(result.best_content)

asyncio.run(main())
```

## Factory Functions

All four factory functions are exported from the top-level `asset_optimizer` package
and read from `.env` (or the YAML config) automatically:

```python
from asset_optimizer import (
    create_text_provider,
    create_judge_provider,
    create_image_provider,
    create_engine,
)

# Individual providers
text_provider  = create_text_provider()    # uses TEXT_PROVIDER env var
judge_provider = create_judge_provider()   # uses JUDGE_PROVIDER env var
image_provider = create_image_provider()   # uses IMAGE_PROVIDER env var

# Fully wired engine (all three roles)
engine = create_engine()
```

## Engine

`Engine` is the entry point for all optimizations.

```python
from asset_optimizer import Engine
from asset_optimizer.providers.anthropic_provider import AnthropicProvider
from asset_optimizer.providers.openai_provider import OpenAITextProvider

generator = OpenAITextProvider(model="gpt-4o-mini", api_key="sk-...")
judge = AnthropicProvider(model="claude-sonnet-4-20250514", api_key="sk-ant-...")

# Separate providers for generation and judging
engine = Engine(provider=generator, judge_provider=judge)

# Single provider for both roles
engine = Engine(provider=generator)
```

### engine.optimize() Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `content` | `str` | required | Initial asset content |
| `evaluation` | `EvaluationConfig` | required | Scoring criteria |
| `max_iterations` | `int` | `20` | Hard cap on iterations |
| `target_score` | `float \| None` | `None` | Stop when this score is reached (requires `convergence_strategy="target"`) |
| `convergence_strategy` | `str` | `"greedy"` | One of `"greedy"`, `"target"`, `"budget"` |
| `stagnation_limit` | `int` | `5` | Greedy: stop after this many non-improving iterations |
| `min_improvement` | `float` | `0.01` | Greedy: minimum delta to count as improvement |
| `on_iteration` | `Callable \| None` | `None` | Callback invoked after each iteration |

## Image Optimization

When an `image_provider` is set on the engine, the visual optimization loop activates.
The engine generates an image each iteration and uses multimodal AI judging (vision)
to score the actual image — not just the prompt text.

```python
import asyncio
from asset_optimizer import create_engine, load_evaluation

async def main():
    # Requires IMAGE_PROVIDER=openai_image in .env
    engine = create_engine()
    evaluation = load_evaluation("evaluations/image-visual.yaml")

    result = await engine.optimize(
        content="A serene mountain lake at golden hour, photorealistic",
        evaluation=evaluation,
        max_iterations=8,
        convergence_strategy="budget",  # recommended for image runs
    )
    print(f"Score: {result.initial_score:.2f} -> {result.best_score:.2f}")
    print(f"Cost: ${result.total_cost:.4f}")

    if result.best_image:
        with open(f"output.{result.best_image_format}", "wb") as f:
            f.write(result.best_image)

asyncio.run(main())
```

Or wire the image provider manually:

```python
from asset_optimizer import Engine
from asset_optimizer.providers.openai_provider import OpenAITextProvider
from asset_optimizer.providers.image_providers.openai_image import OpenAIImageProvider

text_provider = OpenAITextProvider(model="gpt-4o", api_key="sk-...")
image_provider = OpenAIImageProvider(model="dall-e-3", api_key="sk-...")

engine = Engine(
    provider=text_provider,
    judge_provider=text_provider,
    image_provider=image_provider,   # enables visual optimization loop
)
```

See `examples/img-prompt-enhancement/` for runnable scripts.

## Convergence Strategies

```python
# Greedy: stop when score stops improving
result = await engine.optimize(
    content=content,
    evaluation=evaluation,
    convergence_strategy="greedy",
    stagnation_limit=3,
    min_improvement=0.05,
    max_iterations=20,
)

# Target: stop when a specific score is reached
result = await engine.optimize(
    content=content,
    evaluation=evaluation,
    convergence_strategy="target",
    target_score=8.5,
    max_iterations=20,
)

# Budget: always run the full iteration budget
result = await engine.optimize(
    content=content,
    evaluation=evaluation,
    convergence_strategy="budget",
    max_iterations=10,
)
```

## Callbacks

Use `on_iteration` to observe progress in real time:

```python
def progress(data: dict) -> None:
    iteration = data["iteration"]
    score = data["score"]
    accepted = data["accepted"]
    status = "accepted" if accepted else "rejected"
    print(f"[{iteration}] score={score:.2f}  {status}")

result = await engine.optimize(
    content=content,
    evaluation=evaluation,
    max_iterations=10,
    on_iteration=progress,
)
```

The callback receives a dict with keys: `"iteration"`, `"score"`, `"content"`,
`"accepted"`.

## Result Handling

`OptimizationResult` contains the full run history:

```python
from asset_optimizer import OptimizationResult

result: OptimizationResult = await engine.optimize(...)

# Summary
print(result.best_content)       # best content string
print(result.best_score)         # highest aggregate score achieved
print(result.initial_score)      # baseline score before any optimization
print(result.total_iterations)   # how many iterations were run
print(result.total_cost)         # total API cost in USD
print(result.stopped_early)      # True if convergence triggered before max_iterations
print(result.stop_reason)        # e.g. "stagnation", "target_reached", "budget"

# Image artifacts (set when image_provider was used)
print(result.best_image)         # bytes | None
print(result.best_image_format)  # "png" | "jpg" | ""

# Per-iteration history
for iter_result in result.iterations:
    print(f"Iteration {iter_result.iteration}")
    print(f"  input_score:  {iter_result.input_score:.2f}")
    print(f"  output_score: {iter_result.output_score:.2f}")
    print(f"  accepted:     {iter_result.accepted}")
    print(f"  duration_ms:  {iter_result.duration_ms:.0f}ms")
    print(f"  image_format: {iter_result.image_format}")   # "" if no image
    print(f"  image_cost:   ${iter_result.image_cost:.4f}")

    # Per-criterion scores for this iteration
    for score in iter_result.scores:
        print(f"    {score.criterion}: {score.value:.1f}/{score.max_value:.1f}")
```

## Loading Evaluations

```python
from pathlib import Path
from asset_optimizer import load_evaluation, EvaluationConfig

# From a YAML file
evaluation = load_evaluation(Path("evaluations/prompt-clarity.yaml"))

# Programmatically
from asset_optimizer.core.evaluation import CriterionConfig, ScorerConfig

evaluation = EvaluationConfig(
    name="my-evaluation",
    asset_type="prompt",
    description="Custom evaluation",
    criteria=[
        CriterionConfig(
            name="tone",
            description="Is the tone professional and friendly?",
            max_score=10,
            rubric="1-3: Rude or robotic\n4-6: Neutral\n7-10: Warm and professional",
        ),
        CriterionConfig(
            name="visual_quality",
            description="Is the generated image sharp and well-composed?",
            max_score=10,
            rubric="1-3: Blurry or artifacts\n4-6: Acceptable\n7-10: Sharp and well-composed",
            requires_image=True,   # only scored when image_provider is active
        ),
    ],
    scorer_config=ScorerConfig(
        type="composite",
        heuristic_weight=0.0,
        ai_judge_weight=1.0,
    ),
)
```

## Using Providers Directly

Providers can be used independently for text generation and judgment:

```python
from asset_optimizer.providers.openai_provider import OpenAITextProvider
from asset_optimizer.providers.base import Message, Criterion

provider = OpenAITextProvider(model="gpt-4o", api_key="sk-...")

# Text completion
messages = [Message(role="user", content="Write a haiku about Python.")]
text = await provider.complete(messages)
print(text)

# Judgment (text-only)
criteria = [
    Criterion(name="quality", description="Is this high quality?", max_score=10),
]
result = await provider.judge(content=text, criteria=criteria)
for score in result.scores:
    print(f"{score.criterion}: {score.score} — {score.reasoning}")

# Judgment (multimodal — include image bytes)
with open("photo.png", "rb") as f:
    image_bytes = f.read()
result = await provider.judge(content=text, criteria=criteria, image=image_bytes)
```

## Batch Optimization

Run multiple assets in parallel using `asyncio.gather`:

```python
import asyncio
from asset_optimizer import create_engine, load_evaluation

async def optimize_all(prompts: list[str]) -> list[str]:
    engine = create_engine()
    evaluation = load_evaluation("evaluations/prompt-clarity.yaml")

    tasks = [
        engine.optimize(content=p, evaluation=evaluation, max_iterations=5)
        for p in prompts
    ]
    results = await asyncio.gather(*tasks)
    return [r.best_content for r in results]
```
