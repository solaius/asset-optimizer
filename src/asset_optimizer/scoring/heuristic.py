"""Heuristic scorers for content evaluation."""

import re

from asset_optimizer.scoring.base import Scorer, ScoreResult


class LengthScorer(Scorer):
    """Scores content based on its length relative to an optimal target."""

    def __init__(
        self,
        min_length: int,
        max_length: int,
        optimal_length: int | None = None,
    ) -> None:
        self.min_length = min_length
        self.max_length = max_length
        if optimal_length is not None:
            self.optimal_length = optimal_length
        else:
            self.optimal_length = (min_length + max_length) // 2

    def score(self, content: str) -> ScoreResult:
        length = len(content)

        if length == 0:
            return ScoreResult(
                criterion="length",
                value=0.0,
                scorer_type="heuristic",
                details={"length": 0, "optimal_length": self.optimal_length},
            )

        # Distance from optimal as a fraction of the usable range
        distance = abs(length - self.optimal_length)
        half_range = max(
            self.optimal_length - self.min_length,
            self.max_length - self.optimal_length,
            1,
        )
        ratio = distance / half_range
        value = max(0.0, 10.0 * (1.0 - ratio))

        return ScoreResult(
            criterion="length",
            value=value,
            scorer_type="heuristic",
            details={
                "length": length,
                "optimal_length": self.optimal_length,
                "min_length": self.min_length,
                "max_length": self.max_length,
            },
        )


class StructureScorer(Scorer):
    """Scores content based on the presence of required sections."""

    def __init__(self, required_sections: list[str]) -> None:
        self.required_sections = required_sections

    def score(self, content: str) -> ScoreResult:
        if not self.required_sections:
            return ScoreResult(
                criterion="structure",
                value=10.0,
                scorer_type="heuristic",
                details={"found": 0, "required": 0},
            )

        found = sum(1 for section in self.required_sections if section in content)
        proportion = found / len(self.required_sections)
        value = proportion * 10.0

        return ScoreResult(
            criterion="structure",
            value=value,
            scorer_type="heuristic",
            details={
                "found": found,
                "required": len(self.required_sections),
                "missing": [s for s in self.required_sections if s not in content],
            },
        )


class KeywordScorer(Scorer):
    """Scores content based on the presence of required keywords."""

    def __init__(self, required_keywords: list[str]) -> None:
        self.required_keywords = required_keywords

    def score(self, content: str) -> ScoreResult:
        if not self.required_keywords:
            return ScoreResult(
                criterion="keywords",
                value=10.0,
                scorer_type="heuristic",
                details={"found": 0, "required": 0},
            )

        lower_content = content.lower()
        found = sum(
            1 for kw in self.required_keywords if kw.lower() in lower_content
        )
        proportion = found / len(self.required_keywords)
        value = proportion * 10.0

        return ScoreResult(
            criterion="keywords",
            value=value,
            scorer_type="heuristic",
            details={
                "found": found,
                "required": len(self.required_keywords),
                "missing": [
                    kw
                    for kw in self.required_keywords
                    if kw.lower() not in lower_content
                ],
            },
        )


def _count_syllables(word: str) -> int:
    """Count syllables in a word using a simple heuristic."""
    word = word.lower().strip(".,!?;:'\"")
    if not word:
        return 0
    # Count vowel groups as syllables
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    # Silent 'e' at end
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


class ReadabilityScorer(Scorer):
    """Scores content using a simplified Flesch-Kincaid readability metric."""

    def score(self, content: str) -> ScoreResult:
        if not content.strip():
            return ScoreResult(
                criterion="readability",
                value=0.0,
                scorer_type="heuristic",
                details={"reason": "empty content"},
            )

        # Split into sentences
        sentences = re.split(r"[.!?]+", content)
        sentences = [s.strip() for s in sentences if s.strip()]
        num_sentences = max(len(sentences), 1)

        # Split into words
        words = re.findall(r"\b\w+\b", content)
        num_words = len(words)

        if num_words == 0:
            return ScoreResult(
                criterion="readability",
                value=0.0,
                scorer_type="heuristic",
                details={"reason": "no words found"},
            )

        # Count syllables
        num_syllables = sum(_count_syllables(w) for w in words)

        # Flesch Reading Ease formula:
        # 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
        words_per_sentence = num_words / num_sentences
        syllables_per_word = num_syllables / num_words
        flesch = 206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word

        # Flesch score: 0 (hard) to 100 (easy); clamp and normalize to 0-10
        flesch_clamped = max(0.0, min(100.0, flesch))
        value = flesch_clamped / 10.0

        return ScoreResult(
            criterion="readability",
            value=value,
            scorer_type="heuristic",
            details={
                "flesch_score": round(flesch, 2),
                "num_sentences": num_sentences,
                "num_words": num_words,
                "num_syllables": num_syllables,
            },
        )
