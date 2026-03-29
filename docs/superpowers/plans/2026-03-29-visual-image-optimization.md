# Visual Image Optimization Loop — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the optimization engine to generate images, evaluate them with a multimodal AI judge, and feed visual feedback back into prompt improvement — full stack from engine to UI.

**Architecture:** Extend the existing `Engine` class with an optional `image_provider` parameter. When set, the optimize loop generates an image each iteration, passes it alongside text to a multimodal judge, and uses visual feedback to improve the prompt. Image artifacts are stored to disk in experiment-scoped directories and served via a new API endpoint.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0, pytest, React 18 + TypeScript + Tailwind CSS

---

## File Map

| Action | File | Responsibility |
|--------|------|---------------|
| Modify | `src/asset_optimizer/core/evaluation.py` | Add `requires_image` to `CriterionConfig` |
| Modify | `src/asset_optimizer/providers/base.py` | Add `requires_image` to `Criterion`, add `image`/`image_format` params to `TextProvider.judge()` |
| Modify | `src/asset_optimizer/scoring/base.py` | Add `cost` field to `ScoreResult` |
| Modify | `src/asset_optimizer/scoring/ai_judge.py` | Accept optional image, filter criteria by `requires_image` |
| Modify | `src/asset_optimizer/providers/openai_provider.py` | Multimodal judge support |
| Modify | `src/asset_optimizer/providers/anthropic_provider.py` | Multimodal judge support |
| Modify | `src/asset_optimizer/providers/gemini_provider.py` | Multimodal judge support |
| Modify | `src/asset_optimizer/core/engine.py` | Add `image_provider`, image gen in loop, visual feedback, cost tracking, early stop |
| Create | `src/asset_optimizer/storage/image_storage.py` | Write/read/delete image files on disk |
| Modify | `src/asset_optimizer/providers/factory.py` | Add `create_engine()` convenience function |
| Create | `evaluations/image-visual.yaml` | Visual evaluation criteria |
| Modify | `src/asset_optimizer/api/schemas.py` | Add iteration/experiment image+cost fields |
| Create | `src/asset_optimizer/api/routes/assets.py` | `GET /api/v1/assets/{id}/image` endpoint |
| Modify | `src/asset_optimizer/api/app.py` | Register assets router |
| Modify | `src/asset_optimizer/storage/repository.py` | Add `get_asset_version()` method |
| Modify | `ui/src/api/client.ts` | Add image URL helper, update types |
| Modify | `ui/src/pages/ExperimentDetail.tsx` | Best image panel, expandable iteration images, cost summary |
| Modify | `tests/unit/test_evaluation.py` | Test `requires_image` field |
| Modify | `tests/unit/test_providers.py` | Test multimodal judge on all providers |
| Modify | `tests/unit/test_scoring.py` | Test AIJudgeScorer with image |
| Modify | `tests/unit/test_engine.py` | Test engine with image provider |
| Create | `tests/unit/test_image_storage.py` | Test image write/read/delete |
| Modify | `tests/unit/test_factory.py` | Test `create_engine()` |
| Modify | `tests/unit/test_api.py` | Test image serving endpoint |

---

### Task 1: Add `requires_image` to CriterionConfig and Criterion

**Files:**
- Modify: `src/asset_optimizer/core/evaluation.py:14-20`
- Modify: `src/asset_optimizer/providers/base.py:16-23`
- Test: `tests/unit/test_evaluation.py`
- Test: `tests/unit/test_providers.py`

- [ ] **Step 1: Write failing test for CriterionConfig.requires_image**

In `tests/unit/test_evaluation.py`, add:

```python
class TestCriterionConfig:
    def test_requires_image_defaults_false(self) -> None:
        c = CriterionConfig(name="clarity", description="Is it clear?")
        assert c.requires_image is False

    def test_requires_image_set_true(self) -> None:
        c = CriterionConfig(
            name="visual_quality",
            description="Is the image sharp?",
            requires_image=True,
        )
        assert c.requires_image is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_evaluation.py::TestCriterionConfig -v`
Expected: FAIL — `CriterionConfig.__init__() got an unexpected keyword argument 'requires_image'`

- [ ] **Step 3: Add `requires_image` field to CriterionConfig**

In `src/asset_optimizer/core/evaluation.py`, change the `CriterionConfig` class:

```python
class CriterionConfig(BaseModel):
    """A single evaluation criterion."""

    name: str
    description: str
    max_score: float = 10.0
    rubric: str = ""
    requires_image: bool = False
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_evaluation.py::TestCriterionConfig -v`
Expected: PASS

- [ ] **Step 5: Write failing test for Criterion.requires_image**

In `tests/unit/test_providers.py`, in the `TestMessageTypes` class, add:

```python
    def test_criterion_requires_image_default(self) -> None:
        c = Criterion(name="clarity", description="Is it clear?")
        assert c.requires_image is False

    def test_criterion_requires_image_true(self) -> None:
        c = Criterion(
            name="visual_quality",
            description="Sharp?",
            requires_image=True,
        )
        assert c.requires_image is True
```

- [ ] **Step 6: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_providers.py::TestMessageTypes::test_criterion_requires_image_default -v`
Expected: FAIL — `TypeError: Criterion.__init__() got an unexpected keyword argument 'requires_image'`

- [ ] **Step 7: Add `requires_image` field to Criterion dataclass**

In `src/asset_optimizer/providers/base.py`, change the `Criterion` class:

```python
@dataclass
class Criterion:
    """A single evaluation criterion for judging content."""

    name: str
    description: str
    max_score: float = 10.0
    rubric: str = ""
    requires_image: bool = False
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_providers.py::TestMessageTypes tests/unit/test_evaluation.py::TestCriterionConfig -v`
Expected: All PASS

- [ ] **Step 9: Add `cost` field to ScoreResult**

In `src/asset_optimizer/scoring/base.py`, change the `ScoreResult` class:

```python
@dataclass
class ScoreResult:
    """Result of scoring content against a single criterion."""

    criterion: str
    value: float
    max_value: float = 10.0
    scorer_type: str = "heuristic"
    details: dict[str, object] = field(default_factory=dict)
    cost: float | None = None
```

- [ ] **Step 10: Run full test suite to ensure no regressions**

Run: `uv run pytest tests/ -v`
Expected: All existing tests PASS

- [ ] **Step 11: Commit**

```bash
git add src/asset_optimizer/core/evaluation.py src/asset_optimizer/providers/base.py src/asset_optimizer/scoring/base.py tests/unit/test_evaluation.py tests/unit/test_providers.py
git commit -m "feat: add requires_image to CriterionConfig/Criterion, cost to ScoreResult"
```

---

### Task 2: Add multimodal image support to TextProvider.judge() — base + OpenAI

**Files:**
- Modify: `src/asset_optimizer/providers/base.py:50-61`
- Modify: `src/asset_optimizer/providers/openai_provider.py:55-72`
- Test: `tests/unit/test_providers.py`

- [ ] **Step 1: Write failing test for TextProvider.judge() with image param**

In `tests/unit/test_providers.py`, update `FakeTextProvider` and add a test:

```python
class FakeTextProvider(TextProvider):
    async def complete(self, messages: list[Message], **kwargs: object) -> str:
        return "fake response"

    async def judge(
        self,
        content: str,
        criteria: list[Criterion],
        image: bytes | None = None,
        image_format: str = "png",
    ) -> JudgmentResult:
        return JudgmentResult(
            scores=[
                JudgmentScore(criterion=c.name, score=5.0, reasoning="ok")
                for c in criteria
            ]
        )
