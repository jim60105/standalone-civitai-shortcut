"""
Gallery module - Refactored from civitai_gallery_action.py

This module provides a clean, modular approach to gallery management
following SRP and KISS principles.
"""

import gradio as gr

from .ui_components import GalleryUIComponents
from .event_handlers import GalleryEventHandlers
from .data_processor import GalleryDataProcessor
from .download_manager import GalleryDownloadManager
from .gallery_utilities import GalleryUtilities, CompatibilityManager

# Import util for backward compatibility
from .. import util  # noqa: F401
from ..logging_config import get_logger

logger = get_logger(__name__)

# Global instances for backward compatibility
_ui_components = None
_event_handlers = None
_data_processor = None
_download_manager = None
_utilities = None
_compat_manager = CompatibilityManager()


def get_gallery_components():
    """Get or create gallery component instances."""
    global _ui_components, _event_handlers, _data_processor, _download_manager, _utilities

    if _ui_components is None:
        _ui_components = GalleryUIComponents()
        _data_processor = GalleryDataProcessor()
        _download_manager = GalleryDownloadManager()
        _utilities = GalleryUtilities()
        _event_handlers = GalleryEventHandlers(_data_processor, _download_manager, _utilities)

    return _ui_components, _event_handlers, _data_processor, _download_manager, _utilities


# Backward compatibility functions
def on_ui(recipe_input):
    """Main UI creation function - backward compatibility."""
    ui_components, _, _, _, _ = get_gallery_components()
    return ui_components.create_main_ui(recipe_input)


def on_gallery_select(evt, civitai_images):
    """Gallery selection handler - backward compatibility."""
    # Legacy Gradio v3/v4 event handler: auto-fix parameter mixup for select event
    # 1. evt 應為 SelectData，civitai_images 應為 list
    # 2. 若 evt 不是 SelectData、但 civitai_images 是 SelectData，則自動交換
    # 3. 若 evt 是 list、civitai_images 是 None，則自動 fallback
    import gradio as gr
    if not isinstance(evt, gr.SelectData):
        if isinstance(civitai_images, gr.SelectData):
            logger.warning("[GALLERY] Detected parameter mixup - auto-swapping evt/civitai_images (legacy v3/v4 fix)")
            evt, civitai_images = civitai_images, evt
        elif isinstance(evt, list) and civitai_images is None:
            logger.debug("[GALLERY] Detected Gradio v3/v4 default parameter mode: evt is images list, civitai_images is None")
            civitai_images = evt
            evt = type('FakeSelectData', (), {'index': 0, 'value': None, 'selected': True})()
        else:
            logger.error(f"[GALLERY] evt is NOT SelectData! It's {type(evt)}: {evt}")
            return None, None, gr.update(), "Error: Invalid event type (not SelectData)"
    if civitai_images is None:
        logger.error("[GALLERY] civitai_images is None! This indicates incorrect event binding.")
        return None, None, gr.update(), "Error: No images data available"
    _, event_handlers, _, _, _ = get_gallery_components()
    return event_handlers.handle_gallery_select(evt, civitai_images)


def on_send_to_recipe_click(model_id, img_file_info, img_index, civitai_images):
    """Recipe integration handler - backward compatibility."""
    _, event_handlers, _, _, _ = get_gallery_components()
    return event_handlers.handle_recipe_integration(
        model_id, img_file_info, img_index, civitai_images
    )


def on_open_image_folder_click(modelid):
    """Open image folder handler - backward compatibility."""
    _, event_handlers, _, _, _ = get_gallery_components()
    return event_handlers.handle_open_image_folder(modelid)


def on_download_images_click(page_url, images_url):
    """Download images handler - backward compatibility."""
    _, event_handlers, _, _, _ = get_gallery_components()
    return event_handlers.handle_download_click(page_url, images_url)


def on_page_slider_release(usergal_page_url, page_slider, paging_information):
    """Page slider handler - backward compatibility."""
    _, event_handlers, _, _, _ = get_gallery_components()
    return event_handlers.handle_page_slider_release(
        usergal_page_url, page_slider, paging_information
    )


