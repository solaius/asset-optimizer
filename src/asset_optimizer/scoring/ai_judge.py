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

    async def score(self, content: str) -> list[ScoreResult]:
        """Judge content against all criteria and return a ScoreResult per criterion."""
        judgment = await self.provider.judge(content, self.criteria)

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

        # Ensure every criterion has a result; fill zero for any unscored ones
        results: list[ScoreResult] = []
        for criterion in self.criteria:
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
