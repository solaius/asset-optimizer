"""SQLAlchemy ORM models for all persistent entities."""

from __future__ import annotations

import enum
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, Enum, Float, Integer, String, Text, Uuid
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    type_annotation_map = {
        dict[str, Any]: JSON,
        list[dict[str, Any]]: JSON,
    }


class ExperimentStatus(enum.StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IterationStatus(enum.StrEnum):
    RUNNING = "running"
    IMPROVED = "improved"
    NO_IMPROVEMENT = "no_improvement"
    ERROR = "error"


class AssetVersionRole(enum.StrEnum):
    INPUT = "input"
    OUTPUT = "output"


class ScorerType(enum.StrEnum):
    HEURISTIC = "heuristic"
    AI_JUDGE = "ai_judge"


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _new_uuid() -> uuid.UUID:
    return uuid.uuid4()


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_new_uuid)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    asset_type: Mapped[str] = mapped_column(String(50))
    evaluation_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    provider_config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[ExperimentStatus] = mapped_column(
        Enum(ExperimentStatus), default=ExperimentStatus.PENDING
    )
    config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    best_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )


class Iteration(Base):
    __tablename__ = "iterations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_new_uuid)
    experiment_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    number: Mapped[int] = mapped_column(Integer)
    status: Mapped[IterationStatus] = mapped_column(Enum(IterationStatus))
    strategy_used: Mapped[str] = mapped_column(String(100), default="default")
    improvement_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)


class AssetVersion(Base):
    __tablename__ = "asset_versions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_new_uuid)
    iteration_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    role: Mapped[AssetVersionRole] = mapped_column(Enum(AssetVersionRole))
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_new_uuid)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    asset_type: Mapped[str] = mapped_column(String(50))
    criteria: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    scorer_config: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_new_uuid)
    iteration_id: Mapped[uuid.UUID] = mapped_column(Uuid)
    criterion_name: Mapped[str] = mapped_column(String(100))
    value: Mapped[float] = mapped_column(Float)
    max_value: Mapped[float] = mapped_column(Float, default=10.0)
    scorer_type: Mapped[ScorerType] = mapped_column(Enum(ScorerType))
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