def on_first_btn_click(usergal_page_url, paging_information):
    """First page button handler - backward compatibility."""
    _, event_handlers, _, _, _ = get_gallery_components()
    return event_handlers.handle_first_btn_click(usergal_page_url, paging_information)


def on_end_btn_click(usergal_page_url, paging_information):
    """End page button handler - backward compatibility."""
    _, event_handlers, _, _, _ = get_gallery_components()
    return event_handlers.handle_end_btn_click(usergal_page_url, paging_information)


def on_next_btn_click(usergal_page_url, paging_information):
    """Next page button handler - backward compatibility."""
    _, event_handlers, _, _, _ = get_gallery_components()
    return event_handlers.handle_next_btn_click(usergal_page_url, paging_information)


def on_prev_btn_click(usergal_page_url, paging_information):
    """Previous page button handler - backward compatibility."""
    _, event_handlers, _, _, _ = get_gallery_components()
    return event_handlers.handle_prev_btn_click(usergal_page_url, paging_information)


def on_selected_model_id_change(modelid):
    """Model selection change handler - backward compatibility."""
    _, event_handlers, _, _, _ = get_gallery_components()
    return event_handlers.handle_selected_model_id_change(modelid)


def on_versions_list_select(evt, modelid=None):
    """Version selection handler - backward compatibility."""
    _, event_handlers, _, _, _ = get_gallery_components()
    return event_handlers.handle_versions_list_select(evt, modelid)


def on_usergal_page_url_change(usergal_page_url, paging_information):
    """Page URL change handler - backward compatibility."""
    _, event_handlers, _, _, _ = get_gallery_components()
    return event_handlers.handle_usergal_page_url_change(usergal_page_url, paging_information)


def on_refresh_gallery_change(images_url, progress=None):
    """Refresh gallery handler - backward compatibility."""
    _, event_handlers, _, _, _ = get_gallery_components()
    return event_handlers.handle_refresh_gallery_change(images_url, progress)


def on_pre_loading_change(usergal_page_url, paging_information):
    """Pre-loading handler - backward compatibility."""
    _, event_handlers, _, _, _ = get_gallery_components()
    return event_handlers.handle_pre_loading_change(usergal_page_url, paging_information)


def on_civitai_hidden_change(hidden, index):
    """Hidden change handler - backward compatibility."""
    _, event_handlers, _, _, _ = get_gallery_components()
    return event_handlers.handle_civitai_hidden_change(hidden, index)


def format_civitai_metadata_to_auto1111(meta):
    """Metadata formatting function - backward compatibility."""
    _, _, data_processor, _, _ = get_gallery_components()
    return data_processor.format_metadata_to_auto1111(meta)


def get_model_information(page_url=None):
    """Get model information - backward compatibility."""
    _, _, data_processor, _, _ = get_gallery_components()
    return data_processor.get_model_information(page_url)


def get_gallery_information(page_url=None, show_nsfw=False):
    """Get gallery information - backward compatibility."""
    _, _, data_processor, _, _ = get_gallery_components()
    return data_processor.get_gallery_data(page_url, show_nsfw)


def get_user_gallery(modelid, page_url, show_nsfw):
    """Get user gallery - backward compatibility."""
    _, _, data_processor, _, _ = get_gallery_components()
    return data_processor.get_user_gallery(modelid, page_url, show_nsfw)


def get_image_page(modelid, page_url, show_nsfw=False):
    """Get image page data - backward compatibility."""
    _, _, data_processor, _, _ = get_gallery_components()
    return data_processor.get_image_page_data(modelid, page_url, show_nsfw)


def get_paging_information_working(modelId, modelVersionId=None, show_nsfw=False):
    """Get pagination information - backward compatibility."""
    _, _, data_processor, _, _ = get_gallery_components()
    return data_processor.get_pagination_info(modelId, modelVersionId, show_nsfw)


def get_current_page(paging_information, page_url):
    """Calculate current page - backward compatibility."""
    _, _, data_processor, _, _ = get_gallery_components()
    return data_processor.calculate_current_page(paging_information, page_url)


