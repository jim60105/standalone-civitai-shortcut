"""
Metadata Processor Module

Handles metadata processing including version descriptions, tags extraction,
and data formatting for display purposes.
"""

from typing import Dict, Any, List, Tuple, Optional
from ..logging_config import get_logger
from ..error_handler import with_error_handling

logger = get_logger(__name__)


class MetadataProcessor:
    """
    Handles metadata processing operations including version descriptions,
    tags processing, and data formatting.
    """

    def __init__(self):
        self.logger = logger

    @with_error_handling(
        fallback_value=("", "", []),
        exception_types=(Exception,),
        retry_count=0,
        user_message="Failed to process version description",
    )
    def get_version_description(
        self, version_info: dict, model_info: dict = None
    ) -> Tuple[str, str, List]:
        """
        Process version description and generate HTML display format.

        Args:
            version_info: Version information dictionary
            model_info: Model information dictionary (optional)

        Returns:
            Tuple of (description_html, trigger_word, files_list)
        """
        if not version_info:
            return "", "", []

        # Extract description
        description = version_info.get('description', '')
        if not description and model_info:
            description = model_info.get('description', '')

        # Process trigger words
        trigger_words = self._extract_trigger_words(version_info, model_info)

        # Process files
        files = self._process_version_files(version_info)

        # Generate HTML description
        description_html = self._format_description_html(description, version_info, model_info)

        return description_html, trigger_words, files

    def _extract_trigger_words(self, version_info: dict, model_info: dict = None) -> str:
        """
        Extract trigger words from version or model information.

        Args:
            version_info: Version information
            model_info: Model information

        Returns:
            Comma-separated trigger words string
        """
        trigger_words = []

        # Check version info for trigger words
        if 'trainedWords' in version_info:
            trained_words = version_info['trainedWords']
            if isinstance(trained_words, list):
                trigger_words.extend(trained_words)
            elif isinstance(trained_words, str):
                trigger_words.append(trained_words)

        # Check model info for additional trigger words
        if model_info and 'tags' in model_info:
            tags = model_info['tags']
            if isinstance(tags, list):
                # Filter out non-trigger word tags
                relevant_tags = [tag for tag in tags if self._is_trigger_word_tag(tag)]
                trigger_words.extend(relevant_tags)

        return ', '.join(trigger_words) if trigger_words else ''

    def _is_trigger_word_tag(self, tag: str) -> bool:
        """
        Determine if a tag is likely a trigger word.

        Args:
            tag: Tag string to evaluate

        Returns:
            True if tag is likely a trigger word
        """
        # Simple heuristic - avoid very common or generic tags
        generic_tags = {
            'anime',
            'realistic',
            'female',
            'male',
            'character',
            'style',
            'concept',
            'celebrity',
            'clothing',
        }
        return tag.lower() not in generic_tags and len(tag) > 2

    def _process_version_files(self, version_info: dict) -> List[Dict[str, Any]]:
        """
        Process and format file information from version data.

        Args:
            version_info: Version information containing files

        Returns:
            List of processed file information dictionaries
        """
        files = []
        if 'files' not in version_info:
            return files

        for file_info in version_info['files']:
            processed_file = {
                'id': file_info.get('id'),
                'name': file_info.get('name', ''),
                'type': file_info.get('type', ''),
                'sizeKB': file_info.get('sizeKB', 0),
                'primary': file_info.get('primary', False),
                'downloadUrl': file_info.get('downloadUrl', ''),
                'pickleScanResult': file_info.get('pickleScanResult', 'Unknown'),
                'virusScanResult': file_info.get('virusScanResult', 'Unknown'),
                'scannedAt': file_info.get('scannedAt'),
                'metadata': file_info.get('metadata', {}),
            }
            files.append(processed_file)

        return files

    def _format_description_html(
        self, description: str, version_info: dict, model_info: dict = None
    ) -> str:
        """
        Format description as HTML for display.

        Args:
            description: Raw description text
            version_info: Version information
            model_info: Model information

        Returns:
            Formatted HTML description
        """
        if not description:
            description = "No description available."

        # Basic HTML formatting
        html_description = description.replace('\n', '<br>')

        # Add version-specific information
        version_name = version_info.get('name', '')
        if version_name:
            html_description = f"<h3>Version: {version_name}</h3>" + html_description

        # Add model type if available
        if model_info and 'type' in model_info:
            model_type = model_info['type']
            html_description = f"<p><strong>Type:</strong> {model_type}</p>" + html_description

        # Add base model information
        base_model = version_info.get('baseModel', '')
        if base_model:
            base_model_html = f"<p><strong>Base Model:</strong> {base_model}</p>"
            html_description = base_model_html + html_description

        return html_description

    def get_tags(self) -> List[str]:
        """
        Get available tags from stored shortcut data.

        Returns:
            List of available tags
        """
        from .. import ishortcut  # Import here to avoid circular dependency

        try:
            shortcut_data = ishortcut.load()
            if not shortcut_data:
                return []

            all_tags = set()
            for model_id, model_data in shortcut_data.items():
                if isinstance(model_data, dict) and 'tags' in model_data:
                    tags = model_data['tags']
                    if isinstance(tags, list):
                        all_tags.update(tags)
                    elif isinstance(tags, str):
                        all_tags.add(tags)

            return sorted(list(all_tags))

        except Exception as e:
            self.logger.error(f"Failed to get tags: {e}")
            return []

    @with_error_handling(
        fallback_value=None,
        exception_types=(Exception,),
        retry_count=0,
        user_message="Failed to get version description for gallery",
    )
    def get_version_description_gallery(
        self, modelid: str, version_info: dict
    ) -> Optional[Dict[str, Any]]:
        """
        Get version description specifically formatted for gallery display.

        Args:
            modelid: Model ID
            version_info: Version information

        Returns:
            Gallery-formatted version description
        """
        if not version_info:
            return None

        try:
            # Extract images for gallery
            ver_images = {}
            if 'images' in version_info:
                for idx, image in enumerate(version_info['images']):
                    image_key = f"{modelid}_{version_info.get('id', '')}_{idx}"
                    ver_images[image_key] = {
                        'url': image.get('url', ''),
                        'nsfw': image.get('nsfw', False),
                        'width': image.get('width', 0),
                        'height': image.get('height', 0),
                        'hash': image.get('hash', ''),
                        'meta': image.get('meta', {}),
                    }

            return {
                'images': ver_images,
                'version_id': version_info.get('id'),
                'version_name': version_info.get('name', ''),
                'description': version_info.get('description', ''),
                'base_model': version_info.get('baseModel', ''),
                'created_at': version_info.get('createdAt', ''),
                'download_count': version_info.get('stats', {}).get('downloadCount', 0),
            }

        except Exception as e:
            self.logger.error(f"Failed to process gallery description for model {modelid}: {e}")
            return None

    def extract_metadata(self, model_data: dict) -> dict:
        """
        Extract metadata from model data for indexing and search.

        Args:
            model_data: Raw model data

        Returns:
            Extracted metadata dictionary
        """
        if not model_data:
            return {}

        metadata = {
            'id': model_data.get('id'),
            'name': model_data.get('name', ''),
            'type': model_data.get('type', ''),
            'tags': model_data.get('tags', []),
            'nsfw': model_data.get('nsfw', False),
            'allowNoCredit': model_data.get('allowNoCredit', True),
            'allowCommercialUse': model_data.get('allowCommercialUse', 'Unknown'),
            'allowDerivatives': model_data.get('allowDerivatives', True),
            'allowDifferentLicense': model_data.get('allowDifferentLicense', True),
            'stats': {
                'downloadCount': model_data.get('stats', {}).get('downloadCount', 0),
                'favoriteCount': model_data.get('stats', {}).get('favoriteCount', 0),
                'commentCount': model_data.get('stats', {}).get('commentCount', 0),
                'ratingCount': model_data.get('stats', {}).get('ratingCount', 0),
                'rating': model_data.get('stats', {}).get('rating', 0),
            },
            'creator': {
                'username': model_data.get('creator', {}).get('username', ''),
                'image': model_data.get('creator', {}).get('image', ''),
            },
            'versions': [],
        }

        # Extract version metadata
        if 'modelVersions' in model_data:
            for version in model_data['modelVersions']:
                version_metadata = {
                    'id': version.get('id'),
                    'name': version.get('name', ''),
                    'baseModel': version.get('baseModel', ''),
                    'createdAt': version.get('createdAt', ''),
                    'downloadCount': version.get('stats', {}).get('downloadCount', 0),
                    'files_count': len(version.get('files', [])),
                    'images_count': len(version.get('images', [])),
                }
                metadata['versions'].append(version_metadata)

        return metadata

    def validate_metadata(self, metadata: dict) -> bool:
        """
        Validate metadata structure and content.

        Args:
            metadata: Metadata dictionary to validate

        Returns:
            True if metadata is valid, False otherwise
        """
        if not isinstance(metadata, dict):
            return False

        required_fields = ['id', 'name', 'type']
        for field in required_fields:
            if field not in metadata:
                self.logger.warning(f"Missing required metadata field: {field}")
                return False

        # Validate stats structure
        if 'stats' in metadata:
            stats = metadata['stats']
            if not isinstance(stats, dict):
                self.logger.warning("Stats field must be a dictionary")
                return False

        return True
