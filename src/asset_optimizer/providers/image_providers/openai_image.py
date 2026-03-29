"""OpenAI image generation provider."""

from __future__ import annotations

import base64

import openai

from asset_optimizer.providers.base import ImageResult
from asset_optimizer.providers.image_providers.base import ImageProvider


class OpenAIImageProvider(ImageProvider):
    """Image provider backed by OpenAI's image generation API (DALL-E)."""

    def __init__(
        self,
        model: str = "dall-e-3",
        api_key: str | None = None,
        size: str = "1024x1024",
        quality: str = "standard",
    ) -> None:
        self.model = model
        self.size = size
        self.quality = quality
        self._client = openai.AsyncOpenAI(api_key=api_key)

    async def generate(self, prompt: str, **kwargs: object) -> ImageResult:
        """Generate an image from a text prompt using DALL-E.

        Returns the image as raw bytes.  When the API returns a URL the image
        is downloaded; when it returns base64 data it is decoded directly.
        """
        response = await self._client.images.generate(  # type: ignore[call-overload]
            model=self.model,
            prompt=prompt,
            size=self.size,
            quality=self.quality,
            response_format="b64_json",
            **kwargs,
        )

        image_obj = response.data[0]
        b64 = image_obj.b64_json or ""
        image_bytes = base64.b64decode(b64)

        metadata: dict[str, object] = {
            "model": self.model,
            "size": self.size,
            "revised_prompt": image_obj.revised_prompt or prompt,
        }

        return ImageResult(image_data=image_bytes, format="png", metadata=metadata)
