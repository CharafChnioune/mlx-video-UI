# MLX Video UI

A modern web interface for LTX-2 video generation on Apple Silicon using MLX.

## Features

- Beautiful dark-themed UI with shadcn/ui components
- Real-time generation progress via WebSocket
- Multiple pipeline support (Distilled, Dev, Keyframe, IC-LoRA)
- Image and video conditioning
- Preset resolutions and frame counts
- Generation history
- Video preview with playback controls

## Project Structure

```
mlx-video-ui/
├── frontend/          # Next.js 14 + shadcn/ui
│   ├── app/           # App router pages
│   ├── components/    # React components
│   │   ├── ui/        # shadcn/ui base components
│   │   ├── video-generator.tsx
│   │   ├── model-selector.tsx
│   │   ├── parameter-panel.tsx
│   │   ├── conditioning-panel.tsx
│   │   ├── progress-indicator.tsx
│   │   └── video-preview.tsx
│   └── lib/           # API client
└── backend/           # Python FastAPI
    ├── main.py        # FastAPI app
    ├── routes/        # API endpoints
    ├── services/      # Video generator service
    └── models/        # Pydantic schemas
```

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- mlx-video installed: `pip install git+https://github.com/CharafChnioune/mlx-video.git`

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API will be available at http://localhost:8000 with docs at /docs.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The UI will be available at http://localhost:3000.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/generate` | POST | Start video generation |
| `/api/status/{job_id}` | GET | Check generation status |
| `/ws/progress/{job_id}` | WS | Real-time progress |
| `/api/upload/image` | POST | Upload conditioning image |
| `/api/upload/video` | POST | Upload reference video |
| `/api/videos/{filename}` | GET | Download generated video |

## Models

The UI supports the following quantized MLX models:

| Model | Size | Speed |
|-------|------|-------|
| LTX-2 Distilled 4-bit | ~10GB | Fastest |
| LTX-2 Distilled 8-bit | ~19GB | Fast |
| LTX-2 Dev 4-bit | ~10GB | Medium |
| LTX-2 Dev 8-bit | ~19GB | Slower |

## Generation Parameters

### Basic
- **Prompt**: Text description of the video
- **Resolution**: Width and height (divisible by 32)
- **Frames**: Number of frames (1 + 8*k formula)
- **Seed**: Random seed for reproducibility

### Pipeline-specific
- **Distilled**: Fast generation with fewer steps
- **Dev**: Full control with CFG scale and step count
- **Keyframe**: Image-to-video generation
- **IC-LoRA**: Video conditioning

### Advanced
- FPS (frames per second)
- Prompt enhancement
- Audio generation
- Tiling mode
- Memory limit

## Development

### Frontend

Built with:
- Next.js 14 (App Router)
- shadcn/ui components
- Tailwind CSS
- Radix UI primitives
- Lucide icons

### Backend

Built with:
- FastAPI
- WebSocket support
- Async subprocess management
- File upload handling

## License

MIT
