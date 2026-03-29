"""Asset Optimizer — automatic asset optimization using the autoimprove pattern."""

from asset_optimizer.core.engine import Engine, OptimizationResult
from asset_optimizer.core.evaluation import EvaluationConfig, load_evaluation
from asset_optimizer.providers.factory import (
    create_image_provider,
    create_judge_provider,
    create_text_provider,
)

__all__ = [
    "Engine",
    "EvaluationConfig",
    "OptimizationResult",
    "create_image_provider",
    "create_judge_provider",
    "create_text_provider",
    "load_evaluation",
]
__version__ = "0.1.0"
