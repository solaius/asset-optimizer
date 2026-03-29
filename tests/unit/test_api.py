"""Tests for the FastAPI REST API layer."""

from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from asset_optimizer.api.app import create_app


@pytest.fixture
async def client(tmp_path):
    app = create_app(db_path=tmp_path / "test.db")
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


class TestHealthRoutes:
    @pytest.mark.asyncio
    async def test_health(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_readiness(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/health/ready")
        assert resp.status_code == 200


class TestEvaluationRoutes:
    @pytest.mark.asyncio
    async def test_create_evaluation(self, client: AsyncClient) -> None:
        resp = await client.post("/api/v1/evaluations", json={
            "name": "test-eval", "asset_type": "prompt",
            "criteria": [{"name": "clarity", "description": "Is it clear?"}],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "test-eval"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_list_evaluations(self, client: AsyncClient) -> None:
        await client.post("/api/v1/evaluations", json={
            "name": "eval-1", "asset_type": "prompt",
            "criteria": [{"name": "c1", "description": "d1"}],
        })
        resp = await client.get("/api/v1/evaluations")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    @pytest.mark.asyncio
    async def test_get_evaluation(self, client: AsyncClient) -> None:
        create_resp = await client.post("/api/v1/evaluations", json={
            "name": "eval-get", "asset_type": "prompt",
            "criteria": [{"name": "c1", "description": "d1"}],
        })
        eval_id = create_resp.json()["id"]
        resp = await client.get(f"/api/v1/evaluations/{eval_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "eval-get"

    @pytest.mark.asyncio
    async def test_get_evaluation_not_found(self, client: AsyncClient) -> None:
        resp = await client.get(f"/api/v1/evaluations/{uuid.uuid4()}")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_evaluation(self, client: AsyncClient) -> None:
        create_resp = await client.post("/api/v1/evaluations", json={
            "name": "eval-del", "asset_type": "prompt",
            "criteria": [{"name": "c1", "description": "d1"}],
        })
        eval_id = create_resp.json()["id"]
        resp = await client.delete(f"/api/v1/evaluations/{eval_id}")
        assert resp.status_code == 204
        resp = await client.get(f"/api/v1/evaluations/{eval_id}")
        assert resp.status_code == 404


class TestExperimentRoutes:
    @pytest.mark.asyncio
    async def test_create_experiment(self, client: AsyncClient) -> None:
        eval_resp = await client.post("/api/v1/evaluations", json={
            "name": "exp-eval", "asset_type": "prompt",
            "criteria": [{"name": "c1", "description": "d1"}],
        })
        eval_id = eval_resp.json()["id"]
        resp = await client.post("/api/v1/experiments", json={
            "name": "test-exp", "asset_type": "prompt",
            "evaluation_id": eval_id, "config": {"max_iterations": 5},
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "test-exp"
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_list_experiments(self, client: AsyncClient) -> None:
        resp = await client.get("/api/v1/experiments")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


class TestAssetImageRoutes:
    @pytest.mark.asyncio
    async def test_get_image_not_found(self, client: AsyncClient) -> None:
        resp = await client.get(f"/api/v1/assets/{uuid.uuid4()}/image")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_image_serves_file(self, client: AsyncClient, tmp_path) -> None:
        # Create an evaluation + experiment first
        eval_resp = await client.post("/api/v1/evaluations", json={
            "name": "img-eval", "asset_type": "image",
            "criteria": [{"name": "c1", "description": "d1"}],
        })
        eval_id = eval_resp.json()["id"]
        exp_resp = await client.post("/api/v1/experiments", json={
            "name": "img-exp", "asset_type": "image",
            "evaluation_id": eval_id,
        })

        # Write a fake image file
        image_path = tmp_path / "test_image.png"
        image_path.write_bytes(b"\x89PNG\r\n\x1a\nfake-image-data")

        # Create asset version directly via repository
        from asset_optimizer.storage.models import (
            AssetVersion,
            AssetVersionRole,
            Iteration,
            IterationStatus,
        )
        from asset_optimizer.storage.repository import Repository

        app = client._transport.app  # type: ignore[union-attr]
        session_factory = app.state.session_factory
        async with session_factory() as session:
            repo = Repository(session)
            iteration = Iteration(
                experiment_id=uuid.UUID(exp_resp.json()["id"]),
                number=1,
                status=IterationStatus.IMPROVED,
            )
            iteration = await repo.create_iteration(iteration)

            asset_version = AssetVersion(
                iteration_id=iteration.id,
                role=AssetVersionRole.OUTPUT,
                file_path=str(image_path),
                metadata_={"image_format": "png"},
            )
            asset_version = await repo.create_asset_version(asset_version)
            av_id = str(asset_version.id)

        resp = await client.get(f"/api/v1/assets/{av_id}/image")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/png"
        assert b"fake-image-data" in resp.content
