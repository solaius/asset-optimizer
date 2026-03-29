"""Asset type registry for discovering and managing asset types."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

    from asset_optimizer.assets.base import AssetTypeProtocol

T = TypeVar("T")


class AssetRegistry:
    """Registry for asset type implementations."""

    def __init__(self) -> None:
        self._types: dict[str, AssetTypeProtocol] = {}

    def register_type(self, asset_type: AssetTypeProtocol) -> None:
        """Register an asset type instance."""
        self._types[asset_type.name] = asset_type

    def register_decorator(self, name: str) -> Callable[[type[T]], type[T]]:
        """Decorator for registering asset type classes."""
        def decorator(cls: type[T]) -> type[T]:
            instance: Any = cls()
            self._types[name] = instance
            return cls
        return decorator

    def get(self, name: str) -> AssetTypeProtocol | None:
        """Get an asset type by name."""
        return self._types.get(name)

    def list_types(self) -> list[str]:
        """List all registered asset type names."""
        return list(self._types.keys())


# Global default registry with built-in types
default_registry = AssetRegistry()
