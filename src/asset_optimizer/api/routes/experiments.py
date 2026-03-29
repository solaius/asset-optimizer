"""Experiment CRUD routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from asset_optimizer.api.deps import get_repository
from asset_optimizer.api.schemas import ExperimentCreate, ExperimentResponse
from asset_optimizer.storage.models import Experiment, ExperimentStatus
from asset_optimizer.storage.repository import Repository

router = APIRouter(prefix="/api/v1/experiments", tags=["experiments"])

RepoDep = Annotated[Repository, Depends(get_repository)]


def _to_response(experiment: Experiment) -> ExperimentResponse:
    return ExperimentResponse(
        id=str(experiment.id),
        name=experiment.name,
        description=experiment.description or "",
        asset_type=experiment.asset_type,
        evaluation_id=str(experiment.evaluation_id),
        status=str(experiment.status),
        config=experiment.config,
        best_score=experiment.best_score,
        created_at=experiment.created_at.isoformat(),
        updated_at=experiment.updated_at.isoformat(),
    )


@router.post(
    "",
    response_model=ExperimentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_experiment(
    body: ExperimentCreate, repo: RepoDep
) -> ExperimentResponse:
    """Create a new experiment."""
    experiment = Experiment(
        name=body.name,
        description=body.description or None,
        asset_type=body.asset_type,
        evaluation_id=uuid.UUID(body.evaluation_id),
        provider_config=body.provider_config,
        config=body.config,
    )
    created = await repo.create_experiment(experiment)
    return _to_response(created)


@router.get("", response_model=list[ExperimentResponse])
async def list_experiments(
    repo: RepoDep,
    exp_status: ExperimentStatus | None = None,
    asset_type: str | None = None,
) -> list[ExperimentResponse]:
    """List all experiments with optional filters."""
    experiments = await repo.list_experiments(
        status=exp_status, asset_type=asset_type
    )
    return [_to_response(e) for e in experiments]


@router.get("/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(
    experiment_id: uuid.UUID, repo: RepoDep
) -> ExperimentResponse:
    """Get a single experiment by ID."""
    experiment = await repo.get_experiment(experiment_id)
    if experiment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found",
        )
    return _to_response(experiment)


@router.delete("/{experiment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experiment(
    experiment_id: uuid.UUID, repo: RepoDep
) -> None:
    """Delete an experiment by ID."""
    deleted = await repo.delete_experiment(experiment_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found",
        )
