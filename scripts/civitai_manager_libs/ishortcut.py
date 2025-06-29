"""
ishortcut.py - Unified entry point for Civitai shortcut functionality.

This module serves as a backward-compatible facade over the new modularized
architecture in ishortcut_core/. All existing API functions are preserved
and delegate to the appropriate specialized processors.

The actual implementation has been moved to:
- ishortcut_core.model_processor: Model information handling
- ishortcut_core.file_processor: File operations and storage
- ishortcut_core.image_processor: Image downloading and processing
- ishortcut_core.metadata_processor: Data validation and metadata
- ishortcut_core.data_validator: Input validation
- ishortcut_core.model_factory: Model creation and management
"""

import os

try:
    from tqdm import tqdm
except ImportError:

    def tqdm(iterable, **kwargs):
        return iterable


from . import util
from . import setting

from .logging_config import get_logger

logger = get_logger(__name__)

# Import new modularized architecture
from .ishortcut_core import (
    ModelProcessor,
    FileProcessor,
    ImageProcessor,
    MetadataProcessor,
    DataValidator,
    ModelFactory,
    ShortcutCollectionManager,
    ShortcutSearchFilter,
    ShortcutThumbnailManager,
)

# Initialize processors
_model_processor = ModelProcessor()
_file_processor = FileProcessor()
_image_processor = ImageProcessor()
_metadata_processor = MetadataProcessor()
_data_validator = DataValidator()
_model_factory = ModelFactory()
_collection_manager = ShortcutCollectionManager()
_search_filter = ShortcutSearchFilter(_collection_manager, _model_processor)
_thumbnail_manager = ShortcutThumbnailManager(_image_processor, _collection_manager)

# Legacy constants for backward compatibility
thumbnail_max_size = (400, 400)

# Use centralized HTTP client factory
from .http_client import get_http_client
from .error_handler import with_error_handling
from .exceptions import NetworkError, FileOperationError, CivitaiShortcutError


# =============================================================================
# PUBLIC API - Backward Compatible Functions
# All functions below delegate to the new modularized architecture
# =============================================================================


@with_error_handling(
    fallback_value=(None, None, None, None, None, None, None, None, None, None),
    exception_types=(NetworkError, FileOperationError, CivitaiShortcutError),
    retry_count=1,
    retry_delay=1.0,
    user_message="Failed to get model information",
)
def get_model_information(modelid: str = None, versionid: str = None, ver_index: int = None):
    """
    Get model information from Civitai API.

    This function delegates to ModelProcessor for the actual implementation.
    """
    return _model_processor.get_model_information(modelid, versionid, ver_index)


@with_error_handling(
    fallback_value=None,
    exception_types=(Exception,),
    retry_count=0,
    user_message="Failed to get version description for gallery",
)
def get_version_description_gallery(modelid, version_info):
    """
    Get version description for gallery display.

    This function delegates to ModelProcessor for the actual implementation.
    """
    return _model_processor.get_version_description_gallery(modelid, version_info)


@with_error_handling(
    fallback_value=("", None, None),
    exception_types=(Exception,),
    retry_count=0,
    user_message="Failed to get version description",
)
def get_version_description(version_info: dict, model_info: dict = None):
    """
    Get version description HTML and training tags.

    This function delegates to ModelProcessor for the actual implementation.
    """
    return _model_processor.get_version_description(version_info, model_info)


def sort_shortcut_by_value(ISC, key, reverse=False):
    """Sort shortcuts by a specific value key."""
    return _search_filter.sort_shortcuts_by_value(ISC, key, reverse)


def sort_shortcut_by_modelid(ISC, reverse=False):
    """Sort shortcuts by model ID."""
    return _search_filter.sort_shortcuts_by_model_id(ISC, reverse)


def get_tags():
    """Get all unique tags from shortcuts."""
    return _search_filter.extract_all_tags()


def get_latest_version_info_by_model_id(id: str) -> dict:
    """
    Get latest version info by model ID.

    This function delegates to ModelProcessor for the actual implementation.
    """
    return _model_processor.get_latest_version_info_by_model_id(id)


