"""Asset Optimizer — automatic asset optimization using the autoimprove pattern."""

from asset_optimizer.core.engine import Engine, OptimizationResult
from asset_optimizer.core.evaluation import EvaluationConfig, load_evaluation

__all__ = ["Engine", "EvaluationConfig", "OptimizationResult", "load_evaluation"]
__version__ = "0.1.0"
