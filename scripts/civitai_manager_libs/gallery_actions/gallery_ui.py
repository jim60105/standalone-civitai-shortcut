"""
Gallery UI Components and Event Handlers.

This module contains the main UI creation and gallery interaction handlers.
"""

import gradio as gr
from typing import Any, List

from ..conditional_imports import import_manager
from ..logging_config import get_logger
from .. import setting
from ..error_handler import with_error_handling

logger = get_logger(__name__)


def on_ui(recipe_input):
    """Create the main gallery UI components."""
    with gr.Column(scale=3):
        with gr.Accordion("#", open=True) as model_title_name:
            versions_list = gr.Dropdown(
                label="Model Version",
                choices=[setting.PLACEHOLDER],
                interactive=True,
                value=setting.PLACEHOLDER,
            )
        usergal_gallery = gr.Gallery(
            show_label=False,
            columns=setting.usergallery_images_column,
            height=setting.information_gallery_height,
            object_fit=setting.gallery_thumbnail_image_style,
        )
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Row():
                    first_btn = gr.Button(value="First Page")
                    prev_btn = gr.Button(value="Prev Page")
            with gr.Column(scale=1):
                page_slider = gr.Slider(
                    minimum=1, maximum=1, value=1, step=1, label='Total Pages', interactive=True
                )
            with gr.Column(scale=1):
                with gr.Row():
                    next_btn = gr.Button(value="Next Page")
                    end_btn = gr.Button(value="End Page")
        with gr.Row():
            download_images = gr.Button(value="Download Images")
            open_image_folder = gr.Button(value="Open Download Image Folder", visible=False)

    with gr.Column(scale=1):
        with gr.Tabs() as info_tabs:
            with gr.TabItem("Image Information", id="Image_Information"):
                with gr.Column():
                    img_file_info = gr.Textbox(
                        label="Generate Info",
                        interactive=True,
                        lines=6,
                        container=True,
                        show_copy_button=True,
                    )
                    try:
                        parameters_copypaste = import_manager.get_webui_module(
                            'extras', 'parameters_copypaste'
                        )
                        if parameters_copypaste:
                            send_to_buttons = parameters_copypaste.create_buttons(
                                ["txt2img", "img2img", "inpaint", "extras"]
                            )
                    except Exception:
                        pass
                    send_to_recipe = gr.Button(
                        value="Send To Recipe", variant="primary", visible=True
                    )

    with gr.Row(visible=False):
        selected_model_id = gr.Textbox()
        img_index = gr.Number(show_label=False)
        usergal_images = gr.State()
        usergal_images_url = gr.State()
        hidden = gr.Image(type="pil")
        paging_information = gr.State()
        usergal_page_url = gr.Textbox(value=None)
        refresh_information = gr.Textbox()
        refresh_gallery = gr.Textbox()
        pre_loading = gr.Textbox()

    # Set up event handlers (these will be moved to separate modules)
    _setup_event_handlers(
        usergal_gallery,
        hidden,
        info_tabs,
        img_file_info,
        selected_model_id,
        img_index,
        usergal_images,
        usergal_images_url,
        paging_information,
        usergal_page_url,
        refresh_information,
        refresh_gallery,
        pre_loading,
        recipe_input,
        open_image_folder,
        download_images,
        model_title_name,
        versions_list,
        page_slider,
        first_btn,
        prev_btn,
        next_btn,
        end_btn,
        send_to_recipe,
    )

    try:
        parameters_copypaste = import_manager.get_webui_module('extras', 'parameters_copypaste')
        if parameters_copypaste and 'send_to_buttons' in locals():
            parameters_copypaste.bind_buttons(send_to_buttons, hidden, img_file_info)
    except Exception:
        pass

    return selected_model_id, refresh_information


