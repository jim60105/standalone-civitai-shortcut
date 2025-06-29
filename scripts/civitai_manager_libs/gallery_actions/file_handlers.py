"""
Gallery File Handlers - File operations and folder management.

This module handles file operations such as opening folders and downloading files.
"""

import gradio as gr
from typing import Optional

from ..logging_config import get_logger
from .. import ishortcut, util
from ..error_handler import with_error_handling
from ..exceptions import NetworkError, FileOperationError

logger = get_logger(__name__)


def extract_model_info(page_url: str) -> tuple:
    """Extract model info from page URL."""
    # This function needs to be imported from original module
    return None, None


def download_user_gallery_images(modelid: str, images_url: list) -> Optional[str]:
    """Download user gallery images."""
    # This function needs to be imported from original module
    return None


@with_error_handling()
def on_open_image_folder_click(modelid: str) -> None:
    """Handle open image folder button click."""
    if modelid:
        model_info = ishortcut.get_model_info(modelid)
        if model_info:
            model_name = model_info['name']
            image_folder = util.get_download_image_folder(model_name)
            if image_folder:
                util.open_folder(image_folder)


@with_error_handling(
    fallback_value=gr.update(visible=False),
    exception_types=(NetworkError, FileOperationError),
    retry_count=2,
    retry_delay=3.0,
    user_message="Failed to download images",
)
def on_download_images_click(page_url: str, images_url: list) -> dict:
    """Handle download images button click."""
    is_image_folder = False
    if page_url:
        modelid, versionid = extract_model_info(page_url)
        image_folder = download_user_gallery_images(modelid, images_url)
        if image_folder:
            is_image_folder = True
    return gr.update(visible=is_image_folder)
