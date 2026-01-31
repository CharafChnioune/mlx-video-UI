from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from services.video_generator import video_generator
from services.gallery_service import GalleryService
from datetime import datetime

router = APIRouter()
_gallery = GalleryService(video_generator.output_dir)


@router.get("/gallery")
async def list_gallery():
    videos = _gallery.list_videos()
    for v in videos:
        try:
            mtime = Path(v["path"]).stat().st_mtime
            v["created_at"] = datetime.fromtimestamp(mtime).isoformat()
        except Exception:
            v["created_at"] = datetime.utcnow().isoformat()
    return {"videos": videos}


@router.delete("/gallery/{video_id}")
async def delete_video(video_id: str):
    success = _gallery.delete_video(video_id)
    if not success:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"message": "Deleted"}


@router.get("/thumbnails/{filename}")
async def get_thumbnail(filename: str):
    thumb = _gallery.get_thumbnail(filename)
    if not thumb or not thumb.exists():
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(path=str(thumb), media_type="image/jpeg", filename=thumb.name)
