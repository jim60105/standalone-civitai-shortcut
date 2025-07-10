"""Unit tests for the settings modules."""
import os
import pytest
from scripts.civitai_manager_libs.settings import (
    ConfigManager,
    SettingCategories,
    SettingDefaults,
    SettingPersistence,
    SettingValidator,
)

@pytest.fixture
def config_manager(tmp_path):
    """Fixture for creating a ConfigManager with a temporary config file."""
    config_file = tmp_path / "test_settings.json"
    return ConfigManager(config_file=str(config_file))

class TestSettingDefaults:
    """Tests for the SettingDefaults class."""

    def test_get_all_defaults(self):
        """Test that get_all_defaults returns a non-empty dictionary."""
        defaults = SettingDefaults.get_all_defaults()
        assert isinstance(defaults, dict)
        assert len(defaults) > 0

    def test_get_default_value(self):
        """Test that get_default_value returns the correct default value."""
        default_value = SettingDefaults.get_default_value('shortcut_column')
        assert default_value == 5

class TestSettingCategories:
    """Tests for the SettingCategories class."""

    def test_get_all_categories(self):
        """Test that get_all_categories returns a non-empty dictionary."""
        categories = SettingCategories.get_all_categories()
        assert isinstance(categories, dict)
        assert len(categories) > 0

    def test_get_setting_type(self):
        """Test that get_setting_type returns the correct type for a settings."""
        setting_type = SettingCategories.get_setting_type('shortcut_column')
        assert setting_type == 'integer'

class TestSettingValidator:
    """Tests for the SettingValidator class."""

    def setup_method(self):
        """Set up a SettingValidator instance before each test."""
        self.validator = SettingValidator()

    def test_validate_range_setting(self):
        """Test the validation of a range settings."""
        is_valid, _ = self.validator.validate_range_setting(5, 1, 10)
        assert is_valid
        is_valid, _ = self.validator.validate_range_setting(15, 1, 10)
        assert not is_valid

    def test_validate_path_setting(self, tmp_path):
        """Test the validation of a path settings."""
        is_valid, _ = self.validator.validate_path_setting(str(tmp_path))
        assert is_valid
        is_valid, _ = self.validator.validate_path_setting("/invalid/path")
        assert not is_valid

class TestSettingPersistence:
    """Tests for the SettingPersistence class."""

    def test_save_and_load(self, tmp_path):
        """Test saving and loading settings to/from a file."""
        config_file = tmp_path / "settings.json"
        persistence = SettingPersistence(config_file=str(config_file))
        settings_to_save = {"key": "value"}
        persistence.save_to_file(settings_to_save)
        loaded_settings = persistence.load_from_file()
        assert loaded_settings == settings_to_save

class TestConfigManager:
    """Tests for the ConfigManager class."""

    def test_get_and_set_setting(self, config_manager):
        """Test getting and settings a single settings."""
        config_manager.set_setting('shortcut_column', 8)
        value = config_manager.get_setting('shortcut_column')
        assert value == 8

    def test_load_and_save_settings(self, config_manager):
        """Test loading and saving the entire settings configuration."""
        settings_to_save = {'shortcut_column': 10, 'gallery_column': 6}
        config_manager.save_settings(settings_to_save)
        loaded_settings = config_manager.load_settings(reload=True)
        assert loaded_settings['shortcut_column'] == 10

    def test_reset_setting(self, config_manager):
        """Test resetting a settings to its default value."""
        config_manager.set_setting('shortcut_column', 12)
        config_manager.reset_setting('shortcut_column')
        value = config_manager.get_setting('shortcut_column')
        assert value == SettingDefaults.get_default_value('shortcut_column')
