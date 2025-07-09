"""
Event wiring for recipe UI components.
"""

import gradio as gr
from ..logging_config import get_logger

logger = get_logger(__name__)


class RecipeEventWiring:
    """Handles all Gradio event bindings for recipe UI components."""

    def __init__(self):
        self._logger = logger
        # Import action handlers
        from .recipe_management import RecipeManager
        from .recipe_gallery import RecipeGallery
        from .recipe_reference import RecipeReferenceManager
        from .recipe_utilities import RecipeUtilities

        self.recipe_manager = RecipeManager()
        self.recipe_gallery = RecipeGallery()
        self.recipe_reference = RecipeReferenceManager()
        self.recipe_utilities = RecipeUtilities()

    def wire_all_events(self, components, recipe_input, shortcut_input, civitai_tabs):
        """Wire all recipe UI events to their respective handlers."""
        self._logger.debug("Wiring all recipe UI events...")

        # Basic tab selection
        components['recipe_prompt_tabs'].select(
            fn=self._on_recipe_prompt_tabs_select,
            inputs=None,
            outputs=[components['recipe_reference_tabs']],
        )

        # Reference shortcuts management
        components['reference_gallery'].select(
            fn=self.recipe_reference.on_reference_gallery_select,
            inputs=[components['reference_shortcuts'], components['reference_delete']],
            outputs=[
                components['reference_shortcuts'],
                components['refresh_reference_gallery'],
                components['reference_gallery'],
                components['reference_modelid'],
            ],
            show_progress=False,
        )

        components['refresh_reference_gallery'].change(
            fn=self.recipe_reference.on_reference_gallery_loading,
            inputs=[components['reference_shortcuts']],
            outputs=[components['reference_gallery']],
            show_progress=False,
        )

        components['reference_sc_gallery'].select(
            fn=self.recipe_reference.on_reference_sc_gallery_select,
            inputs=[components['reference_shortcuts']],
            outputs=[
                components['reference_shortcuts'],
                components['refresh_reference_gallery'],
            ],
            show_progress=False,
        )

        # Prompt generation on blur
        components['recipe_prompt'].blur(
            fn=self.recipe_utilities.generate_prompt,
            inputs=[
                components['recipe_prompt'],
                components['recipe_negative'],
                components['recipe_option'],
            ],
            outputs=[components['recipe_output']],
        )
        components['recipe_negative'].blur(
            fn=self.recipe_utilities.generate_prompt,
            inputs=[
                components['recipe_prompt'],
                components['recipe_negative'],
                components['recipe_option'],
            ],
            outputs=[components['recipe_output']],
        )
        components['recipe_option'].blur(
            fn=self.recipe_utilities.generate_prompt,
            inputs=[
                components['recipe_prompt'],
                components['recipe_negative'],
                components['recipe_option'],
            ],
            outputs=[components['recipe_output']],
        )

        # Image handling
        recipe_drop_image_upload = components['recipe_drop_image'].upload(
            fn=self.recipe_gallery.on_recipe_drop_image_upload,
            inputs=[components['recipe_drop_image']],
            outputs=[components['recipe_image'], components['recipe_generate_data']],
            show_progress=False,
        )

        recipe_generate_data_change = components['recipe_generate_data'].change(
            fn=self.recipe_gallery.on_recipe_generate_data_change,
            inputs=[components['recipe_drop_image']],
            outputs=[
                components['recipe_prompt'],
                components['recipe_negative'],
                components['recipe_option'],
                components['recipe_output'],
            ],
        )

        # Recipe input change (from shortcut information)
        recipe_input.change(
            fn=self._on_recipe_input_change,
            inputs=[recipe_input, components['reference_shortcuts']],
            outputs=[
                components['selected_recipe_name'],
                components['recipe_drop_image'],
                components['recipe_image'],
                components['recipe_generate_data'],
                recipe_input,
                civitai_tabs,
                components['recipe_prompt_tabs'],
                components['recipe_reference_tabs'],
                components['recipe_prompt'],
                components['recipe_negative'],
                components['recipe_option'],
                components['recipe_output'],
                components['recipe_name'],
                components['recipe_desc'],
                components['recipe_classification'],
                components['recipe_title_name'],
                components['recipe_create_btn'],
                components['recipe_update_btn'],
                components['reference_shortcuts'],
                components['reference_modelid'],
                components['reference_gallery'],
                components['refresh_reference_gallery'],
            ],
            cancels=[recipe_drop_image_upload, recipe_generate_data_change],
        )

        # Refresh recipe
        components['refresh_recipe'].change(
            fn=self._on_refresh_recipe_change,
            inputs=None,
            outputs=[
                components['refresh_reference_sc_browser'],
                components['refresh_recipe_browser'],
                components['refresh_reference_gallery'],
            ],
            show_progress=False,
        )

        # Recipe gallery selection
        components['recipe_gallery'].select(
            fn=self.recipe_gallery.on_recipe_gallery_select,
            inputs=None,
            outputs=[
                components['selected_recipe_name'],
                components['recipe_name'],
                components['recipe_desc'],
                components['recipe_prompt'],
                components['recipe_negative'],
                components['recipe_option'],
                components['recipe_output'],
                components['recipe_classification'],
                components['recipe_title_name'],
                components['recipe_image'],
                components['recipe_drop_image'],
                components['recipe_create_btn'],
                components['recipe_update_btn'],
                components['reference_shortcuts'],
                components['reference_modelid'],
                components['refresh_reference_gallery'],
            ],
            cancels=[recipe_drop_image_upload],
        )

        # Recipe management buttons
        components['recipe_new_btn'].click(
            fn=self.recipe_manager.on_recipe_new_btn_click,
            inputs=None,
            outputs=[
                components['selected_recipe_name'],
                components['recipe_name'],
                components['recipe_desc'],
                components['recipe_prompt'],
                components['recipe_negative'],
                components['recipe_option'],
                components['recipe_output'],
                components['recipe_classification'],
                components['recipe_title_name'],
                components['recipe_image'],
                components['recipe_drop_image'],
                components['recipe_create_btn'],
                components['recipe_update_btn'],
                components['reference_shortcuts'],
                components['reference_modelid'],
                components['refresh_reference_gallery'],
            ],
        )

        components['recipe_create_btn'].click(
            fn=self.recipe_manager.on_recipe_create_btn_click,
            inputs=[
                components['recipe_name'],
                components['recipe_desc'],
                components['recipe_prompt'],
                components['recipe_negative'],
                components['recipe_option'],
                components['recipe_classification'],
                components['recipe_image'],
                components['reference_shortcuts'],
            ],
            outputs=[
                components['selected_recipe_name'],
                components['recipe_classification'],
                components['recipe_title_name'],
                components['recipe_create_btn'],
                components['recipe_update_btn'],
                components['refresh_recipe_browser'],
            ],
        )

        components['recipe_update_btn'].click(
            fn=self.recipe_manager.on_recipe_update_btn_click,
            inputs=[
                components['selected_recipe_name'],
                components['recipe_name'],
                components['recipe_desc'],
                components['recipe_prompt'],
                components['recipe_negative'],
                components['recipe_option'],
                components['recipe_classification'],
                components['recipe_image'],
                components['reference_shortcuts'],
            ],
            outputs=[
                components['selected_recipe_name'],
                components['recipe_classification'],
                components['recipe_title_name'],
                components['refresh_recipe_browser'],
            ],
        )

        components['recipe_delete_btn'].click(
            fn=self.recipe_manager.on_recipe_delete_btn_click,
            inputs=[components['selected_recipe_name']],
            outputs=[
                components['selected_recipe_name'],
                components['recipe_classification'],
                components['recipe_title_name'],
                components['recipe_create_btn'],
                components['recipe_update_btn'],
                components['refresh_recipe_browser'],
            ],
        )

        # Reference model management
        components['reference_modelid'].change(
            fn=self.recipe_reference.on_reference_modelid_change,
            inputs=[components['reference_modelid']],
            outputs=[
                components['reference_modeltype'],
                components['reference_disp_modeltype'],
                components['reference_versions'],
                components['reference_filenames'],
                components['reference_triger'],
                components['reference_weight_slider'],
                components['insert_prompt_btn'],
                components['reference_model_information'],
            ],
            show_progress=False,
        )

        components['reference_versions'].select(
            fn=self.recipe_reference.on_reference_versions_select,
            inputs=[components['reference_modelid']],
            outputs=[
                components['reference_modeltype'],
                components['reference_disp_modeltype'],
                components['reference_versions'],
                components['reference_filenames'],
                components['reference_triger'],
                components['reference_weight_slider'],
                components['insert_prompt_btn'],
                components['reference_model_information'],
            ],
            show_progress=False,
        )

        components['goto_model_info_btn'].click(
            fn=lambda x: x, inputs=[components['reference_modelid']], outputs=[shortcut_input]
        )

        components['delete_reference_model_btn'].click(
            fn=self.recipe_reference.on_delete_reference_model_btn_click,
            inputs=[
                components['reference_modelid'],
                components['reference_shortcuts'],
            ],
            outputs=[
                components['reference_shortcuts'],
                components['refresh_reference_gallery'],
                components['reference_gallery'],
                components['reference_modelid'],
            ],
            show_progress=False,
        )

        components['insert_prompt_btn'].click(
            fn=self.recipe_reference.on_insert_prompt_btn_click,
            inputs=[
                components['reference_modeltype'],
                components['recipe_prompt'],
                components['recipe_negative'],
                components['recipe_option'],
                components['reference_filenames'],
                components['reference_weight_slider'],
                components['reference_triger'],
            ],
            outputs=[components['recipe_prompt'], components['recipe_output']],
        )

        components['close_reference_model_information_btn'].click(
            fn=self.recipe_reference.on_close_reference_model_information_btn_click,
            inputs=[components['reference_shortcuts']],
            outputs=[
                components['reference_shortcuts'],
                components['refresh_reference_gallery'],
                components['reference_gallery'],
                components['reference_modelid'],
            ],
            show_progress=False,
        )

        self._logger.debug("All recipe UI events wired successfully")

    def _on_recipe_prompt_tabs_select(self, evt: gr.SelectData):
        """Handle recipe prompt tabs selection event."""
        if hasattr(evt, 'index') and evt.index == 1:
            return gr.update(selected="reference_model")
        return gr.update(selected=None)

    def _on_recipe_input_change(self, recipe_input: str, shortcuts):
        """Handle recipe input change event."""
        # Use the existing implementation from RecipeBrowser
        from .recipe_browser import RecipeBrowser

        browser = RecipeBrowser()
        return browser.on_recipe_input_change(recipe_input, shortcuts)

    def _on_refresh_recipe_change(self):
        """Handle refresh recipe change event."""
        import datetime

        current_time = datetime.datetime.now()
        return current_time, current_time, current_time