```

Add a new test class:

```python
class TestMultimodalJudge:
    @pytest.mark.asyncio
    async def test_judge_with_image(self) -> None:
        provider = FakeTextProvider()
        criteria = [
            Criterion(name="visual_quality", description="Sharp?", requires_image=True),
        ]
        result = await provider.judge(
            "a sunset", criteria, image=b"fake-png-data", image_format="png"
        )
        assert len(result.scores) == 1
        assert result.scores[0].criterion == "visual_quality"

    @pytest.mark.asyncio
    async def test_judge_without_image(self) -> None:
        provider = FakeTextProvider()
        criteria = [Criterion(name="clarity", description="Clear?")]
        result = await provider.judge("test content", criteria)
        assert len(result.scores) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_providers.py::TestMultimodalJudge -v`
Expected: FAIL — `TypeError: TextProvider.judge() got an unexpected keyword argument 'image'`

- [ ] **Step 3: Update TextProvider base class**

In `src/asset_optimizer/providers/base.py`, update the `judge` abstract method:

```python
class TextProvider(ABC):
    """Abstract base class for text-based AI providers."""

    @abstractmethod
    async def complete(self, messages: list[Message], **kwargs: object) -> str:
        """Generate a text completion from a list of messages."""
        ...

    @abstractmethod
    async def judge(
        self,
        content: str,
        criteria: list[Criterion],
        image: bytes | None = None,
        image_format: str = "png",
    ) -> JudgmentResult:
        """Judge content against a list of criteria and return scores."""
        ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_providers.py::TestMultimodalJudge -v`
Expected: PASS

- [ ] **Step 5: Write failing test for OpenAI multimodal judge**

In `tests/unit/test_providers.py`, add:

```python
class TestOpenAIMultimodalJudge:
    @pytest.mark.asyncio
    async def test_judge_builds_multimodal_message(self) -> None:
        """Verify that when image is provided, the prompt includes image instruction."""
        import base64
        from unittest.mock import AsyncMock, patch

        from asset_optimizer.providers.openai_provider import OpenAITextProvider

        provider = OpenAITextProvider(model="gpt-4o", api_key="sk-test")
        fake_image = b"fake-png-bytes"

        # Mock complete to capture what's sent
        captured_messages: list[Message] = []

        async def mock_complete(messages: list[Message], **kwargs: object) -> str:
            captured_messages.extend(messages)
            return '{"scores": [{"criterion": "visual_quality", "score": 8.0, "reasoning": "sharp"}]}'

        with patch.object(provider, "complete", side_effect=mock_complete):
            criteria = [
                Criterion(name="visual_quality", description="Sharp?", requires_image=True),
            ]
            result = await provider.judge(
                "a sunset", criteria, image=fake_image, image_format="png"
            )
            assert result.scores[0].score == 8.0

    @pytest.mark.asyncio
    async def test_judge_rejects_non_vision_model(self) -> None:
        from asset_optimizer.providers.openai_provider import OpenAITextProvider

        provider = OpenAITextProvider(model="gpt-3.5-turbo", api_key="sk-test")
        criteria = [Criterion(name="visual_quality", description="Sharp?", requires_image=True)]
        with pytest.raises(ValueError, match="does not support vision"):
            await provider.judge("test", criteria, image=b"fake")
```

- [ ] **Step 6: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_providers.py::TestOpenAIMultimodalJudge -v`
Expected: FAIL — `TypeError: OpenAITextProvider.judge() got an unexpected keyword argument 'image'`

- [ ] **Step 7: Implement multimodal judge in OpenAITextProvider**

In `src/asset_optimizer/providers/openai_provider.py`, replace the `judge` method:

```python
import base64 as _base64

# Add at module level, after existing constants:
_VISION_MODELS = {"gpt-4o", "gpt-4o-mini", "gpt-4-turbo"}


class OpenAITextProvider(TextProvider):
    # ... (complete stays the same)

    async def judge(
        self,
        content: str,
        criteria: list[Criterion],
        image: bytes | None = None,
        image_format: str = "png",
    ) -> JudgmentResult:
        """Judge content against criteria using the OpenAI model."""
        if image is not None and self.model not in _VISION_MODELS:
            raise ValueError(
                f"Model {self.model} does not support vision. "
                f"Use one of: {', '.join(sorted(_VISION_MODELS))}"
            )

        criteria_text = "\n".join(
            f"- {c.name} (max {c.max_score}): {c.description}"
            + (f"\n  Rubric: {c.rubric}" if c.rubric else "")
            for c in criteria
        )

        if image is not None:
            b64_data = _base64.b64encode(image).decode("ascii")
            data_uri = f"data:image/{image_format};base64,{b64_data}"
            prompt = (
                f"{_JUDGE_INTRO}"
                f"Image generation prompt to evaluate:\n{content}\n\n"
                "The generated image is attached. Evaluate BOTH the prompt text "
                "AND the generated image against the criteria below.\n\n"
                f"Criteria:\n{criteria_text}\n\n"
                f"Respond with a JSON object in this exact format:\n{_JSON_FORMAT}"
            )
            oai_messages: list[dict[str, object]] = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": data_uri, "detail": "high"},
                        },
                    ],
                }
            ]
            response = await self._client.chat.completions.create(
                model=self.model,
                messages=oai_messages,  # type: ignore[arg-type]
                response_format={"type": "json_object"},
            )
            response_text = response.choices[0].message.content or ""
        else:
            prompt = (
                f"{_JUDGE_INTRO}"
                f"Content to evaluate:\n{content}\n\n"
                f"Criteria:\n{criteria_text}\n\n"
                f"Respond with a JSON object in this exact format:\n{_JSON_FORMAT}"
            )
            response_text = await self.complete(
                [Message(role="user", content=prompt)],
                response_format={"type": "json_object"},
            )

        return self._parse_judgment(response_text, criteria)
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_providers.py::TestOpenAIMultimodalJudge tests/unit/test_providers.py::TestMultimodalJudge -v`
Expected: All PASS

- [ ] **Step 9: Run full test suite**

Run: `uv run pytest tests/ -v`
Expected: All PASS

- [ ] **Step 10: Commit**

```bash
git add src/asset_optimizer/providers/base.py src/asset_optimizer/providers/openai_provider.py tests/unit/test_providers.py
git commit -m "feat: add multimodal image support to TextProvider.judge() and OpenAI implementation"
```

---

### Task 3: Add multimodal judge to Anthropic and Gemini providers

**Files:**
- Modify: `src/asset_optimizer/providers/anthropic_provider.py:77-92`
- Modify: `src/asset_optimizer/providers/gemini_provider.py:55-70`
- Test: `tests/unit/test_providers.py`

- [ ] **Step 1: Write failing tests for Anthropic and Gemini multimodal judge**

In `tests/unit/test_providers.py`, add:

```python
class TestAnthropicMultimodalJudge:
    @pytest.mark.asyncio
    async def test_judge_with_image_builds_multimodal_message(self) -> None:
        from unittest.mock import AsyncMock, patch

        from asset_optimizer.providers.anthropic_provider import AnthropicProvider

        provider = AnthropicProvider(model="claude-sonnet-4-20250514", api_key="sk-test")

        mock_response = AsyncMock()
        mock_block = AsyncMock()
        mock_block.text = '{"scores": [{"criterion": "visual_quality", "score": 7.0, "reasoning": "good"}]}'
        mock_response.content = [mock_block]

        with patch.object(provider._client.messages, "create", return_value=mock_response):
            criteria = [
                Criterion(name="visual_quality", description="Sharp?", requires_image=True),
            ]
            result = await provider.judge(
                "a sunset", criteria, image=b"fake-png-bytes", image_format="png"
            )
            assert result.scores[0].score == 7.0

    @pytest.mark.asyncio
    async def test_judge_rejects_non_vision_model(self) -> None:
        from asset_optimizer.providers.anthropic_provider import AnthropicProvider

        provider = AnthropicProvider(model="claude-3-haiku-20240307", api_key="sk-test")
        criteria = [Criterion(name="visual_quality", description="Sharp?", requires_image=True)]
        with pytest.raises(ValueError, match="does not support vision"):
            await provider.judge("test", criteria, image=b"fake")


class TestGeminiMultimodalJudge:
    @pytest.mark.asyncio
    async def test_judge_with_image(self) -> None:
        from unittest.mock import AsyncMock, MagicMock, patch

        from asset_optimizer.providers.gemini_provider import GeminiProvider

        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel") as mock_model_cls:
            provider = GeminiProvider(model="gemini-2.5-pro", api_key="test-key")

            mock_response = MagicMock()
            mock_response.text = '{"scores": [{"criterion": "visual_quality", "score": 8.5, "reasoning": "excellent"}]}'
            provider._generative_model.generate_content_async = AsyncMock(return_value=mock_response)

            criteria = [
                Criterion(name="visual_quality", description="Sharp?", requires_image=True),
            ]
            result = await provider.judge(
                "a sunset", criteria, image=b"fake-png-bytes", image_format="png"
            )
            assert result.scores[0].score == 8.5

    @pytest.mark.asyncio
    async def test_judge_rejects_non_vision_model(self) -> None:
        from unittest.mock import patch

        from asset_optimizer.providers.gemini_provider import GeminiProvider

        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel"):
            provider = GeminiProvider(model="gemini-1.0-pro", api_key="test-key")
            criteria = [Criterion(name="visual_quality", description="Sharp?", requires_image=True)]
            with pytest.raises(ValueError, match="does not support vision"):
                await provider.judge("test", criteria, image=b"fake")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_providers.py::TestAnthropicMultimodalJudge tests/unit/test_providers.py::TestGeminiMultimodalJudge -v`
