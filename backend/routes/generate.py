from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import asyncio
import json
from pathlib import Path

from models.schemas import (
    GenerationRequest,
    GenerationResponse,
    JobStatus,
    JobStatusResponse,
)
from services.video_generator import video_generator

router = APIRouter()


@router.post("/generate", response_model=GenerationResponse)
async def start_generation(request: GenerationRequest):
    """Start a video generation job."""
    try:
        job_id = await video_generator.start_generation(request)
        return GenerationResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            message="Generation started"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get the status of a generation job."""
    job = video_generator.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        current_step=job.current_step,
        output_path=job.output_path,
        error=job.error
    )


@router.delete("/cancel/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a running generation job."""
    success = await video_generator.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found or not running")
    return {"message": "Job cancelled"}


@router.get("/videos/{filename}")
async def get_video(filename: str):
    """Download a generated video."""
    video_path = video_generator.output_dir / filename
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")

    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        filename=filename
    )


@router.websocket("/ws/progress/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time progress updates."""
    await websocket.accept()

    job = video_generator.get_job(job_id)
    if not job:
        await websocket.send_json({
            "type": "error",
            "job_id": job_id,
            "error": "Job not found"
        })
        await websocket.close()
        return

    # Send initial status
    await websocket.send_json({
        "type": "status",
        "job_id": job_id,
        "progress": job.progress,
        "current_step": job.current_step
    })

    # Register callback for progress updates
    async def send_update(update: dict):
        try:
            await websocket.send_json(update)
        except:
            pass

    video_generator.register_progress_callback(job_id, send_update)

    try:
        # Keep connection alive and wait for completion
        while True:
            job = video_generator.get_job(job_id)
            if not job or job.status in [JobStatus.COMPLETED, JobStatus.ERROR]:
                break

            # Wait for messages (ping/pong) to keep connection alive
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30)
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await websocket.send_json({"type": "ping"})
                except:
                    break

    except WebSocketDisconnect:
        pass
    finally:
        video_generator.unregister_progress_callback(job_id)
