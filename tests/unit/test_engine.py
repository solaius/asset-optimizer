"""Tests for the optimization engine."""

from __future__ import annotations

from typing import Any

import pytest

from asset_optimizer.core.engine import Engine, OptimizationResult
from asset_optimizer.core.evaluation import (
    CriterionConfig,
    EvaluationConfig,
    ScorerConfig,
)
from asset_optimizer.providers.base import (
    Criterion,
    ImageResult,
    JudgmentResult,
    JudgmentScore,
    Message,
    TextProvider,
)
from asset_optimizer.providers.image_providers.base import ImageProvider


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


@pytest.fixture
def eval_config() -> EvaluationConfig:
    return EvaluationConfig(
        name="test-eval",
        asset_type="prompt",
        criteria=[
            CriterionConfig(
                name="clarity", description="Is it clear?", max_score=10.0
            ),
            CriterionConfig(
                name="specificity", description="Is it specific?", max_score=10.0
            ),
        ],
        scorer_config=ScorerConfig(
            type="composite", ai_judge_weight=1.0, heuristic_weight=0.0
        ),
    )


class TestEngine:
    @pytest.mark.asyncio
    async def test_optimize_improves_score(self, eval_config: EvaluationConfig) -> None:
        provider = MockProvider()
        engine = Engine(provider=provider, judge_provider=provider)
        result = await engine.optimize(
            content="You are a helpful assistant.",
            evaluation=eval_config,
            max_iterations=3,
        )
        assert isinstance(result, OptimizationResult)
        assert result.total_iterations >= 1
        assert result.best_score > 0.0
        assert result.best_content != "You are a helpful assistant."

    @pytest.mark.asyncio
    async def test_optimize_stops_at_max_iterations(
        self, eval_config: EvaluationConfig
    ) -> None:
        provider = MockProvider()
        engine = Engine(provider=provider, judge_provider=provider)
        result = await engine.optimize(
            content="Short", evaluation=eval_config, max_iterations=2
        )
        assert result.total_iterations <= 2

    @pytest.mark.asyncio
    async def test_optimize_with_target_score(
        self, eval_config: EvaluationConfig
    ) -> None:
        provider = MockProvider()
        engine = Engine(provider=provider, judge_provider=provider)
        result = await engine.optimize(
            content="Short",
            evaluation=eval_config,
            max_iterations=10,
            target_score=3.0,
            convergence_strategy="target",
        )
        assert result.best_score >= 3.0

    @pytest.mark.asyncio
    async def test_optimize_callback(self, eval_config: EvaluationConfig) -> None:
        provider = MockProvider()
        engine = Engine(provider=provider, judge_provider=provider)
        iterations_seen: list[int] = []

        def on_iteration(info: dict[str, Any]) -> None:
            iterations_seen.append(info["iteration"])

        await engine.optimize(
            content="Test",
            evaluation=eval_config,
            max_iterations=2,
            on_iteration=on_iteration,
        )
        assert len(iterations_seen) >= 1

    @pytest.mark.asyncio
    async def test_optimize_with_stagnation(
        self, eval_config: EvaluationConfig
    ) -> None:
        provider = DegradingProvider()
        engine = Engine(provider=provider, judge_provider=provider)
        content = "Already good content that is clear and specific with great detail."
        result = await engine.optimize(
            content=content,
            evaluation=eval_config,
            max_iterations=20,
            stagnation_limit=2,
        )
        assert result.total_iterations < 20


@pytest.fixture
def image_eval_config() -> EvaluationConfig:
    return EvaluationConfig(
        name="test-image-eval",
        asset_type="image",
        criteria=[
            CriterionConfig(
                name="prompt_specificity",
                description="Is the prompt specific?",
            ),
            CriterionConfig(
                name="visual_quality",
                description="Is the image sharp?",
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
        assert result.total_cost is not None
