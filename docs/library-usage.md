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

## Basic Usage

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
    print(f"Iterations:    {result.total_iterations}")
    print()
    print(result.best_content)

asyncio.run(main())
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

# Per-iteration history
for iter_result in result.iterations:
    print(f"Iteration {iter_result.iteration}")
    print(f"  input_score:  {iter_result.input_score:.2f}")
    print(f"  output_score: {iter_result.output_score:.2f}")
    print(f"  accepted:     {iter_result.accepted}")
    print(f"  duration_ms:  {iter_result.duration_ms:.0f}ms")

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

# Judgment
criteria = [
    Criterion(name="quality", description="Is this high quality?", max_score=10),
]
result = await provider.judge(content=text, criteria=criteria)
for score in result.scores:
    print(f"{score.criterion}: {score.score} — {score.reasoning}")
```

## Batch Optimization

Run multiple assets in parallel using `asyncio.gather`:

```python
import asyncio
from asset_optimizer import Engine, load_evaluation
from asset_optimizer.providers.openai_provider import OpenAITextProvider

async def optimize_all(prompts: list[str]) -> list[str]:
    provider = OpenAITextProvider(model="gpt-4o", api_key="sk-...")
    evaluation = load_evaluation(Path("evaluations/prompt-clarity.yaml"))
    engine = Engine(provider=provider)

    tasks = [
        engine.optimize(content=p, evaluation=evaluation, max_iterations=5)
        for p in prompts
    ]
    results = await asyncio.gather(*tasks)
    return [r.best_content for r in results]
```
