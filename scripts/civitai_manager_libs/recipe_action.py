"""
Recipe Action Module - Dual Mode Compatible

This module has been modified to support both AUTOMATIC1111 and standalone modes
through the compatibility layer.
"""

import os
import gradio as gr
import datetime
import uuid
import re

from .conditional_imports import import_manager
from .logging_config import get_logger

logger = get_logger(__name__)

from . import setting
from . import recipe
from . import prompt

# from . import prompt_ui
from . import sc_browser_page
import scripts.civitai_manager_libs.ishortcut_core as ishortcut
from . import recipe_browser_page

from .compat.compat_layer import CompatibilityLayer
from .error_handler import with_error_handling
from .exceptions import (
    NetworkError,
    FileOperationError,
    ValidationError,
)

from PIL import Image


def on_ui(recipe_input, shortcut_input, civitai_tabs):

    # data = (
    #     'Best quality, masterpiece, ultra high res, (photorealistic:1.4),girl, beautiful_face, detailed skin,upper body, <lora:caise2-000022:0.6>\n'
    #     'Negative prompt: ng_deepnegative_v1_75t, badhandv4 (worst quality:2), (low quality:2), (normal quality:2), lowres, bad anatomy, bad hands, normal quality, ((monochrome)), ((grayscale)), ng_deepnegative_v1_75t, badhandv4 (worst quality:2), (low quality:2), (normal quality:2), lowres, bad anatomy, bad hands, normal quality, ((monochrome)), ((grayscale)),\n'
    #     'Steps: 28, Sampler: DPM++ 2M Karras, CFG scale: 11, Seed: 2508416159, Size: 640x384, Model hash: 7af26c6c98, Model: RealPerson_xsmix_V04VeryNice, Denoising strength: 0.53, Hires upscale: 2, Hires steps: 20, Hires upscaler: 4x-UltraSharp, Dynamic thresholding enabled: True, Mimic scale: 7, Threshold percentile: 100'
    # )

    # aaa = (
    #     "D:\\AI\\stable-diffusion-webui\\outputs\\download-images\\[Macross Delta]Freyja Wion Charecter LoRA(Freyja Wion Character Model)\\images\\59749-651966.png"
    # )

    with gr.Column(scale=setting.shortcut_browser_screen_split_ratio):
        with gr.Tabs():
            with gr.TabItem("Prompt Recipe List"):
                recipe_new_btn = gr.Button(value="New Recipe", variant="primary")
                recipe_gallery, refresh_recipe_browser = recipe_browser_page.on_ui()
            with gr.TabItem("Generate Prompt From Image"):
                recipe_drop_image = gr.Image(type="pil", label="Drop image", height='100%')

    with gr.Column(
        scale=(
            setting.shortcut_browser_screen_split_ratio_max
            - setting.shortcut_browser_screen_split_ratio
        )
    ):
        with gr.Accordion(label=setting.NEWRECIPE, open=True) as recipe_title_name:
            with gr.Row():
                with gr.Column(scale=4):
                    with gr.Tabs() as recipe_prompt_tabs:
                        with gr.TabItem("Prompt", id="Prompt"):
                            recipe_name = gr.Textbox(
                                label="Name",
                                value="",
                                interactive=True,
                                lines=1,
                                placeholder="Please enter the prompt recipe name.",
                                container=True,
                            )
                            recipe_desc = gr.Textbox(
                                label="Description",
                                value="",
                                interactive=True,
                                lines=3,
                                placeholder="Please enter the prompt recipe description.",
                                container=True,
                                show_copy_button=True,
                            )
                            recipe_prompt = gr.Textbox(
                                label="Prompt",
                                placeholder="Prompt",
                                value="",
                                lines=3,
                                interactive=True,
                                container=True,
                                show_copy_button=True,
                            )
                            recipe_negative = gr.Textbox(
                                label="Negative prompt",
                                placeholder="Negative prompt",
                                show_label=False,
                                value="",
                                lines=3,
                                interactive=True,
                                container=True,
                                show_copy_button=True,
                            )
                            recipe_option = gr.Textbox(
                                label="Parameter",
                                placeholder="Parameter",
                                value="",
                                lines=3,
                                interactive=True,
                                container=True,
                                show_copy_button=True,
                            )
                            # with gr.Accordion(label="Parameter", open=True):
                            #     prompt_ui.ui(recipe_option)
                            # recipe_output = gr.Textbox(label="Generate Info", interactive=False, lines=6, placeholder="The prompt and parameters are combined and displayed here.", container=True, show_copy_button=True)
                            with gr.Row():
                                try:
                                    parameters_copypaste = import_manager.get_webui_module(
                                        'extras', 'parameters_copypaste'
                                    )
                                    if parameters_copypaste:
                                        send_to_buttons = parameters_copypaste.create_buttons(
                                            ["txt2img", "img2img", "inpaint", "extras"]
                                        )
                                except:
                                    pass
                            recipe_classification = gr.Dropdown(
                                label="Prompt Recipe Classification",
                                choices=[setting.PLACEHOLDER] + recipe.get_classifications(),
                                value=setting.PLACEHOLDER,
                                info="You can choose from a list or enter manually. If you enter a classification that didn't exist before, a new classification will be created.",
                                interactive=True,
                                allow_custom_value=True,
                            )
                        with gr.TabItem("Additional Shortcut Models for Reference"):
                            (
                                reference_sc_gallery,
                                refresh_reference_sc_browser,
                                refresh_reference_sc_gallery,
                            ) = sc_browser_page.on_ui(
                                False,
                                "DOWN",
                                setting.prompt_reference_shortcut_column,
                                setting.prompt_reference_shortcut_rows_per_page,
                            )
                    with gr.Row():
                        recipe_create_btn = gr.Button(value="Create", variant="primary")
                        recipe_update_btn = gr.Button(
                            value="Update", variant="primary", visible=False
                        )
                        with gr.Accordion("Delete Prompt Recipe", open=False):
                            recipe_delete_btn = gr.Button(value="Delete", variant="primary")

                with gr.Column(scale=2):
                    gr.Markdown("###")
                    with gr.Tabs() as recipe_reference_tabs:
                        with gr.TabItem("Reference Image", id="reference_image"):
                            recipe_image = gr.Image(
                                type="pil",
                                interactive=True,
                                label="Prompt recipe image",
                                height='100%',
                            )
                            gr.Markdown(
                                "This image does not influence the prompt on the left. You can choose any image that matches the created prompt."
                            )
                            # recipe_image_info = gr.Textbox(label="Ganerate Infomation", lines=6, visible=True)
                        with gr.TabItem("Reference Models", id="reference_model"):
                            reference_delete = gr.Checkbox(
                                label="Delete from references when selecting a thumbnail.",
                                value=False,
                            )

                            with gr.Accordion(
                                "#", open=True, visible=False
                            ) as reference_model_information:
                                reference_modelid = gr.Textbox(visible=False)
                                reference_modeltype = gr.Textbox(visible=False)
                                reference_disp_modeltype = gr.Textbox(
                                    label="Model Type", interactive=False, lines=1
                                )
                                reference_versions = gr.Dropdown(
                                    label="Model Version", interactive=True
                                )
                                reference_filenames = gr.Dropdown(
                                    label="Version filename", interactive=True
                                )
                                reference_weight_slider = gr.Slider(
                                    minimum=0,
                                    maximum=2,
                                    value=0.7,
                                    step=0.1,
                                    label="Preferred weight",
                                    interactive=True,
                                    visible=True,
                                )
                                reference_triger = gr.Textbox(
                                    label="Triger", interactive=True, lines=1
                                )
                                insert_prompt_btn = gr.Button(
                                    value="Add\\Remove from Prompt", variant="primary"
                                )
                                with gr.Row():
                                    goto_model_info_btn = gr.Button(
                                        value="Information", variant="primary"
                                    )
                                    delete_reference_model_btn = gr.Button(
                                        value="Delete", variant="primary"
                                    )
                                close_reference_model_information_btn = gr.Button(
                                    value="Close", variant="primary"
                                )

                            reference_gallery = gr.Gallery(
                                show_label=False,
                                columns=3,
                                height='auto',
                                object_fit=setting.gallery_thumbnail_image_style,
                                preview=False,
                                allow_preview=False,
                            )
                            # with gr.Accordion("Add Reference Shortcut Items", open=False):
                            #     reference_sc_gallery, refresh_reference_sc_browser, refresh_reference_sc_gallery = sc_browser_page.on_ui()
                        with gr.TabItem("Generate Information", id="generation_info"):
                            recipe_output = gr.Textbox(
                                label="Generate Information",
                                interactive=False,
                                lines=20,
                                placeholder="The prompt and parameters are combined and displayed here.",
                                container=True,
                                show_copy_button=True,
                            )

    with gr.Row(visible=False):
        selected_recipe_name = gr.Textbox()

        refresh_recipe = gr.Textbox()
        recipe_generate_data = gr.Textbox()

        reference_shortcuts = gr.State()
        refresh_reference_gallery = gr.Textbox()
    try:
        parameters_copypaste = import_manager.get_webui_module('extras', 'parameters_copypaste')
        if parameters_copypaste and 'send_to_buttons' in locals():
            # Standardize parameters for WebUI compatibility before binding
            compat = CompatibilityLayer.get_compatibility_layer()
            if compat and compat.parameter_processor:
                standardized_info = gr.Textbox(
                    value=compat.parameter_processor.standardize_parameters_for_webui(
                        recipe_output.value or ""
                    ),
                    visible=False,
                )
                parameters_copypaste.bind_buttons(send_to_buttons, recipe_image, standardized_info)
            else:
                parameters_copypaste.bind_buttons(send_to_buttons, recipe_image, recipe_output)
    except Exception:
        pass

    recipe_prompt_tabs.select(on_recipe_prompt_tabs_select, None, [recipe_reference_tabs])

    # reference shortcuts
    reference_gallery.select(
        fn=on_reference_gallery_select,
        inputs=[reference_shortcuts, reference_delete],
        outputs=[
            reference_shortcuts,
            refresh_reference_gallery,
            reference_gallery,  # 이거는 None으로 할 필요는 gallery를 미선택으로 만드는 방법을 몰라서 일단 이렇게 해보자
            reference_modelid,
            # shortcut_input
        ],
        show_progress=False,
    )

    refresh_reference_gallery.change(
        fn=on_reference_gallery_loading,
        inputs=[
            reference_shortcuts,
        ],
        outputs=[reference_gallery],
        show_progress=False,
    )

    reference_sc_gallery.select(
        fn=on_reference_sc_gallery_select,
        inputs=[reference_shortcuts],
        outputs=[
            reference_shortcuts,
            refresh_reference_gallery,
        ],
        show_progress=False,
    )
    # reference shortcuts

    recipe_prompt.blur(
        generate_prompt, [recipe_prompt, recipe_negative, recipe_option], recipe_output
    )
    recipe_negative.blur(
        generate_prompt, [recipe_prompt, recipe_negative, recipe_option], recipe_output
    )
    recipe_option.blur(
        generate_prompt, [recipe_prompt, recipe_negative, recipe_option], recipe_output
    )

    # 이렇게 합시다.
    # send to reciepe -> recipe_input : input drop image, reciep image, call recipe_generate_data(drop image) -> recipe_generate_data: img info 생성 ,분석, 갱신
    # drop image -> recipe_drop_image.upload(drop image) : reciep image, call recipe_generate_data(drop image) -> recipe_generate_data: img info 생성 ,분석, 갱신
    # drop image.upload 만쓰이고 change는 안쓰임

    # 이미지를 드롭할때는 현재 레시피 상태에서 정보만 갱신한다.
    recipe_drop_image_upload = recipe_drop_image.upload(
        fn=on_recipe_drop_image_upload,
        inputs=[recipe_drop_image],
        outputs=[recipe_image, recipe_generate_data],
        show_progress=False,
    )

    # Process PNG info asynchronously on generate_data change
    recipe_generate_data_change = recipe_generate_data.change(
        fn=on_recipe_generate_data_change,
        inputs=[recipe_drop_image],
        outputs=[recipe_prompt, recipe_negative, recipe_option, recipe_output],
    )

    # shortcut information 에서 넘어올때는 새로운 레시피를 만든다.
    recipe_input.change(
        fn=on_recipe_input_change,
        inputs=[recipe_input, reference_shortcuts],
        outputs=[
            selected_recipe_name,
            recipe_drop_image,
            recipe_image,
            recipe_generate_data,
            recipe_input,
            civitai_tabs,
            recipe_prompt_tabs,
            recipe_reference_tabs,
            recipe_prompt,
            recipe_negative,
            recipe_option,
            recipe_output,
            # 새 레시피 상태로 만든다.
            recipe_name,
            recipe_desc,
            recipe_classification,
            recipe_title_name,
            recipe_create_btn,
            recipe_update_btn,
            reference_shortcuts,
            reference_modelid,
            reference_gallery,
            refresh_reference_gallery,
        ],
        cancels=[recipe_drop_image_upload, recipe_generate_data_change],
    )

    refresh_recipe.change(
        fn=on_refresh_recipe_change,
        inputs=None,
        outputs=[refresh_reference_sc_browser, refresh_recipe_browser, refresh_reference_gallery],
        show_progress=False,
    )

    recipe_gallery.select(
        fn=on_recipe_gallery_select,
        inputs=None,
        outputs=[
            selected_recipe_name,
            recipe_name,
            recipe_desc,
            recipe_prompt,
            recipe_negative,
            recipe_option,
            recipe_output,
            recipe_classification,
            recipe_title_name,
            recipe_image,
            recipe_drop_image,
            recipe_create_btn,
            recipe_update_btn,
            reference_shortcuts,
            reference_modelid,
            reference_gallery,
            refresh_reference_gallery,
        ],
        cancels=recipe_drop_image_upload,
    )

    recipe_new_btn.click(
        fn=on_recipe_new_btn_click,
        inputs=None,
        outputs=[
            selected_recipe_name,
            recipe_name,
            recipe_desc,
            recipe_prompt,
            recipe_negative,
            recipe_option,
            recipe_output,
            recipe_classification,
            recipe_title_name,
            recipe_image,
            recipe_drop_image,
            recipe_create_btn,
            recipe_update_btn,
            reference_shortcuts,
            reference_modelid,
            refresh_reference_gallery,
        ],
    )

    recipe_create_btn.click(
        fn=on_recipe_create_btn_click,
        inputs=[
            recipe_name,
            recipe_desc,
            recipe_prompt,
            recipe_negative,
            recipe_option,
            recipe_classification,
            recipe_image,
            reference_shortcuts,
        ],
        outputs=[
            selected_recipe_name,
            recipe_classification,
            recipe_title_name,
            recipe_create_btn,
            recipe_update_btn,
            refresh_recipe_browser,
        ],
    )

    recipe_update_btn.click(
        fn=on_recipe_update_btn_click,
        inputs=[
            selected_recipe_name,
            recipe_name,
            recipe_desc,
            recipe_prompt,
            recipe_negative,
            recipe_option,
            recipe_classification,
            recipe_image,
            reference_shortcuts,
        ],
        outputs=[
            selected_recipe_name,
            recipe_classification,
            recipe_title_name,
            refresh_recipe_browser,
        ],
    )

    recipe_delete_btn.click(
        fn=on_recipe_delete_btn_click,
        inputs=[selected_recipe_name],
        outputs=[
            selected_recipe_name,
            recipe_classification,
            recipe_title_name,
            recipe_create_btn,
            recipe_update_btn,
            refresh_recipe_browser,
        ],
    )

    reference_modelid.change(
        fn=on_reference_modelid_change,
        inputs=[
            reference_modelid,
        ],
        outputs=[
            reference_modeltype,
            reference_disp_modeltype,
            reference_versions,
            reference_filenames,
            reference_triger,
            reference_weight_slider,
            insert_prompt_btn,
            reference_model_information,
        ],
        show_progress=False,
    )

    reference_versions.select(
        fn=on_reference_versions_select,
        inputs=[
            reference_modelid,
        ],
        outputs=[
            reference_modeltype,
            reference_disp_modeltype,
            reference_versions,
            reference_filenames,
            reference_triger,
            reference_weight_slider,
            insert_prompt_btn,
            reference_model_information,
        ],
        show_progress=False,
    )

    goto_model_info_btn.click(lambda x: x, reference_modelid, shortcut_input)

    delete_reference_model_btn.click(
        fn=on_delete_reference_model_btn_click,
        inputs=[
            reference_modelid,
            reference_shortcuts,
        ],
        outputs=[
            reference_shortcuts,
            refresh_reference_gallery,
            reference_gallery,
            reference_modelid,
        ],
        show_progress=False,
    )

    insert_prompt_btn.click(
        fn=on_insert_prompt_btn_click,
        inputs=[
            reference_modeltype,
            recipe_prompt,
            recipe_negative,
            recipe_option,
            reference_filenames,
            reference_weight_slider,
            reference_triger,
        ],
        outputs=[recipe_prompt, recipe_output],
    )

    # close_reference_model_information_btn.click(lambda :gr.update(visible=False),None,reference_model_information)

    close_reference_model_information_btn.click(
        fn=on_close_reference_model_information_btn_click,
        inputs=[
            reference_shortcuts,
        ],
        outputs=[
            reference_shortcuts,
            refresh_reference_gallery,
            reference_gallery,
            reference_modelid,
        ],
        show_progress=False,
    )

    return refresh_recipe


