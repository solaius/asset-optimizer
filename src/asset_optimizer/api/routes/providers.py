"""Provider listing routes."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/providers", tags=["providers"])


class ProviderInfo(BaseModel):
    name: str
    type: str
    description: str


class ProvidersResponse(BaseModel):
    text: list[ProviderInfo]
    image: list[ProviderInfo]


_TEXT_PROVIDERS: list[ProviderInfo] = [
    ProviderInfo(name="openai", type="text", description="OpenAI GPT models"),
    ProviderInfo(
        name="anthropic", type="text", description="Anthropic Claude models"
    ),
    ProviderInfo(
        name="gemini", type="text", description="Google Gemini models"
    ),
    ProviderInfo(
        name="openai_compat",
        type="text",
        description="OpenAI-compatible API endpoint",
    ),
]

_IMAGE_PROVIDERS: list[ProviderInfo] = [
    ProviderInfo(
        name="openai_image",
        type="image",
        description="OpenAI DALL-E image generation",
    ),
    ProviderInfo(
        name="nano_banana",
        type="image",
        description="Nano Banana image generation",
    ),
]


@router.get("", response_model=ProvidersResponse)
async def list_providers() -> ProvidersResponse:
    """Return all available text and image providers."""
    return ProvidersResponse(text=_TEXT_PROVIDERS, image=_IMAGE_PROVIDERS)
