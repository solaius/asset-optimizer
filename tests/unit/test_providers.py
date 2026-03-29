import pytest

from asset_optimizer.providers.base import (
    Criterion,
    ImageResult,
    JudgmentResult,
    JudgmentScore,
    Message,
    TextProvider,
)
from asset_optimizer.providers.image_providers.base import ImageProvider
from asset_optimizer.providers.registry import ProviderRegistry


class TestMessageTypes:
    def test_message_creation(self) -> None:
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_criterion_creation(self) -> None:
        c = Criterion(
            name="clarity",
            description="Is it clear?",
            max_score=10,
            rubric="1-10 scale",
        )
        assert c.name == "clarity"
        assert c.max_score == 10

    def test_criterion_requires_image_default(self) -> None:
        c = Criterion(name="clarity", description="Is it clear?")
        assert c.requires_image is False

    def test_criterion_requires_image_true(self) -> None:
        c = Criterion(
            name="visual_appeal", description="Does it look good?", requires_image=True
        )
        assert c.requires_image is True

    def test_judgment_result(self) -> None:
        scores = [JudgmentScore(criterion="clarity", score=8.0, reasoning="Very clear")]
        result = JudgmentResult(scores=scores)
        assert result.scores[0].score == 8.0

    def test_image_result(self) -> None:
        result = ImageResult(image_data=b"fake", format="png", metadata={"width": 512})
        assert result.format == "png"
        assert result.metadata["width"] == 512


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


class FakeImageProvider(ImageProvider):
    async def generate(self, prompt: str, **kwargs: object) -> ImageResult:
        return ImageResult(image_data=b"fake-image", format="png")


class TestProviderProtocols:
    @pytest.mark.asyncio
    async def test_text_provider_complete(self) -> None:
        provider = FakeTextProvider()
        result = await provider.complete([Message(role="user", content="test")])
        assert result == "fake response"

    @pytest.mark.asyncio
    async def test_text_provider_judge(self) -> None:
        provider = FakeTextProvider()
        criteria = [Criterion(name="clarity", description="test", max_score=10)]
        result = await provider.judge("content", criteria)
        assert len(result.scores) == 1
        assert result.scores[0].score == 5.0

    @pytest.mark.asyncio
    async def test_image_provider_generate(self) -> None:
        provider = FakeImageProvider()
        result = await provider.generate("a cat")
        assert result.format == "png"


class TestProviderRegistry:
    def test_register_and_get_text_provider(self) -> None:
        registry = ProviderRegistry()
        provider = FakeTextProvider()
        registry.register_text("fake", provider)
        assert registry.get_text("fake") is provider

    def test_register_and_get_image_provider(self) -> None:
        registry = ProviderRegistry()
        provider = FakeImageProvider()
        registry.register_image("fake", provider)
        assert registry.get_image("fake") is provider

    def test_get_unknown_returns_none(self) -> None:
        registry = ProviderRegistry()
        assert registry.get_text("unknown") is None
        assert registry.get_image("unknown") is None

    def test_list_providers(self) -> None:
        registry = ProviderRegistry()
        registry.register_text("a", FakeTextProvider())
        registry.register_text("b", FakeTextProvider())
        registry.register_image("c", FakeImageProvider())
        assert set(registry.list_text()) == {"a", "b"}
        assert registry.list_image() == ["c"]

    def test_set_and_get_default(self) -> None:
        registry = ProviderRegistry()
        provider = FakeTextProvider()
        registry.register_text("main", provider)
        registry.set_default_text("main")
        assert registry.get_default_text() is provider


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


class TestAnthropicMultimodalJudge:
    @pytest.mark.asyncio
    async def test_judge_with_image_builds_multimodal_message(self) -> None:
        from unittest.mock import AsyncMock, MagicMock

        from asset_optimizer.providers.anthropic_provider import AnthropicProvider

        provider = AnthropicProvider(
            model="claude-sonnet-4-20250514", api_key="sk-test"
        )

        mock_response = MagicMock()
        mock_block = MagicMock()
        mock_block.text = (
            '{"scores": [{"criterion": "visual_quality",'
            ' "score": 7.0, "reasoning": "good"}]}'
        )
        mock_response.content = [mock_block]

        provider._client.messages.create = AsyncMock(return_value=mock_response)

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

        provider = AnthropicProvider(
            model="claude-3-haiku-20240307", api_key="sk-test",
        )
        criteria = [
            Criterion(
                name="visual_quality",
                description="Sharp?",
                requires_image=True,
            )
        ]
        with pytest.raises(ValueError, match="does not support vision"):
            await provider.judge("test", criteria, image=b"fake")


class TestGeminiMultimodalJudge:
    @pytest.mark.asyncio
    async def test_judge_with_image(self) -> None:
        from unittest.mock import AsyncMock, MagicMock, patch

        from asset_optimizer.providers.gemini_provider import GeminiProvider

        with patch("google.generativeai.configure"), \
             patch("google.generativeai.GenerativeModel"):
            provider = GeminiProvider(model="gemini-2.5-pro", api_key="test-key")

            mock_response = MagicMock()
            mock_response.text = (
                '{"scores": [{"criterion": "visual_quality",'
                ' "score": 8.5, "reasoning": "excellent"}]}'
            )
            provider._generative_model.generate_content_async = (
                AsyncMock(return_value=mock_response)
            )

            criteria = [
                Criterion(
                    name="visual_quality",
                    description="Sharp?",
                    requires_image=True,
                ),
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
            provider = GeminiProvider(
                model="gemini-1.0-pro", api_key="test-key",
            )
            criteria = [
                Criterion(
                    name="visual_quality",
                    description="Sharp?",
                    requires_image=True,
                )
            ]
            with pytest.raises(ValueError, match="does not support vision"):
                await provider.judge("test", criteria, image=b"fake")


class TestOpenAIMultimodalJudge:
    @pytest.mark.asyncio
    async def test_judge_builds_multimodal_message(self) -> None:
        from unittest.mock import AsyncMock, MagicMock

        from asset_optimizer.providers.openai_provider import OpenAITextProvider

        provider = OpenAITextProvider(model="gpt-4o", api_key="sk-test")

        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = (
            '{"scores": [{"criterion": "visual_quality",'
            ' "score": 8.0, "reasoning": "sharp"}]}'
        )
        mock_response.choices = [mock_choice]
        provider._client.chat.completions.create = AsyncMock(  # type: ignore[method-assign]
            return_value=mock_response
        )

        criteria = [
            Criterion(name="visual_quality", description="Sharp?", requires_image=True),
        ]
        result = await provider.judge(
            "a sunset", criteria, image=b"fake-png-bytes", image_format="png"
        )
        assert result.scores[0].score == 8.0
        # Verify multimodal message was sent
        call_kwargs = provider._client.chat.completions.create.call_args
        messages = call_kwargs.kwargs.get("messages") or call_kwargs[1].get("messages")
        assert messages is not None
        assert any(isinstance(m.get("content"), list) for m in messages)

    @pytest.mark.asyncio
    async def test_judge_rejects_non_vision_model(self) -> None:
        from asset_optimizer.providers.openai_provider import OpenAITextProvider

        provider = OpenAITextProvider(model="gpt-3.5-turbo", api_key="sk-test")
        criteria = [
            Criterion(name="visual_quality", description="Sharp?", requires_image=True)
        ]
        with pytest.raises(ValueError, match="does not support vision"):
            await provider.judge("test", criteria, image=b"fake")
