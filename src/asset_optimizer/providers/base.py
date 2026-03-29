"""Base types and abstract classes for AI text providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Message:
    """A single message in a conversation."""

    role: str
    content: str


@dataclass
class Criterion:
    """A single evaluation criterion for judging content."""

    name: str
    description: str
    max_score: float = 10.0
    rubric: str = ""
    requires_image: bool = False


@dataclass
class JudgmentScore:
    """Score for a single criterion."""

    criterion: str
    score: float
    reasoning: str


@dataclass
class JudgmentResult:
    """Result of judging content against multiple criteria."""

    scores: list[JudgmentScore] = field(default_factory=list)


@dataclass
class ImageResult:
    """Result of image generation."""

    image_data: bytes = field(default_factory=bytes)
    format: str = "png"
    metadata: dict[str, object] = field(default_factory=dict)


class TextProvider(ABC):
    """Abstract base class for text-based AI providers."""

    @abstractmethod
    async def complete(self, messages: list[Message], **kwargs: object) -> str:
        """Generate a text completion from a list of messages."""
        ...

    @abstractmethod
    async def judge(
        self,
        content: str,
        criteria: list[Criterion],
        image: bytes | None = None,
        image_format: str = "png",
    ) -> JudgmentResult:
        """Judge content against a list of criteria and return scores."""
        ...
