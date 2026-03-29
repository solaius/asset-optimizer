"""Skill asset type — optimizes Claude Code skill files (markdown with frontmatter)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

from asset_optimizer.assets.base import AssetContent


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse YAML frontmatter from markdown. Returns (frontmatter_dict, body)."""
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    frontmatter_raw = parts[1].strip()
    body = parts[2].strip()

    metadata: dict[str, str] = {}
    for line in frontmatter_raw.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            metadata[key.strip()] = value.strip()

    return metadata, body


class SkillAssetType:
    """Asset type for Claude Code skill files (markdown with YAML frontmatter)."""

    name: str = "skill"
    file_extensions: list[str] = [".md"]

    def load(self, path: Path) -> AssetContent:
        raw = path.read_text(encoding="utf-8")
        metadata, body = _parse_frontmatter(raw)
        return AssetContent(text=raw, metadata=metadata)

    def save(self, content: AssetContent, path: Path) -> None:
        path.write_text(content.text or "", encoding="utf-8")

    def validate(self, content: AssetContent) -> list[str]:
        errors: list[str] = []
        text = content.text or ""
        if not text.strip():
            errors.append("Skill content must not be empty")
            return errors
        if not text.startswith("---"):
            errors.append("Skill must have YAML frontmatter (start with ---)")
        else:
            metadata, _ = _parse_frontmatter(text)
            if "name" not in metadata:
                errors.append("Skill frontmatter must include 'name'")
            if "description" not in metadata:
                errors.append("Skill frontmatter must include 'description'")
        return errors

    def default_evaluation(self) -> dict[str, Any]:
        return {
            "asset_type": "skill",
            "criteria": [
                {
                    "name": "structure",
                    "description": (
                        "Does the skill have proper frontmatter and clear sections?"
                    ),
                    "max_score": 10,
                },
                {
                    "name": "completeness",
                    "description": (
                        "Does the skill cover all necessary instructions"
                        " and edge cases?"
                    ),
                    "max_score": 10,
                },
                {
                    "name": "clarity",
                    "description": "Are instructions unambiguous and easy to follow?",
                    "max_score": 10,
                },
                {
                    "name": "actionability",
                    "description": (
                        "Can a developer follow the skill without additional context?"
                    ),
                    "max_score": 10,
                },
            ],
            "scorer_config": {
                "type": "composite",
                "heuristic_weight": 0.3,
                "ai_judge_weight": 0.7,
            },
        }

    def render_for_prompt(self, content: AssetContent) -> str:
        return f"```markdown\n{content.text}\n```"
