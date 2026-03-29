"""Convergence strategies for the optimization engine."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ConvergenceResult:
    """Result of a convergence check."""

    should_continue: bool
    reason: str = ""


class ConvergenceStrategy(ABC):
    """Abstract base class for convergence strategies."""

    @abstractmethod
    def check(
        self,
        iteration: int,
        current_score: float,
        previous_score: float,
        max_iterations: int,
    ) -> ConvergenceResult:
        """Check whether optimization should continue.

        Args:
            iteration: The current iteration number (1-based).
            current_score: The score achieved in the current iteration.
            previous_score: The score from the previous iteration.
            max_iterations: The maximum number of iterations allowed.

        Returns:
            A :class:`ConvergenceResult` indicating whether to continue.
        """
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset any internal state so the strategy can be reused."""
        ...


class GreedyStrategy(ConvergenceStrategy):
    """Stops when there is no meaningful improvement for several consecutive iterations.

    Args:
        stagnation_limit: Consecutive non-improving iterations before stopping.
        min_improvement: Minimum score delta to count as an improvement.
    """

    def __init__(
        self,
        stagnation_limit: int = 3,
        min_improvement: float = 0.01,
    ) -> None:
        self.stagnation_limit = stagnation_limit
        self.min_improvement = min_improvement
        self._stagnation_count: int = 0

    def check(
        self,
        iteration: int,
        current_score: float,
        previous_score: float,
        max_iterations: int,
    ) -> ConvergenceResult:
        if iteration >= max_iterations:
            return ConvergenceResult(
                should_continue=False,
                reason="reached max iterations",
            )

        improvement = current_score - previous_score
        if improvement >= self.min_improvement:
            self._stagnation_count = 0
        else:
            self._stagnation_count += 1

        if self._stagnation_count >= self.stagnation_limit:
            return ConvergenceResult(
                should_continue=False,
                reason=(
                    f"stagnation detected: no improvement for "
                    f"{self._stagnation_count} consecutive iterations"
                ),
            )

        return ConvergenceResult(should_continue=True, reason="continuing")

    def reset(self) -> None:
        self._stagnation_count = 0


class TargetStrategy(ConvergenceStrategy):
    """Stops as soon as the score meets or exceeds a target.

    Args:
        target_score: The score threshold at which optimization is considered complete.
    """

    def __init__(self, target_score: float) -> None:
        self.target_score = target_score

    def check(
        self,
        iteration: int,
        current_score: float,
        previous_score: float,
        max_iterations: int,
    ) -> ConvergenceResult:
        if iteration >= max_iterations:
            return ConvergenceResult(
                should_continue=False,
                reason="reached max iterations",
            )

        if current_score >= self.target_score:
            return ConvergenceResult(
                should_continue=False,
                reason=(
                    f"target score {self.target_score} reached "
                    f"with score {current_score:.4f}"
                ),
            )

        return ConvergenceResult(should_continue=True, reason="below target score")

    def reset(self) -> None:
        pass


class BudgetStrategy(ConvergenceStrategy):
    """Runs for the full iteration budget regardless of score changes."""

    def check(
        self,
        iteration: int,
        current_score: float,
        previous_score: float,
        max_iterations: int,
    ) -> ConvergenceResult:
        if iteration >= max_iterations:
            return ConvergenceResult(should_continue=False, reason="budget exhausted")

        return ConvergenceResult(should_continue=True, reason="within budget")

    def reset(self) -> None:
        pass


def create_strategy(name: str, **kwargs: object) -> ConvergenceStrategy:
    """Factory function that returns a convergence strategy by name.

    Args:
        name: One of ``"greedy"``, ``"target"``, or ``"budget"``.
        **kwargs: Keyword arguments forwarded to the strategy constructor.

    Returns:
        An instantiated :class:`ConvergenceStrategy`.

    Raises:
        ValueError: If *name* is not recognised.
    """
    strategies: dict[str, type[ConvergenceStrategy]] = {
        "greedy": GreedyStrategy,
        "target": TargetStrategy,
        "budget": BudgetStrategy,
    }
    if name not in strategies:
        raise ValueError(
            f"Unknown convergence strategy '{name}'. "
            f"Choose from: {list(strategies)}"
        )
    return strategies[name](**kwargs)
