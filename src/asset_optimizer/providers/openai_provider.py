"""OpenAI text provider implementation."""

from __future__ import annotations

import json

import openai

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


class OpenAITextProvider(TextProvider):
    """Text provider backed by OpenAI's chat completion API."""

    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.model = model
        self._client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    async def complete(self, messages: list[Message], **kwargs: object) -> str:
        """Generate a chat completion from the given messages."""
        oai_messages: list[dict[str, str]] = [
            {"role": m.role, "content": m.content} for m in messages
        ]
        response = await self._client.chat.completions.create(  # type: ignore[call-overload]
            model=self.model,
            messages=oai_messages,
            **kwargs,
        )
        content = response.choices[0].message.content
        return content if content is not None else ""

    async def judge(self, content: str, criteria: list[Criterion]) -> JudgmentResult:
        """Judge content against criteria using the OpenAI model."""
        criteria_text = "\n".join(
            f"- {c.name} (max {c.max_score}): {c.description}"
            + (f"\n  Rubric: {c.rubric}" if c.rubric else "")
            for c in criteria
        )
        prompt = (
            f"{_JUDGE_INTRO}"
            f"Content to evaluate:\n{content}\n\n"
            f"Criteria:\n{criteria_text}\n\n"
            f"Respond with a JSON object in this exact format:\n{_JSON_FORMAT}"
        )
        response_text = await self.complete(
            [Message(role="user", content=prompt)],
            response_format={"type": "json_object"},
        )
        return self._parse_judgment(response_text, criteria)

    def _parse_judgment(
        self, response_text: str, criteria: list[Criterion]
    ) -> JudgmentResult:
        """Parse the JSON judgment response into a JudgmentResult."""
        try:
            data = json.loads(response_text)
            scores = [
                JudgmentScore(
                    criterion=item["criterion"],
                    score=float(item["score"]),
                    reasoning=item.get("reasoning", ""),
                )
                for item in data.get("scores", [])
            ]
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            # Fall back to neutral scores on parse failure
            scores = [
                JudgmentScore(
                    criterion=c.name, score=c.max_score / 2, reasoning="parse error"
                )
                for c in criteria
            ]
        return JudgmentResult(scores=scores)
