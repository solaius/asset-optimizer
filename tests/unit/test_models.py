import uuid
from datetime import UTC, datetime

from asset_optimizer.storage.models import (
    AssetVersion,
    AssetVersionRole,
    Evaluation,
    Experiment,
    ExperimentStatus,
    Iteration,
    IterationStatus,
    Score,
    ScorerType,
)


def test_experiment_model_fields() -> None:
    exp_id = uuid.uuid4()
    eval_id = uuid.uuid4()
    now = datetime.now(UTC)
    exp = Experiment(
        id=exp_id,
        name="Test Experiment",
        description="A test",
        asset_type="prompt",
        evaluation_id=eval_id,
        provider_config={"text": {"default": "openai"}},
        status=ExperimentStatus.PENDING,
        config={"max_iterations": 10},
        best_score=None,
        created_at=now,
        updated_at=now,
    )
    assert exp.name == "Test Experiment"
    assert exp.status == ExperimentStatus.PENDING
    assert exp.asset_type == "prompt"


def test_iteration_model_fields() -> None:
    it = Iteration(
        id=uuid.uuid4(),
        experiment_id=uuid.uuid4(),
        number=1,
        status=IterationStatus.IMPROVED,
        strategy_used="default",
        improvement_prompt="Improve clarity",
        feedback="Better structure",
        created_at=datetime.now(UTC),
        duration_ms=1500,
    )
    assert it.number == 1
    assert it.status == IterationStatus.IMPROVED


def test_asset_version_model_fields() -> None:
    av = AssetVersion(
        id=uuid.uuid4(),
        iteration_id=uuid.uuid4(),
        role=AssetVersionRole.OUTPUT,
        content="Improved prompt text",
        file_path=None,
        metadata_={},
        created_at=datetime.now(UTC),
    )
    assert av.role == AssetVersionRole.OUTPUT
    assert av.content == "Improved prompt text"


def test_evaluation_model_fields() -> None:
    ev = Evaluation(
        id=uuid.uuid4(),
        name="prompt-clarity",
        asset_type="prompt",
        criteria=[{"name": "clarity", "max_score": 10}],
        scorer_config={"type": "composite"},
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    assert ev.name == "prompt-clarity"
    assert len(ev.criteria) == 1


def test_score_model_fields() -> None:
    sc = Score(
        id=uuid.uuid4(),
        iteration_id=uuid.uuid4(),
        criterion_name="clarity",
        value=7.5,
        max_value=10.0,
        scorer_type=ScorerType.AI_JUDGE,
        details={"reasoning": "Clear and specific"},
        created_at=datetime.now(UTC),
    )
    assert sc.value == 7.5
    assert sc.scorer_type == ScorerType.AI_JUDGE


def test_experiment_status_enum() -> None:
    assert ExperimentStatus.PENDING.value == "pending"
    assert ExperimentStatus.RUNNING.value == "running"
    assert ExperimentStatus.COMPLETED.value == "completed"
    assert ExperimentStatus.FAILED.value == "failed"
    assert ExperimentStatus.CANCELLED.value == "cancelled"
    assert ExperimentStatus.PAUSED.value == "paused"


def test_iteration_status_enum() -> None:
    assert IterationStatus.RUNNING.value == "running"
    assert IterationStatus.IMPROVED.value == "improved"
    assert IterationStatus.NO_IMPROVEMENT.value == "no_improvement"
    assert IterationStatus.ERROR.value == "error"
