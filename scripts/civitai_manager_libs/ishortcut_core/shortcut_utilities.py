"""
shortcut_utilities: Utility functions for shortcut operations.

This module provides common helper methods for formatting and validating
shortcut-related data across the ishortcut_core components.
"""

import os
import datetime


class ShortcutUtilities:
    """Utility functions for shortcut operations."""

    @staticmethod
    def extract_version_image_id(filename: str) -> list:
        """Extract version and image ID from filename."""
        version_image, _ = os.path.splitext(filename)
        ids = version_image.split("-")
        return ids if len(ids) > 1 else None

    @staticmethod
    def generate_shortcut_name(name: str, model_id: str) -> str:
        """Generate formatted shortcut name combining base name and model ID."""
        base = (name or '').strip()
        mid = str(model_id).strip()
        return f"{base}-{mid}" if base and mid else base or mid

    @staticmethod
    def validate_model_id(model_id: str) -> bool:
        """Validate model ID format using DataValidator."""
        from .data_validator import DataValidator

        return DataValidator().validate_model_id(model_id)

    @staticmethod
    def format_date_string() -> str:
        """Generate formatted date string for timestamps: YYYYMMDD_HHMMSS."""
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    @staticmethod
    def ensure_nsfw_field(shortcut_data: dict) -> dict:
        """Ensure NSFW field exists in shortcut data with default False."""
        if not isinstance(shortcut_data, dict):
            return shortcut_data
        shortcut_data.setdefault('nsfw', False)
        return shortcut_data