def load_model_information(modelid=None, ver_index=None):
    if modelid:
        (
            model_info,
            version_info,
            versionid,
            version_name,
            model_type,
            model_basemodels,
            versions_list,
            dhtml,
            triger,
            files,
        ) = ishortcut.modelprocessor.get_model_information(modelid, None, ver_index)
        if model_info:
            insert_btn_visible = False
            weight_visible = False
            triger_visible = False
            if model_type == 'LORA' or model_type == 'LoCon' or model_type == 'Hypernetwork':
                insert_btn_visible = True
                weight_visible = True
                triger_visible = True
            elif model_type == 'TextualInversion':
                insert_btn_visible = True

            flist = list()
            for file in files:
                flist.append(file['name'])

            file_name = ''
            if len(flist) > 0:
                file_name = flist[0]

            title_name = f"# {model_info['name']} : {version_name}"

            return (
                gr.update(value=model_type),
                gr.update(value=setting.get_ui_typename(model_type)),
                gr.update(choices=versions_list, value=version_name),
                gr.update(choices=flist, value=file_name),
                gr.update(value=triger, visible=triger_visible),
                gr.update(visible=weight_visible),
                gr.update(visible=insert_btn_visible),
                gr.update(label=title_name, visible=True),
            )
    return (
        None,
        None,
        None,
        None,
        gr.update(value=None, visible=True),
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(label="#", visible=False),
    )


