"""Database engine and session factory management."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_engine_from_config(
    backend: str = "sqlite",
    sqlite_path: Path | None = None,
    postgres_url: str | None = None,
) -> AsyncEngine:
    """Create an async SQLAlchemy engine from configuration."""
    if backend == "postgres" and postgres_url:
        url = postgres_url
    else:
        path = sqlite_path or Path("./data/optimizer.db")
        path.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite+aiosqlite:///{path}"

    return create_async_engine(url, echo=False)


def get_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create a session factory bound to the given engine."""
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
