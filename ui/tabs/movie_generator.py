from __future__ import annotations

from dataclasses import dataclass

import gradio as gr


@dataclass
class MovieGeneratorTabComponents:
    movie_scenes_state: gr.State
    movie_theme: gr.Textbox
    movie_input_image: gr.Image
    movie_image_description: gr.Textbox
    movie_image_strength: gr.Slider
    movie_duration_preset: gr.Dropdown
    movie_duration: gr.Slider
    movie_duration_display: gr.Textbox
    num_scenes_display: gr.Number
    llm_provider: gr.Dropdown
    llm_model: gr.Dropdown
    refresh_models_btn: gr.Button
    enhance_scenes_with_gemma: gr.Checkbox
    generate_scenes_btn: gr.Button
    script_generation_status: gr.Textbox
    scenes_dataframe: gr.Dataframe
    add_scene_btn: gr.Button
    scene_to_remove: gr.Number
    remove_scene_btn: gr.Button
    regenerate_scene_btn: gr.Button
    script_name_input: gr.Textbox
    save_script_btn: gr.Button
    script_dropdown: gr.Dropdown
    refresh_scripts_btn: gr.Button
    load_script_btn: gr.Button
    delete_script_btn: gr.Button
    script_status: gr.Markdown
    resolution_preset: gr.Dropdown
    width: gr.Number
    height: gr.Number
    fps: gr.Slider
    tiling_mode: gr.Dropdown
    use_continuity: gr.Checkbox
    continuity_strength: gr.Slider
    enhance_prompts: gr.Checkbox
    temperature: gr.Slider
    max_tokens: gr.Slider
    generate_movie_btn: gr.Button
    cancel_movie_btn: gr.Button
    overall_progress_md: gr.Textbox
    scene_progress_md: gr.Textbox
    scene_preview_gallery: gr.Gallery
    current_scene_video: gr.Video
    final_movie_output: gr.Video
    generation_log: gr.Textbox


