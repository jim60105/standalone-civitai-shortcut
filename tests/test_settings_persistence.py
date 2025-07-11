"""Unit tests for the SettingPersistence class."""

import json
import os
import pytest
from unittest.mock import patch

from scripts.civitai_manager_libs.settings import SettingPersistence
from scripts.civitai_manager_libs.settings import path_manager as pm
from scripts.civitai_manager_libs.exceptions import FileOperationError


class TestSettingPersistence:
    """Tests for the SettingPersistence class."""

    def test_init_with_default_config_file(self):
        """Test initialization with default config file."""
        with patch.object(pm, 'shortcut_setting', '/default/path'):
            persistence = SettingPersistence()
            assert persistence.config_file == '/default/path'

    def test_init_with_custom_config_file(self, tmp_path):
        """Test initialization with custom config file."""
        config_file = tmp_path / "custom_settings.json"
        persistence = SettingPersistence(config_file=str(config_file))
        assert persistence.config_file == str(config_file)
        assert persistence.backup_file == str(config_file) + ".backup"

    def test_load_from_file_non_existent(self, tmp_path):
        """Test loading from non-existent file creates new one."""
        config_file = tmp_path / "new_settings.json"
        persistence = SettingPersistence(config_file=str(config_file))
        
        settings = persistence.load_from_file()
        assert settings == {}
        assert os.path.exists(str(config_file))

    def test_load_from_file_invalid_json(self, tmp_path):
        """Test loading from file with invalid JSON."""
        config_file = tmp_path / "invalid_settings.json"
        with open(str(config_file), 'w') as f:
            f.write("invalid json content")
        
        persistence = SettingPersistence(config_file=str(config_file))
        
        with pytest.raises(FileOperationError):
            persistence.load_from_file()

    def test_load_from_file_file_not_found_exception(self, tmp_path):
        """Test loading from file that gets deleted between checks."""
        config_file = tmp_path / "disappearing_settings.json"
        persistence = SettingPersistence(config_file=str(config_file))
        
        # Mock os.path.isfile to return True but file reading to fail
        with patch('os.path.isfile', return_value=True), \
             patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            with pytest.raises(FileOperationError):
                persistence.load_from_file()

    def test_save_to_file_success(self, tmp_path):
        """Test successfully saving settings to file."""
        config_file = tmp_path / "settings.json"
        persistence = SettingPersistence(config_file=str(config_file))
        settings_to_save = {"key": "value", "number": 42}
        
        result = persistence.save_to_file(settings_to_save)
        assert result is True
        
        # Verify the file was created and contains correct data
        assert os.path.exists(str(config_file))
        with open(str(config_file), 'r') as f:
            loaded_data = json.load(f)
        assert loaded_data == settings_to_save

    def test_save_to_file_with_existing_backup(self, tmp_path):
        """Test saving when there's already an existing file (creates backup)."""
        config_file = tmp_path / "settings.json"
        backup_file = tmp_path / "settings.json.backup"
        
        # Create an existing config file
        existing_settings = {"old": "data"}
        with open(str(config_file), 'w') as f:
            json.dump(existing_settings, f)
        
        persistence = SettingPersistence(config_file=str(config_file))
        new_settings = {"new": "data"}
        
        result = persistence.save_to_file(new_settings)
        assert result is True
        
        # Verify backup was created with old data
        assert os.path.exists(str(backup_file))
        with open(str(backup_file), 'r') as f:
            backup_data = json.load(f)
        assert backup_data == existing_settings
        
        # Verify new data is in the main file
        with open(str(config_file), 'r') as f:
            new_data = json.load(f)
        assert new_data == new_settings

    def test_save_to_file_io_error(self, tmp_path):
        """Test saving to file with IO error."""
        config_file = tmp_path / "readonly_settings.json"
        persistence = SettingPersistence(config_file=str(config_file))
        
        # Mock open to raise IOError
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with pytest.raises(FileOperationError):
                persistence.save_to_file({"test": "data"})

    def test_backup_settings_success(self, tmp_path):
        """Test successfully backing up settings."""
        config_file = tmp_path / "settings.json"
        backup_file = tmp_path / "settings.json.backup"
        
        # Create a config file
        settings = {"test": "data"}
        with open(str(config_file), 'w') as f:
            json.dump(settings, f)
        
        persistence = SettingPersistence(config_file=str(config_file))
        result = persistence.backup_settings()
        
        assert result is True
        assert os.path.exists(str(backup_file))
        
        with open(str(backup_file), 'r') as f:
            backup_data = json.load(f)
        assert backup_data == settings

    def test_backup_settings_no_file(self, tmp_path):
        """Test backing up when no settings file exists."""
        config_file = tmp_path / "non_existent_settings.json"
        persistence = SettingPersistence(config_file=str(config_file))
        
        result = persistence.backup_settings()
        assert result is False

    def test_backup_settings_io_error(self, tmp_path):
        """Test backing up with IO error."""
        config_file = tmp_path / "settings.json"
        
        # Create a config file
        with open(str(config_file), 'w') as f:
            json.dump({"test": "data"}, f)
        
        persistence = SettingPersistence(config_file=str(config_file))
        
        # Mock shutil.copy2 to raise IOError
        with patch('shutil.copy2', side_effect=IOError("Permission denied")):
            result = persistence.backup_settings()
            assert result is False

    def test_restore_from_backup_success(self, tmp_path):
        """Test successfully restoring from backup."""
        config_file = tmp_path / "settings.json"
        backup_file = tmp_path / "settings.json.backup"
        
        # Create backup file
        backup_settings = {"backup": "data"}
        with open(str(backup_file), 'w') as f:
            json.dump(backup_settings, f)
        
        persistence = SettingPersistence(config_file=str(config_file))
        result = persistence.restore_from_backup()
        
        assert result == backup_settings
        assert os.path.exists(str(config_file))
        
        with open(str(config_file), 'r') as f:
            restored_data = json.load(f)
        assert restored_data == backup_settings

    def test_restore_from_backup_no_backup(self, tmp_path):
        """Test restoring when no backup file exists."""
        config_file = tmp_path / "settings.json"
        persistence = SettingPersistence(config_file=str(config_file))
        
        result = persistence.restore_from_backup()
        assert result == {}

    def test_restore_from_backup_io_error(self, tmp_path):
        """Test restoring with IO error."""
        config_file = tmp_path / "settings.json"
        backup_file = tmp_path / "settings.json.backup"
        
        # Create backup file
        with open(str(backup_file), 'w') as f:
            json.dump({"backup": "data"}, f)
        
        persistence = SettingPersistence(config_file=str(config_file))
        
        # Mock shutil.copy2 to raise IOError
        with patch('shutil.copy2', side_effect=IOError("Permission denied")):
            result = persistence.restore_from_backup()
            assert result == {}

    def test_migrate_settings(self, tmp_path):
        """Test settings migration."""
        config_file = tmp_path / "settings.json"
        persistence = SettingPersistence(config_file=str(config_file))
        
        old_settings = {"old_format": "data"}
        result = persistence.migrate_settings(old_settings)
        
        # Currently just returns the same settings
        assert result == old_settings

    def test_validate_file_integrity_valid(self, tmp_path):
        """Test file integrity validation with valid JSON."""
        config_file = tmp_path / "settings.json"
        
        # Create valid JSON file
        with open(str(config_file), 'w') as f:
            json.dump({"valid": "json"}, f)
        
        persistence = SettingPersistence(config_file=str(config_file))
        result = persistence.validate_file_integrity()
        
        assert result is True

    def test_validate_file_integrity_invalid(self, tmp_path):
        """Test file integrity validation with invalid JSON."""
        config_file = tmp_path / "settings.json"
        
        # Create invalid JSON file
        with open(str(config_file), 'w') as f:
            f.write("invalid json content")
        
        persistence = SettingPersistence(config_file=str(config_file))
        result = persistence.validate_file_integrity()
        
        assert result is False

    def test_validate_file_integrity_no_file(self, tmp_path):
        """Test file integrity validation when file doesn't exist."""
        config_file = tmp_path / "non_existent.json"
        persistence = SettingPersistence(config_file=str(config_file))
        
        result = persistence.validate_file_integrity()
        assert result is False

    def test_create_default_config(self, tmp_path):
        """Test creating default configuration."""
        config_file = tmp_path / "default_settings.json"
        persistence = SettingPersistence(config_file=str(config_file))
        
        result = persistence.create_default_config()
        assert result is True
        
        # Verify file was created with empty dict
        assert os.path.exists(str(config_file))
        with open(str(config_file), 'r') as f:
            data = json.load(f)
        assert data == {}

    def test_get_config_info_existing_file(self, tmp_path):
        """Test getting config info for existing file."""
        config_file = tmp_path / "settings.json"
        
        # Create a config file
        with open(str(config_file), 'w') as f:
            json.dump({"test": "data"}, f)
        
        persistence = SettingPersistence(config_file=str(config_file))
        info = persistence.get_config_info()
        
        assert info["status"] == "found"
        assert info["path"] == os.path.abspath(str(config_file))
        assert info["size"] > 0
        assert "last_modified" in info

    def test_get_config_info_non_existent_file(self, tmp_path):
        """Test getting config info for non-existent file."""
        config_file = tmp_path / "non_existent.json"
        persistence = SettingPersistence(config_file=str(config_file))
        
        info = persistence.get_config_info()
        assert info == {"status": "not_found"}

    def test_save_and_load(self, tmp_path):
        """Test saving and loading settings to/from a file."""
        config_file = tmp_path / "settings.json"
        persistence = SettingPersistence(config_file=str(config_file))
        settings_to_save = {"key": "value"}
        persistence.save_to_file(settings_to_save)
        loaded_settings = persistence.load_from_file()
        assert loaded_settings == settings_to_save
