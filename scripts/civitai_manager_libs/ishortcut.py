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
import json
import datetime

try:
    from tqdm import tqdm
except ImportError:

    def tqdm(iterable, **kwargs):
        return iterable


from . import util
from . import setting
from . import civitai
from . import classification

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
)

# Initialize processors
_model_processor = ModelProcessor()
_file_processor = FileProcessor()
_image_processor = ImageProcessor()
_metadata_processor = MetadataProcessor()
_data_validator = DataValidator()
_model_factory = ModelFactory()

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
    sorted_data = sorted(ISC.items(), key=lambda x: x[1][key], reverse=reverse)
    return dict(sorted_data)


def sort_shortcut_by_modelid(ISC, reverse=False):
    """Sort shortcuts by model ID."""
    sorted_data = {}
    for key in sorted(ISC.keys(), reverse=reverse):
        sorted_data[key] = ISC[key]
    return sorted_data


def get_tags():
    """Get all unique tags from shortcuts."""
    ISC = load()
    if not ISC:
        return

    result = []
    for item in ISC.values():
        name_values = set(tag['name'] for tag in item['tags'])
        result.extend(name_values)

    result = list(set(result))
    return result


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


def update_shortcut_model_note(modelid, note):
    """Update note for a specific model shortcut."""
    if modelid:
        ISC = load()
        try:
            ISC[str(modelid)]["note"] = str(note)
            save(ISC)
        except Exception:
            pass


def get_shortcut_model_note(modelid):
    """Get note for a specific model shortcut."""
    if modelid:
        ISC = load()
        try:
            return ISC[str(modelid)]["note"]
        except Exception:
            pass
    return None


def get_shortcut_model(modelid):
    """Get shortcut for a specific model."""
    if modelid:
        ISC = load()
        try:
            return ISC[str(modelid)]
        except Exception:
            pass
    return None


def delete_shortcut_model(modelid):
    """Delete shortcut for a specific model."""
    if modelid:
        ISC = load()
        ISC = delete(ISC, modelid)
        save(ISC)


def update_shortcut(modelid, progress=None):
    """
    Update or create a shortcut for a model.

    This function delegates to ModelFactory for the actual implementation.
    """
    if not modelid:
        return

    # Get existing shortcut data to preserve notes and dates
    ISC = load()
    existing_data = {}
    if ISC and str(modelid) in ISC:
        existing_data = ISC[str(modelid)]

    # Create/update shortcut using ModelFactory
    result_shortcuts = _model_factory.create_model_shortcut(
        str(modelid), register_information_only=False, progress=progress
    )

    if result_shortcuts and str(modelid) in result_shortcuts:
        # Preserve existing note and date
        if "note" in existing_data:
            result_shortcuts[str(modelid)]["note"] = existing_data["note"]
        if "date" in existing_data and existing_data["date"]:
            result_shortcuts[str(modelid)]["date"] = existing_data["date"]
        else:
            # Set current date if no existing date
            date = datetime.datetime.now()
            result_shortcuts[str(modelid)]["date"] = date.strftime("%Y-%m-%d %H:%M:%S")

        # Ensure NSFW field exists
        if 'nsfw' not in result_shortcuts[str(modelid)]:
            result_shortcuts[str(modelid)]["nsfw"] = False

        # Update the shortcuts database
        if ISC:
            ISC.update(result_shortcuts)
        else:
            ISC = result_shortcuts
        save(ISC)


def update_shortcut_models(modelid_list: list, progress):
    """Update multiple shortcuts."""
    if not modelid_list:
        return

    for k in progress.tqdm(modelid_list, desc="Updating Shortcut"):
        update_shortcut(k, progress)


def update_shortcut_informations(modelid_list: list, progress):
    """Update shortcut information for multiple models."""
    if not modelid_list:
        return

    for modelid in progress.tqdm(modelid_list, desc="Updating Models Information"):
        if modelid:
            update_shortcut(modelid, progress)


def update_all_shortcut_informations(progress):
    """Update all shortcut information."""
    preISC = load()
    if not preISC:
        return

    modelid_list = [k for k in preISC]
    update_shortcut_informations(modelid_list, progress)


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


def update_thumbnail_images(progress):
    """Update thumbnail images for all shortcuts."""
    preISC = load()
    if not preISC:
        return

    for k, v in progress.tqdm(preISC.items(), desc="Update Shortcut's Thumbnails"):
        if v:
            # Get latest information from the site
            version_info = civitai.get_latest_version_info_by_model_id(v['id'])
            if not version_info:
                continue

            if 'images' not in version_info.keys():
                continue

            # Select the most appropriate image by NSFW level
            if len(version_info["images"]) > 0:
                cur_nsfw_level = len(setting.NSFW_levels)
                def_image = None
                for img_dict in version_info["images"]:
                    img_nsfw_level = 1

                    if "nsfw" in img_dict.keys():
                        img_nsfw_level = setting.NSFW_levels.index(img_dict["nsfw"])

                    if "nsfwLevel" in img_dict.keys():
                        img_nsfw_level = img_dict["nsfwLevel"] - 1
                        if img_nsfw_level < 0:
                            img_nsfw_level = 0

                    if img_nsfw_level < cur_nsfw_level:
                        cur_nsfw_level = img_nsfw_level
                        def_image = img_dict["url"]

                if not def_image:
                    def_image = version_info["images"][0]["url"]

                v['imageurl'] = def_image
                download_thumbnail_image(v['id'], v['imageurl'])

    # Merge changes back to shortcuts
    ISC = load()
    if ISC:
        ISC.update(preISC)
    else:
        ISC = preISC
    save(ISC)


