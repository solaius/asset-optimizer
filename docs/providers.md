# Providers

Providers are the AI backends used for two distinct roles:

- **Generation provider** — rewrites content to improve it
- **Judge provider** — scores content against evaluation criteria

You can use the same provider for both roles, or different providers. A common pattern
is to use a fast/cheap model for generation and a smarter model for judging.

## Text Providers

### OpenAI

Uses OpenAI's chat completion API.

**Python:**

```python
from asset_optimizer.providers.openai_provider import OpenAITextProvider

provider = OpenAITextProvider(
    model="gpt-4o",
    api_key="sk-...",
)
```

**YAML (`asset-optimizer.yaml`):**

```yaml
providers:
  text:
    default: openai
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o
```

Supported models: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `o1`, `o3-mini`, and any
other model available in your OpenAI account.

---

### Anthropic (Claude)

Uses Anthropic's Messages API. System messages are handled automatically.

**Python:**

```python
from asset_optimizer.providers.anthropic_provider import AnthropicProvider

provider = AnthropicProvider(
    model="claude-sonnet-4-20250514",
    api_key="sk-ant-...",
    max_tokens=4096,
)
```

**YAML:**

```yaml
providers:
  text:
    default: claude
    claude:
      api_key: ${ANTHROPIC_API_KEY}
      model: claude-sonnet-4-20250514
```

Supported models: `claude-opus-4-5`, `claude-sonnet-4-20250514`,
`claude-haiku-3-5-latest`, and other Claude models.

---

### Google Gemini

Uses the `google-generativeai` SDK. Messages are combined into a single prompt.

**Python:**

```python
from asset_optimizer.providers.gemini_provider import GeminiProvider

provider = GeminiProvider(
    model="gemini-1.5-flash",
    api_key="AIza...",
)
```

**YAML:**

```yaml
providers:
  text:
    default: gemini
    gemini:
      api_key: ${GEMINI_API_KEY}
      model: gemini-1.5-flash
```

Supported models: `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-2.0-flash`, and
other models in the Gemini family.

---

### vLLM (OpenAI-compatible)

Self-hosted inference using vLLM's OpenAI-compatible endpoint.

**Python:**

```python
from asset_optimizer.providers.openai_compat import OpenAICompatProvider

provider = OpenAICompatProvider(
    model="mistralai/Mistral-7B-Instruct-v0.3",
    base_url="http://localhost:8000/v1",
    api_key="EMPTY",
)
```

**YAML:**

```yaml
providers:
  text:
    default: vllm
    vllm:
      base_url: http://localhost:8000/v1
      model: mistralai/Mistral-7B-Instruct-v0.3
      api_key: EMPTY
```

Start vLLM:

```bash
vllm serve mistralai/Mistral-7B-Instruct-v0.3 --port 8000
```

---

### Ollama (OpenAI-compatible)

Local inference using Ollama's OpenAI-compatible API.

**Python:**

```python
from asset_optimizer.providers.openai_compat import OpenAICompatProvider

provider = OpenAICompatProvider(
    model="llama3",
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)
```

**YAML:**

```yaml
providers:
  text:
    default: ollama
    ollama:
      base_url: http://localhost:11434/v1
      model: llama3
      api_key: ollama
```

Start Ollama and pull a model:

```bash
ollama pull llama3
ollama serve
```

## Image Providers

Image providers implement `ImageProvider` and are used when the asset type is
`image`. They generate images from text prompts.

### OpenAI Image (DALL-E)

**Python:**

```python
from asset_optimizer.providers.image_providers.openai_image import OpenAIImageProvider

provider = OpenAIImageProvider(
    model="dall-e-3",
    api_key="sk-...",
    size="1024x1024",
    quality="standard",
)
```

**YAML:**

```yaml
providers:
  image:
    default: openai_image
    openai_image:
      api_key: ${OPENAI_API_KEY}
      model: dall-e-3
```

Available sizes for DALL-E 3: `1024x1024`, `1792x1024`, `1024x1792`.
Quality options: `standard`, `hd`.

---

### Nano Banana

A fast, low-cost image generation REST API.

**Python:**

```python
from asset_optimizer.providers.image_providers.nano_banana import NanoBananaProvider

provider = NanoBananaProvider(
    base_url="https://api.nanobanana.com/v1",
    api_key="nb-...",
    model="default",
    timeout=60.0,
)
```

**YAML:**

```yaml
providers:
  image:
    default: nano_banana
    nano_banana:
      base_url: https://api.nanobanana.com/v1
      api_key: ${NANO_BANANA_API_KEY}
      model: default
```

## Using Different Providers for Generation and Judging

```python
from asset_optimizer import Engine
from asset_optimizer.providers.openai_provider import OpenAITextProvider
from asset_optimizer.providers.anthropic_provider import AnthropicProvider

# Fast model for generation, smart model for judging
generator = OpenAITextProvider(model="gpt-4o-mini", api_key="sk-...")
judge = AnthropicProvider(model="claude-sonnet-4-20250514", api_key="sk-ant-...")

engine = Engine(provider=generator, judge_provider=judge)
```
