import asyncio
import sys
import uuid
import os
import json
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
import re
import shutil
import subprocess

from models.schemas import GenerationRequest, JobStatus, LoraSpec


@dataclass
class Job:
    id: str
    status: JobStatus
    request: GenerationRequest
    progress: float = 0.0
    current_step: str = ""
    download_progress: float = 0.0
    download_step: str = ""
    preview_path: Optional[str] = None
    output_path: Optional[str] = None
    error: Optional[str] = None
    process: Optional[asyncio.subprocess.Process] = None


class VideoGeneratorService:
    def __init__(self, output_dir: Optional[str] = None, upload_dir: Optional[str] = None):
        repo_root = Path(__file__).resolve().parents[3]
        ui_root = Path(__file__).resolve().parents[2]
        default_output = ui_root / "outputs"
        default_upload = ui_root / "uploads"
        self.output_dir = Path(output_dir) if output_dir else default_output
        self.upload_dir = Path(upload_dir) if upload_dir else default_upload
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.jobs: Dict[str, Job] = {}
        self._progress_callbacks: Dict[str, Callable] = {}
        self._repo_root = repo_root
        self._python_cmd = self._resolve_python()

    def _resolve_python(self) -> str:
        """Prefer the mlx-video venv python if available."""
        mlx_root = self._repo_root / "mlx-video"
        venv_bin = mlx_root / ".venv" / "bin"
        for candidate in ("python", "python3"):
            path = venv_bin / candidate
            if path.exists():
                return str(path)
        # Fallback to current interpreter
        return sys.executable

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

    def _debug(self, message: str):
        print(f"[mlx-video-ui][debug] {message}", flush=True)

    def _build_command(self, request: GenerationRequest, output_path: str) -> list:
        """Build the mlx-video CLI command (mlx_video.generate)."""
        cmd = [
            self._python_cmd, "-m", "mlx_video.generate",
            "--prompt", request.prompt,
            "--height", str(request.height),
            "--width", str(request.width),
            "--num-frames", str(request.num_frames),
            "--seed", str(request.seed),
            "--fps", str(request.fps),
            "--pipeline", request.pipeline.value,
            "--output-path", output_path,
        ]

        if request.negative_prompt:
            cmd.extend(["--negative-prompt", request.negative_prompt])

        if request.model_repo:
            cmd.extend(["--model-repo", request.model_repo])

        if request.text_encoder_repo and os.environ.get("ALLOW_TEXT_ENCODER_REPO"):
            cmd.extend(["--text-encoder-repo", request.text_encoder_repo])

        if request.checkpoint_path:
            cmd.extend(["--checkpoint-path", request.checkpoint_path])

        if request.pipeline.value == "dev":
            if request.steps:
                cmd.extend(["--steps", str(request.steps)])
            if request.cfg_scale:
                cmd.extend(["--cfg-scale", str(request.cfg_scale)])

        if request.auto_output_name and not request.output_filename:
            cmd.append("--auto-output-name")

        if request.tiling:
            cmd.extend(["--tiling", request.tiling.value])

        if request.cache_limit_gb is not None:
            cmd.extend(["--cache-limit-gb", str(request.cache_limit_gb)])
        if request.memory_limit_gb is not None:
            cmd.extend(["--memory-limit-gb", str(request.memory_limit_gb)])
        if request.eval_interval:
            cmd.extend(["--eval-interval", str(request.eval_interval)])
        if request.mem_log:
            cmd.append("--mem-log")
        if request.clear_cache:
            cmd.append("--clear-cache")

        if request.audio:
            cmd.append("--audio")

        if request.stream:
            cmd.append("--stream")

        if request.conditioning_image:
            frame_idx = request.conditioning_frame_idx or 0
            strength = request.conditioning_strength if request.conditioning_strength is not None else 1.0
            cmd.extend(["--image", request.conditioning_image, str(frame_idx), str(strength)])
            if request.conditioning_mode:
                cmd.extend(["--conditioning-mode", request.conditioning_mode.value])

        if request.video_conditioning:
            frame_idx = request.conditioning_frame_idx or 0
            strength = request.conditioning_strength if request.conditioning_strength is not None else 1.0
            cmd.extend(["--video-conditioning", request.video_conditioning, str(frame_idx), str(strength)])
            if request.conditioning_mode:
                cmd.extend(["--conditioning-mode", request.conditioning_mode.value])

        # LoRAs
        for lora in request.loras:
            if lora.path:
                cmd.extend(["--lora", lora.path, str(lora.strength)])
        if request.pipeline.value == "distilled":
            for lora in request.distilled_loras:
                if lora.path:
                    cmd.extend(["--distilled-lora", lora.path, str(lora.strength)])

        if request.extra_args:
            cmd.extend(request.extra_args)

        return cmd

    def _parse_download_progress(self, line: str) -> tuple[Optional[float], Optional[str]]:
        """Parse model download progress from mlx-video output."""
        lowered = line.lower()
        if "downloading" in lowered and "model" in lowered:
            return 0.0, "Downloading model weights..."
        if "fetching" in lowered or "downloading" in lowered:
            pct_match = re.search(r'(\d+(?:\.\d+)?)\s*%', line)
            if pct_match:
                return float(pct_match.group(1)), "Downloading model weights..."
            return None, "Downloading model weights..."
        return None, None

    def _parse_generation_progress(self, line: str) -> tuple[Optional[float], Optional[str]]:
        """Parse generation progress from mlx-video output."""
        lowered = line.lower()
        if "fetching" in lowered or ("downloading" in lowered and "model" in lowered):
            return None, None
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
        if "loading" in lowered:
            return None, "Loading model..."
        if "encoding" in lowered:
            return None, "Encoding prompt..."
        if "generating" in lowered or "sampling" in lowered:
            return None, "Generating frames..."
        if "decoding video" in lowered or "streaming frames" in lowered:
            return None, "Decoding video..."
        if "saving" in lowered or "writing" in lowered:
            return None, "Saving video..."

        return None, None

    async def start_generation(self, request: GenerationRequest) -> str:
        """Start a video generation job."""
        job_id = str(uuid.uuid4())
        output_filename = f"video_{job_id[:8]}.mp4"
        if request.output_filename:
            safe_name = Path(request.output_filename).name.strip()
            if safe_name:
                if not safe_name.lower().endswith(".mp4"):
                    safe_name = f"{safe_name}.mp4"
                output_filename = safe_name
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
                "current_step": "Starting generation...",
                "download_progress": job.download_progress,
                "download_step": job.download_step,
                "preview_path": job.preview_path,
                "output_path": job.output_path,
            })

            # If auto_output_name is enabled, pass directory to let mlx_video.generate choose filename.
            output_arg = output_path
            auto_output_name = job.request.auto_output_name and not job.request.output_filename
            if auto_output_name:
                output_arg = str(self.output_dir)

            cmd = self._build_command(job.request, output_arg)
            if job.request.text_encoder_repo and not os.environ.get("ALLOW_TEXT_ENCODER_REPO"):
                self._debug("Ignoring text_encoder_repo (disabled by default).")
            self._debug(
                "Starting generation "
                f"job_id={job_id} "
                f"pipeline={job.request.pipeline.value} "
                f"audio={job.request.audio} "
                f"stream={job.request.stream} "
                f"auto_output_name={job.request.auto_output_name} "
                f"output_arg={output_arg}"
            )
            self._debug(f"Command: {' '.join(cmd)}")

            # Create subprocess
            repo_override = os.environ.get("MLX_VIDEO_REPO_PATH")
            repo_path = Path(repo_override).expanduser() if repo_override else (self._repo_root / "mlx-video")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                env={
                    **os.environ,
                    "PYTHONUNBUFFERED": "1",
                    "PYTHONPATH": os.pathsep.join(
                        [
                            str(repo_path),
                            os.environ.get("PYTHONPATH", ""),
                        ]
                    ).strip(os.pathsep),
                },
            )
            job.process = process

            # Read output line by line
            last_progress = 0.0
            pending_output_context: Optional[str] = None
            pending_output_buffer = ""
            pending_output_label = ""
            stage_floor = {
                "Loading model...": 5.0,
                "Encoding prompt...": 10.0,
                "Generating frames...": 20.0,
                "Decoding video...": 85.0,
                "Saving video...": 95.0,
            }

            while True:
                line = await process.stdout.readline()
                if not line:
                    break

                line_str = line.decode('utf-8', errors='ignore').strip()
                if not line_str:
                    continue

                print(f"[mlx-video] {line_str}", flush=True)

                download_progress, download_step = self._parse_download_progress(line_str)
                if download_step:
                    job.download_step = download_step
                if download_progress is not None:
                    job.download_progress = min(100.0, max(0.0, download_progress))
                    if job.download_progress >= 100:
                        job.download_step = "Download complete"

                progress, step = self._parse_generation_progress(line_str)
                if progress is not None:
                    last_progress = progress
                    job.progress = max(job.progress, min(100.0, progress))
                if step:
                    job.current_step = step
                    floor = stage_floor.get(step)
                    if floor is not None:
                        job.progress = max(job.progress, floor)

                pending_output_armed = False

                def arm_output_capture(label: str, remainder: str):
                    nonlocal pending_output_context, pending_output_buffer, pending_output_label, pending_output_armed
                    pending_output_context = label
                    pending_output_label = label
                    pending_output_buffer = remainder.strip()
                    pending_output_armed = True

                def finalize_output_capture():
                    nonlocal pending_output_context, pending_output_buffer, pending_output_label
                    path_str = pending_output_buffer.strip()
                    if not path_str:
                        pending_output_context = None
                        pending_output_buffer = ""
                        return
                    path = Path(path_str)
                    if path.exists():
                        # When streaming with audio enabled, mlx-video writes a temporary
                        # ".temp.mp4" first (video-only), then muxes audio into the final mp4.
                        if pending_output_label == "stream" and job.request.audio and path.name.endswith(".temp.mp4"):
                            job.preview_path = str(path)
                            self._debug(f"{pending_output_label}: detected preview_path={job.preview_path}")
                        else:
                            job.output_path = str(path)
                            self._debug(f"{pending_output_label}: detected output_path={job.output_path}")
                    else:
                        self._debug(f"{pending_output_label}: path not found: {path_str}")
                    pending_output_context = None
                    pending_output_buffer = ""

                if "Streamed video to" in line_str:
                    remainder = line_str.split("Streamed video to", 1)[1].strip()
                    arm_output_capture("stream", remainder)
                    if ".mp4" in pending_output_buffer:
                        finalize_output_capture()

                if "Saved video with audio to" in line_str:
                    remainder = line_str.split("Saved video with audio to", 1)[1].strip()
                    arm_output_capture("final_with_audio", remainder)
                    if ".mp4" in pending_output_buffer:
                        finalize_output_capture()

                if "Saved video to" in line_str and "Saved video with audio to" not in line_str:
                    remainder = line_str.split("Saved video to", 1)[1].strip()
                    arm_output_capture("final", remainder)
                    if ".mp4" in pending_output_buffer:
                        finalize_output_capture()

                if "Saved audio to" in line_str:
                    self._debug(f"audio: {line_str}")

                if pending_output_context and not pending_output_armed:
                    pending_output_buffer = f"{pending_output_buffer}{line_str}".strip()
                    if ".mp4" in pending_output_buffer:
                        finalize_output_capture()

                await self._notify_progress(job_id, {
                    "type": "progress",
                    "job_id": job_id,
                    "progress": job.progress,
                    "current_step": job.current_step,
                    "download_progress": job.download_progress,
                    "download_step": job.download_step,
                    "preview_path": job.preview_path,
                    "output_path": job.output_path,
                })

            # Wait for process to complete
            await process.wait()

            # If auto output name, find newest mp4 in output dir
            final_output = Path(output_path)
            if auto_output_name:
                # Filter out streamed temp previews; they are video-only when audio is enabled.
                mp4s = [
                    p
                    for p in self.output_dir.glob("*.mp4")
                    if not p.name.endswith(".temp.mp4")
                ]
                mp4s = sorted(mp4s, key=lambda p: p.stat().st_mtime, reverse=True)
                self._debug(f"auto_output_name detected {len(mp4s)} mp4(s) in output dir")
                if mp4s:
                    final_output = mp4s[0]
                self._debug(f"auto_output_name selected final_output={final_output}")

            if process.returncode == 0 and final_output.exists():
                job.status = JobStatus.COMPLETED
                job.progress = 100
                job.output_path = str(final_output)
                job.current_step = "Complete"
                try:
                    size_mb = final_output.stat().st_size / (1024 * 1024)
                    self._debug(f"final output size={size_mb:.2f} MB path={final_output}")
                except Exception as e:
                    self._debug(f"final output size check failed: {e}")

                if shutil.which("ffprobe"):
                    try:
                        audio_cmd = [
                            "ffprobe",
                            "-v",
                            "error",
                            "-select_streams",
                            "a",
                            "-show_entries",
                            "stream=codec_name,channels",
                            "-of",
                            "csv=p=0",
                            str(final_output),
                        ]
                        video_cmd = [
                            "ffprobe",
                            "-v",
                            "error",
                            "-select_streams",
                            "v",
                            "-show_entries",
                            "stream=codec_name,width,height,avg_frame_rate",
                            "-of",
                            "csv=p=0",
                            str(final_output),
                        ]
                        audio_result = await asyncio.to_thread(
                            subprocess.run,
                            audio_cmd,
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        video_result = await asyncio.to_thread(
                            subprocess.run,
                            video_cmd,
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        self._debug(f"ffprobe audio streams: {audio_result.stdout.strip()}")
                        self._debug(f"ffprobe video streams: {video_result.stdout.strip()}")
                    except Exception as e:
                        self._debug(f"ffprobe failed: {e}")
                try:
                    params = job.request.dict() if hasattr(job.request, "dict") else job.request.model_dump()
                    if "pipeline" in params and hasattr(job.request.pipeline, "value"):
                        params["pipeline"] = job.request.pipeline.value
                    if "tiling" in params and hasattr(job.request.tiling, "value"):
                        params["tiling"] = job.request.tiling.value
                    meta = {
                        "prompt": job.request.prompt,
                        "params": params,
                        "width": job.request.width,
                        "height": job.request.height,
                    }
                    meta_path = final_output.with_suffix(".json")
                    meta_path.write_text(json.dumps(meta, indent=2))
                except Exception:
                    pass

                await self._notify_progress(job_id, {
                    "type": "complete",
                    "job_id": job_id,
                    "progress": 100,
                    "preview_path": job.preview_path,
                    "output_path": str(final_output)
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
