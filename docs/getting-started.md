# Getting Started

Asset Optimizer is a Python framework for automatically improving assets — prompts,
skills, and images — using the autoimprove pattern. It runs an iterative loop where an
AI provider generates improved content, a judge scores it, and the best version is kept.

## Installation

### With UV (recommended)

```bash
uv pip install asset-optimizer
```

### With pip

```bash
pip install asset-optimizer
```

Requires Python 3.12 or later.

## Configure Providers via .env

The easiest way to configure providers is with a `.env` file. Copy the example and
fill in your keys:

```bash
cp .env.example .env
```

```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...

# Which provider to use for each role
TEXT_PROVIDER=openai          # openai | anthropic | gemini
JUDGE_PROVIDER=openai
IMAGE_PROVIDER=openai_image   # openai_image | gemini | nano_banana
```

The factory functions (`create_text_provider`, `create_engine`, etc.) read these
variables automatically — no manual wiring needed.

## Initialize a Project

Run `init` to scaffold the standard directory layout:

```bash
asset-optimizer init
```

Or target a specific directory:

```bash
asset-optimizer init my-project
cd my-project
```

This creates:

```
my-project/
  assets/          # place your asset files here
  evaluations/     # evaluation YAML files
  data/            # SQLite database (auto-created)
  asset-optimizer.yaml
```

## Configure Providers via YAML

If you prefer YAML over `.env`, edit `asset-optimizer.yaml`. Use `${VAR}` to keep
secrets out of the file:

```yaml
storage:
  backend: sqlite
  sqlite_path: ./data/optimizer.db

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
      model: dall-e-3

defaults:
  max_iterations: 20
  convergence_strategy: greedy
  stagnation_limit: 5
  min_improvement: 0.01
```

Copy `asset-optimizer.yaml.example` from the repository for the full set of options
including vLLM, Ollama, Gemini image generation, and Nano Banana.

## Run Your First Optimization

### Using the Python library (with factory functions)

The factory functions auto-configure from your `.env` file:

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
    print(f"Score improved: {result.initial_score:.2f} -> {result.best_score:.2f}")
    print(f"Total cost: ${result.total_cost:.4f}")
    print(result.best_content)

asyncio.run(main())
```

You can also construct providers manually:

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
    print(f"Score improved: {result.initial_score:.2f} -> {result.best_score:.2f}")
    print(result.best_content)

asyncio.run(main())
```

The `Engine` accepts any `TextProvider` for both generation and judging. You can
use separate providers for each — for example, use a fast model to generate and a
smarter model to judge.

### Using the CLI

Start the server and use the web UI to run experiments:

```bash
asset-optimizer serve
```

The server starts on `http://localhost:8000` by default. Open that URL to access the
React-based web interface where you can create evaluations, run experiments, and
browse results.

Use `--port` and `--host` to customise the binding:

```bash
asset-optimizer serve --host 127.0.0.1 --port 9000
```

## Image Optimization

When an image provider is set, the engine generates an image each iteration and uses
multimodal AI judging (GPT-4o vision or equivalent) to evaluate the actual image —
not just the prompt text.

```python
import asyncio
from asset_optimizer import create_engine, load_evaluation

async def main():
    # Set IMAGE_PROVIDER=openai_image in .env to enable image generation
    engine = create_engine()
    evaluation = load_evaluation("evaluations/image-visual.yaml")

    result = await engine.optimize(
        content="A serene mountain lake at golden hour, photorealistic",
        evaluation=evaluation,
        max_iterations=8,
        convergence_strategy="budget",   # recommended for image runs
    )
    print(f"Score: {result.initial_score:.2f} -> {result.best_score:.2f}")
    print(f"Cost: ${result.total_cost:.4f}")

    if result.best_image:
        with open(f"output.{result.best_image_format}", "wb") as f:
            f.write(result.best_image)

asyncio.run(main())
```

See `examples/img-prompt-enhancement/` for more runnable scripts.

## Start the Web UI

The web UI is served automatically by `asset-optimizer serve`. It provides:

- An experiment dashboard with score progression charts
- Per-iteration cards showing generated images and score bars with reasoning
- Clickable evaluations with criteria and rubrics
- An evaluation builder for creating scoring rubrics
- A provider configuration panel

Visit `http://localhost:8000` after starting the server.

## Next Steps

- See [asset-types.md](asset-types.md) to understand prompt, skill, and image assets
- See [evaluations.md](evaluations.md) to write scoring criteria
- See [providers.md](providers.md) for all provider configuration options
- See [library-usage.md](library-usage.md) for more Python library examples