def get_model_filenames(modelid: str):
    """
    Get model filenames for a given model ID.

    This function delegates to ModelProcessor for the actual implementation.
    """
    return _model_processor.get_model_filenames(modelid)


def is_baseModel(modelid: str, baseModels):
    """
    Check if model matches base models.

    This function delegates to ModelProcessor for the actual implementation.
    """
    return _model_processor.is_baseModel(modelid, baseModels)


def get_model_info(modelid: str):
    """
    Get model info from local storage.

    This function delegates to ModelProcessor for the actual implementation.
    """
    return _model_processor.get_model_info(modelid)


def get_version_info(modelid: str, versionid: str):
    """
    Get version info for a specific model and version.

    This function delegates to ModelProcessor for the actual implementation.
    """
    return _model_processor.get_version_info(modelid, versionid)


def get_version_images(modelid: str, versionid: str):
    """
    Get version images for a specific model and version.

    This function delegates to ModelProcessor for the actual implementation.
    """
    return _model_processor.get_version_images(modelid, versionid)


def get_version_image_id(filename):
    """Extract version and image ID from filename."""
    version_image, ext = os.path.splitext(filename)
    ids = version_image.split("-")
    if len(ids) > 1:
        return ids
    return None


def update_shortcut_note(model_id, note):
    """Update note for a specific model shortcut."""
    return _collection_manager.update_shortcut_note(model_id, note)


def get_shortcut_note(model_id):
    """Get note for a specific model shortcut."""
    return _collection_manager.get_shortcut_note(model_id)


def get_shortcut(model_id):
    """Get shortcut for a specific model."""
    return _collection_manager.get_shortcut(model_id)


def delete(ISC: dict, model_id):
    """Delete a shortcut for a specific model."""
    return _collection_manager.delete_shortcut(ISC, model_id)


def add(ISC: dict, model_id, register_information_only=False, progress=None) -> dict:
    """Add a model to shortcuts."""
    return _collection_manager.add_shortcut(ISC, model_id, register_information_only, progress)


def update_shortcut(model_id, progress=None):
    """Update or create a shortcut for a model."""
    return _collection_manager.update_shortcut(model_id, progress)


def update_shortcut_models(modelid_list: list, progress):
    """Update multiple shortcuts."""
    return _collection_manager.update_multiple_shortcuts(modelid_list, progress)


def update_shortcut_informations(modelid_list: list, progress):
    """Update shortcut information for multiple models."""
    return _collection_manager.update_multiple_shortcuts(modelid_list, progress)


def update_all_shortcut_informations(progress):
    """Update all shortcut information."""
    return _collection_manager.update_all_shortcuts(progress)


@with_error_handling(
    fallback_value=None,
    exception_types=(NetworkError, FileOperationError, CivitaiShortcutError),
    retry_count=1,
    retry_delay=1.0,
    user_message="Failed to write model information",
)
def write_model_information(modelid: str, register_only_information=False, progress=None):
    """
    Write model information to local storage.

    This function delegates to FileProcessor for the actual implementation.
    """
    return _file_processor.write_model_information(modelid, register_only_information, progress)


def delete_model_information(modelid: str):
    """
    Delete model information files.

    This function delegates to FileProcessor for the actual implementation.
    """
    return _file_processor.delete_model_information(modelid)


@with_error_handling(
    fallback_value=None,
    exception_types=(NetworkError, FileOperationError, CivitaiShortcutError),
    retry_count=1,
    retry_delay=1.0,
    user_message="Failed to update thumbnail images",
)
def update_thumbnail_images(progress):
    """Update thumbnail images for all shortcuts."""
    return _thumbnail_manager.update_all_thumbnails(progress)


def get_list(shortcut_types=None) -> str:
    """Get list of shortcut names."""
    return _search_filter.get_shortcuts_list(shortcut_types)


def get_image_list(
    shortcut_types=None, search=None, shortcut_basemodels=None, shortcut_classification=None
) -> str:
    """Get filtered list of shortcut images."""
    return _search_filter.get_filtered_shortcuts(
        shortcut_types, search, shortcut_basemodels, shortcut_classification
    )