def build_movie_generator_tab(
    resolution_presets: dict[str, tuple[int, int] | None],
    min_movie_duration: int,
    max_movie_duration: int,
    max_scenes: int,
) -> MovieGeneratorTabComponents:
    with gr.Tab("Movie Generator", id="movie_generator"):
        movie_scenes_state = gr.State([])

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Story Input")
                with gr.Group():
                    movie_theme = gr.Textbox(
                        label="Movie Theme / Idea",
                        placeholder=(
                            "Describe your movie idea...\n\n"
                            "Example: A magical journey through an enchanted forest, from "
                            "sunrise to moonlit night, following a glowing firefly.\n\n"
                            "Tip: Upload a reference image below and describe what it "
                            "represents in your prompt!"
                        ),
                        lines=4,
                        max_lines=8,
                    )

                with gr.Accordion("🖼️ Reference Image (Optional)", open=False):
                    gr.Markdown("*Upload an image and describe what it represents in your story*")
                    movie_input_image = gr.Image(
                        label="Reference Image",
                        type="filepath",
                        height=150,
                    )
                    movie_image_description = gr.Textbox(
                        label="What does this image represent?",
                        placeholder=(
                            "Examples:\n"
                            "• 'This is the main character'\n"
                            "• 'This is the setting/background'\n"
                            "• 'This is the object that appears throughout the story'"
                        ),
                        lines=2,
                        max_lines=4,
                    )
                    with gr.Row():
                        movie_image_strength = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.8,
                            step=0.05,
                            label="Image Influence",
                            info="How strongly the image affects generation",
                        )

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
                        "3 hours (Epic)",
                    ],
                    value="3 min (Music video)",
                    label="Duration Preset",
                )
                with gr.Row():
                    movie_duration = gr.Slider(
                        minimum=min_movie_duration,
                        maximum=max_movie_duration,
                        value=180,
                        step=5,
                        label="Target Duration (seconds)",
                    )
                    movie_duration_display = gr.Textbox(
                        value="3 min",
                        label="Duration",
                        interactive=False,
                        scale=0,
                    )
                num_scenes_display = gr.Number(
                    value=12,
                    label="Number of Scenes",
                    precision=0,
                    interactive=True,
                    minimum=1,
                    maximum=max_scenes,
                )

                gr.Markdown("### AI Scene Writer (LLM + Gemma)")
                gr.Markdown("*Step 1: LLM writes script | Step 2: Gemma enhances each scene*")
                with gr.Group():
                    with gr.Row():
                        llm_provider = gr.Dropdown(
                            choices=["LM Studio", "Ollama"],
                            value="LM Studio",
                            label="LLM Provider (Script)",
                            scale=1,
                        )
                        llm_model = gr.Dropdown(
                            choices=[],
                            label="Model",
                            interactive=True,
                            scale=2,
                            allow_custom_value=True,
                        )
                    refresh_models_btn = gr.Button(
                        "Refresh Models",
                        variant="secondary",
                        size="sm",
                        elem_classes="secondary-btn",
                    )

                    enhance_scenes_with_gemma = gr.Checkbox(
                        label="Enhance scenes with Gemma (Step 2)",
                        value=True,
                        info="After LLM generates script, Gemma optimizes each scene for LTX-2",
                    )

                    generate_scenes_btn = gr.Button("Generate Script", variant="primary", size="sm")

                    script_generation_status = gr.Textbox(
                        label="Script Generation Status",
                        interactive=False,
                        lines=1,
                        placeholder="Click 'Generate Script' to start...",
                        elem_classes="generation-status",
                    )

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
                        elem_classes="scene-editor",
                    )
                    with gr.Row():
                        add_scene_btn = gr.Button(
                            "+ Add Scene",
                            variant="secondary",
                            size="sm",
                            elem_classes="secondary-btn",
                        )
                        scene_to_remove = gr.Number(
                            value=1,
                            label="Scene #",
                            precision=0,
                            minimum=1,
                            scale=0,
                        )
                        remove_scene_btn = gr.Button(
                            "Remove",
                            variant="secondary",
                            size="sm",
                            elem_classes="secondary-btn",
                        )
                        regenerate_scene_btn = gr.Button(
                            "Regenerate",
                            variant="secondary",
                            size="sm",
                            elem_classes="secondary-btn",
                        )

                with gr.Accordion("📁 Script Manager", open=False, elem_classes=["glass-card"]):
                    with gr.Row():
                        script_name_input = gr.Textbox(
                            label="Script Name",
                            placeholder="My Awesome Movie",
                            scale=2,
                        )
                        save_script_btn = gr.Button("💾 Save", elem_classes=["secondary-btn"], scale=1)

                    with gr.Row():
                        script_dropdown = gr.Dropdown(
                            label="Saved Scripts",
                            choices=[],
                            interactive=True,
                            scale=2,
                        )
                        refresh_scripts_btn = gr.Button(
                            "🔄",
                            elem_classes=["secondary-btn"],
                            scale=0,
                            min_width=50,
                        )

                    with gr.Row():
                        load_script_btn = gr.Button("📂 Load", elem_classes=["secondary-btn"])
                        delete_script_btn = gr.Button("🗑️ Delete", elem_classes=["secondary-btn"])

                    script_status = gr.Markdown("")

                gr.Markdown("### Video Settings")
                with gr.Group():
                    resolution_preset = gr.Dropdown(
                        choices=list(resolution_presets.keys()),
                        value="1080p (1920x1088)",
                        label="Resolution",
                    )
                    with gr.Row():
                        width = gr.Number(value=1920, precision=0, visible=False)
                        height = gr.Number(value=1088, precision=0, visible=False)
                    fps = gr.Slider(
                        minimum=12,
                        maximum=30,
                        value=24,
                        step=1,
                        label="FPS",
                    )
                    tiling_mode = gr.Dropdown(
                        choices=["auto", "none", "conservative", "default", "aggressive", "spatial", "temporal"],
                        value="auto",
                        label="VAE Tiling Mode",
                        info="Memory optimization: aggressive=lowest memory (57% reduction), none=fastest",
                    )
                    with gr.Row():
                        use_continuity = gr.Checkbox(
                            label="Scene Continuity (I2V)",
                            value=True,
                            info="Use last frame of each scene as input for next scene",
                        )
                        continuity_strength = gr.Slider(
                            minimum=0.3,
                            maximum=0.9,
                            value=0.7,
                            step=0.05,
                            label="Continuity Strength",
                        )
                    enhance_prompts = gr.Checkbox(
                        label="Final Gemma polish during generation",
                        value=True,
                        info="Extra Gemma enhancement when generating each scene",
                    )
                    with gr.Row(visible=True):
                        temperature = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.7,
                            step=0.1,
                            label="Temperature",
                        )
                        max_tokens = gr.Slider(
                            minimum=128,
                            maximum=1024,
                            value=512,
                            step=64,
                            label="Max Tokens",
                        )

                with gr.Row():
                    generate_movie_btn = gr.Button(
                        "Generate Movie",
                        variant="primary",
                        size="lg",
                        elem_classes="generate-btn",
                    )
                    cancel_movie_btn = gr.Button("Cancel", variant="secondary", size="lg")

            with gr.Column(scale=1, elem_classes="output-section"):
                gr.Markdown("### Progress")
                overall_progress_md = gr.Textbox(
                    label="Overall Status",
                    value="Ready",
                    interactive=False,
                    max_lines=1,
                )
                scene_progress_md = gr.Textbox(
                    label="Current Scene",
                    value="",
                    interactive=False,
                    max_lines=1,
                )

                gr.Markdown("### Scene Previews")
                scene_preview_gallery = gr.Gallery(
                    label="Scene Thumbnails",
                    columns=3,
                    height=200,
                    object_fit="cover",
                )
                current_scene_video = gr.Video(
                    label="Current/Latest Scene",
                    autoplay=True,
                    height=200,
                )

                gr.Markdown("### Final Movie")
                final_movie_output = gr.Video(
                    label="Complete Movie",
                    autoplay=True,
                    height=300,
                )

                generation_log = gr.Textbox(
                    label="Generation Log",
                    interactive=False,
                    lines=8,
                    max_lines=15,
                    elem_classes="generation-log",
                )

    return MovieGeneratorTabComponents(
        movie_scenes_state=movie_scenes_state,
        movie_theme=movie_theme,
        movie_input_image=movie_input_image,
        movie_image_description=movie_image_description,
        movie_image_strength=movie_image_strength,
        movie_duration_preset=movie_duration_preset,
        movie_duration=movie_duration,
        movie_duration_display=movie_duration_display,
        num_scenes_display=num_scenes_display,
        llm_provider=llm_provider,
        llm_model=llm_model,
        refresh_models_btn=refresh_models_btn,
        enhance_scenes_with_gemma=enhance_scenes_with_gemma,
        generate_scenes_btn=generate_scenes_btn,
        script_generation_status=script_generation_status,
        scenes_dataframe=scenes_dataframe,
        add_scene_btn=add_scene_btn,
        scene_to_remove=scene_to_remove,
        remove_scene_btn=remove_scene_btn,
        regenerate_scene_btn=regenerate_scene_btn,
        script_name_input=script_name_input,
        save_script_btn=save_script_btn,
        script_dropdown=script_dropdown,
        refresh_scripts_btn=refresh_scripts_btn,
        load_script_btn=load_script_btn,
        delete_script_btn=delete_script_btn,
        script_status=script_status,
        resolution_preset=resolution_preset,
        width=width,
        height=height,
        fps=fps,
        tiling_mode=tiling_mode,
        use_continuity=use_continuity,
        continuity_strength=continuity_strength,
        enhance_prompts=enhance_prompts,
        temperature=temperature,
        max_tokens=max_tokens,
        generate_movie_btn=generate_movie_btn,
        cancel_movie_btn=cancel_movie_btn,
        overall_progress_md=overall_progress_md,
        scene_progress_md=scene_progress_md,
        scene_preview_gallery=scene_preview_gallery,
        current_scene_video=current_scene_video,
        final_movie_output=final_movie_output,
        generation_log=generation_log,
    )
