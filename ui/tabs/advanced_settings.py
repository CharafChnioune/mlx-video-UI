from __future__ import annotations

from dataclasses import dataclass

import gradio as gr


@dataclass
class AdvancedSettingsTabComponents:
    cfg_preset: gr.Dropdown
    text_cfg: gr.Slider
    cross_modal_cfg: gr.Slider
    prompt_enhancer_choice: gr.Dropdown
    llm_provider: gr.Dropdown
    llm_model: gr.Dropdown
    refresh_models_btn: gr.Button
    enhance_prompt_checkbox: gr.Checkbox
    temperature: gr.Slider
    max_tokens: gr.Slider
    audio_sample_rate: gr.Radio
    stereo_output: gr.Checkbox
    num_inference_steps: gr.Slider
    negative_prompt: gr.Textbox


def build_advanced_settings_tab(
    cfg_preset_values: dict[str, dict[str, float] | None],
) -> AdvancedSettingsTabComponents:
    with gr.Tab("Advanced Settings", id="settings"):
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Classifier-Free Guidance (LTX-2)")
                gr.Markdown("*Based on LTX-2 paper: optimal video s_t=3, s_m=3; audio s_t=7, s_m=3*")
                with gr.Group():
                    cfg_preset = gr.Dropdown(
                        choices=list(cfg_preset_values.keys()),
                        value="Balanced (Default)",
                        label="CFG Preset",
                    )
                    with gr.Row():
                        text_cfg = gr.Slider(
                            minimum=1.0,
                            maximum=10.0,
                            value=3.0,
                            step=0.5,
                            label="Text Guidance (s_t)",
                            info="Higher = stronger text prompt adherence",
                        )
                        cross_modal_cfg = gr.Slider(
                            minimum=1.0,
                            maximum=10.0,
                            value=3.0,
                            step=0.5,
                            label="Cross-Modal Guidance (s_m)",
                            info="Higher = stronger audio-video sync",
                        )

                gr.Markdown("### Prompt Enhancement")
                with gr.Group():
                    with gr.Row():
                        llm_provider = gr.Dropdown(
                            choices=["None", "LM Studio", "Ollama"],
                            value="None",
                            label="LLM Provider (Global)",
                            scale=1,
                            allow_custom_value=True,
                        )
                        llm_model = gr.Dropdown(
                            choices=[],
                            label="LLM Model",
                            interactive=False,
                            scale=2,
                            allow_custom_value=True,
                        )
                        refresh_models_btn = gr.Button(
                            "Refresh",
                            variant="secondary",
                            size="sm",
                            scale=0,
                            elem_classes="secondary-btn",
                        )
                    prompt_enhancer_choice = gr.Dropdown(
                        choices=["Gemma (Built-in)", "LLM (Ollama/LM Studio)"],
                        value="Gemma (Built-in)",
                        label="Prompt Enhancer",
                        info="LLM provider overrides Gemma when selected",
                    )
                    enhance_prompt_checkbox = gr.Checkbox(
                        label="Enable Auto-Enhancement",
                        value=True,
                        info="Automatisch prompts verbeteren bij generatie",
                    )
                    with gr.Row():
                        temperature = gr.Slider(
                            minimum=0.0,
                            maximum=1.0,
                            value=0.7,
                            step=0.1,
                            label="Temperature",
                        )
                        max_tokens = gr.Slider(
                            minimum=512,
                            maximum=4096,
                            value=2048,
                            step=256,
                            label="Max Tokens",
                        )

            with gr.Column(scale=1):
                gr.Markdown("### Audio Output (LTX-2)")
                with gr.Group():
                    audio_sample_rate = gr.Radio(
                        choices=[16000, 24000, 48000],
                        value=24000,
                        label="Sample Rate (Hz)",
                        info="24kHz is LTX-2 default output",
                    )
                    stereo_output = gr.Checkbox(
                        label="Stereo Output",
                        value=True,
                        info="LTX-2 supports 2-channel stereo audio",
                    )

                gr.Markdown("### Diffusion Settings")
                with gr.Group():
                    num_inference_steps = gr.Slider(
                        minimum=10,
                        maximum=100,
                        value=50,
                        step=5,
                        label="Diffusion Steps",
                        info=(
                            "Minder stappen = sneller, meer = hogere kwaliteit "
                            "(LTX-2 paper: ~18x sneller dan Wan 2.2)"
                        ),
                    )

                gr.Markdown("### Other")
                negative_prompt = gr.Textbox(
                    label="Negative Prompt (Legacy)",
                    placeholder="Use Pipeline Settings > Dev pipeline for CFG + negative prompts",
                    lines=2,
                    info="Negative prompts now work with the Dev pipeline in Generation tab",
                    interactive=False,
                )

    return AdvancedSettingsTabComponents(
        cfg_preset=cfg_preset,
        text_cfg=text_cfg,
        cross_modal_cfg=cross_modal_cfg,
        prompt_enhancer_choice=prompt_enhancer_choice,
        llm_provider=llm_provider,
        llm_model=llm_model,
        refresh_models_btn=refresh_models_btn,
        enhance_prompt_checkbox=enhance_prompt_checkbox,
        temperature=temperature,
        max_tokens=max_tokens,
        audio_sample_rate=audio_sample_rate,
        stereo_output=stereo_output,
        num_inference_steps=num_inference_steps,
        negative_prompt=negative_prompt,
    )
