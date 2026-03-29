"""Anthropic text provider implementation."""

from __future__ import annotations

import json

import anthropic

from asset_optimizer.providers.base import (
    Criterion,
    JudgmentResult,
    JudgmentScore,
    Message,
    TextProvider,
)

_SYSTEM_ROLE = "system"
_JUDGE_INTRO = (
    "You are an expert evaluator. "
    "Score the following content against each criterion.\n\n"
)
_JSON_FORMAT = (
    '{"scores": [{"criterion": "<name>", "score": <number>,'
    ' "reasoning": "<text>"}, ...]}'
)


class AnthropicProvider(TextProvider):
    """Text provider backed by Anthropic's Messages API."""

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-latest",
        api_key: str | None = None,
        max_tokens: int = 4096,
    ) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self._client = anthropic.AsyncAnthropic(api_key=api_key)

    async def complete(self, messages: list[Message], **kwargs: object) -> str:
        """Generate a completion using the Anthropic Messages API.

        Anthropic separates the system prompt from the conversation messages,
        so any leading message with role="system" is extracted and passed as
        the ``system`` parameter.
        """
        system: str | anthropic.NotGiven = anthropic.NOT_GIVEN
        filtered: list[Message] = []

        for msg in messages:
            if msg.role == _SYSTEM_ROLE and not filtered:
                # Only the first system message (before any user/assistant turns)
                # is used as the top-level system prompt.
                system = msg.content
            else:
                filtered.append(msg)

        anthropic_messages: list[dict[str, str]] = [
            {"role": m.role, "content": m.content} for m in filtered
        ]

        response = await self._client.messages.create(  # type: ignore[call-overload]
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=anthropic_messages,
            **kwargs,
        )
        block = response.content[0] if response.content else None
        if block is None:
            return ""
        if hasattr(block, "text"):
            return str(block.text)
        return ""

    async def judge(self, content: str, criteria: list[Criterion]) -> JudgmentResult:
        """Judge content against criteria using the Anthropic model."""
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
        response_text = await self.complete([Message(role="user", content=prompt)])
        return self._parse_judgment(response_text, criteria)

    def _parse_judgment(
        self, response_text: str, criteria: list[Criterion]
    ) -> JudgmentResult:
        """Parse the JSON judgment response into a JudgmentResult."""
        try:
            # Strip potential markdown code fences
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