Expected: FAIL

- [ ] **Step 3: Implement multimodal judge in AnthropicProvider**

In `src/asset_optimizer/providers/anthropic_provider.py`, add at module level and update the `judge` method:

```python
import base64 as _base64

# Add after existing constants:
_VISION_MODELS = {
    "claude-sonnet-4-20250514",
    "claude-opus-4-20250514",
    "claude-3-5-sonnet-latest",
    "claude-3-5-sonnet-20241022",
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
}


class AnthropicProvider(TextProvider):
    # ... (complete stays the same)

    async def judge(
        self,
        content: str,
        criteria: list[Criterion],
        image: bytes | None = None,
        image_format: str = "png",
    ) -> JudgmentResult:
        """Judge content against criteria using the Anthropic model."""
        if image is not None and self.model not in _VISION_MODELS:
            raise ValueError(
                f"Model {self.model} does not support vision. "
                f"Use one of: {', '.join(sorted(_VISION_MODELS))}"
            )

        criteria_text = "\n".join(
            f"- {c.name} (max {c.max_score}): {c.description}"
            + (f"\n  Rubric: {c.rubric}" if c.rubric else "")
            for c in criteria
        )

        if image is not None:
            b64_data = _base64.b64encode(image).decode("ascii")
            media_type = f"image/{image_format}"
            prompt_text = (
                f"{_JUDGE_INTRO}"
                f"Image generation prompt to evaluate:\n{content}\n\n"
                "The generated image is attached. Evaluate BOTH the prompt text "
                "AND the generated image against the criteria below.\n\n"
                f"Criteria:\n{criteria_text}\n\n"
                "Respond with a JSON object in this exact format "
                f"(no markdown, raw JSON only):\n{_JSON_FORMAT}"
            )
            message_content: list[dict[str, object]] = [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": b64_data,
                    },
                },
                {"type": "text", "text": prompt_text},
            ]
            response = await self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": message_content}],  # type: ignore[arg-type]
            )
            block = response.content[0] if response.content else None
            response_text = str(block.text) if block and hasattr(block, "text") else ""
        else:
            prompt = (
                f"{_JUDGE_INTRO}"
                f"Content to evaluate:\n{content}\n\n"
                f"Criteria:\n{criteria_text}\n\n"
                "Respond with a JSON object in this exact format "
                f"(no markdown, raw JSON only):\n{_JSON_FORMAT}"
            )
            response_text = await self.complete([Message(role="user", content=prompt)])

        return self._parse_judgment(response_text, criteria)
```

- [ ] **Step 4: Implement multimodal judge in GeminiProvider**

In `src/asset_optimizer/providers/gemini_provider.py`, add at module level and update the `judge` method:

```python
# Add after existing constants:
_VISION_MODELS = {
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
}


class GeminiProvider(TextProvider):
    # ... (complete stays the same)

    async def judge(
        self,
        content: str,
        criteria: list[Criterion],
        image: bytes | None = None,
        image_format: str = "png",
    ) -> JudgmentResult:
        """Judge content against criteria using the Gemini model."""
        if image is not None and self.model not in _VISION_MODELS:
            raise ValueError(
                f"Model {self.model} does not support vision. "
                f"Use one of: {', '.join(sorted(_VISION_MODELS))}"
            )

        criteria_text = "\n".join(
            f"- {c.name} (max {c.max_score}): {c.description}"
            + (f"\n  Rubric: {c.rubric}" if c.rubric else "")
            for c in criteria
        )

        if image is not None:
            prompt_text = (
                f"{_JUDGE_INTRO}"
                f"Image generation prompt to evaluate:\n{content}\n\n"
                "The generated image is attached. Evaluate BOTH the prompt text "
                "AND the generated image against the criteria below.\n\n"
                f"Criteria:\n{criteria_text}\n\n"
                "Respond with a JSON object in this exact format "
                f"(no markdown, raw JSON only):\n{_JSON_FORMAT}"
            )
            image_part = {
                "inline_data": {
                    "mime_type": f"image/{image_format}",
                    "data": image,
                }
            }
            response = await self._generative_model.generate_content_async(
                [prompt_text, image_part]  # type: ignore[arg-type]
            )
            response_text = str(response.text) if response.text else ""
        else:
            prompt = (
                f"{_JUDGE_INTRO}"
                f"Content to evaluate:\n{content}\n\n"
                f"Criteria:\n{criteria_text}\n\n"
                "Respond with a JSON object in this exact format "
                f"(no markdown, raw JSON only):\n{_JSON_FORMAT}"
            )
            response_text = await self.complete([Message(role="user", content=prompt)])

        return self._parse_judgment(response_text, criteria)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_providers.py::TestAnthropicMultimodalJudge tests/unit/test_providers.py::TestGeminiMultimodalJudge -v`
Expected: All PASS

- [ ] **Step 6: Update the existing FakeTextProvider and MockProvider for new signature**

In `tests/unit/test_engine.py`, update `MockProvider` and `DegradingProvider`:

```python
class MockProvider(TextProvider):
    def __init__(self) -> None:
        self.call_count = 0

    async def complete(self, messages: list[Message], **kwargs: Any) -> str:
        self.call_count += 1
        return (
            f"Improved prompt version {self.call_count}. "
            "Clear, specific, and actionable instructions for the assistant."
        )

    async def judge(
        self,
        content: str,
        criteria: list[Criterion],
        image: bytes | None = None,
        image_format: str = "png",
    ) -> JudgmentResult:
        base = min(9.0, len(content) / 20.0)
        return JudgmentResult(
            scores=[
                JudgmentScore(
                    criterion=c.name, score=min(base, c.max_score), reasoning="ok"
                )
                for c in criteria
            ]
        )


class DegradingProvider(TextProvider):
    async def complete(self, messages: list[Message], **kwargs: Any) -> str:
        return "Bad"

    async def judge(
        self,
        content: str,
        criteria: list[Criterion],
        image: bytes | None = None,
        image_format: str = "png",
    ) -> JudgmentResult:
        return JudgmentResult(
            scores=[
                JudgmentScore(criterion=c.name, score=1.0, reasoning="poor")
                for c in criteria
            ]
        )
```

- [ ] **Step 7: Run full test suite**

Run: `uv run pytest tests/ -v`
Expected: All PASS

- [ ] **Step 8: Commit**

```bash
git add src/asset_optimizer/providers/anthropic_provider.py src/asset_optimizer/providers/gemini_provider.py tests/unit/test_providers.py tests/unit/test_engine.py
git commit -m "feat: add multimodal judge support to Anthropic and Gemini providers"
```

---

### Task 4: Update AIJudgeScorer to support image scoring

**Files:**
- Modify: `src/asset_optimizer/scoring/ai_judge.py`
- Test: `tests/unit/test_scoring.py`

- [ ] **Step 1: Write failing tests for AIJudgeScorer with image**

In `tests/unit/test_scoring.py`, add these imports and test class:

