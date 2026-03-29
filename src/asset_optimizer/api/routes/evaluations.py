"""Evaluation CRUD routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from asset_optimizer.api.deps import get_repository
from asset_optimizer.api.schemas import EvaluationCreate, EvaluationResponse
from asset_optimizer.storage.models import Evaluation
from asset_optimizer.storage.repository import Repository

router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])

RepoDep = Annotated[Repository, Depends(get_repository)]


def _to_response(evaluation: Evaluation) -> EvaluationResponse:
    return EvaluationResponse(
        id=str(evaluation.id),
        name=evaluation.name,
        asset_type=evaluation.asset_type,
        description=getattr(evaluation, "description", None) or "",
        criteria=evaluation.criteria,
        scorer_config=evaluation.scorer_config,
        created_at=evaluation.created_at.isoformat(),
        updated_at=evaluation.updated_at.isoformat(),
    )


@router.post(
    "",
    response_model=EvaluationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_evaluation(
    body: EvaluationCreate, repo: RepoDep
) -> EvaluationResponse:
    """Create a new evaluation."""
    criteria = [c.model_dump() for c in body.criteria]
    evaluation = Evaluation(
        name=body.name,
        asset_type=body.asset_type,
        criteria=criteria,
        scorer_config=body.scorer_config,
    )
    created = await repo.create_evaluation(evaluation)
    return _to_response(created)


@router.get("", response_model=list[EvaluationResponse])
async def list_evaluations(
    repo: RepoDep, asset_type: str | None = None
) -> list[EvaluationResponse]:
    """List all evaluations, optionally filtered by asset_type."""
    evaluations = await repo.list_evaluations(asset_type=asset_type)
    return [_to_response(e) for e in evaluations]


@router.get("/{evaluation_id}", response_model=EvaluationResponse)
async def get_evaluation(
    evaluation_id: uuid.UUID, repo: RepoDep
) -> EvaluationResponse:
    """Get a single evaluation by ID."""
    evaluation = await repo.get_evaluation(evaluation_id)
    if evaluation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found",
        )
    return _to_response(evaluation)


@router.delete("/{evaluation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evaluation(
    evaluation_id: uuid.UUID, repo: RepoDep
) -> None:
    """Delete an evaluation by ID."""
    deleted = await repo.delete_evaluation(evaluation_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found",
        )
