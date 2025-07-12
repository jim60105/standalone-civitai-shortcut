"""
UI Components Module

Handles UI component creation, layout management, and Gradio interface building.
Extracted from civitai_gallery_action.py to follow SRP principles.
"""

from typing import Tuple

import gradio as gr

from ..conditional_imports import import_manager
from ..logging_config import get_logger
from .. import settings

logger = get_logger(__name__)


class GalleryUIComponents:
    """Gallery UI components manager following SRP principle."""

    def __init__(self):
        self.components = {}

    def create_main_ui(self, recipe_input) -> Tuple[gr.Textbox, gr.Textbox]:
        """Create main gallery UI components."""
        logger.debug("Creating main gallery UI")

        # Event handlers will be imported in _bind_event_handlers method

        # Create main gallery layout
        with gr.Column(scale=3):
            with gr.Accordion("#", open=True) as model_title_name:
                versions_list = gr.Dropdown(
                    label="Model Version",
                    choices=[settings.PLACEHOLDER],
                    interactive=True,
                    value=settings.PLACEHOLDER,
                )
            usergal_gallery = gr.Gallery(
                show_label=False,
                columns=settings.usergallery_images_column,
                height=settings.information_gallery_height,
                object_fit=settings.gallery_thumbnail_image_style,
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
                open_image_folder = gr.Button(
                    value="Open Download Image Folder",
                    visible=False,  # initial, controlled by dynamic logic
                )

        # Create info panel
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

        # Create hidden state components
        with gr.Row(visible=False):
            selected_model_id = gr.Textbox()

            # user gallery information
            img_index = gr.Number(show_label=False)

            # actually loaded images
            usergal_images = gr.State()

            # images to be loaded
            usergal_images_url = gr.State()

            # trigger component
            hidden = gr.Image(type="pil")

            # paging related information
            paging_information = gr.State()

            usergal_page_url = gr.Textbox(value=None)

            refresh_information = gr.Textbox()

            refresh_gallery = gr.Textbox()

            # preload next page
            pre_loading = gr.Textbox()

        # Bind WebUI copy-paste integration if available
        try:
            parameters_copypaste = import_manager.get_webui_module('extras', 'parameters_copypaste')
            if parameters_copypaste and 'send_to_buttons' in locals():
                parameters_copypaste.bind_buttons(send_to_buttons, hidden, img_file_info)
        except Exception:
            pass

        # Bind event handlers
        self._bind_event_handlers(
            usergal_gallery,
            open_image_folder,
            send_to_recipe,
            download_images,
            refresh_gallery,
            usergal_page_url,
            refresh_information,
            selected_model_id,
            versions_list,
            pre_loading,
            first_btn,
            end_btn,
            prev_btn,
            next_btn,
            page_slider,
            recipe_input,
            img_index,
            hidden,
            info_tabs,
            img_file_info,
            usergal_images,
            usergal_images_url,
            paging_information,
            model_title_name,
        )

        return selected_model_id, refresh_information

    def _bind_event_handlers(
        self,
        usergal_gallery,
        open_image_folder,
        send_to_recipe,
        download_images,
        refresh_gallery,
        usergal_page_url,
        refresh_information,
        selected_model_id,
        versions_list,
        pre_loading,
        first_btn,
        end_btn,
        prev_btn,
        next_btn,
        page_slider,
        recipe_input,
        img_index,
        hidden,
        info_tabs,
        img_file_info,
        usergal_images,
        usergal_images_url,
        paging_information,
        model_title_name,
    ):
        """Bind all event handlers to UI components."""
        # Import event handlers
        from . import (
            on_gallery_select,
            on_open_image_folder_click,
            on_send_to_recipe_click,
            on_download_images_click,
            on_refresh_gallery_change,
            on_usergal_page_url_change,
            on_selected_model_id_change,
            on_versions_list_select,
            on_pre_loading_change,
            on_first_btn_click,
            on_end_btn_click,
            on_prev_btn_click,
            on_next_btn_click,
            on_page_slider_release,
        )

        # Gallery selection - Use legacy syntax for compatibility
        usergal_gallery.select(
            on_gallery_select, usergal_images, [img_index, hidden, info_tabs, img_file_info]
        )

        # Button clicks
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

        # Gallery refresh and loading
        gallery = refresh_gallery.change(
            fn=on_refresh_gallery_change,
            inputs=[usergal_images_url],
            outputs=[usergal_gallery, usergal_images, pre_loading],
        )

        gallery_page = usergal_page_url.change(
            fn=on_usergal_page_url_change,
            inputs=[usergal_page_url, paging_information],
            outputs=[
                refresh_gallery,
                usergal_images_url,
                page_slider,
                img_file_info,
            ],
            cancels=gallery,
        )

        refresh_information.change(
            fn=on_usergal_page_url_change,
            inputs=[usergal_page_url, paging_information],
            outputs=[
                refresh_gallery,
                usergal_images_url,
                page_slider,
                img_file_info,
            ],
            cancels=gallery,
        )

        # Model and version selection
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

        # Pre-loading
        pre_loading.change(
            fn=on_pre_loading_change, inputs=[usergal_page_url, paging_information], outputs=None
        )

        # Navigation buttons
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
