"""Optimization engine — the core autoimprove loop."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from asset_optimizer.core.convergence import ConvergenceStrategy, create_strategy
from asset_optimizer.providers.base import Criterion, Message, TextProvider
from asset_optimizer.scoring.ai_judge import AIJudgeScorer

if TYPE_CHECKING:
    from collections.abc import Callable

    from asset_optimizer.core.evaluation import CriterionConfig, EvaluationConfig
    from asset_optimizer.scoring.base import ScoreResult


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


@dataclass
class OptimizationResult:
    """Final result of the optimization run."""

    best_content: str
    best_score: float
    initial_score: float
    total_iterations: int
    iterations: list[IterationResult] = field(default_factory=list)


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
    provider knows exactly what to fix.
    """
    # Sort by ascending score to find weakest criteria
    sorted_scores = sorted(scores, key=lambda s: s.value)
    weakest = sorted_scores[:2]

    # Build criterion detail strings with rubric if available
    criterion_map = {c.name: c for c in criteria}
    focus_parts: list[str] = []
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

    focus_block = "\n".join(focus_parts)

    return (
        "You are an expert content optimizer. Improve the following content by "
        "addressing the weakest scoring criteria listed below. Return ONLY the "
        "improved content without any explanation or commentary.\n\n"
        f"CURRENT CONTENT:\n{content}\n\n"
        f"CRITERIA TO IMPROVE:\n{focus_block}\n\n"
        "Provide the improved content now:"
    )


class Engine:
    """Core optimization engine implementing the autoimprove loop.

    Args:
        provider: The :class:`~asset_optimizer.providers.base.TextProvider` used to
            generate improved content.
        judge_provider: An optional separate provider used for scoring. Falls back to
            *provider* when not supplied.
    """

    def __init__(
        self,
        provider: TextProvider,
        judge_provider: TextProvider | None = None,
    ) -> None:
        self.provider = provider
        self.judge_provider: TextProvider = (
            judge_provider if judge_provider is not None else provider
        )

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
            )
            for c in evaluation.criteria
        ]

        scorer = AIJudgeScorer(provider=self.judge_provider, criteria=criteria)

        # Score baseline
        baseline_scores = await scorer.score(content)
        baseline_score = _compute_aggregate_score(baseline_scores)

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

            new_scores = await scorer.score(new_content)
            new_score = _compute_aggregate_score(new_scores)

            accepted = new_score >= previous_score
            if accepted:
                best_content = new_content
                best_score = new_score
                current_scores = new_scores

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
            total_iterations=iteration,
            iterations=iterations,
        )
