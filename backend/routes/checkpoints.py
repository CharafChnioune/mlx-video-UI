from fastapi import APIRouter
from pathlib import Path

router = APIRouter()


@router.get("/checkpoints")
async def list_checkpoints():
    repo_root = Path(__file__).resolve().parents[3]
    candidates = [repo_root / "checkpoints", repo_root / "training_output", repo_root / "mlx-video" / "checkpoints"]
    found = []
    for base in candidates:
        if not base.exists():
            continue
        for path in base.rglob("*.safetensors"):
            found.append(str(path))
    return {"checkpoints": sorted(found)}
