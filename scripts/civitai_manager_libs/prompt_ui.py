"""
Prompt UI Module - Dual Mode Compatible

This module has been modified to support both AUTOMATIC1111 and standalone modes
through the compatibility layer.
"""

import gradio as gr

from .conditional_imports import import_manager

from . import prompt
from . import util
from .compat.compat_layer import CompatibilityLayer

# Compatibility layer variables
_compat_layer = None


def set_compatibility_layer(compat_layer):
    """Set compatibility layer."""
    global _compat_layer
    _compat_layer = compat_layer


def on_option_change(option):
    parameters = None

    sampler = None
    steps = 1
    faces = False
    upscaler = None
    enable_hr = False
    size = None
    size_width = 0
    size_height = 0

    hr_steps = 0
    hr_denoising = 0.7
    hr_upscale = 2
    hr_resize = None
    hr_resize_width = 0
    hr_resize_height = 0

    cfg_scale = 7.0
    others = None

    try:
        parameters = prompt.parse_option_data(option)
    except:
        pass

    if parameters:

        sampler = parameters.pop('Sampler', None)
        steps = parameters.pop('Steps', 1)
        faces = parameters.pop('Face restoration', False)

        size = parameters.pop('Size', None)

        if size:
            try:
                size_width, size_height = map(int, size.split("x"))
            except:
                pass

        cfg_scale = parameters.pop('CFG scale', 7.0)
        upscaler = parameters.pop('Hires upscaler', None)
        if upscaler:
            enable_hr = True
            hr_steps = parameters.pop('Hires steps', 0)
            hr_denoising = parameters.pop('Denoising strength', 0.7)
            hr_upscale = parameters.pop('Hires upscale', 2)
            hr_resize = parameters.pop('Hires resize', None)
            if hr_resize:
                try:
                    hr_resize_width, hr_resize_height = map(int, hr_resize.split("x"))
                except:
                    pass

        others = [f"{k}:{v}" for k, v in parameters.items()]
        if others:
            others = ", ".join(others)

    return (
        steps,
        sampler,
        faces,
        enable_hr,
        gr.update(visible=True if enable_hr else False),
        upscaler,
        hr_steps,
        hr_denoising,
        hr_upscale,
        hr_resize_width,
        hr_resize_height,
        size_width,
        size_height,
        cfg_scale,
        others,
    )


def on_make_parameters(
    steps,
    sampler,
    faces,
    cfg_scale,
    size_width,
    size_height,
    enable_hr,
    upscaler,
    hr_steps,
    hr_denoising,
    hr_upscale,
    hr_resize_width,
    hr_resize_height,
    others,
):

    parameters_string = f"Steps:{steps}"

    if sampler:
        parameters_string = parameters_string + f", Sampler:{sampler}"

    if faces:
        parameters_string = parameters_string + f", Face restoration:CodeFormer"

    if cfg_scale:
        parameters_string = parameters_string + f", CFG scale:{cfg_scale}"

    if size_width and size_height:
        size = f"{size_width}x{size_height}"
        parameters_string = parameters_string + f", Size:{size}"

    if enable_hr:
        if upscaler:
            parameters_string = parameters_string + f", Hires upscaler:{upscaler}"

        if hr_steps:
            parameters_string = parameters_string + f", Hires steps:{hr_steps}"

        if hr_denoising:
            parameters_string = parameters_string + f", Denoising strength:{hr_denoising}"

        if hr_upscale:
            parameters_string = parameters_string + f", Hires upscale:{hr_upscale}"

        if hr_resize_width and hr_resize_height:
            hr_resize = f"{hr_resize_width}x{hr_resize_height}"
            parameters_string = parameters_string + f", Hires resize:{hr_resize}"

    if others:
        parameters_string = parameters_string + f", {others}"

    return parameters_string


def on_enable_hr_change(
    steps,
    sampler,
    faces,
    cfg_scale,
    size_width,
    size_height,
    enable_hr,
    upscaler,
    hr_steps,
    hr_denoising,
    hr_upscale,
    hr_resize_width,
    hr_resize_height,
    others,
):
    parameter_string = on_make_parameters(
        steps,
        sampler,
        faces,
        cfg_scale,
        size_width,
        size_height,
        enable_hr,
        upscaler,
        hr_steps,
        hr_denoising,
        hr_upscale,
        hr_resize_width,
        hr_resize_height,
        others,
    )
    return gr.update(visible=enable_hr), parameter_string