def on_reference_modelid_change(modelid=None):
    return load_model_information(modelid, None)


def on_reference_versions_select(evt: gr.SelectData, modelid: str):
    return load_model_information(modelid, evt.index)


def on_delete_reference_model_btn_click(sc_model_id: str, shortcuts):
    if sc_model_id:
        current_time = datetime.datetime.now()

        if not shortcuts:
            shortcuts = list()

        if sc_model_id in shortcuts:
            shortcuts.remove(sc_model_id)
            return shortcuts, current_time, None, None

    return shortcuts, gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)


def on_close_reference_model_information_btn_click(shortcuts):
    current_time = datetime.datetime.now()
    return shortcuts, current_time, None, None


def add_string(text, mtype, filename, weight, triger=None):
    pattern = f"<{mtype}:{filename}:{weight}>"
    if triger:
        pattern = pattern + ' ' + triger

    return text.strip() + ' ' + pattern


def remove_strings(text, mtype, filename, triger=None):
    # Use regular expression to find and remove all <lora:filename:number> strings
    pattern = f"<{mtype}:{re.escape(filename)}:.*?>"
    if triger:
        pattern = pattern + ' ' + triger
    text = re.sub(pattern, '', text)
    return text


def is_string(text, mtype, filename, triger=None):
    pattern = f"<{mtype}:{re.escape(filename)}:.*?>"
    if triger:
        pattern = pattern + ' ' + triger
    return re.search(pattern, text)


