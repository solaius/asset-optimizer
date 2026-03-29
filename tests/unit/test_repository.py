import uuid

import pytest

from asset_optimizer.storage.database import (
    create_engine_from_config,
    get_session_factory,
)
from asset_optimizer.storage.models import (
    Evaluation,
    Experiment,
    ExperimentStatus,
    Iteration,
    IterationStatus,
    Score,
    ScorerType,
)
from asset_optimizer.storage.repository import Repository


@pytest.fixture
async def repo(tmp_path):
    db_path = tmp_path / "test.db"
    engine = create_engine_from_config("sqlite", sqlite_path=db_path)
    session_factory = get_session_factory(engine)

    from asset_optimizer.storage.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        yield Repository(session)

    await engine.dispose()


async def test_create_and_get_evaluation(repo: Repository) -> None:
    evaluation = Evaluation(
        name="test-eval",
        asset_type="prompt",
        criteria=[{"name": "clarity", "max_score": 10}],
        scorer_config={"type": "composite"},
    )
    created = await repo.create_evaluation(evaluation)
    assert created.id is not None

    fetched = await repo.get_evaluation(created.id)
    assert fetched is not None
    assert fetched.name == "test-eval"


async def test_list_evaluations(repo: Repository) -> None:
    for i in range(3):
        await repo.create_evaluation(
            Evaluation(
                name=f"eval-{i}",
                asset_type="prompt",
                criteria=[],
                scorer_config={},
            )
        )
    evaluations = await repo.list_evaluations()
    assert len(evaluations) == 3


async def test_create_and_get_experiment(repo: Repository) -> None:
    eval_id = uuid.uuid4()
    experiment = Experiment(
        name="test-exp",
        asset_type="prompt",
        evaluation_id=eval_id,
        config={"max_iterations": 10},
    )
    created = await repo.create_experiment(experiment)
    assert created.status == ExperimentStatus.PENDING

    fetched = await repo.get_experiment(created.id)
    assert fetched is not None
    assert fetched.name == "test-exp"


async def test_update_experiment_status(repo: Repository) -> None:
    experiment = Experiment(
        name="status-test",
        asset_type="prompt",
        evaluation_id=uuid.uuid4(),
    )
    created = await repo.create_experiment(experiment)
    updated = await repo.update_experiment_status(
        created.id, ExperimentStatus.RUNNING
    )
    assert updated.status == ExperimentStatus.RUNNING


async def test_list_experiments_with_status_filter(repo: Repository) -> None:
    statuses = [
        ExperimentStatus.PENDING,
        ExperimentStatus.RUNNING,
        ExperimentStatus.PENDING,
    ]
    for i, status in enumerate(statuses):
        exp = Experiment(
            name=f"exp-{i}",
            asset_type="prompt",
            evaluation_id=uuid.uuid4(),
            status=status,
        )
        await repo.create_experiment(exp)

    pending = await repo.list_experiments(status=ExperimentStatus.PENDING)
    assert len(pending) == 2

    running = await repo.list_experiments(status=ExperimentStatus.RUNNING)
    assert len(running) == 1


async def test_create_and_list_iterations(repo: Repository) -> None:
    exp_id = uuid.uuid4()
    for i in range(3):
        await repo.create_iteration(
            Iteration(
                experiment_id=exp_id,
                number=i + 1,
                status=IterationStatus.IMPROVED,
            )
        )
    iterations = await repo.list_iterations(exp_id)
    assert len(iterations) == 3
    assert iterations[0].number == 1


async def test_create_and_list_scores(repo: Repository) -> None:
    iter_id = uuid.uuid4()
    await repo.create_score(
        Score(
            iteration_id=iter_id,
            criterion_name="clarity",
            value=7.5,
            max_value=10.0,
            scorer_type=ScorerType.AI_JUDGE,
        )
    )
    await repo.create_score(
        Score(
            iteration_id=iter_id,
            criterion_name="specificity",
            value=6.0,
            max_value=10.0,
            scorer_type=ScorerType.HEURISTIC,
        )
    )
    scores = await repo.list_scores(iter_id)
    assert len(scores) == 2
