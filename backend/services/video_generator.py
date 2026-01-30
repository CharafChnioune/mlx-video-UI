import asyncio
import subprocess
import sys
import uuid
import os
import json
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import re

from models.schemas import GenerationRequest, JobStatus


@dataclass
class Job:
    id: str
    status: JobStatus
    request: GenerationRequest
    progress: float = 0.0
    current_step: str = ""
    output_path: Optional[str] = None
    error: Optional[str] = None
    process: Optional[asyncio.subprocess.Process] = None


class VideoGeneratorService:
    def __init__(self, output_dir: str = "./outputs", upload_dir: str = "./uploads"):
        self.output_dir = Path(output_dir)
        self.upload_dir = Path(upload_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.jobs: Dict[str, Job] = {}
        self._progress_callbacks: Dict[str, Callable] = {}

    def register_progress_callback(self, job_id: str, callback: Callable):
        """Register a callback for progress updates."""
        self._progress_callbacks[job_id] = callback

    def unregister_progress_callback(self, job_id: str):
        """Unregister a progress callback."""
        self._progress_callbacks.pop(job_id, None)

    async def _notify_progress(self, job_id: str, update: dict):
        """Notify progress callback if registered."""
        if job_id in self._progress_callbacks:
            callback = self._progress_callbacks[job_id]
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(update)
                else:
                    callback(update)
            except Exception as e:
                print(f"Error in progress callback: {e}")

    def _build_command(self, request: GenerationRequest, output_path: str) -> list:
        """Build the mlx-video CLI command."""
        cmd = [
            sys.executable, "-m", "mlx_video",
            "--prompt", request.prompt,
            "--height", str(request.height),
            "--width", str(request.width),
            "--num-frames", str(request.num_frames),
            "--seed", str(request.seed),
            "--fps", str(request.fps),
            "--pipeline", request.pipeline.value,
            "--output", output_path,
        ]

        if request.negative_prompt:
            cmd.extend(["--negative-prompt", request.negative_prompt])

        if request.model_repo:
            cmd.extend(["--model-repo", request.model_repo])

        if request.checkpoint_path:
            cmd.extend(["--checkpoint-path", request.checkpoint_path])

        if request.pipeline.value == "dev":
            if request.steps:
                cmd.extend(["--steps", str(request.steps)])
            if request.cfg_scale:
                cmd.extend(["--cfg-scale", str(request.cfg_scale)])

        if request.enhance_prompt:
            cmd.append("--enhance-prompt")

        if request.tiling:
            cmd.extend(["--tiling", request.tiling.value])

        if request.cache_limit_gb:
            cmd.extend(["--cache-limit-gb", str(request.cache_limit_gb)])

        if request.audio:
            cmd.append("--audio")

        if request.stream:
            cmd.append("--stream")

        if request.conditioning_image:
            cmd.extend(["--image", request.conditioning_image])
            if request.conditioning_frame_idx is not None:
                cmd.extend(["--frame-idx", str(request.conditioning_frame_idx)])
            if request.conditioning_strength is not None:
                cmd.extend(["--strength", str(request.conditioning_strength)])

        if request.video_conditioning:
            cmd.extend(["--video-conditioning", request.video_conditioning])
            if request.conditioning_mode:
                cmd.extend(["--conditioning-mode", request.conditioning_mode.value])

        return cmd

    def _parse_progress(self, line: str) -> tuple[Optional[float], Optional[str]]:
        """Parse progress from mlx-video output."""
        # Look for progress patterns like "Step 10/40" or percentage
        step_match = re.search(r'(?:Step|step)\s+(\d+)\s*/\s*(\d+)', line)
        if step_match:
            current, total = int(step_match.group(1)), int(step_match.group(2))
            progress = (current / total) * 100
            return progress, f"Step {current}/{total}"

        # Look for percentage patterns
        pct_match = re.search(r'(\d+(?:\.\d+)?)\s*%', line)
        if pct_match:
            return float(pct_match.group(1)), None

        # Look for stage indicators
        if "loading" in line.lower():
            return None, "Loading model..."
        if "encoding" in line.lower():
            return None, "Encoding prompt..."
        if "generating" in line.lower() or "sampling" in line.lower():
            return None, "Generating frames..."
        if "saving" in line.lower() or "writing" in line.lower():
            return None, "Saving video..."

        return None, None

    async def start_generation(self, request: GenerationRequest) -> str:
        """Start a video generation job."""
        job_id = str(uuid.uuid4())
        output_filename = f"video_{job_id[:8]}.mp4"
        output_path = str(self.output_dir / output_filename)

        job = Job(
            id=job_id,
            status=JobStatus.PENDING,
            request=request,
            current_step="Initializing..."
        )
        self.jobs[job_id] = job

        # Start generation in background
        asyncio.create_task(self._run_generation(job_id, output_path))

        return job_id

    async def _run_generation(self, job_id: str, output_path: str):
        """Run the video generation process."""
        job = self.jobs.get(job_id)
        if not job:
            return

        try:
            job.status = JobStatus.PROCESSING
            await self._notify_progress(job_id, {
                "type": "status",
                "job_id": job_id,
                "progress": 0,
                "current_step": "Starting generation..."
            })

            cmd = self._build_command(job.request, output_path)

            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env={**os.environ, "PYTHONUNBUFFERED": "1"}
            )
            job.process = process

            # Read output line by line
            last_progress = 0.0
            while True:
                line = await process.stdout.readline()
                if not line:
                    break

                line_str = line.decode('utf-8', errors='ignore').strip()
                if line_str:
                    print(f"[mlx-video] {line_str}")

                    progress, step = self._parse_progress(line_str)
                    if progress is not None:
                        last_progress = progress
                        job.progress = progress
                    if step:
                        job.current_step = step

                    await self._notify_progress(job_id, {
                        "type": "progress",
                        "job_id": job_id,
                        "progress": job.progress,
                        "current_step": job.current_step
                    })

            # Wait for process to complete
            await process.wait()

            if process.returncode == 0 and Path(output_path).exists():
                job.status = JobStatus.COMPLETED
                job.progress = 100
                job.output_path = output_path
                job.current_step = "Complete"

                await self._notify_progress(job_id, {
                    "type": "complete",
                    "job_id": job_id,
                    "progress": 100,
                    "output_path": output_path
                })
            else:
                job.status = JobStatus.ERROR
                job.error = f"Generation failed with return code {process.returncode}"

                await self._notify_progress(job_id, {
                    "type": "error",
                    "job_id": job_id,
                    "error": job.error
                })

        except Exception as e:
            job.status = JobStatus.ERROR
            job.error = str(e)

            await self._notify_progress(job_id, {
                "type": "error",
                "job_id": job_id,
                "error": str(e)
            })

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        return self.jobs.get(job_id)

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job."""
        job = self.jobs.get(job_id)
        if job and job.process:
            job.process.terminate()
            job.status = JobStatus.ERROR
            job.error = "Cancelled by user"
            return True
        return False


# Global service instance
video_generator = VideoGeneratorService()
