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

## Configure Providers

Edit `asset-optimizer.yaml` to add your API keys. Use environment variable
interpolation (`${VAR}`) to keep secrets out of the file:

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
including vLLM, Ollama, and Nano Banana.

## Run Your First Optimization

### Using the Python library

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

## Start the Web UI

The web UI is served automatically by `asset-optimizer serve`. It provides:

- An experiment dashboard showing all runs and their scores
- An evaluation builder for creating scoring rubrics
- A provider configuration panel
- Per-iteration history with content diffs

Visit `http://localhost:8000` after starting the server.

## Next Steps

- See [asset-types.md](asset-types.md) to understand prompt, skill, and image assets
- See [evaluations.md](evaluations.md) to write scoring criteria
- See [providers.md](providers.md) for all provider configuration options
- See [library-usage.md](library-usage.md) for more Python library examples