def get_list(shortcut_types=None) -> str:
    """Get list of shortcut names."""
    ISC = load()
    if not ISC:
        return

    tmp_types = list()
    if shortcut_types:
        for sc_type in shortcut_types:
            try:
                tmp_types.append(setting.ui_typenames[sc_type])
            except Exception:
                pass

    shotcutlist = list()
    for k, v in ISC.items():
        if v:
            if tmp_types:
                if v['type'] in tmp_types:
                    shotcutlist.append(setting.set_shortcutname(v['name'], v['id']))
            else:
                shotcutlist.append(setting.set_shortcutname(v['name'], v['id']))

    return shotcutlist


def get_image_list(
    shortcut_types=None, search=None, shortcut_basemodels=None, shortcut_classification=None
) -> str:
    """Get filtered list of shortcut images."""
    ISC = load()
    if not ISC:
        return

    result_list = list()

    keys, tags, notes = util.get_search_keyword(search)

    # Classification filtering with AND operation
    if shortcut_classification:
        clfs_list = list()
        CISC = classification.load()
        if CISC:
            for name in shortcut_classification:
                name_list = classification.get_shortcut_list(CISC, name)
                if name_list:
                    if len(clfs_list) > 0:
                        clfs_list = list(set(clfs_list) & set(name_list))
                    else:
                        clfs_list = name_list
                else:
                    clfs_list = list()
                    break

            clfs_list = list(set(clfs_list))

        if len(clfs_list) > 0:
            for mid in clfs_list:
                if str(mid) in ISC.keys():
                    result_list.append(ISC[str(mid)])
    else:
        result_list = ISC.values()

    # Type filtering
    tmp_types = list()
    if shortcut_types:
        for sc_type in shortcut_types:
            try:
                tmp_types.append(setting.ui_typenames[sc_type])
            except Exception:
                pass

    if tmp_types:
        result_list = [v for v in result_list if v['type'] in tmp_types]

    # Keyword filtering
    if keys:
        key_list = list()
        for v in result_list:
            if v:
                for key in keys:
                    if key in v['name'].lower():
                        key_list.append(v)
                        break
        result_list = key_list

    # Tag filtering
    if tags:
        tags_list = list()
        for v in result_list:
            if v:
                if "tags" not in v.keys():
                    continue
                v_tags = [tag.lower() for tag in v["tags"]]
                common_tags = set(v_tags) & set(tags)
                if common_tags:
                    tags_list.append(v)
        result_list = tags_list

    # Note filtering
    if notes:
        note_list = list()
        for v in result_list:
            if v:
                if "note" not in v.keys():
                    continue

                if not v['note']:
                    continue

                for note in notes:
                    if note in v['note'].lower():
                        note_list.append(v)
                        break
        result_list = note_list

    # Base model filtering
    tmp_basemodels = list()
    if shortcut_basemodels:
        tmp_basemodels.extend(shortcut_basemodels)
        result_list = [v for v in result_list if is_baseModel(str(v['id']), tmp_basemodels)]

    return result_list


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


def add(ISC: dict, model_id, register_information_only=False, progress=None) -> dict:
    """
    Add a model to shortcuts.

    This function delegates to ModelFactory for the actual implementation.
    """
    if not model_id:
        return ISC

    if not ISC:
        ISC = dict()

    # Use ModelFactory to create the shortcut
    new_shortcuts = _model_factory.create_model_shortcut(
        str(model_id), register_information_only, progress
    )

    if new_shortcuts and str(model_id) in new_shortcuts:
        ISC.update(new_shortcuts)

    return ISC


def delete(ISC: dict, model_id) -> dict:
    """Delete a model from shortcuts."""
    if not model_id:
        return ISC

    if not ISC:
        return ISC

    cis = ISC.pop(str(model_id), None)
    cis_to_file(cis)
    delete_thumbnail_image(model_id)
    delete_model_information(model_id)

    return ISC


def cis_to_file(cis):
    """Save shortcut to backup file."""
    if not cis:
        return

    if "name" in cis.keys() and 'id' in cis.keys():
        backup_cis(cis['name'], f"{civitai.Url_Page()}{cis['id']}")


def backup_cis(name, url):
    """Backup shortcut information."""
    if not name or not url:
        return

    backup_dict = None
    try:
        with open(setting.shortcut_civitai_internet_shortcut_url, 'r') as f:
            backup_dict = json.load(f)
    except Exception:
        backup_dict = dict()

    backup_dict[f"url={url}"] = name

    try:
        with open(setting.shortcut_civitai_internet_shortcut_url, 'w') as f:
            json.dump(backup_dict, f, indent=4)
    except Exception:
        logger.error("Error when writing file:" + setting.shortcut_civitai_internet_shortcut_url)
        pass


def save(ISC: dict):
    """Save shortcuts to file."""
    output = ""

    try:
        with open(setting.shortcut, 'w') as f:
            json.dump(ISC, f, indent=4)
    except Exception:
        logger.error("Error when writing file:" + setting.shortcut)
        return output

    output = "Civitai Internet Shortcut saved to: " + setting.shortcut
    return output


def load() -> dict:
    """Load shortcuts from file."""
    if not os.path.isfile(setting.shortcut):
        logger.debug("Unable to load the shortcut file. Starting with an empty file.")
        save({})
        return

    json_data = None
    try:
        with open(setting.shortcut, 'r') as f:
            json_data = json.load(f)
    except Exception:
        return None

    if not json_data:
        logger.debug("There are no registered shortcuts.")
        return None

    return json_data


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
