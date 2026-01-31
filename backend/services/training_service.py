import asyncio
import os
import re
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Callable, Dict, Any

from models.schemas import TrainingRequest, TrainingStatus


@dataclass
class TrainingJob:
    id: str
    status: TrainingStatus
    request: TrainingRequest
    step: int = 0
    total_steps: int = 0
    loss: Optional[float] = None
    eta: Optional[str] = None
    checkpoint_path: Optional[str] = None
    error: Optional[str] = None
    process: Optional[asyncio.subprocess.Process] = None


class TrainingService:
    def __init__(self):
        self.jobs: Dict[str, TrainingJob] = {}
        self._progress_callbacks: Dict[str, Callable] = {}
        self._repo_root = Path(__file__).resolve().parents[3]

    def register_progress_callback(self, job_id: str, callback: Callable):
        self._progress_callbacks[job_id] = callback

    def unregister_progress_callback(self, job_id: str):
        self._progress_callbacks.pop(job_id, None)

    async def _notify_progress(self, job_id: str, update: dict):
        if job_id in self._progress_callbacks:
            callback = self._progress_callbacks[job_id]
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(update)
                else:
                    callback(update)
            except Exception as e:
                print(f"Error in progress callback: {e}")

    def _build_config(self, request: TrainingRequest, config_path: Path) -> None:
        try:
            import yaml
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("PyYAML is required to build training configs.") from exc

        validation_width, validation_height, validation_frames = request.validation_video_dims
        cfg: Dict[str, Any] = {
            "pipeline": request.pipeline,
            "seed": request.seed,
            "output_dir": request.output_dir,
            "log_every": request.log_every,
            "model": {
                "model_path": request.model_repo,
                "training_mode": request.training_mode,
            },
            "training_strategy": {
                "name": request.strategy,
                "with_audio": request.with_audio,
                "first_frame_conditioning_p": request.first_frame_conditioning_p,
            },
            "lora": {
                "rank": request.lora_rank,
                "alpha": request.lora_alpha,
                "dropout": request.lora_dropout,
                "target_modules": request.lora_target_modules or None,
            },
            "optimization": {
                "learning_rate": request.learning_rate,
                "steps": request.steps,
                "batch_size": request.batch_size,
                "gradient_accumulation_steps": request.gradient_accumulation_steps,
                "max_grad_norm": request.max_grad_norm,
                "optimizer_type": request.optimizer_type,
                "scheduler_type": request.scheduler_type,
                "scheduler_params": request.scheduler_params or {},
                "enable_gradient_checkpointing": request.enable_gradient_checkpointing,
            },
            "data": {
                "preprocessed_data_root": request.data_root,
                "data_sources": request.data_sources,
                "num_dataloader_workers": request.num_dataloader_workers,
            },
            "checkpoints": {
                "interval": request.checkpoint_interval,
                "keep_last_n": request.keep_last_n_checkpoints,
            },
            "validation": {
                "prompts": request.validation_prompts or None,
                "interval": request.validation_interval or 0,
                "width": validation_width,
                "height": validation_height,
                "num_frames": validation_frames,
                "seed": request.validation_seed,
                "steps": request.validation_inference_steps,
                "cfg_scale": request.validation_guidance_scale,
                "fps": request.validation_fps,
                "negative_prompt": "worst quality, inconsistent motion, blurry, jittery, distorted",
                "skip_initial_validation": request.skip_initial_validation,
                "images": request.validation_images,
                "reference_videos": request.validation_reference_videos,
            },
            "acceleration": {
                "mixed_precision_mode": request.mixed_precision_mode,
                "load_text_encoder_in_8bit": request.load_text_encoder_in_8bit,
                "quantization": request.quantization,
            },
            "wandb": {
                "enabled": request.wandb_enabled,
                "project": request.wandb_project,
                "entity": request.wandb_entity,
                "tags": request.wandb_tags,
                "log_validation_videos": request.wandb_log_validation,
            },
            "hub": {
                "push_to_hub": request.hub_push,
                "hub_model_id": request.hub_model_id,
            },
        }

        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(yaml.safe_dump(cfg, sort_keys=False))

    def _parse_progress(self, line: str) -> Dict[str, Any]:
        update: Dict[str, Any] = {}
        step_match = re.search(r"step\s+(\d+)\s*:\s*loss=([0-9eE.+-]+)", line)
        if step_match:
            update["step"] = int(step_match.group(1))
            update["loss"] = float(step_match.group(2))
            return update

        val_match = re.search(r"Validation @ step\s+(\d+)", line)
        if val_match:
            update["validation"] = int(val_match.group(1))
            return update

        ckpt_match = re.search(r"Saved checkpoint:\s*(.*)", line)
        if ckpt_match:
            update["checkpoint_path"] = ckpt_match.group(1).strip()
            return update

        return update

    async def start_training(self, request: TrainingRequest) -> str:
        job_id = str(uuid.uuid4())
        job = TrainingJob(
            id=job_id,
            status=TrainingStatus.PENDING,
            request=request,
            total_steps=request.steps,
        )
        self.jobs[job_id] = job
        asyncio.create_task(self._run_training(job_id))
        return job_id

    async def _run_training(self, job_id: str) -> None:
        job = self.jobs.get(job_id)
        if not job:
            return

        try:
            job.status = TrainingStatus.TRAINING
            await self._notify_progress(job_id, {
                "type": "progress",
                "job_id": job_id,
                "step": 0,
                "total_steps": job.total_steps,
            })

            output_dir = Path(job.request.output_dir)
            config_path = output_dir / f"training_config_{job_id[:8]}.yaml"
            self._build_config(job.request, config_path)

            cmd = [
                sys.executable,
                "-m",
                "mlx_video.mlx_trainer.trainer",
                "--config",
                str(config_path),
            ]
            if job.request.debug:
                cmd.append("--debug")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env={
                    **os.environ,
                    "PYTHONUNBUFFERED": "1",
                    "PYTHONPATH": os.pathsep.join(
                        [
                            str(self._repo_root / "mlx-video"),
                            os.environ.get("PYTHONPATH", ""),
                        ]
                    ).strip(os.pathsep),
                },
            )
            job.process = process

            last_step_time = None
            last_step_ts = None
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                line_str = line.decode("utf-8", errors="ignore").strip()
                if not line_str:
                    continue
                print(f"[mlx-trainer] {line_str}")

                parsed = self._parse_progress(line_str)
                if "step" in parsed:
                    job.step = parsed["step"]
                    job.loss = parsed.get("loss")
                    if last_step_ts is not None:
                        last_step_time = max(0.0, (asyncio.get_event_loop().time() - last_step_ts))
                    last_step_ts = asyncio.get_event_loop().time()
                    if last_step_time is not None and job.total_steps:
                        remaining = max(job.total_steps - job.step, 0)
                        eta_sec = remaining * last_step_time
                        job.eta = f"{int(eta_sec // 60)}m {int(eta_sec % 60)}s"
                    await self._notify_progress(job_id, {
                        "type": "progress",
                        "job_id": job_id,
                        "step": job.step,
                        "total_steps": job.total_steps,
                        "loss": job.loss,
                        "eta": job.eta,
                    })
                if "validation" in parsed:
                    await self._notify_progress(job_id, {
                        "type": "validation",
                        "job_id": job_id,
                        "step": parsed["validation"],
                    })
                if "checkpoint_path" in parsed:
                    job.checkpoint_path = parsed["checkpoint_path"]
                    await self._notify_progress(job_id, {
                        "type": "checkpoint",
                        "job_id": job_id,
                        "checkpoint_path": job.checkpoint_path,
                    })

            await process.wait()
            if process.returncode == 0:
                job.status = TrainingStatus.COMPLETED
                await self._notify_progress(job_id, {
                    "type": "complete",
                    "job_id": job_id,
                })
            else:
                job.status = TrainingStatus.ERROR
                job.error = f"Training failed with return code {process.returncode}"
                await self._notify_progress(job_id, {
                    "type": "error",
                    "job_id": job_id,
                    "error": job.error,
                })

        except Exception as exc:
            job.status = TrainingStatus.ERROR
            job.error = str(exc)
            await self._notify_progress(job_id, {
                "type": "error",
                "job_id": job_id,
                "error": job.error,
            })

    def get_job(self, job_id: str) -> Optional[TrainingJob]:
        return self.jobs.get(job_id)

    async def stop_training(self, job_id: str) -> bool:
        job = self.jobs.get(job_id)
        if job and job.process:
            job.process.terminate()
            job.status = TrainingStatus.STOPPED
            return True
        return False


training_service = TrainingService()
