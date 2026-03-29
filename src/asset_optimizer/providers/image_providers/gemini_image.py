"""Gemini image generation provider using Google's generative AI API."""

from __future__ import annotations

from typing import Any

import google.generativeai as genai  # type: ignore[import-untyped]

from asset_optimizer.providers.base import ImageResult
from asset_optimizer.providers.image_providers.base import ImageProvider


class GeminiImageProvider(ImageProvider):
    """Image generation using Gemini's native image generation capability."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash-preview-image-generation",
    ) -> None:
        genai.configure(api_key=api_key)  # type: ignore[attr-defined]
        self._model_name = model

    async def generate(self, prompt: str, **kwargs: Any) -> ImageResult:
        """Generate an image using Gemini's image generation model."""
        model = genai.GenerativeModel(self._model_name)  # type: ignore[attr-defined]
        response = await model.generate_content_async(  # type: ignore[attr-defined]
            prompt,
            generation_config=genai.types.GenerationConfig(  # type: ignore[attr-defined]
                response_modalities=["TEXT", "IMAGE"],
            ),
        )

        # Extract image data from response parts
        image_data = b""
        fmt = "png"
        for part in response.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                image_data = part.inline_data.data
                mime = part.inline_data.mime_type or "image/png"
                fmt = mime.split("/")[-1] if "/" in mime else "png"
                break

        return ImageResult(
            image_data=image_data,
            format=fmt,
            metadata={
                "model": self._model_name,
                "prompt": prompt,
            },
        )
