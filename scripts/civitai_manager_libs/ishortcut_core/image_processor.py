"""
Image Processor Module

Handles image operations including downloading, thumbnail creation,
and image file management for models.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
from ..logging_config import get_logger
from ..error_handler import with_error_handling

logger = get_logger(__name__)

# Configuration constants
THUMBNAIL_MAX_SIZE = (400, 400)


class ImageProcessor:
    """
    Handles image processing operations including downloads, thumbnail creation,
    and image file management for models.
    """

    def __init__(self):
        self.logger = logger
        self.thumbnail_max_size = THUMBNAIL_MAX_SIZE

    @with_error_handling(
        fallback_value=[],
        exception_types=(Exception,),
        retry_count=1,
        retry_delay=1.0,
        user_message="Failed to extract version images",
    )
    def extract_version_images(self, model_info: dict, modelid: str) -> List[Dict[str, Any]]:
        """
        Extract image information from model data.

        Args:
            model_info: Model information dictionary
            modelid: Model ID for reference

        Returns:
            List of image information dictionaries
        """
        if not model_info or 'modelVersions' not in model_info:
            return []

        version_list = []
        for version in model_info['modelVersions']:
            if 'images' in version and version['images']:
                processed_images = self._process_version_images(
                    version['images'], version.get('id', '')
                )
                version_data = {
                    'id': version.get('id', ''),
                    'name': version.get('name', ''),
                    'images': processed_images,
                }
                version_list.append(version_data)

        return version_list

    def _process_version_images(self, images: List[dict], version_id: str) -> List[Dict[str, Any]]:
        """
        Process individual version images.

        Args:
            images: List of image dictionaries
            version_id: Version ID for reference

        Returns:
            List of processed image information
        """
        processed_images = []
        for idx, image in enumerate(images):
            if not image.get('url'):
                continue

            processed_image = {
                'id': image.get('id', f"{version_id}_{idx}"),
                'url': image['url'],
                'nsfw': image.get('nsfw', False),
                'width': image.get('width', 0),
                'height': image.get('height', 0),
                'hash': image.get('hash', ''),
                'type': image.get('type', 'image'),
                'metadata': image.get('meta', {}),
                'version_id': version_id,
            }
            processed_images.append(processed_image)

        return processed_images

    @with_error_handling(
        fallback_value=False,
        exception_types=(Exception,),
        retry_count=2,
        retry_delay=1.0,
        user_message="Failed to create thumbnail",
    )
    def create_thumbnail(self, model_id: str, input_image_path: str) -> bool:
        """
        Create thumbnail from input image.

        Args:
            model_id: Model ID for thumbnail naming
            input_image_path: Path to source image

        Returns:
            True if thumbnail created successfully
        """
        from .. import setting  # Import here to avoid circular dependency

        try:
            if not os.path.exists(input_image_path):
                self.logger.error(f"Input image not found: {input_image_path}")
                return False

            # Create thumbnail directory
            thumbnail_dir = os.path.join(setting.shortcut_thumbnail_path, model_id)
            os.makedirs(thumbnail_dir, exist_ok=True)

            # Generate thumbnail filename
            thumbnail_filename = f"{model_id}_thumbnail.jpg"
            thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)

            # Create thumbnail
            with Image.open(input_image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')

                # Create thumbnail
                img.thumbnail(self.thumbnail_max_size, Image.Resampling.LANCZOS)
                img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)

            self.logger.info(f"Created thumbnail: {thumbnail_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create thumbnail for model {model_id}: {e}")
            return False

    def delete_thumbnail_image(self, model_id: str) -> bool:
        """
        Delete thumbnail image for model.

        Args:
            model_id: Model ID for thumbnail deletion

        Returns:
            True if deleted successfully
        """
        from .. import setting  # Import here to avoid circular dependency

        try:
            thumbnail_dir = os.path.join(setting.shortcut_thumbnail_path, model_id)

            if os.path.exists(thumbnail_dir):
                shutil.rmtree(thumbnail_dir)
                self.logger.info(f"Deleted thumbnail directory: {thumbnail_dir}")
                return True
            else:
                self.logger.warning(f"Thumbnail directory not found: {thumbnail_dir}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to delete thumbnail for model {model_id}: {e}")
            return False

    @with_error_handling(
        fallback_value=False,
        exception_types=(Exception,),
        retry_count=2,
        retry_delay=1.0,
        user_message="Failed to download thumbnail image",
    )
    def download_thumbnail_image(self, model_id: str, url: str) -> bool:
        """
        Download thumbnail image from URL.

        Args:
            model_id: Model ID for thumbnail naming
            url: URL to download image from

        Returns:
            True if downloaded successfully
        """
        from .. import setting  # Import here to avoid circular dependency
        from ..http_client import get_http_client

        try:
            # Create thumbnail directory
            thumbnail_dir = os.path.join(setting.shortcut_thumbnail_path, model_id)
            os.makedirs(thumbnail_dir, exist_ok=True)

            # Generate filename from URL
            filename = f"{model_id}_thumbnail.jpg"
            file_path = os.path.join(thumbnail_dir, filename)

            # Download image
            client = get_http_client()
            response = client.get(url, stream=True)
            response.raise_for_status()

            # Save image
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Create thumbnail from downloaded image
            return self.create_thumbnail(model_id, file_path)

        except Exception as e:
            self.logger.error(f"Failed to download thumbnail for model {model_id}: {e}")
            return False

    def is_sc_image(self, model_id: str) -> bool:
        """
        Check if shortcut image exists for model.

        Args:
            model_id: Model ID to check

        Returns:
            True if shortcut image exists
        """
        from .. import setting  # Import here to avoid circular dependency

        try:
            thumbnail_dir = os.path.join(setting.shortcut_thumbnail_path, model_id)
            if not os.path.exists(thumbnail_dir):
                return False

            # Check for common image file extensions
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            for ext in image_extensions:
                image_path = os.path.join(thumbnail_dir, f"{model_id}_thumbnail{ext}")
                if os.path.exists(image_path):
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Failed to check shortcut image for model {model_id}: {e}")
            return False

    def collect_images_to_download(
        self, version_list: List[dict], modelid: str
    ) -> List[Dict[str, Any]]:
        """
        Collect all images that need to be downloaded.

        Args:
            version_list: List of version data with images
            modelid: Model ID for reference

        Returns:
            List of images to download with metadata
        """
        from .. import setting  # Import here to avoid circular dependency

        all_images_to_download = []

        for version_data in version_list:
            version_id = version_data.get('id', '')
            images = version_data.get('images', [])

            for image in images:
                image_url = image.get('url', '')
                if not image_url:
                    continue

                # Generate filename
                image_id = image.get('id', f"{version_id}_{len(all_images_to_download)}")
                file_extension = self._get_image_extension(image_url)
                filename = f"{image_id}.{file_extension}"

                # Create file path
                image_dir = os.path.join(setting.shortcut_info_path, modelid, 'images')
                file_path = os.path.join(image_dir, filename)

                # Skip if file already exists
                if os.path.exists(file_path):
                    continue

                download_info = {
                    'url': image_url,
                    'file_path': file_path,
                    'filename': filename,
                    'image_id': image_id,
                    'version_id': version_id,
                    'model_id': modelid,
                    'nsfw': image.get('nsfw', False),
                    'width': image.get('width', 0),
                    'height': image.get('height', 0),
                    'metadata': image.get('metadata', {}),
                }
                all_images_to_download.append(download_info)

        return all_images_to_download

    def _get_image_extension(self, url: str) -> str:
        """
        Extract image file extension from URL.

        Args:
            url: Image URL

        Returns:
            File extension (default: 'jpg')
        """
        try:
            path = Path(url)
            extension = path.suffix.lstrip('.')
            if extension.lower() in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                return extension.lower()
            else:
                return 'jpg'  # Default extension
        except Exception:
            return 'jpg'

    def get_image_list(
        self,
        shortcut_types: Optional[List[str]] = None,
        base_models: Optional[List[str]] = None,
        sort_by: str = 'name',
        nsfw_filter: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Get list of images with filtering and sorting options.

        Args:
            shortcut_types: List of model types to include
            base_models: List of base models to include
            sort_by: Sort criteria ('name', 'date', 'rating')
            nsfw_filter: Whether to filter out NSFW content

        Returns:
            List of image information dictionaries
        """
        from .. import ishortcut  # Import here to avoid circular dependency
        from .. import setting

        try:
            shortcut_data = ishortcut.load()
            if not shortcut_data:
                return []

            image_list = []

            for model_id, model_data in shortcut_data.items():
                if not isinstance(model_data, dict):
                    continue

                # Apply type filter
                if shortcut_types and model_data.get('type') not in shortcut_types:
                    continue

                # Apply base model filter
                if base_models:
                    model_base = model_data.get('baseModel', '').lower()
                    if not any(base.lower() in model_base for base in base_models):
                        continue

                # Check for images
                image_dir = os.path.join(setting.shortcut_info_path, model_id, 'images')
                if not os.path.exists(image_dir):
                    continue

                # Collect image files
                image_files = []
                for filename in os.listdir(image_dir):
                    if filename.lower().endswith(
                        ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
                    ):
                        image_path = os.path.join(image_dir, filename)
                        image_info = {
                            'model_id': model_id,
                            'filename': filename,
                            'path': image_path,
                            'size': os.path.getsize(image_path),
                            'modified_time': os.path.getmtime(image_path),
                            'model_name': model_data.get('name', ''),
                            'model_type': model_data.get('type', ''),
                            'base_model': model_data.get('baseModel', ''),
                            'nsfw': model_data.get('nsfw', False),
                        }

                        # Apply NSFW filter
                        if nsfw_filter and image_info['nsfw']:
                            continue

                        image_files.append(image_info)

                image_list.extend(image_files)

            # Sort the list
            if sort_by == 'name':
                image_list.sort(key=lambda x: x['model_name'].lower())
            elif sort_by == 'date':
                image_list.sort(key=lambda x: x['modified_time'], reverse=True)
            elif sort_by == 'size':
                image_list.sort(key=lambda x: x['size'], reverse=True)

            return image_list

        except Exception as e:
            self.logger.error(f"Failed to get image list: {e}")
            return []

    def validate_image_file(self, file_path: str) -> bool:
        """
        Validate if file is a valid image.

        Args:
            file_path: Path to image file

        Returns:
            True if valid image file
        """
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception as e:
            self.logger.error(f"Invalid image file {file_path}: {e}")
            return False

    def get_image_dimensions(self, file_path: str) -> Tuple[int, int]:
        """
        Get image dimensions.

        Args:
            file_path: Path to image file

        Returns:
            Tuple of (width, height), (0, 0) if failed
        """
        try:
            with Image.open(file_path) as img:
                return img.size
        except Exception as e:
            self.logger.error(f"Failed to get image dimensions for {file_path}: {e}")
            return (0, 0)
