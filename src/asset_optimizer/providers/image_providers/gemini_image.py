"""Gemini image generation provider using the google-genai SDK."""

from __future__ import annotations

from typing import Any

from google import genai  # type: ignore[import-untyped]
from google.genai import types  # type: ignore[import-untyped]

from asset_optimizer.providers.base import ImageResult
from asset_optimizer.providers.image_providers.base import ImageProvider


class GeminiImageProvider(ImageProvider):
    """Image generation using Gemini's native image generation capability.

    Uses the google-genai SDK (not the deprecated google-generativeai).
    Supports models like gemini-2.0-flash-preview-image-generation
    and gemini-2.5-flash-preview.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash-preview-image-generation",
    ) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model_name = model

    async def generate(self, prompt: str, **kwargs: Any) -> ImageResult:
        """Generate an image using Gemini's image generation model."""
        response = self._client.models.generate_content(
            model=self._model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
            ),
        )

        # Extract image data from response parts
        image_data = b""
        fmt = "png"

        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    image_data = part.inline_data.data  # type: ignore[assignment]
                    mime = part.inline_data.mime_type or "image/png"
                    fmt = mime.split("/")[-1] if "/" in mime else "png"
                    break

        if not image_data:
            msg = "Gemini returned no image data"
            raise RuntimeError(msg)

        return ImageResult(
            image_data=image_data,
            format=fmt,
            metadata={
                "model": self._model_name,
                "prompt": prompt,
            },
        )
