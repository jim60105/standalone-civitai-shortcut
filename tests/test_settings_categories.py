"""Unit tests for the SettingCategories class."""

from scripts.civitai_manager_libs.settings import SettingCategories


class TestSettingCategories:
    """Tests for the SettingCategories class."""

    def test_get_all_categories(self):
        """Test that get_all_categories returns a non-empty dictionary."""
        categories = SettingCategories.get_all_categories()
        assert isinstance(categories, dict)
        assert len(categories) > 0

    def test_get_category_settings(self):
        """Test getting settings for a specific category."""
        # Test with a valid category
        ui_settings = SettingCategories.get_category_settings('ui_settings')
        assert isinstance(ui_settings, dict)
        
    def test_get_setting_type(self):
        """Test that get_setting_type returns the correct type for a settings."""
        setting_type = SettingCategories.get_setting_type('shortcut_column')
        assert setting_type == 'integer'
        
        # Test with non-existent setting - returns 'string' as default
        setting_type = SettingCategories.get_setting_type('non_existent_setting')
        assert setting_type == 'string'  # Default type is string, not None

    def test_get_category_defaults(self):
        """Test getting default values for a specific category."""
        defaults = SettingCategories.get_category_defaults('ui_settings')
        assert isinstance(defaults, dict)

    def test_get_all_defaults(self):
        """Test that get_all_defaults returns a non-empty dictionary."""
        defaults = SettingCategories.get_all_defaults()
        assert isinstance(defaults, dict)
        assert len(defaults) > 0

    def test_get_default_value(self):
        """Test that get_default_value returns the correct default value."""
        default_value = SettingCategories.get_default_value('shortcut_column')
        assert default_value == 5

    def test_get_config_category_mapping(self):
        """Test that config category mapping is returned."""
        mapping = SettingCategories.get_config_category_mapping()
        assert isinstance(mapping, dict)

    def test_find_setting_category(self):
        """Test finding the category for a given setting."""
        category = SettingCategories.find_setting_category('shortcut_column')
        assert category is not None
        
        # Test with non-existent setting
        category = SettingCategories.find_setting_category('non_existent_setting')
        assert category is None

    def test_get_validation_range(self):
        """Test getting validation range for settings."""
        range_info = SettingCategories.get_validation_range('shortcut_column')
        assert isinstance(range_info, (dict, tuple, type(None)))
