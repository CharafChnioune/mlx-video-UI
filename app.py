"""
mlx-video-UI - Modern Gradio UI for LTX-2
A professional UI for generating videos with audio using mlx-video on Apple Silicon.
"""

import uuid
import tempfile
import os
import random
import re
import shutil
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Generator

import gradio as gr
import requests
from gradio.themes.base import Base
from gradio.themes.utils import colors, fonts, sizes

from ui.tabs.advanced_settings import build_advanced_settings_tab
from ui.tabs.generation import build_generation_tab
from ui.tabs.movie_generator import build_movie_generator_tab


# ===== AURORA THEME - Premium Dark Theme with Glassmorphism =====
class AuroraTheme(Base):
    """
    Premium Aurora theme with glassmorphism, animated gradients,
    and modern design patterns for a professional dark UI.
    """
    def __init__(self):
        super().__init__(
            primary_hue=colors.violet,
            secondary_hue=colors.cyan,
            neutral_hue=colors.slate,
            spacing_size=sizes.spacing_lg,
            radius_size=sizes.radius_lg,
            text_size=sizes.text_md,
            font=(fonts.GoogleFont("Outfit"), "ui-sans-serif", "system-ui", "sans-serif"),
            font_mono=(fonts.GoogleFont("JetBrains Mono"), "ui-monospace", "SFMono-Regular", "monospace"),
        )
        super().set(
            # Body & Background
            body_background_fill="#0a0a0f",
            body_background_fill_dark="#0a0a0f",

            # Blocks & Cards
            block_background_fill="rgba(15, 15, 25, 0.8)",
            block_background_fill_dark="rgba(15, 15, 25, 0.8)",
            block_border_color="rgba(139, 92, 246, 0.2)",
            block_border_color_dark="rgba(139, 92, 246, 0.2)",
            block_border_width="1px",
            block_label_background_fill="rgba(139, 92, 246, 0.1)",
            block_label_background_fill_dark="rgba(139, 92, 246, 0.1)",
            block_label_text_color="#a78bfa",
            block_label_text_color_dark="#a78bfa",
            block_shadow="*shadow_drop_lg",
            block_shadow_dark="*shadow_drop_lg",
            block_title_text_color="#f1f5f9",
            block_title_text_color_dark="#f1f5f9",

            # Buttons
            button_primary_background_fill="linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%)",
            button_primary_background_fill_dark="linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%)",
            button_primary_background_fill_hover="linear-gradient(135deg, #a78bfa 0%, #22d3ee 100%)",
            button_primary_background_fill_hover_dark="linear-gradient(135deg, #a78bfa 0%, #22d3ee 100%)",
            button_primary_text_color="white",
            button_primary_text_color_dark="white",
            button_primary_border_color="transparent",
            button_primary_border_color_dark="transparent",
            button_primary_shadow="*shadow_drop_lg",
            button_primary_shadow_dark="*shadow_drop_lg",
            button_secondary_background_fill="rgba(139, 92, 246, 0.1)",
            button_secondary_background_fill_dark="rgba(139, 92, 246, 0.1)",
            button_secondary_background_fill_hover="rgba(139, 92, 246, 0.2)",
            button_secondary_background_fill_hover_dark="rgba(139, 92, 246, 0.2)",
            button_secondary_text_color="#a78bfa",
            button_secondary_text_color_dark="#a78bfa",
            button_secondary_border_color="rgba(139, 92, 246, 0.3)",
            button_secondary_border_color_dark="rgba(139, 92, 246, 0.3)",

            # Inputs
            input_background_fill="rgba(15, 15, 25, 0.6)",
            input_background_fill_dark="rgba(15, 15, 25, 0.6)",
            input_border_color="rgba(139, 92, 246, 0.2)",
            input_border_color_dark="rgba(139, 92, 246, 0.2)",
            input_border_color_focus="rgba(139, 92, 246, 0.5)",
            input_border_color_focus_dark="rgba(139, 92, 246, 0.5)",
            input_placeholder_color="#64748b",
            input_placeholder_color_dark="#64748b",

            # Slider
            slider_color="#8b5cf6",
            slider_color_dark="#8b5cf6",

            # Text colors
            body_text_color="#e2e8f0",
            body_text_color_dark="#e2e8f0",
            body_text_color_subdued="#94a3b8",
            body_text_color_subdued_dark="#94a3b8",

            # Links
            link_text_color="#22d3ee",
            link_text_color_dark="#22d3ee",
            link_text_color_hover="#06b6d4",
            link_text_color_hover_dark="#06b6d4",

            # Checkboxes
            checkbox_background_color="rgba(139, 92, 246, 0.1)",
            checkbox_background_color_dark="rgba(139, 92, 246, 0.1)",
            checkbox_background_color_selected="#8b5cf6",
            checkbox_background_color_selected_dark="#8b5cf6",
            checkbox_border_color="rgba(139, 92, 246, 0.3)",
            checkbox_border_color_dark="rgba(139, 92, 246, 0.3)",

            # Tables
            table_border_color="rgba(139, 92, 246, 0.15)",
            table_border_color_dark="rgba(139, 92, 246, 0.15)",
            table_even_background_fill="rgba(139, 92, 246, 0.05)",
            table_even_background_fill_dark="rgba(139, 92, 246, 0.05)",
            table_odd_background_fill="transparent",
            table_odd_background_fill_dark="transparent",
            table_row_focus="rgba(139, 92, 246, 0.1)",
            table_row_focus_dark="rgba(139, 92, 246, 0.1)",

            # Border
            border_color_accent="rgba(139, 92, 246, 0.3)",
            border_color_accent_dark="rgba(139, 92, 246, 0.3)",
            border_color_primary="rgba(139, 92, 246, 0.2)",
            border_color_primary_dark="rgba(139, 92, 246, 0.2)",

            # Shadow
            shadow_drop="0 4px 6px rgba(0, 0, 0, 0.3)",
            shadow_drop_lg="0 10px 25px rgba(0, 0, 0, 0.4)",
            shadow_spread="6px",

            # Panel
            panel_background_fill="rgba(15, 15, 25, 0.9)",
            panel_background_fill_dark="rgba(15, 15, 25, 0.9)",
            panel_border_color="rgba(139, 92, 246, 0.2)",
            panel_border_color_dark="rgba(139, 92, 246, 0.2)",
        )


def check_ffmpeg():
    """Check if FFmpeg is installed and return status."""
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    return ffmpeg is not None and ffprobe is not None


FFMPEG_INSTALLED = check_ffmpeg()

# ===== MOVIE GENERATOR CONSTANTS =====
MAX_SCENE_DURATION = 20  # Max seconds per scene (LTX-2 supports up to 20 sec!)
DEFAULT_SCENE_DURATION = 6  # Default duration (increased from 4)
MAX_SCENES = 5000  # Maximum number of scenes (very long films)
MIN_MOVIE_DURATION = 6  # Minimum total movie duration in seconds
MAX_MOVIE_DURATION = 86400  # Maximum 24 hours (practical limit)
MOVIE_PACING_PRESETS = {
    "Fast (8s avg)": 8,
    "Standard (12s avg)": 12,
    "Slow (16s avg)": 16,
}

# Script Storage Directory
SCRIPTS_DIR = Path.home() / ".mlx-video-ui" / "scripts"
SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

# Video Output Directory
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ===== SETTINGS PERSISTENCE =====
SETTINGS_FILE = Path.home() / ".mlx-video-ui" / "settings.json"

DEFAULT_SETTINGS = {
    "generation": {
        "resolution_preset": "1080p (1920x1088)",
        "width": 1920,
        "height": 1088,
        "frames": 241,
        "fps": 24,
        "seed": 42,
        "save_frames": False,
        "tiling_mode": "auto",
        "image_strength": 0.8,
        "pb_camera": "Static",
        "pb_lighting": "Natural daylight"
    },
    "advanced": {
        "cfg_preset": "Balanced (Default)",
        "text_cfg": 3.0,
        "cross_modal_cfg": 3.0,
        "prompt_enhancer": "Gemma (Built-in)",
        "llm_provider": "None",
        "llm_model": None,
        "enhance_prompt": True,
        "temperature": 0.7,
        "max_tokens": 2048,
        "audio_sample_rate": 24000,
        "stereo_output": True,
        "num_inference_steps": 50
    },
    "movie": {
        "duration_preset": "3 min (Music video)",
        "duration": 180,
        "fps": 24,
        "resolution_preset": "1080p (1920x1088)",
        "tiling_mode": "auto",
        "script_mode": "Auto (recommended)",
        "story_structure": "Three-act (Hollywood)",
        "pacing": "Standard (12s avg)",
        "use_continuity": True,
        "continuity_strength": 0.7,
        "enhance_prompts": True,
        "temperature": 0.7,
        "max_tokens": 512
    }
}


def normalize_llm_provider(value: str | None) -> str:
    """Normalize LLM provider values from settings."""
    if value in VALID_LLM_PROVIDERS or value == "None":
        return value
    return "None"


def load_settings():
    """Load settings from JSON file."""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r") as f:
                saved = json.load(f)
                # Merge with defaults for any missing keys
                settings = {}
                for section in DEFAULT_SETTINGS:
                    settings[section] = DEFAULT_SETTINGS[section].copy()
                    if section in saved:
                        settings[section].update(saved[section])
                settings["advanced"]["llm_provider"] = normalize_llm_provider(
                    settings["advanced"].get("llm_provider", "None")
                )
                if settings["advanced"]["llm_provider"] == "None":
                    settings["advanced"]["llm_model"] = None
                return settings
        except Exception:
            pass
    return {section: DEFAULT_SETTINGS[section].copy() for section in DEFAULT_SETTINGS}


def save_settings(settings: dict):
    """Save settings to JSON file."""
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


def save_setting(section: str, key: str, value):
    """Save a single setting."""
    settings = load_settings()
    settings[section][key] = value
    save_settings(settings)
    return None


def load_all_settings():
    """Load all settings on app startup."""
    s = load_settings()
    return [
        # Generation tab
        s["generation"]["resolution_preset"],
        s["generation"]["width"],
        s["generation"]["height"],
        s["generation"]["frames"],
        s["generation"]["fps"],
        s["generation"]["seed"],
        s["generation"]["save_frames"],
        s["generation"]["tiling_mode"],
        s["generation"]["image_strength"],
        s["generation"]["pb_camera"],
        s["generation"]["pb_lighting"],
        # Advanced settings tab
        s["advanced"]["cfg_preset"],
        s["advanced"]["text_cfg"],
        s["advanced"]["cross_modal_cfg"],
        s["advanced"]["prompt_enhancer"],
        s["advanced"]["llm_provider"],
        s["advanced"]["llm_model"],
        s["advanced"]["enhance_prompt"],
        s["advanced"]["temperature"],
        s["advanced"]["max_tokens"],
        s["advanced"]["audio_sample_rate"],
        s["advanced"]["stereo_output"],
        s["advanced"]["num_inference_steps"],
        # Movie tab
        s["movie"]["duration_preset"],
        s["movie"]["duration"],
        s["movie"]["fps"],
        s["movie"]["resolution_preset"],
        s["movie"]["tiling_mode"],
        s["movie"]["script_mode"],
        s["movie"]["story_structure"],
        s["movie"]["pacing"],
        s["movie"]["use_continuity"],
        s["movie"]["continuity_strength"],
        s["movie"]["enhance_prompts"],
        s["movie"]["temperature"],
        s["movie"]["max_tokens"],
    ]


# Scene Writer System Prompt for LLM (Based on LTX-2 paper Section 4.2)
# "Comprehensive yet factual, describing only what is seen and heard without emotional interpretation"
SCENE_WRITER_SYSTEM_PROMPT = """You are a professional screenwriter creating scenes for LTX-2 AI video generation with synchronized audio.

CRITICAL: Follow the LTX-2 paper's captioning guidelines and be extremely specific:
- Be COMPREHENSIVE yet FACTUAL
- Describe ONLY what is seen and heard
- NO emotional interpretation or subjective commentary
- Include BOTH visual AND audio elements
- Add micro details (wind/briesje, fabric movement, reflections, dust, small sounds)

CONTINUITY (VERY IMPORTANT):
- Scenes are one continuous film, not standalone clips
- Each scene must explicitly connect to the previous scene via a shared visual/audio anchor
- If time/location changes, describe the transition (e.g., match cut, sound bridge, dissolve)
- End each scene with a concrete hook that can carry into the next scene

OUTPUT FORMAT (JSON array):
[
  {
    "description": "Full scene description following LTX-2 format",
    "duration": 8,
    "visual_style": "cinematic look, lens, palette, grain, depth of field",
    "audio_style": "score, foley, soundscape, dialogue style",
    "characters": "names, roles, relationships, voice/accent",
    "setting": "time period, locations, mood, key props"
  }
]

PROMPT STRUCTURE (per LTX-2 paper):
1. BEGIN with subject: "A woman with long dark hair...", "A vintage red car..."
2. ADD action: "...walks through a sunlit garden...", "...drives down a winding road..."
3. CAMERA movement: "...camera slowly tracking alongside...", "...dolly forward...", "...static wide shot..."
4. LIGHTING: "...soft golden hour lighting...", "...dramatic shadows...", "...blue hour ambiance..."
5. AUDIO cues: "...birds singing, footsteps on gravel...", "...engine rumbling, wind noise..."
6. BE SPECIFIC: NOT "ambient sounds" but "distant traffic, wind through trees, church bells"
7. MICRO DETAIL: breeze direction + effect, fabric rustle, hair movement, tiny debris, reflections
7. SPEECH/DIALOGUE: Include ACTUAL dialogue text that characters speak!

SPEECH/DIALOGUE RULES (CRITICAL):
- Include ACTUAL dialogue text that characters speak
- Format: "Character says: 'Actual dialogue here'" with language/accent
- Example: "The woman looks at the sunset and says: 'It's beautiful, isn't it?' in a soft British accent"
- NOT just "speaks softly" but the actual words they say!
- LTX-2 generates video WITH audio, so dialogue text is spoken by the model

VISUAL ELEMENTS:
- Camera: static, pan left/right, zoom in/out, tracking shot, dolly forward/backward, crane up/down, handheld, orbit
- Lighting: natural daylight, golden hour, blue hour, dramatic shadows, soft diffused, backlit, neon/artificial, candlelight, moonlight
- Subject: detailed appearance, specific actions, expressions
- Environment: setting details, atmosphere, weather, time of day
- Lens/DOF: focal length, depth of field, film grain, lens flare, bokeh

AUDIO ELEMENTS (LTX-2 supports stereo 24kHz):
- Ambient: specific environmental sounds (wind through leaves, distant traffic, crowd murmur, ocean waves)
- Foley: precise sound effects (footsteps on gravel, rustling fabric, door creaking, glass clinking)
- Music: style, mood, instruments, or "no music" for natural atmosphere
- Speech: ACTUAL dialogue with speaker description, language, AND accent (e.g., "male voice says: 'Hello there!' in American English")
- Micro audio: room tone, air movement, cloth creak, small impacts

RULES:
1. Output ONLY valid JSON array, no other text
2. Each scene 4-15 seconds (LTX-2 supports up to 20 sec)
3. Integrate visual AND audio naturally in description
4. Ensure continuity between scenes
5. Be factual - describe what is seen/heard, no interpretation
6. Include ACTUAL spoken dialogue, not just descriptions of speech
7. Fill visual_style, audio_style, characters, setting for every scene with dense detail

EXAMPLE for theme "A day in the forest":
[
  {
    "description": "A misty forest at dawn, golden sunlight filtering through dense pine trees, illuminating particles floating in the air. Camera slowly pans across moss-covered rocks and ferns glistening with dew. Audio: birds singing in the canopy, gentle rustling of leaves, distant stream trickling over rocks, no music.",
    "duration": 10,
    "visual_style": "slow pan, golden hour light, misty atmosphere, shallow depth of field",
    "audio_style": "birdsong, rustling leaves, distant stream, no music",
    "characters": "none",
    "setting": "dawn forest, mossy rocks, dew, cool air"
  },
  {
    "description": "Close-up of a spider web covered in dewdrops, each drop catching morning light like tiny prisms. Gentle breeze causes subtle movement, camera static with shallow depth of field. Audio: soft chirping of crickets, single bird call echoing, light wind, no music.",
    "duration": 8,
    "visual_style": "static macro close-up, shallow DOF, backlit dewdrops",
    "audio_style": "crickets chirping, bird call, gentle wind",
    "characters": "none",
    "setting": "forest floor, dew-covered web, early morning light"
  },
  {
    "description": "Wide shot of a forest clearing, a deer grazing peacefully in tall grass. Soft afternoon light creates long shadows, camera slowly zooms in. Audio: deer hooves stepping softly on grass, birds chirping overhead, distant woodpecker tapping, wind rustling through tall grass.",
    "duration": 12,
    "visual_style": "wide shot, slow zoom, soft afternoon light, long shadows",
    "audio_style": "soft hoofsteps, birdsong, woodpecker, wind in grass",
    "characters": "deer (wild animal)",
    "setting": "forest clearing, tall grass, afternoon"
  }
]

EXAMPLE with dialogue for theme "A woman reunites with her hometown":
[
  {
    "description": "A woman with long dark hair stands on a cliff overlooking the ocean at sunset. She turns to the camera and says: 'I never thought I would see this place again.' in a gentle American accent. Camera slowly pushes in on her face. Audio: ocean waves crashing, seagulls calling, wind.",
    "duration": 10,
    "visual_style": "medium shot, slow push-in, golden hour backlight, film grain",
    "audio_style": "ocean waves, seagulls, wind, spoken dialogue",
    "characters": "woman, returning to hometown, gentle American accent",
    "setting": "sunset cliff, ocean horizon, salty wind"
  }
]"""

# Sequential Scene Writer Prompt (for story continuity)
SEQUENTIAL_SCENE_WRITER_PROMPT = """You are a professional screenwriter creating scenes for an AI video generator (LTX-2).

CRITICAL RULES:
1. Each scene MUST continue naturally from previous scenes
2. Maintain visual consistency: same characters, locations, lighting style
3. Maintain narrative flow: actions have consequences, time progresses logically
4. Each scene description must be self-contained but reference shared elements
5. Include micro details: breeze/wind effects, fabric movement, reflections, tiny sounds
6. Open with a continuity anchor from the previous scene (sound, motion, object)
7. End with a clear hook that sets up the next scene

CHARACTER CONSISTENCY (VERY IMPORTANT):
If a main character was described (from reference image), ensure this character:
- Appears consistently in relevant scenes with the EXACT same physical description
- Has the same hair color, eye color, clothing, and distinctive features each time
- Is referred to by the same terms throughout all scenes
- Include the full character description at the START of scenes where they appear

FORMAT: Return ONLY valid JSON: {"description": "...", "duration": N, "visual_style": "...", "audio_style": "...", "characters": "...", "setting": "..."}
- description: Detailed visual+audio description (50-150 words)
- duration: Scene length in seconds (1-20)
- visual_style: lens, palette, grain, depth of field, lighting vibe
- audio_style: score/foley/soundscape style and intensity
- characters: names, roles, relationships, voice/accent
- setting: time period, location, mood, key props
Fill every field for each scene.

DESCRIPTION GUIDELINES (per LTX-2 paper):
- Start with subject and action
- Include camera movement/angle
- Specify lighting and atmosphere
- Add ambient audio and sound effects
- Be factual, not emotional
- Add concrete specifics: textures, colors, props, wardrobe, micro-actions

SPEECH/DIALOGUE RULES (CRITICAL):
- Include ACTUAL dialogue text that characters speak
- Format: "Character says: 'Actual dialogue here'" with language/accent
- Example: "The woman smiles and says: 'Good morning!' in a warm French accent"
- NOT just "speaks softly" but the actual words they say!
- LTX-2 generates video WITH audio, so dialogue text will be spoken

VISUAL ELEMENTS:
- Camera: static, pan left/right, zoom in/out, tracking shot, dolly forward/backward, crane up/down, handheld, orbit
- Lighting: natural daylight, golden hour, blue hour, dramatic shadows, soft diffused, backlit, neon/artificial
- Subject: detailed appearance, specific actions, expressions
- Environment: setting details, atmosphere, weather, time of day
- Lens/DOF: focal length, depth of field, film grain, lens flare, bokeh

AUDIO ELEMENTS (LTX-2 supports stereo 24kHz):
- Ambient: specific environmental sounds (wind, traffic, crowd, ocean)
- Foley: precise sound effects (footsteps, rustling, doors, glass)
- Music: style, mood, instruments, or "no music" for natural atmosphere
- Speech: ACTUAL dialogue with speaker description, language, AND accent (e.g., "she says: 'Hello!' in British English")
- Micro audio: room tone, air movement, cloth creak, small impacts
"""

