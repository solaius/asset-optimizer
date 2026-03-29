"""Application configuration with YAML file and environment variable support."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


def _resolve_env_vars(value: str) -> str:
    """Replace ${VAR_NAME} patterns with environment variable values."""
    def replacer(match: re.Match[str]) -> str:
        var_name = match.group(1)
        return os.environ.get(var_name, match.group(0))
    return re.sub(r"\$\{(\w+)\}", replacer, value)


def _resolve_env_vars_in_dict(data: dict[str, Any]) -> dict[str, Any]:
    """Recursively resolve environment variables in a config dict."""
    resolved: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, str):
            resolved[key] = _resolve_env_vars(value)
        elif isinstance(value, dict):
            resolved[key] = _resolve_env_vars_in_dict(value)
        else:
            resolved[key] = value
    return resolved


class StorageConfig(BaseModel):
    """Database storage configuration."""

    backend: str = "sqlite"
    sqlite_path: Path = Path("./data/optimizer.db")
    postgres_url: str | None = None


class ProviderEntry(BaseModel):
    """Single provider configuration entry."""

    api_key: str | None = None
    model: str | None = None
    base_url: str | None = None
    endpoint: str | None = None


class ProvidersConfig(BaseModel):
    """AI provider configuration."""

    text: dict[str, Any] = {}
    image: dict[str, Any] = {}


class ServerConfig(BaseModel):
    """API server configuration."""

    host: str = "0.0.0.0"
    port: int = 8000


class DefaultsConfig(BaseModel):
    """Default optimization parameters."""

    max_iterations: int = 20
    min_improvement: float = 0.01
    convergence_strategy: str = "greedy"
    stagnation_limit: int = 5


class AppConfig(BaseModel):
    """Root application configuration."""

    storage: StorageConfig = StorageConfig()
    providers: ProvidersConfig = ProvidersConfig()
    server: ServerConfig = ServerConfig()
    defaults: DefaultsConfig = DefaultsConfig()


def load_config(path: Path | None = None) -> AppConfig:
    """Load configuration from a YAML file, falling back to defaults.

    Supports ${ENV_VAR} interpolation in string values.
    """
    if path is None:
        path = Path("asset-optimizer.yaml")

    if not path.exists():
        return AppConfig()

    raw = yaml.safe_load(path.read_text()) or {}
    resolved = _resolve_env_vars_in_dict(raw)
    return AppConfig(**resolved)
