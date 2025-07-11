"""
Gallery presentation and management for recipe-associated images.
"""

import os

import gradio as gr
from PIL import Image

from .. import settings
from .. import recipe
from ..logging_config import get_logger
from ..compat.compat_layer import CompatibilityLayer
from ..image_processor import ImageMetadataProcessor

logger = get_logger(__name__)


class RecipeGallery:
    """Manages display and CRUD of recipe-associated images."""

    def __init__(self):
        self._logger = logger

    def create_gallery_ui(self, recipe_id: str) -> gr.Gallery:
        """Create a Gradio gallery UI component for a given recipe."""
        images = self.load_recipe_images(recipe_id)
        return gr.Gallery(
            value=images,
            show_label=False,
            columns=settings.prompt_shortcut_column,
            height="auto",
            object_fit=settings.gallery_thumbnail_image_style,
            preview=False,
            allow_preview=False,
        )

    def load_recipe_images(self, recipe_id: str) -> list:
        """Load file paths of images associated with the specified recipe."""
        if not recipe_id:
            return []
        rc = recipe.get_recipe(recipe_id)
        img = rc.get('image') if isinstance(rc, dict) else None
        if img:
            img_path = os.path.join(settings.shortcut_recipe_folder, img)
            if os.path.isfile(img_path):
                return [img_path]
        return []

    def add_image_to_recipe(self, recipe_id: str, image_path: str) -> bool:
        """Associate an image file with a recipe."""
        result = recipe.update_recipe_image(recipe_id, image_path)
        return result if result is not None else False

    def remove_image_from_recipe(self, recipe_id: str, image_id: str) -> bool:
        """Remove associated image from a recipe."""
        # Clearing image association
        result = recipe.update_recipe_image(recipe_id, None)
        return result if result is not None else False

    def generate_image_thumbnail(self, image_path: str) -> str:
        """Generate and return the thumbnail path for an image."""
        try:
            thumb_dir = getattr(settings, 'shortcut_thumbnail_folder', 'thumbnails')
            os.makedirs(thumb_dir, exist_ok=True)
            base = os.path.basename(image_path)
            thumb_path = os.path.join(thumb_dir, base)
            with Image.open(image_path) as img:
                # Use default thumbnail size if not available in settings
                thumb_width = getattr(settings, 'thumbnail_width', 256)
                thumb_height = getattr(settings, 'thumbnail_height', 256)
                img.thumbnail((thumb_width, thumb_height))
                img.save(thumb_path)
            return thumb_path
        except Exception as e:
            self._logger.error("generate_image_thumbnail: %s", e)
            return image_path

    def get_image_metadata(self, image_path: str) -> dict:
        """Retrieve embedded metadata or parameters from an image file."""
        compat = CompatibilityLayer.get_compatibility_layer()
        if compat and hasattr(compat, 'metadata_processor'):
            try:
                info = compat.metadata_processor.extract_png_info(image_path)
                if isinstance(info, tuple) and len(info) >= 2:
                    # Return the parameters dict from the tuple
                    return info[1] if info[1] else {}
                return info if isinstance(info, dict) else {}
            except Exception:
                pass
        # Fallback to PIL metadata extraction
        try:
            processor = ImageMetadataProcessor(mode='standalone')
            result = processor.extract_png_info(image_path)
            return result if isinstance(result, dict) else {}
        except Exception as e:
            self._logger.error("get_image_metadata: %s", e)
            return {}

    def on_recipe_drop_image_upload(self, recipe_img):
        """Handle image drop upload for recipe."""
        if recipe_img:
            import datetime

            current_time = datetime.datetime.now()
            return recipe_img, current_time
        return gr.update(visible=True), gr.update(visible=False)

    def on_recipe_generate_data_change(self, recipe_img):
        """Process recipe PNG info with compatibility layer support."""
        from ..conditional_imports import import_manager
        import io

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
            from .recipe_utilities import RecipeUtilities

            positivePrompt, negativePrompt, options, gen_string = RecipeUtilities.analyze_prompt(
                generate_data
            )
            return (
                gr.update(value=positivePrompt),
                gr.update(value=negativePrompt),
                gr.update(value=options),
                gr.update(value=gen_string),
            )
        return (gr.update(value=""), gr.update(value=""), gr.update(value=""), gr.update(value=""))

    def on_recipe_gallery_select(self, evt: gr.SelectData):
        """Handle recipe gallery selection event."""
        import datetime

        current_time = datetime.datetime.now()

        logger.info(f"[RECIPE] Gallery selection triggered! evt.value: {evt.value}")

        # Handle evt.value which can be either a string or a list [image_url, shortcut_name]
        if isinstance(evt.value, list) and len(evt.value) > 1:
            select_name = evt.value[1]  # Use the shortcut name (second element)
            logger.info(f"[RECIPE] Gallery select - using list element: {select_name}")
        elif isinstance(evt.value, str):
            select_name = evt.value
            logger.info(f"[RECIPE] Gallery select - using string: {select_name}")
        # Support new Gradio Gallery select event format
        elif isinstance(evt.value, dict):
            # Use caption as the recipe name
            select_name = evt.value.get("caption")
            logger.info(f"[RECIPE] Gallery select - using dict caption: {select_name}")
        else:
            logger.debug(
                f"[RECIPE] Unexpected evt.value format in on_recipe_gallery_select: " f"{evt.value}"
            )
            return (
                gr.update(value=""),  # selected_recipe_name
                gr.update(value=""),  # recipe_name
                gr.update(value=""),  # recipe_desc
                gr.update(value=""),  # recipe_prompt
                gr.update(value=""),  # recipe_negative
                gr.update(value=""),  # recipe_option
                gr.update(value=""),  # recipe_output
                gr.update(choices=[], value=""),  # recipe_classification
                gr.update(label=""),  # recipe_title_name
                None,  # recipe_image
                None,  # recipe_drop_image
                gr.update(visible=True),  # recipe_create_btn
                gr.update(visible=False),  # recipe_update_btn
                [],  # reference_shortcuts
                None,  # reference_modelid
                current_time,  # refresh_reference_gallery
            )

        from .recipe_utilities import RecipeUtilities

        logger.info(f"[RECIPE] Getting recipe information for: {select_name}")
        result = RecipeUtilities.get_recipe_information(select_name)
        description, Prompt, negativePrompt, options, gen_string, classification, imagefile = result
        logger.info(
            f"[RECIPE] Recipe info result - desc: {description}, "
            f"prompt: {Prompt[:50] if Prompt else None}..."
        )

        if imagefile:
            if not os.path.isfile(imagefile):
                imagefile = None

        shortcuts = recipe.get_recipe_shortcuts(select_name)

        logger.info("[RECIPE] Returning 16 outputs for UI update")

        # Fallback if select_name is invalid
        if not select_name:
            logger.debug("[RECIPE] select_name is None or empty, fallback.")
            return (
                gr.update(value=""),  # selected_recipe_name
                gr.update(value=""),  # recipe_name
                gr.update(value=""),  # recipe_desc
                gr.update(value=""),  # recipe_prompt
                gr.update(value=""),  # recipe_negative
                gr.update(value=""),  # recipe_option
                gr.update(value=""),  # recipe_output
                gr.update(choices=[], value=""),  # recipe_classification
                gr.update(label=""),  # recipe_title_name
                None,  # recipe_image
                None,  # recipe_drop_image
                gr.update(visible=True),  # recipe_create_btn
                gr.update(visible=False),  # recipe_update_btn
                [],  # reference_shortcuts
                None,  # reference_modelid
                current_time,  # refresh_reference_gallery
            )

        return (
            gr.update(value=select_name),
            gr.update(value=select_name),
            gr.update(value=description),
            gr.update(value=Prompt),
            gr.update(value=negativePrompt),
            gr.update(value=options),
            gr.update(value=gen_string),
            gr.update(
                choices=[settings.PLACEHOLDER] + recipe.get_classifications(), value=classification
            ),
            gr.update(label=select_name),
            imagefile,
            None,
            gr.update(visible=False),
            gr.update(visible=True),
            shortcuts,
            None,
            current_time,
        )
