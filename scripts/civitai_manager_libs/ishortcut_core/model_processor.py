"""
Model Processor Module

Handles model data processing, information extraction, and model-related operations.
Contains the core business logic for processing model information from Civitai API.
"""

from typing import Any, List, Tuple
from ..logging_config import get_logger
from ..error_handler import with_error_handling
from ..exceptions import NetworkError, FileOperationError, CivitaiShortcutError

logger = get_logger(__name__)


class ModelProcessor:
    """
    Handles core model processing operations including data extraction,
    validation, and transformation of model information.
    """

    def __init__(self):
        self.logger = logger

    @with_error_handling(
        fallback_value=(None, None, None, None, None, None, None, None, None, None),
        exception_types=(NetworkError, FileOperationError, CivitaiShortcutError),
        retry_count=1,
        retry_delay=1.0,
        user_message="Failed to get model information",
    )
    def get_model_information(
        self, modelid: str = None, versionid: str = None, ver_index: int = None
    ) -> Tuple[Any, ...]:
        """
        Get comprehensive model information including version details.

        Args:
            modelid: Model ID to retrieve information for
            versionid: Specific version ID (optional)
            ver_index: Version index if versionid not provided (optional)

        Returns:
            Tuple containing model info, version info, and related data
        """
        from .. import ishortcut  # Import here to avoid circular dependency

        model_info = None
        version_info = None

        if modelid:
            model_info = ishortcut.get_model_info(modelid)
            version_info = dict()
            if model_info:
                if not versionid and not ver_index:
                    if "modelVersions" in model_info.keys():
                        version_info = model_info["modelVersions"][0]
                        if version_info["id"]:
                            versionid = version_info["id"]
                elif versionid:
                    if "modelVersions" in model_info.keys():
                        for ver in model_info["modelVersions"]:
                            if versionid == ver["id"]:
                                version_info = ver
                else:
                    if "modelVersions" in model_info.keys():
                        if len(model_info["modelVersions"]) > 0:
                            version_info = model_info["modelVersions"][ver_index]
                            if version_info["id"]:
                                versionid = version_info["id"]

        if model_info and version_info:
            version_name = version_info["name"]
            model_type = model_info['type']
            model_basemodels = version_info["baseModel"]
            versions_list = list()
            for ver in model_info['modelVersions']:
                versions_list.append(ver['name'])

            from .metadata_processor import MetadataProcessor

            metadata_processor = MetadataProcessor()
            dhtml, triger, files = metadata_processor.get_version_description(
                version_info, model_info
            )

            return (
                model_info,
                version_info,
                versionid,
                version_name,
                model_type,
                model_basemodels,
                versions_list,
                dhtml,
                triger,
                files,
            )
        return None, None, None, None, None, None, None, None, None, None

    def extract_model_info(self, model_data: dict) -> dict:
        """
        Extract relevant model information from raw API data.

        Args:
            model_data: Raw model data from API

        Returns:
            Processed model information dictionary
        """
        if not model_data:
            return {}

        extracted_info = {
            'id': model_data.get('id'),
            'name': model_data.get('name'),
            'description': model_data.get('description'),
            'type': model_data.get('type'),
            'tags': model_data.get('tags', []),
            'creator': model_data.get('creator', {}),
            'stats': model_data.get('stats', {}),
            'modelVersions': self._process_model_versions(model_data.get('modelVersions', [])),
        }

        return extracted_info

    def _process_model_versions(self, versions: List[dict]) -> List[dict]:
        """
        Process model versions data.

        Args:
            versions: List of version dictionaries

        Returns:
            Processed versions list
        """
        processed_versions = []
        for version in versions:
            processed_version = {
                'id': version.get('id'),
                'name': version.get('name'),
                'baseModel': version.get('baseModel'),
                'description': version.get('description'),
                'downloadUrl': version.get('downloadUrl'),
                'files': version.get('files', []),
                'images': version.get('images', []),
                'stats': version.get('stats', {}),
                'createdAt': version.get('createdAt'),
                'updatedAt': version.get('updatedAt'),
            }
            processed_versions.append(processed_version)

        return processed_versions

    def validate_model_data(self, model_data: dict) -> bool:
        """
        Validate model data structure and required fields.

        Args:
            model_data: Model data to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(model_data, dict):
            return False

        required_fields = ['id', 'name', 'type']
        for field in required_fields:
            if field not in model_data:
                self.logger.warning(f"Missing required field: {field}")
                return False

        return True

    def get_latest_version_info_by_model_id(self, model_id: str) -> dict:
        """
        Get the latest version information for a given model ID.

        Args:
            model_id: The model ID to get version info for

        Returns:
            Latest version information dictionary
        """
        from .. import ishortcut  # Import here to avoid circular dependency

        try:
            model_info = ishortcut.get_model_info(model_id)
            if not model_info or 'modelVersions' not in model_info:
                return {}

            versions = model_info['modelVersions']
            if not versions:
                return {}

            # Return the first version (should be the latest)
            return versions[0]

        except Exception as e:
            self.logger.error(f"Failed to get latest version info for model {model_id}: {e}")
            return {}

    def get_model_filenames(self, modelid: str) -> List[str]:
        """
        Get list of filenames for a given model.

        Args:
            modelid: Model ID to get filenames for

        Returns:
            List of filenames
        """
        from .. import ishortcut  # Import here to avoid circular dependency

        try:
            model_info = ishortcut.get_model_info(modelid)
            if not model_info or 'modelVersions' not in model_info:
                return []

            filenames = []
            for version in model_info['modelVersions']:
                if 'files' in version:
                    for file_info in version['files']:
                        if 'name' in file_info:
                            filenames.append(file_info['name'])

            return filenames

        except Exception as e:
            self.logger.error(f"Failed to get filenames for model {modelid}: {e}")
            return []

    def is_baseModel(self, modelid: str, baseModels: List[str]) -> bool:
        """
        Check if model matches any of the specified base models.

        Args:
            modelid: Model ID to check
            baseModels: List of base model names to match against

        Returns:
            True if model matches any base model, False otherwise
        """
        try:
            latest_version = self.get_latest_version_info_by_model_id(modelid)
            if not latest_version:
                return False

            model_base = latest_version.get('baseModel', '').lower()
            return any(base.lower() in model_base for base in baseModels)

        except Exception as e:
            self.logger.error(f"Failed to check base model for {modelid}: {e}")
            return False
