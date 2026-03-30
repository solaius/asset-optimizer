# Asset Optimizer

Automatic asset optimization using the autoimprove pattern. Point it at a prompt, skill, or image generation prompt — it iteratively improves it using AI-judged scoring until it converges on a better version.

## Features

- **Three built-in asset types**: prompts, Claude Code skills, image generation prompts
- **Extensible**: add custom asset types with a simple protocol
- **Multiple AI providers**: OpenAI, Anthropic Claude, Google Gemini, vLLM, Ollama
- **Image generation**: OpenAI DALL-E, Gemini image generation, Nano Banana
- **Visual optimization loop**: generate images each iteration, use GPT-4o vision to judge them, improve the prompt from visual feedback
- **Dual scoring**: heuristic (fast, deterministic) + AI-judged (nuanced, multimodal)
- **Three convergence strategies**: greedy, target score, fixed budget
- **Four entry points**: Python library, CLI, REST API, web dashboard
- **Production-ready**: SQLite/PostgreSQL, Docker, Helm, OpenShift
- **Auto-wired factory functions**: `create_text_provider()`, `create_image_provider()`, `create_engine()` — configured from `.env` + YAML, no boilerplate

## Quick Start

```bash
# Install
pip install asset-optimizer

# Copy and fill in your API keys
cp .env.example .env
# edit .env

# Or configure via YAML
asset-optimizer init my-project && cd my-project

# Optimize a prompt
echo "You are a helpful assistant." > prompt.txt
asset-optimizer optimize prompt.txt --evaluation prompt-clarity --iterations 10

# Or use the web UI
asset-optimizer serve
# Open http://localhost:8000
```

## As a Python Library

The simplest way — use the factory functions that auto-configure from your `.env`:

```python
from asset_optimizer import create_engine, load_evaluation

engine = create_engine()  # reads OPENAI_API_KEY / ANTHROPIC_API_KEY from .env
evaluation = load_evaluation("evaluations/prompt-clarity.yaml")

result = await engine.optimize(
    content="You are a helpful assistant.",
    evaluation=evaluation,
    max_iterations=10,
)
print(f"Score: {result.initial_score} -> {result.best_score}")
print(f"Total cost: ${result.total_cost:.4f}")
```

Manual provider construction is also supported:

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
```

## Visual Image Optimization

When an image provider is configured, the engine generates an image each iteration and uses multimodal AI judging (GPT-4o vision) to score the actual image — not just the prompt text:

```python
from asset_optimizer import create_engine, load_evaluation

engine = create_engine()  # auto-wires image provider when IMAGE_PROVIDER is set in .env
evaluation = load_evaluation("evaluations/image-visual.yaml")

result = await engine.optimize(
    content="A serene mountain lake at golden hour, photorealistic",
    evaluation=evaluation,
    max_iterations=8,
)
print(f"Score: {result.initial_score:.2f} -> {result.best_score:.2f}")
# result.best_image contains the final generated image bytes
# result.best_image_format is "png" or "jpg"
```

See `examples/img-prompt-enhancement/` for runnable scripts.

## Environment Configuration

Provider selection and API keys are read from `.env`:

```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...

TEXT_PROVIDER=openai          # openai | anthropic | gemini
JUDGE_PROVIDER=openai
IMAGE_PROVIDER=openai_image   # openai_image | gemini | nano_banana
```

Copy `.env.example` for the full list of options.

## Documentation

- [Getting Started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [Asset Types](docs/asset-types.md)
- [Providers](docs/providers.md)
- [Evaluations](docs/evaluations.md)
- [API Reference](docs/api-reference.md)
- [Library Usage](docs/library-usage.md)
- [Extending](docs/extending.md)
- [Deployment](docs/deployment.md)
- [Development](docs/development.md)

## Development

```bash
uv sync                              # Install dependencies
cp .env.example .env                 # Configure API keys
uv run pytest                        # Run tests
uv run ruff check src/ tests/        # Lint
uv run mypy src/asset_optimizer/     # Type check
uv run asset-optimizer serve         # Start dev server
```

## License

MIT
