"""OpenAI-compatible provider for vLLM, Ollama, and similar local servers."""

from __future__ import annotations

from asset_optimizer.providers.openai_provider import OpenAITextProvider


class OpenAICompatProvider(OpenAITextProvider):
    """Text provider for servers that expose an OpenAI-compatible REST API.

    This covers self-hosted inference servers such as vLLM and Ollama, which
    implement OpenAI's ``/v1/chat/completions`` endpoint but run locally or on
    a private network.

    Example::

        # vLLM
        provider = OpenAICompatProvider(
            model="mistralai/Mistral-7B-Instruct-v0.3",
            base_url="http://localhost:8000/v1",
            api_key="EMPTY",
        )

        # Ollama
        provider = OpenAICompatProvider(
            model="llama3",
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )
    """

    def __init__(
        self,
        model: str,
        base_url: str,
        api_key: str = "EMPTY",
    ) -> None:
        super().__init__(model=model, api_key=api_key, base_url=base_url)
