"""Unit tests for the ConfigManager class."""

import pytest
from unittest.mock import Mock, patch

from scripts.civitai_manager_libs.settings import (
    ConfigManager,
    SettingCategories,
    SettingPersistence,
)


@pytest.fixture
def config_manager(tmp_path):
    """Fixture for creating a ConfigManager with a temporary config file."""
    config_file = tmp_path / "test_settings.json"
    return ConfigManager(config_file=str(config_file))


class TestConfigManager:
    """Tests for the ConfigManager class."""

    def test_init_with_default_persistence(self):
        """Test initialization with default persistence."""
        manager = ConfigManager()
        assert isinstance(manager.persistence, SettingPersistence)

    def test_init_with_custom_config_file(self, tmp_path):
        """Test initialization with custom config file."""
        config_file = tmp_path / "custom_config.json"
        manager = ConfigManager(config_file=str(config_file))
        assert manager.persistence.config_file == str(config_file)

    def test_load_settings_reload_true(self, config_manager):
        """Test loading settings with reload=True."""
        # Set some initial data
        config_manager.settings = {"initial": "data"}
        
        # Load with reload=True should reload from file
        result = config_manager.load_settings(reload=True)
        assert isinstance(result, dict)

    def test_load_settings_reload_false(self, config_manager):
        """Test loading settings with reload=False."""
        # Set some initial data
        test_data = {"cached": "data"}
        config_manager.settings = test_data
        
        # Load with reload=False should return cached data
        result = config_manager.load_settings(reload=False)
        assert result == test_data

    def test_save_settings_with_dict(self, config_manager):
        """Test saving settings with provided dictionary."""
        settings_to_save = {"test": "data", "number": 42}
        result = config_manager.save_settings(settings_to_save)
        
        assert result is True

    def test_save_settings_without_dict(self, config_manager):
        """Test saving current settings without providing dictionary."""
        config_manager.settings = {"current": "settings"}
        result = config_manager.save_settings()
        
        assert result is True

    def test_get_setting_flat_structure(self, config_manager):
        """Test getting setting from flat structure."""
        config_manager.settings = {"flat_key": "flat_value"}
        result = config_manager.get_setting("flat_key")
        assert result == "flat_value"

    def test_get_setting_nested_structure(self, config_manager):
        """Test getting setting from nested structure."""
        config_manager.settings = {
            "category": {
                "nested_key": "nested_value"
            }
        }
        
        # Mock the _search_nested_setting to find the value
        with patch.object(config_manager, '_search_nested_setting', return_value="nested_value"):
            result = config_manager.get_setting("nested_key")
            assert result == "nested_value"

    def test_get_setting_not_found(self, config_manager):
        """Test getting non-existent setting returns default."""
        config_manager.settings = {}
        result = config_manager.get_setting("non_existent")
        # Should return default value from SettingCategories
        default_value = SettingCategories.get_default_value("non_existent")
        assert result == default_value

    def test_search_nested_setting_found(self, config_manager):
        """Test _search_nested_setting when key is found."""
        config_manager.settings = {
            "category1": {"key1": "value1"},
            "category2": {"key2": "value2"}
        }
        category_mapping = {'category1': 'category1'}
        with patch.object(SettingCategories, 'find_setting_category', return_value='category1'), \
             patch.object(SettingCategories, 'get_config_category_mapping',
                          return_value=category_mapping):
            result = config_manager._search_nested_setting("key1")
            assert result == "value1"

    def test_search_nested_setting_not_found(self, config_manager):
        """Test _search_nested_setting when key is not found."""
        config_manager.settings = {
            "category1": {"key1": "value1"}
        }
        with patch.object(SettingCategories, 'find_setting_category', return_value=None):
            result = config_manager._search_nested_setting("non_existent")
            assert result is None

    def test_search_nested_setting_non_dict_value(self, config_manager):
        """Test _search_nested_setting with non-dict values."""
        config_manager.settings = {
            "category1": "not_a_dict",
            "category2": {"key2": "value2"}
        }
        category_mapping = {'category2': 'category2'}
        with patch.object(SettingCategories, 'find_setting_category', return_value='category2'), \
             patch.object(SettingCategories, 'get_config_category_mapping',
                          return_value=category_mapping):
            result = config_manager._search_nested_setting("key2")
            assert result == "value2"

    def test_set_setting_valid(self, config_manager):
        """Test setting a valid setting."""
        result = config_manager.set_setting("shortcut_column", 8)
        assert result is True
        assert config_manager.get_setting("shortcut_column") == 8

    def test_set_setting_invalid(self, config_manager):
        """Test setting an invalid setting."""
        # Mock validator to return invalid
        mock_validate = Mock(return_value=(False, "Invalid"))
        with patch.object(config_manager.validator, 'validate_setting', mock_validate):
            result = config_manager.set_setting("test_key", "invalid_value")
            assert result is False

    def test_set_setting_with_category_mapping(self, config_manager):
        """Test setting with proper category mapping."""
        mapping = {'ui_settings': 'screen_style'}
        with patch.object(SettingCategories, 'find_setting_category', return_value='ui_settings'), \
             patch.object(SettingCategories, 'get_config_category_mapping',
                          return_value=mapping):
            
            result = config_manager.set_setting("test_ui_setting", "test_value")
            assert result is True
            assert config_manager.settings["screen_style"]["test_ui_setting"] == "test_value"

    def test_set_setting_fallback_flat(self, config_manager):
        """Test setting falls back to flat structure when no category found."""
        with patch.object(SettingCategories, 'find_setting_category', return_value=None):
            result = config_manager.set_setting("fallback_key", "fallback_value")
            assert result is True
            assert config_manager.settings["fallback_key"] == "fallback_value"

    def test_update_settings(self, config_manager):
        """Test updating multiple settings at once."""
        settings_dict = {
            "shortcut_column": 8,
            "gallery_column": 6
        }
        
        result = config_manager.update_settings(settings_dict)
        assert len(result) == 2
        assert result["shortcut_column"] == 8
        assert result["gallery_column"] == 6

    def test_update_settings_with_invalid(self, config_manager):
        """Test updating settings with some invalid values."""
        settings_dict = {
            "shortcut_column": 8,
            "invalid_key": "invalid_value"
        }
        
        # Mock validator to make invalid_key invalid
        def mock_validate(key, value):
            if key == "invalid_key":
                return False, "Invalid key"
            return True, "Valid"
        
        with patch.object(config_manager.validator, 'validate_setting', side_effect=mock_validate):
            result = config_manager.update_settings(settings_dict)
            assert len(result) == 1  # Only valid setting should be returned
            assert "shortcut_column" in result

    def test_reset_setting_existing(self, config_manager):
        """Test resetting an existing setting."""
        # Set a custom value first
        config_manager.set_setting("shortcut_column", 10)
        
        # Reset to default
        result = config_manager.reset_setting("shortcut_column")
        assert result is True
        default_value = SettingCategories.get_default_value("shortcut_column")
        assert config_manager.get_setting("shortcut_column") == default_value

    def test_reset_setting_non_existent(self, config_manager):
        """Test resetting a non-existent setting."""
        result = config_manager.reset_setting("non_existent_setting")
        assert result is False

    def test_reset_all_settings(self, config_manager):
        """Test resetting all settings to defaults."""
        # Set some custom values
        config_manager.set_setting("shortcut_column", 10)
        
        # Reset all
        result = config_manager.reset_all_settings()
        assert result is True
        
        # Verify settings are reset to defaults
        assert config_manager.settings == config_manager.defaults

    def test_validate_all_settings(self, config_manager):
        """Test validating all current settings."""
        config_manager.settings = {
            "shortcut_column": 5,
            "invalid_setting": "invalid_value"
        }
        
        # Mock validator
        def mock_validate(key, value):
            if key == "invalid_setting":
                return False, "Invalid"
            return True, "Valid"
        
        with patch.object(config_manager.validator, 'validate_setting', side_effect=mock_validate):
            results = config_manager.validate_all_settings()
            assert "shortcut_column" in results
            assert "invalid_setting" in results
            assert results["shortcut_column"]["valid"] is True
            assert results["invalid_setting"]["valid"] is False

    def test_get_and_set_setting(self, config_manager):
        """Test getting and setting a single setting."""
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
        """Test resetting a setting to its default value."""
        config_manager.set_setting('shortcut_column', 12)
        config_manager.reset_setting('shortcut_column')
        value = config_manager.get_setting('shortcut_column')
        assert value == SettingCategories.get_default_value('shortcut_column')
