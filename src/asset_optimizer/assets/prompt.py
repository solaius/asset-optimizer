"""Prompt asset type — optimizes text prompts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

from asset_optimizer.assets.base import AssetContent


class PromptAssetType:
    """Asset type for text prompts (system prompts, user prompts, templates)."""

    name: str = "prompt"
    file_extensions: list[str] = [".txt", ".md", ".prompt"]

    def load(self, path: Path) -> AssetContent:
        return AssetContent(text=path.read_text(encoding="utf-8"))

    def save(self, content: AssetContent, path: Path) -> None:
        path.write_text(content.text or "", encoding="utf-8")

    def validate(self, content: AssetContent) -> list[str]:
        errors: list[str] = []
        if not content.text or not content.text.strip():
            errors.append("Prompt content must not be empty")
        return errors

    def default_evaluation(self) -> dict[str, Any]:
        return {
            "asset_type": "prompt",
            "criteria": [
                {
                    "name": "clarity",
                    "description": "Is the prompt unambiguous and easy to understand?",
                    "max_score": 10,
                    "rubric": (
                        "1-3: Vague, multiple interpretations possible\n"
                        "4-6: Mostly clear but some ambiguity\n"
                        "7-9: Clear and specific\n"
                        "10: Crystal clear, no room for misinterpretation"
                    ),
                },
                {
                    "name": "specificity",
                    "description": (
                        "Does the prompt include specific, actionable instructions?"
                    ),
                    "max_score": 10,
                    "rubric": (
                        "1-3: Generic instructions, no concrete guidance\n"
                        "4-6: Some specifics but leaves gaps\n"
                        "7-9: Detailed, actionable instructions\n"
                        "10: Exhaustively specific with examples"
                    ),
                },
                {
                    "name": "effectiveness",
                    "description": (
                        "Would this prompt reliably produce the desired output?"
                    ),
                    "max_score": 10,
                    "rubric": (
                        "1-3: Unreliable, inconsistent results expected\n"
                        "4-6: Sometimes produces desired output\n"
                        "7-9: Reliably produces good output\n"
                        "10: Consistently produces excellent output"
                    ),
                },
            ],
            "scorer_config": {
                "type": "composite",
                "heuristic_weight": 0.2,
                "ai_judge_weight": 0.8,
            },
        }

    def render_for_prompt(self, content: AssetContent) -> str:
        return f"```\n{content.text}\n```"
