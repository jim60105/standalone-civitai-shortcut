"""
Model Factory Module

Factory classes for creating and managing model objects and data structures.
"""

from typing import Any, List
from ..logging_config import get_logger

logger = get_logger(__name__)


class ModelFactory:
    """
    Factory class for creating model objects and data structures.
    """

    def __init__(self):
        self.logger = logger

    def create_model_data_structure(self, model_info: dict) -> dict:
        """
        Create standardized model data structure.

        Args:
            model_info: Raw model information

        Returns:
            Standardized model data structure
        """
        if not model_info:
            return {}

        return {
            'id': str(model_info.get('id', '')),
            'name': model_info.get('name', ''),
            'description': model_info.get('description', ''),
            'type': model_info.get('type', ''),
            'baseModel': self._extract_base_model(model_info),
            'tags': model_info.get('tags', []),
            'nsfw': model_info.get('nsfw', False),
            'creator': self._create_creator_info(model_info.get('creator', {})),
            'stats': self._create_stats_info(model_info.get('stats', {})),
            'versions': self._create_versions_list(model_info.get('modelVersions', [])),
            'license': model_info.get('allowCommercialUse', 'Unknown'),
            'createdAt': model_info.get('createdAt', ''),
            'updatedAt': model_info.get('updatedAt', ''),
            'metadata': {'processed_at': self._get_current_timestamp(), 'source': 'civitai_api'},
        }

    def _extract_base_model(self, model_info: dict) -> str:
        """
        Extract base model from model information.

        Args:
            model_info: Model information dictionary

        Returns:
            Base model string
        """
        # Try to get from first version
        if 'modelVersions' in model_info and model_info['modelVersions']:
            first_version = model_info['modelVersions'][0]
            return first_version.get('baseModel', '')

        return model_info.get('baseModel', '')

    def _create_creator_info(self, creator_data: dict) -> dict:
        """
        Create standardized creator information.

        Args:
            creator_data: Raw creator data

        Returns:
            Standardized creator information
        """
        return {
            'username': creator_data.get('username', ''),
            'image': creator_data.get('image', ''),
            'link': creator_data.get('link', ''),
        }

    def _create_stats_info(self, stats_data: dict) -> dict:
        """
        Create standardized statistics information.

        Args:
            stats_data: Raw stats data

        Returns:
            Standardized stats information
        """
        return {
            'downloadCount': stats_data.get('downloadCount', 0),
            'favoriteCount': stats_data.get('favoriteCount', 0),
            'commentCount': stats_data.get('commentCount', 0),
            'ratingCount': stats_data.get('ratingCount', 0),
            'rating': stats_data.get('rating', 0.0),
        }

    def _create_versions_list(self, versions_data: List[dict]) -> List[dict]:
        """
        Create standardized versions list.

        Args:
            versions_data: Raw versions data

        Returns:
            List of standardized version information
        """
        standardized_versions = []
        for version in versions_data:
            standardized_version = {
                'id': str(version.get('id', '')),
                'name': version.get('name', ''),
                'description': version.get('description', ''),
                'baseModel': version.get('baseModel', ''),
                'createdAt': version.get('createdAt', ''),
                'updatedAt': version.get('updatedAt', ''),
                'trainedWords': version.get('trainedWords', []),
                'files': self._create_files_list(version.get('files', [])),
                'images': self._create_images_list(version.get('images', [])),
                'stats': self._create_stats_info(version.get('stats', {})),
                'downloadUrl': version.get('downloadUrl', ''),
            }
            standardized_versions.append(standardized_version)

        return standardized_versions

    def _create_files_list(self, files_data: List[dict]) -> List[dict]:
        """
        Create standardized files list.

        Args:
            files_data: Raw files data

        Returns:
            List of standardized file information
        """
        standardized_files = []
        for file_data in files_data:
            standardized_file = {
                'id': str(file_data.get('id', '')),
                'name': file_data.get('name', ''),
                'type': file_data.get('type', ''),
                'sizeKB': file_data.get('sizeKB', 0),
                'primary': file_data.get('primary', False),
                'downloadUrl': file_data.get('downloadUrl', ''),
                'metadata': file_data.get('metadata', {}),
                'pickleScanResult': file_data.get('pickleScanResult', 'Unknown'),
                'virusScanResult': file_data.get('virusScanResult', 'Unknown'),
                'scannedAt': file_data.get('scannedAt', ''),
            }
            standardized_files.append(standardized_file)

        return standardized_files

    def _create_images_list(self, images_data: List[dict]) -> List[dict]:
        """
        Create standardized images list.

        Args:
            images_data: Raw images data

        Returns:
            List of standardized image information
        """
        standardized_images = []
        for image_data in images_data:
            standardized_image = {
                'id': str(image_data.get('id', '')),
                'url': image_data.get('url', ''),
                'nsfw': image_data.get('nsfw', False),
                'width': image_data.get('width', 0),
                'height': image_data.get('height', 0),
                'hash': image_data.get('hash', ''),
                'type': image_data.get('type', 'image'),
                'metadata': image_data.get('meta', {}),
            }
            standardized_images.append(standardized_image)

        return standardized_images

    def create_shortcut_entry(self, model_data: dict, additional_info: dict = None) -> dict:
        """
        Create shortcut entry for model data.

        Args:
            model_data: Standardized model data
            additional_info: Additional information to include

        Returns:
            Shortcut entry dictionary
        """
        shortcut_entry = {
            'id': model_data.get('id', ''),
            'name': model_data.get('name', ''),
            'type': model_data.get('type', ''),
            'baseModel': model_data.get('baseModel', ''),
            'description': model_data.get('description', ''),
            'tags': model_data.get('tags', []),
            'nsfw': model_data.get('nsfw', False),
            'creator': model_data.get('creator', {}),
            'stats': model_data.get('stats', {}),
            'license': model_data.get('license', 'Unknown'),
            'versions_count': len(model_data.get('versions', [])),
            'latest_version': self._get_latest_version_info(model_data.get('versions', [])),
            'created_at': model_data.get('createdAt', ''),
            'updated_at': model_data.get('updatedAt', ''),
            'shortcut_metadata': {
                'added_at': self._get_current_timestamp(),
                'last_updated': self._get_current_timestamp(),
                'note': additional_info.get('note', '') if additional_info else '',
                'classification': (
                    additional_info.get('classification', '') if additional_info else ''
                ),
            },
        }

        return shortcut_entry

    def _get_latest_version_info(self, versions: List[dict]) -> dict:
        """
        Get latest version information.

        Args:
            versions: List of version dictionaries

        Returns:
            Latest version information
        """
        if not versions:
            return {}

        # Assume first version is latest (as returned by API)
        latest = versions[0]
        return {
            'id': latest.get('id', ''),
            'name': latest.get('name', ''),
            'baseModel': latest.get('baseModel', ''),
            'createdAt': latest.get('createdAt', ''),
            'files_count': len(latest.get('files', [])),
            'images_count': len(latest.get('images', [])),
        }

    def create_download_task(
        self, model_data: dict, version_id: str = None, file_ids: List[str] = None
    ) -> dict:
        """
        Create download task structure.

        Args:
            model_data: Model data
            version_id: Specific version ID (optional)
            file_ids: Specific file IDs to download (optional)

        Returns:
            Download task structure
        """
        task = {
            'model_id': model_data.get('id', ''),
            'model_name': model_data.get('name', ''),
            'model_type': model_data.get('type', ''),
            'task_id': f"download_{model_data.get('id', '')}_{self._get_current_timestamp()}",
            'created_at': self._get_current_timestamp(),
            'status': 'pending',
            'downloads': [],
        }

        # Determine which version to download
        versions = model_data.get('versions', [])
        if not versions:
            return task

        target_version = None
        if version_id:
            target_version = next((v for v in versions if v.get('id') == version_id), None)
        else:
            target_version = versions[0]  # Latest version

        if not target_version:
            return task

        # Create download items
        files = target_version.get('files', [])
        for file_data in files:
            file_id = file_data.get('id', '')

            # Skip if specific files requested and this isn't one of them
            if file_ids and file_id not in file_ids:
                continue

            download_item = {
                'file_id': file_id,
                'filename': file_data.get('name', ''),
                'url': file_data.get('downloadUrl', ''),
                'size_kb': file_data.get('sizeKB', 0),
                'type': file_data.get('type', ''),
                'primary': file_data.get('primary', False),
                'status': 'pending',
            }
            task['downloads'].append(download_item)

        return task

    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp as ISO string.

        Returns:
            Current timestamp string
        """
        from datetime import datetime

        return datetime.now().isoformat()

    def create_error_response(self, error_message: str, error_code: str = None) -> dict:
        """
        Create standardized error response.

        Args:
            error_message: Error message
            error_code: Error code (optional)

        Returns:
            Error response dictionary
        """
        return {
            'success': False,
            'error': {
                'message': error_message,
                'code': error_code or 'UNKNOWN_ERROR',
                'timestamp': self._get_current_timestamp(),
            },
            'data': None,
        }

    def create_success_response(self, data: Any, message: str = None) -> dict:
        """
        Create standardized success response.

        Args:
            data: Response data
            message: Success message (optional)

        Returns:
            Success response dictionary
        """
        return {
            'success': True,
            'message': message or 'Operation completed successfully',
            'timestamp': self._get_current_timestamp(),
            'data': data,
        }

    def merge_model_data(self, existing_data: dict, new_data: dict) -> dict:
        """
        Merge existing model data with new data.

        Args:
            existing_data: Existing model data
            new_data: New model data to merge

        Returns:
            Merged model data
        """
        if not existing_data:
            return new_data

        if not new_data:
            return existing_data

        merged = existing_data.copy()

        # Update basic fields
        for key in ['name', 'description', 'type', 'baseModel', 'tags', 'nsfw']:
            if key in new_data:
                merged[key] = new_data[key]

        # Merge stats
        if 'stats' in new_data:
            if 'stats' not in merged:
                merged['stats'] = {}
            merged['stats'].update(new_data['stats'])

        # Update versions (replace with newer data)
        if 'versions' in new_data:
            merged['versions'] = new_data['versions']

        # Update timestamps
        merged['updated_at'] = self._get_current_timestamp()
        if 'metadata' not in merged:
            merged['metadata'] = {}
        merged['metadata']['last_updated'] = self._get_current_timestamp()

        return merged
