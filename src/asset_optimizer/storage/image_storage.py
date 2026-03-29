"""Image file storage — write, read, and delete image artifacts on disk."""

from __future__ import annotations

import shutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import uuid
    from pathlib import Path


class ImageStorage:
    """Manages image files stored in experiment-scoped directories.

    Directory layout::

        {base_dir}/{experiment_id}/{iteration_number}.{format}
    """

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir

    def _experiment_dir(self, experiment_id: uuid.UUID) -> Path:
        return self.base_dir / str(experiment_id)

    def _image_path(
        self, experiment_id: uuid.UUID, iteration_number: int, image_format: str
    ) -> Path:
        filename = f"{iteration_number}.{image_format}"
        return self._experiment_dir(experiment_id) / filename

    def save(
        self,
        experiment_id: uuid.UUID,
        iteration_number: int,
        image_data: bytes,
        image_format: str,
    ) -> Path:
        """Write image bytes to disk. Returns the file path."""
        path = self._image_path(experiment_id, iteration_number, image_format)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(image_data)
        return path

    def load(
        self,
        experiment_id: uuid.UUID,
        iteration_number: int,
        image_format: str,
    ) -> bytes:
        """Read image bytes from disk."""
        path = self._image_path(experiment_id, iteration_number, image_format)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")
        return path.read_bytes()

    def load_from_path(self, path: Path) -> bytes:
        """Read image bytes from an arbitrary path."""
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")
        return path.read_bytes()

    def delete_experiment(self, experiment_id: uuid.UUID) -> None:
        """Delete all images for an experiment."""
        exp_dir = self._experiment_dir(experiment_id)
        if exp_dir.exists():
            shutil.rmtree(exp_dir)