def on_insert_prompt_btn_click(
    model_type, recipe_prompt, recipe_negative, recipe_option, filename, weight, triger
):

    if model_type == 'LORA' or model_type == 'LoCon':
        mtype = 'lora'
    elif model_type == 'Hypernetwork':
        mtype = 'hypernet'
    elif model_type == 'TextualInversion':
        mtype = 'ti'

    if filename:
        filename, ext = os.path.splitext(filename)

    if mtype == 'lora' or mtype == 'hypernet':
        if is_string(recipe_prompt, mtype, filename, triger):
            recipe_prompt = remove_strings(recipe_prompt, mtype, filename, triger)
        else:
            recipe_prompt = remove_strings(recipe_prompt, mtype, filename)
            recipe_prompt = add_string(recipe_prompt, mtype, filename, weight, triger)
    elif mtype == 'ti':
        if filename in recipe_prompt:
            recipe_prompt = recipe_prompt.replace(filename, '')
        else:
            recipe_prompt = recipe_prompt.replace(filename, '')
            recipe_prompt = recipe_prompt + ' ' + filename

    return gr.update(value=recipe_prompt), gr.update(
        value=generate_prompt(recipe_prompt, recipe_negative, recipe_option)
    )


def on_recipe_prompt_tabs_select(evt: gr.SelectData):
    if evt.index == 1:
        return gr.update(selected="reference_model")
    return gr.update(selected=None)


