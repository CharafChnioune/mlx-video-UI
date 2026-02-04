import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any


def _run(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, text=True).strip()
    except Exception:
        return ""


def _get_memory_gb() -> float:
    if sys.platform == "darwin":
        mem = _run(["sysctl", "-n", "hw.memsize"])
        if mem:
            return round(int(mem) / (1024 ** 3), 2)
    if hasattr(os, "sysconf"):
        try:
            pages = os.sysconf("SC_PHYS_PAGES")
            size = os.sysconf("SC_PAGE_SIZE")
            return round(pages * size / (1024 ** 3), 2)
        except Exception:
            pass
    return 0.0


def _get_cpu_name() -> str:
    if sys.platform == "darwin":
        name = _run(["sysctl", "-n", "machdep.cpu.brand_string"])
        if name:
            return name
    return platform.processor() or platform.machine()


def _get_cores() -> int:
    if sys.platform == "darwin":
        cores = _run(["sysctl", "-n", "hw.ncpu"])
        if cores:
            return int(cores)
    return os.cpu_count() or 0


def get_hardware_info() -> Dict[str, Any]:
    memory_gb = _get_memory_gb()
    cpu = _get_cpu_name()
    cores = _get_cores()
    is_apple_silicon = sys.platform == "darwin" and "Apple" in cpu
    mlx_version = None
    try:
        import mlx

        mlx_version = getattr(mlx, "__version__", None)
    except Exception:
        mlx_version = None

    return {
        "platform": sys.platform,
        "cpu": cpu,
        "cores": cores,
        "memory_gb": memory_gb,
        "is_apple_silicon": is_apple_silicon,
        "mlx_version": mlx_version,
        "python_version": sys.version.split()[0],
    }


def recommended_defaults() -> Dict[str, Any]:
    hw = get_hardware_info()
    mem = hw["memory_gb"] or 0.0

    if mem >= 64:
        model = "AITRADER/ltx2-dev-8bit-mlx"
        pipeline = "dev"
        width, height = 1024, 576
        steps = 30
        cfg = 4.5
    elif mem >= 48:
        model = "AITRADER/ltx2-dev-4bit-mlx"
        pipeline = "dev"
        width, height = 832, 480
        steps = 25
        cfg = 4.5
    elif mem >= 32:
        model = "AITRADER/ltx2-distilled-8bit-mlx"
        pipeline = "distilled"
        width, height = 832, 512
        steps = 8
        cfg = 4.0
    else:
        model = "AITRADER/ltx2-distilled-4bit-mlx"
        pipeline = "distilled"
        width, height = 704, 448
        steps = 8
        cfg = 4.0

    cache_limit = max(8, int(mem * 0.6)) if mem else None

    generation = {
        "model_repo": model,
        "pipeline": pipeline,
        "width": width,
        "height": height,
        "num_frames": 33,
        "fps": 24,
        "steps": steps,
        "cfg_scale": cfg,
        "seed": 42,
        "tiling": "auto",
        "cache_limit_gb": cache_limit,
        "eval_interval": 2,
        "audio": True,
        "stream": True,
    }
    # Do not set text_encoder_repo by default; let mlx-video pick its bundled/default encoder.

    training = {
        "model_repo": model,
        "pipeline": pipeline if pipeline in {"dev", "distilled"} else "dev",
        "training_mode": "lora",
        "steps": 1000 if mem >= 32 else 500,
        "batch_size": 1,
        "learning_rate": 5e-4,
        "mixed_precision_mode": "bf16",
    }

    return {"hardware": hw, "generation": generation, "training": training}
