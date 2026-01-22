from __future__ import annotations

from dataclasses import dataclass

import gradio as gr


PROMPT_TIPS_MARKDOWN = """
**Based on the LTX-2 paper's captioning system:**

1. **Start with subject**: "A woman with long dark hair...", "A vintage red car..."
2. **Add action**: "...walks through a sunlit garden...", "...drives down a winding road..."
3. **Camera movement**: "...camera slowly tracking alongside...", "...dolly forward..."
4. **Lighting**: "...soft golden hour lighting...", "...dramatic shadows..."
5. **Audio cues**: "...birds singing, footsteps on gravel...", "...engine rumbling, wind noise..."
6. **Be specific**: Not "ambient sounds", but "distant traffic, wind through trees"
7. **Speech**: Mention language and accent: "speaks softly in British English"

**Example prompt:**
> A young woman with curly auburn hair walks through a misty forest, camera tracking alongside, golden hour lighting filtering through the trees. Audio: leaves crunching underfoot, distant bird calls, soft wind through branches, she hums quietly in French.
"""


@dataclass
class GenerationTabComponents:
    prompt: gr.Textbox
    enhance_btn: gr.Button
    clear_btn: gr.Button
    pb_camera: gr.Dropdown
    pb_lighting: gr.Dropdown
    pb_environment: gr.Textbox
    pb_subject: gr.Textbox
    pb_action: gr.Textbox
    pb_ambient: gr.Textbox
    pb_foley: gr.Textbox
    pb_music: gr.Textbox
    pb_speech: gr.Textbox
    pb_speech_language: gr.Dropdown
    pb_speech_accent: gr.Dropdown
    build_prompt_btn: gr.Button
    resolution_preset: gr.Dropdown
    duration_preset: gr.Dropdown
    width_slider: gr.Slider
    height_slider: gr.Slider
    frames_slider: gr.Slider
    fps_slider: gr.Slider
    width: gr.Number
    height: gr.Number
    num_frames: gr.Number
    seed: gr.Number
    random_seed_btn: gr.Button
    save_frames: gr.Checkbox
    tiling_mode: gr.Dropdown
    stream_output: gr.Checkbox
    # Pipeline settings (Dev model)
    pipeline_type: gr.Dropdown
    cfg_scale: gr.Slider
    num_inference_steps: gr.Slider
    negative_prompt: gr.Textbox
    # I2V components
    input_image: gr.Image
    image_strength: gr.Slider
    image_frame_idx: gr.Number
    generate_btn: gr.Button
    output_video: gr.Video
    output_audio: gr.Audio
    streaming_preview: gr.Image
    status: gr.Textbox
    generation_log: gr.Textbox


