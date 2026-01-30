from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class PipelineType(str, Enum):
    DISTILLED = "distilled"
    DEV = "dev"
    KEYFRAME = "keyframe"
    IC_LORA = "ic_lora"


class TilingMode(str, Enum):
    AUTO = "auto"
    ON = "on"
    OFF = "off"


class ConditioningMode(str, Enum):
    REPLACE = "replace"
    GUIDE = "guide"


class GenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Text prompt for video generation")
    negative_prompt: Optional[str] = Field(None, description="Negative prompt (dev pipeline only)")
    height: int = Field(512, ge=256, le=1024, description="Video height (divisible by 32)")
    width: int = Field(512, ge=256, le=1024, description="Video width (divisible by 32)")
    num_frames: int = Field(33, ge=9, le=97, description="Number of frames (1 + 8*k)")
    seed: int = Field(42, ge=0, description="Random seed")
    fps: float = Field(24.0, ge=1, le=60, description="Frames per second")
    pipeline: PipelineType = Field(PipelineType.DISTILLED, description="Pipeline type")
    steps: Optional[int] = Field(40, ge=1, le=100, description="Inference steps (dev pipeline)")
    cfg_scale: Optional[float] = Field(4.0, ge=1, le=20, description="CFG scale (dev pipeline)")
    model_repo: Optional[str] = Field(None, description="HuggingFace model repo or local path")
    checkpoint_path: Optional[str] = Field(None, description="Optional checkpoint path")
    enhance_prompt: bool = Field(False, description="Enable prompt enhancement")
    tiling: TilingMode = Field(TilingMode.AUTO, description="Tiling mode")
    cache_limit_gb: Optional[int] = Field(32, ge=4, le=256, description="Memory limit in GB")
    audio: bool = Field(False, description="Enable audio generation")
    stream: bool = Field(False, description="Stream output")
    conditioning_image: Optional[str] = Field(None, description="Path to conditioning image")
    conditioning_frame_idx: Optional[int] = Field(0, ge=0, description="Conditioning frame index")
    conditioning_strength: Optional[float] = Field(1.0, ge=0, le=1, description="Conditioning strength")
    video_conditioning: Optional[str] = Field(None, description="Path to conditioning video")
    conditioning_mode: Optional[ConditioningMode] = Field(ConditioningMode.GUIDE, description="Conditioning mode")


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class GenerationResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str = "Job started"


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: Optional[float] = None
    current_step: Optional[str] = None
    output_path: Optional[str] = None
    error: Optional[str] = None


class UploadResponse(BaseModel):
    path: str
    filename: str


class ProgressUpdate(BaseModel):
    type: Literal["progress", "status", "complete", "error"]
    job_id: str
    progress: Optional[float] = None
    current_step: Optional[str] = None
    output_path: Optional[str] = None
    error: Optional[str] = None