# LLM API endpoints
LM_STUDIO_BASE = "http://localhost:1234/v1"
OLLAMA_BASE = "http://localhost:11434"
VALID_LLM_PROVIDERS = {"LM Studio", "Ollama"}

# Gemma model configuration - using abliterated version for unrestricted prompt enhancement
GEMMA_MODEL_REPO = "mlx-community/gemma-3-12b-it-qat-abliterated-lm-4bit"

# Global cache for Gemma model to avoid reloading
_gemma_model_cache = {"model": None, "tokenizer": None}

def load_abliterated_gemma():
    """Load the abliterated Gemma 3 model using mlx_lm.

    Uses a global cache to avoid reloading the model on every call.

    Returns:
        Tuple of (model, tokenizer)
    """
    if _gemma_model_cache["model"] is not None:
        return _gemma_model_cache["model"], _gemma_model_cache["tokenizer"]

    from mlx_lm import load

    print(f"[Gemma] Loading abliterated model: {GEMMA_MODEL_REPO}")
    model, tokenizer = load(GEMMA_MODEL_REPO)
    print(f"[Gemma] Model loaded successfully")

    _gemma_model_cache["model"] = model
    _gemma_model_cache["tokenizer"] = tokenizer

    return model, tokenizer


def generate_with_abliterated_gemma(
    prompt: str,
    max_tokens: int = 2048,
    temperature: float = 0.7,
) -> str:
    """Generate text using the abliterated Gemma 3 model.

    Args:
        prompt: The input prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature

    Returns:
        Generated text
    """
    from mlx_lm import generate
    from mlx_lm.sample_utils import make_sampler

    model, tokenizer = load_abliterated_gemma()
    sampler = make_sampler(temp=temperature)

    response = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=max_tokens,
        sampler=sampler,
        verbose=False,
    )

    return response


# Resolution presets: (name, width, height)
RESOLUTION_PRESETS = {
    "512x512 (Square)": (512, 512),
    "768x512 (Landscape)": (768, 512),
    "512x768 (Portrait)": (512, 768),
    "1024x576 (Widescreen)": (1024, 576),
    "576x1024 (Vertical)": (576, 1024),
    "720p (1280x768)": (1280, 768),        # HD - LTX-2 supported (768 % 64 = 0)
    "1080p (1920x1088)": (1920, 1088),     # Full HD - LTX-2 supported (1088 % 64 = 0)
    "4K (3840x2176)": (3840, 2176),        # 4K UHD - Fixed: 2176 % 64 = 0
    "Custom": None,
}

# Duration presets: (name, frames) at 24fps - Extended for LTX-2 (up to 20 sec)
DURATION_PRESETS = {
    "1 sec (25 frames)": 25,
    "2 sec (49 frames)": 49,
    "3 sec (73 frames)": 73,
    "4 sec (97 frames)": 97,
    "5 sec (121 frames)": 121,
    "6 sec (145 frames)": 145,
    "8 sec (193 frames)": 193,             # NEW: Extended duration
    "10 sec (241 frames)": 241,            # NEW: Extended duration
    "15 sec (361 frames)": 361,            # NEW: Extended duration
    "20 sec (481 frames)": 481,            # NEW: LTX-2 max duration
    "Custom": None,
}

# CFG (Classifier-Free Guidance) Presets based on LTX-2 paper
# Video stream optimal: s_t = 3, s_m = 3 (text guidance, cross-modal guidance)
# Audio stream optimal: s_t = 7, s_m = 3
CFG_PRESET_VALUES = {
    "Balanced (Default)": {"text_cfg": 3.0, "cross_modal_cfg": 3.0},
    "Optimal Audio (Paper)": {"text_cfg": 7.0, "cross_modal_cfg": 3.0},  # LTX-2 paper audio
    "High Text Adherence": {"text_cfg": 5.0, "cross_modal_cfg": 2.0},
    "Strong Audio Sync": {"text_cfg": 3.0, "cross_modal_cfg": 5.0},
    "Maximum Quality": {"text_cfg": 4.0, "cross_modal_cfg": 4.0},
    "Custom": None,
}

# Camera motion options for Prompt Builder
CAMERA_MOTIONS = [
    "Static",
    "Pan left",
    "Pan right",
    "Zoom in",
    "Zoom out",
    "Tracking shot",
    "Dolly forward",
    "Dolly backward",
    "Crane up",
    "Crane down",
    "Handheld",
    "Orbit",
]

# Lighting options for Prompt Builder
LIGHTING_OPTIONS = [
    "Natural daylight",
    "Golden hour",
    "Blue hour",
    "Dramatic shadows",
    "Soft diffused",
    "Backlit",
    "Neon/artificial",
    "Candlelight",
    "Moonlight",
    "Overcast",
    "Studio lighting",
]

# Speech languages for Prompt Builder (LTX-2 paper: "speaker, language, and accent identification")
SPEECH_LANGUAGES = [
    "No specific language",
    "English",
    "Spanish",
    "French",
    "German",
    "Dutch",
    "Italian",
    "Portuguese",
    "Chinese",
    "Japanese",
    "Korean",
    "Russian",
    "Arabic",
    "Hindi",
]

# Speech accents for Prompt Builder
SPEECH_ACCENTS = [
    "No specific accent",
    "American",
    "British",
    "Australian",
    "Irish",
    "Scottish",
    "Indian",
    "Southern American",
    "New York",
    "French",
    "German",
    "Spanish",
    "Italian",
]

# Custom CSS for professional styling
CUSTOM_CSS = """
/* ===== AURORA DESIGN SYSTEM - CSS Custom Properties ===== */
:root {
    --aurora-violet: #8b5cf6;
    --aurora-violet-light: #a78bfa;
    --aurora-violet-dark: #7c3aed;
    --aurora-cyan: #06b6d4;
    --aurora-cyan-light: #22d3ee;
    --aurora-pink: #ec4899;
    --aurora-pink-light: #f472b6;
    --aurora-x: 0px;
    --aurora-y: 0px;
    --font-body: 'Outfit', ui-sans-serif, system-ui, sans-serif;
    --font-display: 'Space Grotesk', 'Outfit', ui-sans-serif, system-ui, sans-serif;
    --bg-primary: #0a0a0f;
    --bg-secondary: rgba(15, 15, 25, 0.8);
    --bg-card: rgba(15, 15, 25, 0.9);
    --bg-glass: rgba(255, 255, 255, 0.03);
    --border-glass: rgba(255, 255, 255, 0.08);
    --border-soft: rgba(148, 163, 184, 0.18);
    --surface-1: rgba(12, 14, 22, 0.72);
    --surface-2: rgba(18, 21, 32, 0.88);
    --surface-3: rgba(24, 28, 42, 0.94);
    --border-accent: rgba(139, 92, 246, 0.3);
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --glow-violet: rgba(139, 92, 246, 0.4);
    --glow-cyan: rgba(6, 182, 212, 0.3);
    --shadow-soft: 0 18px 40px rgba(5, 8, 18, 0.45);
}

/* ===== ANIMATED AURORA BACKGROUND ===== */
.gradio-container {
    background: var(--bg-primary) !important;
    min-height: 100vh;
    position: relative;
    overflow-x: hidden;
    font-family: var(--font-body);
    color-scheme: dark;
    isolation: isolate;
}

.gradio-container::before {
    content: '';
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background:
        radial-gradient(ellipse at 20% 20%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(6, 182, 212, 0.1) 0%, transparent 50%),
        radial-gradient(ellipse at 40% 60%, rgba(236, 72, 153, 0.08) 0%, transparent 40%);
    animation: aurora 20s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}

@keyframes aurora {
    0%, 100% {
        transform: translate(calc(var(--aurora-x, 0px) + 0%), calc(var(--aurora-y, 0px) + 0%)) rotate(0deg);
    }
    25% {
        transform: translate(calc(var(--aurora-x, 0px) + 2%), calc(var(--aurora-y, 0px) - 2%)) rotate(1deg);
    }
    50% {
        transform: translate(calc(var(--aurora-x, 0px) - 1%), calc(var(--aurora-y, 0px) + 1%)) rotate(-1deg);
    }
    75% {
        transform: translate(calc(var(--aurora-x, 0px) - 2%), calc(var(--aurora-y, 0px) + 2%)) rotate(0.5deg);
    }
}

/* ===== GLASSMORPHISM HEADER ===== */
.header-container {
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.14) 0%, rgba(6, 182, 212, 0.12) 45%, rgba(236, 72, 153, 0.12) 100%), var(--surface-2) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: 16px !important;
    padding: 2rem 2.5rem !important;
    margin-bottom: 1.5rem !important;
    box-shadow:
        var(--shadow-soft),
        inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
    position: relative;
    overflow: hidden;
    z-index: 1;
}

/* Header shimmer effect */
.header-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(255, 255, 255, 0.05),
        transparent
    );
    animation: shimmer 8s ease-in-out infinite;
}

@keyframes shimmer {
    0%, 100% { left: -100%; }
    50% { left: 100%; }
}

.header-container h1 {
    color: #ffffff !important;
    font-family: var(--font-display);
    font-weight: 700 !important;
    font-size: 2.2rem !important;
    margin: 0 0 0.5rem 0 !important;
    letter-spacing: -0.02em !important;
    text-shadow: 0 0 30px rgba(139, 92, 246, 0.5), 0 0 60px rgba(6, 182, 212, 0.3) !important;
}

/* Gradient text for browsers that support it */
@supports (-webkit-background-clip: text) {
    .header-container h1 {
        background: linear-gradient(135deg, #ffffff 0%, #a78bfa 50%, #22d3ee 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        text-shadow: none !important;
    }
}

/* Target Gradio markdown headings specifically */
.header-container .markdown-text h1,
.header-container .prose h1,
.header-container [class*="markdown"] h1 {
    color: #ffffff !important;
    font-family: var(--font-display);
    font-weight: 700 !important;
    font-size: 2.2rem !important;
    margin: 0 0 0.5rem 0 !important;
    letter-spacing: -0.02em !important;
    text-shadow: 0 0 30px rgba(139, 92, 246, 0.5), 0 0 60px rgba(6, 182, 212, 0.3) !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}

@supports (-webkit-background-clip: text) {
    .header-container .markdown-text h1,
    .header-container .prose h1,
    .header-container [class*="markdown"] h1 {
        background: linear-gradient(135deg, #ffffff 0%, #a78bfa 50%, #22d3ee 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        text-shadow: none !important;
    }
}

.header-container p {
    color: var(--text-secondary) !important;
    font-size: 0.95rem !important;
    margin: 0 !important;
    font-weight: 400 !important;
}

/* ===== GLASS CARDS ===== */
.glass-card, .gr-group, .gr-box {
    background: linear-gradient(180deg, var(--surface-1) 0%, var(--surface-2) 100%) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: 12px !important;
    box-shadow: var(--shadow-soft) !important;
    transition: all 0.3s ease !important;
}

.glass-card:hover, .gr-group:hover {
    border-color: var(--border-accent) !important;
    box-shadow: 0 8px 32px rgba(139, 92, 246, 0.15) !important;
}

/* ===== AURORA GRADIENT BUTTONS ===== */
.generate-btn {
    background: linear-gradient(135deg, var(--aurora-violet) 0%, var(--aurora-cyan) 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    padding: 1rem 2.5rem !important;
    color: white !important;
    box-shadow:
        0 4px 20px var(--glow-violet),
        0 0 40px rgba(139, 92, 246, 0.2) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative;
    overflow: hidden;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

.generate-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        90deg,
        transparent,
        rgba(255, 255, 255, 0.2),
        transparent
    );
    transition: left 0.5s ease;
}

.generate-btn:hover {
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow:
        0 8px 30px var(--glow-violet),
        0 0 60px rgba(139, 92, 246, 0.3) !important;
}

.generate-btn:hover::before {
    left: 100%;
}

.generate-btn:active {
    transform: translateY(-1px) scale(0.98) !important;
}

/* ===== SECONDARY/GHOST BUTTONS ===== */
.secondary-btn {
    background: rgba(139, 92, 246, 0.1) !important;
    border: 1px solid var(--border-accent) !important;
    border-radius: 8px !important;
    color: var(--aurora-violet-light) !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

.secondary-btn:hover {
    background: rgba(139, 92, 246, 0.2) !important;
    border-color: var(--aurora-violet) !important;
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.2) !important;
}

.generate-btn:focus-visible,
.secondary-btn:focus-visible {
    outline: 2px solid rgba(34, 211, 238, 0.6) !important;
    outline-offset: 2px !important;
}

/* ===== TABS WITH GRADIENT UNDERLINE ===== */
.tabs > .tab-nav {
    background: transparent !important;
    border-bottom: 1px solid var(--border-glass) !important;
    padding: 0 !important;
    gap: 0.5rem !important;
}

.tabs > .tab-nav > button {
    background: transparent !important;
    border: none !important;
    border-radius: 8px 8px 0 0 !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    padding: 1rem 1.5rem !important;
    transition: all 0.3s ease !important;
    position: relative;
}

.tabs > .tab-nav > button::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--aurora-violet), var(--aurora-cyan));
    border-radius: 3px 3px 0 0;
    transition: width 0.3s ease;
}

.tabs > .tab-nav > button:hover {
    color: var(--text-primary) !important;
    background: rgba(139, 92, 246, 0.1) !important;
}

.tabs > .tab-nav > button.selected {
    color: var(--text-primary) !important;
    background: rgba(139, 92, 246, 0.15) !important;
}

.tabs > .tab-nav > button.selected::after {
    width: 80%;
}

/* ===== INPUT FIELDS WITH GLOW ===== */
.prompt-input textarea,
.gr-textbox textarea,
.gr-input input {
    background: rgba(15, 15, 25, 0.6) !important;
    border: 1px solid var(--border-glass) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
}

.prompt-input textarea:focus,
.gr-textbox textarea:focus,
.gr-input input:focus {
    border-color: var(--aurora-violet) !important;
    box-shadow:
        0 0 0 3px rgba(139, 92, 246, 0.1),
        0 0 20px rgba(139, 92, 246, 0.15) !important;
    outline: none !important;
}

.prompt-input textarea::placeholder,
.gr-textbox textarea::placeholder {
    color: var(--text-muted) !important;
}

/* ===== OUTPUT SECTION ===== */
.output-section {
    background: linear-gradient(180deg, var(--surface-2) 0%, var(--surface-3) 100%) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    min-height: 450px !important;
    box-shadow: var(--shadow-soft) !important;
}

.output-section video {
    border-radius: 12px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
}

/* ===== GENERATION LOG ===== */
.generation-log textarea {
    font-family: 'JetBrains Mono', 'Monaco', 'Menlo', monospace !important;
    font-size: 0.85rem !important;
    background: rgba(10, 10, 15, 0.8) !important;
    border: 1px solid var(--border-glass) !important;
    border-radius: 10px !important;
    color: var(--aurora-cyan-light) !important;
    padding: 1rem !important;
    line-height: 1.6 !important;
}

/* ===== ACCORDIONS ===== */
.gr-accordion {
    background: linear-gradient(180deg, var(--surface-1) 0%, var(--surface-2) 100%) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

.gr-accordion > .label-wrap {
    background: rgba(59, 130, 246, 0.08) !important;
    border-bottom: 1px solid var(--border-soft) !important;
    padding: 1rem 1.25rem !important;
    transition: all 0.2s ease !important;
}

.gr-accordion > .label-wrap:hover {
    background: rgba(139, 92, 246, 0.1) !important;
}

.gr-accordion > .label-wrap .icon {
    color: var(--aurora-violet-light) !important;
}

/* ===== SLIDERS ===== */
.gr-slider input[type="range"] {
    accent-color: var(--aurora-violet) !important;
}

.gr-slider .range-slider {
    background: rgba(139, 92, 246, 0.2) !important;
}

.gr-slider .range-slider .thumb {
    background: var(--aurora-violet) !important;
    box-shadow: 0 0 10px var(--glow-violet) !important;
}

/* ===== DROPDOWNS ===== */
.gr-dropdown,
[data-testid="dropdown"] {
    background: rgba(15, 15, 25, 0.72) !important;
    border: 1px solid var(--border-glass) !important;
    border-radius: 10px !important;
    overflow: visible !important;
    position: relative;
}

.gr-dropdown:focus-within,
[data-testid="dropdown"]:focus-within {
    border-color: var(--aurora-violet) !important;
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.15) !important;
}

/* ===== DROPDOWN POSITIONING FIX (Floating UI) ===== */
[data-floating-ui-portal] {
    z-index: 100000 !important;
}

[data-floating-ui-portal] ul.options,
[data-floating-ui-portal] [role="listbox"],
.gr-dropdown ul.options,
.gr-dropdown [role="listbox"],
div[data-testid="dropdown"] ul.options,
div[data-testid="dropdown"] [role="listbox"] {
    z-index: 100000 !important;
    background: rgba(12, 14, 22, 0.98) !important;
    border: 1px solid var(--border-accent) !important;
    border-radius: 10px !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6) !important;
    max-height: min(320px, calc(100vh - 8rem)) !important;
    overflow-y: auto !important;
    overscroll-behavior: contain;
    padding: 0.25rem 0 !important;
}

/* Dropdown input clickable */
.gr-dropdown input,
.gr-dropdown button,
[data-testid="dropdown"] input {
    pointer-events: auto !important;
    position: relative !important;
    z-index: 10 !important;
}

/* Individual dropdown options styling */
.gr-dropdown li,
.gr-dropdown [role="option"],
div[data-testid="dropdown"] li,
div[data-testid="dropdown"] [role="option"],
ul.options li,
[role="option"] {
    color: var(--text-primary) !important;
    padding: 0.625rem 1rem !important;
    font-size: 0.92rem !important;
    line-height: 1.2 !important;
    cursor: pointer !important;
    transition: background 0.15s ease !important;
}

.gr-dropdown li:hover,
.gr-dropdown [role="option"]:hover,
div[data-testid="dropdown"] li:hover,
div[data-testid="dropdown"] [role="option"]:hover,
ul.options li:hover,
[role="option"]:hover {
    background: rgba(139, 92, 246, 0.2) !important;
}

.gr-dropdown li[aria-selected="true"],
.gr-dropdown [role="option"][aria-selected="true"],
ul.options li.selected,
[role="option"][aria-selected="true"] {
    background: rgba(139, 92, 246, 0.3) !important;
    color: var(--aurora-violet-light) !important;
}

/* ===== DROPDOWN OVERLAY FIX - Ensure dropdowns always open on top ===== */

/* Force dropdown containers to allow overflow */
.gr-group,
.gr-box,
.gradio-group,
[class*="group"],
.block {
    overflow: visible !important;
}

/* Ensure Gradio dropdown wrapper allows overflow */
.gr-dropdown,
[data-testid="dropdown"],
.svelte-dropdown,
.dropdown {
    overflow: visible !important;
    position: relative !important;
}

/* Target the actual dropdown popup/listbox with higher specificity */
.gr-dropdown .options,
.gr-dropdown ul,
.gr-dropdown [role="listbox"],
[data-testid="dropdown"] .options,
[data-testid="dropdown"] ul,
[data-testid="dropdown"] [role="listbox"],
.svelte-dropdown ul,
div[class*="dropdown"] ul {
    position: fixed !important;
    z-index: 999999 !important;
    background: rgba(12, 14, 22, 0.98) !important;
    border: 1px solid var(--border-accent) !important;
    border-radius: 10px !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6) !important;
    max-height: 300px !important;
    overflow-y: auto !important;
}

/* Floating UI portal - highest z-index */
[data-floating-ui-portal],
.floating-ui-portal,
[id*="floating"] {
    z-index: 999999 !important;
    position: fixed !important;
}

/* Ensure tab content doesn't clip dropdowns */
.tabs,
.tabitem,
.tab-content,
[role="tabpanel"] {
    overflow: visible !important;
}

/* ===== SCENE EDITOR (Dataframe) ===== */
.scene-editor {
    border-radius: 12px !important;
    border: 1px solid var(--border-soft) !important;
    background: var(--surface-1) !important;
    overflow: hidden !important;
    --gr-df-accent: var(--aurora-cyan);
}

/* Scrollable container styling */
.scene-editor .table-wrap {
    max-height: 350px !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    border-radius: 10px !important;
    scrollbar-gutter: stable;
}

/* Custom scrollbar for scene editor */
.scene-editor .table-wrap::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

.scene-editor .table-wrap::-webkit-scrollbar-track {
    background: rgba(15, 15, 25, 0.5);
    border-radius: 4px;
}

.scene-editor .table-wrap::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--aurora-violet), var(--aurora-cyan));
    border-radius: 4px;
}

.scene-editor table {
    background: transparent !important;
    width: 100% !important;
    table-layout: fixed !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
}

/* Sticky header */
.scene-editor thead {
    position: sticky !important;
    top: 0 !important;
    z-index: 10 !important;
}

.scene-editor th {
    background: rgba(139, 92, 246, 0.25) !important;
    color: var(--aurora-violet-light) !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.75rem 1rem !important;
    border-bottom: 2px solid var(--aurora-violet) !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

.scene-editor td {
    border-color: var(--border-glass) !important;
    padding: 0.625rem 0.75rem !important;
    color: var(--text-primary) !important;
    vertical-align: middle !important;
    border-bottom: 1px solid var(--border-glass) !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* Description column - allow wrapping */
.scene-editor td:nth-child(2) {
    max-width: 300px !important;
    white-space: normal !important;
    word-wrap: break-word !important;
    word-break: break-word !important;
    line-height: 1.4 !important;
    overflow: visible !important;
    text-overflow: clip !important;
}

.scene-editor tr:hover td {
    background: rgba(139, 92, 246, 0.12) !important;
}

/* Alternate row colors */
.scene-editor tbody tr:nth-child(even) td {
    background: rgba(255, 255, 255, 0.02) !important;
}

.scene-editor tbody tr:nth-child(even):hover td {
    background: rgba(139, 92, 246, 0.12) !important;
}

/* Input fields in cells */
.scene-editor input,
.scene-editor textarea {
    background: rgba(15, 15, 25, 0.6) !important;
    border: 1px solid var(--border-glass) !important;
    border-radius: 6px !important;
    color: var(--text-primary) !important;
    padding: 0.375rem 0.5rem !important;
}

.scene-editor input:focus,
.scene-editor textarea:focus {
    border-color: var(--aurora-violet) !important;
    box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
    outline: none !important;
}

/* ===== CHECKBOXES ===== */
.gr-checkbox input[type="checkbox"] {
    accent-color: var(--aurora-violet) !important;
}

/* ===== SCROLLBAR STYLING ===== */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(15, 15, 25, 0.5);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--aurora-violet), var(--aurora-cyan));
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, var(--aurora-violet-light), var(--aurora-cyan-light));
}

/* ===== LOADING/PROCESSING STATES ===== */
.generating {
    position: relative;
}

.generating::after {
    content: '';
    position: absolute;
    inset: -2px;
    border-radius: 14px;
    background: linear-gradient(90deg,
        var(--aurora-violet),
        var(--aurora-cyan),
        var(--aurora-pink),
        var(--aurora-violet));
    background-size: 300% 100%;
    animation: gradient-shift 2s linear infinite;
    z-index: -1;
    opacity: 0.7;
}

@keyframes gradient-shift {
    0% { background-position: 0% 50%; }
    100% { background-position: 300% 50%; }
}

/* ===== PULSE GLOW FOR ACTIVE STATES ===== */
@keyframes pulse-glow {
    0%, 100% {
        box-shadow: 0 0 20px var(--glow-violet);
    }
    50% {
        box-shadow: 0 0 40px var(--glow-violet), 0 0 60px var(--glow-cyan);
    }
}

.pulse-glow {
    animation: pulse-glow 2s ease-in-out infinite;
}

/* ===== FADE IN ANIMATION ===== */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-in {
    animation: fadeIn 0.5s ease-out forwards;
}

/* ===== STATUS INDICATOR ===== */
.status-indicator {
    padding: 0.75rem 1.25rem;
    border-radius: 10px;
    font-weight: 500;
    background: var(--bg-glass);
    border: 1px solid var(--border-glass);
}

.generation-status textarea,
.generation-status input {
    background: linear-gradient(180deg, rgba(6, 182, 212, 0.08), rgba(15, 23, 42, 0.9)) !important;
    border: 1px solid var(--border-soft) !important;
    color: var(--aurora-cyan-light) !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
}

/* ===== RESPONSIVE ADJUSTMENTS ===== */
@media (max-width: 768px) {
    .header-container {
        padding: 1.5rem !important;
    }

    .header-container h1 {
        font-size: 1.5rem !important;
    }

    .generate-btn {
        padding: 0.875rem 1.5rem !important;
        font-size: 1rem !important;
    }
}

/* ===== VIDEO PLAYER ENHANCEMENTS ===== */
video {
    border-radius: 12px !important;
}

.gr-video {
    background: transparent !important;
    border: 1px solid var(--border-glass) !important;
    border-radius: 14px !important;
    overflow: hidden !important;
}

/* ===== MARKDOWN STYLING ===== */
.gr-markdown h2,
.gr-markdown h3,
.gr-markdown h4 {
    color: var(--text-primary) !important;
    font-family: var(--font-display);
    font-weight: 600 !important;
    margin-top: 1.5rem !important;
}

.gr-markdown p, .gr-markdown li {
    color: var(--text-secondary) !important;
}

.gr-markdown code {
    background: rgba(139, 92, 246, 0.15) !important;
    color: var(--aurora-cyan-light) !important;
    padding: 0.2rem 0.5rem !important;
    border-radius: 4px !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ===== TOOLTIP STYLING ===== */
.gr-tooltip {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-accent) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
}
"""

