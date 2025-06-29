"""
Gallery Actions Package - Refactored from civitai_gallery_action.py

This package contains gallery-related UI event handlers and utilities,
split from the original large module for better maintainability.
"""

from .download_manager import (
    GalleryDownloadManager,
    download_images_with_progress,
    download_images_batch,
)
from .gallery_ui import (
    on_ui,
    on_gallery_select,
    on_send_to_recipe_click,
    on_civitai_hidden_change,
)
from .navigation_handlers import (
    on_page_slider_release,
    on_first_btn_click,
    on_end_btn_click,
    on_next_btn_click,
    on_prev_btn_click,
)
from .model_handlers import (
    on_selected_model_id_change,
    on_versions_list_select,
    get_model_information,
)
from .page_handlers import (
    on_usergal_page_url_change,
    on_refresh_gallery_change,
)
from .file_handlers import (
    on_open_image_folder_click,
    on_download_images_click,
)

# For backward compatibility
from .download_manager import _download_single_image

__all__ = [
    'GalleryDownloadManager',
    'download_images_with_progress',
    'download_images_batch',
    'on_ui',
    'on_gallery_select',
    'on_send_to_recipe_click',
    'on_civitai_hidden_change',
    'on_page_slider_release',
    'on_first_btn_click',
    'on_end_btn_click',
    'on_next_btn_click',
    'on_prev_btn_click',
    'on_selected_model_id_change',
    'on_versions_list_select',
    'get_model_information',
    'on_usergal_page_url_change',
    'on_refresh_gallery_change',
    'on_open_image_folder_click',
    'on_download_images_click',
    '_download_single_image',
]
