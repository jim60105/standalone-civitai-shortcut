"""
UI and interaction logic for browsing recipes.
"""

import gradio as gr
import importlib

from .. import recipe
from .. import settings
from .. import sc_browser_page
from .. import recipe_browser_page
from ..logging_config import get_logger

logger = get_logger(__name__)


class RecipeBrowser:
    """Provides recipe browsing UI construc        logger = get_logger(__name__)
    logger.info(f"[RECIPE_INPUT_CHANGE] Event triggered with input: {repr(recipe_input)}")

    # If recipe_input is an empty string or contains no meaningful data,
    # return immediately without any UI updates to avoid interfering with other events
    if recipe_input is None or recipe_input == "" or not recipe_input.strip():
        logger.info(
            "[RECIPE_INPUT_CHANGE] Received empty/meaningless input, "
            "returning no-op updates to avoid interference."
        )
        # Return no-op updates that don't change any UI components
        return tuple(gr.update() for _ in range(22))st handling."""

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

        # Wire all events
        from .recipe_event_wiring import RecipeEventWiring

        event_wiring = RecipeEventWiring()
        event_wiring.wire_all_events(self.components, recipe_input, shortcut_input, civitai_tabs)

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

    def on_recipe_input_change(self, recipe_input: str, shortcuts):
        """
        Handle recipe input change with complete processing logic.
        Parses recipe input for image info and parameters, returns full UI update.
        """
        import gradio as gr
        import datetime
        from ..logging_config import get_logger
        from .. import settings, recipe
        from .recipe_utilities import RecipeUtilities

        logger = get_logger(__name__)
        logger.warning(f"[RECIPE_INPUT_CHANGE] Event triggered with input: {repr(recipe_input)}")

        # If recipe_input is an empty string or contains no meaningful data,
        # return immediately without any UI updates to avoid interfering with other events
        if (
            recipe_input is None
            or recipe_input == ""
            or not recipe_input.strip()
            or not self._is_valid_recipe_input_data(recipe_input)
        ):
            logger.warning(
                "[RECIPE_INPUT_CHANGE] Received empty/invalid input, "
                "returning no-op updates to avoid interference."
            )
            # Return no-op updates that don't change any UI components
            return tuple(gr.update() for _ in range(22))

        logger.warning(
            "[RECIPE_INPUT_CHANGE] Processing non-empty input, this will reset UI components!"
        )
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
                prompt_result = RecipeUtilities.analyze_prompt(param_data)
                positivePrompt, negativePrompt, options, gen_string = prompt_result
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
                result = setting.get_imagefn_and_shortcutid_from_recipe_image(recipe_input)
                if result:
                    shortcutid, recipe_image = result
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

    def on_recipe_prompt_tabs_select(self, evt):
        """Handle recipe prompt tabs selection event."""
        import gradio as gr

        if hasattr(evt, 'index') and evt.index == 1:
            return gr.update(selected="reference_model")
        return gr.update(selected=None)

    def _is_valid_recipe_input_data(self, recipe_input: str) -> bool:
        """
        Check if recipe_input contains valid data that should trigger UI updates.
        Returns True only if the input appears to be from 'send to recipe' functionality.
        """
        if not recipe_input or not recipe_input.strip():
            return False

        # Valid recipe input should contain either:
        # 1. A shortcut ID with image filename and parameters
        #    (format: "shortcutid:image.png\nparameters")
        # 2. Just an image filename that can be resolved to a shortcut

        # Check for the "shortcutid:image\nparameters" format
        if '\n' in recipe_input and ':' in recipe_input.split('\n')[0]:
            first_line = recipe_input.split('\n')[0]
            # Should have format "shortcutid:image_filename"
            if ':' in first_line and len(first_line.split(':', 1)) == 2:
                shortcut_id, image_fn = first_line.split(':', 1)
                # Basic validation: both parts should be non-empty
                if shortcut_id.strip() and image_fn.strip():
                    return True

        # Check if it's a valid image path that can be resolved
        from .. import settings

        try:
            result = settings.get_imagefn_and_shortcutid_from_recipe_image(recipe_input)
            if result is not None:
                shortcut_id, image_fn = result
                # Only consider valid if both shortcut_id and image_fn are provided
                return bool(shortcut_id and image_fn)
        except Exception:
            pass

        # If nothing matches, it's probably not valid recipe input data
        return False
