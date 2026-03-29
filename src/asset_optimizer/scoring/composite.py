"""Composite scorer that combines multiple scorers with weights."""

from typing import Any

from asset_optimizer.scoring.base import Scorer, ScoreResult


class CompositeScorer:
    """Combines multiple scorers using weighted averaging.

    Each entry in ``scorers`` is a dict with keys:
      - ``scorer``: a :class:`~asset_optimizer.scoring.base.Scorer` instance
      - ``weight``: a float weight (need not sum to 1; will be normalised)
      - ``criterion``: a human-readable label for the criterion
    """

    def __init__(self, scorers: list[dict[str, Any]]) -> None:
        self.scorers = scorers

    def score_all(self, content: str) -> list[ScoreResult]:
        """Run every scorer against *content* and return results in order."""
        results: list[ScoreResult] = []
        for entry in self.scorers:
            scorer: Scorer = entry["scorer"]
            criterion: str = entry["criterion"]
            result = scorer.score(content)
            # Override the criterion label with the composite-level label
            result.criterion = criterion
            results.append(result)
        return results

    def composite_score(self, results: list[ScoreResult]) -> float:
        """Return the weighted average score (0-10) for the given results.

        Weights are taken from ``self.scorers`` in the same order as *results*.
        If total weight is zero, returns 0.0.
        """
        if not results:
            return 0.0

        total_weight: float = sum(
            float(entry["weight"]) for entry in self.scorers[: len(results)]
        )
        if total_weight == 0.0:
            return 0.0

        weighted_sum: float = sum(
            result.value * float(self.scorers[i]["weight"])
            for i, result in enumerate(results)
        )
        raw = weighted_sum / total_weight
        # Normalise to 0-10 (values are already on a 0-10 scale; clamp for safety)
        return max(0.0, min(10.0, raw))
