"""Google Gemini text provider implementation."""

from __future__ import annotations

import json

import google.generativeai as genai

from asset_optimizer.providers.base import (
    Criterion,
    JudgmentResult,
    JudgmentScore,
    Message,
    TextProvider,
)

_JUDGE_INTRO = (
    "You are an expert evaluator. "
    "Score the following content against each criterion.\n\n"
)
_JSON_FORMAT = (
    '{"scores": [{"criterion": "<name>", "score": <number>,'
    ' "reasoning": "<text>"}, ...]}'
)


_VISION_MODELS = {
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
}


class GeminiProvider(TextProvider):
    """Text provider backed by Google's Gemini generative AI API."""

    def __init__(
        self,
        model: str = "gemini-1.5-flash",
        api_key: str | None = None,
    ) -> None:
        self.model = model
        if api_key is not None:
            genai.configure(api_key=api_key)  # type: ignore[attr-defined]
        self._generative_model = genai.GenerativeModel(model)  # type: ignore[attr-defined]

    async def complete(self, messages: list[Message], **kwargs: object) -> str:
        """Generate a completion by combining messages into a single prompt.

        Gemini's Python SDK uses a simple generate_content interface.  We
        combine all messages into a single text block, labelling each turn so
        the model has the necessary context.
        """
        combined = "\n\n".join(
            f"[{m.role.upper()}]: {m.content}" for m in messages
        )
        response = await self._generative_model.generate_content_async(
            combined, **kwargs  # type: ignore[arg-type]
        )
        return str(response.text) if response.text else ""

    async def judge(
        self,
        content: str,
        criteria: list[Criterion],
        image: bytes | None = None,
        image_format: str = "png",
    ) -> JudgmentResult:
        """Judge content against criteria using the Gemini model."""
        if image is not None and self.model not in _VISION_MODELS:
            raise ValueError(
                f"Model {self.model} does not support vision. "
                f"Use one of: {', '.join(sorted(_VISION_MODELS))}"
            )

        criteria_text = "\n".join(
            f"- {c.name} (max {c.max_score}): {c.description}"
            + (f"\n  Rubric: {c.rubric}" if c.rubric else "")
            for c in criteria
        )
        prompt = (
            f"{_JUDGE_INTRO}"
            f"Content to evaluate:\n{content}\n\n"
            f"Criteria:\n{criteria_text}\n\n"
            "Respond with a JSON object in this exact format "
            f"(no markdown, raw JSON only):\n{_JSON_FORMAT}"
        )

        if image is not None:
            parts: list[object] = [
                prompt,
                {
                    "inline_data": {
                        "mime_type": f"image/{image_format}",
                        "data": image,
                    }
                },
            ]
            response = await self._generative_model.generate_content_async(parts)
            response_text = str(response.text) if response.text else ""
        else:
            response_text = await self.complete(
                [Message(role="user", content=prompt)]
            )

        return self._parse_judgment(response_text, criteria)

    def _parse_judgment(
        self, response_text: str, criteria: list[Criterion]
    ) -> JudgmentResult:
        """Parse the JSON judgment response into a JudgmentResult."""
        try:
            text = response_text.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = json.loads(text)
            scores = [
                JudgmentScore(
                    criterion=item["criterion"],
                    score=float(item["score"]),
                    reasoning=item.get("reasoning", ""),
                )
                for item in data.get("scores", [])
            ]
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            scores = [
                JudgmentScore(
                    criterion=c.name, score=c.max_score / 2, reasoning="parse error"
                )
                for c in criteria
            ]
        return JudgmentResult(scores=scores)
