"""
UI and interaction logic for browsing recipes.
"""

import gradio as gr
import importlib

from .. import recipe
from .. import setting
from .. import sc_browser_page
from .. import recipe_browser_page
from ..logging_config import get_logger

logger = get_logger(__name__)


class RecipeBrowser:
    """Provides recipe browsing UI construction and list handling."""

    def __init__(self):
        self._logger = logger

    def on_ui(self, recipe_input, shortcut_input, civitai_tabs):
        """Create the complete recipe management UI."""
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
                                with gr.Row():
                                    try:
                                        from ..conditional_imports import import_manager

                                        parameters_copypaste = import_manager.get_webui_module(
                                            'extras', 'parameters_copypaste'
                                        )
                                        if parameters_copypaste:
                                            send_to_buttons = parameters_copypaste.create_buttons(
                                                ["txt2img", "img2img", "inpaint", "extras"]
                                            )
                                    except Exception:
                                        pass
                                recipe_classification = gr.Dropdown(
                                    label="Prompt Recipe Classification",
                                    choices=[setting.PLACEHOLDER] + recipe.get_classifications(),
                                    value=setting.PLACEHOLDER,
                                    info=(
                                        "You can choose from a list or enter manually. "
                                        "If you enter a classification that didn't exist before, "
                                        "a new classification will be created."
                                    ),
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
                                    "This image does not influence the prompt on the left. "
                                    "You can choose any image that matches the created prompt."
                                )
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
                            with gr.TabItem("Generate Information", id="generation_info"):
                                recipe_output = gr.Textbox(
                                    label="Generate Information",
                                    interactive=False,
                                    lines=20,
                                    placeholder=(
                                        "The prompt and parameters are combined and displayed here."
                                    ),
                                    container=True,
                                    show_copy_button=True,
                                )

        with gr.Row(visible=False):
            selected_recipe_name = gr.Textbox()
            refresh_recipe = gr.Textbox()
            recipe_generate_data = gr.Textbox()
            reference_shortcuts = gr.State()
            refresh_reference_gallery = gr.Textbox()

        # Bind copy-paste buttons if available
        send_to_buttons = None
        try:
            from ..conditional_imports import import_manager

            parameters_copypaste = import_manager.get_webui_module('extras', 'parameters_copypaste')
            if parameters_copypaste:
                send_to_buttons = parameters_copypaste.create_buttons(
                    ["txt2img", "img2img", "inpaint", "extras"]
                )
                if send_to_buttons:
                    parameters_copypaste.bind_buttons(send_to_buttons, recipe_image, recipe_output)
        except Exception:
            pass

        # Store component references for event binding
        self.components = {
            'recipe_new_btn': recipe_new_btn,
            'recipe_gallery': recipe_gallery,
            'refresh_recipe_browser': refresh_recipe_browser,
            'recipe_drop_image': recipe_drop_image,
            'recipe_title_name': recipe_title_name,
            'recipe_name': recipe_name,
            'recipe_desc': recipe_desc,
            'recipe_prompt': recipe_prompt,
            'recipe_negative': recipe_negative,
            'recipe_option': recipe_option,
            'recipe_classification': recipe_classification,
            'recipe_create_btn': recipe_create_btn,
            'recipe_update_btn': recipe_update_btn,
            'recipe_delete_btn': recipe_delete_btn,
            'recipe_image': recipe_image,
            'recipe_output': recipe_output,
            'recipe_prompt_tabs': recipe_prompt_tabs,
            'recipe_reference_tabs': recipe_reference_tabs,
            'reference_sc_gallery': reference_sc_gallery,
            'reference_delete': reference_delete,
            'reference_model_information': reference_model_information,
            'reference_modelid': reference_modelid,
            'reference_modeltype': reference_modeltype,
            'reference_disp_modeltype': reference_disp_modeltype,
            'reference_versions': reference_versions,
            'reference_filenames': reference_filenames,
            'reference_weight_slider': reference_weight_slider,
            'reference_triger': reference_triger,
            'insert_prompt_btn': insert_prompt_btn,
            'goto_model_info_btn': goto_model_info_btn,
            'delete_reference_model_btn': delete_reference_model_btn,
            'close_reference_model_information_btn': close_reference_model_information_btn,
            'reference_gallery': reference_gallery,
            'selected_recipe_name': selected_recipe_name,
            'refresh_recipe': refresh_recipe,
            'recipe_generate_data': recipe_generate_data,
            'reference_shortcuts': reference_shortcuts,
            'refresh_reference_gallery': refresh_reference_gallery,
            'refresh_reference_sc_browser': refresh_reference_sc_browser,
            'refresh_reference_sc_gallery': refresh_reference_sc_gallery,
        }

        return refresh_recipe

    def create_browser_ui(self) -> tuple:
        """Construct and return the browser gallery and refresh trigger."""
        # Dynamically import on_ui to respect monkeypatch overrides
        module = importlib.import_module('scripts.civitai_manager_libs.recipe_browser_page')
        return module.on_ui()

    def refresh_recipe_list(self, search_term: str = "") -> list:
        """Refresh list of recipes matching the search term."""
        result = recipe.get_list(search=search_term)
        return result or []

    def filter_recipes(self, filter_type: str, filter_value: str) -> list:
        """Filter recipes by classification or shortcuts."""
        criteria = {filter_type: filter_value}
        result = recipe.get_list(**criteria)
        return result or []

    def sort_recipes(self, sort_by: str, ascending: bool = True) -> list:
        """Sort recipes by specified field."""
        recipelist = recipe.get_list()
        if recipelist is None:
            return []
        try:
            return sorted(recipelist, key=lambda x: x.get(sort_by), reverse=not ascending)
        except Exception:
            self._logger.warning("sort_recipes: unable to sort by %s", sort_by)
            return recipelist

    def handle_recipe_selection(self, recipe_id: str) -> dict:
        """Retrieve detailed recipe information for selection event."""
        result = recipe.get_recipe(recipe_id)
        return result or {}

    def search_recipes(self, query: str) -> list:
        """Search recipes by name, description, or classification."""
        result = recipe.get_list(search=query)
        return result or []

    def on_refresh_recipe_change(self):
        """Handle refresh recipe change event."""
        import datetime

        current_time = datetime.datetime.now()
        return current_time, current_time, current_time

    def on_recipe_input_change(self, recipe_input: str, _):
        """
        Handle recipe input change, parsing first line for image filename and metadata for prompts.
        Returns list of updated values matching Gradio component order.
        """
        from .recipe_utilities import RecipeUtilities

        parts = recipe_input.splitlines()
        first_line = parts[0] if parts else ''
        img = ''
        if ':' in first_line:
            img = first_line.split(':', 1)[1]
        base = [None, img, img, None, None, None, None, None]
        metadata = recipe_input[len(first_line) + 1 :]
        ap, an, ao, ag = RecipeUtilities.analyze_prompt(metadata)
        prompt_update = {'value': ap or ''}
        negative_update = {'value': an or ''}
        option_update = {'value': ao or ''}
        output_update = {'value': ag}
        return base + [prompt_update, negative_update, option_update, output_update]

    def on_recipe_prompt_tabs_select(self, evt):
        """Handle recipe prompt tabs selection event."""
        import gradio as gr

        if hasattr(evt, 'index') and evt.index == 1:
            return gr.update(selected="reference_model")
        return gr.update(selected=None)
