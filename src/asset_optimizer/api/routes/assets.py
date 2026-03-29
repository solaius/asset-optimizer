"""Asset image serving routes."""

import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from asset_optimizer.api.deps import get_repository
from asset_optimizer.storage.repository import Repository

router = APIRouter(prefix="/api/v1/assets", tags=["assets"])

RepoDep = Annotated[Repository, Depends(get_repository)]


@router.get("/{asset_version_id}/image")
async def get_asset_image(
    asset_version_id: uuid.UUID,
    repo: RepoDep,
) -> FileResponse:
    """Serve the image file for an asset version."""
    asset_version = await repo.get_asset_version(asset_version_id)
    if asset_version is None or not asset_version.file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset image not found",
        )

    file_path = Path(asset_version.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found on disk",
        )

    image_format = asset_version.metadata_.get("image_format", "png")
    media_type = f"image/{image_format}"

    return FileResponse(path=file_path, media_type=media_type)
