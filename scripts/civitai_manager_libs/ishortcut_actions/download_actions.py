"""
Download Actions Module

This module contains download related UI event handlers
migrated from ishortcut_action.py according to the design plan.
"""

import os
import datetime
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
from .. import downloader


@with_error_handling(
    fallback_value=False,
    exception_types=(NetworkError, FileOperationError),
    retry_count=3,
    retry_delay=5.0,
    user_message="Failed to download model",
)
def on_download_model_click(
    model_id,
    version_id,
    file_name,
    vs_folder,
    vs_foldername,
    cs_foldername=None,
    ms_foldername=None,
):
    """Handle model download button click"""
    msg = None
    if version_id and model_id:
        # Download both preview images and files
        if cs_foldername == setting.CREATE_MODEL_FOLDER:
            msg = downloader.download_file_thread(
                file_name,
                version_id,
                True,
                vs_folder,
                vs_foldername.encode('utf-8'),
                None,
                ms_foldername,
            )
        else:
            msg = downloader.download_file_thread(
                file_name, version_id, False, False, None, cs_foldername, ms_foldername
            )

        # Update downloaded model information
        # This is done before loading model info, so it might not be necessary
        # model.update_downloaded_model()

        current_time = datetime.datetime.now()

        return (
            gr.update(value=current_time),
            gr.update(value=current_time)
        )
    return (
        gr.update(visible=True),
        gr.update(visible=True)
    )


@with_error_handling(
    fallback_value=gr.update(visible=False),
    exception_types=(NetworkError, FileOperationError),
    retry_count=2,
    user_message="Failed to download images",
)
def on_download_images_click(model_id: str, images_url):
    """Handle image download button click"""
    msg = None
    if model_id:
        model_info = ishortcut.get_model_info(model_id)
        if not model_info:
            return gr.update(visible=False)

        if "name" not in model_info.keys():
            return gr.update(visible=False)

        downloader.download_image_file(model_info['name'], images_url)
    current_time = datetime.datetime.now()
    return current_time


def on_file_gallery_loading(image_url):
    """Handle file gallery loading"""
    chk_image_url = image_url
    if image_url:
        chk_image_url = [
            img if os.path.isfile(img) else setting.no_card_preview_image for img in image_url
        ]
        return chk_image_url, chk_image_url
    return None, None
