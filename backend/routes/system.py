from fastapi import APIRouter

from models.schemas import HardwareInfo, DefaultSettings
from services.system_info import get_hardware_info, recommended_defaults

router = APIRouter()


@router.get("/system/hardware", response_model=HardwareInfo)
async def system_hardware():
    return get_hardware_info()


@router.get("/system/defaults", response_model=DefaultSettings)
async def system_defaults():
    defaults = recommended_defaults()
    return {"generation": defaults["generation"], "training": defaults["training"]}
