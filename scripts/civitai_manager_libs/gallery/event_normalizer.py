"""
Event normalization utilities for gallery module.

This module provides utilities to normalize different types of events
and parameters for consistent handling across different Gradio versions
and testing scenarios.
"""

from typing import Any, Tuple
from ..logging_config import get_logger

logger = get_logger(__name__)


class EventNormalizer:
    """Utility class for normalizing gallery select events."""

    @staticmethod
    def create_test_event(index: int = 0, value: Any = None, selected: bool = True):
        """Create a test-compatible event object.

        This method creates an event object that mimics the structure of
        Gradio SelectData for testing purposes.

        Args:
            index: Event index
            value: Event value
            selected: Selection state

        Returns:
            A test-compatible event object
        """
        return type('TestSelectData', (), {'index': index, 'value': value, 'selected': selected})()

    @staticmethod
    def normalize_gallery_event(evt: Any, civitai_images: Any) -> Tuple[Any, Any]:
        """Normalize gallery event parameters for consistent processing.

        Handles different parameter combinations that may occur due to:
        - Gradio version differences (v3/v4)
        - Test scenarios with mock objects
        - Parameter order mixups

        Args:
            evt: Event object (should have .index attribute) or list
            civitai_images: Image list or event object

        Returns:
            Tuple of (normalized_event, normalized_images)

        Raises:
            ValueError: If event cannot be normalized
        """
        # Handle case where evt is a list and civitai_images is None
        # This can happen in Gradio v3/v4 default parameter modes
        if isinstance(evt, list) and civitai_images is None:
            logger.debug(
                "[GALLERY] Detected Gradio v3/v4 default parameter mode: "
                "evt is images list, civitai_images is None"
            )
            civitai_images = evt
            evt = EventNormalizer.create_test_event(index=0)

        # Handle reverse case where civitai_images is a list and evt is None
        elif isinstance(civitai_images, list) and evt is None:
            logger.debug(
                "[GALLERY] Detected Gradio v3/v4 default parameter mode: "
                "civitai_images is images list, evt is None"
            )
            evt = EventNormalizer.create_test_event(index=0)

        # Handle parameter mixup - check if parameters are swapped
        elif not hasattr(evt, 'index'):
            if hasattr(civitai_images, 'index'):
                logger.warning(
                    "[GALLERY] Detected parameter mixup - auto-swapping "
                    "evt/civitai_images (v3/v4 fix)"
                )
                evt, civitai_images = civitai_images, evt
            else:
                error_msg = (
                    f"evt is not a SelectData or compatible object! " f"It's {type(evt)}: {evt}"
                )
                logger.error(f"[GALLERY] {error_msg}")
                raise ValueError(f"Invalid event type (no .index attribute): {error_msg}")

        # Validate final state
        if civitai_images is None:
            error_msg = "civitai_images is None! This indicates incorrect event binding."
            logger.error(f"[GALLERY] {error_msg}")
            raise ValueError(f"No images data available: {error_msg}")

        return evt, civitai_images


class CompatibilityEventAdapter:
    """Adapter for handling compatibility across different environments."""

    @staticmethod
    def adapt_for_testing(evt: Any, civitai_images: Any) -> Tuple[Any, Any]:
        """Adapt events specifically for testing scenarios.

        This method handles test-specific adaptations without affecting
        production code paths.

        Args:
            evt: Event from test
            civitai_images: Images from test

        Returns:
            Tuple of adapted (event, images)
        """
        # For testing, we might receive mock objects or simplified structures
        # This adapter ensures they work correctly with the main logic
        try:
            return EventNormalizer.normalize_gallery_event(evt, civitai_images)
        except ValueError as e:
            # In test scenarios, we might want to be more lenient
            logger.debug(f"[GALLERY] Test adapter handling error: {e}")
            if not hasattr(evt, 'index') and civitai_images is not None:
                # Create a minimal compatible event for tests
                evt = EventNormalizer.create_test_event(index=0)
            return evt, civitai_images
