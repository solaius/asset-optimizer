# Providers

Providers are the AI backends used for two distinct roles:

- **Generation provider** — rewrites content to improve it
- **Judge provider** — scores content against evaluation criteria (supports optional image input for multimodal judging)

You can use the same provider for both roles, or different providers. A common pattern
is to use a fast/cheap model for generation and a smarter model for judging.

## Auto-Configuration via .env

The easiest way to configure providers is through environment variables in `.env`.
The factory functions read these automatically:

```bash
# .env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...

TEXT_PROVIDER=openai          # openai | anthropic | gemini
JUDGE_PROVIDER=openai
IMAGE_PROVIDER=openai_image   # openai_image | gemini | nano_banana
```

```python
from asset_optimizer import create_text_provider, create_judge_provider, create_image_provider, create_engine

# Each factory reads from .env automatically
text_provider  = create_text_provider()
judge_provider = create_judge_provider()
image_provider = create_image_provider()

# Or wire everything at once
engine = create_engine()
```

## Text Providers

### OpenAI

Uses OpenAI's chat completion API. Supports multimodal judging (GPT-4o vision).

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

Supported models: `gpt-4o`, `gpt-4o-mini`, `o1`, `o3-mini`, and any other model
available in your OpenAI account.

Vision judging is supported for `gpt-4o` and `gpt-4o-mini`.

---

### Anthropic (Claude)

Uses Anthropic's Messages API. System messages are handled automatically.
Supports multimodal judging (Claude Sonnet/Opus vision).

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

Vision judging is supported for Sonnet and Opus variants.

---

### Google Gemini

Uses the `google-genai` SDK. Supports multimodal judging.

**Python:**

```python
from asset_optimizer.providers.gemini_provider import GeminiProvider

provider = GeminiProvider(
    model="gemini-2.0-flash",
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
      model: gemini-2.0-flash
```

Supported models: `gemini-2.0-flash`, `gemini-2.5-pro`, and other models in the
Gemini family.

Note: The provider uses the `google-genai` SDK (not the deprecated
`google-generativeai` SDK).

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

Image providers implement `ImageProvider` and generate images from text prompts.
When an image provider is configured on the `Engine`, the visual optimization loop
activates: images are generated each iteration and passed to the multimodal judge.

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

### Google Gemini Image

Uses the `google-genai` SDK for Gemini image generation.

**Python:**

```python
from asset_optimizer.providers.image_providers.gemini_image import GeminiImageProvider

provider = GeminiImageProvider(
    model="imagen-3.0-generate-002",
    api_key="AIza...",
)
```

**YAML:**

```yaml
providers:
  image:
    default: gemini
    gemini:
      api_key: ${GEMINI_API_KEY}
      model: imagen-3.0-generate-002
```

Note: Uses the `google-genai` SDK (not the deprecated `google-generativeai` SDK).

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

Or with factory functions and `.env` presets:

```python
from asset_optimizer import create_engine

# Set TEXT_PROVIDER=openai and JUDGE_PROVIDER=anthropic in .env
engine = create_engine()
```

## Multimodal Judging

All three text providers (OpenAI, Anthropic, Gemini) support multimodal judging.
The `judge()` method accepts an optional `image: bytes` parameter:

```python
# Used internally by the engine when image_provider is set
result = await provider.judge(
    content="A mountain lake at golden hour",
    criteria=criteria,
    image=image_bytes,   # passes image to vision model
)
```

Criteria with `requires_image: true` in the evaluation YAML are only scored when
an image is provided; they are skipped in text-only runs.
