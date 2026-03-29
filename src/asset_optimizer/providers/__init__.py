"""AI provider abstractions, implementations, and registry."""

from asset_optimizer.providers.anthropic_provider import AnthropicProvider
from asset_optimizer.providers.base import (
    Criterion,
    ImageResult,
    JudgmentResult,
    JudgmentScore,
    Message,
    TextProvider,
)
from asset_optimizer.providers.gemini_provider import GeminiProvider
from asset_optimizer.providers.image_providers import (
    ImageProvider,
    NanoBananaProvider,
    OpenAIImageProvider,
)
from asset_optimizer.providers.openai_compat import OpenAICompatProvider
from asset_optimizer.providers.openai_provider import OpenAITextProvider
from asset_optimizer.providers.registry import ProviderRegistry

__all__ = [
    # Base types
    "Message",
    "Criterion",
    "JudgmentScore",
    "JudgmentResult",
    "ImageResult",
    # Abstract bases
    "TextProvider",
    "ImageProvider",
    # Text providers
    "OpenAITextProvider",
    "AnthropicProvider",
    "OpenAICompatProvider",
    "GeminiProvider",
    # Image providers
    "OpenAIImageProvider",
    "NanoBananaProvider",
    # Registry
    "ProviderRegistry",
]