def ui(option):
    with gr.Row():
        parameters = gr.Textbox(label="Parameters", lines=3, interactive=True, container=True)
    with gr.Row():
        # Get samplers through compatibility layer
        sampler_choices = _get_sampler_choices()
        sampler = gr.Dropdown(label="Sampling method", choices=sampler_choices, interactive=True)
        steps = gr.Slider(
            minimum=1, maximum=150, step=1, label="Sampling steps", value=20, interactive=True
        )
    with gr.Row(Variant="compact"):
        restore_faces = gr.Checkbox(label='Restore faces', value=False, interactive=True)
        # tiling = gr.Checkbox(label='Tiling', value=False, interactive=True)
        enable_hr = gr.Checkbox(label='Hires. fix', value=False, interactive=True)
    with gr.Row(visible=False) as hr:
        with gr.Column():
            with gr.Row(variant="compact"):
                # Get upscalers through compatibility layer
                upscaler_choices = _get_upscaler_choices()
                hr_upscaler = gr.Dropdown(
                    label="Upscaler", choices=upscaler_choices, interactive=True
                )
                hr_second_pass_steps = gr.Slider(
                    minimum=0, maximum=150, step=1, label='Hires steps', value=0, interactive=True
                )
                denoising_strength = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    step=0.01,
                    label='Denoising strength',
                    value=0.7,
                    interactive=True,
                )
            with gr.Row(variant="compact"):
                hr_upscale = gr.Slider(
                    minimum=1.0,
                    maximum=4.0,
                    step=0.05,
                    label="Upscale by",
                    value=2.0,
                    interactive=True,
                )
                hr_resize_x = gr.Slider(
                    minimum=0,
                    maximum=2048,
                    step=8,
                    label="Resize width to",
                    value=0,
                    interactive=True,
                )
                hr_resize_y = gr.Slider(
                    minimum=0,
                    maximum=2048,
                    step=8,
                    label="Resize height to",
                    value=0,
                    interactive=True,
                )
    with gr.Row():
        with gr.Column():
            width = gr.Slider(
                minimum=64, maximum=2048, step=8, label="Width", value=512, interactive=True
            )
            height = gr.Slider(
                minimum=64, maximum=2048, step=8, label="Height", value=512, interactive=True
            )
            cfg_scale = gr.Slider(
                minimum=1.0, maximum=30.0, step=0.5, label='CFG Scale', value=7.0, interactive=True
            )
    with gr.Row(visible=True):
        others = gr.Textbox(label="other", visible=True)

    option.change(
        fn=on_option_change,
        inputs=option,
        outputs=[
            steps,
            sampler,
            restore_faces,
            enable_hr,
            hr,
            hr_upscaler,
            hr_second_pass_steps,
            denoising_strength,
            hr_upscale,
            hr_resize_x,
            hr_resize_y,
            width,
            height,
            cfg_scale,
            others,
        ],
    )

    sampler.change(
        fn=on_make_parameters,
        inputs=[
            steps,
            sampler,
            restore_faces,
            cfg_scale,
            width,
            height,
            enable_hr,
            hr_upscaler,
            hr_second_pass_steps,
            denoising_strength,
            hr_upscale,
            hr_resize_x,
            hr_resize_y,
            others,
        ],
        outputs=[parameters],
    )

    enable_hr.change(
        fn=on_enable_hr_change,
        inputs=[
            steps,
            sampler,
            restore_faces,
            cfg_scale,
            width,
            height,
            enable_hr,
            hr_upscaler,
            hr_second_pass_steps,
            denoising_strength,
            hr_upscale,
            hr_resize_x,
            hr_resize_y,
            others,
        ],
        outputs=[hr, parameters],
    )

    steps.change(
        fn=on_make_parameters,
        inputs=[
            steps,
            sampler,
            restore_faces,
            cfg_scale,
            width,
            height,
            enable_hr,
            hr_upscaler,
            hr_second_pass_steps,
            denoising_strength,
            hr_upscale,
            hr_resize_x,
            hr_resize_y,
            others,
        ],
        outputs=[parameters],
    )

    restore_faces.change(
        fn=on_make_parameters,
        inputs=[
            steps,
            sampler,
            restore_faces,
            cfg_scale,
            width,
            height,
            enable_hr,
            hr_upscaler,
            hr_second_pass_steps,
            denoising_strength,
            hr_upscale,
            hr_resize_x,
            hr_resize_y,
            others,
        ],
        outputs=[parameters],
    )

    hr_upscaler.change(
        fn=on_make_parameters,
        inputs=[
            steps,
            sampler,
            restore_faces,
            cfg_scale,
            width,
            height,
            enable_hr,
            hr_upscaler,
            hr_second_pass_steps,
            denoising_strength,
            hr_upscale,
            hr_resize_x,
            hr_resize_y,
            others,
        ],
        outputs=[parameters],
    )

    hr_second_pass_steps.change(
        fn=on_make_parameters,
        inputs=[
            steps,
            sampler,
            restore_faces,
            cfg_scale,
            width,
            height,
            enable_hr,
            hr_upscaler,
            hr_second_pass_steps,
            denoising_strength,
            hr_upscale,
            hr_resize_x,
            hr_resize_y,
            others,
        ],
        outputs=[parameters],
    )

    denoising_strength.change(
        fn=on_make_parameters,
        inputs=[
            steps,
            sampler,
            restore_faces,
            cfg_scale,
            width,
            height,
            enable_hr,
            hr_upscaler,
            hr_second_pass_steps,
            denoising_strength,
            hr_upscale,
            hr_resize_x,
            hr_resize_y,
            others,
        ],
        outputs=[parameters],
    )

    hr_upscale.change(
        fn=on_make_parameters,
        inputs=[
            steps,
            sampler,
            restore_faces,
            cfg_scale,
            width,
            height,
            enable_hr,
            hr_upscaler,
            hr_second_pass_steps,
            denoising_strength,
            hr_upscale,
            hr_resize_x,
            hr_resize_y,
            others,
        ],
        outputs=[parameters],
    )

    hr_resize_x.change(
        fn=on_make_parameters,
        inputs=[
            steps,
            sampler,
            restore_faces,
            cfg_scale,
            width,
            height,
            enable_hr,
            hr_upscaler,
            hr_second_pass_steps,
            denoising_strength,
            hr_upscale,
            hr_resize_x,
            hr_resize_y,
            others,
        ],
        outputs=[parameters],
    )

    hr_resize_y.change(
        fn=on_make_parameters,
        inputs=[
            steps,
            sampler,
            restore_faces,
            cfg_scale,
            width,
            height,
            enable_hr,
            hr_upscaler,
            hr_second_pass_steps,
            denoising_strength,
            hr_upscale,
            hr_resize_x,
            hr_resize_y,
            others,
        ],
        outputs=[parameters],
    )

    width.change(
        fn=on_make_parameters,
        inputs=[
            steps,
            sampler,
            restore_faces,
            cfg_scale,
            width,
            height,
            enable_hr,
            hr_upscaler,
            hr_second_pass_steps,
            denoising_strength,
            hr_upscale,
            hr_resize_x,
            hr_resize_y,
            others,
        ],
        outputs=[parameters],
    )

    height.change(
        fn=on_make_parameters,
        inputs=[
            steps,
            sampler,
            restore_faces,
            cfg_scale,
            width,
            height,
            enable_hr,
            hr_upscaler,
            hr_second_pass_steps,
            denoising_strength,
            hr_upscale,
            hr_resize_x,
            hr_resize_y,
            others,
        ],
        outputs=[parameters],
    )

    cfg_scale.change(
        fn=on_make_parameters,
        inputs=[
            steps,
            sampler,
            restore_faces,
            cfg_scale,
            width,
            height,
            enable_hr,
            hr_upscaler,
            hr_second_pass_steps,
            denoising_strength,
            hr_upscale,
            hr_resize_x,
            hr_resize_y,
            others,
        ],
        outputs=[parameters],
    )


