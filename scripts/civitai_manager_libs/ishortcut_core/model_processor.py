"""
ModelProcessor: Handles model information retrieval and API interactions.

This module is responsible for:
- Fetching model information from Civitai API
- Processing model versions and metadata
- Extracting model descriptions and details
- Managing model-related API calls

Extracted from ishortcut.py functions:
- get_model_information()
- get_version_description()
- get_version_description_gallery()
- get_model_info()
- get_version_info()
- get_version_images()
- get_latest_version_info_by_model_id()
- get_model_filenames()
- is_baseModel()
"""

import os
import json
from typing import Dict, List, Optional, Tuple

# Import dependencies from parent modules
from .. import settings
from .. import civitai
from ..logging_config import get_logger
from ..error_handler import with_error_handling
from ..exceptions import NetworkError, FileOperationError, CivitaiShortcutError

logger = get_logger(__name__)


class ModelProcessor:
    """Handles model information processing and API interactions."""

    def __init__(self):
        """Initialize ModelProcessor."""
        pass

    @with_error_handling(
        fallback_value=(None, None, None, None, None, None, None, None, None, None),
        exception_types=(NetworkError, FileOperationError, CivitaiShortcutError),
        retry_count=1,
        retry_delay=1.0,
        user_message="Failed to get model information",
    )
    def get_model_information(
        self, modelid: str = None, versionid: str = None, ver_index: int = None
    ) -> Tuple[
        Optional[Dict],
        Optional[Dict],
        Optional[str],
        Optional[str],
        Optional[str],
        Optional[str],
        Optional[List],
        Optional[str],
        Optional[str],
        Optional[List],
    ]:
        """
        Get comprehensive model information including versions and metadata.

        Args:
            modelid: Model ID to fetch information for
            versionid: Specific version ID (optional)
            ver_index: Version index to use (optional)

        Returns:
            Tuple containing model info, version info, version ID, version name,
            model type, base models, versions list, description HTML, trigger words, and files
        """
        logger.info(f"[ModelProcessor] Getting model information for modelid: {modelid}")

        if not modelid:
            logger.warning("[ModelProcessor] No modelid provided")
            return (None, None, None, None, None, None, None, None, None, None)

        model_info = self.get_model_info(modelid)
        if not model_info:
            logger.error(f"[ModelProcessor] Failed to get model info for {modelid}")
            return (None, None, None, None, None, None, None, None, None, None)

        version_info = self._get_version_info_from_model(model_info, versionid, ver_index)

        if not version_info:
            logger.warning(f"[ModelProcessor] No version info found for {modelid}")
            return (None, None, None, None, None, None, None, None, None, None)

        # Extract version details
        version_name = version_info.get("name")
        model_type = model_info.get('type')
        model_basemodels = version_info.get("baseModel")

        # Build versions list
        versions_list = []
        if "modelVersions" in model_info:
            versions_list = [ver.get('name', '') for ver in model_info['modelVersions']]

        # Get description and files
        dhtml, triger, files = self.get_version_description(version_info, model_info)

        logger.info(f"[ModelProcessor] Successfully processed model {modelid}")
        return (
            model_info,
            version_info,
            str(version_info.get('id', '')),
            version_name,
            model_type,
            model_basemodels,
            versions_list,
            dhtml,
            triger,
            files,
        )

    def _get_version_info_from_model(
        self, model_info: Dict, versionid: str = None, ver_index: int = None
    ) -> Optional[Dict]:
        """Extract version info from model data based on criteria."""
        if "modelVersions" not in model_info or not model_info["modelVersions"]:
            return None

        model_versions = model_info["modelVersions"]

        # If no specific version requested, return first (latest)
        if not versionid and ver_index is None:
            return model_versions[0]

        # Search by version ID
        if versionid:
            for ver in model_versions:
                if str(ver.get("id", "")) == str(versionid):
                    return ver

        # Use version index
        if ver_index is not None and 0 <= ver_index < len(model_versions):
            return model_versions[ver_index]

        return None

    @with_error_handling(
        fallback_value=("", None, None),
        exception_types=(Exception,),
        retry_count=0,
        user_message="Failed to get version description",
    )
    def get_version_description(
        self, version_info: Dict, model_info: Dict = None
    ) -> Tuple[str, Optional[str], List]:
        """
        Generate HTML description for model version.

        Args:
            version_info: Version information dictionary
            model_info: Model information dictionary

        Returns:
            Tuple of (HTML description, training words, files list)
        """
        if not version_info:
            return ("", None, [])

        model_id = version_info.get('modelId')
        if model_id and not model_info:
            model_info = self.get_model_info(str(model_id))

        if not model_info:
            return ("", None, [])

        logger.debug(
            f"[ModelProcessor] Generating description for version {version_info.get('id')}"
        )

        # Build HTML components
        html_parts = []
        training_words = None
        files = []

        # Model type
        model_type = model_info.get('type', 'Unknown')
        html_parts.append(f"<br><b>Type: {model_type}</b>")

        # Model link
        model_url = f"{civitai.Url_Page()}{model_id}"
        model_name = model_info.get('name', 'Unknown Model')
        html_parts.append(
            f'<br><b>Model: <a href="{model_url}" target="_blank">{model_name}</a></b>'
        )

        # Version details
        version_name = version_info.get('name', 'Unknown Version')
        base_model = version_info.get('baseModel', 'Unknown')
        html_parts.append(f"<br><b>Version: {version_name}</b>")

        # Creator
        creator = model_info.get('creator', {}).get('username', 'Unknown')
        html_parts.append(f"<br><b>Uploaded by:</b> {creator}")

        # Training words
        if 'trainedWords' in version_info and version_info['trainedWords']:
            training_words = ", ".join(version_info['trainedWords'])
            html_parts.append(f'<br><b>Training Tags:</b> {training_words}')

        # Base model info
        html_parts.append(f"<br><b>Description</b><br>BaseModel: {base_model}<br>")

        # Version description
        if version_info.get('description'):
            html_parts.append(f"<b>Version Description:</b><br>{version_info['description']}<br>")

        # Model tags
        if model_info.get('tags'):
            tags_html = "<br><b>Model Tags:</b>"
            for tag in model_info['tags']:
                tags_html += f"<b> [{tag}]</b>"
            html_parts.append(tags_html)

        # Model description
        if model_info.get('description'):
            html_parts.append(f"<br><b>Model Description:</b><br>{model_info['description']}<br>")

        # Download links and files
        if 'files' in version_info:
            for file_info in version_info['files']:
                files.append(file_info)
                download_url = file_info.get('downloadUrl', '')
                if download_url:
                    html_parts.append(f"<br><a href='{download_url}'><b>Download << Here</b></a>")

        # Homepage link
        html_parts.append(
            f'<br><b><a href="{model_url}" target="_blank">Civitai Homepage << Here</a></b><br>'
        )

        output_html = "".join(html_parts)
        logger.debug(f"[ModelProcessor] Generated description HTML ({len(output_html)} chars)")

        return output_html, training_words, files

    @with_error_handling(
        fallback_value=None,
        exception_types=(Exception,),
        retry_count=0,
        user_message="Failed to get version description for gallery",
    )
    def get_version_description_gallery(
        self, modelid: str, version_info: Dict
    ) -> Optional[List[str]]:
        """
        Get image URLs for gallery display with NSFW filtering.

        Args:
            modelid: Model ID
            version_info: Version information dictionary

        Returns:
            List of local image file paths for gallery display
        """
        if not modelid or not version_info:
            return None

        versionid = str(version_info.get('id', ''))
        if not versionid:
            return None

        version_images = version_info.get('images', [])
        if not version_images:
            return None

        logger.debug(f"[ModelProcessor] Processing {len(version_images)} images for gallery")

        images_url = []
        for img_dict in version_images:
            img_url = img_dict.get('url')
            if not img_url:
                continue

            # Get local image path
            description_img = settings.get_image_url_to_shortcut_file(modelid, versionid, img_url)

            # Apply NSFW filtering
            if settings.NSFW_filtering_enable:
                img_nsfw_level = self._get_image_nsfw_level(img_dict)
                user_nsfw_level = settings.NSFW_levels.index(settings.NSFW_level_user)

                if img_nsfw_level > user_nsfw_level:
                    description_img = settings.get_nsfw_disable_image

            # Check if file exists locally
            if os.path.isfile(description_img):
                images_url.append(description_img)

        logger.debug(f"[ModelProcessor] Found {len(images_url)} local images for gallery")
        return images_url if images_url else None

    def _get_image_nsfw_level(self, img_dict: Dict) -> int:
        """Get NSFW level for an image."""
        # Default to level 1 (safe)
        img_nsfw_level = 1

        # Check new format first
        if "nsfwLevel" in img_dict:
            img_nsfw_level = img_dict["nsfwLevel"] - 1
            if img_nsfw_level < 0:
                img_nsfw_level = 0
        # Fallback to old format
        elif "nsfw" in img_dict and img_dict["nsfw"] in settings.NSFW_levels:
            img_nsfw_level = settings.NSFW_levels.index(img_dict["nsfw"])

        return img_nsfw_level

    def get_model_info(self, modelid: str) -> Optional[Dict]:
        """
        Load model information from local storage.

        Args:
            modelid: Model ID to load

        Returns:
            Model information dictionary or None if not found
        """
        if not modelid:
            return None

        model_path = os.path.join(
            settings.shortcut_info_folder,
            modelid,
            f"{modelid}{settings.info_suffix}{settings.info_ext}",
        )

        try:
            with open(model_path, 'r', encoding='utf-8') as f:
                contents = json.load(f)

            if 'id' not in contents:
                logger.warning(f"[ModelProcessor] Model info missing ID: {model_path}")
                return None

            logger.debug(f"[ModelProcessor] Loaded model info for {modelid}")
            return contents

        except FileNotFoundError:
            logger.debug(f"[ModelProcessor] Model info not found: {model_path}")
            return None
        except Exception as e:
            logger.error(f"[ModelProcessor] Error loading model info {model_path}: {e}")
            return None

    def get_version_info(self, modelid: str, versionid: str) -> Optional[Dict]:
        """
        Get specific version information from model data.

        Args:
            modelid: Model ID
            versionid: Version ID to find

        Returns:
            Version information dictionary or None if not found
        """
        model_info = self.get_model_info(modelid)
        if not model_info or "modelVersions" not in model_info:
            return None

        for ver in model_info["modelVersions"]:
            if str(versionid) == str(ver.get("id", "")):
                logger.debug(f"[ModelProcessor] Found version {versionid} for model {modelid}")
                return ver

        logger.debug(f"[ModelProcessor] Version {versionid} not found for model {modelid}")
        return None

    def get_version_images(self, modelid: str, versionid: str) -> Optional[List]:
        """
        Get images for a specific model version.

        Args:
            modelid: Model ID
            versionid: Version ID

        Returns:
            List of image data or None if not found
        """
        version_info = self.get_version_info(modelid, versionid)
        if not version_info:
            return None

        images = version_info.get("images")
        if images:
            logger.debug(f"[ModelProcessor] Found {len(images)} images for version {versionid}")
        return images

    def get_latest_version_info_by_model_id(self, model_id: str) -> Optional[Dict]:
        """
        Get the latest version information for a model.

        Args:
            model_id: Model ID to get latest version for

        Returns:
            Latest version information dictionary or None
        """
        model_info = self.get_model_info(model_id)
        if not model_info or "modelVersions" not in model_info:
            return None

        model_versions = model_info["modelVersions"]
        if not model_versions:
            return None

        # First version is typically the latest
        latest_version = model_versions[0]
        if "id" not in latest_version:
            return None

        logger.debug(f"[ModelProcessor] Latest version for {model_id}: {latest_version.get('id')}")
        return latest_version

    def get_model_filenames(self, modelid: str) -> Optional[List[str]]:
        """
        Get all filenames available for a model across all versions.

        Args:
            modelid: Model ID to get filenames for

        Returns:
            List of filenames or None if model not found
        """
        model_info = self.get_model_info(modelid)
        if not model_info or "modelVersions" not in model_info:
            return None

        filenames = []
        for version in model_info["modelVersions"]:
            for file_info in version.get("files", []):
                filename = file_info.get("name")
                if filename:
                    filenames.append(filename)

        logger.debug(f"[ModelProcessor] Found {len(filenames)} files for model {modelid}")
        return filenames if filenames else None

    def is_baseModel(self, modelid: str, baseModels: List[str]) -> Optional[bool]:
        """
        Check if model uses any of the specified base models.

        Args:
            modelid: Model ID to check
            baseModels: List of base model names to match against

        Returns:
            True if model uses any specified base model, False otherwise, None if error
        """
        model_info = self.get_model_info(modelid)
        if not model_info or "modelVersions" not in model_info:
            return None

        for version in model_info["modelVersions"]:
            try:
                base_model = version.get("baseModel")
                if base_model and base_model in baseModels:
                    logger.debug(f"[ModelProcessor] Model {modelid} uses base model {base_model}")
                    return True
            except Exception as e:
                logger.debug(f"[ModelProcessor] Error checking base model for {modelid}: {e}")
                continue

        logger.debug(f"[ModelProcessor] Model {modelid} does not use specified base models")
        return False