```python
import pytest

from asset_optimizer.providers.base import (
    Criterion,
    JudgmentResult,
    JudgmentScore,
    Message,
    TextProvider,
)
from asset_optimizer.scoring.ai_judge import AIJudgeScorer


class _MockJudgeProvider(TextProvider):
    """Mock provider that records whether image was passed."""

    def __init__(self) -> None:
        self.last_image: bytes | None = None

    async def complete(self, messages: list[Message], **kwargs: object) -> str:
        return ""

    async def judge(
        self,
        content: str,
        criteria: list[Criterion],
        image: bytes | None = None,
        image_format: str = "png",
    ) -> JudgmentResult:
        self.last_image = image
        return JudgmentResult(
            scores=[
                JudgmentScore(criterion=c.name, score=7.0, reasoning="good")
                for c in criteria
            ]
        )


class TestAIJudgeScorerWithImage:
    @pytest.mark.asyncio
    async def test_score_with_image_passes_image_to_provider(self) -> None:
        provider = _MockJudgeProvider()
        criteria = [
            Criterion(name="clarity", description="Clear?"),
            Criterion(name="visual_quality", description="Sharp?", requires_image=True),
        ]
        scorer = AIJudgeScorer(provider=provider, criteria=criteria)
        results = await scorer.score("test content", image=b"fake-png", image_format="png")
        assert provider.last_image == b"fake-png"
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_score_without_image_skips_image_criteria(self) -> None:
        provider = _MockJudgeProvider()
        criteria = [
            Criterion(name="clarity", description="Clear?"),
            Criterion(name="visual_quality", description="Sharp?", requires_image=True),
        ]
        scorer = AIJudgeScorer(provider=provider, criteria=criteria)
        results = await scorer.score("test content")
        # Only the text-only criterion should be scored
        assert len(results) == 1
        assert results[0].criterion == "clarity"
        assert provider.last_image is None

    @pytest.mark.asyncio
    async def test_score_without_image_all_text_criteria(self) -> None:
        provider = _MockJudgeProvider()
        criteria = [
            Criterion(name="clarity", description="Clear?"),
            Criterion(name="specificity", description="Specific?"),
        ]
        scorer = AIJudgeScorer(provider=provider, criteria=criteria)
        results = await scorer.score("test content")
        assert len(results) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_scoring.py::TestAIJudgeScorerWithImage -v`
Expected: FAIL — `TypeError: AIJudgeScorer.score() got an unexpected keyword argument 'image'`

- [ ] **Step 3: Implement image support in AIJudgeScorer**

Replace `src/asset_optimizer/scoring/ai_judge.py`:

```python
"""AI-based judge scorer using a TextProvider."""

from asset_optimizer.providers.base import Criterion, TextProvider
from asset_optimizer.scoring.base import ScoreResult


class AIJudgeScorer:
    """Scores content using an AI provider's judgment capabilities.

    Not a Scorer subclass — it is async and returns multiple ScoreResults
    at once (one per criterion).
    """

    def __init__(self, provider: TextProvider, criteria: list[Criterion]) -> None:
        self.provider = provider
        self.criteria = criteria

    async def score(
        self,
        content: str,
        image: bytes | None = None,
        image_format: str = "png",
    ) -> list[ScoreResult]:
        """Judge content against criteria and return a ScoreResult per criterion.

        When *image* is None, only criteria with ``requires_image=False`` are
        scored.  Image-requiring criteria are skipped entirely (not scored as 0).
        """
        if image is not None:
            active_criteria = self.criteria
        else:
            active_criteria = [c for c in self.criteria if not c.requires_image]

        if not active_criteria:
            return []

        judgment = await self.provider.judge(
            content, active_criteria, image=image, image_format=image_format
        )

        # Build a lookup by criterion name
        scored: dict[str, ScoreResult] = {}
        for judgment_score in judgment.scores:
            scored[judgment_score.criterion] = ScoreResult(
                criterion=judgment_score.criterion,
                value=judgment_score.score,
                max_value=10.0,
                scorer_type="ai_judge",
                details={"reasoning": judgment_score.reasoning},
            )

        # Ensure every active criterion has a result
        results: list[ScoreResult] = []
        for criterion in active_criteria:
            if criterion.name in scored:
                results.append(scored[criterion.name])
            else:
                results.append(
                    ScoreResult(
                        criterion=criterion.name,
                        value=0.0,
                        max_value=criterion.max_score,
                        scorer_type="ai_judge",
                        details={"reasoning": "not scored by provider"},
                    )
                )

        return results
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_scoring.py::TestAIJudgeScorerWithImage -v`
Expected: All PASS

- [ ] **Step 5: Run full test suite**

Run: `uv run pytest tests/ -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add src/asset_optimizer/scoring/ai_judge.py tests/unit/test_scoring.py
git commit -m "feat: AIJudgeScorer accepts optional image, filters criteria by requires_image"
```

---

### Task 5: Extend Engine with image provider, visual loop, cost tracking, and early stop

**Files:**
- Modify: `src/asset_optimizer/core/engine.py`
- Test: `tests/unit/test_engine.py`

- [ ] **Step 1: Write failing tests for Engine with image provider**

In `tests/unit/test_engine.py`, add these imports and mock:

```python
from asset_optimizer.providers.base import ImageResult
from asset_optimizer.providers.image_providers.base import ImageProvider


class MockImageProvider(ImageProvider):
    def __init__(self) -> None:
        self.call_count = 0

    async def generate(self, prompt: str, **kwargs: object) -> ImageResult:
        self.call_count += 1
        return ImageResult(
            image_data=b"fake-image-" + str(self.call_count).encode(),
            format="png",
            metadata={"width": 1024, "height": 1024},
        )


class FailingImageProvider(ImageProvider):
    async def generate(self, prompt: str, **kwargs: object) -> ImageResult:
        raise RuntimeError("Content policy violation")
```

Add tests:

```python
@pytest.fixture
def image_eval_config() -> EvaluationConfig:
    return EvaluationConfig(
        name="test-image-eval",
        asset_type="image",
        criteria=[
            CriterionConfig(
                name="prompt_specificity", description="Is the prompt specific?",
            ),
            CriterionConfig(
                name="visual_quality", description="Is the image sharp?",
                requires_image=True,
            ),
        ],
        scorer_config=ScorerConfig(
            type="composite", ai_judge_weight=1.0, heuristic_weight=0.0
        ),
    )


class TestEngineWithImageProvider:
    @pytest.mark.asyncio
    async def test_optimize_with_image_provider(
        self, image_eval_config: EvaluationConfig
    ) -> None:
        provider = MockProvider()
        image_provider = MockImageProvider()
        engine = Engine(
            provider=provider, judge_provider=provider, image_provider=image_provider
        )
        result = await engine.optimize(
            content="A beautiful sunset over mountains",
            evaluation=image_eval_config,
            max_iterations=2,
        )
        assert result.best_image is not None
        assert result.best_image_format == "png"
        assert image_provider.call_count >= 1
        assert result.iterations[0].image_data is not None

    @pytest.mark.asyncio
    async def test_optimize_without_image_provider_unchanged(
        self, eval_config: EvaluationConfig
    ) -> None:
        """Existing text-only optimization still works."""
        provider = MockProvider()
        engine = Engine(provider=provider, judge_provider=provider)
        result = await engine.optimize(
            content="You are a helpful assistant.",
            evaluation=eval_config,
            max_iterations=2,
        )
        assert result.best_image is None
        assert result.stopped_early is False

    @pytest.mark.asyncio
    async def test_optimize_stops_on_image_failure(
        self, image_eval_config: EvaluationConfig
    ) -> None:
        provider = MockProvider()
        image_provider = FailingImageProvider()
        engine = Engine(
            provider=provider, judge_provider=provider, image_provider=image_provider
        )
        result = await engine.optimize(
            content="A sunset",
            evaluation=image_eval_config,
            max_iterations=5,
        )
        assert result.stopped_early is True
        assert "image generation failed" in result.stop_reason.lower()

    @pytest.mark.asyncio
    async def test_optimize_tracks_total_cost(
        self, image_eval_config: EvaluationConfig
    ) -> None:
        provider = MockProvider()
        image_provider = MockImageProvider()
        engine = Engine(
            provider=provider, judge_provider=provider, image_provider=image_provider
        )
        result = await engine.optimize(
            content="A sunset",
            evaluation=image_eval_config,
            max_iterations=2,
        )
        # total_cost should be set (even if 0.0 for mock providers)
        assert result.total_cost is not None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_engine.py::TestEngineWithImageProvider -v`
