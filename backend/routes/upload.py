from fastapi import APIRouter, HTTPException, UploadFile, File
from pathlib import Path
import uuid
import aiofiles

from models.schemas import UploadResponse
from services.video_generator import video_generator

router = APIRouter()

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime", "video/x-msvideo"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


@router.post("/upload/image", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """Upload a conditioning image."""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )

    # Generate unique filename
    ext = Path(file.filename).suffix if file.filename else ".png"
    filename = f"img_{uuid.uuid4().hex[:8]}{ext}"
    file_path = video_generator.upload_dir / filename

    # Read and save file
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 100MB)")

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return UploadResponse(path=str(file_path), filename=filename)


@router.post("/upload/video", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """Upload a conditioning video."""
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_VIDEO_TYPES)}"
        )

    # Generate unique filename
    ext = Path(file.filename).suffix if file.filename else ".mp4"
    filename = f"vid_{uuid.uuid4().hex[:8]}{ext}"
    file_path = video_generator.upload_dir / filename

    # Read and save file
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 100MB)")

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return UploadResponse(path=str(file_path), filename=filename)
