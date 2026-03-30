"""Pydantic models for API request/response serialization."""

from typing import Any

from pydantic import BaseModel


class CriterionCreate(BaseModel):
    name: str
    description: str
    max_score: float = 10.0
    rubric: str = ""


class EvaluationCreate(BaseModel):
    name: str
    asset_type: str
    description: str = ""
    criteria: list[CriterionCreate]
    scorer_config: dict[str, Any] = {}


class EvaluationResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: str
    asset_type: str
    description: str
    criteria: list[dict[str, Any]]
    scorer_config: dict[str, Any]
    created_at: str
    updated_at: str


class ExperimentCreate(BaseModel):
    name: str
    description: str = ""
    asset_type: str
    evaluation_id: str
    provider_config: dict[str, Any] = {}
    config: dict[str, Any] = {}


class ExperimentResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: str
    description: str
    asset_type: str
    evaluation_id: str
    status: str
    config: dict[str, Any]
    best_score: float | None
    created_at: str
    updated_at: str


class IterationResponse(BaseModel):
    id: str
    experiment_id: str
    number: int
    status: str
    strategy_used: str
    improvement_prompt: str | None
    feedback: str | None
    duration_ms: int | None
    created_at: str


class ScoreResponse(BaseModel):
    criterion_name: str
    value: float
    max_value: float
    scorer_type: str
    details: dict[str, Any]


class AssetVersionResponse(BaseModel):
    id: str
    role: str
    content: str | None
    file_path: str | None
    metadata: dict[str, Any]


class IterationDetailResponse(BaseModel):
    id: str
    experiment_id: str
    number: int
    status: str
    strategy_used: str
    improvement_prompt: str | None
    feedback: str | None
    duration_ms: int | None
    created_at: str
    scores: list[ScoreResponse]
    asset_versions: list[AssetVersionResponse]


class HealthResponse(BaseModel):
    status: str
    version: str