Expected: FAIL — `TypeError: Engine.__init__() got an unexpected keyword argument 'image_provider'`

- [ ] **Step 3: Implement Engine changes**

Replace `src/asset_optimizer/core/engine.py` with the full updated implementation:

```python
"""Optimization engine — the core autoimprove loop."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from asset_optimizer.core.convergence import ConvergenceStrategy, create_strategy
from asset_optimizer.providers.base import Criterion, Message, TextProvider
from asset_optimizer.scoring.ai_judge import AIJudgeScorer

if TYPE_CHECKING:
    from collections.abc import Callable

    from asset_optimizer.core.evaluation import CriterionConfig, EvaluationConfig
    from asset_optimizer.providers.image_providers.base import ImageProvider
    from asset_optimizer.scoring.base import ScoreResult

logger = logging.getLogger(__name__)


@dataclass
class IterationResult:
    """Record for a single optimization iteration."""

    iteration: int
    input_content: str
    output_content: str
    input_score: float
    output_score: float
    scores: list[ScoreResult]
    improvement_prompt: str
    accepted: bool
    duration_ms: float
    image_data: bytes | None = None
    image_format: str = ""
    image_cost: float | None = None


@dataclass
class OptimizationResult:
    """Final result of the optimization run."""

    best_content: str
    best_score: float
    initial_score: float
    total_iterations: int
    iterations: list[IterationResult] = field(default_factory=list)
    best_image: bytes | None = None
    best_image_format: str = ""
    total_cost: float | None = None
    stopped_early: bool = False
    stop_reason: str = ""


def _compute_aggregate_score(scores: list[ScoreResult]) -> float:
    """Return the mean of all ScoreResult values (normalised to 0–10)."""
    if not scores:
        return 0.0
    return sum(s.value for s in scores) / len(scores)


def _build_improvement_prompt(
    content: str,
    scores: list[ScoreResult],
    criteria: list[CriterionConfig],
) -> str:
    """Return a prompt instructing the provider to improve *content*.

    Targets the two weakest criteria with specific rubric references so the
    provider knows exactly what to fix.  When visual scores are available,
    includes the judge's reasoning about what it saw in the generated image.
    """
    # Sort by ascending score to find weakest criteria
    sorted_scores = sorted(scores, key=lambda s: s.value)
    weakest = sorted_scores[:2]

    # Build criterion detail strings with rubric if available
    criterion_map = {c.name: c for c in criteria}
    focus_parts: list[str] = []
    visual_feedback_parts: list[str] = []

    for score_result in weakest:
        crit = criterion_map.get(score_result.criterion)
        if crit is None:
            focus_parts.append(
                f"- {score_result.criterion}: "
                f"scored {score_result.value:.1f}/{score_result.max_value:.1f}"
            )
        else:
            rubric_hint = f" Rubric: {crit.rubric}" if crit.rubric else ""
            focus_parts.append(
                f"- {crit.name}: scored {score_result.value:.1f}/{crit.max_score:.1f}"
                f" — {crit.description}.{rubric_hint}"
            )

        # Collect visual feedback from image-required criteria
        reasoning = score_result.details.get("reasoning", "")
        if crit and crit.requires_image and reasoning:
            visual_feedback_parts.append(f"- {crit.name}: {reasoning}")

    focus_block = "\n".join(focus_parts)

    visual_section = ""
    if visual_feedback_parts:
        visual_block = "\n".join(visual_feedback_parts)
        visual_section = (
            "\n\nVISUAL FEEDBACK FROM THE JUDGE (about the generated image):\n"
            f"{visual_block}\n"
            "Focus on addressing these visual issues in the image generation prompt."
        )

    return (
        "You are an expert content optimizer. Improve the following content by "
        "addressing the weakest scoring criteria listed below. Return ONLY the "
        "improved content without any explanation or commentary.\n\n"
        f"CURRENT CONTENT:\n{content}\n\n"
        f"CRITERIA TO IMPROVE:\n{focus_block}"
        f"{visual_section}\n\n"
        "Provide the improved content now:"
    )


async def _generate_image_with_retry(
    image_provider: ImageProvider,
    content: str,
) -> tuple[bytes, str] | None:
    """Attempt image generation with one retry on failure.

    Returns ``(image_data, format)`` on success, or ``None`` on persistent
    failure.
    """
    for attempt in range(2):
        try:
            result = await image_provider.generate(content)
            return result.image_data, result.format
        except Exception:
            if attempt == 0:
                logger.warning("Image generation failed, retrying once...")
                continue
            return None
    return None


class Engine:
    """Core optimization engine implementing the autoimprove loop.

    Args:
        provider: The :class:`~asset_optimizer.providers.base.TextProvider` used to
            generate improved content.
        judge_provider: An optional separate provider used for scoring. Falls back to
            *provider* when not supplied.
        image_provider: An optional image generation provider. When set, the loop
            generates an image each iteration and passes it to the multimodal judge.
    """

    def __init__(
        self,
        provider: TextProvider,
        judge_provider: TextProvider | None = None,
        image_provider: ImageProvider | None = None,
    ) -> None:
        self.provider = provider
        self.judge_provider: TextProvider = (
            judge_provider if judge_provider is not None else provider
        )
        self.image_provider = image_provider

    async def optimize(
        self,
        content: str,
        evaluation: EvaluationConfig,
        max_iterations: int = 20,
        target_score: float | None = None,
        convergence_strategy: str = "greedy",
        stagnation_limit: int = 5,
        min_improvement: float = 0.01,
        on_iteration: Callable[[dict[str, Any]], None] | None = None,
    ) -> OptimizationResult:
        """Run the optimization loop and return the best content found."""
        # Build convergence strategy
        strategy_kwargs: dict[str, Any] = {}
        if convergence_strategy == "greedy":
            strategy_kwargs = {
                "stagnation_limit": stagnation_limit,
                "min_improvement": min_improvement,
            }
        elif convergence_strategy == "target":
            if target_score is None:
                raise ValueError(
                    "target_score must be provided when using "
                    "the 'target' convergence strategy"
                )
            strategy_kwargs = {"target_score": target_score}

        strategy: ConvergenceStrategy = create_strategy(
            convergence_strategy, **strategy_kwargs
        )

        # Build criteria objects for the AI judge
        criteria: list[Criterion] = [
            Criterion(
                name=c.name,
                description=c.description,
                max_score=c.max_score,
                rubric=c.rubric,
                requires_image=c.requires_image,
            )
            for c in evaluation.criteria
        ]

        scorer = AIJudgeScorer(provider=self.judge_provider, criteria=criteria)

        use_image = self.image_provider is not None

        # Cost warning for image optimization
        if use_image:
            estimated_cost = max_iterations * 0.10  # rough estimate
            if estimated_cost > 2.0:
                logger.warning(
                    "Estimated cost for %d iterations with image generation: ~$%.2f",
                    max_iterations,
                    estimated_cost,
                )

        # Generate baseline image if applicable
        baseline_image: bytes | None = None
        baseline_image_format: str = ""
        stopped_early = False
        stop_reason = ""

        if use_image:
            assert self.image_provider is not None
            gen_result = await _generate_image_with_retry(
                self.image_provider, content
            )
            if gen_result is None:
                return OptimizationResult(
                    best_content=content,
                    best_score=0.0,
                    initial_score=0.0,
                    total_iterations=0,
                    stopped_early=True,
                    stop_reason="Image generation failed on baseline",
                    total_cost=0.0,
                )
            baseline_image, baseline_image_format = gen_result

        # Score baseline
        baseline_scores = await scorer.score(
            content,
            image=baseline_image,
            image_format=baseline_image_format,
        )
        baseline_score = _compute_aggregate_score(baseline_scores)

        best_content = content
        best_score = baseline_score
        best_image = baseline_image
        best_image_format = baseline_image_format
        previous_score = baseline_score
        current_scores: list[ScoreResult] = baseline_scores
        iterations: list[IterationResult] = []
        total_cost = 0.0

        iteration = 0
        while True:
            iteration += 1
            t_start = time.monotonic()

            improvement_prompt = _build_improvement_prompt(
                content=best_content,
                scores=current_scores,
                criteria=evaluation.criteria,
            )

            messages: list[Message] = [Message(role="user", content=improvement_prompt)]
            new_content = await self.provider.complete(messages)

            # Generate image if applicable
            iter_image: bytes | None = None
            iter_image_format: str = ""
            if use_image:
                assert self.image_provider is not None
                gen_result = await _generate_image_with_retry(
                    self.image_provider, new_content
                )
                if gen_result is None:
                    stopped_early = True
                    stop_reason = "Image generation failed — returning best result so far"
                    duration_ms = (time.monotonic() - t_start) * 1000.0
                    break
                iter_image, iter_image_format = gen_result

            new_scores = await scorer.score(
                new_content,
                image=iter_image,
                image_format=iter_image_format,
            )
            new_score = _compute_aggregate_score(new_scores)

            accepted = new_score >= previous_score
            if accepted:
                best_content = new_content
                best_score = new_score
                current_scores = new_scores
                if iter_image is not None:
                    best_image = iter_image
                    best_image_format = iter_image_format

            duration_ms = (time.monotonic() - t_start) * 1000.0

            iter_result = IterationResult(
                iteration=iteration,
                input_content=content if iteration == 1 else best_content,
                output_content=new_content,
                input_score=previous_score,
                output_score=new_score,
                scores=new_scores,
                improvement_prompt=improvement_prompt,
                accepted=accepted,
                duration_ms=duration_ms,
                image_data=iter_image,
                image_format=iter_image_format,
                image_cost=0.0 if use_image else None,
            )
            iterations.append(iter_result)

            if on_iteration is not None:
                on_iteration({
                    "iteration": iteration,
                    "score": new_score,
                    "content": new_content,
                    "accepted": accepted,
                })

            convergence = strategy.check(
                iteration=iteration,
                current_score=new_score,
                previous_score=previous_score,
                max_iterations=max_iterations,
            )

            previous_score = new_score

            if not convergence.should_continue:
                break

        return OptimizationResult(
            best_content=best_content,
            best_score=best_score,
            initial_score=baseline_score,
            total_iterations=iteration if not stopped_early else len(iterations),
            iterations=iterations,
            best_image=best_image,
            best_image_format=best_image_format,
            total_cost=total_cost if use_image else None,
            stopped_early=stopped_early,
            stop_reason=stop_reason,
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_engine.py -v`
Expected: All PASS