def analyze_prompt(generate_data):
    logger.debug(f"analyze_prompt called with: {repr(generate_data)}")

    positivePrompt = None
    negativePrompt = None
    options = None
    gen_string = None

    if generate_data:
        generate = None
        try:
            logger.debug(" Calling prompt.parse_data")
            generate = prompt.parse_data(generate_data)
            logger.debug(f" prompt.parse_data returned: {generate}")
        except Exception as e:
            logger.debug(f" Exception in prompt.parse_data: {e}")

        if generate:
            if "options" in generate:
                options = [f"{k}:{v}" for k, v in generate['options'].items()]
                if options:
                    options = ", ".join(options)
                logger.debug(f" Processed options: {repr(options)}")

            if 'prompt' in generate:
                positivePrompt = generate['prompt']
                logger.debug(f" Extracted positive prompt: {repr(positivePrompt)}")

            if 'negativePrompt' in generate:
                negativePrompt = generate['negativePrompt']
                logger.debug(f" Extracted negative prompt: {repr(negativePrompt)}")
        else:
            logger.debug(" generate is None after parse_data")

        gen_string = generate_prompt(positivePrompt, negativePrompt, options)
        logger.debug(f" Generated string: {repr(gen_string)}")
    else:
        logger.debug(" generate_data is empty")

    result = (positivePrompt, negativePrompt, options, gen_string)
    logger.debug(f" analyze_prompt returning: {result}")
    return result


def generate_prompt(prompt, negativePrompt, Options):
    meta_string = None
    if prompt and len(prompt.strip()) > 0:
        meta_string = f"""{prompt.strip()}""" + "\n"

    if negativePrompt and len(negativePrompt.strip()) > 0:
        if meta_string:
            meta_string = meta_string + f"""Negative prompt:{negativePrompt.strip()}""" + "\n"
        else:
            meta_string = f"""Negative prompt:{negativePrompt.strip()}""" + "\n"

    if Options and len(Options.strip()) > 0:
        if meta_string:
            meta_string = meta_string + Options.strip()
        else:
            meta_string = Options.strip()

    return meta_string


def get_recipe_information(select_name):

    generate = None
    options = None
    classification = None
    gen_string = None
    Prompt = None
    negativePrompt = None
    description = None
    imagefile = None

    if select_name:
        rc = recipe.get_recipe(select_name)

        if "generate" in rc:
            generate = rc['generate']
            if "options" in generate:
                options = [f"{k}:{v}" for k, v in generate['options'].items()]
                if options:
                    options = ", ".join(options)

            if "prompt" in generate:
                Prompt = generate['prompt']

            if "negativePrompt" in generate:
                negativePrompt = generate['negativePrompt']

            gen_string = generate_prompt(Prompt, negativePrompt, options)

        if "image" in rc:
            if rc['image']:
                imagefile = os.path.join(setting.shortcut_recipe_folder, rc['image'])

        if "description" in rc:
            description = rc['description']

        if "classification" in rc:
            classification = rc['classification']
            if not classification or len(classification.strip()) == 0:
                classification = setting.PLACEHOLDER

    return description, Prompt, negativePrompt, options, gen_string, classification, imagefile


def on_recipe_input_change(recipe_input, shortcuts):
    logger.debug(f" on_recipe_input_change called with: {repr(recipe_input)}")

    # If recipe_input is an empty string, return immediately with no UI update (keep all states)
    if recipe_input is None or recipe_input == "":
        logger.debug(
            "[RECIPE] on_recipe_input_change received empty string, returning without changes."
        )
        return tuple(gr.update() for _ in range(22))

    current_time = datetime.datetime.now()
    param_data = None
    logger.debug(" recipe_input is not empty, processing...")
    shortcuts = None
    recipe_image = None
    positivePrompt = None
    negativePrompt = None
    options = None
    gen_string = None
    # recipe_input may include both image info and parsed parameters separated by newline
    try:
        if isinstance(recipe_input, str) and '\n' in recipe_input:
            logger.debug(" Found newline in recipe_input, splitting...")
            first_line, param_data = recipe_input.split('\n', 1)
            logger.debug(f" first_line: {repr(first_line)}")
            logger.debug(f" param_data: {repr(param_data)}")

            shortcutid, image_fn = first_line.split(':', 1)
            recipe_image = image_fn
            logger.debug(f" shortcutid: {repr(shortcutid)}, image_fn: {repr(image_fn)}")

            logger.debug(" Calling analyze_prompt with param_data...")
            positivePrompt, negativePrompt, options, gen_string = analyze_prompt(param_data)
            logger.debug(" analyze_prompt results:")
            logger.debug(f"   positivePrompt: {repr(positivePrompt)}")
            logger.debug(f"   negativePrompt: {repr(negativePrompt)}")
            logger.debug(f"   options: {repr(options)}")
            logger.debug(f"   gen_string: {repr(gen_string)}")

            shortcuts = [shortcutid]
        else:
            logger.debug(
                "[RECIPE] No newline found, using get_imagefn_and_shortcutid_from_recipe_image"
            )
            shortcutid, recipe_image = setting.get_imagefn_and_shortcutid_from_recipe_image(
                recipe_input
            )
            if shortcutid:
                shortcuts = [shortcutid]
    except Exception as e:
        logger.debug(f" Exception in recipe_input processing: {e}")

    logger.debug(" Final values before return:")
    logger.debug(f"   recipe_image: {repr(recipe_image)}")
    logger.debug(f"   positivePrompt: {repr(positivePrompt)}")
    logger.debug(f"   negativePrompt: {repr(negativePrompt)}")
    logger.debug(f"   options: {repr(options)}")
    logger.debug(f"   param_data: {repr(param_data)}")
    logger.debug(f"   shortcuts: {shortcuts}")

    return (
        gr.update(value=""),  # selected_recipe_name
        recipe_image,  # recipe_drop_image
        recipe_image,  # recipe_image
        gr.update(),  # recipe_generate_data
        gr.update(),  # recipe_input
        gr.update(selected="Recipe"),  # civitai_tabs
        gr.update(selected="Prompt"),  # recipe_prompt_tabs
        gr.update(selected="reference_image"),  # recipe_reference_tabs
        gr.update(value=positivePrompt or ""),  # recipe_prompt
        gr.update(value=negativePrompt or ""),  # recipe_negative
        gr.update(value=options or ""),  # recipe_option
        gr.update(value=param_data or ""),  # recipe_output (raw generate info)
        gr.update(value=""),  # recipe_name
        gr.update(value=""),  # recipe_desc
        gr.update(
            choices=[setting.PLACEHOLDER] + recipe.get_classifications(),
            value=setting.PLACEHOLDER,
        ),  # recipe_classification
        gr.update(label=setting.NEWRECIPE),  # recipe_title_name
        gr.update(visible=True),  # recipe_create_btn
        gr.update(visible=False),  # recipe_update_btn
        shortcuts or [],  # reference_shortcuts
        gr.update(),  # reference_modelid
        [],  # reference_gallery
        current_time,  # refresh_reference_gallery
    )


