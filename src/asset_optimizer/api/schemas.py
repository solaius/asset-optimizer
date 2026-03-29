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


class HealthResponse(BaseModel):
    status: str
    version: str