def _get_sampler_choices():
    """Get sampler choices through compatibility layer"""
    compat = CompatibilityLayer.get_compatibility_layer()

    if compat and hasattr(compat, 'sampler_provider'):
        try:
            return compat.sampler_provider.get_txt2img_samplers()
        except Exception as e:
            util.printD(f"Error getting samplers through compatibility layer: {e}")

    # Fallback: Try WebUI direct access
    sd_samplers = import_manager.get_webui_module('sd_samplers')
    if sd_samplers and hasattr(sd_samplers, 'samplers'):
        try:
            return [x.name for x in sd_samplers.samplers]
        except Exception as e:
            util.printD(f"Error getting samplers from WebUI: {e}")

    # Final fallback: Basic sampler list
    return [
        "Euler",
        "Euler a",
        "LMS",
        "Heun",
        "DPM2",
        "DPM2 a",
        "DPM++ 2S a",
        "DPM++ 2M",
        "DPM++ SDE",
        "DPM fast",
        "DPM adaptive",
        "LMS Karras",
        "DPM2 Karras",
        "DPM2 a Karras",
        "DPM++ 2S a Karras",
        "DPM++ 2M Karras",
        "DPM++ SDE Karras",
        "DDIM",
        "PLMS",
    ]


def _get_upscaler_choices():
    """Get upscaler choices through compatibility layer"""
    compat = CompatibilityLayer.get_compatibility_layer()

    if compat and hasattr(compat, 'config_manager'):
        try:
            # Try to get upscaler configuration from compatibility layer
            upscalers = compat.config_manager.get('upscalers', [])
            if upscalers:
                return upscalers
        except Exception as e:
            util.printD(f"Error getting upscalers through compatibility layer: {e}")

    # Fallback: Try WebUI direct access
    shared = import_manager.get_webui_module('shared')
    if shared:
        try:
            latent_modes = getattr(shared, 'latent_upscale_modes', [])
            sd_upscalers = getattr(shared, 'sd_upscalers', [])
            upscaler_names = [x.name for x in sd_upscalers] if sd_upscalers else []
            return list(latent_modes) + upscaler_names
        except Exception as e:
            util.printD(f"Error getting upscalers from WebUI: {e}")

    # Final fallback: Basic upscaler list
    return [
        "None",
        "Lanczos",
        "Nearest",
        "LDSR",
        "BSRGAN",
        "ESRGAN_4x",
        "R-ESRGAN 4x+",
        "R-ESRGAN 4x+ Anime6B",
        "ScuNET GAN",
        "ScuNET PSNR",
        "SwinIR 4x",
    ]