# Custom JavaScript for micro-animations and interactions
CUSTOM_JS = """
<!-- Premium Google Fonts for Header -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700&family=Outfit:wght@400;500;600&display=swap" rel="stylesheet">

<style>
/* Premium Title Styling */
.aurora-title {
    font-family: var(--font-display) !important;
    font-size: 2.8rem !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #ffffff 0%, #a78bfa 40%, #22d3ee 70%, #f472b6 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    letter-spacing: -0.03em !important;
    margin: 0 0 0.75rem 0 !important;
    line-height: 1.1 !important;
    animation: title-glow 3s ease-in-out infinite alternate;
}

@keyframes title-glow {
    from {
        filter: drop-shadow(0 0 20px rgba(139, 92, 246, 0.4));
    }
    to {
        filter: drop-shadow(0 0 30px rgba(6, 182, 212, 0.5));
    }
}

.aurora-subtitle {
    font-family: var(--font-body) !important;
    color: #cbd5e1 !important;
    font-size: 1rem !important;
    font-weight: 400 !important;
    margin: 0 0 0.5rem 0 !important;
    letter-spacing: 0.01em !important;
}

.aurora-credits {
    font-family: var(--font-body) !important;
    color: #64748b !important;
    font-size: 0.85rem !important;
    font-weight: 400 !important;
    margin: 0 !important;
}

.aurora-credits a {
    color: #a78bfa !important;
    text-decoration: none !important;
    transition: color 0.2s ease !important;
}

.aurora-credits a:hover {
    color: #22d3ee !important;
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // ===== INTERSECTION OBSERVER FOR FADE-IN ANIMATIONS =====
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const fadeInObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                fadeInObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements for fade-in
    setTimeout(() => {
        document.querySelectorAll('.gr-group, .gr-accordion, .output-section').forEach(el => {
            el.style.opacity = '0';
            fadeInObserver.observe(el);
        });
    }, 100);

    // ===== RIPPLE EFFECT FOR BUTTONS =====
    function createRipple(event) {
        const button = event.currentTarget;
        const rect = button.getBoundingClientRect();

        const ripple = document.createElement('span');
        ripple.className = 'ripple';
        ripple.style.cssText = `
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
            pointer-events: none;
        `;

        const size = Math.max(rect.width, rect.height);
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = (event.clientX - rect.left - size / 2) + 'px';
        ripple.style.top = (event.clientY - rect.top - size / 2) + 'px';

        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    }

    // Add ripple CSS animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    // Attach ripple to buttons
    setTimeout(() => {
        document.querySelectorAll('.generate-btn, .secondary-btn').forEach(btn => {
            btn.addEventListener('click', createRipple);
        });
    }, 500);

    // ===== PARALLAX AURORA BACKGROUND =====
    let ticking = false;
    const auroraHost = document.querySelector('.gradio-container');
    document.addEventListener('mousemove', (e) => {
        if (!auroraHost) {
            return;
        }
        if (!ticking) {
            window.requestAnimationFrame(() => {
                const x = (e.clientX / window.innerWidth - 0.5) * 20;
                const y = (e.clientY / window.innerHeight - 0.5) * 20;
                document.documentElement.style.setProperty('--aurora-x', x + 'px');
                document.documentElement.style.setProperty('--aurora-y', y + 'px');
                ticking = false;
            });
            ticking = true;
        }
    });

    // ===== SMOOTH SCROLL FOR TAB NAVIGATION =====
    document.querySelectorAll('.tab-nav button').forEach(tab => {
        tab.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });

    // ===== GENERATE BUTTON PULSE ON PROMPT INPUT =====
    const promptInput = document.querySelector('.prompt-input textarea');
    const generateBtn = document.querySelector('.generate-btn');

    if (promptInput && generateBtn) {
        promptInput.addEventListener('input', () => {
            if (promptInput.value.trim().length > 10) {
                generateBtn.classList.add('pulse-glow');
            } else {
                generateBtn.classList.remove('pulse-glow');
            }
        });
    }

    // ===== DROPDOWN POSITIONING FIX (Floating UI recalculate) =====
    document.addEventListener('click', function(e) {
        if (e.target.closest('[data-testid="dropdown"]') || e.target.closest('.gr-dropdown')) {
            setTimeout(() => {
                window.dispatchEvent(new Event('resize'));
            }, 10);
        }
    });

    console.log('Aurora UI animations initialized');
});
</script>
"""


def get_available_models(provider: str) -> list[str]:
    """Fetch available models from LM Studio or Ollama."""
    try:
        if provider == "LM Studio":
            resp = requests.get(f"{LM_STUDIO_BASE}/models", timeout=5)
            resp.raise_for_status()
            return [m["id"] for m in resp.json().get("data", [])]
        elif provider == "Ollama":
            resp = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
            resp.raise_for_status()
            return [m["name"] for m in resp.json().get("models", [])]
    except Exception as e:
        print(f"Error fetching models: {e}")
    return []


def update_models(provider: str) -> gr.Dropdown:
    """Update model dropdown based on selected provider."""
    if provider == "None":
        return gr.Dropdown(choices=[], value=None, interactive=False)
    if provider not in VALID_LLM_PROVIDERS:
        return gr.Dropdown(choices=[], value=None, interactive=False)

    models = get_available_models(provider)
    return gr.Dropdown(
        choices=models,
        value=models[0] if models else None,
        interactive=True,
        allow_custom_value=True,
    )


def enhance_prompt_with_llm(
    prompt: str,
    provider: str,
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 500,
) -> str:
    """Use LLM to enhance the video prompt."""
    print(f"[DEBUG] enhance called: prompt='{prompt}', provider='{provider}', model='{model}'")

    if not prompt or not prompt.strip():
        gr.Warning("Voer eerst een prompt in!")
        return prompt or ""
    if not provider or provider == "None":
        gr.Warning("Selecteer eerst een LLM provider (LM Studio of Ollama)")
        return prompt
    if not model:
        gr.Warning("Selecteer eerst een model")
        return prompt

    gr.Info(f"Enhancing prompt met {provider}...")

    # System message that expands detail while preserving intent
    system_message = """Je bent een video+audio prompt engineer voor het LTX-2 model.

DOEL: Maak de prompt VEEL specifieker en rijker aan details, zonder de intentie te veranderen.
- Behoud onderwerp, actie, setting en stijl van de gebruiker
- Voeg concrete details toe als ze ontbreken (plausibel en consistent)
- Geef personen volledig detail: leeftijdsrange, lichaamsbouw, huidtint, haar, kleding, accessoires, houding, gezichtsuitdrukking
- Beschrijf omgeving: materialen, texturen, kleuren, weersomstandigheden, tijd van dag, props
- Camera: shot type, lens, afstand, beweging, compositie, depth of field
- Licht: richting, kwaliteit, kleurtemperatuur, schaduwen
- Audio: ambience, foley, ruimte/afstand, wind/briesje + wat het doet en hoe het klinkt
- Als er mensen zijn, voeg 1-2 korte dialogregels toe met spreker + taal/accent

STRUCTUUR: subject → action → setting → camera → lighting → audio → dialogue
Antwoord ALLEEN met de verbeterde prompt in het Engels, 1-2 korte paragrafen, geen uitleg."""

    try:
        if provider == "LM Studio":
            resp = requests.post(
                f"{LM_STUDIO_BASE}/chat/completions",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": f"Verbeter deze video prompt: {prompt}"}
                    ],
                    "temperature": float(temperature),
                    "max_tokens": int(max_tokens),
                },
                timeout=60
            )
            resp.raise_for_status()
            data = resp.json()
            choices = data.get("choices", [])
            if not choices or "message" not in choices[0]:
                gr.Warning("Unexpected LM Studio response format - originele prompt behouden")
                return prompt
            message = choices[0]["message"]
            result = message.get("content", "").strip()

            # Support reasoning models - use reasoning field if content is empty
            if not result and "reasoning" in message:
                reasoning = message["reasoning"]
                print(f"[DEBUG] Using reasoning field")
                # Look for quoted text that looks like an improved prompt
                quotes = re.findall(r'"([^"]{20,})"', reasoning)
                if quotes:
                    result = quotes[-1]  # Take the last (most complete) quote
                else:
                    # Take last meaningful sentence
                    sentences = [s.strip() for s in reasoning.split('.') if len(s.strip()) > 30]
                    if sentences:
                        result = sentences[-1]

            print(f"[DEBUG] LM Studio result: '{result[:100]}...'")
            if not result:
                gr.Warning("LLM gaf lege response - originele prompt behouden")
                return prompt
            gr.Info("Prompt enhanced!")
            return result

        elif provider == "Ollama":
            resp = requests.post(
                f"{OLLAMA_BASE}/api/chat",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": f"Verbeter deze video prompt: {prompt}"}
                    ],
                    "stream": False,
                    "options": {
                        "temperature": float(temperature),
                        "num_predict": int(max_tokens),
                    },
                },
                timeout=60
            )
            resp.raise_for_status()
            data = resp.json()
            result = data.get("message", {}).get("content", "").strip()
            print(f"[DEBUG] Ollama result: '{result}'")
            if not result:
                gr.Warning("LLM gaf lege response - originele prompt behouden")
                return prompt
            gr.Info("Prompt enhanced!")
            return result

    except Exception as e:
        print(f"[DEBUG] Error: {e}")
        gr.Warning(f"LLM error: {e}")
        return prompt

    return prompt


def apply_resolution_preset(preset: str, current_width: int, current_height: int):
    """Apply resolution preset or keep custom values."""
    if preset == "Custom" or preset not in RESOLUTION_PRESETS:
        return current_width, current_height
    resolution = RESOLUTION_PRESETS[preset]
    if resolution:
        return resolution[0], resolution[1]
    return current_width, current_height


def apply_duration_preset(preset: str, current_frames: int):
    """Apply duration preset or keep custom value."""
    if preset == "Custom" or preset not in DURATION_PRESETS:
        return current_frames
    frames = DURATION_PRESETS[preset]
    if frames:
        return frames
    return current_frames


def randomize_seed():
    """Generate a random seed."""
    return random.randint(0, 2147483647)


def build_prompt_from_components(
    camera: str,
    lighting: str,
    environment: str,
    subject: str,
    action: str,
    ambient: str,
    foley: str,
    music: str,
    speech: str,
    speech_language: str,
    speech_accent: str
) -> str:
    """Build a structured prompt from individual components.

    Based on LTX-2 paper's optimal prompt structure:
    1. Begin with subject
    2. Add action
    3. Describe camera movement
    4. Lighting details
    5. Audio cues (with language/accent for speech)
    6. Mood/atmosphere

    Args:
        camera: Camera motion (e.g., "Pan left", "Tracking shot")
        lighting: Lighting style (e.g., "Golden hour", "Dramatic shadows")
        environment: Scene environment description
        subject: Subject description
        action: Action being performed
        ambient: Ambient sounds
        foley: Foley/sound effects
        music: Music description
        speech: Speech/dialogue description
        speech_language: Language for speech (LTX-2 paper feature)
        speech_accent: Accent for speech (LTX-2 paper feature)

    Returns:
        Formatted prompt string optimized for LTX-2
    """
    parts = []

    # Visual elements
    if subject:
        parts.append(subject.strip())
    if action:
        parts.append(action.strip())
    if environment:
        parts.append(f"in {environment.strip()}")
    if camera and camera != "Static":
        parts.append(f"camera {camera.lower()}")
    if lighting:
        parts.append(f"{lighting.lower()} lighting")

    # Join visual parts
    visual_text = ", ".join(parts) if parts else ""

    # Audio elements
    audio_parts = []
    if ambient:
        audio_parts.append(ambient.strip())
    if foley:
        audio_parts.append(foley.strip())
    if music:
        audio_parts.append(music.strip())

    # Build speech with language/accent (LTX-2 paper: "speaker, language, and accent identification")
    if speech:
        speech_desc = speech.strip()
        # Add language and accent if specified
        lang_accent_parts = []
        if speech_language and speech_language != "No specific language":
            lang_accent_parts.append(speech_language)
        if speech_accent and speech_accent != "No specific accent":
            lang_accent_parts.append(f"{speech_accent} accent")
        if lang_accent_parts:
            speech_desc = f"{speech_desc} in {', '.join(lang_accent_parts)}"
        audio_parts.append(speech_desc)

    # Combine visual and audio
    if visual_text and audio_parts:
        return f"{visual_text}. Audio: {', '.join(audio_parts)}."
    elif visual_text:
        return f"{visual_text}."
    elif audio_parts:
        return f"Audio: {', '.join(audio_parts)}."
    else:
        return ""


def apply_cfg_preset(preset: str):
    """Apply CFG preset values.

    Args:
        preset: Name of the preset

    Returns:
        Tuple of (text_cfg, cross_modal_cfg) values or (gr.update(), gr.update()) for Custom
    """
    if preset == "Custom" or preset not in CFG_PRESET_VALUES or CFG_PRESET_VALUES[preset] is None:
        return gr.update(), gr.update()
    values = CFG_PRESET_VALUES[preset]
    return values["text_cfg"], values["cross_modal_cfg"]


# ===== MOVIE GENERATOR HELPER FUNCTIONS =====

def get_pacing_seconds(pacing: str | None) -> int:
    """Get average scene duration based on pacing selection."""
    if pacing in MOVIE_PACING_PRESETS:
        return MOVIE_PACING_PRESETS[pacing]
    return MOVIE_PACING_PRESETS["Standard (12s avg)"]


def build_scene_prompt(
    theme: str,
    num_scenes: int,
    structure: str,
    pacing: str,
    story_summary: str,
    recent_scenes: list[dict],
    pacing_seconds: int,
) -> str:
    """Build a prompt for generating one or more scenes."""
    recent_text = ""
    if recent_scenes:
        recent_lines = [f"- {s.get('description', '')}" for s in recent_scenes]
        recent_text = "\n".join(recent_lines)

    structure_text = structure if structure and structure != "None" else "None"

    return f"""Movie theme: {theme}

Story structure: {structure_text}
Pacing: {pacing}

Story so far (summary):
{story_summary or "None"}

Recent scenes:
{recent_text or "None"}

Create EXACTLY {num_scenes} new scenes that continue the story.
Each scene MUST include:
- description: full visual + audio description (subject, action, camera movement, lighting, sound)
- include micro details like breeze direction + effect, fabric rustle, reflections, small sounds
- if characters appear, fully describe them (appearance, wardrobe, expression) and include spoken dialogue lines
- visual_style: cinematic look (lens, palette, grain, depth of field)
- audio_style: score/foley/soundscape style and intensity
- characters: names, roles, relationships, voice/accent
- setting: time period, locations, mood, key props
- Continuity rule: start with a shared anchor from the previous scene and end with a hook for the next

Duration rules:
- Aim for ~{pacing_seconds}s per scene
- Hard max: {MAX_SCENE_DURATION}s
- Use integers for duration

Output ONLY a valid JSON array of objects with keys:
"description", "duration", "visual_style", "audio_style", "characters", "setting".
"""


def summarize_story_so_far(
    existing_summary: str,
    new_scenes: list[dict],
    provider: str,
    model: str | None,
    temperature: float,
) -> str:
    """Summarize story so far using the configured LLM."""
    if provider not in VALID_LLM_PROVIDERS or not model:
        return existing_summary

    scene_lines = "\n".join([f"- {s.get('description', '')}" for s in new_scenes])
    prompt = f"""Update the story summary in 6-8 sentences.

Existing summary:
{existing_summary or "None"}

New scenes:
{scene_lines}

Return only the updated summary plus a short bullet list of current characters and locations."""

    messages = [
        {"role": "system", "content": "You summarize movie plots for continuity."},
        {"role": "user", "content": prompt},
    ]

    try:
        if provider == "LM Studio":
            resp = requests.post(
                f"{LM_STUDIO_BASE}/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": float(temperature),
                    "max_tokens": 400,
                },
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            choices = data.get("choices", [])
            if not choices or "message" not in choices[0]:
                return existing_summary
            response = choices[0]["message"].get("content", "").strip()
        else:
            resp = requests.post(
                f"{OLLAMA_BASE}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": float(temperature), "num_predict": 400},
                },
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            response = data.get("message", {}).get("content", "").strip()

        return response or existing_summary
    except Exception as e:
        print(f"[DEBUG] Summary error: {e}")
        return existing_summary


