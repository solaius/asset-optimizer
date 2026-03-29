"""Evaluation configuration — defines what 'good' looks like for an asset."""

from __future__ import annotations

from typing import TYPE_CHECKING

import yaml
from pydantic import BaseModel

if TYPE_CHECKING:
    from pathlib import Path


class CriterionConfig(BaseModel):
    """A single evaluation criterion."""

    name: str
    description: str
    max_score: float = 10.0
    rubric: str = ""


class ScorerConfig(BaseModel):
    """Configuration for how scoring is performed."""

    type: str = "composite"
    judge_provider: str | None = None
    heuristic_weight: float = 0.2
    ai_judge_weight: float = 0.8


class EvaluationConfig(BaseModel):
    """Complete evaluation configuration."""

    name: str
    asset_type: str
    description: str = ""
    criteria: list[CriterionConfig]
    scorer_config: ScorerConfig = ScorerConfig()


def load_evaluation(path: Path) -> EvaluationConfig:
    """Load an evaluation configuration from a YAML file."""
    if not path.exists():
        raise FileNotFoundError(f"Evaluation file not found: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    config = EvaluationConfig(**raw)

    if not config.criteria:
        raise ValueError(f"Evaluation '{config.name}' must have at least one criterion")

    return config