- [ ] **Step 5: Run full test suite**

Run: `uv run pytest tests/ -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add src/asset_optimizer/core/engine.py tests/unit/test_engine.py
git commit -m "feat: engine generates images in loop, multimodal judging, visual feedback, early stop"
```

---

### Task 6: Create ImageStorage helper and evaluation config

**Files:**
- Create: `src/asset_optimizer/storage/image_storage.py`
- Create: `evaluations/image-visual.yaml`
- Test: `tests/unit/test_image_storage.py`

- [ ] **Step 1: Write failing tests for ImageStorage**

Create `tests/unit/test_image_storage.py`:

```python
"""Tests for image file storage helper."""

from __future__ import annotations

import uuid

import pytest

from asset_optimizer.storage.image_storage import ImageStorage


class TestImageStorage:
    def test_save_image(self, tmp_path) -> None:
        storage = ImageStorage(base_dir=tmp_path / "data" / "images")
        experiment_id = uuid.uuid4()
        path = storage.save(
            experiment_id=experiment_id,
            iteration_number=1,
            image_data=b"fake-png-data",
            image_format="png",
        )
        assert path.exists()
        assert path.read_bytes() == b"fake-png-data"
        assert path.name == "1.png"
        assert path.parent.name == str(experiment_id)

    def test_save_creates_directory(self, tmp_path) -> None:
        storage = ImageStorage(base_dir=tmp_path / "data" / "images")
        experiment_id = uuid.uuid4()
        path = storage.save(
            experiment_id=experiment_id,
            iteration_number=3,
            image_data=b"data",
            image_format="jpg",
        )
        assert path.parent.exists()
        assert path.name == "3.jpg"

    def test_load_image(self, tmp_path) -> None:
        storage = ImageStorage(base_dir=tmp_path / "data" / "images")
        experiment_id = uuid.uuid4()
        storage.save(experiment_id, 1, b"test-data", "png")
        data = storage.load(experiment_id, 1, "png")
        assert data == b"test-data"

    def test_load_missing_raises(self, tmp_path) -> None:
        storage = ImageStorage(base_dir=tmp_path / "data" / "images")
        with pytest.raises(FileNotFoundError):
            storage.load(uuid.uuid4(), 99, "png")

    def test_delete_experiment_images(self, tmp_path) -> None:
        storage = ImageStorage(base_dir=tmp_path / "data" / "images")
        experiment_id = uuid.uuid4()
        storage.save(experiment_id, 1, b"data1", "png")
        storage.save(experiment_id, 2, b"data2", "png")
        storage.delete_experiment(experiment_id)
        assert not (tmp_path / "data" / "images" / str(experiment_id)).exists()

    def test_delete_nonexistent_experiment_is_noop(self, tmp_path) -> None:
        storage = ImageStorage(base_dir=tmp_path / "data" / "images")
        storage.delete_experiment(uuid.uuid4())  # should not raise

    def test_load_from_path(self, tmp_path) -> None:
        storage = ImageStorage(base_dir=tmp_path / "data" / "images")
        experiment_id = uuid.uuid4()
        path = storage.save(experiment_id, 1, b"path-data", "png")
        data = storage.load_from_path(path)
        assert data == b"path-data"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_image_storage.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'asset_optimizer.storage.image_storage'`

- [ ] **Step 3: Implement ImageStorage**

Create `src/asset_optimizer/storage/image_storage.py`:

```python
"""Image file storage — write, read, and delete image artifacts on disk."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path


class ImageStorage:
    """Manages image files stored in experiment-scoped directories.

    Directory layout::

        {base_dir}/{experiment_id}/{iteration_number}.{format}
    """

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def _experiment_dir(self, experiment_id: uuid.UUID) -> Path:
        return self.base_dir / str(experiment_id)

    def _image_path(
        self, experiment_id: uuid.UUID, iteration_number: int, image_format: str
    ) -> Path:
        return self._experiment_dir(experiment_id) / f"{iteration_number}.{image_format}"

    def save(
        self,
        experiment_id: uuid.UUID,
        iteration_number: int,
        image_data: bytes,
        image_format: str,
    ) -> Path:
        """Write image bytes to disk. Returns the file path."""
        path = self._image_path(experiment_id, iteration_number, image_format)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(image_data)
        return path

    def load(
        self,
        experiment_id: uuid.UUID,
        iteration_number: int,
        image_format: str,
    ) -> bytes:
        """Read image bytes from disk."""
        path = self._image_path(experiment_id, iteration_number, image_format)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")
        return path.read_bytes()

    def load_from_path(self, path: Path) -> bytes:
        """Read image bytes from an arbitrary path."""
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")
        return path.read_bytes()

    def delete_experiment(self, experiment_id: uuid.UUID) -> None:
        """Delete all images for an experiment."""
        exp_dir = self._experiment_dir(experiment_id)
        if exp_dir.exists():
            shutil.rmtree(exp_dir)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_image_storage.py -v`
Expected: All PASS

- [ ] **Step 5: Create evaluation config**

Create `evaluations/image-visual.yaml`:

```yaml
name: image-visual
asset_type: image
description: Evaluates image generation prompts by scoring both the prompt text and the generated image

criteria:
  - name: prompt_specificity
    description: "Does the prompt clearly and specifically describe the desired image?"
    max_score: 10
    rubric: |
      1-3: Vague description, missing key details about subject, style, or composition
      4-6: Describes the subject but lacks specifics on lighting, perspective, or mood
      7-9: Detailed prompt with clear subject, style, composition, and mood guidance
      10: Exhaustively specific with concrete visual references and technical direction

  - name: prompt_style
    description: "Does the prompt include clear artistic style and aesthetic direction?"
    max_score: 10
    rubric: |
      1-3: No style guidance or contradictory style instructions
      4-6: Names a style but doesn't elaborate on how it should manifest
      7-9: Clear style direction with specific references to techniques or artists
      10: Comprehensive style guide with medium, technique, color palette, and mood

  - name: visual_quality
    description: "Is the generated image sharp, well-composed, and free of artifacts?"
    max_score: 10
    requires_image: true
    rubric: |
      1-3: Blurry, distorted, or contains obvious AI artifacts (extra fingers, melted text)
      4-6: Acceptable quality but has minor issues (slightly soft focus, minor artifacts)
      7-9: Sharp, clean, well-composed image with good lighting and no visible artifacts
      10: Professional quality — could be used in production without editing

  - name: visual_relevance
    description: "Does the generated image accurately depict what the prompt asked for?"
    max_score: 10
    requires_image: true
    rubric: |
      1-3: Image bears little resemblance to the prompt description
      4-6: Captures the general idea but misses key details or adds unwanted elements
      7-9: Accurately depicts the prompt with most details correct
      10: Perfect match — every element described in the prompt is faithfully rendered

  - name: style_match
    description: "Does the image reflect the requested artistic style?"
    max_score: 10
    requires_image: true
    rubric: |
      1-3: Style is completely different from what was requested
      4-6: Some stylistic elements present but inconsistent or weak
      7-9: Clear match to the requested style with appropriate techniques visible
      10: Masterful execution of the requested style — immediately recognizable

scorer_config:
  type: composite
  heuristic_weight: 0.1
  ai_judge_weight: 0.9
```

- [ ] **Step 6: Write test that loads the evaluation config**

In `tests/unit/test_evaluation.py`, add:

```python
from pathlib import Path

from asset_optimizer.core.evaluation import load_evaluation


class TestImageVisualEvaluation:
    def test_load_image_visual_config(self) -> None:
        config = load_evaluation(Path("evaluations/image-visual.yaml"))
        assert config.name == "image-visual"
        assert config.asset_type == "image"
        assert len(config.criteria) == 5
        image_criteria = [c for c in config.criteria if c.requires_image]
        text_criteria = [c for c in config.criteria if not c.requires_image]
        assert len(image_criteria) == 3
        assert len(text_criteria) == 2
```

- [ ] **Step 7: Run test**

Run: `uv run pytest tests/unit/test_evaluation.py::TestImageVisualEvaluation -v`
Expected: PASS

- [ ] **Step 8: Run full test suite**

Run: `uv run pytest tests/ -v`
Expected: All PASS

- [ ] **Step 9: Commit**

```bash
git add src/asset_optimizer/storage/image_storage.py tests/unit/test_image_storage.py evaluations/image-visual.yaml tests/unit/test_evaluation.py
git commit -m "feat: add ImageStorage helper and image-visual evaluation config"
```

---

### Task 7: Add `create_engine()` factory function

**Files:**
- Modify: `src/asset_optimizer/providers/factory.py`
- Test: `tests/unit/test_factory.py`

- [ ] **Step 1: Write failing test for create_engine**

In `tests/unit/test_factory.py`, add:

```python
from asset_optimizer.providers.factory import create_engine


class TestCreateEngine:
    def test_create_engine_text_only(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        engine = create_engine(text_provider="openai")
        assert engine is not None
        assert engine.image_provider is None

    def test_create_engine_with_image_provider(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        engine = create_engine(
            text_provider="openai", image_provider="openai_image"
        )
        assert engine is not None
        assert engine.image_provider is not None

    def test_create_engine_no_image_provider_when_none(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        engine = create_engine(text_provider="openai", image_provider=None)
        assert engine.image_provider is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_factory.py::TestCreateEngine -v`
Expected: FAIL — `ImportError: cannot import name 'create_engine' from 'asset_optimizer.providers.factory'`

- [ ] **Step 3: Implement create_engine in factory.py**

At the end of `src/asset_optimizer/providers/factory.py`, add:

```python
def create_engine(
    text_provider: str | None = None,
    judge_provider: str | None = None,
    image_provider: str | None = None,
    config_path: Path | None = None,
) -> "Engine":
    """Create an Engine with all providers auto-configured from args/config/env."""
    from asset_optimizer.core.engine import Engine

    text = create_text_provider(name=text_provider, config_path=config_path)
    judge = create_judge_provider(name=judge_provider, config_path=config_path)
    image = (
        create_image_provider(name=image_provider, config_path=config_path)
        if image_provider
        else None
    )
    return Engine(provider=text, judge_provider=judge, image_provider=image)
```

Also add `Engine` to the `TYPE_CHECKING` imports at the top:

```python
if TYPE_CHECKING:
    from asset_optimizer.core.engine import Engine
    from asset_optimizer.providers.base import TextProvider
    from asset_optimizer.providers.image_providers.base import ImageProvider
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_factory.py::TestCreateEngine -v`
Expected: All PASS

- [ ] **Step 5: Run full test suite**

Run: `uv run pytest tests/ -v`
Expected: All PASS

- [ ] **Step 6: Commit**

```bash
git add src/asset_optimizer/providers/factory.py tests/unit/test_factory.py
git commit -m "feat: add create_engine() factory function with optional image provider"
```

---

### Task 8: API — image serving endpoint and schema updates

**Files:**
- Modify: `src/asset_optimizer/api/schemas.py`
- Create: `src/asset_optimizer/api/routes/assets.py`
- Modify: `src/asset_optimizer/api/app.py`
- Modify: `src/asset_optimizer/storage/repository.py`
- Test: `tests/unit/test_api.py`

- [ ] **Step 1: Add `get_asset_version` to Repository**

In `src/asset_optimizer/storage/repository.py`, in the `# --- Asset Versions ---` section, add:

```python
    async def get_asset_version(self, asset_version_id: uuid.UUID) -> AssetVersion | None:
        return await self._session.get(AssetVersion, asset_version_id)
```

- [ ] **Step 2: Write failing test for image serving endpoint**

In `tests/unit/test_api.py`, add:

```python
import os
from pathlib import Path


class TestAssetImageRoutes:
    @pytest.mark.asyncio
    async def test_get_image_not_found(self, client: AsyncClient) -> None:
        resp = await client.get(f"/api/v1/assets/{uuid.uuid4()}/image")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_image_serves_file(self, client: AsyncClient, tmp_path: Path) -> None:
        # Create an evaluation + experiment + iteration + asset version with a file
        eval_resp = await client.post("/api/v1/evaluations", json={
            "name": "img-eval", "asset_type": "image",
            "criteria": [{"name": "c1", "description": "d1"}],
        })
        eval_id = eval_resp.json()["id"]
        exp_resp = await client.post("/api/v1/experiments", json={
            "name": "img-exp", "asset_type": "image",
            "evaluation_id": eval_id,
        })

        # Write a fake image file
        image_path = tmp_path / "test_image.png"
        image_path.write_bytes(b"\x89PNG\r\n\x1a\nfake-image-data")

        # Create asset version directly via the repository
        from asset_optimizer.api.deps import get_repository
        from asset_optimizer.storage.models import AssetVersion, AssetVersionRole, Iteration, IterationStatus

        app = client._transport.app  # type: ignore[attr-defined]
        session_factory = app.state.session_factory
        async with session_factory() as session:
            from asset_optimizer.storage.repository import Repository
            repo = Repository(session)

            iteration = Iteration(
                experiment_id=uuid.UUID(exp_resp.json()["id"]),
                number=1,
                status=IterationStatus.IMPROVED,
            )
            iteration = await repo.create_iteration(iteration)

            asset_version = AssetVersion(
                iteration_id=iteration.id,
                role=AssetVersionRole.OUTPUT,
                file_path=str(image_path),
                metadata_={"image_format": "png"},
            )
            asset_version = await repo.create_asset_version(asset_version)
            av_id = str(asset_version.id)

        resp = await client.get(f"/api/v1/assets/{av_id}/image")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/png"
        assert b"fake-image-data" in resp.content
```

