"""
Gallery Handlers Module

Handles gallery-specific UI events and interactions.
Manages gallery navigation, selection, and display operations.
"""

from typing import Any, Dict, List, Optional
from ..logging_config import get_logger
from ..error_handler import with_error_handling

logger = get_logger(__name__)


class GalleryHandlers:
    """
    Handles gallery-specific UI events and interactions.
    Manages gallery navigation, selection, and display operations.
    """

    def __init__(self, ui_controllers=None):
        """
        Initialize gallery handlers.

        Args:
            ui_controllers: UI controllers instance
        """
        self.ui_controllers = ui_controllers
        self._current_gallery = None
        self._selected_items = []
        self._gallery_cache = {}

    @with_error_handling("Failed to handle gallery selection")
    def on_gallery_select(self, selected_item: Any, gallery_type: str = 'default') -> bool:
        """
        Handle gallery item selection.

        Args:
            selected_item: Selected gallery item
            gallery_type: Type of gallery

        Returns:
            bool: True if successful, False otherwise
        """
        if selected_item is None:
            logger.debug("Gallery selection cleared")
            self._selected_items.clear()
            return True

        # Handle list input (gradio sometimes sends lists)
        if isinstance(selected_item, list):
            if len(selected_item) > 0:
                selected_item = selected_item[0]
            else:
                logger.debug("Empty list received for gallery selection")
                return True

        # Add to selected items
        if selected_item not in self._selected_items:
            self._selected_items.append(selected_item)

        # Update UI state
        if self.ui_controllers:
            self.ui_controllers.update_ui_state('selected_gallery_item', selected_item)
            self.ui_controllers.update_ui_state('gallery_type', gallery_type)

        logger.debug(f"Gallery item selected: {selected_item} (type: {gallery_type})")
        return True

    @with_error_handling("Failed to load gallery")
    def load_gallery(self, gallery_id: str, items: List[Any], cache: bool = True) -> bool:
        """
        Load gallery with items.

        Args:
            gallery_id: Gallery identifier
            items: List of gallery items
            cache: Whether to cache the gallery

        Returns:
            bool: True if successful, False otherwise
        """
        if cache:
            self._gallery_cache[gallery_id] = items.copy()

        self._current_gallery = gallery_id

        # Update UI state
        if self.ui_controllers:
            self.ui_controllers.update_ui_state('current_gallery', gallery_id)
            self.ui_controllers.update_ui_state('gallery_items', items)

        logger.info(f"Loaded gallery '{gallery_id}' with {len(items)} items")
        return True

    def get_current_gallery(self) -> Optional[str]:
        """
        Get current gallery ID.

        Returns:
            Optional[str]: Current gallery ID or None
        """
        return self._current_gallery

    def get_selected_items(self) -> List[Any]:
        """
        Get currently selected items.

        Returns:
            List[Any]: Selected items
        """
        return self._selected_items.copy()

    def clear_selection(self) -> None:
        """Clear all selected items."""
        self._selected_items.clear()
        if self.ui_controllers:
            self.ui_controllers.update_ui_state('selected_gallery_item', None)

    @with_error_handling("Failed to handle gallery navigation")
    def navigate_gallery(self, direction: str) -> bool:
        """
        Navigate gallery in specified direction.

        Args:
            direction: Navigation direction ('next', 'previous', 'first', 'last')

        Returns:
            bool: True if successful, False otherwise
        """
        if not self._current_gallery or self._current_gallery not in self._gallery_cache:
            logger.warning("No current gallery for navigation")
            return False

        items = self._gallery_cache[self._current_gallery]
        if not items:
            logger.warning("Gallery has no items")
            return False

        current_selection = self._selected_items[-1] if self._selected_items else None
        if current_selection is None:
            # No current selection, select first item
            new_selection = items[0]
        else:
            try:
                current_index = items.index(current_selection)

                if direction == 'next':
                    new_index = (current_index + 1) % len(items)
                elif direction == 'previous':
                    new_index = (current_index - 1) % len(items)
                elif direction == 'first':
                    new_index = 0
                elif direction == 'last':
                    new_index = len(items) - 1
                else:
                    logger.warning(f"Unknown navigation direction: {direction}")
                    return False

                new_selection = items[new_index]
            except ValueError:
                # Current selection not in items, select first
                new_selection = items[0]

        return self.on_gallery_select(new_selection)

    @with_error_handling("Failed to filter gallery")
    def filter_gallery(self, filter_func: callable, gallery_id: str = None) -> List[Any]:
        """
        Filter gallery items.

        Args:
            filter_func: Function to filter items
            gallery_id: Gallery to filter (current if None)

        Returns:
            List[Any]: Filtered items
        """
        target_gallery = gallery_id or self._current_gallery
        if not target_gallery or target_gallery not in self._gallery_cache:
            logger.warning("No gallery available for filtering")
            return []

        items = self._gallery_cache[target_gallery]
        try:
            filtered_items = [item for item in items if filter_func(item)]
            logger.debug(f"Filtered gallery: {len(items)} -> {len(filtered_items)} items")
            return filtered_items
        except Exception as e:
            logger.error(f"Error filtering gallery: {e}")
            return items.copy()

    def get_gallery_info(self, gallery_id: str = None) -> Dict[str, Any]:
        """
        Get gallery information.

        Args:
            gallery_id: Gallery ID (current if None)

        Returns:
            Dict[str, Any]: Gallery information
        """
        target_gallery = gallery_id or self._current_gallery
        if not target_gallery:
            return {'id': None, 'items': [], 'selected': []}

        items = self._gallery_cache.get(target_gallery, [])
        return {
            'id': target_gallery,
            'items': items.copy(),
            'selected': self._selected_items.copy(),
            'item_count': len(items),
            'selection_count': len(self._selected_items),
        }


