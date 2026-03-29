"""Nano Banana image generation provider."""

from __future__ import annotations

import base64

import httpx

from asset_optimizer.providers.base import ImageResult
from asset_optimizer.providers.image_providers.base import ImageProvider


class NanoBananaProvider(ImageProvider):
    """Image provider backed by the Nano Banana REST API.

    Nano Banana is a fast, low-cost image generation service.  The provider
    POSTs a JSON payload to the configured endpoint and expects either a
    base64-encoded image or binary image data in the response.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        model: str = "default",
        timeout: float = 60.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout,
        )

    async def generate(self, prompt: str, **kwargs: object) -> ImageResult:
        """Generate an image by calling the Nano Banana REST API."""
        payload: dict[str, object] = {
            "prompt": prompt,
            "model": self.model,
            **kwargs,
        }
        response = await self._client.post("/generate", json=payload)
        response.raise_for_status()

        data = response.json()

        # Support both base64-encoded and raw binary responses
        if "image_b64" in data:
            image_bytes = base64.b64decode(data["image_b64"])
        elif "image_data" in data:
            image_bytes = bytes(data["image_data"])
        else:
            # Assume the entire response body is raw image bytes
            image_bytes = response.content

        fmt: str = str(data.get("format", "png"))
        metadata: dict[str, object] = {
            "model": self.model,
            "prompt": prompt,
        }
        if "width" in data:
            metadata["width"] = data["width"]
        if "height" in data:
            metadata["height"] = data["height"]

        return ImageResult(image_data=image_bytes, format=fmt, metadata=metadata)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()
