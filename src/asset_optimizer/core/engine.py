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
    provider knows exactly what to fix.  When a weak score comes from a
    ``requires_image=True`` criterion and has reasoning in its details, a
    "VISUAL FEEDBACK FROM THE JUDGE" section is appended so the text provider
    can refine the prompt to address visual shortcomings.
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
            # Collect visual feedback from image-requiring criteria
            if crit.requires_image:
                reasoning = score_result.details.get("reasoning")
                if reasoning:
                    visual_feedback_parts.append(
                        f"- {crit.name}: {reasoning}"
                    )

    focus_block = "\n".join(focus_parts)

    prompt = (
        "You are an expert content optimizer. Improve the following content by "
        "addressing the weakest scoring criteria listed below. Return ONLY the "
        "improved content without any explanation or commentary.\n\n"
        f"CURRENT CONTENT:\n{content}\n\n"
        f"CRITERIA TO IMPROVE:\n{focus_block}\n\n"
    )

    if visual_feedback_parts:
        visual_block = "\n".join(visual_feedback_parts)
        prompt += (
            f"VISUAL FEEDBACK FROM THE JUDGE:\n{visual_block}\n\n"
        )

    prompt += "Provide the improved content now:"

    return prompt


async def _generate_image_with_retry(
    image_provider: ImageProvider,
    content: str,
) -> tuple[bytes, str] | None:
    """Try to generate an image up to 2 times.

    Returns ``(image_data, format)`` on success or ``None`` on persistent
    failure.
    """
    for attempt in range(2):
        try:
            result = await image_provider.generate(content)
            return (result.image_data, result.format)
        except Exception:
            if attempt == 0:
                logger.warning(
                    "Image generation failed (attempt 1/2), retrying..."
                )
            else:
                logger.error("Image generation failed after 2 attempts")
    return None


class Engine:
    """Core optimization engine implementing the autoimprove loop.

    Args:
        provider: The :class:`~asset_optimizer.providers.base.TextProvider` used to
            generate improved content.
        judge_provider: An optional separate provider used for scoring. Falls back to
            *provider* when not supplied.
        image_provider: An optional image generation provider. When supplied,
            the engine generates images each iteration and includes them in
            multimodal scoring.
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
        """Run the optimization loop and return the best content found.

        Args:
            content: The initial asset content to improve.
            evaluation: Configuration describing what "good" looks like.
            max_iterations: Hard cap on the number of iterations.
            target_score: When using the ``"target"`` strategy, stop once this
                aggregate score is reached.
            convergence_strategy: One of ``"greedy"``, ``"target"``, or
                ``"budget"``.
            stagnation_limit: For the ``"greedy"`` strategy — consecutive
                non-improving iterations before stopping.
            min_improvement: For the ``"greedy"`` strategy — minimum score
                delta to count as an improvement.
            on_iteration: Optional callback invoked after each iteration with a
                dict containing ``"iteration"``, ``"score"``, ``"content"``,
                and ``"accepted"`` keys.

        Returns:
            An :class:`OptimizationResult` with the best content and metadata.
        """
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

        # Early-stop / cost tracking state
        stopped_early = False
        stop_reason = ""
        total_cost: float = 0.0

        # Image state
        best_image: bytes | None = None
        best_image_format: str = ""
        current_image: bytes | None = None
        current_image_format: str = ""

        # If we have an image provider, log a cost warning and generate the
        # baseline image.
        if self.image_provider is not None:
            estimated_cost = max_iterations * 0.04  # rough per-image estimate
            if estimated_cost > 2.0:
                logger.warning(
                    "Estimated image generation cost ($%.2f) exceeds $2. "
                    "Consider reducing max_iterations.",
                    estimated_cost,
                )

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
                    total_cost=total_cost,
                )
            current_image, current_image_format = gen_result
            best_image = current_image
            best_image_format = current_image_format

        # Score baseline
        baseline_scores = await scorer.score(
            content,
            image=current_image,
            image_format=current_image_format or "png",
        )
        baseline_score = _compute_aggregate_score(baseline_scores)

        # Accumulate costs from baseline scoring
        for s in baseline_scores:
            if s.cost is not None:
                total_cost += s.cost

        best_content = content
        best_score = baseline_score
        previous_score = baseline_score
        current_scores: list[ScoreResult] = baseline_scores
        iterations: list[IterationResult] = []

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

            # Generate image for the new content if image_provider is set
            iter_image: bytes | None = None
            iter_image_format: str = ""
            iter_image_cost: float | None = 0.0 if self.image_provider is not None else None

            if self.image_provider is not None:
                gen_result = await _generate_image_with_retry(
                    self.image_provider, new_content
                )
                if gen_result is None:
                    stopped_early = True
                    stop_reason = "Image generation failed during optimization"

                    duration_ms = (time.monotonic() - t_start) * 1000.0
                    iter_result = IterationResult(
                        iteration=iteration,
                        input_content=content if iteration == 1 else best_content,
                        output_content=new_content,
                        input_score=previous_score,
                        output_score=previous_score,
                        scores=[],
                        improvement_prompt=improvement_prompt,
                        accepted=False,
                        duration_ms=duration_ms,
                    )
                    iterations.append(iter_result)
                    break

                iter_image, iter_image_format = gen_result

            new_scores = await scorer.score(
                new_content,
                image=iter_image,
                image_format=iter_image_format or "png",
            )
            new_score = _compute_aggregate_score(new_scores)

            # Accumulate costs from scoring
            for s in new_scores:
                if s.cost is not None:
                    total_cost += s.cost

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
                image_cost=iter_image_cost,
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
            total_cost=(
                total_cost
                if total_cost > 0.0 or self.image_provider is not None
                else None
            ),
            stopped_early=stopped_early,
            stop_reason=stop_reason,
        )
