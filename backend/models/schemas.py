from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal, List, Dict, Any, Tuple
from enum import Enum


class PipelineType(str, Enum):
    DISTILLED = "distilled"
    DEV = "dev"
    KEYFRAME = "keyframe"
    IC_LORA = "ic_lora"


class TilingMode(str, Enum):
    AUTO = "auto"
    NONE = "none"
    DEFAULT = "default"
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"
    SPATIAL = "spatial"
    TEMPORAL = "temporal"


class ConditioningMode(str, Enum):
    REPLACE = "replace"
    GUIDE = "guide"


class LoraSpec(BaseModel):
    path: str = Field(..., description="Path to LoRA safetensors")
    strength: float = Field(1.0, ge=0, description="LoRA strength")


class GenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Text prompt for video generation")
    negative_prompt: Optional[str] = Field(None, description="Negative prompt (dev pipeline only)")
    output_filename: Optional[str] = Field(None, description="Optional output filename override")
    height: int = Field(512, ge=256, le=4096, description="Video height (divisible by 32)")
    width: int = Field(512, ge=256, le=4096, description="Video width (divisible by 32)")
    num_frames: int = Field(33, ge=9, le=4097, description="Number of frames (1 + 8*k)")
    seed: int = Field(42, ge=0, description="Random seed")
    fps: float = Field(24.0, ge=1, le=60, description="Frames per second")
    pipeline: PipelineType = Field(PipelineType.DISTILLED, description="Pipeline type")
    steps: Optional[int] = Field(40, ge=1, le=200, description="Inference steps (dev pipeline)")
    cfg_scale: Optional[float] = Field(4.0, ge=1, le=20, description="CFG scale (dev pipeline)")
    model_repo: Optional[str] = Field(None, description="HuggingFace model repo or local path")
    text_encoder_repo: Optional[str] = Field(None, description="Text encoder repo or local path")
    checkpoint_path: Optional[str] = Field(None, description="Optional checkpoint path")
    enhance_prompt: bool = Field(False, description="Enable prompt enhancement")
    auto_output_name: bool = Field(False, description="Auto-generate output filename from prompt")
    tiling: TilingMode = Field(TilingMode.AUTO, description="Tiling mode")
    cache_limit_gb: Optional[float] = Field(None, ge=1, le=512, description="Cache limit in GB")
    memory_limit_gb: Optional[float] = Field(None, ge=1, le=1024, description="Memory limit in GB")
    eval_interval: int = Field(2, ge=1, le=1000, description="Evaluate latents every N steps")
    audio: bool = Field(False, description="Enable audio generation")
    stream: bool = Field(False, description="Stream output")
    mem_log: bool = Field(False, description="Enable memory logging")
    clear_cache: bool = Field(False, description="Clear MLX cache after generation")
    conditioning_image: Optional[str] = Field(None, description="Path to conditioning image")
    conditioning_frame_idx: Optional[int] = Field(0, ge=0, description="Conditioning frame index")
    conditioning_strength: Optional[float] = Field(1.0, ge=0, le=1, description="Conditioning strength")
    video_conditioning: Optional[str] = Field(None, description="Path to conditioning video")
    conditioning_mode: Optional[ConditioningMode] = Field(ConditioningMode.GUIDE, description="Conditioning mode")
    loras: List[LoraSpec] = Field(default_factory=list, description="LoRA list")
    distilled_loras: List[LoraSpec] = Field(default_factory=list, description="Stage-2 distilled LoRAs")
    extra_args: Optional[List[str]] = Field(default=None, description="Extra CLI args for mlx_video.generate")

    @model_validator(mode="after")
    def _validate_prompt_enhancers(self):
        if self.text_encoder_repo is not None and not self.text_encoder_repo.strip():
            self.text_encoder_repo = None
        if self.output_filename is not None and not self.output_filename.strip():
            self.output_filename = None
        if self.pipeline == PipelineType.IC_LORA and not self.video_conditioning:
            raise ValueError("ic_lora pipeline requires video_conditioning")
        if self.pipeline == PipelineType.KEYFRAME and not self.conditioning_image:
            raise ValueError("keyframe pipeline requires conditioning_image")
        return self


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
    download_progress: Optional[float] = None
    download_step: Optional[str] = None
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
    download_progress: Optional[float] = None
    download_step: Optional[str] = None
    output_path: Optional[str] = None
    error: Optional[str] = None


