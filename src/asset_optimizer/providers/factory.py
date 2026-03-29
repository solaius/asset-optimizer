"""Provider factory — creates providers from config/env vars.

Usage::

    # Auto-detect from .env + asset-optimizer.yaml
    provider = create_text_provider()
    judge = create_judge_provider()
    image_provider = create_image_provider()

    # Override via arguments
    provider = create_text_provider(name="claude", model="claude-sonnet-4-20250514")
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from asset_optimizer.config import AppConfig, load_config

if TYPE_CHECKING:
    from asset_optimizer.providers.base import TextProvider
    from asset_optimizer.providers.image_providers.base import ImageProvider

# Provider name -> (module_path, class_name)
_TEXT_PROVIDERS: dict[str, tuple[str, str]] = {
    "openai": ("asset_optimizer.providers.openai_provider", "OpenAITextProvider"),
    "claude": ("asset_optimizer.providers.anthropic_provider", "AnthropicProvider"),
    "gemini": ("asset_optimizer.providers.gemini_provider", "GeminiProvider"),
    "vllm": ("asset_optimizer.providers.openai_compat", "OpenAICompatProvider"),
    "ollama": ("asset_optimizer.providers.openai_compat", "OpenAICompatProvider"),
}

_IMAGE_PROVIDERS: dict[str, tuple[str, str]] = {
    "openai_image": (
        "asset_optimizer.providers.image_providers.openai_image",
        "OpenAIImageProvider",
    ),
    "nano_banana": (
        "asset_optimizer.providers.image_providers.nano_banana",
        "NanoBananaProvider",
    ),
}

# Provider name -> env var for API key
_API_KEY_ENV: dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "vllm": "VLLM_API_KEY",
    "ollama": "OLLAMA_API_KEY",
    "openai_image": "OPENAI_API_KEY",
    "nano_banana": "NANO_BANANA_API_KEY",
}

# Provider name -> env var for default model
_MODEL_ENV: dict[str, str] = {
    "openai": "AO_DEFAULT_TEXT_MODEL",
    "claude": "AO_DEFAULT_TEXT_MODEL",
    "gemini": "AO_DEFAULT_TEXT_MODEL",
    "vllm": "VLLM_MODEL",
    "ollama": "OLLAMA_MODEL",
    "openai_image": "AO_DEFAULT_IMAGE_MODEL",
}

# Default models per provider when nothing is configured
_DEFAULT_MODELS: dict[str, str] = {
    "openai": "gpt-4o",
    "claude": "claude-sonnet-4-20250514",
    "gemini": "gemini-2.0-flash",
    "vllm": "default",
    "ollama": "llama3",
    "openai_image": "dall-e-3",
}


def _load_dotenv() -> None:
    """Load .env file into os.environ if it exists."""
    env_path = Path(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        # Don't overwrite existing env vars (explicit env takes precedence)
        if key not in os.environ:
            os.environ[key] = value


def _import_class(module_path: str, class_name: str) -> type:
    """Dynamically import a class from a module path."""
    import importlib

    module = importlib.import_module(module_path)
    return getattr(module, class_name)  # type: ignore[no-any-return]


def _resolve_provider_config(
    name: str,
    config: AppConfig,
    category: str = "text",
) -> dict[str, Any]:
    """Extract provider-specific config from the loaded AppConfig."""
    providers_dict = getattr(config.providers, category, {})
    if isinstance(providers_dict, dict) and name in providers_dict:
        entry = providers_dict[name]
        if isinstance(entry, dict):
            return entry
    return {}


def create_text_provider(
    name: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    config_path: Path | None = None,
) -> TextProvider:
    """Create a text provider from config, env vars, or explicit arguments.

    Resolution order for each parameter:
    1. Explicit argument (highest priority)
    2. YAML config file
    3. Environment variable
    4. Built-in default
    """
    _load_dotenv()
    config = load_config(config_path)

    # Resolve provider name
    if name is None:
        name = os.environ.get("AO_DEFAULT_TEXT_PROVIDER")
    if name is None:
        yaml_default = config.providers.text.get("default") if isinstance(
            config.providers.text, dict
        ) else None
        if yaml_default:
            name = str(yaml_default)
    if name is None:
        name = "openai"

    if name not in _TEXT_PROVIDERS:
        available = ", ".join(_TEXT_PROVIDERS.keys())
        msg = f"Unknown text provider '{name}'. Available: {available}"
        raise ValueError(msg)

    # Get provider-specific config from YAML
    yaml_config = _resolve_provider_config(name, config, "text")

    # Resolve API key
    if api_key is None:
        api_key = yaml_config.get("api_key")
    if api_key is None or api_key.startswith("${"):
        env_var = _API_KEY_ENV.get(name, "")
        api_key = os.environ.get(env_var, "")

    if not api_key and name not in ("vllm", "ollama"):
        env_var = _API_KEY_ENV.get(name, "")
        msg = (
            f"No API key for provider '{name}'."
            f" Set {env_var} in .env or pass api_key="
        )
        raise ValueError(msg)

    # Resolve model
    if model is None:
        model = yaml_config.get("model")
    if model is None or (isinstance(model, str) and model.startswith("${")):
        model_env = _MODEL_ENV.get(name, "")
        model = os.environ.get(model_env)
    if model is None:
        model = _DEFAULT_MODELS.get(name, "default")

    # Resolve base_url (for vllm, ollama)
    if base_url is None:
        base_url = yaml_config.get("base_url")
    if base_url is None or (isinstance(base_url, str) and base_url.startswith("${")):
        if name == "vllm":
            base_url = os.environ.get("VLLM_BASE_URL", "http://localhost:8000/v1")
        elif name == "ollama":
            base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")

    # Import and instantiate
    module_path, class_name = _TEXT_PROVIDERS[name]
    cls = _import_class(module_path, class_name)

    if name in ("vllm", "ollama"):
        return cls(model=model, base_url=base_url or "", api_key=api_key or "EMPTY")  # type: ignore[no-any-return]
    return cls(api_key=api_key, model=model)  # type: ignore[no-any-return]


def create_judge_provider(
    name: str | None = None,
    model: str | None = None,
    config_path: Path | None = None,
) -> TextProvider:
    """Create the AI judge provider. Falls back to the default text provider."""
    _load_dotenv()

    # Check if a separate judge is configured
    if name is None:
        name = os.environ.get("AO_JUDGE_PROVIDER") or None
    if model is None:
        model = os.environ.get("AO_JUDGE_MODEL") or None

    # Fall back to default text provider
    return create_text_provider(name=name, model=model, config_path=config_path)


def create_image_provider(
    name: str | None = None,
    api_key: str | None = None,
    config_path: Path | None = None,
) -> ImageProvider:
    """Create an image provider from config, env vars, or explicit arguments."""
    _load_dotenv()
    config = load_config(config_path)

    # Resolve provider name
    if name is None:
        name = os.environ.get("AO_DEFAULT_IMAGE_PROVIDER")
    if name is None:
        yaml_img = config.providers.image
        if isinstance(yaml_img, dict) and "default" in yaml_img:
            name = str(yaml_img["default"])
    if name is None:
        name = "openai_image"

    if name not in _IMAGE_PROVIDERS:
        available = ", ".join(_IMAGE_PROVIDERS.keys())
        msg = f"Unknown image provider '{name}'. Available: {available}"
        raise ValueError(msg)

    # Get provider-specific config from YAML
    yaml_config = _resolve_provider_config(name, config, "image")

    # Resolve API key
    if api_key is None:
        api_key = yaml_config.get("api_key")
    if api_key is None or (isinstance(api_key, str) and api_key.startswith("${")):
        env_var = _API_KEY_ENV.get(name, "")
        api_key = os.environ.get(env_var, "")

    if not api_key:
        env_var = _API_KEY_ENV.get(name, "")
        msg = f"No API key for image provider '{name}'. Set {env_var} in .env"
        raise ValueError(msg)

    # Import and instantiate
    module_path, class_name = _IMAGE_PROVIDERS[name]
    cls = _import_class(module_path, class_name)

    if name == "nano_banana":
        base_url = yaml_config.get("endpoint") or os.environ.get(
            "NANO_BANANA_ENDPOINT", "https://api.nanobanana.com/v1"
        )
        return cls(base_url=base_url, api_key=api_key)  # type: ignore[no-any-return]

    # openai_image
    model = yaml_config.get("model") or os.environ.get(
        "AO_DEFAULT_IMAGE_MODEL", "dall-e-3"
    )
    return cls(api_key=api_key, model=model)  # type: ignore[no-any-return]
