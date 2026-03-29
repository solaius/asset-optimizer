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
        scored. Image-requiring criteria are skipped entirely (not scored as 0).
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
