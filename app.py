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
MAX_SCENES = 1000  # Maximum number of scenes (enough for ~1.5 hour film)
MIN_MOVIE_DURATION = 6  # Minimum total movie duration in seconds
MAX_MOVIE_DURATION = 10800  # Maximum 3 hours (Hollywood film length)

# Script Storage Directory
SCRIPTS_DIR = Path.home() / ".mlx-video-ui" / "scripts"
SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

# Scene Writer System Prompt for LLM (Based on LTX-2 paper Section 4.2)
# "Comprehensive yet factual, describing only what is seen and heard without emotional interpretation"
SCENE_WRITER_SYSTEM_PROMPT = """You are a professional screenwriter creating scenes for LTX-2 AI video generation with synchronized audio.

CRITICAL: Follow the LTX-2 paper's captioning guidelines:
- Be COMPREHENSIVE yet FACTUAL
- Describe ONLY what is seen and heard
- NO emotional interpretation or subjective commentary
- Include BOTH visual AND audio elements

OUTPUT FORMAT (JSON array):
[
  {
    "description": "Full scene description following LTX-2 format",
    "duration": 8,
    "visual": "camera, lighting, subject, environment",
    "audio": "ambient, foley, music, speech with language/accent"
  }
]

PROMPT STRUCTURE (per LTX-2 paper):
1. BEGIN with subject: "A woman with long dark hair...", "A vintage red car..."
2. ADD action: "...walks through a sunlit garden...", "...drives down a winding road..."
3. CAMERA movement: "...camera slowly tracking alongside...", "...dolly forward...", "...static wide shot..."
4. LIGHTING: "...soft golden hour lighting...", "...dramatic shadows...", "...blue hour ambiance..."
5. AUDIO cues: "...birds singing, footsteps on gravel...", "...engine rumbling, wind noise..."
6. BE SPECIFIC: NOT "ambient sounds" but "distant traffic, wind through trees, church bells"
7. SPEECH: Include language AND accent: "speaks softly in British English", "whispers in French"

VISUAL ELEMENTS:
- Camera: static, pan left/right, zoom in/out, tracking shot, dolly forward/backward, crane up/down, handheld, orbit
- Lighting: natural daylight, golden hour, blue hour, dramatic shadows, soft diffused, backlit, neon/artificial, candlelight, moonlight
- Subject: detailed appearance, specific actions, expressions
- Environment: setting details, atmosphere, weather, time of day

AUDIO ELEMENTS (LTX-2 supports stereo 24kHz):
- Ambient: specific environmental sounds (wind through leaves, distant traffic, crowd murmur, ocean waves)
- Foley: precise sound effects (footsteps on gravel, rustling fabric, door creaking, glass clinking)
- Music: style, mood, instruments, or "no music" for natural atmosphere
- Speech: dialogue with speaker description, language, AND accent (e.g., "male voice speaks calmly in American English")

RULES:
1. Output ONLY valid JSON array, no other text
2. Each scene 4-15 seconds (LTX-2 supports up to 20 sec)
3. Integrate visual AND audio naturally in description
4. Ensure continuity between scenes
5. Be factual - describe what is seen/heard, no interpretation

EXAMPLE for theme "A day in the forest":
[
  {
    "description": "A misty forest at dawn, golden sunlight filtering through dense pine trees, illuminating particles floating in the air. Camera slowly pans across moss-covered rocks and ferns glistening with dew. Audio: birds singing in the canopy, gentle rustling of leaves, distant stream trickling over rocks, no music.",
    "duration": 10,
    "visual": "slow pan, golden hour lighting through trees, misty atmosphere",
    "audio": "birdsong, rustling leaves, distant stream, no music"
  },
  {
    "description": "Close-up of a spider web covered in dewdrops, each drop catching morning light like tiny prisms. Gentle breeze causes subtle movement, camera static with shallow depth of field. Audio: soft chirping of crickets, single bird call echoing, light wind, no music.",
    "duration": 8,
    "visual": "static close-up, shallow DOF, backlit dewdrops",
    "audio": "crickets chirping, bird call, gentle wind"
  },
  {
    "description": "Wide shot of a forest clearing, a deer grazing peacefully in tall grass. Soft afternoon light creates long shadows, camera slowly zooms in. Audio: deer hooves stepping softly on grass, birds chirping overhead, distant woodpecker tapping, wind rustling through tall grass.",
    "duration": 12,
    "visual": "wide shot with slow zoom, afternoon soft light, long shadows",
    "audio": "soft hoofsteps, birdsong, woodpecker, wind in grass"
  }
]"""

# Sequential Scene Writer Prompt (for story continuity)
SEQUENTIAL_SCENE_WRITER_PROMPT = """You are a professional screenwriter creating scenes for an AI video generator (LTX-2).

CRITICAL RULES:
1. Each scene MUST continue naturally from previous scenes
2. Maintain visual consistency: same characters, locations, lighting style
3. Maintain narrative flow: actions have consequences, time progresses logically
4. Each scene description must be self-contained but reference shared elements

FORMAT: Return ONLY valid JSON: {"description": "...", "duration": N}
- description: Detailed visual+audio description (50-150 words)
- duration: Scene length in seconds (1-20)

DESCRIPTION GUIDELINES (per LTX-2 paper):
- Start with subject and action
- Include camera movement/angle
- Specify lighting and atmosphere
- Add ambient audio and sound effects
- Be factual, not emotional

VISUAL ELEMENTS:
- Camera: static, pan left/right, zoom in/out, tracking shot, dolly forward/backward, crane up/down, handheld, orbit
- Lighting: natural daylight, golden hour, blue hour, dramatic shadows, soft diffused, backlit, neon/artificial
- Subject: detailed appearance, specific actions, expressions
- Environment: setting details, atmosphere, weather, time of day

AUDIO ELEMENTS (LTX-2 supports stereo 24kHz):
- Ambient: specific environmental sounds (wind, traffic, crowd, ocean)
- Foley: precise sound effects (footsteps, rustling, doors, glass)
- Music: style, mood, instruments, or "no music" for natural atmosphere
- Speech: dialogue with speaker description, language, AND accent
"""

# LLM API endpoints
LM_STUDIO_BASE = "http://localhost:1234/v1"
OLLAMA_BASE = "http://localhost:11434"

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

    models = get_available_models(provider)
    return gr.Dropdown(
        choices=models,
        value=models[0] if models else None,
        interactive=True
    )


def enhance_prompt_with_llm(prompt: str, provider: str, model: str) -> str:
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

    # System message that preserves user intent while adding prompt techniques
    system_message = """Je bent een video+audio prompt engineer voor het LTX-2 model.

KRITIEKE REGEL: BEHOUD DE OORSPRONKELIJKE INTENTIE VAN DE GEBRUIKER!
- VOEG GEEN details toe die de gebruiker niet heeft gespecificeerd
- Als de gebruiker "een vrouw" zegt, voeg GEEN haarkleur/leeftijd/kleding toe
- Als de gebruiker "een auto" zegt, voeg GEEN kleur/merk/model toe
- Gebruik alleen de informatie die de gebruiker heeft gegeven

JE TAAK: Voeg ALLEEN prompt-technieken toe:
1. CAMERA beweging: tracking shot, pan, dolly, static wide shot, etc.
2. BELICHTING: natural lighting, soft diffused light, golden hour (als niet gespecificeerd)
3. AUDIO cues: ambient sounds passend bij de scene, no music (tenzij gevraagd)
4. STRUCTUUR: Herformuleer naar subject → action → setting

VOORBEELD:
INPUT: "een vrouw loopt in het bos"
OUTPUT: "A woman walks through a forest, camera tracking alongside at eye level, natural daylight filtering through the trees. Audio: footsteps on forest floor, birds in the distance, gentle wind through leaves."

NIET: "A young woman with auburn hair..." (voegt onnodige details toe!)

Antwoord ALLEEN met de verbeterde prompt in het Engels, geen uitleg."""

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
                    "temperature": 0.7,
                    "max_tokens": 500
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
                    "stream": False
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

