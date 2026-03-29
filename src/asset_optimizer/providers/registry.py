"""Provider registry for managing text and image providers."""

from asset_optimizer.providers.base import TextProvider
from asset_optimizer.providers.image_providers.base import ImageProvider


class ProviderRegistry:
    """Registry for managing and retrieving AI providers."""

    def __init__(self) -> None:
        self._text_providers: dict[str, TextProvider] = {}
        self._image_providers: dict[str, ImageProvider] = {}
        self._default_text: str | None = None
        self._default_image: str | None = None

    # --- Text providers ---

    def register_text(self, name: str, provider: TextProvider) -> None:
        """Register a text provider under the given name."""
        self._text_providers[name] = provider

    def get_text(self, name: str) -> TextProvider | None:
        """Return the text provider registered under name, or None."""
        return self._text_providers.get(name)

    def list_text(self) -> list[str]:
        """Return a list of registered text provider names."""
        return list(self._text_providers.keys())

    def set_default_text(self, name: str) -> None:
        """Set the default text provider by name (must already be registered)."""
        if name not in self._text_providers:
            raise KeyError(f"Text provider '{name}' is not registered")
        self._default_text = name

    def get_default_text(self) -> TextProvider | None:
        """Return the default text provider, or None if not set."""
        if self._default_text is None:
            return None
        return self._text_providers.get(self._default_text)

    # --- Image providers ---

    def register_image(self, name: str, provider: ImageProvider) -> None:
        """Register an image provider under the given name."""
        self._image_providers[name] = provider

    def get_image(self, name: str) -> ImageProvider | None:
        """Return the image provider registered under name, or None."""
        return self._image_providers.get(name)

    def list_image(self) -> list[str]:
        """Return a list of registered image provider names."""
        return list(self._image_providers.keys())

    def set_default_image(self, name: str) -> None:
        """Set the default image provider by name (must already be registered)."""
        if name not in self._image_providers:
            raise KeyError(f"Image provider '{name}' is not registered")
        self._default_image = name

    def get_default_image(self) -> ImageProvider | None:
        """Return the default image provider, or None if not set."""
        if self._default_image is None:
            return None
        return self._image_providers.get(self._default_image)
