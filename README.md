# Asset Optimizer

Automatic asset optimization using the autoimprove pattern. Point it at a prompt, skill, or image generation prompt — it iteratively improves it using AI-judged scoring until it converges on a better version.

## Features

- **Three built-in asset types**: prompts, Claude Code skills, image generation prompts
- **Extensible**: add custom asset types with a simple protocol
- **Multiple AI providers**: OpenAI, Anthropic Claude, Google Gemini, vLLM, Ollama
- **Image generation**: OpenAI Image 01, Nano Banana
- **Dual scoring**: heuristic (fast, deterministic) + AI-judged (nuanced)
- **Three convergence strategies**: greedy, target score, fixed budget
- **Four entry points**: Python library, CLI, REST API, web dashboard
- **Production-ready**: SQLite/PostgreSQL, Docker, Helm, OpenShift

## Quick Start

```bash
# Install
pip install asset-optimizer

# Initialize project
asset-optimizer init my-project && cd my-project

# Configure provider (set OPENAI_API_KEY env var)
# Edit asset-optimizer.yaml

# Optimize a prompt
echo "You are a helpful assistant." > prompt.txt
asset-optimizer optimize prompt.txt --evaluation prompt-clarity --iterations 10

# Or use the web UI
asset-optimizer serve
# Open http://localhost:8000
```

## As a Python Library

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
print(f"Score: {result.initial_score} -> {result.best_score}")
```

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
uv run pytest                        # Run tests
uv run ruff check src/ tests/        # Lint
uv run mypy src/asset_optimizer/     # Type check
uv run asset-optimizer serve         # Start dev server
```

## License

MIT
