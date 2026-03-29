"""FastAPI application factory."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from asset_optimizer.api import deps
from asset_optimizer.api.routes import evaluations, experiments, health, providers


def create_app(db_path: Path | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        engine, session_factory = await deps.init_db(db_path=db_path)
        app.state.engine = engine
        app.state.session_factory = session_factory
        yield
        await deps.close_db(engine)

    app = FastAPI(
        title="Asset Optimizer API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(evaluations.router)
    app.include_router(experiments.router)
    app.include_router(providers.router)

    return app
