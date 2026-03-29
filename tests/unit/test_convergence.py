"""Tests for convergence strategies."""

from asset_optimizer.core.convergence import (
    BudgetStrategy,
    ConvergenceResult,
    GreedyStrategy,
    TargetStrategy,
)


class TestGreedyStrategy:
    def test_should_continue_with_improvement(self) -> None:
        strategy = GreedyStrategy(stagnation_limit=3)
        result = strategy.check(iteration=1, current_score=5.0, previous_score=3.0, max_iterations=20)
        assert result.should_continue is True

    def test_should_stop_after_stagnation(self) -> None:
        strategy = GreedyStrategy(stagnation_limit=2)
        strategy.check(iteration=1, current_score=5.0, previous_score=5.0, max_iterations=20)
        result = strategy.check(iteration=2, current_score=5.0, previous_score=5.0, max_iterations=20)
        assert result.should_continue is False
        assert "stagnation" in result.reason.lower()

    def test_should_stop_at_max_iterations(self) -> None:
        strategy = GreedyStrategy(stagnation_limit=10)
        result = strategy.check(iteration=20, current_score=5.0, previous_score=4.0, max_iterations=20)
        assert result.should_continue is False

    def test_resets_stagnation_on_improvement(self) -> None:
        strategy = GreedyStrategy(stagnation_limit=2)
        strategy.check(iteration=1, current_score=5.0, previous_score=5.0, max_iterations=20)
        strategy.check(iteration=2, current_score=6.0, previous_score=5.0, max_iterations=20)
        result = strategy.check(iteration=3, current_score=6.0, previous_score=6.0, max_iterations=20)
        assert result.should_continue is True


class TestTargetStrategy:
    def test_should_stop_when_target_reached(self) -> None:
        strategy = TargetStrategy(target_score=8.0)
        result = strategy.check(iteration=1, current_score=8.5, previous_score=0.0, max_iterations=20)
        assert result.should_continue is False
        assert "target" in result.reason.lower()

    def test_should_continue_below_target(self) -> None:
        strategy = TargetStrategy(target_score=8.0)
        result = strategy.check(iteration=1, current_score=6.0, previous_score=4.0, max_iterations=20)
        assert result.should_continue is True


class TestBudgetStrategy:
    def test_runs_exact_iterations(self) -> None:
        strategy = BudgetStrategy()
        result = strategy.check(iteration=5, current_score=5.0, previous_score=4.0, max_iterations=10)
        assert result.should_continue is True

    def test_stops_at_max(self) -> None:
        strategy = BudgetStrategy()
        result = strategy.check(iteration=10, current_score=5.0, previous_score=4.0, max_iterations=10)
        assert result.should_continue is False
