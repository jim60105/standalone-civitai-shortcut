"""
Download utility functions for file operations, metadata, and thumbnails.
"""

import os

from ..logging_config import get_logger
from ..http.client_manager import get_http_client
from .. import util, settings, civitai
from ..settings import config_manager
from .notifier import DownloadNotifier

logger = get_logger(__name__)


def add_number_to_duplicate_files(files: list) -> dict:
    """Generate unique filenames for duplicate entries keyed by identifier."""
    result: dict = {}
    used_names: set = set()

    for entry in files:
        if ":" not in entry:
            continue
        key, name = entry.split(":", 1)
        # Skip if key already processed
        if key in result:
            continue

        base, ext = os.path.splitext(name)
        new_name = name
        count = 1
        # Append number suffix until name is unique
        while new_name in used_names:
            new_name = f"{base} ({count}){ext}"
            count += 1

        result[key] = new_name
        used_names.add(new_name)
    return result


def get_save_base_name(version_info: dict) -> str:
    primary = civitai.get_primary_file_by_version_info(version_info)
    if primary:
        # support primary as dict or list of dicts
        entry = primary[0] if isinstance(primary, (list, tuple)) else primary
        name = entry.get("name")
        if name:
            return os.path.splitext(name)[0]
    return settings.generate_version_foldername(
        version_info.get("model", {}).get("name", ""),
        version_info.get("name", ""),
        version_info.get("id", None),
    )


def download_preview_image(filepath: str, version_info: dict) -> bool:
    """Download preview image for a version into filepath."""
    if not version_info:
        return False
    images = version_info.get("images") or []
    if not images:
        return False
    img_dict = images[0]
    img_url = img_dict.get("url")
    if not img_url:
        return False
    # adjust width if specified
    width = img_dict.get("width")
    if width:
        img_url = util.change_width_from_image_url(img_url, width)
    try:
        client = get_http_client()
        return client.download_file_with_resume(
            img_url,
            filepath,
            headers={"Authorization": f"Bearer {config_manager.get_setting('civitai_api_key')}"},
        )
    except Exception as e:
        logger.error(f"[downloader] Failed to download preview image: {e}")
        return False


def download_file_thread_async(
    file_name, version_id, ms_folder, vs_folder, vs_foldername, cs_foldername, ms_foldername
):
    """Download logic executed in a background thread."""
    if not file_name or not version_id:
        return

    vi = civitai.get_version_info_by_version_id(version_id)
    if not vi:
        DownloadNotifier.notify_complete(str(file_name), False, "Failed to get version info")
        return

    files = civitai.get_files_by_version_info(vi)
    folder = util.make_download_model_folder(
        vi, ms_folder, vs_folder, vs_foldername, cs_foldername, ms_foldername
    )
    if not folder:
        DownloadNotifier.notify_complete(str(file_name), False, "Failed to create download folder")
        return

    savefile_base = None
    dup = add_number_to_duplicate_files(file_name)
    info_files = vi.get("files") or []

    # Use DownloadManager for actual asynchronous download
    from .task_manager import DownloadManager

    download_manager = DownloadManager()

    for fid, fname in dup.items():
        file_info = next((f for f in info_files if str(f.get('id')) == str(fid)), None)
        file_size = file_info.get('sizeKB', 0) * 1024 if file_info else None

        # Send start notification (including file size)
        DownloadNotifier.notify_start(fname, file_size)

        url = files.get(str(fid), {}).get("downloadUrl")
        path = os.path.join(folder, fname)

        # Use DownloadManager for actual background download
        task_id = download_manager.start(url, path)
        logger.info(f"[downloader] Started background download: {task_id} for {fname}")

        # Record primary file base name
        if file_info and file_info.get('primary'):
            base, _ = os.path.splitext(fname)
            savefile_base = base

    # Handle version info and preview image (in background thread)
    if savefile_base:
        info_path = os.path.join(
            folder,
            f"{util.replace_filename(savefile_base)}{settings.INFO_SUFFIX}{settings.INFO_EXT}",
        )
        if civitai.write_version_info(info_path, vi):
            logger.info(f"[downloader] Wrote version info: {info_path}")

        preview_path = os.path.join(
            folder,
            f"{util.replace_filename(savefile_base)}"
            f"{settings.PREVIEW_IMAGE_SUFFIX}{settings.PREVIEW_IMAGE_EXT}",
        )
        if download_preview_image(preview_path, vi):
            logger.info(f"[downloader] Wrote preview image: {preview_path}")

        # Generate metadata for LoRa models
        if _is_lora_model(vi):
            metadata_path = os.path.join(folder, f"{util.replace_filename(savefile_base)}.json")
            if civitai.write_LoRa_metadata(metadata_path, vi):
                logger.info(f"[downloader] Wrote LoRa metadata: {metadata_path}")

        # Create shortcut thumbnail for downloaded model
        model_id = str(vi.get("modelId", ""))
        if model_id:
            _create_shortcut_for_downloaded_model(vi, savefile_base, folder, model_id)


def _is_lora_model(version_info: dict) -> bool:
    """Check if the model is a LoRa or LyCORIS model."""
    if not version_info or "model" not in version_info:
        return False

    model_type = version_info["model"].get("type", "").upper()
    return model_type in ["LORA", "LOCON", "LYCORIS"]


def _create_shortcut_for_downloaded_model(
    version_info: dict, model_filename: str, model_folder: str, model_id: str
):
    """Create shortcut thumbnail for downloaded model."""
    try:
        from ..ishortcut_core.image_processor import ImageProcessor

        # Try to create thumbnail from existing preview image
        preview_path = os.path.join(
            model_folder,
            f"{util.replace_filename(model_filename)}"
            f"{settings.PREVIEW_IMAGE_SUFFIX}{settings.PREVIEW_IMAGE_EXT}",
        )

        image_processor = ImageProcessor()

        # Try to create thumbnail from existing preview first
        if os.path.exists(preview_path):
            if not image_processor.create_thumbnail(model_id, preview_path):
                logger.debug(
                    f"[downloader] Failed to create thumbnail from preview for model {model_id}"
                )
            else:
                logger.info(f"[downloader] Created thumbnail from preview for model {model_id}")
                return True

        # If no preview image exists, try to download thumbnail directly
        images = version_info.get("images", [])
        if not images:
            logger.warning(f"[downloader] No images available for model {model_id}")
            return False

        preview_url = images[0].get("url")
        if not preview_url:
            logger.warning(f"[downloader] No preview URL available for model {model_id}")
            return False

        if not image_processor.download_thumbnail_image(model_id, preview_url):
            logger.warning(f"[downloader] Failed to download thumbnail for model {model_id}")
            return False

        logger.info(f"[downloader] Downloaded thumbnail for model {model_id}")
        return True

    except Exception as e:
        logger.error(f"[downloader] Error creating shortcut for downloaded model: {e}")
        return False
