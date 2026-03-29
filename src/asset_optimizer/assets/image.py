"""Image asset type — optimizes image generation prompts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

from asset_optimizer.assets.base import AssetContent


class ImageAssetType:
    """Asset type for image generation prompts."""

    name: str = "image"
    file_extensions: list[str] = [".txt", ".prompt"]

    def load(self, path: Path) -> AssetContent:
        return AssetContent(text=path.read_text(encoding="utf-8"))

    def save(self, content: AssetContent, path: Path) -> None:
        path.write_text(content.text or "", encoding="utf-8")

    def validate(self, content: AssetContent) -> list[str]:
        errors: list[str] = []
        if not content.text or not content.text.strip():
            errors.append("Image generation prompt must not be empty")
        if content.text and len(content.text) > 4000:
            errors.append("Image generation prompt exceeds 4000 character limit")
        return errors

    def default_evaluation(self) -> dict[str, Any]:
        return {
            "asset_type": "image",
            "criteria": [
                {
                    "name": "prompt_specificity",
                    "description": (
                        "Does the prompt clearly describe the desired image?"
                    ),
                    "max_score": 10,
                },
                {
                    "name": "prompt_style",
                    "description": (
                        "Does the prompt include style, mood, and composition guidance?"
                    ),
                    "max_score": 10,
                },
                {
                    "name": "image_quality",
                    "description": (
                        "Is the generated image high quality and visually appealing?"
                    ),
                    "max_score": 10,
                },
                {
                    "name": "image_relevance",
                    "description": (
                        "Does the generated image match the prompt intent?"
                    ),
                    "max_score": 10,
                },
            ],
            "scorer_config": {
                "type": "composite",
                "heuristic_weight": 0.1,
                "ai_judge_weight": 0.9,
            },
        }

    def render_for_prompt(self, content: AssetContent) -> str:
        return f"Image generation prompt:\n```\n{content.text}\n```"
