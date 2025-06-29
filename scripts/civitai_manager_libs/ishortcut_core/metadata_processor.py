"""
MetadataProcessor: Handles data validation and metadata processing.

This module is responsible for:
- Validating model information structure
- Processing model metadata and descriptions
- Handling version information validation
- NSFW content filtering and validation
- Data consistency checks and error reporting

Extracted from ishortcut.py functions:
- Various validation checks within get_model_information()
- NSFW filtering logic
- Model info structure validation
- Version data validation
"""

import re
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

# Import dependencies from parent modules
from .. import setting
from ..logging_config import get_logger
from ..error_handler import with_error_handling
from ..exceptions import DataValidationError

logger = get_logger(__name__)


class MetadataProcessor:
    """Handles metadata processing and validation operations."""

    def __init__(self):
        """Initialize MetadataProcessor."""
        self.required_model_fields = ['id', 'name', 'type']
        self.required_version_fields = ['id', 'name', 'downloadUrl']

    @with_error_handling(
        fallback_value=False,
        exception_types=(DataValidationError,),
        retry_count=0,
        user_message="Failed to validate model information",
    )
    def validate_model_info(self, model_info: Dict) -> bool:
        """
        Validate the structure and content of model information.

        Args:
            model_info: Model information dictionary from API

        Returns:
            True if valid, False otherwise

        Raises:
            DataValidationError: If critical validation fails
        """
        if not model_info:
            logger.error("[MetadataProcessor] Model info is None or empty")
            raise DataValidationError("Model info is None or empty")

        # Check required fields
        missing_fields = []
        for field in self.required_model_fields:
            if field not in model_info:
                missing_fields.append(field)

        if missing_fields:
            error_msg = f"Missing required fields: {missing_fields}"
            logger.error(f"[MetadataProcessor] {error_msg}")
            raise DataValidationError(error_msg)

        # Validate model ID
        model_id = model_info.get('id')
        if not isinstance(model_id, (int, str)) or not str(model_id).strip():
            logger.error("[MetadataProcessor] Invalid model ID")
            raise DataValidationError("Invalid model ID")

        # Validate model name
        model_name = model_info.get('name')
        if not isinstance(model_name, str) or not model_name.strip():
            logger.error("[MetadataProcessor] Invalid model name")
            raise DataValidationError("Invalid model name")

        # Validate model type
        model_type = model_info.get('type')
        if not isinstance(model_type, str) or not model_type.strip():
            logger.error("[MetadataProcessor] Invalid model type")
            raise DataValidationError("Invalid model type")

        logger.debug(f"[MetadataProcessor] Model info validation passed for ID: {model_id}")
        return True

    @with_error_handling(
        fallback_value=False,
        exception_types=(DataValidationError,),
        retry_count=0,
        user_message="Failed to validate model versions",
    )
    def validate_model_versions(self, model_info: Dict) -> bool:
        """
        Validate model version information.

        Args:
            model_info: Model information containing versions

        Returns:
            True if versions are valid, False otherwise
        """
        if 'modelVersions' not in model_info:
            logger.warning("[MetadataProcessor] No modelVersions found")
            return True  # Not required, so consider valid

        versions = model_info['modelVersions']
        if not isinstance(versions, list):
            logger.error("[MetadataProcessor] modelVersions is not a list")
            raise DataValidationError("modelVersions is not a list")

        if not versions:
            logger.warning("[MetadataProcessor] Empty modelVersions list")
            return True  # Empty list is acceptable

        # Validate each version
        for idx, version in enumerate(versions):
            if not self._validate_single_version(version, idx):
                return False

        logger.debug(f"[MetadataProcessor] All {len(versions)} versions validated successfully")
        return True

    def _validate_single_version(self, version: Dict, index: int) -> bool:
        """
        Validate a single model version.

        Args:
            version: Version information dictionary
            index: Version index for error reporting

        Returns:
            True if version is valid, False otherwise
        """
        if not isinstance(version, dict):
            logger.error(f"[MetadataProcessor] Version {index} is not a dictionary")
            return False

        # Check required version fields
        missing_fields = []
        for field in self.required_version_fields:
            if field not in version:
                missing_fields.append(field)

        if missing_fields:
            logger.error(f"[MetadataProcessor] Version {index} missing fields: {missing_fields}")
            return False

        # Validate version ID
        version_id = version.get('id')
        if not isinstance(version_id, (int, str)) or not str(version_id).strip():
            logger.error(f"[MetadataProcessor] Version {index} has invalid ID")
            return False

        # Validate download URL
        download_url = version.get('downloadUrl')
        if not isinstance(download_url, str) or not download_url.strip():
            logger.error(f"[MetadataProcessor] Version {index} has invalid download URL")
            return False

        logger.debug(f"[MetadataProcessor] Version {index} (ID: {version_id}) validated")
        return True

    @with_error_handling(
        fallback_value=False,
        exception_types=(Exception,),
        retry_count=0,
        user_message="Failed to check NSFW content",
    )
    def is_nsfw_content(self, model_info: Dict) -> bool:
        """
        Check if model contains NSFW content.

        Args:
            model_info: Model information dictionary

        Returns:
            True if content is NSFW, False otherwise
        """
        try:
            # Check model-level NSFW flag
            if model_info.get('nsfw', False):
                logger.debug("[MetadataProcessor] Model marked as NSFW")
                return True

            # Check version-level NSFW content
            if 'modelVersions' in model_info:
                for version in model_info['modelVersions']:
                    if isinstance(version, dict) and 'images' in version:
                        for image in version['images']:
                            if isinstance(image, dict) and image.get('nsfw') == 'X':
                                logger.debug("[MetadataProcessor] Found NSFW image in version")
                                return True

            # Check tags for NSFW indicators
            tags = model_info.get('tags', [])
            if isinstance(tags, list):
                nsfw_tags = ['nsfw', 'adult', 'explicit', 'mature']
                for tag in tags:
                    if isinstance(tag, dict):
                        tag_name = tag.get('name', '').lower()
                    else:
                        tag_name = str(tag).lower()

                    if any(nsfw_tag in tag_name for nsfw_tag in nsfw_tags):
                        logger.debug(f"[MetadataProcessor] Found NSFW tag: {tag_name}")
                        return True

            logger.debug("[MetadataProcessor] No NSFW content detected")
            return False

        except Exception as e:
            logger.error(f"[MetadataProcessor] Error checking NSFW content: {e}")
            return False  # Default to safe content on error

    @with_error_handling(
        fallback_value="",
        exception_types=(Exception,),
        retry_count=0,
        user_message="Failed to extract model description",
    )
    def extract_model_description(self, model_info: Dict) -> str:
        """
        Extract and clean model description.

        Args:
            model_info: Model information dictionary

        Returns:
            Cleaned model description string
        """
        try:
            description = model_info.get('description', '')
            if not isinstance(description, str):
                return ""

            # Clean HTML tags if present
            description = self._clean_html_tags(description)

            # Truncate if too long
            default_max_length = 1000
            max_length = getattr(setting, 'max_description_length', default_max_length)
            if len(description) > max_length:
                description = description[:max_length] + "..."
                logger.debug(
                    f"[MetadataProcessor] Truncated description to {max_length} characters"
                )

            return description.strip()

        except Exception as e:
            logger.error(f"[MetadataProcessor] Error extracting description: {e}")
            return ""

    def _clean_html_tags(self, text: str) -> str:
        """
        Remove HTML tags from text.

        Args:
            text: Text that may contain HTML tags

        Returns:
            Text with HTML tags removed
        """
        if not text:
            return ""

        # Simple HTML tag removal
        clean_text = re.sub(r'<[^>]+>', '', text)

        # Clean up multiple whitespaces
        clean_text = re.sub(r'\s+', ' ', clean_text)

        return clean_text.strip()

    @with_error_handling(
        fallback_value={},
        exception_types=(Exception,),
        retry_count=0,
        user_message="Failed to extract model statistics",
    )
    def extract_model_stats(self, model_info: Dict) -> Dict[str, Any]:
        """
        Extract model statistics and metrics.

        Args:
            model_info: Model information dictionary

        Returns:
            Dictionary containing model statistics
        """
        stats = {
            'download_count': 0,
            'like_count': 0,
            'comment_count': 0,
            'rating': 0.0,
            'created_at': None,
            'updated_at': None,
        }

        try:
            # Extract basic statistics
            stats['download_count'] = model_info.get('downloadCount', 0)
            stats['like_count'] = model_info.get('thumbsUpCount', 0)
            stats['comment_count'] = model_info.get('commentCount', 0)

            # Extract rating
            rating_info = model_info.get('stats', {})
            if isinstance(rating_info, dict):
                stats['rating'] = rating_info.get('rating', 0.0)

            # Extract timestamps
            created_at = model_info.get('createdAt')
            if created_at:
                stats['created_at'] = self._parse_timestamp(created_at)

            updated_at = model_info.get('updatedAt')
            if updated_at:
                stats['updated_at'] = self._parse_timestamp(updated_at)

            logger.debug(f"[MetadataProcessor] Extracted stats: {stats}")
            return stats

        except Exception as e:
            logger.error(f"[MetadataProcessor] Error extracting stats: {e}")
            return stats

    def _parse_timestamp(self, timestamp: Union[str, datetime]) -> Optional[str]:
        """
        Parse timestamp to standardized format.

        Args:
            timestamp: Timestamp string or datetime object

        Returns:
            Formatted timestamp string or None if parsing fails
        """
        try:
            if isinstance(timestamp, datetime):
                return timestamp.isoformat()

            if isinstance(timestamp, str):
                # Try common timestamp formats
                formats = [
                    '%Y-%m-%dT%H:%M:%S.%fZ',
                    '%Y-%m-%dT%H:%M:%SZ',
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d',
                ]

                for fmt in formats:
                    try:
                        dt = datetime.strptime(timestamp, fmt)
                        return dt.isoformat()
                    except ValueError:
                        continue

                # If no format matches, return as-is
                return timestamp

            return None

        except Exception as e:
            logger.error(f"[MetadataProcessor] Error parsing timestamp {timestamp}: {e}")
            return None

    @with_error_handling(
        fallback_value=[],
        exception_types=(Exception,),
        retry_count=0,
        user_message="Failed to extract model tags",
    )
    def extract_model_tags(self, model_info: Dict) -> List[str]:
        """
        Extract and normalize model tags.

        Args:
            model_info: Model information dictionary

        Returns:
            List of normalized tag strings
        """
        try:
            tags = model_info.get('tags', [])
            if not isinstance(tags, list):
                return []

            normalized_tags = []
            for tag in tags:
                if isinstance(tag, dict):
                    tag_name = tag.get('name', '')
                elif isinstance(tag, str):
                    tag_name = tag
                else:
                    continue

                if tag_name and isinstance(tag_name, str):
                    normalized_tag = tag_name.strip().lower()
                    if normalized_tag and normalized_tag not in normalized_tags:
                        normalized_tags.append(normalized_tag)

            logger.debug(f"[MetadataProcessor] Extracted {len(normalized_tags)} tags")
            return normalized_tags

        except Exception as e:
            logger.error(f"[MetadataProcessor] Error extracting tags: {e}")
            return []

    @with_error_handling(
        fallback_value={},
        exception_types=(Exception,),
        retry_count=0,
        user_message="Failed to process model metadata",
    )
    def process_model_metadata(self, model_info: Dict) -> Dict[str, Any]:
        """
        Process and extract comprehensive model metadata.

        Args:
            model_info: Raw model information from API

        Returns:
            Processed metadata dictionary
        """
        if not self.validate_model_info(model_info):
            logger.error("[MetadataProcessor] Model info validation failed")
            return {}

        metadata = {
            'id': model_info.get('id'),
            'name': model_info.get('name', ''),
            'type': model_info.get('type', ''),
            'description': self.extract_model_description(model_info),
            'stats': self.extract_model_stats(model_info),
            'tags': self.extract_model_tags(model_info),
            'is_nsfw': self.is_nsfw_content(model_info),
            'version_count': len(model_info.get('modelVersions', [])),
            'processed_at': datetime.now().isoformat(),
        }

        # Add creator information if available
        creator = model_info.get('creator', {})
        if isinstance(creator, dict):
            metadata['creator'] = {
                'username': creator.get('username', ''),
                'name': creator.get('name', ''),
            }

        logger.info(f"[MetadataProcessor] Processed metadata for model {metadata['id']}")
        return metadata

    @with_error_handling(
        fallback_value=False,
        exception_types=(Exception,),
        retry_count=0,
        user_message="Failed to validate processed metadata",
    )
    def validate_processed_metadata(self, metadata: Dict) -> bool:
        """
        Validate processed metadata for completeness and consistency.

        Args:
            metadata: Processed metadata dictionary

        Returns:
            True if metadata is valid and complete
        """
        required_keys = ['id', 'name', 'type', 'processed_at']

        for key in required_keys:
            if key not in metadata:
                logger.error(f"[MetadataProcessor] Missing required metadata key: {key}")
                return False

        # Validate ID
        if not metadata['id']:
            logger.error("[MetadataProcessor] Invalid metadata ID")
            return False

        # Validate name
        if not isinstance(metadata['name'], str) or not metadata['name'].strip():
            logger.error("[MetadataProcessor] Invalid metadata name")
            return False

        # Validate processed timestamp
        try:
            datetime.fromisoformat(metadata['processed_at'].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            logger.error("[MetadataProcessor] Invalid processed_at timestamp")
            return False

        logger.debug("[MetadataProcessor] Metadata validation passed")
        return True
