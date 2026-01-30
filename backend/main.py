from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from routes.generate import router as generate_router
from routes.upload import router as upload_router
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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generate_router, prefix="/api", tags=["generation"])
app.include_router(upload_router, prefix="/api", tags=["upload"])

# Mount static files for video output
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


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
        port=8000,
        reload=True,
        ws_ping_interval=30,
        ws_ping_timeout=30,
    )