def build_generation_tab(
    camera_motions: list[str],
    lighting_options: list[str],
    speech_languages: list[str],
    speech_accents: list[str],
    resolution_presets: dict[str, tuple[int, int] | None],
    duration_presets: dict[str, int | None],
) -> GenerationTabComponents:
    with gr.Tab("Generation", id="generation"):
        with gr.Row():
            with gr.Column(scale=1):
                prompt = gr.Textbox(
                    label="Video Prompt",
                    placeholder=(
                        "Describe the video you want to generate...\n\n"
                        "Example: A serene ocean view at sunset, waves gently crashing on "
                        "golden sand, seagulls flying in the distance"
                    ),
                    lines=4,
                    max_lines=8,
                    elem_classes="prompt-input",
                )
                with gr.Row():
                    enhance_btn = gr.Button(
                        "Enhance Prompt",
                        variant="secondary",
                        size="sm",
                        elem_classes="secondary-btn",
                    )
                    clear_btn = gr.Button(
                        "Clear",
                        variant="secondary",
                        size="sm",
                        elem_classes="secondary-btn",
                    )

                with gr.Accordion("Prompt Builder (LTX-2 Optimized)", open=False):
                    gr.Markdown("*Build structured prompts following the LTX-2 paper's captioning system*")

                    gr.Markdown("#### Visual Elements")
                    with gr.Row():
                        pb_camera = gr.Dropdown(
                            choices=camera_motions,
                            value="Static",
                            label="Camera Motion",
                            scale=1,
                        )
                        pb_lighting = gr.Dropdown(
                            choices=lighting_options,
                            value="Natural daylight",
                            label="Lighting",
                            scale=1,
                        )
                    pb_environment = gr.Textbox(
                        label="Environment",
                        placeholder="forest, city street, interior room, beach...",
                        lines=1,
                    )

                    gr.Markdown("#### Subject")
                    pb_subject = gr.Textbox(
                        label="Subject Description",
                        placeholder="A young woman with red hair, a golden retriever, a vintage car...",
                        lines=1,
                    )
                    pb_action = gr.Textbox(
                        label="Action",
                        placeholder="walks slowly, looks around, runs through the field...",
                        lines=1,
                    )

                    gr.Markdown("#### Audio Elements")
                    with gr.Row():
                        pb_ambient = gr.Textbox(
                            label="Ambient Sounds",
                            placeholder="birds chirping, distant traffic, crowd murmur...",
                            lines=1,
                            scale=1,
                        )
                        pb_foley = gr.Textbox(
                            label="Foley/Effects",
                            placeholder="footsteps on gravel, rustling clothes, door creaking...",
                            lines=1,
                            scale=1,
                        )
                    with gr.Row():
                        pb_music = gr.Textbox(
                            label="Music",
                            placeholder="soft piano melody, no music, epic orchestral...",
                            lines=1,
                            scale=1,
                        )
                        pb_speech = gr.Textbox(
                            label="Speech/Dialogue",
                            placeholder="whispers softly, speaks clearly, no dialogue...",
                            lines=1,
                            scale=1,
                        )
                    with gr.Row():
                        pb_speech_language = gr.Dropdown(
                            choices=speech_languages,
                            value="No specific language",
                            label="Speech Language",
                            scale=1,
                        )
                        pb_speech_accent = gr.Dropdown(
                            choices=speech_accents,
                            value="No specific accent",
                            label="Speech Accent",
                            scale=1,
                        )

                    build_prompt_btn = gr.Button(
                        "Build Prompt",
                        variant="secondary",
                        size="sm",
                        elem_classes="secondary-btn",
                    )

                with gr.Accordion("LTX-2 Prompt Tips", open=False):
                    gr.Markdown(PROMPT_TIPS_MARKDOWN)

                gr.Markdown("### Video Settings")
                with gr.Row():
                    resolution_preset = gr.Dropdown(
                        choices=list(resolution_presets.keys()),
                        value="1080p (1920x1088)",
                        label="Resolution",
                        scale=1,
                    )
                    duration_preset = gr.Dropdown(
                        choices=list(duration_presets.keys()),
                        value="10 sec (241 frames)",
                        label="Duration",
                        scale=1,
                    )

                with gr.Row():
                    width_slider = gr.Slider(
                        minimum=256,
                        maximum=3840,
                        value=1920,
                        step=64,
                        label="Width",
                    )
                    height_slider = gr.Slider(
                        minimum=256,
                        maximum=2176,
                        value=1088,
                        step=64,
                        label="Height",
                    )

                with gr.Row():
                    frames_slider = gr.Slider(
                        minimum=9,
                        maximum=481,
                        value=241,
                        step=8,
                        label="Frames",
                    )
                    fps_slider = gr.Slider(
                        minimum=12,
                        maximum=60,
                        value=24,
                        step=1,
                        label="FPS",
                    )

                with gr.Row(visible=False):
                    width = gr.Number(value=1920, precision=0)
                    height = gr.Number(value=1088, precision=0)
                    num_frames = gr.Number(value=241, precision=0)

                with gr.Row():
                    seed = gr.Number(value=42, label="Seed", precision=0, scale=2)
                    random_seed_btn = gr.Button(
                        "🎲",
                        variant="secondary",
                        size="sm",
                        scale=0,
                        elem_classes="secondary-btn",
                    )
                    save_frames = gr.Checkbox(label="Save Frames as PNG", value=False, scale=1)

                with gr.Accordion("Memory Optimization", open=False):
                    tiling_mode = gr.Dropdown(
                        choices=["auto", "none", "conservative", "default", "aggressive", "spatial", "temporal"],
                        value="auto",
                        label="VAE Tiling Mode",
                        info="Memory optimization: aggressive=lowest memory (57% reduction), none=fastest",
                    )
                    stream_output = gr.Checkbox(
                        label="Stream Output Preview",
                        value=False,
                        info="Show frames as they're decoded (requires tiling + dev pipeline)",
                        visible=False,  # Visibility controlled by event handlers
                    )

                with gr.Accordion("Pipeline Settings", open=False):
                    pipeline_type = gr.Dropdown(
                        choices=["distilled", "dev"],
                        value="distilled",
                        label="Pipeline",
                        info="'dev' enables CFG + negative prompts (slower, higher quality)",
                    )
                    cfg_scale = gr.Slider(
                        minimum=1.0,
                        maximum=15.0,
                        value=4.0,
                        step=0.5,
                        label="CFG Scale",
                        info="Classifier-Free Guidance scale (only for dev pipeline)",
                        visible=False,
                    )
                    num_inference_steps = gr.Slider(
                        minimum=10,
                        maximum=100,
                        value=40,
                        step=5,
                        label="Inference Steps",
                        info="Number of denoising steps (only for dev pipeline)",
                        visible=False,
                    )
                    negative_prompt = gr.Textbox(
                        label="Negative Prompt",
                        placeholder="What to avoid in the video...",
                        lines=2,
                        info="Only used with dev pipeline",
                        visible=False,
                    )

                with gr.Accordion("Image to Video (I2V)", open=False):
                    input_image = gr.Image(
                        label="Input Image (optional)",
                        type="filepath",
                        height=150,
                    )
                    with gr.Row():
                        image_strength = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.8,
                            step=0.05,
                            label="Image Strength",
                        )
                        image_frame_idx = gr.Number(
                            value=0,
                            label="Frame Index",
                            precision=0,
                        )

                generate_btn = gr.Button(
                    "Generate Video",
                    variant="primary",
                    size="lg",
                    elem_classes="generate-btn",
                )

            with gr.Column(scale=1, elem_classes="output-section"):
                output_video = gr.Video(label="Generated Video", autoplay=True, height=350)
                streaming_preview = gr.Image(
                    label="Live Preview",
                    visible=False,
                    height=200,
                    show_label=True,
                )
                output_audio = gr.Audio(label="Generated Audio", type="filepath")
                status = gr.Textbox(label="Status", interactive=False, max_lines=2)
                generation_log = gr.Textbox(
                    label="Generation Log",
                    interactive=False,
                    lines=6,
                    max_lines=10,
                    elem_classes="generation-log",
                )

    return GenerationTabComponents(
        prompt=prompt,
        enhance_btn=enhance_btn,
        clear_btn=clear_btn,
        pb_camera=pb_camera,
        pb_lighting=pb_lighting,
        pb_environment=pb_environment,
        pb_subject=pb_subject,
        pb_action=pb_action,
        pb_ambient=pb_ambient,
        pb_foley=pb_foley,
        pb_music=pb_music,
        pb_speech=pb_speech,
        pb_speech_language=pb_speech_language,
        pb_speech_accent=pb_speech_accent,
        build_prompt_btn=build_prompt_btn,
        resolution_preset=resolution_preset,
        duration_preset=duration_preset,
        width_slider=width_slider,
        height_slider=height_slider,
        frames_slider=frames_slider,
        fps_slider=fps_slider,
        width=width,
        height=height,
        num_frames=num_frames,
        seed=seed,
        random_seed_btn=random_seed_btn,
        save_frames=save_frames,
        tiling_mode=tiling_mode,
        stream_output=stream_output,
        pipeline_type=pipeline_type,
        cfg_scale=cfg_scale,
        num_inference_steps=num_inference_steps,
        negative_prompt=negative_prompt,
        input_image=input_image,
        image_strength=image_strength,
        image_frame_idx=image_frame_idx,
        generate_btn=generate_btn,
        output_video=output_video,
        output_audio=output_audio,
        streaming_preview=streaming_preview,
        status=status,
        generation_log=generation_log,
    )