def calculate_scenes_from_duration(total_duration: int, pacing: str) -> int:
    """Calculate number of scenes based on total movie duration."""
    avg_scene_duration = get_pacing_seconds(pacing)
    num_scenes = max(1, min(MAX_SCENES, int(total_duration / avg_scene_duration)))
    return num_scenes


def extract_frame_ffmpeg(video_path: str, output_path: str, position: str = "last") -> bool:
    """Extract a frame from video using FFmpeg.

    Args:
        video_path: Path to input video
        output_path: Path for output image
        position: "first" or "last" frame

    Returns:
        True if successful, False otherwise
    """
    import subprocess

    try:
        if position == "first":
            # Extract first frame
            cmd = [
                "ffmpeg", "-y", "-i", video_path,
                "-vf", "select=eq(n\\,0)",
                "-vframes", "1",
                output_path
            ]
        else:
            # Extract last frame
            cmd = [
                "ffmpeg", "-y", "-sseof", "-1", "-i", video_path,
                "-update", "1", "-q:v", "1",
                output_path
            ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return os.path.exists(output_path)
    except Exception as e:
        print(f"[DEBUG] Frame extraction error: {e}")
        return False


def merge_videos_ffmpeg(video_paths: list[str], output_path: str, fps: int = 24) -> bool:
    """Merge multiple videos using FFmpeg concat demuxer.

    Args:
        video_paths: List of video file paths
        output_path: Output path for merged video
        fps: Frames per second for output

    Returns:
        True if successful, False otherwise
    """
    import subprocess

    if not video_paths:
        return False

    # Create concat file
    concat_file = os.path.join(tempfile.gettempdir(), f"concat_{uuid.uuid4().hex[:8]}.txt")
    try:
        with open(concat_file, "w") as f:
            for vp in video_paths:
                # Escape single quotes in path
                escaped_path = vp.replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")

        # Run FFmpeg concat
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-r", str(fps),
            "-pix_fmt", "yuv420p",
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode != 0:
            print(f"[DEBUG] FFmpeg merge error: {result.stderr}")
            return False

        return os.path.exists(output_path)

    except Exception as e:
        print(f"[DEBUG] Merge error: {e}")
        return False
    finally:
        # Cleanup concat file
        if os.path.exists(concat_file):
            os.remove(concat_file)


def scenes_to_dataframe(scenes: list[dict]) -> list[list]:
    """Convert scenes list to Gradio dataframe format.

    Args:
        scenes: List of scene dicts with description, duration, status

    Returns:
        List of lists for Gradio Dataframe
    """
    result = []
    for i, scene in enumerate(scenes):
        result.append([
            i + 1,  # Scene number
            scene.get("description", ""),
            scene.get("duration", DEFAULT_SCENE_DURATION),
            scene.get("status", "pending"),
            scene.get("visual_style", ""),
            scene.get("audio_style", ""),
            scene.get("characters", ""),
            scene.get("setting", ""),
        ])
    return result


def dataframe_to_scenes(df_data) -> list[dict]:
    """Convert Gradio dataframe back to scenes list.

    Handles both pandas DataFrame and list[list] formats.

    Args:
        df_data: List of lists or pandas DataFrame from Gradio Dataframe

    Returns:
        List of scene dicts
    """
    # Convert pandas DataFrame to list[list] if needed
    if hasattr(df_data, 'values'):
        # It's a pandas DataFrame - convert to list of lists
        df_data = df_data.values.tolist()

    if df_data is None or len(df_data) == 0:
        return []

    scenes = []
    for row in df_data:
        if len(row) >= 3:
            # Parse duration - handle strings like "5s", "5", or just numbers
            duration_val = row[2]
            try:
                if isinstance(duration_val, (int, float)):
                    duration = int(duration_val)
                elif duration_val:
                    # Extract numeric part from strings like "5s"
                    duration_str = str(duration_val).strip().rstrip('s').strip()
                    duration = int(duration_str) if duration_str else DEFAULT_SCENE_DURATION
                else:
                    duration = DEFAULT_SCENE_DURATION
            except (ValueError, TypeError):
                duration = DEFAULT_SCENE_DURATION

            scenes.append({
                "description": str(row[1]) if row[1] else "",
                "duration": duration,
                "status": str(row[3]) if len(row) > 3 and row[3] else "pending",
                "visual_style": str(row[4]) if len(row) > 4 and row[4] else "",
                "audio_style": str(row[5]) if len(row) > 5 and row[5] else "",
                "characters": str(row[6]) if len(row) > 6 and row[6] else "",
                "setting": str(row[7]) if len(row) > 7 and row[7] else "",
            })
    return scenes


def build_scene_generation_prompt(scene: dict) -> str:
    """Build the final prompt text for a scene using per-scene fields."""
    description = str(scene.get("description", "") or "").strip()
    extras = []
    visual_style = str(scene.get("visual_style", "") or "").strip()
    audio_style = str(scene.get("audio_style", "") or "").strip()
    characters = str(scene.get("characters", "") or "").strip()
    setting = str(scene.get("setting", "") or "").strip()

    if visual_style:
        extras.append(f"Visual style: {visual_style}")
    if audio_style:
        extras.append(f"Audio style: {audio_style}")
    if characters:
        extras.append(f"Characters: {characters}")
    if setting:
        extras.append(f"Setting / World: {setting}")

    if extras:
        extra_text = "\n".join(extras)
        if description:
            return f"{description}\n\n{extra_text}"
        return extra_text
    return description


def add_empty_scene(scenes: list[dict]) -> list[dict]:
    """Add an empty scene to the list."""
    scenes = scenes.copy()
    scenes.append({
        "description": "New scene - edit this description",
        "duration": DEFAULT_SCENE_DURATION,
        "status": "pending",
        "visual_style": "",
        "audio_style": "",
        "characters": "",
        "setting": "",
    })
    return scenes


def remove_scene_at_index(scenes: list[dict], index: int) -> list[dict]:
    """Remove scene at specified index (1-based)."""
    scenes = scenes.copy()
    idx = index - 1  # Convert to 0-based
    if 0 <= idx < len(scenes):
        scenes.pop(idx)
    return scenes


# ===== SCRIPT MANAGEMENT FUNCTIONS =====
def save_script(name: str, theme: str, scenes: list, settings: dict) -> str:
    """Save script to JSON file.

    Args:
        name: Script name
        theme: Movie theme/prompt
        scenes: List of scene dictionaries
        settings: Video settings (width, height, fps)

    Returns:
        Status message
    """
    script = {
        "name": name,
        "theme": theme,
        "created": datetime.now().isoformat(),
        "settings": settings,
        "scenes": scenes
    }
    # Create safe filename
    safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in name)
    filepath = SCRIPTS_DIR / f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filepath, 'w') as f:
        json.dump(script, f, indent=2)
    return f"✅ Script saved: {filepath.name}"


def load_script(filepath: str) -> tuple:
    """Load script from JSON file.

    Args:
        filepath: Path to script JSON file

    Returns:
        Tuple of (theme, scenes, settings)
    """
    with open(filepath, 'r') as f:
        script = json.load(f)
    return script.get("theme", ""), script.get("scenes", []), script.get("settings", {})


def list_scripts() -> list:
    """List all saved scripts.

    Returns:
        List of script metadata dictionaries
    """
    scripts = []
    for f in sorted(SCRIPTS_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            with open(f, 'r') as file:
                data = json.load(file)
                scripts.append({
                    "filename": f.name,
                    "path": str(f),
                    "name": data.get("name", f.stem),
                    "theme": data.get("theme", "")[:50],
                    "scenes": len(data.get("scenes", [])),
                    "created": data.get("created", "")[:10]
                })
        except Exception:
            continue
    return scripts


def delete_script(filepath: str) -> str:
    """Delete a script file.

    Args:
        filepath: Path to script file

    Returns:
        Status message
    """
    Path(filepath).unlink()
    return "🗑️ Script deleted"


def enhance_scene_with_gemma(scene_description: str, temperature: float = 0.7, max_tokens: int = 512) -> str:
    """Enhance a single scene description using abliterated Gemma 3.

    Uses mlx-community/gemma-3-12b-it-qat-abliterated-lm-4bit for unrestricted prompt enhancement.
    Based on LTX-2 paper: "Comprehensive yet factual, describing only what is seen and heard"

    Args:
        scene_description: Original scene description from LLM
        temperature: Gemma temperature
        max_tokens: Maximum tokens for response

    Returns:
        Enhanced scene description optimized for LTX-2
    """
    try:
        enhance_prompt = f"""Enhance this scene description for LTX-2 video generation.

RULES (LTX-2 paper + high detail):
1. Be COMPREHENSIVE but FACTUAL; expand to high detail without changing intent
2. Visuals: subject appearance (age range, build, hair, clothing, textures), action, micro-actions, environment materials/props, weather, time of day
3. Camera: shot size, lens, movement, angle, framing, depth of field
4. Lighting/color: direction, quality, color temperature, shadows, reflections
5. Audio: ambience, foley, room tone, wind/briesje with effects, music or "no music"
6. Dialogue: include actual spoken lines with speaker + language/accent; if no speech, say "No dialogue."
7. Preserve continuity cues already present (location, time, ongoing actions); do NOT introduce new story events or characters
8. No interpretation or emotions unless shown physically; describe only what is seen/heard
9. Target length: 80-180 words, concrete and specific

ORIGINAL SCENE:
{scene_description}

ENHANCED SCENE (only the description, no explanation):"""

        enhanced = generate_with_abliterated_gemma(
            enhance_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )

        # Clean up the response - remove any prefix text
        enhanced = enhanced.strip()

        # Remove common prefixes that Gemma might add
        prefixes_to_remove = [
            "ENHANCED SCENE:",
            "Enhanced Scene:",
            "Here is the enhanced scene:",
            "Here's the enhanced scene:",
        ]
        for prefix in prefixes_to_remove:
            if enhanced.startswith(prefix):
                enhanced = enhanced[len(prefix):].strip()

        if enhanced:
            return enhanced

    except Exception as e:
        print(f"[DEBUG] Gemma enhancement error: {e}")

    return scene_description


def enhance_scene_with_llm(
    scene_description: str,
    provider: str,
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 512,
) -> str:
    """Enhance a single scene description using LM Studio or Ollama."""
    try:
        enhance_prompt = f"""Enhance this scene description for LTX-2 video generation.

RULES (LTX-2 paper + high detail):
1. Be COMPREHENSIVE but FACTUAL; expand to high detail without changing intent
2. Visuals: subject appearance (age range, build, hair, clothing, textures), action, micro-actions, environment materials/props, weather, time of day
3. Camera: shot size, lens, movement, angle, framing, depth of field
4. Lighting/color: direction, quality, color temperature, shadows, reflections
5. Audio: ambience, foley, room tone, wind/briesje with effects, music or "no music"
6. Dialogue: include actual spoken lines with speaker + language/accent; if no speech, say "No dialogue."
7. Preserve continuity cues already present (location, time, ongoing actions); do NOT introduce new story events or characters
8. No interpretation or emotions unless shown physically; describe only what is seen/heard
9. Target length: 80-180 words, concrete and specific

ORIGINAL SCENE:
{scene_description}

ENHANCED SCENE (only the description, no explanation):"""

        messages = [
            {"role": "system", "content": "You are a precise LTX-2 scene enhancer."},
            {"role": "user", "content": enhance_prompt},
        ]

        if provider == "LM Studio":
            resp = requests.post(
                f"{LM_STUDIO_BASE}/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": float(temperature),
                    "max_tokens": int(max_tokens),
                },
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            choices = data.get("choices", [])
            if not choices or "message" not in choices[0]:
                gr.Warning("Unexpected LM Studio response format")
                return scene_description
            message = choices[0]["message"]
            response = message.get("content", "").strip()
            if not response and "reasoning" in message:
                response = message.get("reasoning", "").strip()

        elif provider == "Ollama":
            resp = requests.post(
                f"{OLLAMA_BASE}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": float(temperature),
                        "num_predict": int(max_tokens),
                    },
                },
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            response = data.get("message", {}).get("content", "").strip()
        else:
            return scene_description

        response = response.strip()
        prefixes_to_remove = [
            "ENHANCED SCENE:",
            "Enhanced Scene:",
            "Here is the enhanced scene:",
            "Here's the enhanced scene:",
        ]
        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()

        return response or scene_description

    except Exception as e:
        print(f"[DEBUG] LLM scene enhancement error: {e}")
        gr.Warning(f"LLM error: {e}")
        return scene_description


def enhance_scene_description(
    scene_description: str,
    prompt_enhancer_choice: str,
    provider: str,
    model: str | None,
    temperature: float,
    max_tokens: int,
) -> str:
    """Enhance scenes using global settings."""
    if provider in VALID_LLM_PROVIDERS:
        if not model:
            gr.Warning("Select an LLM model in Advanced Settings")
            return scene_description
        return enhance_scene_with_llm(scene_description, provider, model, temperature, max_tokens)
    if prompt_enhancer_choice == "Gemma (Built-in)":
        return enhance_scene_with_gemma(scene_description, temperature=temperature, max_tokens=max_tokens)
    if prompt_enhancer_choice == "LLM (Ollama/LM Studio)":
        gr.Warning("Select an LLM provider in Advanced Settings")
    return scene_description


def resolve_prompt_enhancement(
    prompt: str,
    enhance_prompt: bool,
    prompt_enhancer_choice: str,
    provider: str,
    model: str | None,
    temperature: float,
    max_tokens: int,
) -> tuple[str, bool]:
    """Return (prompt, use_builtin_enhancer) based on global LLM settings."""
    if not enhance_prompt:
        return prompt, False
    if provider in VALID_LLM_PROVIDERS:
        if not model:
            gr.Warning("Select an LLM model in Advanced Settings")
            return prompt, False
        enhanced = enhance_prompt_with_llm(
            prompt,
            provider,
            model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return enhanced, False
    if prompt_enhancer_choice == "LLM (Ollama/LM Studio)":
        gr.Warning("Select an LLM provider in Advanced Settings")
        return prompt, False
    return prompt, True


def generate_scenes_with_llm(
    theme: str,
    num_scenes: int,
    provider: str,
    model: str,
    structure: str,
    pacing: str,
    prompt_enhancer_choice: str,
    story_summary: str = "",
    recent_scenes: list[dict] | None = None,
    enhance_with_gemma: bool = True,
    temperature: float = 0.7,
    max_tokens: int | None = None,
) -> list[dict]:
    """Generate scene descriptions using LLM, then enhance using global settings.

    Args:
        theme: Main theme/idea for the movie
        num_scenes: Number of scenes to generate
        provider: "LM Studio" or "Ollama"
        model: Model name
        enhance_with_gemma: Whether to enhance each scene after LLM generation
        temperature: LLM temperature
        max_tokens: Maximum tokens for response (None = no limit)

    Returns:
        List of scene dicts with description, duration, status
    """
    pacing_seconds = get_pacing_seconds(pacing)
    user_prompt = build_scene_prompt(
        theme,
        num_scenes,
        structure,
        pacing,
        story_summary,
        recent_scenes or [],
        pacing_seconds,
    )

    try:
        # Always use external LLM for script writing
        if not provider or provider == "None":
            gr.Warning("Select an LLM provider first")
            return []
        if not model:
            gr.Warning("Select a model first")
            return []

        gr.Info(f"Step 1: Generating script with {provider}...")

        messages = [
            {"role": "system", "content": SCENE_WRITER_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        if provider == "LM Studio":
            request_body = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                **({"max_tokens": max_tokens} if max_tokens else {})
            }
            resp = requests.post(
                f"{LM_STUDIO_BASE}/chat/completions",
                json=request_body,
                timeout=120
            )
            resp.raise_for_status()
            data = resp.json()
            choices = data.get("choices", [])
            if not choices or "message" not in choices[0]:
                gr.Warning("Unexpected LM Studio response format")
                return []
            message = choices[0]["message"]
            response = message.get("content", "")

            # Handle reasoning models: try reasoning field if content is empty or has no JSON
            if not response.strip() or not re.search(r'\[', response):
                reasoning = message.get("reasoning", "")
                if reasoning and re.search(r'\[[\s\S]*?"description"[\s\S]*?\]', reasoning):
                    response = reasoning

        elif provider == "Ollama":
            resp = requests.post(
                f"{OLLAMA_BASE}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False
                },
                timeout=120
            )
            resp.raise_for_status()
            data = resp.json()
            response = data.get("message", {}).get("content", "")
        else:
            gr.Warning(f"Unknown provider: {provider}")
            return []

        # Parse JSON from response
        response = response.strip()

        # Try to extract JSON array from response
        json_match = re.search(r'\[[\s\S]*\]', response)
        if json_match:
            json_str = json_match.group(0)
            scenes_data = json.loads(json_str)

            # Validate and normalize scenes
            scenes = []
            for scene in scenes_data:
                if isinstance(scene, dict) and "description" in scene:
                    duration = scene.get("duration", pacing_seconds)
                    duration = max(1, min(MAX_SCENE_DURATION, int(duration)))
                    scenes.append({
                        "description": scene["description"],
                        "duration": duration,
                        "status": "pending",
                        "visual_style": scene.get("visual_style", ""),
                        "audio_style": scene.get("audio_style", ""),
                        "characters": scene.get("characters", ""),
                        "setting": scene.get("setting", ""),
                    })

            if scenes:
                gr.Info(f"LLM generated {len(scenes)} scenes!")

                # Step 2: Enhance scenes if enabled
                if enhance_with_gemma:
                    gr.Info("Step 2: Enhancing scenes...")
                    enhance_tokens = int(max_tokens) if max_tokens else 512
                    for i, scene in enumerate(scenes):
                        enhanced_desc = enhance_scene_description(
                            scene["description"],
                            prompt_enhancer_choice,
                            provider,
                            model,
                            temperature=temperature,
                            max_tokens=enhance_tokens,
                        )
                        scenes[i]["description"] = enhanced_desc
                        scenes[i]["status"] = "enhanced"
                    gr.Info(f"Enhanced {len(scenes)} scenes!")

                return scenes

        gr.Warning("Could not parse scene data from LLM response")
        return []

    except json.JSONDecodeError as e:
        gr.Warning(f"JSON parse error: {e}")
        return []
    except requests.RequestException as e:
        gr.Warning(f"LLM request failed: {e}")
        return []
    except Exception as e:
        gr.Warning(f"Scene generation error: {e}")
        return []


def generate_scenes_in_batches(
    theme: str,
    num_scenes: int,
    provider: str,
    model: str,
    structure: str,
    pacing: str,
    prompt_enhancer_choice: str,
    enhance_with_gemma: bool = True,
    temperature: float = 0.7,
    max_tokens: int | None = None,
    progress=None,
) -> Generator[tuple[list[dict], str], None, None]:
    """Generate scenes in batches for long films."""
    if not provider or provider == "None":
        gr.Warning("Select an LLM provider first")
        yield [], "Error: No LLM provider selected"
        return
    if not model:
        gr.Warning("Select a model first")
        yield [], "Error: No model selected"
        return

    scenes: list[dict] = []
    story_summary = ""
    batch_size = 20 if num_scenes <= 200 else 30
    total_batches = (num_scenes + batch_size - 1) // batch_size

    for batch_index in range(total_batches):
        if progress:
            progress((batch_index, total_batches), desc=f"Generating batch {batch_index + 1}/{total_batches}")

        remaining = num_scenes - len(scenes)
        count = min(batch_size, remaining)
        recent_scenes = scenes[-6:] if scenes else []

        batch_scenes = generate_scenes_with_llm(
            theme,
            count,
            provider,
            model,
            structure,
            pacing,
            prompt_enhancer_choice,
            story_summary=story_summary,
            recent_scenes=recent_scenes,
            enhance_with_gemma=False,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if not batch_scenes:
            yield scenes, f"Batch {batch_index + 1}: failed to generate scenes"
            continue

        scenes.extend(batch_scenes)

        if num_scenes > 60:
            story_summary = summarize_story_so_far(
                story_summary,
                batch_scenes,
                provider,
                model,
                temperature,
            )

        yield scenes, f"Generated {len(scenes)}/{num_scenes} scenes"

    if enhance_with_gemma and scenes:
        yield scenes, "Enhancing all scenes..."
        for i, scene in enumerate(scenes):
            if progress:
                progress((i, len(scenes)), desc=f"Enhancing scene {i + 1}/{len(scenes)}")
            enhanced_desc = enhance_scene_description(
                scene["description"],
                prompt_enhancer_choice,
                provider,
                model,
                temperature=temperature,
                max_tokens=int(max_tokens) if max_tokens else 512,
            )
            scenes[i]["description"] = enhanced_desc
            scenes[i]["status"] = "enhanced"
            yield scenes, f"Enhanced scene {i + 1}/{len(scenes)}"

    yield scenes, "All scenes ready for generation!"


def extract_scene_json(response: str) -> dict | None:
    """Extract scene JSON from LLM response with multiple strategies.

    Handles cases like:
    - Clean JSON output
    - JSON wrapped in markdown code blocks
    - Truncated JSON (recovers description with default duration)
    - JSON in reasoning field for reasoning models

    Args:
        response: Raw LLM response text

    Returns:
        Parsed scene dict with 'description' and 'duration', or None if extraction fails
    """
    if not response:
        return None

    # Strategy 1: Find JSON with "description" key (most specific for single objects)
    match = re.search(r'\{[^{}]*"description"\s*:\s*"[^"]*"[^{}]*\}', response)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Strategy 2: Find any complete JSON object and check for description
    match = re.search(r'\{[^{}]*\}', response)
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, dict) and "description" in data:
                return data
        except json.JSONDecodeError:
            pass

    # Strategy 3: Handle nested JSON (greedy match but validate)
    match = re.search(r'\{[\s\S]*\}', response)
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, dict) and "description" in data:
                return data
        except json.JSONDecodeError:
            pass

    # Strategy 4: Try to repair truncated JSON
    # Find start of JSON with description and extract what we can
    match = re.search(r'\{"description"\s*:\s*"([^"]*)', response)
    if match:
        desc = match.group(1)
        if desc.strip():  # Only if we got a non-empty description
            return {"description": desc, "duration": 8}

    # Strategy 5: Extract description from malformed JSON-like text
    match = re.search(r'"description"\s*:\s*"([^"]+)"', response)
    if match:
        desc = match.group(1)
        # Try to find duration too
        duration_match = re.search(r'"duration"\s*:\s*(\d+)', response)
        duration = int(duration_match.group(1)) if duration_match else 8
        return {"description": desc, "duration": duration}

    return None