def calculate_scenes_from_duration(total_duration: int) -> int:
    """Calculate number of scenes based on total movie duration."""
    avg_scene_duration = (DEFAULT_SCENE_DURATION + MAX_SCENE_DURATION) / 2
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
            scene.get("status", "pending")
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
                "status": str(row[3]) if len(row) > 3 and row[3] else "pending"
            })
    return scenes


def add_empty_scene(scenes: list[dict]) -> list[dict]:
    """Add an empty scene to the list."""
    scenes = scenes.copy()
    scenes.append({
        "description": "New scene - edit this description",
        "duration": DEFAULT_SCENE_DURATION,
        "status": "pending"
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
    """Enhance a single scene description using built-in Gemma.

    Based on LTX-2 paper: "Comprehensive yet factual, describing only what is seen and heard"

    Args:
        scene_description: Original scene description from LLM
        temperature: Gemma temperature
        max_tokens: Maximum tokens for response

    Returns:
        Enhanced scene description optimized for LTX-2
    """
    try:
        from mlx_video.generate_av import load_gemma, generate_text_gemma

        gemma_model, gemma_tokenizer = load_gemma()

        enhance_prompt = f"""Verbeter deze scene beschrijving voor LTX-2 video generatie.

REGELS (LTX-2 paper):
1. Wees UITGEBREID maar FEITELIJK
2. Beschrijf ZOWEL visuele ALS audio elementen
3. Specificeer: subject, actie, camera beweging, belichting
4. Specificeer: ambient geluiden, foley, muziek, spraak met taal/accent
5. GEEN emotionele interpretatie

ORIGINELE SCENE:
{scene_description}

VERBETERDE SCENE (alleen de beschrijving, geen uitleg):"""

        enhanced = generate_text_gemma(
            gemma_model,
            gemma_tokenizer,
            enhance_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )

        # Clean up the response
        enhanced = enhanced.strip()
        if enhanced:
            return enhanced

    except ImportError:
        pass  # Gemma not available, return original
    except Exception as e:
        print(f"[DEBUG] Gemma enhancement error: {e}")

    return scene_description


def generate_scenes_with_llm(
    theme: str,
    num_scenes: int,
    provider: str,
    model: str,
    enhance_with_gemma: bool = True,
    temperature: float = 0.7,
    max_tokens: int | None = None,
    image_description: str | None = None
) -> list[dict]:
    """Generate scene descriptions from theme using external LLM, then enhance with Gemma.

    Args:
        theme: Main theme/idea for the movie
        num_scenes: Number of scenes to generate
        provider: "LM Studio" or "Ollama"
        model: Model name
        enhance_with_gemma: Whether to enhance each scene with Gemma after LLM generation
        temperature: LLM temperature
        max_tokens: Maximum tokens for response (None = no limit)
        image_description: Description of what the reference image represents (if provided)

    Returns:
        List of scene dicts with description, duration, status
    """
    # Build the user prompt with optional image context
    image_context = ""
    if image_description and image_description.strip():
        image_context = f"""

IMPORTANT - Reference Image Context:
The user has provided a reference image. {image_description.strip()}
When writing scenes, incorporate this visual reference naturally. Each scene should reference or include elements from the provided image where appropriate."""

    user_prompt = f"""Create exactly {num_scenes} scenes for a short film about:

{theme}{image_context}

Remember: Output ONLY a valid JSON array with {num_scenes} scene objects. Each object must have "description" and "duration" fields."""

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
                    duration = scene.get("duration", DEFAULT_SCENE_DURATION)
                    duration = max(1, min(MAX_SCENE_DURATION, int(duration)))
                    scenes.append({
                        "description": scene["description"],
                        "duration": duration,
                        "status": "pending"
                    })

            if scenes:
                gr.Info(f"LLM generated {len(scenes)} scenes!")

                # Step 2: Enhance with Gemma if enabled
                if enhance_with_gemma:
                    gr.Info("Step 2: Enhancing scenes with Gemma...")
                    for i, scene in enumerate(scenes):
                        enhanced_desc = enhance_scene_with_gemma(
                            scene["description"],
                            temperature=temperature,
                            max_tokens=512
                        )
                        scenes[i]["description"] = enhanced_desc
                        scenes[i]["status"] = "enhanced"
                    gr.Info(f"Gemma enhanced {len(scenes)} scenes!")

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
    enhance_with_gemma: bool = True,
    temperature: float = 0.7,
    max_tokens: int | None = None,
    image_description: str | None = None,
    progress=None
) -> Generator[tuple[list[dict], str], None, None]:
    """
    Generate scenes sequentially with story continuity.

    Workflow:
    1. For each scene: generate with context of previous scenes
    2. After all scenes: apply Gemma enhancement
    3. Yield updates for live UI feedback

    Args:
        theme: Main theme/idea for the movie
        num_scenes: Number of scenes to generate
        provider: "LM Studio" or "Ollama"
        model: Model name
        enhance_with_gemma: Whether to enhance each scene with Gemma after all are generated
        temperature: LLM temperature
        max_tokens: Maximum tokens for response (None = no limit)
        image_description: Description of what the reference image represents (if provided)
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
    MAX_RETRIES = 3

    # Step 1: Sequential Scene Generation
    for i in range(num_scenes):
        if progress:
            progress((i, num_scenes), desc=f"Generating scene {i+1}/{num_scenes}")

        # Build context from previous scenes
        context = f"Movie theme: {theme}\n\n"

        # Add reference image context if provided
        if image_description and image_description.strip():
            context += f"=== REFERENCE IMAGE ===\nThe user has provided a reference image: {image_description.strip()}\nIncorporate this visual reference naturally in the scenes.\n=== END REFERENCE IMAGE ===\n\n"

        if scenes:
            context += "=== PREVIOUS SCENES (for story continuity) ===\n"
            for j, prev_scene in enumerate(scenes, 1):
                context += f"Scene {j}: {prev_scene['description']}\n"
            context += "\n=== END PREVIOUS SCENES ===\n\n"

        # Build prompt for this scene
        user_prompt = f"""{context}Now write Scene {i+1} of {num_scenes}.
Continue the story naturally from the previous scenes.
Maintain visual and narrative consistency.
Return ONLY a JSON object: {{"description": "...", "duration": N}}"""

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
                    duration = scene_data.get("duration", DEFAULT_SCENE_DURATION)
                    duration = max(1, min(MAX_SCENE_DURATION, int(duration)))
                    scene = {
                        "description": scene_data["description"],
                        "duration": duration,
                        "status": "pending"
                    }
                    scenes.append(scene)
                    scene_generated = True

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

    # Step 2: Gemma Enhancement (after all scenes are generated)
    if enhance_with_gemma and scenes:
        yield scenes, "Enhancing all scenes with Gemma..."

        for i, scene in enumerate(scenes):
            if progress:
                progress((i, len(scenes)), desc=f"Enhancing scene {i+1}/{len(scenes)}")

            enhanced_desc = enhance_scene_with_gemma(
                scene["description"],
                temperature=temperature,
                max_tokens=512
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
    enhance_with_gemma: bool = True
) -> list[dict]:
    """Regenerate a single scene using LLM + Gemma.

    Args:
        scenes: Current scenes list
        scene_index: Index of scene to regenerate (1-based)
        theme: Original movie theme
        provider: LLM provider
        model: Model name
        enhance_with_gemma: Whether to enhance with Gemma after LLM

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

    # Generate single scene with LLM + optional Gemma enhancement
    new_scenes = generate_scenes_with_llm(
        context, 1, provider, model, enhance_with_gemma
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
    temperature: float,
    max_tokens: int,
    input_image: str | None = None,
    image_strength: float = 0.8,
    progress=gr.Progress()
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
        enhance_prompt: Use Gemma to enhance prompts
        temperature: LLM temperature
        max_tokens: LLM max tokens
        input_image: Optional reference image path for I2V generation
        image_strength: Strength of input image influence (0.0-1.0)

    Yields:
        Tuple of (gallery_images, current_video, final_video, overall_status, scene_status, log)
    """
    # Reset cancel event for new generation (thread-safe)
    _movie_generation_cancel_event.clear()

    log_messages = []

    def log(msg: str) -> str:
        log_messages.append(msg)
        return "\n".join(log_messages)

    if not scenes:
        yield [], None, None, "Error: No scenes", "", log("ERROR: No scenes to generate")
        return

    # Validate scenes - filter out empty descriptions
    valid_scenes = []
    for i, scene in enumerate(scenes):
        desc = scene.get("description", "").strip()
        if not desc:
            log(f"WARNING: Scene {i+1} has empty description, skipping")
            continue
        valid_scenes.append(scene)

    if not valid_scenes:
        yield [], None, None, "Error: All scenes have empty descriptions", "", log("ERROR: No valid scenes to generate. All scene descriptions are empty.")
        return

    # Replace scenes with validated list
    scenes = valid_scenes
    yield [], None, None, f"Validated {len(scenes)} scenes", "Preparing...", log(f"Validated {len(scenes)} scenes with non-empty descriptions")

    # Log all scene prompts that will be used
    yield [], None, None, f"Validated {len(scenes)} scenes", "Preparing...", log("\n=== SCENE PROMPTS TO BE GENERATED ===")
    for i, scene in enumerate(scenes):
        desc = scene.get("description", "")
        duration = scene.get("duration", DEFAULT_SCENE_DURATION)
        yield [], None, None, f"Validated {len(scenes)} scenes", "Preparing...", log(f"Scene {i+1} ({duration}s): {desc[:80]}{'...' if len(desc) > 80 else ''}")
    yield [], None, None, f"Validated {len(scenes)} scenes", "Preparing...", log("=" * 40)

    # Validate FFmpeg
    if not FFMPEG_INSTALLED:
        yield [], None, None, "Error: FFmpeg required", "", log("ERROR: FFmpeg not installed. Run: brew install ffmpeg")
        return

    # Setup output directory
    output_dir = Path(tempfile.gettempdir()) / "mlx_movie_ui" / uuid.uuid4().hex[:8]
    output_dir.mkdir(parents=True, exist_ok=True)

    yield [], None, None, "Starting movie generation...", "Preparing...", log(f"Output directory: {output_dir}")

    # Import video generation
    try:
        from mlx_video.generate_av import generate_video_with_audio
    except ImportError as e:
        yield [], None, None, "Error: mlx-video not installed", "", log(f"ERROR: {e}")
        return

    video_paths = []
    gallery_images = []
    last_frame_path = None
    total_scenes = len(scenes)
    failed_scenes = []  # Track scenes that failed after all retries
    MAX_SCENE_RETRIES = 2  # Number of retry attempts per scene

    for i, scene in enumerate(scenes):
        # Check for cancellation (thread-safe)
        if _movie_generation_cancel_event.is_set():
            yield gallery_images, None, None, "Cancelled", "Cancelled by user", log("Generation cancelled by user")
            return

        scene_num = i + 1
        scene_desc = scene.get("description", "")
        scene_duration = scene.get("duration", DEFAULT_SCENE_DURATION)
        num_frames = min(481, int(scene_duration * fps) + 1)  # LTX-2 supports up to 481 frames (20 sec)

        overall_status = f"Movie: {scene_num}/{total_scenes} scenes"
        scene_status = f"Generating Scene {scene_num}..."

        yield gallery_images, None, None, overall_status, scene_status, log(f"\n=== Scene {scene_num}/{total_scenes} ===")
        yield gallery_images, None, None, overall_status, scene_status, log(f"Description: {scene_desc[:100]}...")
        yield gallery_images, None, None, overall_status, scene_status, log(f"Duration: {scene_duration}s ({num_frames} frames)")

        progress((i / total_scenes), desc=f"Generating scene {scene_num}/{total_scenes}")

        # Prepare paths
        video_path = str(output_dir / f"scene_{scene_num:02d}.mp4")
        audio_path = str(output_dir / f"scene_{scene_num:02d}.wav")

        # Prepare kwargs
        kwargs = {
            "model_repo": "Lightricks/LTX-2",
            "text_encoder_repo": None,
            "prompt": scene_desc,
            "height": int(height),
            "width": int(width),
            "num_frames": num_frames,
            "seed": random.randint(0, 2147483647),
            "fps": int(fps),
            "output_path": video_path,
            "output_audio_path": audio_path,
            "verbose": True,
            "enhance_prompt": enhance_prompt,
            "temperature": temperature,
            "max_tokens": int(max_tokens),
        }

        # Add I2V: Use reference image for first scene, or continuity for subsequent scenes
        if i == 0 and input_image and os.path.exists(input_image):
            # First scene: use the user's reference image
            kwargs["image"] = input_image
            kwargs["image_strength"] = image_strength
            kwargs["image_frame_idx"] = 0
            yield gallery_images, None, None, overall_status, scene_status, log(f"Using reference image: {os.path.basename(input_image)}")
        elif use_continuity and last_frame_path and os.path.exists(last_frame_path):
            # Subsequent scenes: use last frame for continuity
            kwargs["image"] = last_frame_path
            kwargs["image_strength"] = continuity_strength
            kwargs["image_frame_idx"] = 0
            yield gallery_images, None, None, overall_status, scene_status, log(f"Using I2V continuity (strength: {continuity_strength})")

        # Retry loop for scene generation
        scene_success = False
        for attempt in range(MAX_SCENE_RETRIES + 1):
            try:
                # Generate video
                if attempt > 0:
                    yield gallery_images, None, None, overall_status, f"Scene {scene_num}: Retry {attempt}...", log(f"Retry {attempt}/{MAX_SCENE_RETRIES} for scene {scene_num}...")
                    # Use a new seed for retry
                    kwargs["seed"] = random.randint(0, 2147483647)

                yield gallery_images, None, None, overall_status, f"Scene {scene_num}: Generating video...", log("Generating video with audio...")
                generate_video_with_audio(**kwargs)

                if os.path.exists(video_path):
                    video_paths.append(video_path)
                    yield gallery_images, None, None, overall_status, f"Scene {scene_num}: Video complete", log(f"Video saved: {video_path}")

                    # Extract thumbnail for gallery
                    thumb_path = str(output_dir / f"thumb_{scene_num:02d}.jpg")
                    if extract_frame_ffmpeg(video_path, thumb_path, "first"):
                        gallery_images.append(thumb_path)
                        yield gallery_images, video_path, None, overall_status, f"Scene {scene_num}: Complete", log("Thumbnail extracted")

                    # Extract last frame for continuity
                    if use_continuity:
                        last_frame_path = str(output_dir / f"lastframe_{scene_num:02d}.jpg")
                        if extract_frame_ffmpeg(video_path, last_frame_path, "last"):
                            yield gallery_images, video_path, None, overall_status, scene_status, log("Last frame extracted for continuity")

                    scene_success = True
                    break  # Success - exit retry loop
                else:
                    raise Exception("Video file not created")

            except Exception as e:
                if attempt < MAX_SCENE_RETRIES:
                    yield gallery_images, None, None, overall_status, f"Scene {scene_num}: Error (will retry)", log(f"ERROR on attempt {attempt + 1}: {e}")
                    continue
                else:
                    yield gallery_images, None, None, overall_status, f"Scene {scene_num}: Failed", log(f"FAILED after {MAX_SCENE_RETRIES + 1} attempts: {e}")
                    failed_scenes.append(scene_num)
                    # Continue to next scene but track failure

    # Check for cancellation before merge (thread-safe)
    if _movie_generation_cancel_event.is_set():
        yield gallery_images, None, None, "Cancelled", "Cancelled by user", log("Generation cancelled before merge")
        return

    # Report failed scenes if any
    if failed_scenes:
        yield gallery_images, None, None, "Merging videos...", "Some scenes failed", log(f"\nWARNING: Scenes {failed_scenes} failed after all retries")

    # Merge all videos
    if len(video_paths) > 0:
        yield gallery_images, None, None, "Merging videos...", "Creating final movie...", log(f"\n=== Merging {len(video_paths)} videos ===")
        progress(0.9, desc="Merging videos...")

        final_path = str(output_dir / "final_movie.mp4")
        if merge_videos_ffmpeg(video_paths, final_path, fps):
            progress(1.0, desc="Complete!")
            success_msg = f"Complete! {len(video_paths)}/{total_scenes} scenes merged"
            if failed_scenes:
                success_msg += f" ({len(failed_scenes)} failed)"
            yield gallery_images, None, final_path, success_msg, "Done!", log(f"Final movie: {final_path}")
        else:
            yield gallery_images, None, None, "Merge failed", "FFmpeg error", log("ERROR: Could not merge videos")
    else:
        yield gallery_images, None, None, "No videos generated", "", log("ERROR: No videos were successfully generated")


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
    temperature: float,
    max_tokens: int,
    save_frames: bool,
    negative_prompt: str,
    progress=gr.Progress()
):
    """Generate video with audio using mlx-video."""

    log_messages = []

    def log(msg: str):
        log_messages.append(msg)
        return "\n".join(log_messages)

    if not prompt.strip():
        gr.Warning("Please enter a prompt!")
        return None, None, "Error: No prompt provided", ""

    # Start logging
    yield None, None, "Starting...", log("Importing mlx-video...")
    progress(0.05, desc="Importing mlx-video...")

    try:
        from mlx_video.generate_av import generate_video_with_audio
    except ImportError as e:
        error_msg = f"Error: mlx-video not installed. Run: uv sync\n{e}"
        yield None, None, error_msg, log(error_msg)
        return

    # Create output paths
    output_dir = Path(tempfile.gettempdir()) / "mlx_video_ui"
    output_dir.mkdir(exist_ok=True)

    video_id = uuid.uuid4().hex[:8]
    output_path = str(output_dir / f"video_{video_id}.mp4")
    audio_path = str(output_dir / f"video_{video_id}.wav")

    yield None, None, "Loading models...", log("Loading models...")
    progress(0.1, desc="Loading models...")

    try:
        # Prepare kwargs
        kwargs = {
            "model_repo": "Lightricks/LTX-2",
            "text_encoder_repo": None,
            "prompt": prompt,
            "height": int(height),
            "width": int(width),
            "num_frames": int(num_frames),
            "seed": int(seed),
            "fps": int(fps),
            "output_path": output_path,
            "output_audio_path": audio_path,
            "verbose": True,
            "enhance_prompt": enhance_prompt,
            "temperature": temperature,
            "max_tokens": int(max_tokens),
            # Note: tiling is not supported by generate_video_with_audio
        }

        # Add image for I2V if provided
        if input_image:
            # Validate image file exists
            if not os.path.exists(input_image):
                error_msg = f"Image file not found: {input_image}"
                yield None, None, f"Error: {error_msg}", log(f"ERROR: {error_msg}")
                return

            # Validate file extension
            valid_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif'}
            ext = os.path.splitext(input_image)[1].lower()
            if ext not in valid_extensions:
                error_msg = f"Invalid image format: {ext}. Use PNG, JPG, JPEG, WebP, BMP, or GIF"
                yield None, None, f"Error: {error_msg}", log(f"ERROR: {error_msg}")
                return

            kwargs["image"] = input_image
            kwargs["image_strength"] = image_strength
            kwargs["image_frame_idx"] = int(image_frame_idx)
            yield None, None, "Processing input image...", log(f"Using image: {input_image}")

        yield None, None, "Generating video latents...", log("Generating video latents (Stage 1)...")
        progress(0.2, desc="Generating video latents...")

        # Warn about unsupported parameters
        if negative_prompt and negative_prompt.strip():
            gr.Warning("Negative prompt is not yet supported by mlx-video and will be ignored")
            log("Note: negative_prompt ignored (not supported by mlx-video)")

        generate_video_with_audio(**kwargs)

        yield None, None, "Encoding final video...", log("Encoding final video with audio...")
        progress(0.9, desc="Encoding final video...")

        # Check if files exist
        video_out = output_path if os.path.exists(output_path) else None
        audio_out = audio_path if os.path.exists(audio_path) else None

        # Save individual frames if requested
        frames_saved = 0
        frames_dir = None
        if save_frames and video_out:
            yield None, None, "Saving individual frames...", log("Saving individual frames as PNG...")
            progress(0.92, desc="Saving frames...")
            try:
                from PIL import Image
                import cv2

                frames_dir = Path(output_path).parent / f"{Path(output_path).stem}_frames"
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
            yield None, audio_out, f"{status}\n\n📁 Video: {video_out}", "\n".join(log_messages)
            return

        yield video_out, audio_out, status, "\n".join(log_messages)

    except Exception as e:
        error_msg = str(e)
        # Check for ffmpeg-related errors
        if "ffprobe" in error_msg.lower() or "ffmpeg" in error_msg.lower():
            error_msg = "FFmpeg niet geïnstalleerd!\n\nInstalleer met: brew install ffmpeg"
        else:
            error_msg = f"Generation failed: {error_msg}"
        gr.Warning(error_msg)
        log(f"ERROR: {error_msg}")
        yield None, None, error_msg, "\n".join(log_messages)


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
        with gr.Tabs() as tabs:

            # ===== GENERATION TAB =====
            with gr.Tab("Generation", id="generation"):
                with gr.Row():
                    # Left column - Controls
                    with gr.Column(scale=1):
                        # Prompt section
                        prompt = gr.Textbox(
                            label="Video Prompt",
                            placeholder="Describe the video you want to generate...\n\nExample: A serene ocean view at sunset, waves gently crashing on golden sand, seagulls flying in the distance",
                            lines=4,
                            max_lines=8,
                            elem_classes="prompt-input"
                        )

                        with gr.Row():
                            llm_provider = gr.Dropdown(
                                choices=["None", "LM Studio", "Ollama"],
                                value="None",
                                label="LLM",
                                scale=1
                            )
                            llm_model = gr.Dropdown(
                                choices=[],
                                label="Model",
                                interactive=False,
                                scale=2,
                                allow_custom_value=True
                            )
                        with gr.Row():
                            enhance_btn = gr.Button("Enhance Prompt", variant="secondary", size="sm", elem_classes="secondary-btn")
                            clear_btn = gr.Button("Clear", variant="secondary", size="sm", elem_classes="secondary-btn")

                        # Prompt Builder (Based on LTX-2 paper's optimal prompt structure)
                        with gr.Accordion("Prompt Builder (LTX-2 Optimized)", open=False):
                            gr.Markdown("*Build structured prompts following the LTX-2 paper's captioning system*")

                            # Visual Section
                            gr.Markdown("#### Visual Elements")
                            with gr.Row():
                                pb_camera = gr.Dropdown(
                                    choices=CAMERA_MOTIONS,
                                    value="Static",
                                    label="Camera Motion",
                                    scale=1
                                )
                                pb_lighting = gr.Dropdown(
                                    choices=LIGHTING_OPTIONS,
                                    value="Natural daylight",
                                    label="Lighting",
                                    scale=1
                                )
                            pb_environment = gr.Textbox(
                                label="Environment",
                                placeholder="forest, city street, interior room, beach...",
                                lines=1
                            )

                            # Subject Section
                            gr.Markdown("#### Subject")
                            pb_subject = gr.Textbox(
                                label="Subject Description",
                                placeholder="A young woman with red hair, a golden retriever, a vintage car...",
                                lines=1
                            )
                            pb_action = gr.Textbox(
                                label="Action",
                                placeholder="walks slowly, looks around, runs through the field...",
                                lines=1
                            )

                            # Audio Section
                            gr.Markdown("#### Audio Elements")
                            with gr.Row():
                                pb_ambient = gr.Textbox(
                                    label="Ambient Sounds",
                                    placeholder="birds chirping, distant traffic, crowd murmur...",
                                    lines=1,
                                    scale=1
                                )
                                pb_foley = gr.Textbox(
                                    label="Foley/Effects",
                                    placeholder="footsteps on gravel, rustling clothes, door creaking...",
                                    lines=1,
                                    scale=1
                                )
                            with gr.Row():
                                pb_music = gr.Textbox(
                                    label="Music",
                                    placeholder="soft piano melody, no music, epic orchestral...",
                                    lines=1,
                                    scale=1
                                )
                                pb_speech = gr.Textbox(
                                    label="Speech/Dialogue",
                                    placeholder="whispers softly, speaks clearly, no dialogue...",
                                    lines=1,
                                    scale=1
                                )
                            # Language/Accent selectors (LTX-2 paper: "speaker, language, and accent identification")
                            with gr.Row():
                                pb_speech_language = gr.Dropdown(
                                    choices=SPEECH_LANGUAGES,
                                    value="No specific language",
                                    label="Speech Language",
                                    scale=1
                                )
                                pb_speech_accent = gr.Dropdown(
                                    choices=SPEECH_ACCENTS,
                                    value="No specific accent",
                                    label="Speech Accent",
                                    scale=1
                                )

                            build_prompt_btn = gr.Button("Build Prompt", variant="secondary", size="sm", elem_classes="secondary-btn")

                        # Prompt Tips Panel (LTX-2 paper best practices)
                        with gr.Accordion("LTX-2 Prompt Tips", open=False):
                            gr.Markdown("""
**Gebaseerd op het LTX-2 paper's captioning systeem:**

1. **Begin met subject**: "A woman with long dark hair...", "A vintage red car..."
2. **Voeg actie toe**: "...walks through a sunlit garden...", "...drives down a winding road..."
3. **Camera beweging**: "...camera slowly tracking alongside...", "...dolly forward..."
4. **Belichting**: "...soft golden hour lighting...", "...dramatic shadows..."
5. **Audio cues**: "...birds singing, footsteps on gravel...", "...engine rumbling, wind noise..."
6. **Wees specifiek**: Niet "ambient sounds", maar "distant traffic, wind through trees"
7. **Spraak**: Vermeld taal en accent: "speaks softly in British English"

**Voorbeeld prompt:**
> A young woman with curly auburn hair walks through a misty forest, camera tracking alongside, golden hour lighting filtering through the trees. Audio: leaves crunching underfoot, distant bird calls, soft wind through branches, she hums quietly in French.
""")

                        # Video Settings
                        gr.Markdown("### Video Settings")
                        with gr.Row():
                            resolution_preset = gr.Dropdown(
                                choices=list(RESOLUTION_PRESETS.keys()),
                                value="1080p (1920x1088)",
                                label="Resolution",
                                scale=1
                            )
                            duration_preset = gr.Dropdown(
                                choices=list(DURATION_PRESETS.keys()),
                                value="10 sec (241 frames)",
                                label="Duration",
                                scale=1
                            )

                        with gr.Row():
                            width_slider = gr.Slider(
                                minimum=256,
                                maximum=3840,  # Up to 4K
                                value=1920,
                                step=64,
                                label="Width"
                            )
                            height_slider = gr.Slider(
                                minimum=256,
                                maximum=2176,  # Up to 4K (2176 % 64 = 0)
                                value=1088,
                                step=64,
                                label="Height"
                            )

                        with gr.Row():
                            frames_slider = gr.Slider(
                                minimum=9,
                                maximum=481,  # LTX-2 supports up to 20 sec (481 frames @ 24fps)
                                value=241,
                                step=8,
                                label="Frames"
                            )
                            fps_slider = gr.Slider(
                                minimum=12,
                                maximum=60,
                                value=24,
                                step=1,
                                label="FPS"
                            )

                        # Hidden inputs for actual values (updated by presets/sliders)
                        with gr.Row(visible=False):
                            width = gr.Number(value=1920, precision=0)
                            height = gr.Number(value=1088, precision=0)
                            num_frames = gr.Number(value=241, precision=0)

                        # Seed and options row
                        with gr.Row():
                            seed = gr.Number(
                                value=42,
                                label="Seed",
                                precision=0,
                                scale=2
                            )
                            random_seed_btn = gr.Button("🎲", variant="secondary", size="sm", scale=0, elem_classes="secondary-btn")
                            save_frames = gr.Checkbox(
                                label="Save Frames as PNG",
                                value=False,
                                scale=1
                            )

                        # Image to Video (I2V)
                        with gr.Accordion("Image to Video (I2V)", open=False):
                            input_image = gr.Image(
                                label="Input Image (optional)",
                                type="filepath",
                                height=150
                            )
                            with gr.Row():
                                image_strength = gr.Slider(
                                    minimum=0.0,
                                    maximum=1.0,
                                    value=0.8,
                                    step=0.05,
                                    label="Image Strength"
                                )
                                image_frame_idx = gr.Number(
                                    value=0,
                                    label="Frame Index",
                                    precision=0
                                )

                        # Generate button
                        generate_btn = gr.Button(
                            "Generate Video",
                            variant="primary",
                            size="lg",
                            elem_classes="generate-btn"
                        )

                    # Right column - Output
                    with gr.Column(scale=1, elem_classes="output-section"):
                        output_video = gr.Video(
                            label="Generated Video",
                            autoplay=True,
                            height=350
                        )
                        output_audio = gr.Audio(
                            label="Generated Audio",
                            type="filepath"
                        )
                        status = gr.Textbox(
                            label="Status",
                            interactive=False,
                            max_lines=2
                        )
                        generation_log = gr.Textbox(
                            label="Generation Log",
                            interactive=False,
                            lines=6,
                            max_lines=10,
                            elem_classes="generation-log"
                        )

            # ===== MOVIE GENERATOR TAB (Position 2) =====
            with gr.Tab("Movie Generator", id="movie_generator"):
                # State for storing scenes
                movie_scenes_state = gr.State([])

                with gr.Row():
                    # Left column - Controls
                    with gr.Column(scale=1):
                        # Story Input Section
                        gr.Markdown("### Story Input")
                        with gr.Group():
                            movie_theme = gr.Textbox(
                                label="Movie Theme / Idea",
                                placeholder="Describe your movie idea...\n\nExample: A magical journey through an enchanted forest, from sunrise to moonlit night, following a glowing firefly.\n\nTip: Upload a reference image below and describe what it represents in your prompt!",
                                lines=4,
                                max_lines=8
                            )

                        # Reference Image Section
                        with gr.Accordion("🖼️ Reference Image (Optional)", open=False):
                            gr.Markdown("*Upload an image and describe what it represents in your story*")
                            movie_input_image = gr.Image(
                                label="Reference Image",
                                type="filepath",
                                height=150
                            )
                            movie_image_description = gr.Textbox(
                                label="What does this image represent?",
                                placeholder="Examples:\n• 'This is the main character'\n• 'This is the setting/background'\n• 'This is the object that appears throughout the story'",
                                lines=2,
                                max_lines=4
                            )
                            with gr.Row():
                                movie_image_strength = gr.Slider(
                                    minimum=0.0,
                                    maximum=1.0,
                                    value=0.8,
                                    step=0.05,
                                    label="Image Influence",
                                    info="How strongly the image affects generation"
                                )

                        # Duration presets for quick selection
                        movie_duration_preset = gr.Dropdown(
                            choices=[
                                "Custom",
                                "30 sec (Short clip)",
                                "1 min (Teaser)",
                                "3 min (Music video)",
                                "5 min (Short film)",
                                "10 min (Episode)",
                                "30 min (TV Episode)",
                                "1 hour (Feature)",
                                "1.5 hours (Standard film)",
                                "2 hours (Hollywood)",
                                "3 hours (Epic)"
                            ],
                            value="3 min (Music video)",
                            label="Duration Preset"
                        )
                        with gr.Row():
                            movie_duration = gr.Slider(
                                minimum=MIN_MOVIE_DURATION,
                                maximum=MAX_MOVIE_DURATION,
                                value=180,
                                step=5,
                                label="Target Duration (seconds)"
                            )
                            movie_duration_display = gr.Textbox(
                                value="3 min",
                                label="Duration",
                                interactive=False,
                                scale=0
                            )
                        num_scenes_display = gr.Number(
                            value=12,
                            label="Number of Scenes",
                            precision=0,
                            interactive=True,
                            minimum=1,
                            maximum=MAX_SCENES
                        )

                        # AI Scene Writer Section - LLM for script + Gemma enhance
                        gr.Markdown("### AI Scene Writer (LLM + Gemma)")
                        gr.Markdown("*Step 1: LLM writes script | Step 2: Gemma enhances each scene*")
                        with gr.Group():
                            # LLM Selection for Script Writing
                            with gr.Row():
                                llm_provider_movie = gr.Dropdown(
                                    choices=["LM Studio", "Ollama"],
                                    value="LM Studio",
                                    label="LLM Provider (Script)",
                                    scale=1
                                )
                                llm_model_movie = gr.Dropdown(
                                    choices=[],
                                    label="Model",
                                    interactive=True,
                                    scale=2,
                                    allow_custom_value=True
                                )
                            refresh_models_movie_btn = gr.Button("Refresh Models", variant="secondary", size="sm", elem_classes="secondary-btn")

                            # Gemma Enhancement Option
                            enhance_scenes_with_gemma = gr.Checkbox(
                                label="Enhance scenes with Gemma (Step 2)",
                                value=True,
                                info="After LLM generates script, Gemma optimizes each scene for LTX-2"
                            )

                            generate_scenes_btn = gr.Button(
                                "Generate Script",
                                variant="primary",
                                size="sm"
                            )

                            # Status textbox for live progress feedback
                            script_generation_status = gr.Textbox(
                                label="Script Generation Status",
                                interactive=False,
                                lines=1,
                                placeholder="Click 'Generate Script' to start...",
                                elem_classes="generation-status"
                            )

                        # Scene Editor Section
                        with gr.Accordion("Scene Editor", open=True):
                            scenes_dataframe = gr.Dataframe(
                                headers=["#", "Description", "Duration (sec)", "Status"],
                                datatype=["number", "str", "number", "str"],
                                column_count=(4, "fixed"),
                                row_count=(0, "dynamic"),
                                interactive=True,
                                wrap=True,
                                label="Scenes",
                                max_height=350,
                                elem_classes="scene-editor"
                            )
                            with gr.Row():
                                add_scene_btn = gr.Button("+ Add Scene", variant="secondary", size="sm", elem_classes="secondary-btn")
                                scene_to_remove = gr.Number(
                                    value=1,
                                    label="Scene #",
                                    precision=0,
                                    minimum=1,
                                    scale=0
                                )
                                remove_scene_btn = gr.Button("Remove", variant="secondary", size="sm", elem_classes="secondary-btn")
                                regenerate_scene_btn = gr.Button("Regenerate", variant="secondary", size="sm", elem_classes="secondary-btn")

                        # Script Manager Section
                        with gr.Accordion("📁 Script Manager", open=False, elem_classes=["glass-card"]):
                            with gr.Row():
                                script_name_input = gr.Textbox(
                                    label="Script Name",
                                    placeholder="My Awesome Movie",
                                    scale=2
                                )
                                save_script_btn = gr.Button("💾 Save", elem_classes=["secondary-btn"], scale=1)

                            with gr.Row():
                                script_dropdown = gr.Dropdown(
                                    label="Saved Scripts",
                                    choices=[],
                                    interactive=True,
                                    scale=2
                                )
                                refresh_scripts_btn = gr.Button("🔄", elem_classes=["secondary-btn"], scale=0, min_width=50)

                            with gr.Row():
                                load_script_btn = gr.Button("📂 Load", elem_classes=["secondary-btn"])
                                delete_script_btn = gr.Button("🗑️ Delete", elem_classes=["secondary-btn"])

                            script_status = gr.Markdown("")

                        # Video Settings Section
                        gr.Markdown("### Video Settings")
                        with gr.Group():
                            resolution_preset_movie = gr.Dropdown(
                                choices=list(RESOLUTION_PRESETS.keys()),
                                value="1080p (1920x1088)",
                                label="Resolution"
                            )
                            with gr.Row():
                                width_movie = gr.Number(value=1920, precision=0, visible=False)
                                height_movie = gr.Number(value=1088, precision=0, visible=False)
                            fps_movie = gr.Slider(
                                minimum=12,
                                maximum=30,
                                value=24,
                                step=1,
                                label="FPS"
                            )
                            with gr.Row():
                                use_continuity = gr.Checkbox(
                                    label="Scene Continuity (I2V)",
                                    value=True,
                                    info="Use last frame of each scene as input for next scene"
                                )
                                continuity_strength = gr.Slider(
                                    minimum=0.3,
                                    maximum=0.9,
                                    value=0.7,
                                    step=0.05,
                                    label="Continuity Strength"
                                )
                            # Gemma enhancement during video generation
                            enhance_prompts_movie = gr.Checkbox(
                                label="Final Gemma polish during generation",
                                value=True,
                                info="Extra Gemma enhancement when generating each scene"
                            )
                            with gr.Row(visible=True) as gemma_settings_movie:
                                temperature_movie = gr.Slider(
                                    minimum=0.0,
                                    maximum=1.0,
                                    value=0.7,
                                    step=0.1,
                                    label="Temperature"
                                )
                                max_tokens_movie = gr.Slider(
                                    minimum=128,
                                    maximum=1024,
                                    value=512,
                                    step=64,
                                    label="Max Tokens"
                                )

                        # Generate Movie Button
                        with gr.Row():
                            generate_movie_btn = gr.Button(
                                "Generate Movie",
                                variant="primary",
                                size="lg",
                                elem_classes="generate-btn"
                            )
                            cancel_movie_btn = gr.Button(
                                "Cancel",
                                variant="secondary",
                                size="lg"
                            )

                    # Right column - Output
                    with gr.Column(scale=1, elem_classes="output-section"):
                        # Progress Section
                        gr.Markdown("### Progress")
                        overall_progress_md = gr.Textbox(
                            label="Overall Status",
                            value="Ready",
                            interactive=False,
                            max_lines=1
                        )
                        scene_progress_md = gr.Textbox(
                            label="Current Scene",
                            value="",
                            interactive=False,
                            max_lines=1
                        )

                        # Preview Section
                        gr.Markdown("### Scene Previews")
                        scene_preview_gallery = gr.Gallery(
                            label="Scene Thumbnails",
                            columns=3,
                            height=200,
                            object_fit="cover"
                        )
                        current_scene_video = gr.Video(
                            label="Current/Latest Scene",
                            autoplay=True,
                            height=200
                        )

                        # Final Output Section
                        gr.Markdown("### Final Movie")
                        final_movie_output = gr.Video(
                            label="Complete Movie",
                            autoplay=True,
                            height=300
                        )

                        # Log Section
                        generation_log_movie = gr.Textbox(
                            label="Generation Log",
                            interactive=False,
                            lines=8,
                            max_lines=15,
                            elem_classes="generation-log"
                        )

            # ===== SETTINGS TAB (Advanced Settings) =====
            with gr.Tab("Advanced Settings", id="settings"):
                with gr.Row():
                    with gr.Column(scale=1):
                        # CFG (Classifier-Free Guidance) Section
                        gr.Markdown("### Classifier-Free Guidance (LTX-2)")
                        gr.Markdown("*Based on LTX-2 paper: optimal video s_t=3, s_m=3; audio s_t=7, s_m=3*")
                        with gr.Group():
                            cfg_preset = gr.Dropdown(
                                choices=list(CFG_PRESET_VALUES.keys()),
                                value="Balanced (Default)",
                                label="CFG Preset"
                            )
                            with gr.Row():
                                text_cfg = gr.Slider(
                                    minimum=1.0,
                                    maximum=10.0,
                                    value=3.0,
                                    step=0.5,
                                    label="Text Guidance (s_t)",
                                    info="Higher = stronger text prompt adherence"
                                )
                                cross_modal_cfg = gr.Slider(
                                    minimum=1.0,
                                    maximum=10.0,
                                    value=3.0,
                                    step=0.5,
                                    label="Cross-Modal Guidance (s_m)",
                                    info="Higher = stronger audio-video sync"
                                )

                        # Built-in Prompt Enhancement (Gemma)
                        gr.Markdown("### Prompt Enhancement (Gemma)")
                        with gr.Group():
                            enhance_prompt_checkbox = gr.Checkbox(
                                label="Enable Gemma Enhancement",
                                value=True,
                                info="Use built-in Gemma 3 for prompt improvement"
                            )
                            with gr.Row():
                                temperature = gr.Slider(
                                    minimum=0.0,
                                    maximum=1.0,
                                    value=0.7,
                                    step=0.1,
                                    label="Temperature"
                                )
                                max_tokens = gr.Slider(
                                    minimum=128,
                                    maximum=1024,
                                    value=512,
                                    step=64,
                                    label="Max Tokens"
                                )

                    with gr.Column(scale=1):
                        # Audio Output Settings
                        gr.Markdown("### Audio Output (LTX-2)")
                        with gr.Group():
                            audio_sample_rate = gr.Radio(
                                choices=[16000, 24000, 48000],
                                value=24000,
                                label="Sample Rate (Hz)",
                                info="24kHz is LTX-2 default output"
                            )
                            stereo_output = gr.Checkbox(
                                label="Stereo Output",
                                value=True,
                                info="LTX-2 supports 2-channel stereo audio"
                            )

                        # Inference/Diffusion Steps (LTX-2 paper: single-step Euler solver)
                        gr.Markdown("### Diffusion Settings")
                        with gr.Group():
                            num_inference_steps = gr.Slider(
                                minimum=10,
                                maximum=100,
                                value=50,
                                step=5,
                                label="Diffusion Steps",
                                info="Minder stappen = sneller, meer = hogere kwaliteit (LTX-2 paper: ~18x sneller dan Wan 2.2)"
                            )

                        # Negative prompt (not supported yet)
                        gr.Markdown("### Other")
                        negative_prompt = gr.Textbox(
                            label="Negative Prompt (NOT YET SUPPORTED)",
                            placeholder="Not yet supported by mlx-video...",
                            lines=2,
                            info="mlx-video does not support negative prompts yet"
                        )

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

        resolution_preset.change(
            fn=on_resolution_change,
            inputs=[resolution_preset],
            outputs=[width, height, width_slider, height_slider]
        )

        # Sync sliders with hidden values
        width_slider.change(fn=lambda x: x, inputs=[width_slider], outputs=[width])
        height_slider.change(fn=lambda x: x, inputs=[height_slider], outputs=[height])
        frames_slider.change(fn=lambda x: x, inputs=[frames_slider], outputs=[num_frames])

        # Duration preset handler
        def on_duration_change(preset):
            if preset == "Custom":
                return gr.update(), gr.update()
            frames = DURATION_PRESETS.get(preset)
            if frames:
                return frames, frames
            return gr.update(), gr.update()

        duration_preset.change(
            fn=on_duration_change,
            inputs=[duration_preset],
            outputs=[num_frames, frames_slider]
        )

        # Random seed button
        random_seed_btn.click(
            fn=randomize_seed,
            outputs=[seed]
        )

        # Clear prompt button
        clear_btn.click(
            fn=lambda: "",
            outputs=[prompt]
        )

        # LLM provider change
        llm_provider.change(
            fn=update_models,
            inputs=[llm_provider],
            outputs=[llm_model]
        )

        # Enhance with external LLM
        # Dual enhance: LLM first, then Gemma
        def dual_enhance_prompt(current_prompt, provider, model, use_gemma):
            if not current_prompt.strip():
                gr.Warning("Enter a prompt first")
                return current_prompt

            # Step 1: LLM enhancement (if provider selected)
            if provider and provider != "None":
                gr.Info("Step 1: Enhancing with LLM...")
                enhanced = enhance_prompt_with_llm(current_prompt, provider, model)
            else:
                enhanced = current_prompt

            # Step 2: Gemma enhancement (if enabled)
            if use_gemma and enhanced:
                gr.Info("Step 2: Enhancing with Gemma...")
                enhanced = enhance_scene_with_gemma(enhanced, temperature=0.7, max_tokens=512)
                gr.Info("Dual enhancement complete!")

            return enhanced

        enhance_btn.click(
            fn=dual_enhance_prompt,
            inputs=[prompt, llm_provider, llm_model, enhance_prompt_checkbox],
            outputs=[prompt]
        )

        # Prompt Builder - Build prompt from components
        build_prompt_btn.click(
            fn=build_prompt_from_components,
            inputs=[
                pb_camera, pb_lighting, pb_environment,
                pb_subject, pb_action,
                pb_ambient, pb_foley, pb_music, pb_speech,
                pb_speech_language, pb_speech_accent
            ],
            outputs=[prompt]
        )

        # CFG Preset handler
        cfg_preset.change(
            fn=apply_cfg_preset,
            inputs=[cfg_preset],
            outputs=[text_cfg, cross_modal_cfg]
        )

        # Main generate button
        generate_btn.click(
            fn=generate_video_ui,
            inputs=[
                prompt, width, height, num_frames, fps_slider,
                seed, input_image, image_strength, image_frame_idx,
                enhance_prompt_checkbox, temperature, max_tokens,
                save_frames, negative_prompt
            ],
            outputs=[output_video, output_audio, status, generation_log]
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
            elif seconds < 3600:
                mins = seconds // 60
                secs = seconds % 60
                return f"{mins}m {secs}s" if secs else f"{mins} min"
            else:
                hours = seconds // 3600
                mins = (seconds % 3600) // 60
                return f"{hours}h {mins}m" if mins else f"{hours} hour"

        # Duration preset change
        def on_duration_preset_change(preset):
            if preset == "Custom":
                return gr.update(), gr.update(), gr.update()
            duration = DURATION_PRESET_MAP.get(preset, 30)
            num_scenes = calculate_scenes_from_duration(duration)
            display = format_duration(duration)
            return duration, display, num_scenes

        movie_duration_preset.change(
            fn=on_duration_preset_change,
            inputs=[movie_duration_preset],
            outputs=[movie_duration, movie_duration_display, num_scenes_display]
        )

        # Auto-calculate number of scenes from duration (when slider changes)
        def on_duration_change_movie(duration):
            num_scenes = calculate_scenes_from_duration(int(duration))
            display = format_duration(int(duration))
            return num_scenes, display

        movie_duration.change(
            fn=on_duration_change_movie,
            inputs=[movie_duration],
            outputs=[num_scenes_display, movie_duration_display]
        )

        # LLM provider change for movie tab
        llm_provider_movie.change(
            fn=update_models,
            inputs=[llm_provider_movie],
            outputs=[llm_model_movie]
        )

        # Refresh models button for movie tab
        refresh_models_movie_btn.click(
            fn=update_models,
            inputs=[llm_provider_movie],
            outputs=[llm_model_movie]
        )

        # Resolution preset for movie tab
        def on_resolution_change_movie(preset):
            if preset == "Custom":
                return gr.update(), gr.update()
            res = RESOLUTION_PRESETS.get(preset)
            if res:
                return res[0], res[1]
            return gr.update(), gr.update()

        resolution_preset_movie.change(
            fn=on_resolution_change_movie,
            inputs=[resolution_preset_movie],
            outputs=[width_movie, height_movie]
        )

        # ===== SCRIPT MANAGEMENT EVENT HANDLERS =====
        def refresh_script_list():
            """Refresh the list of saved scripts."""
            scripts = list_scripts()
            choices = [(f"{s['name']} ({s['scenes']} scenes) - {s['created']}", s['path']) for s in scripts]
            return gr.update(choices=choices)

        def save_current_script(name, theme, scenes, width, height, fps):
            """Save the current script to a file."""
            if not name:
                return "⚠️ Please enter a script name", gr.update()
            if not scenes:
                return "⚠️ No scenes to save", gr.update()
            settings = {"width": int(width), "height": int(height), "fps": int(fps)}
            msg = save_script(name, theme, scenes, settings)
            return msg, refresh_script_list()

        def load_selected_script(selected):
            """Load a selected script."""
            if not selected:
                return gr.update(), gr.update(), [], "⚠️ No script selected"
            try:
                theme, scenes, settings = load_script(selected)
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
        save_script_btn.click(
            save_current_script,
            inputs=[script_name_input, movie_theme, movie_scenes_state, width_movie, height_movie, fps_movie],
            outputs=[script_status, script_dropdown]
        )

        refresh_scripts_btn.click(refresh_script_list, outputs=[script_dropdown])

        load_script_btn.click(
            load_selected_script,
            inputs=[script_dropdown],
            outputs=[movie_theme, scenes_dataframe, movie_scenes_state, script_status]
        )

        delete_script_btn.click(
            delete_selected_script,
            inputs=[script_dropdown],
            outputs=[script_status, script_dropdown]
        )

        # Generate scenes sequentially with LLM + Gemma enhancement (live updates)
        def on_generate_scenes_sequential(theme, num_scenes, provider, model, enhance_gemma, image_desc, current_scenes, progress=gr.Progress()):
            if not theme.strip():
                gr.Warning("Please enter a movie theme first!")
                yield current_scenes, scenes_to_dataframe(current_scenes), "Error: No theme provided"
                return

            # Use the sequential generator for live updates
            for scenes, status in generate_scenes_sequentially(
                theme,
                int(num_scenes),
                provider,
                model,
                enhance_with_gemma=enhance_gemma,
                image_description=image_desc,
                progress=progress
            ):
                df_data = scenes_to_dataframe(scenes) if scenes else []
                yield scenes, df_data, status

        generate_scenes_btn.click(
            fn=on_generate_scenes_sequential,
            inputs=[
                movie_theme, num_scenes_display,
                llm_provider_movie, llm_model_movie,
                enhance_scenes_with_gemma, movie_image_description, movie_scenes_state
            ],
            outputs=[movie_scenes_state, scenes_dataframe, script_generation_status]
        )

        # Sync dataframe changes to state
        def sync_dataframe_to_state(df_data):
            if df_data is None or len(df_data) == 0:
                return []
            scenes = dataframe_to_scenes(df_data)
            return scenes

        scenes_dataframe.change(
            fn=sync_dataframe_to_state,
            inputs=[scenes_dataframe],
            outputs=[movie_scenes_state]
        )

        # Add scene
        def on_add_scene(scenes):
            new_scenes = add_empty_scene(scenes if scenes else [])
            return new_scenes, scenes_to_dataframe(new_scenes)

        add_scene_btn.click(
            fn=on_add_scene,
            inputs=[movie_scenes_state],
            outputs=[movie_scenes_state, scenes_dataframe]
        )

        # Remove scene
        def on_remove_scene(scenes, index):
            if not scenes:
                return scenes, []
            new_scenes = remove_scene_at_index(scenes, int(index))
            return new_scenes, scenes_to_dataframe(new_scenes)

        remove_scene_btn.click(
            fn=on_remove_scene,
            inputs=[movie_scenes_state, scene_to_remove],
            outputs=[movie_scenes_state, scenes_dataframe]
        )

        # Regenerate single scene with LLM + Gemma
        def on_regenerate_scene(scenes, index, theme, provider, model, enhance_gemma):
            if not scenes:
                gr.Warning("No scenes to regenerate")
                return scenes, scenes_to_dataframe(scenes) if scenes else []

            new_scenes = regenerate_single_scene(
                scenes, int(index), theme, provider, model, enhance_gemma
            )
            return new_scenes, scenes_to_dataframe(new_scenes)

        regenerate_scene_btn.click(
            fn=on_regenerate_scene,
            inputs=[
                movie_scenes_state, scene_to_remove, movie_theme,
                llm_provider_movie, llm_model_movie, enhance_scenes_with_gemma
            ],
            outputs=[movie_scenes_state, scenes_dataframe]
        )

        # Cancel movie generation
        cancel_movie_btn.click(
            fn=cancel_movie_generation,
            outputs=[cancel_movie_btn]
        )

        # Generate movie
        def on_generate_movie(
            scenes, df_data, width, height, fps,
            use_cont, cont_strength,
            enhance, temp, max_tok,
            ref_image, ref_image_strength
        ):
            # CRITICAL: Explicitly sync dataframe to scenes before generation
            # This ensures we use the user's edited descriptions, not stale state
            if df_data is not None and len(df_data) > 0:
                scenes = dataframe_to_scenes(df_data)
                print(f"[SYNC] Synced {len(scenes)} scenes from dataframe")

            if not scenes:
                gr.Warning("Generate scenes first!")
                yield [], None, None, "Error: No scenes", "", "Generate scenes first before creating the movie."
                return

            # Run the pipeline generator
            for result in generate_movie_pipeline(
                scenes,
                int(width), int(height), int(fps),
                use_cont, cont_strength,
                enhance, temp, int(max_tok),
                input_image=ref_image,
                image_strength=ref_image_strength
            ):
                yield result

        generate_movie_btn.click(
            fn=on_generate_movie,
            inputs=[
                movie_scenes_state, scenes_dataframe,  # Include dataframe for explicit sync
                width_movie, height_movie, fps_movie,
                use_continuity, continuity_strength,
                enhance_prompts_movie, temperature_movie, max_tokens_movie,
                movie_input_image, movie_image_strength
            ],
            outputs=[
                scene_preview_gallery, current_scene_video, final_movie_output,
                overall_progress_md, scene_progress_md, generation_log_movie
            ]
        )

        # Load saved scripts on app startup
        demo.load(refresh_script_list, outputs=[script_dropdown])

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
