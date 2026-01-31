import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any


class GalleryService:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.thumbnail_dir = output_dir / "thumbnails"
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)

    def _ffprobe_duration(self, path: Path) -> float | None:
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    str(path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return float(result.stdout.strip())
        except Exception:
            return None

    def _ensure_thumbnail(self, path: Path) -> Path | None:
        thumb = self.thumbnail_dir / f"{path.stem}.jpg"
        if thumb.exists():
            return thumb
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(path),
                    "-frames:v",
                    "1",
                    "-q:v",
                    "2",
                    str(thumb),
                ],
                capture_output=True,
                check=True,
            )
            return thumb
        except Exception:
            return None

    def list_videos(self) -> List[Dict[str, Any]]:
        videos = []
        for path in sorted(self.output_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True):
            stat = path.stat()
            metadata_path = path.with_suffix(".json")
            metadata = {}
            if metadata_path.exists():
                try:
                    metadata = json.loads(metadata_path.read_text())
                except Exception:
                    metadata = {}
            duration = self._ffprobe_duration(path)
            thumb = self._ensure_thumbnail(path)
            videos.append(
                {
                    "id": path.name,
                    "filename": path.name,
                    "path": str(path),
                    "thumbnail": str(thumb) if thumb else None,
                    "prompt": metadata.get("prompt"),
                    "params": metadata.get("params"),
                    "created_at": stat.st_mtime,
                    "duration": duration,
                    "width": metadata.get("width"),
                    "height": metadata.get("height"),
                    "size": stat.st_size,
                }
            )
        return videos

    def delete_video(self, video_id: str) -> bool:
        path = self.output_dir / video_id
        if not path.exists():
            return False
        path.unlink()
        meta = path.with_suffix(".json")
        if meta.exists():
            meta.unlink()
        thumb = self.thumbnail_dir / f"{path.stem}.jpg"
        if thumb.exists():
            thumb.unlink()
        return True

    def get_thumbnail(self, filename: str) -> Path | None:
        path = self.output_dir / filename
        if not path.exists():
            return None
        return self._ensure_thumbnail(path)