def create_thumbnail(model_id, input_image_path):
    """
    Create thumbnail from input image.

    This function delegates to ImageProcessor for the actual implementation.
    """
    return _image_processor.create_thumbnail(model_id, input_image_path)


def delete_thumbnail_image(model_id):
    """
    Delete thumbnail image.

    This function delegates to ImageProcessor for the actual implementation.
    """
    return _image_processor.delete_thumbnail_image(model_id)


def download_thumbnail_image(model_id, url):
    """
    Download and generate thumbnail for a shortcut image.

    This function delegates to ImageProcessor for the actual implementation.
    """
    return _image_processor.download_thumbnail_image(model_id, url)


def is_sc_image(model_id):
    """
    Check if thumbnail image exists.

    This function delegates to ImageProcessor for the actual implementation.
    """
    return _image_processor.is_sc_image(model_id)


def save(ISC: dict) -> str:
    """Save shortcuts to file."""
    return _collection_manager.save_shortcuts(ISC)


def load() -> dict:
    """Load shortcuts from file."""
    return _collection_manager.load_shortcuts()


# =============================================================================
# Legacy functions - kept for backward compatibility
# These functions provide preview image functionality
# =============================================================================


def _get_preview_image_url(model_info) -> str:
    """Extract preview image URL from model info."""
    try:
        # Try to get from model versions
        if 'modelVersions' in model_info and model_info['modelVersions']:
            for version in model_info['modelVersions']:
                if 'images' in version and version['images']:
                    for image in version['images']:
                        url = image.get('url')
                        if url:
                            return url
        # Try to get from direct images
        if 'images' in model_info and model_info['images']:
            for image in model_info['images']:
                url = image.get('url')
                if url:
                    return url
        return None
    except Exception as e:
        logger.error(f"[ishortcut] Error extracting preview URL: {e}")
        return None


def _get_preview_image_path(model_info) -> str:
    """Generate local path for preview image."""
    try:
        model_id = model_info.get('id')
        if not model_id:
            return None
        preview_dir = setting.shortcut_thumbnail_folder
        os.makedirs(preview_dir, exist_ok=True)
        filename = f"model_{model_id}_preview.jpg"
        return os.path.join(preview_dir, filename)
    except Exception as e:
        logger.error(f"[ishortcut] Error generating image path: {e}")
        return None


def download_model_preview_image_by_model_info(model_info):
    """Download model preview image with improved error handling."""
    if not model_info:
        logger.error("[ishortcut] download_model_preview_image_by_model_info: model_info is None")
        return None
    model_id = model_info.get('id')
    if not model_id:
        logger.error("[ishortcut] download_model_preview_image_by_model_info: model_id not found")
        return None
    logger.info(f"[ishortcut] Downloading preview image for model: {model_id}")
    preview_url = _get_preview_image_url(model_info)
    if not preview_url:
        logger.warning("[ishortcut] No preview image URL found")
        return None
    image_path = _get_preview_image_path(model_info)
    if not image_path:
        logger.error("[ishortcut] Failed to generate image path")
        return None
    if os.path.exists(image_path):
        logger.info(f"[ishortcut] Preview image already exists: {image_path}")
        return image_path
    client = get_http_client()
    success = util.download_image_safe(preview_url, image_path, client, show_error=False)
    if success:
        logger.info(f"[ishortcut] Successfully downloaded preview image: {image_path}")
        return image_path
    logger.error(f"[ishortcut] Failed to download preview image: {preview_url}")
    return None


def get_preview_image_by_model_info(model_info):
    """Get preview image, download if not exists."""
    if not model_info:
        logger.error("[ishortcut] get_preview_image_by_model_info: model_info is None")
        return setting.no_card_preview_image
    image_path = _get_preview_image_path(model_info)
    if image_path and os.path.exists(image_path):
        logger.info(f"[ishortcut] Using existing preview image: {image_path}")
        return image_path
    downloaded_path = download_model_preview_image_by_model_info(model_info)
    if downloaded_path:
        return downloaded_path
    logger.info("[ishortcut] Using fallback preview image")
    return setting.no_card_preview_image
