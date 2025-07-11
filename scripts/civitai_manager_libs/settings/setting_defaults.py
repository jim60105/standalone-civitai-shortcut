"""Default settings for the application."""

# All defaults are now managed by SettingCategories to follow DRY principle
# This module provides backward compatibility and convenience methods


class SettingDefaults:
    """Manages default settings for the application."""

    @classmethod
    def get_all_defaults(cls) -> dict:
        """Returns all default settings."""
        # Import here to avoid circular import
        from .setting_categories import SettingCategories

        return SettingCategories.get_all_defaults()

    @classmethod
    def get_category_defaults(cls, category: str) -> dict:
        """Returns default settings for a specific category."""
        # Import here to avoid circular import
        from .setting_categories import SettingCategories

        return SettingCategories.get_category_defaults(category)

    @classmethod
    def get_default_value(cls, key: str):
        """Returns the default value for a specific settings key."""
        # Import here to avoid circular import
        from .setting_categories import SettingCategories

        return SettingCategories.get_default_value(key)
