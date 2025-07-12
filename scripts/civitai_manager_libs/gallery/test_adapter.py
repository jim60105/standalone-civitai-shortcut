"""
Test utilities for gallery module.

This module provides test-specific utilities and adapters
for the gallery module, separating test concerns from production code.
"""

from typing import Any
from .event_normalizer import EventNormalizer


class GalleryTestAdapter:
    """Test adapter for gallery module functionality."""

    @staticmethod
    def create_mock_select_event(index: int = 0, value: Any = None):
        """Create a mock SelectData event for testing.

        Args:
            index: Event index
            value: Event value

        Returns:
            Mock event object compatible with gallery handlers
        """
        return EventNormalizer.create_test_event(index=index, value=value, selected=True)

    @staticmethod
    def create_gradio_v3_scenario(images_list: list):
        """Create a Gradio v3-style parameter scenario for testing.

        In Gradio v3, sometimes the images list gets passed as the first parameter
        and the event becomes None.

        Args:
            images_list: List of image paths

        Returns:
            Tuple of (evt, civitai_images) simulating the v3 scenario
        """
        return images_list, None

    @staticmethod
    def create_gradio_v4_scenario(images_list: list):
        """Create a Gradio v4-style parameter scenario for testing.

        In Gradio v4, the parameter order might be different.

        Args:
            images_list: List of image paths

        Returns:
            Tuple of (evt, civitai_images) simulating the v4 scenario
        """
        return None, images_list

    @staticmethod
    def create_swapped_params_scenario(images_list: list):
        """Create a swapped parameters scenario for testing.

        Sometimes due to version differences, the SelectData and images list
        parameters get swapped.

        Args:
            images_list: List of image paths

        Returns:
            Tuple of (evt, civitai_images) with swapped parameters
        """
        mock_event = EventNormalizer.create_test_event(index=0)
        return images_list, mock_event

    @staticmethod
    def verify_event_normalization(evt: Any, civitai_images: Any) -> bool:
        """Verify that event normalization works correctly.

        Args:
            evt: Event object or parameter
            civitai_images: Images list or parameter

        Returns:
            True if normalization succeeds, False otherwise
        """
        try:
            normalized_evt, normalized_images = EventNormalizer.normalize_gallery_event(
                evt, civitai_images
            )
            return (
                hasattr(normalized_evt, 'index')
                and normalized_images is not None
                and isinstance(normalized_images, list)
            )
        except ValueError:
            return False
