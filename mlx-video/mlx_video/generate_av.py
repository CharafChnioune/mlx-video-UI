"""Compatibility wrappers for the distilled audio-video pipeline."""

from __future__ import annotations

from typing import Optional

from .generate import (
    AUDIO_LATENT_CHANNELS,
    AUDIO_MEL_BINS,
    AUDIO_SAMPLE_RATE,
    PipelineType,
    compute_audio_frames,
    create_audio_position_grid,
    create_position_grid,
    DEFAULT_NEGATIVE_PROMPT,
    generate_video,
    load_audio_decoder as _load_audio_decoder,
    load_vocoder as _load_vocoder,
    mux_video_audio,
    save_audio,
)


def load_audio_decoder(model_path):
    return _load_audio_decoder(model_path, pipeline=PipelineType.DISTILLED)


def load_vocoder(model_path):
    return _load_vocoder(model_path, pipeline=PipelineType.DISTILLED)


def generate_video_with_audio(
    model_repo: str,
    text_encoder_repo: Optional[str],
    prompt: str,
    height: int = 512,
    width: int = 512,
    num_frames: int = 33,
    seed: int = 42,
    fps: int = 24,
    output_path: str = "output_av.mp4",
    output_audio_path: Optional[str] = None,
    verbose: bool = True,
    enhance_prompt: bool = False,
    max_tokens: int = 512,
    temperature: float = 0.7,
    image: Optional[str] = None,
    image_strength: float = 1.0,
    image_frame_idx: int = 0,
    tiling: str = "auto",
):
    """Generate video with synchronized audio using the distilled pipeline."""
    return generate_video(
        model_repo=model_repo,
        text_encoder_repo=text_encoder_repo,
        prompt=prompt,
        pipeline=PipelineType.DISTILLED,
        negative_prompt=DEFAULT_NEGATIVE_PROMPT,
        height=height,
        width=width,
        num_frames=num_frames,
        num_inference_steps=40,
        cfg_scale=4.0,
        seed=seed,
        fps=fps,
        output_path=output_path,
        save_frames=False,
        verbose=verbose,
        enhance_prompt=enhance_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        image=image,
        image_strength=image_strength,
        image_frame_idx=image_frame_idx,
        tiling=tiling,
        stream=False,
        audio=True,
        output_audio_path=output_audio_path,
    )