def on_recipe_drop_image_upload(recipe_img):
    if recipe_img:
        current_time = datetime.datetime.now()
        return recipe_img, current_time
    return gr.update(visible=True), gr.update(visible=False)


def on_recipe_generate_data_change(recipe_img):
    """Process recipe PNG info with compatibility layer support"""
    generate_data = None
    if recipe_img:
        compat = CompatibilityLayer.get_compatibility_layer()

        if compat and hasattr(compat, 'metadata_processor'):
            try:
                # extract_png_info returns (geninfo, generation_params, info_text)
                # We need the first element (geninfo) which contains the parameters string
                result = compat.metadata_processor.extract_png_info(recipe_img)
                if result and result[0]:
                    generate_data = result[0]
                    data_len = len(generate_data) if generate_data else 0
                    logger.debug(f" Extracted via compatibility layer: {data_len} chars")
            except Exception as e:
                logger.debug(f"Error processing PNG info through compatibility layer: {e}")

        # Fallback: Try WebUI direct access
        if not generate_data:
            extras_module = import_manager.get_webui_module('extras')
            if extras_module and hasattr(extras_module, 'run_pnginfo'):
                try:
                    info1, generate_data_dict, info3 = extras_module.run_pnginfo(recipe_img)
                    # WebUI run_pnginfo returns info1 as the parameters string
                    generate_data = info1
                    data_len = len(generate_data) if generate_data else 0
                    logger.debug(f" Extracted parameters via WebUI: {data_len} chars")
                except Exception as e:
                    logger.debug(f"Error processing PNG info through WebUI: {e}")

        # Final fallback: Try basic PIL extraction
        if not generate_data:
            try:
                import io

                if isinstance(recipe_img, str):
                    with Image.open(recipe_img) as img:
                        generate_data = img.text.get('parameters', '')
                elif hasattr(recipe_img, 'read'):
                    with Image.open(io.BytesIO(recipe_img.read())) as img:
                        generate_data = img.text.get('parameters', '')

                if generate_data:
                    logger.debug(f" Extracted via PIL fallback: {len(generate_data)} chars")
            except Exception as e:
                logger.debug(f"Error in PNG info fallback processing: {e}")

    if generate_data:
        positivePrompt, negativePrompt, options, gen_string = analyze_prompt(generate_data)
        return (
            gr.update(value=positivePrompt),
            gr.update(value=negativePrompt),
            gr.update(value=options),
            gr.update(value=gen_string),
        )
    return (gr.update(value=""), gr.update(value=""), gr.update(value=""), gr.update(value=""))


def on_refresh_recipe_change():
    current_time = datetime.datetime.now()
    return current_time, current_time, current_time


def on_recipe_gallery_select(evt: gr.SelectData):
    current_time = datetime.datetime.now()

    # Handle evt.value which can be either a string or a list [image_url, shortcut_name]
    if isinstance(evt.value, list) and len(evt.value) > 1:
        select_name = evt.value[1]  # Use the shortcut name (second element)
    elif isinstance(evt.value, str):
        select_name = evt.value
    else:
        logger.debug(
            f"[RECIPE] Unexpected evt.value format in on_recipe_gallery_select: " f"{evt.value}"
        )
        return ("", "", "", "", "", "", None, [])

    description, Prompt, negativePrompt, options, gen_string, classification, imagefile = (
        get_recipe_information(select_name)
    )

    if imagefile:
        if not os.path.isfile(imagefile):
            imagefile = None

    shortcuts = recipe.get_recipe_shortcuts(select_name)

    return (
        gr.update(value=select_name),
        gr.update(value=select_name),
        gr.update(value=description),
        gr.update(value=Prompt),
        gr.update(value=negativePrompt),
        gr.update(value=options),
        gr.update(value=gen_string),
        gr.update(
            choices=[setting.PLACEHOLDER] + recipe.get_classifications(), value=classification
        ),
        gr.update(label=select_name),
        imagefile,
        None,
        gr.update(visible=False),
        gr.update(visible=True),
        shortcuts,
        None,
        None,
        current_time,
    )


