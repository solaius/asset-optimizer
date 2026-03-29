"""Tests for image file storage helper."""

from __future__ import annotations

import uuid

import pytest

from asset_optimizer.storage.image_storage import ImageStorage


class TestImageStorage:
    def test_save_image(self, tmp_path) -> None:
        storage = ImageStorage(base_dir=tmp_path / "data" / "images")
        experiment_id = uuid.uuid4()
        path = storage.save(
            experiment_id=experiment_id,
            iteration_number=1,
            image_data=b"fake-png-data",
            image_format="png",
        )
        assert path.exists()
        assert path.read_bytes() == b"fake-png-data"
        assert path.name == "1.png"
        assert path.parent.name == str(experiment_id)

    def test_save_creates_directory(self, tmp_path) -> None:
        storage = ImageStorage(base_dir=tmp_path / "data" / "images")
        experiment_id = uuid.uuid4()
        path = storage.save(
            experiment_id=experiment_id,
            iteration_number=3,
            image_data=b"data",
            image_format="jpg",
        )
        assert path.parent.exists()
        assert path.name == "3.jpg"

    def test_load_image(self, tmp_path) -> None:
        storage = ImageStorage(base_dir=tmp_path / "data" / "images")
        experiment_id = uuid.uuid4()
        storage.save(experiment_id, 1, b"test-data", "png")
        data = storage.load(experiment_id, 1, "png")
        assert data == b"test-data"

    def test_load_missing_raises(self, tmp_path) -> None:
        storage = ImageStorage(base_dir=tmp_path / "data" / "images")
        with pytest.raises(FileNotFoundError):
            storage.load(uuid.uuid4(), 99, "png")

    def test_delete_experiment_images(self, tmp_path) -> None:
        storage = ImageStorage(base_dir=tmp_path / "data" / "images")
        experiment_id = uuid.uuid4()
        storage.save(experiment_id, 1, b"data1", "png")
        storage.save(experiment_id, 2, b"data2", "png")
        storage.delete_experiment(experiment_id)
        assert not (tmp_path / "data" / "images" / str(experiment_id)).exists()

    def test_delete_nonexistent_experiment_is_noop(self, tmp_path) -> None:
        storage = ImageStorage(base_dir=tmp_path / "data" / "images")
        storage.delete_experiment(uuid.uuid4())  # should not raise

    def test_load_from_path(self, tmp_path) -> None:
        storage = ImageStorage(base_dir=tmp_path / "data" / "images")
        experiment_id = uuid.uuid4()
        path = storage.save(experiment_id, 1, b"path-data", "png")
        data = storage.load_from_path(path)
        assert data == b"path-data"