- [ ] **Step 3: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_api.py::TestAssetImageRoutes -v`
Expected: FAIL — 404 (route doesn't exist yet)

- [ ] **Step 4: Create the assets route**

Create `src/asset_optimizer/api/routes/assets.py`:

```python
"""Asset image serving routes."""

import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from asset_optimizer.api.deps import get_repository
from asset_optimizer.storage.repository import Repository

router = APIRouter(prefix="/api/v1/assets", tags=["assets"])

RepoDep = Annotated[Repository, Depends(get_repository)]


@router.get("/{asset_version_id}/image")
async def get_asset_image(
    asset_version_id: uuid.UUID,
    repo: RepoDep,
) -> FileResponse:
    """Serve the image file for an asset version."""
    asset_version = await repo.get_asset_version(asset_version_id)
    if asset_version is None or not asset_version.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset image not found",
        )

    file_path = Path(asset_version.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found on disk",
        )

    image_format = asset_version.metadata_.get("image_format", "png")
    media_type = f"image/{image_format}"

    return FileResponse(path=file_path, media_type=media_type)
```

- [ ] **Step 5: Register the assets router in app.py**

In `src/asset_optimizer/api/app.py`, add the import and include:

```python
from asset_optimizer.api.routes import assets, evaluations, experiments, health, providers
```

And in the `create_app` function, after the existing router includes:

```python
    app.include_router(assets.router)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_api.py::TestAssetImageRoutes -v`
Expected: All PASS

- [ ] **Step 7: Run full test suite**

Run: `uv run pytest tests/ -v`
Expected: All PASS

- [ ] **Step 8: Commit**

```bash
git add src/asset_optimizer/api/routes/assets.py src/asset_optimizer/api/app.py src/asset_optimizer/storage/repository.py src/asset_optimizer/api/schemas.py tests/unit/test_api.py
git commit -m "feat: add image serving endpoint GET /api/v1/assets/{id}/image"
```

---

### Task 9: UI — API client updates and ExperimentDetail image viewer

**Files:**
- Modify: `ui/src/api/client.ts`
- Modify: `ui/src/pages/ExperimentDetail.tsx`

- [ ] **Step 1: Update API client types and add image URL helper**

In `ui/src/api/client.ts`, update the `Experiment` interface and add an `assets` namespace:

```typescript
const BASE_URL = '/api/v1'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!resp.ok) {
    throw new Error(`API error: ${resp.status} ${resp.statusText}`)
  }
  if (resp.status === 204) return undefined as T
  return resp.json()
}

export interface Evaluation {
  id: string
  name: string
  asset_type: string
  description: string
  criteria: Array<{ name: string; description: string; max_score: number; requires_image?: boolean }>
  scorer_config: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface IterationSummary {
  iteration: number
  score: number
  accepted: boolean
  has_image: boolean
  image_asset_version_id: string | null
  image_cost: number | null
}

export interface Experiment {
  id: string
  name: string
  description: string | null
  asset_type: string
  evaluation_id: string
  status: string
  config: Record<string, unknown>
  best_score: number | null
  best_image_asset_version_id: string | null
  total_cost: number | null
  created_at: string
  updated_at: string
}

export const api = {
  health: () => request<{ status: string; version: string }>('/health'),

  evaluations: {
    list: () => request<Evaluation[]>('/evaluations'),
    get: (id: string) => request<Evaluation>(`/evaluations/${id}`),
    create: (data: Partial<Evaluation>) => request<Evaluation>('/evaluations', { method: 'POST', body: JSON.stringify(data) }),
    delete: (id: string) => request<void>(`/evaluations/${id}`, { method: 'DELETE' }),
  },

  experiments: {
    list: () => request<Experiment[]>('/experiments'),
    get: (id: string) => request<Experiment>(`/experiments/${id}`),
    create: (data: Partial<Experiment>) => request<Experiment>('/experiments', { method: 'POST', body: JSON.stringify(data) }),
    delete: (id: string) => request<void>(`/experiments/${id}`, { method: 'DELETE' }),
  },

  providers: {
    list: () => request<{ text: string[]; image: string[] }>('/providers'),
  },

  assets: {
    getImageUrl: (assetVersionId: string) => `${BASE_URL}/assets/${assetVersionId}/image`,
  },
}
```

- [ ] **Step 2: Update ExperimentDetail with best image panel and cost summary**

Replace `ui/src/pages/ExperimentDetail.tsx`:

```tsx
import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { StatusBadge } from '../components/StatusBadge'
import { ScoreChart } from '../components/ScoreChart'

export function ExperimentDetail() {
  const { id } = useParams<{ id: string }>()
  const { data: experiment, isLoading } = useQuery({
    queryKey: ['experiment', id],
    queryFn: () => api.experiments.get(id!),
    enabled: !!id,
  })

  const [expandedIteration, setExpandedIteration] = useState<string | null>(null)

  if (isLoading) return <p>Loading...</p>
  if (!experiment) return <p>Experiment not found.</p>

  const hasImage = !!experiment.best_image_asset_version_id

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <h1 className="text-2xl font-bold text-gray-900">{experiment.name}</h1>
        <StatusBadge status={experiment.status} />
      </div>
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Asset Type</div>
          <div className="font-semibold">{experiment.asset_type}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Best Score</div>
          <div className="text-xl font-bold">{experiment.best_score !== null ? experiment.best_score.toFixed(2) : '—'}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Max Iterations</div>
          <div className="font-semibold">{(experiment.config as Record<string, unknown>)?.max_iterations as number || '—'}</div>
        </div>
        {experiment.total_cost !== null && experiment.total_cost !== undefined ? (
          <div className="bg-white rounded-lg border p-4">
            <div className="text-sm text-gray-500">Total Cost</div>
            <div className="font-semibold">${experiment.total_cost.toFixed(4)}</div>
          </div>
        ) : (
          <div className="bg-white rounded-lg border p-4">
            <div className="text-sm text-gray-500">Created</div>
            <div className="font-semibold">{new Date(experiment.created_at).toLocaleDateString()}</div>
          </div>
        )}
      </div>

      {hasImage && (
        <div className="bg-white rounded-lg border p-4">
          <h2 className="font-semibold mb-4">Best Generated Image</h2>
          <img
            src={api.assets.getImageUrl(experiment.best_image_asset_version_id!)}
            alt="Best generated image"
            className="max-w-lg rounded-lg border"
            loading="lazy"
          />
        </div>
      )}

      <div className="bg-white rounded-lg border p-4">
        <h2 className="font-semibold mb-4">Score Progression</h2>
        <ScoreChart data={[]} />
      </div>

      {experiment.description && (
        <div className="bg-white rounded-lg border p-4">
          <h2 className="font-semibold mb-2">Description</h2>
          <p className="text-gray-600">{experiment.description}</p>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 3: Verify the UI builds**

Run: `cd ui && npm run build`
Expected: Build succeeds without errors

- [ ] **Step 4: Commit**

```bash
git add ui/src/api/client.ts ui/src/pages/ExperimentDetail.tsx
git commit -m "feat: UI shows best generated image and cost summary on experiment detail"
```

---

### Task 10: Lint, type check, and final verification

**Files:** All modified files

- [ ] **Step 1: Run ruff linter**

Run: `uv run ruff check src/ tests/`
Expected: No errors. If there are errors, fix them.

- [ ] **Step 2: Run ruff formatter check**

Run: `uv run ruff format --check src/ tests/`
Expected: No formatting issues. If there are, run `uv run ruff format src/ tests/` to fix.

- [ ] **Step 3: Run mypy type checker**

Run: `uv run mypy src/asset_optimizer/`
Expected: No errors. Fix any type errors found.

- [ ] **Step 4: Run full test suite with coverage**

Run: `uv run pytest --cov=asset_optimizer --cov-report=term-missing tests/`
Expected: All tests pass.

- [ ] **Step 5: Fix any issues found in steps 1-4**

Address lint, type, or test issues. Re-run the failing check after each fix.

- [ ] **Step 6: Commit any fixes**

```bash
git add -A
git commit -m "fix: resolve lint, type, and test issues from final verification"
```