def on_recipe_new_btn_click():
    current_time = datetime.datetime.now()
    return (
        gr.update(value=""),
        gr.update(value=""),
        gr.update(value=""),
        gr.update(value=""),
        gr.update(value=""),
        gr.update(value=""),
        gr.update(value=""),
        gr.update(
            choices=[setting.PLACEHOLDER] + recipe.get_classifications(), value=setting.PLACEHOLDER
        ),
        gr.update(label=setting.NEWRECIPE),
        None,
        None,
        gr.update(visible=True),
        gr.update(visible=False),
        None,
        None,
        current_time,
    )


@with_error_handling(
    fallback_value=(
        gr.update(value=""),
        gr.update(choices=[]),
        datetime.datetime.now(),
        gr.update(label=setting.NEWRECIPE),
        gr.update(visible=True),
        gr.update(visible=False),
    ),
    exception_types=(FileOperationError, ValidationError),
    retry_count=1,
    user_message="Failed to create recipe",
)
def on_recipe_create_btn_click(
    recipe_name,
    recipe_desc,
    recipe_prompt,
    recipe_negative,
    recipe_option,
    recipe_classification,
    recipe_image=None,
    recipe_shortcuts=None,
):
    """
    Handle recipe creation button click with name validation.

    Shows warning message if recipe name is empty, whitespace-only,
    or set to default value.

    Args:
        recipe_name (str): The name of the recipe to create
        recipe_desc (str): Description of the recipe
        recipe_prompt (str): Prompt text for generation
        recipe_negative (str): Negative prompt text
        recipe_option (str): Additional prompt options string
        recipe_classification (str): Classification/category for the recipe
        recipe_image (PIL.Image, optional): Preview image for the recipe
        recipe_shortcuts (list, optional): Shortcuts associated with the recipe

    Returns:
        tuple: UI update values for recipe creation state

    Raises:
        gr.Warning: When recipe name validation fails
    """
    current_time = datetime.datetime.now()
    s_classification = setting.PLACEHOLDER
    # Validate recipe name before creating
    if not recipe_name or not recipe_name.strip() or recipe_name == setting.NEWRECIPE:
        gr.Warning("Please enter a recipe name before creating.")
        return (
            gr.update(value=""),
            gr.update(
                choices=[setting.PLACEHOLDER] + recipe.get_classifications(), value=s_classification
            ),
            gr.update(label=setting.NEWRECIPE),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
        )
    if recipe_name and len(recipe_name.strip()) > 0 and recipe_name != setting.NEWRECIPE:
        pmt = dict()
        pmt['prompt'] = recipe_prompt
        pmt['negativePrompt'] = recipe_negative

        options = prompt.parse_option_data(recipe_option)
        if options:
            pmt['options'] = options

        if recipe_classification:
            if recipe_classification == setting.PLACEHOLDER:
                recipe_classification = ""
                recipe_classification = recipe_classification.strip()
            else:
                recipe_classification = recipe_classification.strip()
                s_classification = recipe_classification

        if recipe.create_recipe(recipe_name, recipe_desc, pmt, recipe_classification):
            if recipe_image:
                if not os.path.exists(setting.shortcut_recipe_folder):
                    os.makedirs(setting.shortcut_recipe_folder)
                unique_filename = f"{str(uuid.uuid4())}{setting.preview_image_ext}"
                recipe_imgfile = os.path.join(setting.shortcut_recipe_folder, unique_filename)
                recipe_image.save(recipe_imgfile)
                recipe.update_recipe_image(recipe_name, unique_filename)
                recipe.update_recipe_shortcuts(recipe_name, recipe_shortcuts)

            return (
                gr.update(value=recipe_name),
                gr.update(
                    choices=[setting.PLACEHOLDER] + recipe.get_classifications(),
                    value=s_classification,
                ),
                gr.update(label=recipe_name),
                gr.update(visible=False),
                gr.update(visible=True),
                current_time,
            )
    return (
        gr.update(value=""),
        gr.update(
            choices=[setting.PLACEHOLDER] + recipe.get_classifications(), value=s_classification
        ),
        gr.update(label=setting.NEWRECIPE),
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
    )


@with_error_handling(
    fallback_value=(
        gr.update(value=""),
        gr.update(choices=[]),
        datetime.datetime.now(),
        gr.update(label=""),
    ),
    exception_types=(FileOperationError, ValidationError),
    retry_count=1,
    user_message="Failed to update recipe",
)
def on_recipe_update_btn_click(
    select_name,
    recipe_name,
    recipe_desc,
    recipe_prompt,
    recipe_negative,
    recipe_option,
    recipe_classification,
    recipe_image=None,
    recipe_shortcuts=None,
):

    chg_name = setting.NEWRECIPE
    s_classification = setting.PLACEHOLDER

    if (
        select_name
        and select_name != setting.NEWRECIPE
        and recipe_name
        and recipe_name != setting.NEWRECIPE
    ):

        pmt = dict()
        pmt['prompt'] = recipe_prompt
        pmt['negativePrompt'] = recipe_negative

        options = prompt.parse_option_data(recipe_option)
        if options:
            pmt['options'] = options

        if recipe_classification:
            if recipe_classification == setting.PLACEHOLDER:
                recipe_classification = ""
                recipe_classification = recipe_classification.strip()
            else:
                recipe_classification = recipe_classification.strip()
                s_classification = recipe_classification

        if recipe.update_recipe(select_name, recipe_name, recipe_desc, pmt, recipe_classification):
            chg_name = recipe_name
            if recipe_image:
                if not os.path.exists(setting.shortcut_recipe_folder):
                    os.makedirs(setting.shortcut_recipe_folder)
                unique_filename = f"{str(uuid.uuid4())}{setting.preview_image_ext}"
                recipe_imgfile = os.path.join(setting.shortcut_recipe_folder, unique_filename)
                recipe_image.save(recipe_imgfile)
                recipe.update_recipe_image(recipe_name, unique_filename)
            else:
                recipe.update_recipe_image(recipe_name, None)

            recipe.update_recipe_shortcuts(recipe_name, recipe_shortcuts)

    current_time = datetime.datetime.now()
    return (
        gr.update(value=chg_name),
        gr.update(
            choices=[setting.PLACEHOLDER] + recipe.get_classifications(), value=s_classification
        ),
        gr.update(label=chg_name),
        current_time,
    )


