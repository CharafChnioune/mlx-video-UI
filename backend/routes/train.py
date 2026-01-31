from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
import asyncio

from models.schemas import TrainingRequest, TrainingResponse, TrainingStatusResponse, TrainingStatus
from services.training_service import training_service

router = APIRouter()


@router.post("/train", response_model=TrainingResponse)
async def start_training(request: TrainingRequest):
    try:
        job_id = await training_service.start_training(request)
        return TrainingResponse(job_id=job_id, status=TrainingStatus.PENDING)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/train/{job_id}/status", response_model=TrainingStatusResponse)
async def training_status(job_id: str):
    job = training_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return TrainingStatusResponse(
        job_id=job.id,
        status=job.status,
        step=job.step,
        total_steps=job.total_steps,
        loss=job.loss,
        eta=job.eta,
        checkpoint_path=job.checkpoint_path,
        error=job.error,
    )


@router.post("/train/{job_id}/stop")
async def stop_training(job_id: str):
    success = await training_service.stop_training(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found or not running")
    return {"message": "Training stopped"}


@router.websocket("/ws/training/{job_id}")
async def training_ws(websocket: WebSocket, job_id: str):
    await websocket.accept()

    job = training_service.get_job(job_id)
    if not job:
        await websocket.send_json({"type": "error", "job_id": job_id, "error": "Job not found"})
        await websocket.close()
        return

    await websocket.send_json({
        "type": "progress",
        "job_id": job_id,
        "step": job.step,
        "total_steps": job.total_steps,
        "loss": job.loss,
    })

    async def send_update(update: dict):
        try:
            await websocket.send_json(update)
        except Exception:
            pass

    training_service.register_progress_callback(job_id, send_update)

    try:
        while True:
            job = training_service.get_job(job_id)
            if not job or job.status in [TrainingStatus.COMPLETED, TrainingStatus.ERROR, TrainingStatus.STOPPED]:
                break
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30)
            except asyncio.TimeoutError:
                try:
                    await websocket.send_json({"type": "ping"})
                except Exception:
                    break
    except WebSocketDisconnect:
        pass
    finally:
        training_service.unregister_progress_callback(job_id)