# =====================
# TRAINING SCHEMAS
# =====================


class TrainingRequest(BaseModel):
    model_repo: str = Field("Lightricks/LTX-2", description="Base model repo or local path")
    pipeline: Literal["dev", "distilled"] = "dev"
    training_mode: Literal["lora", "full"] = "lora"
    strategy: Literal["text_to_video", "video_to_video", "ic_lora"] = "text_to_video"
    with_audio: bool = False
    first_frame_conditioning_p: float = 0.1

    lora_rank: int = 64
    lora_alpha: float = 64.0
    lora_dropout: float = 0.0
    lora_target_modules: List[str] = Field(default_factory=list)

    learning_rate: float = 5e-4
    steps: int = 3000
    batch_size: int = 1
    gradient_accumulation_steps: int = 1
    max_grad_norm: float = 1.0
    optimizer_type: str = "adamw"
    scheduler_type: str = "linear"
    scheduler_params: Dict[str, Any] = Field(default_factory=dict)
    enable_gradient_checkpointing: bool = False

    data_root: str = Field(..., description="Path to preprocessed dataset root")
    data_sources: Optional[Dict[str, str]] = None
    num_dataloader_workers: int = 0

    mixed_precision_mode: Literal["no", "fp16", "bf16"] = "bf16"
    quantization: Optional[str] = None
    load_text_encoder_in_8bit: bool = False

    checkpoint_interval: int = 250
    keep_last_n_checkpoints: int = 3
    checkpoint_precision: Literal["float32", "bfloat16"] = "bfloat16"

    validation_prompts: List[str] = Field(default_factory=list)
    validation_interval: Optional[int] = 100
    validation_video_dims: Tuple[int, int, int] = (512, 512, 33)
    validation_seed: int = 42
    validation_inference_steps: int = 50
    validation_guidance_scale: float = 4.0
    validation_fps: float = 24.0
    skip_initial_validation: bool = False
    validation_images: Optional[List[str]] = None
    validation_reference_videos: Optional[List[str]] = None

    output_dir: str = "./training_output"
    seed: int = 42
    log_every: int = 1
    wandb_enabled: bool = False
    wandb_project: str = "ltx-trainer"
    wandb_entity: Optional[str] = None
    wandb_tags: Optional[List[str]] = None
    wandb_log_validation: bool = True
    hub_push: bool = False
    hub_model_id: Optional[str] = None
    debug: bool = False


class TrainingStatus(str, Enum):
    PENDING = "pending"
    TRAINING = "training"
    COMPLETED = "completed"
    ERROR = "error"
    STOPPED = "stopped"


class TrainingResponse(BaseModel):
    job_id: str
    status: TrainingStatus


class TrainingStatusResponse(BaseModel):
    job_id: str
    status: TrainingStatus
    step: Optional[int] = None
    total_steps: Optional[int] = None
    loss: Optional[float] = None
    eta: Optional[str] = None
    checkpoint_path: Optional[str] = None
    error: Optional[str] = None


class TrainingProgressUpdate(BaseModel):
    type: Literal["progress", "validation", "checkpoint", "complete", "error"]
    job_id: str
    step: Optional[int] = None
    total_steps: Optional[int] = None
    loss: Optional[float] = None
    eta: Optional[str] = None
    checkpoint_path: Optional[str] = None
    validation_video: Optional[str] = None
    error: Optional[str] = None


# =====================
# SYSTEM / HARDWARE
# =====================


class HardwareInfo(BaseModel):
    platform: str
    cpu: str
    cores: int
    memory_gb: float
    is_apple_silicon: bool
    mlx_version: Optional[str] = None
    python_version: str


class DefaultSettings(BaseModel):
    generation: Dict[str, Any]
    training: Dict[str, Any]