@with_error_handling(
    fallback_value=(
        gr.update(value=""),
        gr.update(choices=[]),
        datetime.datetime.now(),
        gr.update(label=setting.NEWRECIPE),
        gr.update(visible=True),
        gr.update(visible=False),
    ),
    exception_types=(FileOperationError,),
    retry_count=1,
    user_message="Failed to delete recipe",
)
def on_recipe_delete_btn_click(select_name):
    if select_name:
        recipe.delete_recipe(select_name)

    current_time = datetime.datetime.now()
    return (
        gr.update(value=""),
        gr.update(
            choices=[setting.PLACEHOLDER] + recipe.get_classifications(), value=setting.PLACEHOLDER
        ),
        gr.update(label=setting.NEWRECIPE),
        gr.update(visible=True),
        gr.update(visible=False),
        current_time,
    )


# reference shortcuts
@with_error_handling(
    fallback_value=gr.update(value=None),
    exception_types=(FileOperationError, NetworkError),
    user_message="Failed to load reference gallery",
)
def on_reference_gallery_loading(shortcuts):
    ISC = ishortcut.shortcutcollectionmanager.load_shortcuts()
    if not ISC:
        return None

    result_list = None

    if shortcuts:
        result_list = list()
        for mid in shortcuts:
            if str(mid) in ISC.keys():
                v = ISC[str(mid)]
                if ishortcut.imageprocessor.is_sc_image(v['id']):
                    if 'nsfw' in v.keys() and bool(v['nsfw']) and setting.NSFW_filtering_enable:
                        result_list.append(
                            (
                                setting.nsfw_disable_image,
                                setting.set_shortcutname(v['name'], v['id']),
                            )
                        )
                    else:
                        result_list.append(
                            (
                                os.path.join(
                                    setting.shortcut_thumbnail_folder,
                                    f"{v['id']}{setting.preview_image_ext}",
                                ),
                                setting.set_shortcutname(v['name'], v['id']),
                            )
                        )
                else:
                    result_list.append(
                        (
                            setting.no_card_preview_image,
                            setting.set_shortcutname(v['name'], v['id']),
                        )
                    )
            else:
                result_list.append(
                    (setting.no_card_preview_image, setting.set_shortcutname("delete", mid))
                )

    return gr.update(value=result_list)


@with_error_handling(
    fallback_value=(None, datetime.datetime.now(), None, None),
    exception_types=(ValidationError,),
    user_message="Failed to process reference selection",
)
def on_reference_sc_gallery_select(evt: gr.SelectData, shortcuts):
    current_time = datetime.datetime.now()

    if evt.value:
        # evt.value can be Gradio v4+ FileData dict,
        # v3.41+ list [image_url, shortcut_name], or legacy string
        if isinstance(evt.value, dict) and 'caption' in evt.value:
            shortcut = evt.value['caption']
        elif isinstance(evt.value, list) and len(evt.value) > 1:
            shortcut = evt.value[1]
        elif isinstance(evt.value, str):
            shortcut = evt.value
        else:
            logger.debug(f" Unexpected evt.value format: {evt.value}")
            return shortcuts, current_time

        sc_model_id = setting.get_modelid_from_shortcutname(shortcut)

        if not shortcuts:
            shortcuts = list()

        if sc_model_id not in shortcuts:
            shortcuts.append(sc_model_id)

        return shortcuts, current_time
    return shortcuts, gr.update(visible=False)


def on_reference_gallery_select(evt: gr.SelectData, shortcuts, delete_opt=True):
    if evt.value:
        # evt.value can be Gradio v4+ FileData dict,
        # v3.41+ list [image_url, shortcut_name], or legacy string
        if isinstance(evt.value, dict) and 'caption' in evt.value:
            shortcut = evt.value['caption']
        elif isinstance(evt.value, list) and len(evt.value) > 1:
            shortcut = evt.value[1]
        elif isinstance(evt.value, str):
            shortcut = evt.value
        else:
            logger.debug(f" Unexpected evt.value format: {evt.value}")
            return shortcuts, gr.update(visible=False), gr.update(visible=True), None

        sc_model_id = setting.get_modelid_from_shortcutname(shortcut)
        current_time = datetime.datetime.now()

        if not shortcuts:
            shortcuts = list()

        if delete_opt and sc_model_id in shortcuts:
            shortcuts.remove(sc_model_id)
            return shortcuts, current_time, None, None

        return shortcuts, gr.update(visible=False), gr.update(visible=True), sc_model_id

    return shortcuts, gr.update(visible=False), gr.update(visible=True), None
