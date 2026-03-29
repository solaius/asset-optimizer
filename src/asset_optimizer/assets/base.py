"""Base types and protocol for asset types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class AssetContent:
    """Content container for any asset type."""

    text: str | None = None
    file_path: Path | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AssetTypeProtocol(Protocol):
    """Protocol that all asset types must implement."""

    name: str
    file_extensions: list[str]

    def load(self, path: Path) -> AssetContent: ...
    def save(self, content: AssetContent, path: Path) -> None: ...
    def validate(self, content: AssetContent) -> list[str]: ...
    def default_evaluation(self) -> dict[str, Any]: ...
    def render_for_prompt(self, content: AssetContent) -> str: ...
