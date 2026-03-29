"""Data access layer — all database operations go through this class."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import select

from asset_optimizer.storage.models import (
    AssetVersion,
    Evaluation,
    Experiment,
    ExperimentStatus,
    Iteration,
    Score,
)

if TYPE_CHECKING:
    import uuid

    from sqlalchemy.ext.asyncio import AsyncSession


class Repository:
    """Unified data access layer for all storage operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # --- Evaluations ---

    async def create_evaluation(self, evaluation: Evaluation) -> Evaluation:
        self._session.add(evaluation)
        await self._session.commit()
        await self._session.refresh(evaluation)
        return evaluation

    async def get_evaluation(self, evaluation_id: uuid.UUID) -> Evaluation | None:
        return await self._session.get(Evaluation, evaluation_id)

    async def get_evaluation_by_name(self, name: str) -> Evaluation | None:
        stmt = select(Evaluation).where(Evaluation.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_evaluations(self, asset_type: str | None = None) -> list[Evaluation]:
        stmt = select(Evaluation).order_by(Evaluation.created_at.desc())
        if asset_type:
            stmt = stmt.where(Evaluation.asset_type == asset_type)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_evaluation(self, evaluation: Evaluation) -> Evaluation:
        evaluation.updated_at = datetime.now(UTC)
        await self._session.commit()
        await self._session.refresh(evaluation)
        return evaluation

    async def delete_evaluation(self, evaluation_id: uuid.UUID) -> bool:
        evaluation = await self.get_evaluation(evaluation_id)
        if evaluation is None:
            return False
        await self._session.delete(evaluation)
        await self._session.commit()
        return True

    # --- Experiments ---

    async def create_experiment(self, experiment: Experiment) -> Experiment:
        self._session.add(experiment)
        await self._session.commit()
        await self._session.refresh(experiment)
        return experiment

    async def get_experiment(self, experiment_id: uuid.UUID) -> Experiment | None:
        return await self._session.get(Experiment, experiment_id)

    async def list_experiments(
        self,
        status: ExperimentStatus | None = None,
        asset_type: str | None = None,
    ) -> list[Experiment]:
        stmt = select(Experiment).order_by(Experiment.created_at.desc())
        if status:
            stmt = stmt.where(Experiment.status == status)
        if asset_type:
            stmt = stmt.where(Experiment.asset_type == asset_type)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_experiment_status(
        self, experiment_id: uuid.UUID, status: ExperimentStatus
    ) -> Experiment:
        experiment = await self.get_experiment(experiment_id)
        if experiment is None:
            raise ValueError(f"Experiment {experiment_id} not found")
        experiment.status = status
        experiment.updated_at = datetime.now(UTC)
        await self._session.commit()
        await self._session.refresh(experiment)
        return experiment

    async def update_experiment_best_score(
        self, experiment_id: uuid.UUID, score: float
    ) -> Experiment:
        experiment = await self.get_experiment(experiment_id)
        if experiment is None:
            raise ValueError(f"Experiment {experiment_id} not found")
        experiment.best_score = score
        experiment.updated_at = datetime.now(UTC)
        await self._session.commit()
        await self._session.refresh(experiment)
        return experiment

    async def delete_experiment(self, experiment_id: uuid.UUID) -> bool:
        experiment = await self.get_experiment(experiment_id)
        if experiment is None:
            return False
        await self._session.delete(experiment)
        await self._session.commit()
        return True

    # --- Iterations ---

    async def create_iteration(self, iteration: Iteration) -> Iteration:
        self._session.add(iteration)
        await self._session.commit()
        await self._session.refresh(iteration)
        return iteration

    async def get_iteration(
        self, experiment_id: uuid.UUID, number: int
    ) -> Iteration | None:
        stmt = select(Iteration).where(
            Iteration.experiment_id == experiment_id,
            Iteration.number == number,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_iterations(self, experiment_id: uuid.UUID) -> list[Iteration]:
        stmt = (
            select(Iteration)
            .where(Iteration.experiment_id == experiment_id)
            .order_by(Iteration.number)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_iteration(self, iteration: Iteration) -> Iteration:
        await self._session.commit()
        await self._session.refresh(iteration)
        return iteration

    # --- Asset Versions ---

    async def create_asset_version(self, asset_version: AssetVersion) -> AssetVersion:
        self._session.add(asset_version)
        await self._session.commit()
        await self._session.refresh(asset_version)
        return asset_version

    async def list_asset_versions(self, iteration_id: uuid.UUID) -> list[AssetVersion]:
        stmt = (
            select(AssetVersion)
            .where(AssetVersion.iteration_id == iteration_id)
            .order_by(AssetVersion.role)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # --- Scores ---

    async def create_score(self, score: Score) -> Score:
        self._session.add(score)
        await self._session.commit()
        await self._session.refresh(score)
        return score

    async def list_scores(self, iteration_id: uuid.UUID) -> list[Score]:
        stmt = (
            select(Score)
            .where(Score.iteration_id == iteration_id)
            .order_by(Score.criterion_name)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
