# mlx-video-UI

Modern Gradio UI for generating videos with audio using mlx-video on Apple Silicon.

## Requirements
- Python 3.11+
- uv (https://docs.astral.sh/uv/)
- FFmpeg (for video previews in the UI)

## Install with uv
```bash
uv venv --python 3.11
source .venv/bin/activate
uv sync
```

## Run
```bash
uv run mlx-video-ui
```

Or:
```bash
uv run python app.py
```

## Notes
- If FFmpeg is missing, the UI will still run but preview extraction is disabled.
  - macOS: `brew install ffmpeg`
