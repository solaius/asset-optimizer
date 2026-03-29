from pathlib import Path

import yaml

from asset_optimizer.core.evaluation import EvaluationConfig, load_evaluation


class TestEvaluationConfig:
    def test_from_dict(self) -> None:
        data = {
            "name": "test-eval",
            "asset_type": "prompt",
            "criteria": [
                {
                    "name": "clarity",
                    "description": "Is it clear?",
                    "max_score": 10,
                    "rubric": "1-10",
                },
            ],
            "scorer_config": {
                "type": "composite",
                "heuristic_weight": 0.3,
                "ai_judge_weight": 0.7,
            },
        }
        config = EvaluationConfig(**data)
        assert config.name == "test-eval"
        assert config.asset_type == "prompt"
        assert len(config.criteria) == 1
        assert config.criteria[0].name == "clarity"
        assert config.scorer_config.type == "composite"

    def test_criteria_defaults(self) -> None:
        data = {
            "name": "minimal",
            "asset_type": "prompt",
            "criteria": [{"name": "quality", "description": "Overall quality"}],
        }
        config = EvaluationConfig(**data)
        assert config.criteria[0].max_score == 10.0
        assert config.criteria[0].rubric == ""


class TestLoadEvaluation:
    def test_load_from_yaml(self, tmp_path: Path) -> None:
        eval_data = {
            "name": "prompt-clarity",
            "asset_type": "prompt",
            "criteria": [
                {"name": "clarity", "description": "Is it clear?", "max_score": 10},
                {
                    "name": "specificity",
                    "description": "Is it specific?",
                    "max_score": 10,
                },
            ],
            "scorer_config": {"type": "composite"},
        }
        path = tmp_path / "eval.yaml"
        path.write_text(yaml.dump(eval_data))

        config = load_evaluation(path)
        assert config.name == "prompt-clarity"
        assert len(config.criteria) == 2

    def test_load_missing_file_raises(self) -> None:
        import pytest
        with pytest.raises(FileNotFoundError):
            load_evaluation(Path("/nonexistent/eval.yaml"))

    def test_validate_no_criteria_raises(self, tmp_path: Path) -> None:
        eval_data = {"name": "empty", "asset_type": "prompt", "criteria": []}
        path = tmp_path / "eval.yaml"
        path.write_text(yaml.dump(eval_data))

        import pytest
        with pytest.raises(ValueError, match="at least one criterion"):
            load_evaluation(path)