def load_gallery_page(usergal_page_url, paging_information):
    """Load gallery page - backward compatibility."""
    _, _, data_processor, _, _ = get_gallery_components()
    return data_processor.load_page_data(usergal_page_url, paging_information)


def download_images(dn_image_list, client=None):
    """Download images - backward compatibility."""
    _, _, _, download_manager, _ = get_gallery_components()
    return download_manager.download_images_simple(dn_image_list, client)


def download_images_with_progress(dn_image_list, progress_callback=None):
    """Download images with progress - backward compatibility."""
    _, _, _, download_manager, _ = get_gallery_components()
    return download_manager.download_images_parallel(dn_image_list, progress_callback)


def download_images_batch(dn_image_list, batch_size=None):
    """Download images in batches - backward compatibility."""
    _, _, _, download_manager, _ = get_gallery_components()
    return download_manager.download_images_batch(dn_image_list, batch_size)


def download_user_gallery_images(model_id, image_urls):
    """Download user gallery images - backward compatibility."""
    _, _, _, download_manager, _ = get_gallery_components()
    return download_manager.download_user_gallery(model_id, image_urls)


def gallery_loading(images_url, progress):
    """Gallery loading - backward compatibility."""
    _, _, _, download_manager, _ = get_gallery_components()
    return download_manager.load_gallery_images(images_url, progress)


def pre_loading(usergal_page_url, paging_information):
    """Pre-loading - backward compatibility."""
    _, _, _, download_manager, _ = get_gallery_components()
    return download_manager.preload_next_page(usergal_page_url, paging_information)


def _download_single_image(img_url, save_path):
    """Download single image - backward compatibility."""
    _, _, _, download_manager, _ = get_gallery_components()
    return download_manager.download_single_image(img_url, save_path)


def extract_model_info(url):
    """Extract model info from URL - backward compatibility."""
    _, _, _, _, utilities = get_gallery_components()
    return utilities.extract_model_info(url)


def extract_url_cursor(url):
    """Extract URL cursor - backward compatibility."""
    _, _, _, _, utilities = get_gallery_components()
    return utilities.extract_url_cursor(url)


def get_default_page_url(modelId, modelVersionId=None, show_nsfw=False, limit=0):
    """Build default page URL - backward compatibility."""
    _, _, _, _, utilities = get_gallery_components()
    return utilities.build_default_page_url(modelId, modelVersionId, show_nsfw, limit)


def fix_page_url_cursor(page_url, use=True):
    """Fix page URL cursor - backward compatibility."""
    _, _, _, _, utilities = get_gallery_components()
    return utilities.fix_page_url_cursor(page_url, use)


def set_compatibility_layer(compat_layer):
    """Set compatibility layer - backward compatibility."""
    _compat_manager.set_compatibility_layer(compat_layer)


# Class exports for direct access
GalleryDownloadManager = GalleryDownloadManager

# Export all for backward compatibility
__all__ = [
    'GalleryUIComponents',
    'GalleryEventHandlers',
    'GalleryDataProcessor',
    'GalleryDownloadManager',
    'GalleryUtilities',
    'CompatibilityManager',
    'on_ui',
    'on_gallery_select',
    'on_send_to_recipe_click',
    'on_open_image_folder_click',
    'on_download_images_click',
    'on_page_slider_release',
    'on_first_btn_click',
    'on_end_btn_click',
    'on_next_btn_click',
    'on_prev_btn_click',
    'on_selected_model_id_change',
    'on_versions_list_select',
    'on_usergal_page_url_change',
    'on_refresh_gallery_change',
    'on_pre_loading_change',
    'on_civitai_hidden_change',
    'format_civitai_metadata_to_auto1111',
    'get_model_information',
    'get_gallery_information',
    'get_user_gallery',
    'get_image_page',
    'get_paging_information_working',
    'get_current_page',
    'load_gallery_page',
    'download_images',
    'download_images_with_progress',
    'download_images_batch',
    'download_user_gallery_images',
    'gallery_loading',
    'pre_loading',
    '_download_single_image',
    'extract_model_info',
    'extract_url_cursor',
    'get_default_page_url',
    'fix_page_url_cursor',
    'set_compatibility_layer',
]
