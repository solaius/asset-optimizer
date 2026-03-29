"""Abstract base class for image generation providers."""

from abc import ABC, abstractmethod

from asset_optimizer.providers.base import ImageResult


class ImageProvider(ABC):
    """Abstract base class for image generation providers."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: object) -> ImageResult:
        """Generate an image from a text prompt."""
        ...
