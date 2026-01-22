"""Compatibility wrappers for the dev pipeline (CFG)."""

from __future__ import annotations

from typing import Optional

from .generate import (
    AUDIO_LATENT_CHANNELS,
    AUDIO_MEL_BINS,
    AUDIO_SAMPLE_RATE,
    DEFAULT_NEGATIVE_PROMPT,
    PipelineType,
    compute_audio_frames,
    create_audio_position_grid,
    create_position_grid,
    denoise_dev,
    denoise_dev_av,
    generate_video,
    load_audio_decoder as _load_audio_decoder,
    load_vocoder as _load_vocoder,
    ltx2_scheduler,
    mux_video_audio,
    save_audio,
)

denoise_av_with_cfg = denoise_dev_av
denoise_with_cfg = denoise_dev


def load_audio_decoder(model_path):
    return _load_audio_decoder(model_path, pipeline=PipelineType.DEV)


def load_vocoder(model_path):
    return _load_vocoder(model_path, pipeline=PipelineType.DEV)


def generate_video_dev(
    model_repo: str,
    text_encoder_repo: Optional[str],
    prompt: str,
    negative_prompt: str = DEFAULT_NEGATIVE_PROMPT,
    height: int = 512,
    width: int = 768,
    num_frames: int = 33,
    num_inference_steps: int = 40,
    cfg_scale: float = 4.0,
    seed: int = 42,
    fps: int = 24,
    output_path: str = "output.mp4",
    output_audio_path: Optional[str] = None,
    save_frames: bool = False,
    verbose: bool = True,
    enhance_prompt: bool = False,
    max_tokens: int = 512,
    temperature: float = 0.7,
    image: Optional[str] = None,
    image_strength: float = 1.0,
    image_frame_idx: int = 0,
    tiling: str = "none",
    audio: bool = False,
):
    """Generate video using the dev pipeline with CFG (compat wrapper)."""
    return generate_video(
        model_repo=model_repo,
        text_encoder_repo=text_encoder_repo,
        prompt=prompt,
        pipeline=PipelineType.DEV,
        negative_prompt=negative_prompt,
        height=height,
        width=width,
        num_frames=num_frames,
        num_inference_steps=num_inference_steps,
        cfg_scale=cfg_scale,
        seed=seed,
        fps=fps,
        output_path=output_path,
        save_frames=save_frames,
        verbose=verbose,
        enhance_prompt=enhance_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        image=image,
        image_strength=image_strength,
        image_frame_idx=image_frame_idx,
        tiling=tiling,
        stream=False,
        audio=audio,
        output_audio_path=output_audio_path,
    )
