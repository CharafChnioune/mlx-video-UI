from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from routes.generate import router as generate_router
from routes.upload import router as upload_router
from routes.train import router as train_router
from routes.system import router as system_router
from routes.enhance import router as enhance_router
from routes.gallery import router as gallery_router
from routes.checkpoints import router as checkpoints_router
from routes.loras import router as loras_router
from services.video_generator import video_generator


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting MLX Video API...")
    print(f"Output directory: {video_generator.output_dir.absolute()}")
    print(f"Upload directory: {video_generator.upload_dir.absolute()}")
    yield
    # Shutdown
    print("Shutting down MLX Video API...")


app = FastAPI(
    title="MLX Video API",
    description="REST API for LTX-2 video generation with MLX",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration for local development
app.add_middleware(
    CORSMiddleware,
    # Allow dynamic dev ports and Pinokio "*.localhost" domains.
    allow_origins=[],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|0\.0\.0\.0|[a-zA-Z0-9-]+\.localhost)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generate_router, prefix="/api", tags=["generation"])
app.include_router(upload_router, prefix="/api", tags=["upload"])
app.include_router(train_router, prefix="/api", tags=["training"])
app.include_router(system_router, prefix="/api", tags=["system"])
app.include_router(enhance_router, prefix="/api", tags=["enhance"])
app.include_router(gallery_router, prefix="/api", tags=["gallery"])
app.include_router(checkpoints_router, prefix="/api", tags=["checkpoints"])
app.include_router(loras_router, prefix="/api", tags=["loras"])

# Mount static files for video output (optional direct access)
app.mount("/outputs", StaticFiles(directory=str(video_generator.output_dir)), name="outputs")


@app.get("/")
async def root():
    return {
        "name": "MLX Video API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        ws_ping_interval=30,
        ws_ping_timeout=30,
    )
