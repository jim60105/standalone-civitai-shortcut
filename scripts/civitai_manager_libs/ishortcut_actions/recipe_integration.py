"""
Recipe Integration Module

This module contains recipe integration related UI event handlers
migrated from ishortcut_action.py according to the design plan.
"""

import gradio as gr

from ..error_handler import with_error_handling
from ..exceptions import NetworkError, FileOperationError, ValidationError
from ..conditional_imports import import_manager
from ..logging_config import get_logger

logger = get_logger(__name__)

from .. import util
from .. import model
from .. import ishortcut
from .. import setting


@with_error_handling(
    fallback_value=None,
    exception_types=(FileOperationError,),
    retry_count=1,
    user_message="Failed to save personal note",
)
def on_personal_note_save_click(modelid, note):
    """Handle personal note save button click"""
    ishortcut.update_shortcut_model_note(modelid, note)


@with_error_handling(
    fallback_value=gr.update(visible=False),
    exception_types=(NetworkError, FileOperationError),
    retry_count=1,
    user_message="Failed to send image to recipe",
)
def on_send_to_recipe_click(model_id, img_file_info, img_index, civitai_images):
    """Handle send to recipe button click"""
    logger.debug("on_send_to_recipe_click called")
    logger.debug(f"  model_id: {repr(model_id)}")
    logger.debug(f"  img_file_info: {repr(img_file_info)}")
    logger.debug(f"  img_index: {repr(img_index)}")
    logger.debug(f"  civitai_images: {repr(civitai_images)}")

    try:
        # recipe_input format: [ shortcut_id:filename ]
        # This allows including reference shortcut id
        recipe_image = setting.set_imagefn_and_shortcutid_for_recipe_image(
            model_id, civitai_images[int(img_index)]
        )
        logger.debug(f"   recipe_image: {repr(recipe_image)}")

        # Pass parsed generation parameters directly when available
        if img_file_info:
            result = f"{recipe_image}\n{img_file_info}"
            logger.debug(f" Returning combined data: {repr(result)}")
            return result
        else:
            logger.debug(
                f"[RECIPE_INTEGRATION] No img_file_info, returning recipe_image only: "
                f"{repr(recipe_image)}"
            )
            return recipe_image
    except Exception as e:
        logger.debug(f" Exception in on_send_to_recipe_click: {e}")
        return gr.update(visible=False)
