"""Tests for provider factory — auto-wiring from env/config."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
import yaml

if TYPE_CHECKING:
    from pathlib import Path

from asset_optimizer.providers.factory import (
    create_image_provider,
    create_judge_provider,
    create_text_provider,
)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Remove all AO_ and provider env vars and prevent .env loading."""
    for key in list(os.environ):
        prefixes = (
            "AO_", "OPENAI_", "ANTHROPIC_",
            "GEMINI_", "NANO_BANANA_", "VLLM_", "OLLAMA_",
        )
        if key.startswith(prefixes):
            monkeypatch.delenv(key, raising=False)
    # Change cwd to tmp_path so _load_dotenv won't find the real .env
    monkeypatch.chdir(tmp_path)


class TestCreateTextProvider:
    def test_explicit_name_and_key(self) -> None:
        provider = create_text_provider(
            name="openai", api_key="sk-test", model="gpt-4o-mini"
        )
        assert provider is not None

    def test_from_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AO_DEFAULT_TEXT_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("AO_DEFAULT_TEXT_MODEL", "gpt-4o-mini")
        provider = create_text_provider()
        assert provider is not None

    def test_from_yaml_config(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        config = {
            "providers": {
                "text": {
                    "default": "openai",
                    "openai": {"api_key": "sk-from-yaml", "model": "gpt-4o"},
                }
            }
        }
        config_file = tmp_path / "asset-optimizer.yaml"
        config_file.write_text(yaml.dump(config))

        provider = create_text_provider(config_path=config_file)
        assert provider is not None

    def test_explicit_overrides_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AO_DEFAULT_TEXT_PROVIDER", "gemini")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        # Explicit name should override env
        provider = create_text_provider(name="openai", api_key="sk-test")
        assert provider is not None

    def test_unknown_provider_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown text provider"):
            create_text_provider(name="nonexistent", api_key="test")

    def test_missing_api_key_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        with pytest.raises(ValueError, match="No API key"):
            create_text_provider(name="openai")

    def test_claude_provider(self) -> None:
        provider = create_text_provider(
            name="claude", api_key="sk-ant-test", model="claude-haiku-4-5-20251001"
        )
        assert provider is not None

    def test_gemini_provider(self) -> None:
        provider = create_text_provider(
            name="gemini", api_key="test-key", model="gemini-2.0-flash"
        )
        assert provider is not None

    def test_vllm_no_key_required(self) -> None:
        provider = create_text_provider(
            name="vllm", base_url="http://localhost:8000/v1", model="test-model"
        )
        assert provider is not None

    def test_ollama_no_key_required(self) -> None:
        provider = create_text_provider(
            name="ollama", base_url="http://localhost:11434/v1", model="llama3"
        )
        assert provider is not None


class TestCreateJudgeProvider:
    def test_falls_back_to_text_provider(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        judge = create_judge_provider(name="openai")
        assert judge is not None

    def test_separate_judge_provider(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("AO_JUDGE_PROVIDER", "openai")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        judge = create_judge_provider()
        assert judge is not None

    def test_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        monkeypatch.setenv("AO_DEFAULT_TEXT_PROVIDER", "openai")
        judge = create_judge_provider()
        assert judge is not None


class TestCreateImageProvider:
    def test_openai_image(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        provider = create_image_provider(name="openai_image")
        assert provider is not None

    def test_nano_banana(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("NANO_BANANA_API_KEY", "test-key")
        provider = create_image_provider(name="nano_banana")
        assert provider is not None

    def test_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AO_DEFAULT_IMAGE_PROVIDER", "openai_image")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        provider = create_image_provider()
        assert provider is not None

    def test_unknown_image_provider_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown image provider"):
            create_image_provider(name="nonexistent", api_key="test")

    def test_missing_key_raises(self) -> None:
        with pytest.raises(ValueError, match="No API key"):
            create_image_provider(name="openai_image")