def generate_scenes_sequentially(
    theme: str,
    num_scenes: int,
    provider: str,
    model: str,
    structure: str,
    pacing: str,
    prompt_enhancer_choice: str,
    enhance_with_gemma: bool = True,
    temperature: float = 0.7,
    max_tokens: int | None = None,
    progress=None
) -> Generator[tuple[list[dict], str], None, None]:
    """
    Generate scenes sequentially with story continuity.

    Workflow:
    1. For each scene: generate with context of previous scenes
    2. After all scenes: apply enhancement using global settings
    3. Yield updates for live UI feedback

    Args:
        theme: Main theme/idea for the movie
        num_scenes: Number of scenes to generate
        provider: "LM Studio" or "Ollama"
        model: Model name
        enhance_with_gemma: Whether to enhance each scene after all are generated
        temperature: LLM temperature
        max_tokens: Maximum tokens for response (None = no limit)
        progress: Optional Gradio progress object

    Yields:
        Tuple of (scenes list, status message)
    """
    if not provider or provider == "None":
        gr.Warning("Select an LLM provider first")
        yield [], "Error: No LLM provider selected"
        return
    if not model:
        gr.Warning("Select a model first")
        yield [], "Error: No model selected"
        return

    scenes = []
    story_summary = ""
    context_limit = 6
    pacing_seconds = get_pacing_seconds(pacing)
    MAX_RETRIES = 3

    # Step 1: Sequential Scene Generation
    for i in range(num_scenes):
        if progress:
            progress((i, num_scenes), desc=f"Generating scene {i+1}/{num_scenes}")

        recent_scenes = scenes[-context_limit:] if scenes else []
        context = build_scene_prompt(
            theme,
            1,
            structure,
            pacing,
            story_summary,
            recent_scenes,
            pacing_seconds,
        )

        # Build prompt for this scene
        user_prompt = f"""{context}
Now write Scene {i+1} of {num_scenes}.
Continue the story naturally and maintain continuity.
If this is not Scene 1, open with a continuity anchor from the prior scene (sound, motion, object) and end with a hook for the next.
Return ONLY a JSON object: {{"description": "...", "duration": N, "visual_style": "...", "audio_style": "...", "characters": "...", "setting": "..."}}"""

        # Retry loop for robustness
        scene_generated = False
        for attempt in range(MAX_RETRIES):
            try:
                # Call LLM for single scene
                messages = [
                    {"role": "system", "content": SEQUENTIAL_SCENE_WRITER_PROMPT},
                    {"role": "user", "content": user_prompt}
                ]

                response = ""
                if provider == "LM Studio":
                    request_body = {
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        **({"max_tokens": max_tokens} if max_tokens else {})
                    }
                    resp = requests.post(
                        f"{LM_STUDIO_BASE}/chat/completions",
                        json=request_body,
                        timeout=120
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    choices = data.get("choices", [])
                    if not choices or "message" not in choices[0]:
                        gr.Warning("Unexpected LM Studio response format")
                        yield scenes, f"Error: Unexpected LM Studio response"
                        return
                    message = choices[0]["message"]
                    response = message.get("content", "")

                    # Handle reasoning models: try reasoning field if content is empty or has no JSON
                    if not response.strip() or not re.search(r'\{', response):
                        reasoning = message.get("reasoning", "")
                        if reasoning and re.search(r'\{[\s\S]*?"description"[\s\S]*?\}', reasoning):
                            response = reasoning

                elif provider == "Ollama":
                    resp = requests.post(
                        f"{OLLAMA_BASE}/api/chat",
                        json={
                            "model": model,
                            "messages": messages,
                            "stream": False
                        },
                        timeout=120
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    response = data.get("message", {}).get("content", "")
                else:
                    gr.Warning(f"Unknown provider: {provider}")
                    yield scenes, f"Error: Unknown provider {provider}"
                    return

                # Parse JSON from response using multi-strategy extraction
                response = response.strip()
                scene_data = extract_scene_json(response)

                if scene_data and "description" in scene_data:
                    duration = scene_data.get("duration", pacing_seconds)
                    duration = max(1, min(MAX_SCENE_DURATION, int(duration)))
                    scene = {
                        "description": scene_data["description"],
                        "duration": duration,
                        "status": "pending",
                        "visual_style": scene_data.get("visual_style", ""),
                        "audio_style": scene_data.get("audio_style", ""),
                        "characters": scene_data.get("characters", ""),
                        "setting": scene_data.get("setting", ""),
                    }
                    scenes.append(scene)
                    scene_generated = True

                    if num_scenes > 60 and (i + 1) % 20 == 0:
                        story_summary = summarize_story_so_far(
                            story_summary,
                            scenes[-20:],
                            provider,
                            model,
                            temperature,
                        )

                    # Yield progress update
                    yield scenes, f"Generated scene {i+1}/{num_scenes}"
                    break  # Success, exit retry loop

                # No valid JSON found, retry if attempts remain
                if attempt < MAX_RETRIES - 1:
                    gr.Info(f"Scene {i+1}: Retry {attempt + 1}/{MAX_RETRIES} (no valid JSON)")
                    continue

            except requests.RequestException as e:
                if attempt < MAX_RETRIES - 1:
                    gr.Info(f"Scene {i+1}: Retry {attempt + 1}/{MAX_RETRIES} (request error)")
                    continue
                gr.Warning(f"Scene {i+1} LLM request failed after {MAX_RETRIES} attempts: {e}")
                yield scenes, f"Error generating scene {i+1}: {e}"
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    gr.Info(f"Scene {i+1}: Retry {attempt + 1}/{MAX_RETRIES} (error: {e})")
                    continue
                gr.Warning(f"Scene {i+1} error after {MAX_RETRIES} attempts: {e}")
                yield scenes, f"Error in scene {i+1}: {e}"

        # If scene wasn't generated after all retries, warn user
        if not scene_generated:
            gr.Warning(f"Scene {i+1}: Could not extract valid JSON after {MAX_RETRIES} attempts")
            yield scenes, f"Error: Failed to generate scene {i+1} after {MAX_RETRIES} retries"

    # Step 2: Enhancement (after all scenes are generated)
    if enhance_with_gemma and scenes:
        yield scenes, "Enhancing all scenes..."

        for i, scene in enumerate(scenes):
            if progress:
                progress((i, len(scenes)), desc=f"Enhancing scene {i+1}/{len(scenes)}")

            enhance_tokens = int(max_tokens) if max_tokens else 512
            enhanced_desc = enhance_scene_description(
                scene["description"],
                prompt_enhancer_choice,
                provider,
                model,
                temperature=temperature,
                max_tokens=enhance_tokens,
            )
            scenes[i]["description"] = enhanced_desc
            scenes[i]["status"] = "enhanced"

            yield scenes, f"Enhanced scene {i+1}/{len(scenes)}"

    yield scenes, "All scenes ready for generation!"


def regenerate_single_scene(
    scenes: list[dict],
    scene_index: int,
    theme: str,
    provider: str,
    model: str,
    structure: str,
    pacing: str,
    prompt_enhancer_choice: str,
    enhance_with_gemma: bool = True
) -> list[dict]:
    """Regenerate a single scene using LLM + enhancement.

    Args:
        scenes: Current scenes list
        scene_index: Index of scene to regenerate (1-based)
        theme: Original movie theme
        provider: LLM provider
        model: Model name
        enhance_with_gemma: Whether to enhance after LLM

    Returns:
        Updated scenes list
    """
    if not scenes or scene_index < 1 or scene_index > len(scenes):
        gr.Warning("Invalid scene index")
        return scenes

    # Generate context from surrounding scenes
    idx = scene_index - 1
    context = f"Theme: {theme}\n\n"

    if idx > 0:
        context += f"Previous scene: {scenes[idx-1]['description']}\n"
    if idx < len(scenes) - 1:
        context += f"Next scene: {scenes[idx+1]['description']}\n"

    context += f"\nGenerate ONE new scene description that fits between these (or as opening/closing scene)."

    # Generate single scene with LLM + optional enhancement
    new_scenes = generate_scenes_with_llm(
        theme,
        1,
        provider,
        model,
        structure,
        pacing,
        prompt_enhancer_choice,
        story_summary=context,
        recent_scenes=[],
        enhance_with_gemma=enhance_with_gemma,
    )

    if new_scenes:
        scenes = scenes.copy()
        scenes[idx] = new_scenes[0]
        return scenes

    return scenes


# Thread-safe cancel event for movie generation
_movie_generation_cancel_event = threading.Event()


def cancel_movie_generation():
    """Set cancel event to stop movie generation (thread-safe)."""
    _movie_generation_cancel_event.set()
    gr.Info("Cancelling movie generation...")
    return gr.update(interactive=False)


def reset_movie_generation_cancel():
    """Reset the cancel event for a new generation (thread-safe)."""
    _movie_generation_cancel_event.clear()


def generate_movie_pipeline(
    scenes: list[dict],
    width: int,
    height: int,
    fps: int,
    use_continuity: bool,
    continuity_strength: float,
    enhance_prompt: bool,
    prompt_enhancer_choice: str,
    llm_provider: str,
    llm_model: str | None,
    temperature: float,
    max_tokens: int,
    tiling_mode: str = "auto",
    stream_output: bool = False,
    pipeline_type: str = "distilled",
    cfg_scale: float = 4.0,
    num_inference_steps: int = 40,
):
    """Main pipeline for generating a movie from scenes.

    This is a generator function that yields progress updates.

    Args:
        scenes: List of scene dicts with description, duration
        width: Video width
        height: Video height
        fps: Frames per second
        use_continuity: Enable I2V continuity between scenes
        continuity_strength: Strength of I2V conditioning
        enhance_prompt: Enable prompt enhancement
        prompt_enhancer_choice: Prompt enhancer selection from settings
        llm_provider: Global LLM provider
        llm_model: Global LLM model
        temperature: LLM temperature
        max_tokens: LLM max tokens
        stream_output: Update the final movie after each scene
        tiling_mode: VAE tiling mode for memory optimization
        pipeline_type: Pipeline type ('distilled' or 'dev')
        cfg_scale: CFG scale for dev pipeline
        num_inference_steps: Number of inference steps for dev pipeline
    Yields:
        Tuple of (gallery_images, current_video, final_video, overall_status, scene_status, log, progress_pct)
    """
    # Reset cancel event for new generation (thread-safe)
    _movie_generation_cancel_event.clear()

    log_messages = []

    def log(msg: str) -> str:
        log_messages.append(msg)
        return "\n".join(log_messages)

    if not scenes:
        yield [], None, None, "Error: No scenes", "", log("ERROR: No scenes to generate"), 0
        return

    # Validate scenes - filter out empty prompts
    valid_scenes = []
    for i, scene in enumerate(scenes):
        scene_prompt = build_scene_generation_prompt(scene).strip()
        if not scene_prompt:
            log(f"WARNING: Scene {i+1} has empty prompt text, skipping")
            continue
        valid_scenes.append(scene)

    if not valid_scenes:
        yield [], None, None, "Error: All scenes have empty descriptions", "", log("ERROR: No valid scenes to generate. All scene descriptions are empty."), 0
        return

    # Replace scenes with validated list
    scenes = valid_scenes
    yield [], None, None, f"Validated {len(scenes)} scenes", "Preparing...", log(f"Validated {len(scenes)} scenes with non-empty descriptions"), 0

    # Log all scene prompts that will be used
    yield [], None, None, f"Validated {len(scenes)} scenes", "Preparing...", log("\n=== SCENE PROMPTS TO BE GENERATED ==="), 0
    for i, scene in enumerate(scenes):
        desc = build_scene_generation_prompt(scene)
        duration = scene.get("duration", DEFAULT_SCENE_DURATION)
        yield [], None, None, f"Validated {len(scenes)} scenes", "Preparing...", log(f"Scene {i+1} ({duration}s): {desc[:80]}{'...' if len(desc) > 80 else ''}"), 0
    yield [], None, None, f"Validated {len(scenes)} scenes", "Preparing...", log("=" * 40), 0

    # Validate FFmpeg
    if not FFMPEG_INSTALLED:
        yield [], None, None, "Error: FFmpeg required", "", log("ERROR: FFmpeg not installed. Run: brew install ffmpeg"), 0
        return

    # Setup output directory
    output_dir = Path(tempfile.gettempdir()) / "mlx_movie_ui" / uuid.uuid4().hex[:8]
    output_dir.mkdir(parents=True, exist_ok=True)

    yield [], None, None, "Starting movie generation...", "Preparing...", log(f"Output directory: {output_dir}"), 0

    stream_output_path = None
    if stream_output:
        stream_output_path = str(OUTPUT_DIR / f"movie_stream_{uuid.uuid4().hex[:8]}.mp4")

    # Import video generation based on pipeline type
    try:
        if pipeline_type == "dev":
            from mlx_video.generate_dev import generate_video_dev
            log(f"Using Dev pipeline: CFG={cfg_scale}, steps={num_inference_steps}")
        else:
            from mlx_video.generate_av import generate_video_with_audio
    except ImportError as e:
        yield [], None, None, "Error: mlx-video not installed", "", log(f"ERROR: {e}"), 0
        return

    video_paths = []
    gallery_images = []
    last_frame_path = None
    total_scenes = len(scenes)
    failed_scenes = []  # Track scenes that failed after all retries
    MAX_SCENE_RETRIES = 2  # Number of retry attempts per scene

    def run_scene_generation(active_kwargs):
        try:
            if pipeline_type == "dev":
                generate_video_dev(**active_kwargs)
            else:
                generate_video_with_audio(**active_kwargs)
            return
        except Exception as e:
            if active_kwargs.get("enhance_prompt"):
                log(f"[WARN] Prompt enhancement failed: {e}. Retrying without enhancement.")
                fallback_kwargs = dict(active_kwargs)
                fallback_kwargs["enhance_prompt"] = False
                if pipeline_type == "dev":
                    generate_video_dev(**fallback_kwargs)
                else:
                    generate_video_with_audio(**fallback_kwargs)
                return
            raise

    for i, scene in enumerate(scenes):
        # Check for cancellation (thread-safe)
        if _movie_generation_cancel_event.is_set():
            progress_pct = int((i / total_scenes) * 100)
            yield gallery_images, None, None, "Cancelled", "Cancelled by user", log("Generation cancelled by user"), progress_pct
            return

        scene_num = i + 1
        scene_desc = build_scene_generation_prompt(scene)
        scene_duration = scene.get("duration", DEFAULT_SCENE_DURATION)
        num_frames = min(481, int(scene_duration * fps) + 1)  # LTX-2 supports up to 481 frames (20 sec)

        overall_status = f"Movie: {scene_num}/{total_scenes} scenes"
        scene_status = f"Generating Scene {scene_num}..."

        progress_pct = int((i / total_scenes) * 100)
        yield gallery_images, None, None, overall_status, scene_status, log(f"\n=== Scene {scene_num}/{total_scenes} ==="), progress_pct
        yield gallery_images, None, None, overall_status, scene_status, log(f"Description: {scene_desc[:100]}..."), progress_pct
        yield gallery_images, None, None, overall_status, scene_status, log(f"Duration: {scene_duration}s ({num_frames} frames)"), progress_pct

        # Prepare paths
        video_path = str(output_dir / f"scene_{scene_num:02d}.mp4")
        audio_path = str(output_dir / f"scene_{scene_num:02d}.wav")

        # Prepare kwargs
        effective_prompt, use_builtin_enhancer = resolve_prompt_enhancement(
            scene_desc,
            enhance_prompt,
            prompt_enhancer_choice,
            llm_provider,
            llm_model,
            temperature,
            max_tokens,
        )
        if effective_prompt != scene_desc:
            log("Scene prompt enhanced using global LLM settings.")
        effective_max_tokens = int(max_tokens)
        if use_builtin_enhancer and effective_max_tokens > 512:
            log("[WARN] Prompt enhancement max_tokens capped to 512 for stability.")
            effective_max_tokens = 512
        if pipeline_type == "dev":
            # Dev pipeline with CFG support
            kwargs = {
                "model_repo": "mlx-community/LTX-2-dev-bf16",
                "text_encoder_repo": None,
                "prompt": effective_prompt,
                "negative_prompt": "worst quality, inconsistent motion, blurry, jittery, distorted",
                "height": int(height),
                "width": int(width),
                "num_frames": num_frames,
                "num_inference_steps": int(num_inference_steps),
                "cfg_scale": float(cfg_scale),
                "seed": random.randint(0, 2147483647),
                "fps": int(fps),
                "output_path": video_path,
                "output_audio_path": audio_path,
                "verbose": True,
                "enhance_prompt": use_builtin_enhancer,
                "tiling": tiling_mode,
                "audio": True,
            }
        else:
            # Distilled pipeline (original)
            kwargs = {
                "model_repo": "Lightricks/LTX-2",
                "text_encoder_repo": None,
                "prompt": effective_prompt,
                "height": int(height),
                "width": int(width),
                "num_frames": num_frames,
                "seed": random.randint(0, 2147483647),
                "fps": int(fps),
                "output_path": video_path,
                "output_audio_path": audio_path,
                "verbose": True,
                "enhance_prompt": use_builtin_enhancer,
                "temperature": temperature,
                "max_tokens": effective_max_tokens,
                "tiling": tiling_mode,
            }

        # Add I2V continuity: use last frame of previous scene for smooth transitions
        if use_continuity and last_frame_path and os.path.exists(last_frame_path):
            kwargs["image"] = last_frame_path
            kwargs["image_strength"] = continuity_strength
            kwargs["image_frame_idx"] = 0
            yield gallery_images, None, None, overall_status, scene_status, log(f"Using I2V continuity (strength: {continuity_strength})"), progress_pct

        # Retry loop for scene generation
        scene_success = False
        for attempt in range(MAX_SCENE_RETRIES + 1):
            try:
                # Generate video
                if attempt > 0:
                    yield gallery_images, None, None, overall_status, f"Scene {scene_num}: Retry {attempt}...", log(f"Retry {attempt}/{MAX_SCENE_RETRIES} for scene {scene_num}..."), progress_pct
                    # Use a new seed for retry
                    kwargs["seed"] = random.randint(0, 2147483647)

                yield gallery_images, None, None, overall_status, f"Scene {scene_num}: Generating video...", log("Generating video with audio..."), progress_pct
                run_scene_generation(kwargs)

                if os.path.exists(video_path):
                    video_paths.append(video_path)
                    # Update progress after scene completion
                    progress_pct = int(((i + 1) / total_scenes) * 100)
                    yield gallery_images, None, None, overall_status, f"Scene {scene_num}: Video complete", log(f"Video saved: {video_path}"), progress_pct

                    if stream_output and stream_output_path:
                        yield gallery_images, video_path, None, overall_status, f"Scene {scene_num}: Updating stream...", log("Updating streaming output..."), progress_pct
                        if merge_videos_ffmpeg(video_paths, stream_output_path, fps):
                            yield gallery_images, video_path, stream_output_path, overall_status, f"Scene {scene_num}: Stream updated", log(f"Streaming output updated: {stream_output_path}"), progress_pct
                        else:
                            yield gallery_images, video_path, None, overall_status, f"Scene {scene_num}: Stream failed", log("WARNING: Streaming merge failed"), progress_pct

                    # Extract thumbnail for gallery
                    thumb_path = str(output_dir / f"thumb_{scene_num:02d}.jpg")
                    if extract_frame_ffmpeg(video_path, thumb_path, "first"):
                        gallery_images.append(thumb_path)
                        yield gallery_images, video_path, None, overall_status, f"Scene {scene_num}: Complete", log("Thumbnail extracted"), progress_pct

                    # Extract last frame for continuity
                    if use_continuity:
                        last_frame_path = str(output_dir / f"lastframe_{scene_num:02d}.jpg")
                        if extract_frame_ffmpeg(video_path, last_frame_path, "last"):
                            yield gallery_images, video_path, None, overall_status, scene_status, log("Last frame extracted for continuity"), progress_pct

                    scene_success = True
                    break  # Success - exit retry loop
                else:
                    raise Exception("Video file not created")

            except Exception as e:
                if attempt < MAX_SCENE_RETRIES:
                    yield gallery_images, None, None, overall_status, f"Scene {scene_num}: Error (will retry)", log(f"ERROR on attempt {attempt + 1}: {e}"), progress_pct
                    continue
                else:
                    yield gallery_images, None, None, overall_status, f"Scene {scene_num}: Failed", log(f"FAILED after {MAX_SCENE_RETRIES + 1} attempts: {e}"), progress_pct
                    failed_scenes.append(scene_num)
                    # Continue to next scene but track failure

    # Check for cancellation before merge (thread-safe)
    if _movie_generation_cancel_event.is_set():
        yield gallery_images, None, None, "Cancelled", "Cancelled by user", log("Generation cancelled before merge"), 100
        return

    # Report failed scenes if any
    if failed_scenes:
        yield gallery_images, None, None, "Merging videos...", "Some scenes failed", log(f"\nWARNING: Scenes {failed_scenes} failed after all retries"), 90

    # Merge all videos
    if len(video_paths) > 0:
        final_path = stream_output_path if stream_output_path and os.path.exists(stream_output_path) else None
        if final_path:
            success_msg = f"Complete! {len(video_paths)}/{total_scenes} scenes merged"
            if failed_scenes:
                success_msg += f" ({len(failed_scenes)} failed)"
            yield gallery_images, None, final_path, success_msg, "Done!", log(f"Final movie: {final_path}"), 100
            return

        yield gallery_images, None, None, "Merging videos...", "Creating final movie...", log(f"\n=== Merging {len(video_paths)} videos ==="), 90

        final_path = str(OUTPUT_DIR / f"movie_{uuid.uuid4().hex[:8]}.mp4")
        if merge_videos_ffmpeg(video_paths, final_path, fps):
            success_msg = f"Complete! {len(video_paths)}/{total_scenes} scenes merged"
            if failed_scenes:
                success_msg += f" ({len(failed_scenes)} failed)"
            yield gallery_images, None, final_path, success_msg, "Done!", log(f"Final movie: {final_path}"), 100
        else:
            yield gallery_images, None, None, "Merge failed", "FFmpeg error", log("ERROR: Could not merge videos"), 100
    else:
        yield gallery_images, None, None, "No videos generated", "", log("ERROR: No videos were successfully generated"), 0


def generate_video_ui(
    prompt: str,
    width: int,
    height: int,
    num_frames: int,
    fps: int,
    seed: int,
    input_image: str | None,
    image_strength: float,
    image_frame_idx: int,
    enhance_prompt: bool,
    prompt_enhancer_choice: str,
    llm_provider: str,
    llm_model: str | None,
    temperature: float,
    max_tokens: int,
    save_frames: bool,
    negative_prompt: str,
    tiling_mode: str = "auto",
    pipeline_type: str = "distilled",
    cfg_scale: float = 4.0,
    num_inference_steps: int = 40,
    stream_output: bool = False,
    progress=gr.Progress()
):
    """Generate video with audio using mlx-video.

    Args:
        stream_output: Enable streaming preview (dev pipeline + tiling only)
    """

    log_messages = []

    def log(msg: str):
        log_messages.append(msg)
        return "\n".join(log_messages)

    if not prompt.strip():
        gr.Warning("Please enter a prompt!")
        return None, None, None, "Error: No prompt provided", ""

    yield None, None, None, "Starting...", log("Importing mlx-video...")
    progress(0.05, desc="Importing mlx-video...")

    try:
        if pipeline_type == "dev":
            from mlx_video.generate_dev import generate_video_dev
        else:
            from mlx_video.generate_av import generate_video_with_audio
    except ImportError as e:
        error_msg = f"Error: mlx-video not installed. Run: uv sync\n{e}"
        yield None, None, None, error_msg, log(error_msg)
        return

    # Create output paths
    temp_dir = Path(tempfile.gettempdir()) / "mlx_video_ui"
    temp_dir.mkdir(exist_ok=True)

    video_id = uuid.uuid4().hex[:8]
    output_path = str(OUTPUT_DIR / f"video_{video_id}.mp4")
    audio_path = str(temp_dir / f"video_{video_id}.wav")

    yield None, None, None, "Loading models...", log("Loading models...")
    progress(0.1, desc="Loading models...")

    try:
        # Prepare kwargs
        effective_prompt, use_builtin_enhancer = resolve_prompt_enhancement(
            prompt,
            enhance_prompt,
            prompt_enhancer_choice,
            llm_provider,
            llm_model,
            temperature,
            max_tokens,
        )
        if effective_prompt != prompt:
            log("Prompt enhanced using global LLM settings.")
        effective_max_tokens = int(max_tokens)
        if use_builtin_enhancer and effective_max_tokens > 512:
            log("[WARN] Prompt enhancement max_tokens capped to 512 for stability.")
            effective_max_tokens = 512

        kwargs = {
            "model_repo": "Lightricks/LTX-2",
            "text_encoder_repo": None,
            "prompt": effective_prompt,
            "height": int(height),
            "width": int(width),
            "num_frames": int(num_frames),
            "seed": int(seed),
            "fps": int(fps),
            "output_path": output_path,
            "output_audio_path": audio_path,
            "verbose": True,
            "enhance_prompt": use_builtin_enhancer,
            "temperature": temperature,
            "max_tokens": effective_max_tokens,
            "tiling": tiling_mode,
        }

        # Add image for I2V if provided
        if input_image:
            # Validate image file exists
            if not os.path.exists(input_image):
                error_msg = f"Image file not found: {input_image}"
                yield None, None, None, f"Error: {error_msg}", log(f"ERROR: {error_msg}")
                return

            # Validate file extension
            valid_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif'}
            ext = os.path.splitext(input_image)[1].lower()
            if ext not in valid_extensions:
                error_msg = f"Invalid image format: {ext}. Use PNG, JPG, JPEG, WebP, BMP, or GIF"
                yield None, None, None, f"Error: {error_msg}", log(f"ERROR: {error_msg}")
                return

            kwargs["image"] = input_image
            kwargs["image_strength"] = image_strength
            kwargs["image_frame_idx"] = int(image_frame_idx)
            yield None, None, None, "Processing input image...", log(f"Using image: {input_image}")

        yield None, None, None, "Generating video latents...", log("Generating video latents (Stage 1)...")
        progress(0.2, desc="Generating video latents...")

        if pipeline_type == "dev":
            # Dev pipeline with CFG support
            log(f"Using Dev pipeline: CFG={cfg_scale}, steps={num_inference_steps}")
            _patch_ltx_attention_mask_alignment()

            # Check if streaming is enabled and possible
            can_stream = stream_output and tiling_mode != "none"

            if can_stream:
                # Streaming mode: use threading to collect frames
                import queue
                frame_queue = queue.Queue()
                generation_done = threading.Event()
                generation_error = [None]  # Use list to allow modification in callback
                latest_frame = [None]  # Latest frame for preview

                def on_frame_ready(frames_np, start_idx):
                    """Callback to receive decoded frames."""
                    # frames_np: (F, H, W, C), uint8
                    for i in range(frames_np.shape[0]):
                        frame = frames_np[i]
                        frame_queue.put((start_idx + i, frame))
                        latest_frame[0] = frame

                def log_callback(msg):
                    log(msg)

                def run_generation():
                    try:
                        generate_video_dev_streaming(
                            prompt=effective_prompt,
                            negative_prompt=negative_prompt if negative_prompt and negative_prompt.strip() else "worst quality, inconsistent motion, blurry, jittery, distorted",
                            width=int(width),
                            height=int(height),
                            num_frames=int(num_frames),
                            num_inference_steps=int(num_inference_steps),
                            cfg_scale=float(cfg_scale),
                            seed=int(seed),
                            fps=int(fps),
                            output_path=output_path,
                            audio_path=audio_path,
                            tiling_mode=tiling_mode,
                            enhance_prompt=use_builtin_enhancer,
                            input_image=input_image,
                            image_strength=image_strength,
                            image_frame_idx=int(image_frame_idx) if input_image else 0,
                            on_frame_ready=on_frame_ready,
                            log_callback=log_callback,
                        )
                    except Exception as e:
                        generation_error[0] = e
                    finally:
                        generation_done.set()

                # Start generation in background thread
                gen_thread = threading.Thread(target=run_generation, daemon=True)
                gen_thread.start()

                # Yield frames as they become available
                frames_received = 0
                while not generation_done.is_set() or not frame_queue.empty():
                    try:
                        frame_idx, frame = frame_queue.get(timeout=0.5)
                        frames_received += 1
                        progress(0.2 + 0.7 * (frames_received / int(num_frames)), desc=f"Decoding frame {frame_idx + 1}...")
                        yield None, None, latest_frame[0], f"Streaming: frame {frame_idx + 1}...", log(f"Frame {frame_idx + 1} received")
                    except queue.Empty:
                        # No frame available, yield current state
                        if latest_frame[0] is not None:
                            yield None, None, latest_frame[0], f"Generating... ({frames_received} frames)", "\n".join(log_messages)
                        continue

                # Wait for generation to complete
                gen_thread.join(timeout=60)

                if generation_error[0]:
                    raise generation_error[0]

            else:
                # Non-streaming mode: use original generate_video_dev
                from mlx_video.generate_dev import generate_video_dev

                dev_kwargs = {
                    "model_repo": "mlx-community/LTX-2-dev-bf16",
                    "text_encoder_repo": None,
                    "prompt": effective_prompt,
                    "negative_prompt": negative_prompt if negative_prompt and negative_prompt.strip() else "worst quality, inconsistent motion, blurry, jittery, distorted",
                    "height": int(height),
                    "width": int(width),
                    "num_frames": int(num_frames),
                    "num_inference_steps": int(num_inference_steps),
                    "cfg_scale": float(cfg_scale),
                    "seed": int(seed),
                    "fps": int(fps),
                    "output_path": output_path,
                    "output_audio_path": audio_path,
                    "verbose": True,
                    "enhance_prompt": use_builtin_enhancer,
                    "tiling": tiling_mode,
                    "audio": True,
                }

                # Add image for I2V if provided
                if input_image:
                    dev_kwargs["image"] = input_image
                    dev_kwargs["image_strength"] = image_strength
                    dev_kwargs["image_frame_idx"] = int(image_frame_idx)

                try:
                    generate_video_dev(**dev_kwargs)
                except Exception as e:
                    if dev_kwargs.get("enhance_prompt"):
                        log(f"[WARN] Prompt enhancement failed: {e}. Retrying without enhancement.")
                        dev_kwargs["enhance_prompt"] = False
                        generate_video_dev(**dev_kwargs)
                    else:
                        raise
        else:
            # Distilled pipeline (original behavior)
            from mlx_video.generate_av import generate_video_with_audio

            # Warn about unsupported parameters
            if negative_prompt and negative_prompt.strip():
                gr.Warning("Negative prompt is only supported by the dev pipeline")
                log("Note: negative_prompt ignored (use dev pipeline for CFG support)")

            def run_generation_with_fallback(active_kwargs):
                try:
                    generate_video_with_audio(**active_kwargs)
                    return
                except Exception as e:
                    if active_kwargs.get("enhance_prompt"):
                        log(f"[WARN] Prompt enhancement failed: {e}. Retrying without enhancement.")
                        fallback_kwargs = dict(active_kwargs)
                        fallback_kwargs["enhance_prompt"] = False
                        generate_video_with_audio(**fallback_kwargs)
                        return
                    raise

            run_generation_with_fallback(kwargs)

        yield None, None, None, "Encoding final video...", log("Encoding final video with audio...")
        progress(0.9, desc="Encoding final video...")

        # Check if files exist
        video_out = output_path if os.path.exists(output_path) else None
        audio_out = audio_path if os.path.exists(audio_path) else None

        # Save individual frames if requested
        frames_saved = 0
        frames_dir = None
        if save_frames and video_out:
            yield None, None, None, "Saving individual frames...", log("Saving individual frames as PNG...")
            progress(0.92, desc="Saving frames...")
            try:
                from PIL import Image
                import cv2

                frames_dir = temp_dir / f"video_{video_id}_frames"
                frames_dir.mkdir(exist_ok=True)

                cap = cv2.VideoCapture(output_path)
                frame_idx = 0
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    Image.fromarray(frame_rgb).save(frames_dir / f"frame_{frame_idx:04d}.png")
                    frame_idx += 1
                cap.release()
                frames_saved = frame_idx
                log(f"Saved {frames_saved} frames to {frames_dir}")
            except Exception as e:
                log(f"Warning: Could not save frames: {e}")

        progress(1.0, desc="Done!")

        status = f"Generated: {num_frames} frames @ {width}x{height}, {fps} FPS, seed={seed}"
        if frames_saved > 0:
            status += f" | Frames saved: {frames_saved}"
        log(f"Success! {status}")

        # Check if ffmpeg is installed for video playback
        if not FFMPEG_INSTALLED:
            log(f"⚠️ FFmpeg niet gevonden - video preview werkt niet")
            log(f"Installeer met: brew install ffmpeg")
            log(f"Video opgeslagen op: {video_out}")
            gr.Warning("FFmpeg niet geïnstalleerd! Run: brew install ffmpeg")
            # Return path as string in status instead of video component
            yield None, audio_out, None, f"{status}\n\n📁 Video: {video_out}", "\n".join(log_messages)
            return

        yield video_out, audio_out, None, status, "\n".join(log_messages)

    except Exception as e:
        error_msg = str(e)
        # Check for ffmpeg-related errors
        if "ffprobe" in error_msg.lower() or "ffmpeg" in error_msg.lower():
            error_msg = "FFmpeg niet geïnstalleerd!\n\nInstalleer met: brew install ffmpeg"
        else:
            error_msg = f"Generation failed: {error_msg}"
        gr.Warning(error_msg)
        log(f"ERROR: {error_msg}")
        yield None, None, None, error_msg, "\n".join(log_messages)


def _patch_ltx_attention_mask_alignment() -> None:
    import mlx.core as mx
    from mlx_video.models.ltx import attention as ltx_attention

    def _align_attention_mask(mask, q_len, k_len, batch_size, heads):
        if mask is None:
            return None

        if mask.ndim == 2:
            mask = mx.expand_dims(mask, axis=0)
            mask = mx.expand_dims(mask, axis=1)
        elif mask.ndim == 3:
            mask = mx.expand_dims(mask, axis=1)
        elif mask.ndim != 4:
            return None

        if mask.shape[0] not in (1, batch_size):
            if mask.shape[0] > batch_size:
                mask = mask[:batch_size]
            else:
                return None

        if mask.shape[1] not in (1, heads):
            if mask.shape[1] > heads:
                mask = mask[:, :heads]
            else:
                return None

        if mask.shape[-2] not in (1, q_len):
            if mask.shape[-2] > q_len:
                mask = mask[..., :q_len, :]
            else:
                return None

        if mask.shape[-1] != k_len:
            if mask.shape[-1] == q_len:
                if k_len > mask.shape[-1]:
                    pad = k_len - mask.shape[-1]
                    pad_values = mx.zeros(
                        (mask.shape[0], mask.shape[1], mask.shape[-2], pad),
                        dtype=mask.dtype,
                    )
                    mask = mx.concatenate([mask, pad_values], axis=-1)
                else:
                    mask = mask[..., :k_len]
            elif mask.shape[-1] > k_len:
                mask = mask[..., :k_len]
            else:
                return None

        return mask

    if not getattr(ltx_attention, "_mlx_video_ui_mask_patch", False):
        ltx_attention._mlx_video_ui_original_scaled_dot_product_attention = (
            ltx_attention.scaled_dot_product_attention
        )
        original = ltx_attention._mlx_video_ui_original_scaled_dot_product_attention

        def scaled_dot_product_attention_patched(q, k, v, heads, mask=None):
            _, q_seq_len, _ = q.shape
            _, kv_seq_len, _ = k.shape
            mask = _align_attention_mask(mask, q_seq_len, kv_seq_len, q.shape[0], heads)
            return original(q, k, v, heads, mask=mask)

        ltx_attention.scaled_dot_product_attention = scaled_dot_product_attention_patched
        ltx_attention._mlx_video_ui_mask_patch = True

    if not getattr(mx.fast, "_mlx_video_ui_mask_patch", False):
        mx.fast._mlx_video_ui_original_scaled_dot_product_attention = mx.fast.scaled_dot_product_attention
        fast_original = mx.fast._mlx_video_ui_original_scaled_dot_product_attention

        def fast_scaled_dot_product_attention_patched(q, k, v, *args, **kwargs):
            scale = kwargs.get("scale")
            mask = kwargs.get("mask")
            args_list = list(args)

            if scale is None and len(args_list) >= 1:
                scale = args_list[0]
            if mask is None and len(args_list) >= 2:
                mask = args_list[1]

            q_len = q.shape[-2]
            k_len = k.shape[-2]
            mask = _align_attention_mask(mask, q_len, k_len, q.shape[0], q.shape[1])

            if "mask" in kwargs:
                kwargs["mask"] = mask
            elif len(args_list) >= 2:
                args_list[1] = mask
            else:
                kwargs["mask"] = mask

            if "scale" not in kwargs and len(args_list) < 1 and scale is not None:
                kwargs["scale"] = scale

            return fast_original(q, k, v, *args_list, **kwargs)

        mx.fast.scaled_dot_product_attention = fast_scaled_dot_product_attention_patched
        mx.fast._mlx_video_ui_mask_patch = True


def generate_video_dev_streaming(
    prompt: str,
    negative_prompt: str,
    width: int,
    height: int,
    num_frames: int,
    num_inference_steps: int,
    cfg_scale: float,
    seed: int,
    fps: int,
    output_path: str,
    audio_path: str,
    tiling_mode: str,
    enhance_prompt: bool,
    input_image: str | None = None,
    image_strength: float = 1.0,
    image_frame_idx: int = 0,
    on_frame_ready: callable = None,
    log_callback: callable = None,
):
    """Generate video with streaming frame callback.

    This is a wrapper around generate_video_dev internals that exposes
    the on_frames_ready callback for real-time frame preview.

    Args:
        prompt: Text prompt for video generation
        negative_prompt: Negative prompt for CFG
        width: Video width
        height: Video height
        num_frames: Number of frames
        num_inference_steps: Denoising steps
        cfg_scale: CFG scale
        seed: Random seed
        fps: Frames per second
        output_path: Path to save output video
        audio_path: Path to save audio
        tiling_mode: Tiling mode for VAE
        enhance_prompt: Whether to enhance prompt
        input_image: Optional input image for I2V
        image_strength: Image conditioning strength
        image_frame_idx: Frame index for image conditioning
        on_frame_ready: Callback for streaming frames (frames_np, start_idx)
        log_callback: Callback for log messages
    """
    import mlx.core as mx
    import numpy as np
    import time
    from pathlib import Path

    def log(msg):
        if log_callback:
            log_callback(msg)
        print(msg)

    _patch_ltx_attention_mask_alignment()

    # Import from mlx_video
    from mlx_video.generate_dev import (
        ltx2_scheduler,
        create_position_grid,
        create_audio_position_grid,
        denoise_av_with_cfg,
        compute_audio_frames,
        load_audio_decoder,
        load_vocoder,
        save_audio,
        mux_video_audio,
        DEFAULT_NEGATIVE_PROMPT,
        AUDIO_LATENT_CHANNELS,
        AUDIO_MEL_BINS,
        AUDIO_SAMPLE_RATE,
    )
    from mlx_video.models.ltx.ltx import LTXModel
    from mlx_video.models.ltx.config import LTXModelConfig, LTXModelType, LTXRopeType
    from mlx_video.models.ltx.text_encoder import LTX2TextEncoder
    from mlx_video.models.ltx.video_vae.decoder import load_vae_decoder
    from mlx_video.models.ltx.video_vae.encoder import load_vae_encoder
    from mlx_video.models.ltx.video_vae.tiling import TilingConfig
    from mlx_video.conditioning import VideoConditionByLatentIndex, apply_conditioning
    from mlx_video.conditioning.latent import LatentState
    from mlx_video.convert import sanitize_transformer_weights
    from mlx_video.utils import get_model_path, load_image, prepare_image_for_encoding

    # Fixed LTX-2 scheduler - avoids division by zero in sigma calculations
    def ltx2_scheduler_fixed(
        steps: int,
        num_tokens: int = None,
        max_shift: float = 2.05,
        base_shift: float = 0.95,
        stretch: bool = True,
        terminal: float = 0.1,
    ) -> mx.array:
        """Fixed LTX-2 scheduler - avoids division by zero."""
        import math
        BASE_SHIFT_ANCHOR = 1024
        MAX_SHIFT_ANCHOR = 4096

        tokens = num_tokens if num_tokens is not None else MAX_SHIFT_ANCHOR
        sigmas = np.linspace(1.0, 0.0, steps + 1)

        x1 = BASE_SHIFT_ANCHOR
        x2 = MAX_SHIFT_ANCHOR
        mm = (max_shift - base_shift) / (x2 - x1)
        b = base_shift - mm * x1
        sigma_shift = tokens * mm + b

        # Fixed: avoid division by zero
        power = 1
        exp_shift = math.exp(sigma_shift)
        non_zero_mask = sigmas > 0
        sigmas_safe = np.where(non_zero_mask, sigmas, 1.0)
        transformed = exp_shift / (exp_shift + (1.0 / sigmas_safe - 1.0) ** power)
        sigmas = np.where(non_zero_mask, transformed, 0.0)

        # Stretch to terminal value
        if stretch:
            non_zero_mask = sigmas > 0
            non_zero_sigmas = sigmas[non_zero_mask]
            if len(non_zero_sigmas) > 0:
                one_minus_z = 1.0 - non_zero_sigmas
                denominator = 1.0 - terminal
                if abs(denominator) > 1e-8 and abs(one_minus_z[-1]) > 1e-8:
                    scale_factor = one_minus_z[-1] / denominator
                    stretched = 1.0 - (one_minus_z / scale_factor)
                    sigmas[non_zero_mask] = stretched

        return mx.array(sigmas, dtype=mx.float32)

    start_time = time.time()

    # Validate dimensions
    if height % 32 != 0:
        raise ValueError(f"Height must be divisible by 32, got {height}")
    if width % 32 != 0:
        raise ValueError(f"Width must be divisible by 32, got {width}")

    if num_frames % 8 != 1:
        adjusted_num_frames = round((num_frames - 1) / 8) * 8 + 1
        log(f"Adjusted frames to {adjusted_num_frames}")
        num_frames = adjusted_num_frames

    # Calculate audio frames
    audio_frames = compute_audio_frames(num_frames, fps)
    is_i2v = input_image is not None

    # Get model path
    model_repo = "mlx-community/LTX-2-dev-bf16"
    model_path = get_model_path(model_repo)

    # Calculate latent dimensions
    latent_h, latent_w = height // 32, width // 32
    latent_frames = 1 + (num_frames - 1) // 8

    mx.random.seed(seed)

    # Load text encoder
    log("Loading text encoder...")
    text_encoder = LTX2TextEncoder()
    text_encoder.load(model_path=model_path, text_encoder_path=model_path)
    mx.eval(text_encoder.parameters())

    # Optionally enhance prompt
    if enhance_prompt:
        log("Enhancing prompt...")
        prompt = text_encoder.enhance_t2v(prompt, max_tokens=512, temperature=0.7, seed=seed, verbose=False)
        log(f"Enhanced: {prompt[:100]}...")

    # Encode prompts
    video_embeddings_pos, audio_embeddings_pos = text_encoder(prompt, return_audio_embeddings=True)
    effective_negative = negative_prompt if negative_prompt and negative_prompt.strip() else DEFAULT_NEGATIVE_PROMPT
    video_embeddings_neg, audio_embeddings_neg = text_encoder(effective_negative, return_audio_embeddings=True)
    model_dtype = video_embeddings_pos.dtype
    mx.eval(video_embeddings_pos, video_embeddings_neg, audio_embeddings_pos, audio_embeddings_neg)

    del text_encoder
    mx.clear_cache()

    # Load transformer
    log("Loading transformer...")
    raw_weights = mx.load(str(model_path / 'ltx-2-19b-dev.safetensors'))
    sanitized = sanitize_transformer_weights(raw_weights)
    sanitized = {k: v.astype(mx.bfloat16) if v.dtype == mx.float32 else v for k, v in sanitized.items()}

    config = LTXModelConfig(
        model_type=LTXModelType.AudioVideo,
        num_attention_heads=32,
        attention_head_dim=128,
        in_channels=128,
        out_channels=128,
        num_layers=48,
        cross_attention_dim=4096,
        caption_channels=3840,
        audio_num_attention_heads=32,
        audio_attention_head_dim=64,
        audio_in_channels=AUDIO_LATENT_CHANNELS * AUDIO_MEL_BINS,
        audio_out_channels=AUDIO_LATENT_CHANNELS * AUDIO_MEL_BINS,
        audio_cross_attention_dim=2048,
        rope_type=LTXRopeType.SPLIT,
        double_precision_rope=True,
        positional_embedding_theta=10000.0,
        positional_embedding_max_pos=[20, 2048, 2048],
        audio_positional_embedding_max_pos=[20],
        use_middle_indices_grid=True,
        timestep_scale_multiplier=1000,
    )

    transformer = LTXModel(config)
    transformer.load_weights(list(sanitized.items()), strict=False)
    mx.eval(transformer.parameters())

    # Load VAE encoder for I2V
    image_latent = None
    if is_i2v:
        log("Loading VAE encoder...")
        vae_encoder = load_vae_encoder(str(model_path / 'ltx-2-19b-dev.safetensors'))
        mx.eval(vae_encoder.parameters())

        input_img = load_image(input_image, height=height, width=width, dtype=model_dtype)
        image_tensor = prepare_image_for_encoding(input_img, height, width, dtype=model_dtype)
        image_latent = vae_encoder(image_tensor)
        mx.eval(image_latent)

        del vae_encoder
        mx.clear_cache()

    # Generate sigma schedule
    num_tokens = latent_frames * latent_h * latent_w
    sigmas = ltx2_scheduler_fixed(steps=num_inference_steps, num_tokens=num_tokens)
    mx.eval(sigmas)

    # Create position grids
    log("Generating video latents...")
    mx.random.seed(seed)

    video_positions = create_position_grid(1, latent_frames, latent_h, latent_w)
    audio_positions = create_audio_position_grid(1, audio_frames)
    mx.eval(video_positions, audio_positions)

    # Initialize latents
    video_state = None
    video_latent_shape = (1, 128, latent_frames, latent_h, latent_w)
    if is_i2v and image_latent is not None:
        video_state = LatentState(
            latent=mx.zeros(video_latent_shape, dtype=model_dtype),
            clean_latent=mx.zeros(video_latent_shape, dtype=model_dtype),
            denoise_mask=mx.ones((1, 1, latent_frames, 1, 1), dtype=model_dtype),
        )
        conditioning = VideoConditionByLatentIndex(
            latent=image_latent,
            frame_idx=image_frame_idx,
            strength=image_strength,
        )
        video_state = apply_conditioning(video_state, [conditioning])

        noise = mx.random.normal(video_latent_shape, dtype=model_dtype)
        noise_scale = sigmas[0]
        scaled_mask = video_state.denoise_mask * noise_scale

        video_state = LatentState(
            latent=noise * scaled_mask + video_state.latent * (mx.array(1.0, dtype=model_dtype) - scaled_mask),
            clean_latent=video_state.clean_latent,
            denoise_mask=video_state.denoise_mask,
        )
        video_latents = video_state.latent
        mx.eval(video_latents)
    else:
        video_latents = mx.random.normal(video_latent_shape, dtype=model_dtype)
        mx.eval(video_latents)

    # Initialize audio latents
    audio_latents = mx.random.normal((1, AUDIO_LATENT_CHANNELS, audio_frames, AUDIO_MEL_BINS), dtype=model_dtype)
    mx.eval(audio_latents)

    # Denoise with CFG
    video_latents, audio_latents = denoise_av_with_cfg(
        video_latents, audio_latents,
        video_positions, audio_positions,
        video_embeddings_pos, video_embeddings_neg,
        audio_embeddings_pos, audio_embeddings_neg,
        transformer, sigmas, cfg_scale=cfg_scale, verbose=True, video_state=video_state
    )

    del transformer
    mx.clear_cache()

    # Decode to video with streaming callback
    log("Decoding video (streaming)...")
    vae_decoder = load_vae_decoder(
        str(model_path / 'ltx-2-19b-dev.safetensors'),
        timestep_conditioning=None
    )
    mx.eval(vae_decoder.parameters())

    # Select tiling configuration
    if tiling_mode == "none":
        tiling_config = None
    elif tiling_mode == "auto":
        tiling_config = TilingConfig.auto(height, width, num_frames)
    elif tiling_mode == "default":
        tiling_config = TilingConfig.default()
    elif tiling_mode == "aggressive":
        tiling_config = TilingConfig.aggressive()
    elif tiling_mode == "conservative":
        tiling_config = TilingConfig.conservative()
    elif tiling_mode == "spatial":
        tiling_config = TilingConfig.spatial_only()
    elif tiling_mode == "temporal":
        tiling_config = TilingConfig.temporal_only()
    else:
        tiling_config = TilingConfig.auto(height, width, num_frames)

    # Create frame callback wrapper
    def frame_callback(frames_mx: mx.array, start_idx: int):
        if on_frame_ready is not None:
            # Convert from MLX to numpy
            frames_mx = frames_mx.astype(mx.float32)
            frames_np = np.array(frames_mx)
            # frames_np shape: (B, C, F, H, W), values [-1, 1]
            # Convert to (F, H, W, C), values [0, 255] uint8
            frames_np = frames_np[0]  # Remove batch: (C, F, H, W)
            frames_np = np.transpose(frames_np, (1, 2, 3, 0))  # (F, H, W, C)
            frames_np = np.clip((frames_np + 1.0) / 2.0, 0.0, 1.0)  # [0, 1]
            frames_uint8 = (frames_np * 255).astype(np.uint8)
            on_frame_ready(frames_uint8, start_idx)

    if tiling_config is not None:
        video = vae_decoder.decode_tiled(
            video_latents,
            tiling_config=tiling_config,
            tiling_mode=tiling_mode,
            debug=True,
            on_frames_ready=frame_callback
        )
    else:
        video = vae_decoder(video_latents)
    mx.eval(video)

    del vae_decoder
    mx.clear_cache()

    # Decode audio
    log("Decoding audio...")
    audio_decoder = load_audio_decoder(model_path)
    mx.eval(audio_decoder.parameters())

    mel_spectrogram = audio_decoder(audio_latents)
    mx.eval(mel_spectrogram)

    del audio_decoder
    mx.clear_cache()

    vocoder = load_vocoder(model_path)
    mx.eval(vocoder.parameters())

    audio_waveform = vocoder(mel_spectrogram)
    mx.eval(audio_waveform)

    del vocoder
    mx.clear_cache()

    audio_waveform = audio_waveform.astype(mx.float32)
    audio_np = np.array(audio_waveform)
    if audio_np.ndim == 3:
        audio_np = audio_np[0]

    # Convert video to uint8 frames
    video = mx.squeeze(video, axis=0)
    video = mx.transpose(video, (1, 2, 3, 0))
    video = mx.clip((video + 1.0) / 2.0, 0.0, 1.0)
    video = (video * 255).astype(mx.uint8)
    video_np = np.array(video)

    # Save outputs
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    audio_output = Path(audio_path)
    save_audio(audio_np, audio_output)
    log(f"Saved audio to {audio_output}")

    # Save video to temp, then mux
    temp_video_path = output_path.parent / f"{output_path.stem}_temp.mp4"

    try:
        import cv2
        h, w = video_np.shape[1], video_np.shape[2]
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(str(temp_video_path), fourcc, fps, (w, h))
        for frame in video_np:
            out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        out.release()

        log("Muxing video and audio...")
        if mux_video_audio(temp_video_path, audio_output, output_path):
            log(f"Saved video with audio to {output_path}")
            temp_video_path.unlink(missing_ok=True)
        else:
            temp_video_path.rename(output_path.parent / f"{output_path.stem}_video.mp4")
    except Exception as e:
        log(f"Could not save video: {e}")

    elapsed = time.time() - start_time
    log(f"Total time: {elapsed:.1f}s")

    return str(output_path), str(audio_output)


def create_ui():
    """Create and return the Gradio UI."""

    with gr.Blocks(title="mlx-video-UI") as demo:

        # Header
        with gr.Column(elem_classes="header-container"):
            gr.HTML("""
                <h1 class="aurora-title">MLX-Video-UI</h1>
                <p class="aurora-subtitle">Generate videos with synchronized audio using LTX-2 on Apple Silicon | Up to 20 sec, 4K, Stereo Audio</p>
                <p class="aurora-credits">Powered by <a href="https://github.com/Blaizzy/mlx-video" target="_blank">mlx-video</a> by <a href="https://x.com/Prince_Canuma" target="_blank">@Prince_Canuma</a></p>
            """)

        # Main Tabs
        with gr.Tabs():
            generation = build_generation_tab(
                CAMERA_MOTIONS,
                LIGHTING_OPTIONS,
                SPEECH_LANGUAGES,
                SPEECH_ACCENTS,
                RESOLUTION_PRESETS,
                DURATION_PRESETS,
            )
            movie = build_movie_generator_tab(
                RESOLUTION_PRESETS,
                MIN_MOVIE_DURATION,
                MAX_MOVIE_DURATION,
                MAX_SCENES,
            )
            settings = build_advanced_settings_tab(CFG_PRESET_VALUES)

        # ===== EVENT HANDLERS =====

        # Resolution preset handler (with VRAM warnings)
        def on_resolution_change(preset):
            # Show warning for high resolutions
            if "4K" in preset:
                gr.Info("4K vereist veel VRAM (~96GB+ aanbevolen) en langere generatietijd")
            elif "1080p" in preset:
                gr.Info("1080p gebruikt multi-tile inference en vereist meer VRAM (~48GB+ aanbevolen)")
            if preset == "Custom":
                return gr.update(), gr.update(), gr.update(), gr.update()
            res = RESOLUTION_PRESETS.get(preset)
            if res:
                return res[0], res[1], res[0], res[1]
            return gr.update(), gr.update(), gr.update(), gr.update()

        generation.resolution_preset.change(
            fn=on_resolution_change,
            inputs=[generation.resolution_preset],
            outputs=[generation.width, generation.height, generation.width_slider, generation.height_slider],
        )

        # Sync sliders with hidden values
        generation.width_slider.change(fn=lambda x: x, inputs=[generation.width_slider], outputs=[generation.width])
        generation.height_slider.change(fn=lambda x: x, inputs=[generation.height_slider], outputs=[generation.height])
        generation.frames_slider.change(fn=lambda x: x, inputs=[generation.frames_slider], outputs=[generation.num_frames])

        # Duration preset handler
        def on_duration_change(preset):
            if preset == "Custom":
                return gr.update(), gr.update()
            frames = DURATION_PRESETS.get(preset)
            if frames:
                return frames, frames
            return gr.update(), gr.update()

        generation.duration_preset.change(
            fn=on_duration_change,
            inputs=[generation.duration_preset],
            outputs=[generation.num_frames, generation.frames_slider],
        )

        # Random seed button
        generation.random_seed_btn.click(fn=randomize_seed, outputs=[generation.seed])

        # Clear prompt button
        generation.clear_btn.click(fn=lambda: "", outputs=[generation.prompt])

        # Global LLM provider/model (Advanced Settings)
        settings.llm_provider.change(
            fn=update_models,
            inputs=[settings.llm_provider],
            outputs=[settings.llm_model],
        )
        settings.refresh_models_btn.click(
            fn=update_models,
            inputs=[settings.llm_provider],
            outputs=[settings.llm_model],
        )

        # Enhance with external LLM
        # Dual enhance: LLM override, Gemma fallback
        def dual_enhance_prompt(current_prompt, enhancer_choice, provider, model, temperature, max_tokens):
            if not current_prompt.strip():
                gr.Warning("Enter a prompt first")
                return current_prompt

            if provider in VALID_LLM_PROVIDERS:
                if not model:
                    gr.Warning("Selecteer eerst een LLM model in Advanced Settings!")
                    return current_prompt
                gr.Info(f"Enhancing with {provider}...")
                enhanced = enhance_prompt_with_llm(
                    current_prompt,
                    provider,
                    model,
                    temperature=temperature,
                    max_tokens=int(max_tokens),
                )
                gr.Info("LLM enhancement complete!")
                return enhanced

            if enhancer_choice == "Gemma (Built-in)":
                gr.Info("Enhancing with Gemma...")
                enhanced = enhance_scene_with_gemma(current_prompt, temperature=temperature, max_tokens=int(max_tokens))
                gr.Info("Gemma enhancement complete!")
                return enhanced
            elif enhancer_choice == "LLM (Ollama/LM Studio)":
                gr.Warning("Selecteer eerst een LLM provider in Advanced Settings!")
                return current_prompt

            return current_prompt

        generation.enhance_btn.click(
            fn=dual_enhance_prompt,
            inputs=[
                generation.prompt,
                settings.prompt_enhancer_choice,
                settings.llm_provider,
                settings.llm_model,
                settings.temperature,
                settings.max_tokens,
            ],
            outputs=[generation.prompt],
        )

        # Prompt Builder - Build prompt from components
        generation.build_prompt_btn.click(
            fn=build_prompt_from_components,
            inputs=[
                generation.pb_camera,
                generation.pb_lighting,
                generation.pb_environment,
                generation.pb_subject,
                generation.pb_action,
                generation.pb_ambient,
                generation.pb_foley,
                generation.pb_music,
                generation.pb_speech,
                generation.pb_speech_language,
                generation.pb_speech_accent,
            ],
            outputs=[generation.prompt],
        )

        # CFG Preset handler
        settings.cfg_preset.change(
            fn=apply_cfg_preset,
            inputs=[settings.cfg_preset],
            outputs=[settings.text_cfg, settings.cross_modal_cfg],
        )

        # Pipeline settings visibility toggle
        def toggle_dev_settings(pipeline):
            is_dev = pipeline == "dev"
            return (
                gr.update(visible=is_dev),  # cfg_scale
                gr.update(visible=is_dev),  # num_inference_steps
                gr.update(visible=is_dev),  # negative_prompt
            )

        generation.pipeline_type.change(
            fn=toggle_dev_settings,
            inputs=[generation.pipeline_type],
            outputs=[
                generation.cfg_scale,
                generation.num_inference_steps,
                generation.negative_prompt,
            ],
        )

        # Streaming visibility handlers
        def update_streaming_visibility(tiling_mode, pipeline_type):
            """Show streaming option only when tiling is enabled and using dev pipeline."""
            show = tiling_mode != "none" and pipeline_type == "dev"
            return gr.update(visible=show)

        generation.tiling_mode.change(
            fn=update_streaming_visibility,
            inputs=[generation.tiling_mode, generation.pipeline_type],
            outputs=[generation.stream_output],
        )

        generation.pipeline_type.change(
            fn=update_streaming_visibility,
            inputs=[generation.tiling_mode, generation.pipeline_type],
            outputs=[generation.stream_output],
        )

        def update_streaming_preview_visibility(stream_output):
            """Show streaming preview when stream output is enabled."""
            return gr.update(visible=stream_output)

        generation.stream_output.change(
            fn=update_streaming_preview_visibility,
            inputs=[generation.stream_output],
            outputs=[generation.streaming_preview],
        )

        # Main generate button
        generation.generate_btn.click(
            fn=generate_video_ui,
            inputs=[
                generation.prompt,
                generation.width,
                generation.height,
                generation.num_frames,
                generation.fps_slider,
                generation.seed,
                generation.input_image,
                generation.image_strength,
                generation.image_frame_idx,
                settings.enhance_prompt_checkbox,
                settings.prompt_enhancer_choice,
                settings.llm_provider,
                settings.llm_model,
                settings.temperature,
                settings.max_tokens,
                generation.save_frames,
                generation.negative_prompt,  # Use generation tab's negative_prompt
                generation.tiling_mode,
                generation.pipeline_type,
                generation.cfg_scale,
                generation.num_inference_steps,
                generation.stream_output,
            ],
            outputs=[
                generation.output_video,
                generation.output_audio,
                generation.streaming_preview,
                generation.status,
                generation.generation_log,
            ],
        )

        # ===== MOVIE GENERATOR EVENT HANDLERS =====

        # Duration preset mapping (in seconds)
        DURATION_PRESET_MAP = {
            "30 sec (Short clip)": 30,
            "1 min (Teaser)": 60,
            "3 min (Music video)": 180,
            "5 min (Short film)": 300,
            "10 min (Episode)": 600,
            "30 min (TV Episode)": 1800,
            "1 hour (Feature)": 3600,
            "1.5 hours (Standard film)": 5400,
            "2 hours (Hollywood)": 7200,
            "3 hours (Epic)": 10800,
        }

        def format_duration(seconds):
            """Format seconds into human readable duration."""
            if seconds < 60:
                return f"{seconds} sec"
            if seconds < 3600:
                mins = seconds // 60
                secs = seconds % 60
                return f"{mins}m {secs}s" if secs else f"{mins} min"
            hours = seconds // 3600
            mins = (seconds % 3600) // 60
            return f"{hours}h {mins}m" if mins else f"{hours} hour"

        # Duration preset change
        def on_duration_preset_change(preset, pacing):
            if preset == "Custom":
                return gr.update(), gr.update(), gr.update()
            duration = DURATION_PRESET_MAP.get(preset, 30)
            num_scenes = calculate_scenes_from_duration(duration, pacing)
            display = format_duration(duration)
            if num_scenes > 300:
                gr.Warning("Very long films can take days to generate (hundreds of scenes).")
            return duration, display, num_scenes

        movie.movie_duration_preset.change(
            fn=on_duration_preset_change,
            inputs=[movie.movie_duration_preset, movie.pacing],
            outputs=[movie.movie_duration, movie.movie_duration_display, movie.num_scenes_display],
        )

        # Auto-calculate number of scenes from duration (when slider changes)
        def on_duration_change_movie(duration, pacing):
            num_scenes = calculate_scenes_from_duration(int(duration), pacing)
            display = format_duration(int(duration))
            if num_scenes > 300:
                gr.Warning("Very long films can take days to generate (hundreds of scenes).")
            return num_scenes, display

        movie.movie_duration.change(
            fn=on_duration_change_movie,
            inputs=[movie.movie_duration, movie.pacing],
            outputs=[movie.num_scenes_display, movie.movie_duration_display],
        )

        def on_pacing_change(pacing, duration):
            num_scenes = calculate_scenes_from_duration(int(duration), pacing)
            display = format_duration(int(duration))
            if num_scenes > 300:
                gr.Warning("Very long films can take days to generate (hundreds of scenes).")
            return num_scenes, display

        movie.pacing.change(
            fn=on_pacing_change,
            inputs=[movie.pacing, movie.movie_duration],
            outputs=[movie.num_scenes_display, movie.movie_duration_display],
        )

        # Resolution preset for movie tab
        def on_resolution_change_movie(preset):
            if preset == "Custom":
                return gr.update(), gr.update()
            res = RESOLUTION_PRESETS.get(preset)
            if res:
                return res[0], res[1]
            return gr.update(), gr.update()

        movie.resolution_preset.change(
            fn=on_resolution_change_movie,
            inputs=[movie.resolution_preset],
            outputs=[movie.width, movie.height],
        )

        # ===== SCRIPT MANAGEMENT EVENT HANDLERS =====
        def refresh_script_list():
            """Refresh the list of saved scripts."""
            scripts = list_scripts()
            choices = [(f"{s['name']} ({s['scenes']} scenes) - {s['created']}", s["path"]) for s in scripts]
            return gr.update(choices=choices)

        def save_current_script(name, theme, scenes, width, height, fps):
            """Save the current script to a file."""
            if not name:
                return "⚠️ Please enter a script name", gr.update()
            if not scenes:
                return "⚠️ No scenes to save", gr.update()
            settings_payload = {"width": int(width), "height": int(height), "fps": int(fps)}
            msg = save_script(name, theme, scenes, settings_payload)
            return msg, refresh_script_list()

        def load_selected_script(selected):
            """Load a selected script."""
            if not selected:
                return gr.update(), gr.update(), [], "⚠️ No script selected"
            try:
                theme, scenes, settings_payload = load_script(selected)
                return theme, scenes_to_dataframe(scenes), scenes, f"✅ Loaded: {Path(selected).stem}"
            except Exception as e:
                return gr.update(), gr.update(), [], f"❌ Error loading: {e}"

        def delete_selected_script(selected):
            """Delete a selected script."""
            if not selected:
                return "⚠️ No script selected", gr.update()
            try:
                delete_script(selected)
                return "🗑️ Script deleted", refresh_script_list()
            except Exception as e:
                return f"❌ Error deleting: {e}", gr.update()

        # Wire up script management events
        movie.save_script_btn.click(
            save_current_script,
            inputs=[
                movie.script_name_input,
                movie.movie_theme,
                movie.movie_scenes_state,
                movie.width,
                movie.height,
                movie.fps,
            ],
            outputs=[movie.script_status, movie.script_dropdown],
        )

        movie.refresh_scripts_btn.click(refresh_script_list, outputs=[movie.script_dropdown])

        movie.load_script_btn.click(
            load_selected_script,
            inputs=[movie.script_dropdown],
            outputs=[movie.movie_theme, movie.scenes_dataframe, movie.movie_scenes_state, movie.script_status],
        )

        movie.delete_script_btn.click(
            delete_selected_script,
            inputs=[movie.script_dropdown],
            outputs=[movie.script_status, movie.script_dropdown],
        )

        # Generate scenes sequentially with LLM + optional enhancement (live updates)
        def on_generate_scenes_sequential(
            theme,
            num_scenes,
            script_mode,
            structure,
            pacing,
            enhance_gemma,
            current_scenes,
            provider,
            model,
            prompt_enhancer_choice,
            temperature,
            max_tokens,
            progress=gr.Progress(),
        ):
            if not theme.strip():
                gr.Warning("Please enter a movie theme first!")
                yield current_scenes, scenes_to_dataframe(current_scenes), "Error: No theme provided"
                return

            mode = script_mode or "Auto (recommended)"
            num_scenes_int = int(num_scenes)
            use_batch = False
            if mode.startswith("Batch"):
                use_batch = True
            elif mode.startswith("Auto") and num_scenes_int > 80:
                use_batch = True

            generator = (
                generate_scenes_in_batches(
                    theme,
                    num_scenes_int,
                    provider,
                    model,
                    structure,
                    pacing,
                    prompt_enhancer_choice,
                    enhance_with_gemma=enhance_gemma,
                    temperature=temperature,
                    max_tokens=int(max_tokens),
                    progress=progress,
                )
                if use_batch
                else generate_scenes_sequentially(
                    theme,
                    num_scenes_int,
                    provider,
                    model,
                    structure,
                    pacing,
                    prompt_enhancer_choice,
                    enhance_with_gemma=enhance_gemma,
                    temperature=temperature,
                    max_tokens=int(max_tokens),
                    progress=progress,
                )
            )

            # Use the selected generator for live updates
            for scenes, status in generator:
                df_data = scenes_to_dataframe(scenes) if scenes else []
                yield scenes, df_data, status

        movie.generate_scenes_btn.click(
            fn=on_generate_scenes_sequential,
            inputs=[
                movie.movie_theme,
                movie.num_scenes_display,
                movie.script_mode,
                movie.story_structure,
                movie.pacing,
                movie.enhance_scenes_with_gemma,
                movie.movie_scenes_state,
                settings.llm_provider,
                settings.llm_model,
                settings.prompt_enhancer_choice,
                settings.temperature,
                settings.max_tokens,
            ],
            outputs=[movie.movie_scenes_state, movie.scenes_dataframe, movie.script_generation_status],
        )

        # Sync dataframe changes to state
        def sync_dataframe_to_state(df_data):
            if df_data is None or len(df_data) == 0:
                return []
            scenes = dataframe_to_scenes(df_data)
            return scenes

        movie.scenes_dataframe.change(
            fn=sync_dataframe_to_state,
            inputs=[movie.scenes_dataframe],
            outputs=[movie.movie_scenes_state],
        )

        # Add scene - use dataframe as source of truth to avoid Gradio state sync issues
        def on_add_scene(df_data):
            scenes = dataframe_to_scenes(df_data) if df_data is not None and len(df_data) > 0 else []
            new_scenes = add_empty_scene(scenes)
            return new_scenes, scenes_to_dataframe(new_scenes)

        movie.add_scene_btn.click(
            fn=on_add_scene,
            inputs=[movie.scenes_dataframe],
            outputs=[movie.movie_scenes_state, movie.scenes_dataframe],
        )

        # Remove scene - use dataframe as source of truth to avoid Gradio state sync issues
        def on_remove_scene(df_data, index):
            scenes = dataframe_to_scenes(df_data) if df_data is not None and len(df_data) > 0 else []
            if not scenes:
                return scenes, []
            new_scenes = remove_scene_at_index(scenes, int(index))
            return new_scenes, scenes_to_dataframe(new_scenes)

        movie.remove_scene_btn.click(
            fn=on_remove_scene,
            inputs=[movie.scenes_dataframe, movie.scene_to_remove],
            outputs=[movie.movie_scenes_state, movie.scenes_dataframe],
        )

        # Regenerate single scene with LLM + optional enhancement
        # Use dataframe as source of truth to avoid Gradio state sync issues
        def on_regenerate_scene(
            df_data,
            index,
            theme,
            provider,
            model,
            structure,
            pacing,
            prompt_enhancer_choice,
            enhance_gemma,
        ):
            scenes = dataframe_to_scenes(df_data) if df_data is not None and len(df_data) > 0 else []
            if not scenes:
                gr.Warning("No scenes to regenerate")
                return scenes, scenes_to_dataframe(scenes) if scenes else []

            new_scenes = regenerate_single_scene(
                scenes,
                int(index),
                theme,
                provider,
                model,
                structure,
                pacing,
                prompt_enhancer_choice,
                enhance_gemma,
            )
            return new_scenes, scenes_to_dataframe(new_scenes)

        movie.regenerate_scene_btn.click(
            fn=on_regenerate_scene,
            inputs=[
                movie.scenes_dataframe,
                movie.scene_to_remove,
                movie.movie_theme,
                settings.llm_provider,
                settings.llm_model,
                movie.story_structure,
                movie.pacing,
                settings.prompt_enhancer_choice,
                movie.enhance_scenes_with_gemma,
            ],
            outputs=[movie.movie_scenes_state, movie.scenes_dataframe],
        )

        # Cancel movie generation
        movie.cancel_movie_btn.click(fn=cancel_movie_generation, outputs=[movie.cancel_movie_btn])

        # Movie pipeline settings visibility toggle
        def toggle_movie_dev_settings(pipeline):
            is_dev = pipeline == "dev"
            return (
                gr.update(visible=is_dev),  # cfg_scale
                gr.update(visible=is_dev),  # num_inference_steps
            )

        movie.pipeline_type.change(
            fn=toggle_movie_dev_settings,
            inputs=[movie.pipeline_type],
            outputs=[
                movie.cfg_scale,
                movie.num_inference_steps,
            ],
        )

        # Generate movie
        def on_generate_movie(
            scenes,
            df_data,
            width,
            height,
            fps,
            tiling,
            use_cont,
            cont_strength,
            enhance,
            stream_output,
            prompt_enhancer_choice,
            llm_provider,
            llm_model,
            temp,
            max_tok,
            pipeline_type,
            cfg_scale,
            num_inference_steps,
        ):
            # CRITICAL: Explicitly sync dataframe to scenes before generation
            # This ensures we use the user's edited descriptions, not stale state
            if df_data is not None and len(df_data) > 0:
                scenes = dataframe_to_scenes(df_data)
                print(f"[SYNC] Synced {len(scenes)} scenes from dataframe")

            if not scenes:
                gr.Warning("Generate scenes first!")
                yield [], None, None, "Error: No scenes", "", "Generate scenes first before creating the movie.", 0
                return

            # Run the pipeline generator
            for result in generate_movie_pipeline(
                scenes,
                int(width),
                int(height),
                int(fps),
                use_cont,
                cont_strength,
                enhance,
                prompt_enhancer_choice,
                llm_provider,
                llm_model,
                temp,
                int(max_tok),
                tiling_mode=tiling,
                stream_output=bool(stream_output),
                pipeline_type=pipeline_type,
                cfg_scale=float(cfg_scale),
                num_inference_steps=int(num_inference_steps),
            ):
                yield result

        movie.generate_movie_btn.click(
            fn=on_generate_movie,
            inputs=[
                movie.movie_scenes_state,
                movie.scenes_dataframe,
                movie.width,
                movie.height,
                movie.fps,
                movie.tiling_mode,
                movie.use_continuity,
                movie.continuity_strength,
                movie.enhance_prompts,
                movie.stream_output,
                settings.prompt_enhancer_choice,
                settings.llm_provider,
                settings.llm_model,
                movie.temperature,
                movie.max_tokens,
                movie.pipeline_type,
                movie.cfg_scale,
                movie.num_inference_steps,
            ],
            outputs=[
                movie.scene_preview_gallery,
                movie.current_scene_video,
                movie.final_movie_output,
                movie.overall_progress_md,
                movie.scene_progress_md,
                movie.generation_log,
                movie.progress_bar,
            ],
        )

        # ===== SETTINGS PERSISTENCE EVENT HANDLERS =====

        # Generation tab settings persistence
        generation.resolution_preset.change(
            lambda v: save_setting("generation", "resolution_preset", v),
            inputs=[generation.resolution_preset]
        )
        generation.width_slider.change(
            lambda v: save_setting("generation", "width", v),
            inputs=[generation.width_slider]
        )
        generation.height_slider.change(
            lambda v: save_setting("generation", "height", v),
            inputs=[generation.height_slider]
        )
        generation.frames_slider.change(
            lambda v: save_setting("generation", "frames", v),
            inputs=[generation.frames_slider]
        )
        generation.fps_slider.change(
            lambda v: save_setting("generation", "fps", v),
            inputs=[generation.fps_slider]
        )
        generation.seed.change(
            lambda v: save_setting("generation", "seed", v),
            inputs=[generation.seed]
        )
        generation.save_frames.change(
            lambda v: save_setting("generation", "save_frames", v),
            inputs=[generation.save_frames]
        )
        generation.tiling_mode.change(
            lambda v: save_setting("generation", "tiling_mode", v),
            inputs=[generation.tiling_mode]
        )
        generation.image_strength.change(
            lambda v: save_setting("generation", "image_strength", v),
            inputs=[generation.image_strength]
        )
        generation.pb_camera.change(
            lambda v: save_setting("generation", "pb_camera", v),
            inputs=[generation.pb_camera]
        )
        generation.pb_lighting.change(
            lambda v: save_setting("generation", "pb_lighting", v),
            inputs=[generation.pb_lighting]
        )
        # Advanced settings tab persistence
        settings.cfg_preset.change(
            lambda v: save_setting("advanced", "cfg_preset", v),
            inputs=[settings.cfg_preset]
        )
        settings.text_cfg.change(
            lambda v: save_setting("advanced", "text_cfg", v),
            inputs=[settings.text_cfg]
        )
        settings.cross_modal_cfg.change(
            lambda v: save_setting("advanced", "cross_modal_cfg", v),
            inputs=[settings.cross_modal_cfg]
        )
        settings.prompt_enhancer_choice.change(
            lambda v: save_setting("advanced", "prompt_enhancer", v),
            inputs=[settings.prompt_enhancer_choice]
        )
        settings.llm_provider.change(
            lambda v: save_setting("advanced", "llm_provider", v),
            inputs=[settings.llm_provider]
        )
        settings.llm_model.change(
            lambda v: save_setting("advanced", "llm_model", v),
            inputs=[settings.llm_model]
        )
        settings.enhance_prompt_checkbox.change(
            lambda v: save_setting("advanced", "enhance_prompt", v),
            inputs=[settings.enhance_prompt_checkbox]
        )
        settings.temperature.change(
            lambda v: save_setting("advanced", "temperature", v),
            inputs=[settings.temperature]
        )
        settings.max_tokens.change(
            lambda v: save_setting("advanced", "max_tokens", v),
            inputs=[settings.max_tokens]
        )
        settings.audio_sample_rate.change(
            lambda v: save_setting("advanced", "audio_sample_rate", v),
            inputs=[settings.audio_sample_rate]
        )
        settings.stereo_output.change(
            lambda v: save_setting("advanced", "stereo_output", v),
            inputs=[settings.stereo_output]
        )
        settings.num_inference_steps.change(
            lambda v: save_setting("advanced", "num_inference_steps", v),
            inputs=[settings.num_inference_steps]
        )

        # Movie generator tab persistence
        movie.movie_duration_preset.change(
            lambda v: save_setting("movie", "duration_preset", v),
            inputs=[movie.movie_duration_preset]
        )
        movie.movie_duration.change(
            lambda v: save_setting("movie", "duration", v),
            inputs=[movie.movie_duration]
        )
        movie.fps.change(
            lambda v: save_setting("movie", "fps", v),
            inputs=[movie.fps]
        )
        movie.resolution_preset.change(
            lambda v: save_setting("movie", "resolution_preset", v),
            inputs=[movie.resolution_preset]
        )
        movie.tiling_mode.change(
            lambda v: save_setting("movie", "tiling_mode", v),
            inputs=[movie.tiling_mode]
        )
        movie.script_mode.change(
            lambda v: save_setting("movie", "script_mode", v),
            inputs=[movie.script_mode]
        )
        movie.story_structure.change(
            lambda v: save_setting("movie", "story_structure", v),
            inputs=[movie.story_structure]
        )
        movie.pacing.change(
            lambda v: save_setting("movie", "pacing", v),
            inputs=[movie.pacing]
        )
        movie.use_continuity.change(
            lambda v: save_setting("movie", "use_continuity", v),
            inputs=[movie.use_continuity]
        )
        movie.continuity_strength.change(
            lambda v: save_setting("movie", "continuity_strength", v),
            inputs=[movie.continuity_strength]
        )
        movie.enhance_prompts.change(
            lambda v: save_setting("movie", "enhance_prompts", v),
            inputs=[movie.enhance_prompts]
        )
        movie.temperature.change(
            lambda v: save_setting("movie", "temperature", v),
            inputs=[movie.temperature]
        )
        movie.max_tokens.change(
            lambda v: save_setting("movie", "max_tokens", v),
            inputs=[movie.max_tokens]
        )

        # Load saved scripts on app startup
        demo.load(refresh_script_list, outputs=[movie.script_dropdown])

        # Load saved settings on app startup
        demo.load(
            load_all_settings,
            outputs=[
                # Generation tab
                generation.resolution_preset,
                generation.width_slider,
                generation.height_slider,
                generation.frames_slider,
                generation.fps_slider,
                generation.seed,
                generation.save_frames,
                generation.tiling_mode,
                generation.image_strength,
                generation.pb_camera,
                generation.pb_lighting,
                # Advanced settings tab
                settings.cfg_preset,
                settings.text_cfg,
                settings.cross_modal_cfg,
                settings.prompt_enhancer_choice,
                settings.llm_provider,
                settings.llm_model,
                settings.enhance_prompt_checkbox,
                settings.temperature,
                settings.max_tokens,
                settings.audio_sample_rate,
                settings.stereo_output,
                settings.num_inference_steps,
                # Movie tab
                movie.movie_duration_preset,
                movie.movie_duration,
                movie.fps,
                movie.resolution_preset,
                movie.tiling_mode,
                movie.script_mode,
                movie.story_structure,
                movie.pacing,
                movie.use_continuity,
                movie.continuity_strength,
                movie.enhance_prompts,
                movie.temperature,
                movie.max_tokens,
            ]
        )

    return demo


def main():
    """Main entry point."""
    # Check dependencies
    if not FFMPEG_INSTALLED:
        print("\n" + "=" * 60)
        print("⚠️  WARNING: FFmpeg niet geïnstalleerd!")
        print("   Video preview in de UI zal niet werken.")
        print("   Installeer met: brew install ffmpeg")
        print("=" * 60 + "\n")

    demo = create_ui()
    demo.queue().launch(
        theme=AuroraTheme(),
        css=CUSTOM_CSS,
        head=CUSTOM_JS
    )


if __name__ == "__main__":
    main()
