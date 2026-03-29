# Asset Types

An asset is any piece of content that can be iteratively improved. Asset Optimizer
ships three built-in types and supports custom types via `AssetTypeProtocol`.

## Built-in Types

### prompt

Optimizes text prompts — system prompts, user prompt templates, instruction strings.

- **File extensions**: `.txt`, `.md`, `.prompt`
- **Validation**: must not be empty
- **Default criteria**: clarity, specificity, effectiveness (each scored 0–10)
- **Default scorer mix**: 20% heuristic, 80% AI judge

Example prompt file (`assets/system-prompt.txt`):

```
You are a helpful assistant. Answer questions concisely.
```

After optimization the engine might produce:

```
You are a knowledgeable, concise assistant. When answering questions:
- Lead with the direct answer before any explanation
- Limit responses to 3 sentences unless the user asks for detail
- If uncertain, say so and offer to search for more information
```

### skill

Optimizes Claude Code skill files — markdown documents with YAML frontmatter that
describe how Claude should approach a class of tasks.

- **File extensions**: `.md`
- **Validation**: must have `---` YAML frontmatter with `name` and `description` keys
- **Default criteria**: structure, completeness, clarity, actionability
- **Default scorer mix**: 30% heuristic, 70% AI judge

Example skill file (`assets/code-review.md`):

```markdown
---
name: code-review
description: Review pull requests for correctness and style
---

When reviewing code:
1. Check for logic errors first
2. Then style and readability
3. Suggest specific improvements
```

### image

Optimizes image generation prompts — text strings passed to DALL-E, Stable Diffusion,
or other image generation models.

- **File extensions**: `.txt`, `.prompt`
- **Validation**: must not be empty; must be under 4000 characters
- **Default criteria**: prompt_specificity, prompt_style, image_quality, image_relevance
- **Default scorer mix**: 10% heuristic, 90% AI judge

Example image prompt (`assets/hero-banner.txt`):

```
A mountain landscape at sunset
```

After optimization:

```
A dramatic alpine landscape at golden hour, jagged snow-capped peaks reflecting
warm amber light, foreground wildflowers in sharp focus, cinematic wide-angle
composition, photorealistic, 8K, shot on Sony A7R IV
```

## Creating a Custom Asset Type

Implement `AssetTypeProtocol` to add support for any content type.

```python
from pathlib import Path
from typing import Any
from asset_optimizer.assets.base import AssetContent, AssetTypeProtocol


class JSONSchemaAssetType:
    """Optimizes JSON Schema documents for clarity and completeness."""

    name: str = "json_schema"
    file_extensions: list[str] = [".json", ".schema.json"]

    def load(self, path: Path) -> AssetContent:
        import json
        raw = path.read_text(encoding="utf-8")
        return AssetContent(text=raw, metadata={"parsed": json.loads(raw)})

    def save(self, content: AssetContent, path: Path) -> None:
        path.write_text(content.text or "", encoding="utf-8")

    def validate(self, content: AssetContent) -> list[str]:
        import json
        errors: list[str] = []
        try:
            json.loads(content.text or "")
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {e}")
        return errors

    def default_evaluation(self) -> dict[str, Any]:
        return {
            "asset_type": "json_schema",
            "criteria": [
                {
                    "name": "completeness",
                    "description": "Are all fields described with types and descriptions?",
                    "max_score": 10,
                },
                {
                    "name": "examples",
                    "description": "Does the schema include example values?",
                    "max_score": 10,
                },
            ],
            "scorer_config": {"type": "composite", "heuristic_weight": 0.3, "ai_judge_weight": 0.7},
        }

    def render_for_prompt(self, content: AssetContent) -> str:
        return f"```json\n{content.text}\n```"
```

### Protocol Reference

Every asset type must satisfy `AssetTypeProtocol`:

| Method | Signature | Purpose |
|---|---|---|
| `load` | `(path: Path) -> AssetContent` | Read file into content container |
| `save` | `(content: AssetContent, path: Path) -> None` | Write content back to disk |
| `validate` | `(content: AssetContent) -> list[str]` | Return list of error strings (empty = valid) |
| `default_evaluation` | `() -> dict[str, Any]` | Evaluation config used when none is supplied |
| `render_for_prompt` | `(content: AssetContent) -> str` | Format content for inclusion in an LLM prompt |

### AssetContent Fields

```python
from asset_optimizer.assets.base import AssetContent

content = AssetContent(
    text="...",          # string content (used for text-based assets)
    file_path=Path(...), # optional path reference
    metadata={},         # arbitrary key-value store for parsed data, EXIF, etc.
)
```
