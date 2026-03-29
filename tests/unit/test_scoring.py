from asset_optimizer.scoring.base import ScoreResult
from asset_optimizer.scoring.composite import CompositeScorer
from asset_optimizer.scoring.heuristic import (
    KeywordScorer,
    LengthScorer,
    ReadabilityScorer,
    StructureScorer,
)


class TestLengthScorer:
    def test_optimal_length(self) -> None:
        scorer = LengthScorer(min_length=10, max_length=100, optimal_length=50)
        result = scorer.score("A" * 50)
        assert result.value == 10.0

    def test_too_short(self) -> None:
        scorer = LengthScorer(min_length=10, max_length=100, optimal_length=50)
        result = scorer.score("Hi")
        assert result.value < 5.0

    def test_too_long(self) -> None:
        scorer = LengthScorer(min_length=10, max_length=100, optimal_length=50)
        result = scorer.score("A" * 200)
        assert result.value < 5.0

    def test_empty_string(self) -> None:
        scorer = LengthScorer(min_length=10, max_length=100)
        result = scorer.score("")
        assert result.value == 0.0


class TestStructureScorer:
    def test_has_all_sections(self) -> None:
        scorer = StructureScorer(required_sections=["# Header", "## Body"])
        text = "# Header\nSome content\n## Body\nMore content"
        result = scorer.score(text)
        assert result.value == 10.0

    def test_missing_sections(self) -> None:
        scorer = StructureScorer(required_sections=["# Header", "## Body", "## Footer"])
        text = "# Header\nSome content"
        result = scorer.score(text)
        assert result.value < 10.0


class TestKeywordScorer:
    def test_all_keywords_present(self) -> None:
        scorer = KeywordScorer(required_keywords=["hello", "world"])
        result = scorer.score("hello beautiful world")
        assert result.value == 10.0

    def test_some_keywords_missing(self) -> None:
        scorer = KeywordScorer(required_keywords=["hello", "world", "foo"])
        result = scorer.score("hello world")
        assert 5.0 < result.value < 10.0

    def test_no_keywords_present(self) -> None:
        scorer = KeywordScorer(required_keywords=["alpha", "beta"])
        result = scorer.score("nothing here")
        assert result.value == 0.0


class TestReadabilityScorer:
    def test_simple_text_scores_well(self) -> None:
        scorer = ReadabilityScorer()
        result = scorer.score("The cat sat on the mat. It was a good cat.")
        assert result.value > 0.0

    def test_empty_text(self) -> None:
        scorer = ReadabilityScorer()
        result = scorer.score("")
        assert result.value == 0.0


class TestCompositeScorer:
    def test_weighted_average(self) -> None:
        scorer1 = LengthScorer(min_length=1, max_length=100, optimal_length=10)
        scorer2 = KeywordScorer(required_keywords=["hello"])

        composite = CompositeScorer(
            scorers=[
                {"scorer": scorer1, "weight": 0.5, "criterion": "length"},
                {"scorer": scorer2, "weight": 0.5, "criterion": "keywords"},
            ]
        )
        results = composite.score_all("hello world")
        assert len(results) == 2
        total = composite.composite_score(results)
        assert 0.0 <= total <= 10.0

    def test_single_scorer(self) -> None:
        scorer = LengthScorer(min_length=5, max_length=50, optimal_length=20)
        composite = CompositeScorer(
            scorers=[{"scorer": scorer, "weight": 1.0, "criterion": "length"}]
        )
        results = composite.score_all("A" * 20)
        assert len(results) == 1
        assert results[0].value == 10.0


class TestScoreResult:
    def test_fields(self) -> None:
        result = ScoreResult(
            criterion="clarity",
            value=7.5,
            max_value=10.0,
            scorer_type="heuristic",
            details={"note": "good"},
        )
        assert result.criterion == "clarity"
        assert result.value == 7.5
        assert result.scorer_type == "heuristic"