def _setup_event_handlers(
    usergal_gallery,
    hidden,
    info_tabs,
    img_file_info,
    selected_model_id,
    img_index,
    usergal_images,
    usergal_images_url,
    paging_information,
    usergal_page_url,
    refresh_information,
    refresh_gallery,
    pre_loading,
    recipe_input,
    open_image_folder,
    download_images,
    model_title_name,
    versions_list,
    page_slider,
    first_btn,
    prev_btn,
    next_btn,
    end_btn,
    send_to_recipe,
):
    """Setup all event handlers for gallery UI components."""
    # Import handlers from other modules to avoid circular imports
    from .navigation_handlers import (
        on_page_slider_release,
        on_first_btn_click,
        on_end_btn_click,
        on_next_btn_click,
        on_prev_btn_click,
    )
    from .model_handlers import on_selected_model_id_change, on_versions_list_select
    from .page_handlers import on_usergal_page_url_change, on_refresh_gallery_change
    from .file_handlers import on_open_image_folder_click, on_download_images_click

    usergal_gallery.select(
        on_gallery_select, usergal_images, [img_index, hidden, info_tabs, img_file_info]
    )

    open_image_folder.click(on_open_image_folder_click, [selected_model_id], None)

    send_to_recipe.click(
        fn=on_send_to_recipe_click,
        inputs=[selected_model_id, img_file_info, img_index, usergal_images],
        outputs=[recipe_input],
    )

    download_images.click(
        fn=on_download_images_click,
        inputs=[usergal_page_url, usergal_images_url],
        outputs=[open_image_folder],
    )

    gallery = refresh_gallery.change(
        fn=on_refresh_gallery_change,
        inputs=[usergal_images_url],
        outputs=[usergal_gallery, usergal_images, pre_loading],
    )

    gallery_page = usergal_page_url.change(
        fn=on_usergal_page_url_change,
        inputs=[usergal_page_url, paging_information],
        outputs=[refresh_gallery, usergal_images_url, page_slider, img_file_info],
        cancels=gallery,
    )

    refresh_information.change(
        fn=on_usergal_page_url_change,
        inputs=[usergal_page_url, paging_information],
        outputs=[refresh_gallery, usergal_images_url, page_slider, img_file_info],
        cancels=gallery,
    )

    selected_model_id.change(
        fn=on_selected_model_id_change,
        inputs=[selected_model_id],
        outputs=[
            model_title_name,
            usergal_page_url,
            versions_list,
            page_slider,
            paging_information,
            open_image_folder,
        ],
        cancels=[gallery, gallery_page],
    )

    versions_list.select(
        fn=on_versions_list_select,
        inputs=[selected_model_id],
        outputs=[
            model_title_name,
            usergal_page_url,
            versions_list,
            page_slider,
            paging_information,
        ],
        cancels=[gallery, gallery_page],
    )

    first_btn.click(
        fn=on_first_btn_click,
        inputs=[usergal_page_url, paging_information],
        outputs=[usergal_page_url],
    )

    end_btn.click(
        fn=on_end_btn_click,
        inputs=[usergal_page_url, paging_information],
        outputs=[usergal_page_url],
    )

    prev_btn.click(
        fn=on_prev_btn_click,
        inputs=[usergal_page_url, paging_information],
        outputs=[usergal_page_url],
    )

    next_btn.click(
        fn=on_next_btn_click,
        inputs=[usergal_page_url, paging_information],
        outputs=[usergal_page_url],
    )

    page_slider.release(
        fn=on_page_slider_release,
        inputs=[usergal_page_url, page_slider, paging_information],
        outputs=[usergal_page_url],
    )


@with_error_handling()
def on_send_to_recipe_click(
    model_id: str, img_file_info: str, img_index: int, civitai_images: List[str]
) -> str:
    """Handle send to recipe button click."""
    logger.debug("on_send_to_recipe_click called")
    logger.debug(f"  model_id: {repr(model_id)}")
    logger.debug(f"  img_file_info: {repr(img_file_info)}")
    logger.debug(f"  img_index: {repr(img_index)}")
    logger.debug(f"  civitai_images: {repr(civitai_images)}")

    try:
        recipe_image = setting.set_imagefn_and_shortcutid_for_recipe_image(
            model_id, civitai_images[int(img_index)]
        )
        logger.debug(f"  recipe_image: {repr(recipe_image)}")

        if img_file_info:
            result = f"{recipe_image}\n{img_file_info}"
            logger.debug(f"Returning combined data: {repr(result)}")
            return result
        else:
            logger.debug(f"No img_file_info, returning recipe_image only: {repr(recipe_image)}")
            return recipe_image
    except Exception as e:
        logger.error(f"Exception in on_send_to_recipe_click: {e}")
        return gr.update(visible=False)


@with_error_handling()
def on_gallery_select(evt: gr.SelectData, civitai_images: List[str]) -> tuple:
    """Handle gallery selection."""
    from ..compat.compat_layer import CompatibilityLayer

    logger.debug(f"Gallery selection event: index={evt.index}")

    try:
        compat_layer = CompatibilityLayer.get_compatibility_layer()
        metadata_processor = compat_layer.metadata_processor

        if not civitai_images or evt.index >= len(civitai_images):
            logger.warning("Invalid gallery selection index")
            return evt.index, None, gr.update(selected="Image_Information"), ""

        image_path = civitai_images[evt.index]
        logger.debug(f"Selected image path: {image_path}")

        png_info = metadata_processor.extract_png_info(image_path)
        if png_info:
            parameters = metadata_processor.extract_parameters_from_png(image_path)
            formatted_info = metadata_processor.format_parameters_for_display(parameters)
            logger.debug(f"Extracted PNG info: {formatted_info[:100]}...")
            return evt.index, image_path, gr.update(selected="Image_Information"), formatted_info
        else:
            logger.debug("No PNG info found in image")
            return evt.index, image_path, gr.update(selected="Image_Information"), ""

    except Exception as e:
        logger.error(f"Error in gallery selection: {e}")
        return evt.index, None, gr.update(selected="Image_Information"), ""


@with_error_handling()
def on_civitai_hidden_change(hidden: Any, index: int) -> str:
    """Handle hidden state change for Civitai images."""
    from ..compat.compat_layer import CompatibilityLayer

    try:
        compat_layer = CompatibilityLayer.get_compatibility_layer()
        metadata_processor = compat_layer.metadata_processor

        if hidden is None:
            return ""

        logger.debug(f"Processing hidden change for index: {index}")

        if hasattr(hidden, 'filename'):
            image_path = hidden.filename
        else:
            image_path = str(hidden)

        parameters = metadata_processor.extract_parameters_from_png(image_path)
        formatted_info = metadata_processor.format_parameters_for_display(parameters)

        logger.debug(f"Extracted parameters: {formatted_info[:100]}...")
        return formatted_info

    except Exception as e:
        logger.error(f"Error processing hidden change: {e}")
        return ""
