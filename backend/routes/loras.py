from fastapi import APIRouter
from pathlib import Path

router = APIRouter()


@router.get("/loras")
async def list_loras():
    ui_root = Path(__file__).resolve().parents[2]
    lora_dir = ui_root / "loras"
    items = []
    if lora_dir.exists():
        for path in sorted(lora_dir.rglob("*.safetensors")):
            items.append(
                {
                    "name": path.name,
                    "path": str(path),
                }
            )
    return {"loras": items}
