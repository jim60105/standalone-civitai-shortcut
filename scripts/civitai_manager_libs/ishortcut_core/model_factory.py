"""
ModelFactory: Handles model creation and shortcut generation.

This module is responsible for:
- Creating model shortcut objects
- Generating model file paths and directories
- Orchestrating the complete model information workflow
- Coordinating between different processors
- Managing the overall model creation pipeline

Extracted from ishortcut.py functions:
- Main orchestration logic from get_model_information()
- Model shortcut creation logic
- File path generation
- Workflow coordination
"""

from typing import Dict, Optional, Any, Callable
import os
import datetime

# Import dependencies from parent modules
from ..logging_config import get_logger
from ..error_handler import with_error_handling
from ..exceptions import CivitaiShortcutError, NetworkError, FileOperationError

# Import modular components
from .model_processor import ModelProcessor
from .file_processor import FileProcessor
from .image_processor import ImageProcessor
from .metadata_processor import MetadataProcessor
from .data_validator import DataValidator
from ..image_format_filter import ImageFormatFilter

logger = get_logger(__name__)


class ModelFactory:
    """Handles model creation and shortcut generation operations."""

    def __init__(self):
        """Initialize ModelFactory with component processors."""
        self.model_processor = ModelProcessor()
        self.file_processor = FileProcessor()
        self.image_processor = ImageProcessor()
        self.metadata_processor = MetadataProcessor()
        self.data_validator = DataValidator()

    @with_error_handling(
        fallback_value=None,
        exception_types=(CivitaiShortcutError, NetworkError, FileOperationError),
        retry_count=1,
        retry_delay=2.0,
        user_message="Failed to create model shortcut",
    )
    def create_model_shortcut(
        self,
        model_id: str,
        progress: Optional[Callable] = None,
        download_images: bool = True,
        validate_data: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Create a complete model shortcut with all components.

        Args:
            model_id: Model ID to create shortcut for
            progress: Progress callback for UI updates
            download_images: Whether to download model images
            validate_data: Whether to perform data validation

        Returns:
            Model shortcut information or None if failed
        """
        logger.info(f"[ModelFactory] Creating model shortcut for ID: {model_id}")

        # Extract model ID from URL if needed
        from ..util import get_model_id_from_url

        actual_model_id = get_model_id_from_url(str(model_id))
        if not actual_model_id:
            logger.error(f"[ModelFactory] Could not extract model ID from: {model_id}")
            return None

        logger.info(f"[ModelFactory] Extracted model ID: {actual_model_id}")

        # Validate input
        if validate_data and not self.data_validator.validate_model_id(actual_model_id):
            logger.error(f"[ModelFactory] Invalid model ID: {actual_model_id}")
            return None

        try:
            # Step 1: Get model information from API
            if progress is not None:
                progress(0.1, desc="Fetching model information...")

            # Import civitai module for API calls
            from .. import civitai

            model_info = civitai.get_model_info(actual_model_id)
            if not model_info:
                logger.error(f"[ModelFactory] Failed to fetch model info for {actual_model_id}")
                return None

            # Step 2: Validate model information
            if validate_data and not self.metadata_processor.validate_model_info(model_info):
                logger.error(f"[ModelFactory] Model info validation failed for {actual_model_id}")
                return None

            # Step 3: Process metadata
            if progress is not None:
                progress(0.2, desc="Processing metadata...")

            metadata = self.metadata_processor.process_model_metadata(model_info)
            if not metadata:
                logger.error(f"[ModelFactory] Metadata processing failed for {actual_model_id}")
                return None

            # Step 4: Create model directory structure
            if progress is not None:
                progress(0.3, desc="Creating directories...")

            model_dir = self.file_processor.create_model_directory(actual_model_id)
            if not model_dir:
                logger.error(f"[ModelFactory] Failed to create directory for {actual_model_id}")
                return None

            # Step 5: Save model information
            if progress is not None:
                progress(0.4, desc="Saving model information...")

            info_saved = self.file_processor.save_model_information(
                model_info, model_dir, actual_model_id
            )
            if not info_saved:
                logger.error(f"[ModelFactory] Failed to save model info for {actual_model_id}")
                return None

            # Step 6: Download images (if requested)
            if download_images:
                if progress is not None:
                    progress(0.5, desc="Downloading images...")

                image_success = self._download_model_images(model_info, actual_model_id, progress)
                if not image_success:
                    logger.warning(f"[ModelFactory] Image download failed for {model_id}")
                    # Continue despite image download failure
            else:
                logger.info(f"[ModelFactory] Skipping image download for {model_id}")

            # Step 7: Generate thumbnail
            if progress is not None:
                progress(0.8, desc="Generating thumbnail...")

            thumbnail_created = self._create_model_thumbnail(model_info, actual_model_id)
            if not thumbnail_created:
                logger.warning(f"[ModelFactory] Thumbnail creation failed for {model_id}")
                # Continue despite thumbnail failure

            # Step 8: Create final shortcut object
            if progress is not None:
                progress(0.9, desc="Creating shortcut...")

            shortcut = self._create_shortcut_object(model_info, metadata, model_dir)
            if not shortcut:
                logger.error(
                    f"[ModelFactory] Failed to create shortcut object for {actual_model_id}"
                )
                return None

            # Step 9: Final validation
            if validate_data and not self._validate_final_shortcut(shortcut):
                logger.error(
                    f"[ModelFactory] Final shortcut validation failed for {actual_model_id}"
                )
                return None

            if progress is not None:
                progress(1.0, desc="Complete!")

            logger.info(f"[ModelFactory] Successfully created model shortcut for {actual_model_id}")
            return shortcut

        except Exception as e:
            logger.error(f"[ModelFactory] Error creating model shortcut for {actual_model_id}: {e}")
            return None

    def _download_model_images(
        self, model_info: Dict, model_id: str, progress: Optional[Callable] = None
    ) -> bool:
        """
        Download model images with progress tracking.

        Args:
            model_info: Model information containing image data
            model_id: Model ID for logging
            progress: Progress callback

        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract version images
            version_list = self.image_processor.extract_version_images(model_info, model_id)

            if not version_list:
                logger.info(f"[ModelFactory] No images to download for {model_id}")
                return True

            # Create progress wrapper for image downloads
            def image_progress(fraction, desc="Downloading images..."):
                if progress is not None:
                    # Map image progress to overall progress (0.5-0.7 range)
                    overall_progress = 0.5 + (fraction * 0.2)
                    progress(overall_progress, desc=desc)

            # Download images
            success = self.image_processor.download_model_images(
                version_list, model_id, image_progress
            )

            if success:
                logger.info(f"[ModelFactory] Images downloaded successfully for {model_id}")
            else:
                logger.warning(f"[ModelFactory] Some images failed to download for {model_id}")

            return success

        except Exception as e:
            logger.error(f"[ModelFactory] Error downloading images for {model_id}: {e}")
            return False

    def _create_model_thumbnail(self, model_info: Dict, model_id: str) -> bool:
        """
        Create thumbnail for the model.

        Args:
            model_info: Model information
            model_id: Model ID

        Returns:
            True if successful, False otherwise
        """
        try:
            # Try to get preview image path
            preview_path = self.image_processor.get_preview_image_by_model_info(model_info)

            if preview_path and os.path.exists(preview_path):
                # Create thumbnail from existing preview
                success = self.image_processor.create_thumbnail(model_id, preview_path)
                if success:
                    logger.info(f"[ModelFactory] Thumbnail created from preview for {model_id}")
                    return True

            # Try to download and create thumbnail
            preview_url = self.image_processor.get_preview_image_url(model_info)
            if preview_url:
                success = self.image_processor.download_thumbnail_image(model_id, preview_url)
                if success:
                    logger.info(f"[ModelFactory] Thumbnail downloaded for {model_id}")
                    return True

            logger.warning(f"[ModelFactory] No thumbnail could be created for {model_id}")
            return False

        except Exception as e:
            logger.error(f"[ModelFactory] Error creating thumbnail for {model_id}: {e}")
            return False

    def _create_shortcut_object(
        self, model_info: Dict, metadata: Dict, model_dir: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create the final shortcut object.

        Args:
            model_info: Raw model information
            metadata: Processed metadata
            model_dir: Model directory path

        Returns:
            Shortcut object dictionary or None if failed
        """
        try:
            model_id = str(model_info.get('id'))

            # Create shortcut structure in the expected format
            shortcut = {
                'id': int(model_id),  # Should be integer in the shortcut format
                'type': metadata.get('type', ''),
                'name': metadata.get('name', ''),
                'tags': metadata.get('tags', []),
                'nsfw': metadata.get('is_nsfw', False),
                'url': f"https://civitai.com/api/v1/models/{model_id}",
                'note': '',  # Default empty note
                'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            # Add version information from first version
            model_versions = model_info.get('modelVersions', [])
            if isinstance(model_versions, list) and len(model_versions) > 0:
                try:
                    first_version = model_versions[0]
                    if isinstance(first_version, dict):
                        shortcut['versionid'] = first_version.get('id', '')
                        # Get preview image URL from first version
                        version_images = first_version.get('images', [])
                        if version_images and len(version_images) > 0:
                            # Pick the first static image from version images
                            static_url = ''
                            for img_item in version_images:
                                if isinstance(
                                    img_item, dict
                                ) and ImageFormatFilter.is_static_image_dict(img_item):
                                    static_url = img_item.get('url', '')
                                    break
                            shortcut['imageurl'] = static_url
                        else:
                            shortcut['imageurl'] = ''
                    else:
                        # Invalid version format, set defaults
                        shortcut['versionid'] = ''
                        shortcut['imageurl'] = ''
                except (IndexError, TypeError, AttributeError):
                    # Handle any unexpected errors in accessing version data
                    logger.warning(f"[ModelFactory] Error accessing version data for {model_id}")
                    shortcut['versionid'] = ''
                    shortcut['imageurl'] = ''
            else:
                # No versions available, set defaults
                shortcut['versionid'] = ''
                shortcut['imageurl'] = ''

            logger.debug(f"[ModelFactory] Created shortcut object for {model_id}")
            return shortcut

        except Exception as e:
            logger.error(f"[ModelFactory] Error creating shortcut object: {e}")
            return None

    def _count_model_images(self, model_info: Dict) -> int:
        """
        Count total images across all model versions.

        Args:
            model_info: Model information

        Returns:
            Total image count
        """
        try:
            total_images = 0

            if 'modelVersions' in model_info:
                for version in model_info['modelVersions']:
                    if 'images' in version and isinstance(version['images'], list):
                        total_images += len(version['images'])

            return total_images

        except Exception:
            return 0

    def _validate_final_shortcut(self, shortcut: Dict) -> bool:
        """
        Validate the final shortcut object.

        Args:
            shortcut: Shortcut object to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            required_keys = ['id', 'name', 'type']

            for key in required_keys:
                if key not in shortcut:
                    logger.error(f"[ModelFactory] Missing required key: {key}")
                    return False

            # Validate ID
            if not self.data_validator.validate_model_id(str(shortcut['id'])):
                return False

            logger.debug("[ModelFactory] Final shortcut validation passed")
            return True

        except Exception as e:
            logger.error(f"[ModelFactory] Error validating final shortcut: {e}")
            return False

    @with_error_handling(
        fallback_value=[],
        exception_types=(Exception,),
        retry_count=0,
        user_message="Failed to create batch shortcuts",
    )
    def create_batch_shortcuts(
        self,
        model_ids: list,
        progress: Optional[Callable] = None,
        download_images: bool = True,
        validate_data: bool = True,
    ) -> list:
        """
        Create shortcuts for multiple models.

        Args:
            model_ids: List of model IDs to process
            progress: Progress callback for UI updates
            download_images: Whether to download images
            validate_data: Whether to validate data

        Returns:
            List of created shortcuts
        """
        logger.info(f"[ModelFactory] Creating batch shortcuts for {len(model_ids)} models")
        shortcuts = []

        for i, model_id in enumerate(model_ids):
            if progress is not None:
                overall_progress = i / len(model_ids)
                progress(overall_progress, desc=f"Processing model {i+1}/{len(model_ids)}")

            shortcut = self.create_model_shortcut(
                model_id,
                progress=None,  # Don't pass progress to individual calls
                download_images=download_images,
                validate_data=validate_data,
            )

            if shortcut:
                shortcuts.append(shortcut)
                logger.info(f"[ModelFactory] Created shortcut {i+1}/{len(model_ids)}")
            else:
                logger.error(f"[ModelFactory] Failed to create shortcut for {model_id}")

        if progress is not None:
            progress(1.0, desc=f"Complete! Created {len(shortcuts)}/{len(model_ids)} shortcuts")

        logger.info(f"[ModelFactory] Batch creation complete: {len(shortcuts)}/{len(model_ids)}")
        return shortcuts

    def update_existing_shortcut(
        self, model_id: str, force_update: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing model shortcut.

        Args:
            model_id: Model ID to update
            force_update: Whether to force update even if recent

        Returns:
            Updated shortcut or None if failed
        """
        logger.info(f"[ModelFactory] Updating existing shortcut for {model_id}")

        try:
            # Check if shortcut exists and needs update
            existing_info = self.file_processor.load_model_information(model_id)
            if not existing_info and not force_update:
                logger.info(f"[ModelFactory] No existing shortcut found for {model_id}")
                return self.create_model_shortcut(model_id)

            # Get fresh model information
            from .. import civitai

            fresh_info = civitai.get_model_info(model_id)
            if not fresh_info:
                logger.error(f"[ModelFactory] Failed to get fresh info for {model_id}")
                return None

            # Check if update is needed
            if not force_update and existing_info:
                if self._is_update_needed(existing_info, fresh_info):
                    logger.info(f"[ModelFactory] Update needed for {model_id}")
                else:
                    logger.info(f"[ModelFactory] No update needed for {model_id}")
                    return existing_info

            # Perform update
            return self.create_model_shortcut(model_id, download_images=True, validate_data=True)

        except Exception as e:
            logger.error(f"[ModelFactory] Error updating shortcut for {model_id}: {e}")
            return None

    def _is_update_needed(self, existing_info: Dict, fresh_info: Dict) -> bool:
        """
        Check if shortcut needs updating based on version changes.

        Args:
            existing_info: Existing model information
            fresh_info: Fresh model information from API

        Returns:
            True if update is needed
        """
        try:
            # Check version count changes
            existing_versions = len(existing_info.get('modelVersions', []))
            fresh_versions = len(fresh_info.get('modelVersions', []))

            if existing_versions != fresh_versions:
                logger.info("[ModelFactory] Version count changed, update needed")
                return True

            # Check for modified dates (if available)
            existing_updated = existing_info.get('updatedAt')
            fresh_updated = fresh_info.get('updatedAt')

            if existing_updated != fresh_updated:
                logger.info("[ModelFactory] Update timestamp changed, update needed")
                return True

            return False

        except Exception as e:
            logger.error(f"[ModelFactory] Error checking update necessity: {e}")
            return True  # Default to updating on error
