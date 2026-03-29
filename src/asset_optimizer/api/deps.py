"""Dependency injection utilities for the FastAPI application."""

from collections.abc import AsyncGenerator
from pathlib import Path

from fastapi import Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from asset_optimizer.storage.database import (
    create_engine_from_config,
    get_session_factory,
)
from asset_optimizer.storage.models import Base
from asset_optimizer.storage.repository import Repository


async def init_db(
    db_path: Path | None = None,
) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """Create the engine, session factory, and all tables."""
    engine = create_engine_from_config(
        backend="sqlite",
        sqlite_path=db_path,
    )
    session_factory = get_session_factory(engine)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine, session_factory


async def close_db(engine: AsyncEngine) -> None:
    """Dispose the given engine on shutdown."""
    await engine.dispose()


async def get_repository(
    request: Request,
) -> AsyncGenerator[Repository, None]:
    """Yield a Repository backed by a fresh database session."""
    session_factory: async_sessionmaker[AsyncSession] = (
        request.app.state.session_factory
    )
    async with session_factory() as session:
        yield Repository(session)