class GalleryImageProcessor:
    """Processes gallery images and metadata."""

    def __init__(self):
        """Initialize gallery image processor."""
        self._image_cache = {}
        self._metadata_cache = {}

    @with_error_handling("Failed to process gallery image")
    def process_gallery_image(
        self, image_path: str, extract_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Process gallery image.

        Args:
            image_path: Path to image file
            extract_metadata: Whether to extract metadata

        Returns:
            Dict[str, Any]: Image information
        """
        if image_path in self._image_cache:
            return self._image_cache[image_path]

        image_info = {
            'path': image_path,
            'filename': self._get_filename(image_path),
            'metadata': {},
            'dimensions': None,
            'file_size': None,
        }

        try:
            # Get file info
            import os

            if os.path.exists(image_path):
                image_info['file_size'] = os.path.getsize(image_path)

                # Get image dimensions
                try:
                    from PIL import Image

                    with Image.open(image_path) as img:
                        image_info['dimensions'] = img.size
                except Exception as e:
                    logger.debug(f"Could not get image dimensions: {e}")

                # Extract metadata if requested
                if extract_metadata:
                    image_info['metadata'] = self._extract_image_metadata(image_path)

            self._image_cache[image_path] = image_info
            return image_info

        except Exception as e:
            logger.error(f"Error processing gallery image {image_path}: {e}")
            return image_info

    def _get_filename(self, path: str) -> str:
        """
        Get filename from path.

        Args:
            path: File path

        Returns:
            str: Filename
        """
        import os

        return os.path.basename(path)

    def _extract_image_metadata(self, image_path: str) -> Dict[str, Any]:
        """
        Extract metadata from image.

        Args:
            image_path: Path to image

        Returns:
            Dict[str, Any]: Extracted metadata
        """
        if image_path in self._metadata_cache:
            return self._metadata_cache[image_path]

        metadata = {}
        try:
            from PIL import Image

            with Image.open(image_path) as img:
                # Extract EXIF data
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    metadata['exif'] = exif

                # Extract PNG info
                if hasattr(img, 'text'):
                    metadata['png_info'] = dict(img.text)

                # Get basic info
                metadata['format'] = img.format
                metadata['mode'] = img.mode
                metadata['size'] = img.size

            self._metadata_cache[image_path] = metadata
            return metadata

        except Exception as e:
            logger.debug(f"Could not extract metadata from {image_path}: {e}")
            return metadata


class GalleryNavigation:
    """Handles gallery navigation operations."""

    @staticmethod
    def create_navigation_controls(gallery_handlers: GalleryHandlers) -> Dict[str, callable]:
        """
        Create navigation control functions.

        Args:
            gallery_handlers: Gallery handlers instance

        Returns:
            Dict[str, callable]: Navigation functions
        """
        return {
            'next': lambda: gallery_handlers.navigate_gallery('next'),
            'previous': lambda: gallery_handlers.navigate_gallery('previous'),
            'first': lambda: gallery_handlers.navigate_gallery('first'),
            'last': lambda: gallery_handlers.navigate_gallery('last'),
        }

    @staticmethod
    def get_keyboard_shortcuts() -> Dict[str, str]:
        """
        Get keyboard shortcuts for gallery navigation.

        Returns:
            Dict[str, str]: Keyboard shortcuts
        """
        return {
            'ArrowRight': 'next',
            'ArrowLeft': 'previous',
            'Home': 'first',
            'End': 'last',
            'Escape': 'clear_selection',
        }


class GalleryUtils:
    """Utility functions for gallery operations."""

    @staticmethod
    def validate_gallery_item(item: Any) -> bool:
        """
        Validate gallery item.

        Args:
            item: Item to validate

        Returns:
            bool: True if valid, False otherwise
        """
        return item is not None

    @staticmethod
    def format_gallery_item_info(item: Any) -> str:
        """
        Format gallery item information for display.

        Args:
            item: Gallery item

        Returns:
            str: Formatted information
        """
        if isinstance(item, str):
            return item
        elif isinstance(item, dict):
            return item.get('name', str(item))
        else:
            return str(item)

    @staticmethod
    def sort_gallery_items(
        items: List[Any], sort_key: str = 'name', reverse: bool = False
    ) -> List[Any]:
        """
        Sort gallery items.

        Args:
            items: Items to sort
            sort_key: Key to sort by
            reverse: Whether to reverse sort

        Returns:
            List[Any]: Sorted items
        """
        try:
            if sort_key == 'name':
                return sorted(items, key=lambda x: str(x), reverse=reverse)
            elif sort_key == 'size' and all(isinstance(item, dict) for item in items):
                return sorted(items, key=lambda x: x.get('size', 0), reverse=reverse)
            else:
                return items.copy()
        except Exception as e:
            logger.warning(f"Error sorting gallery items: {e}")
            return items.copy()
