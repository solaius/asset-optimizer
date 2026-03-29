"""Base types and abstract classes for scorers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ScoreResult:
    """Result of scoring content against a single criterion."""

    criterion: str
    value: float
    max_value: float = 10.0
    scorer_type: str = "heuristic"
    details: dict[str, object] = field(default_factory=dict)


class Scorer(ABC):
    """Abstract base class for content scorers."""

    @abstractmethod
    def score(self, content: str) -> ScoreResult:
        """Score the given content and return a ScoreResult."""
        ...
