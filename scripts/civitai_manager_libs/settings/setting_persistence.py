"""Manages the persistence of application settings."""

import json
import os
import shutil
from typing import Optional

from ..exceptions import FileOperationError
from ..logging_config import get_logger

logger = get_logger(__name__)


class SettingPersistence:
    """Handles loading and saving settings to a file."""

    def __init__(self, config_file: Optional[str] = None):
        """Initializes the SettingPersistence with the given config file."""
        if config_file is None:
            from .path_manager import shortcut_setting

            config_file = shortcut_setting
        self.config_file = config_file
        self.backup_file = f"{config_file}.backup"

    def load_from_file(self) -> dict:
        """Loads settings from the configuration file."""
        if not os.path.isfile(self.config_file):
            logger.info(f"Configuration file not found: {self.config_file}. Creating a new one.")
            self.save_to_file({})
            return {}

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Failed to load settings from {self.config_file}: {e}")
            raise FileOperationError(f"Could not load settings from {self.config_file}") from e

    def save_to_file(self, settings: dict) -> bool:
        """Saves the given settings to the configuration file."""
        logger.debug(
            "[SettingPersistence.save_to_file] Called with config_file: %s, settings: %s",
            self.config_file,
            settings,
        )
        try:
            if os.path.isfile(self.config_file):
                shutil.copy2(self.config_file, self.backup_file)

            tmp_path = f"{self.config_file}.tmp"
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            os.replace(tmp_path, self.config_file)
            logger.info(f"Settings successfully saved to {self.config_file}")
            return True
        except IOError as e:
            logger.error(
                "[SettingPersistence.save_to_file] Failed to save settings to %s: %s",
                self.config_file,
                e,
            )
            raise FileOperationError(f"Could not save settings to {self.config_file}") from e

    def backup_settings(self) -> bool:
        """Creates a backup of the current settings file."""
        if not os.path.isfile(self.config_file):
            logger.warning("No settings file to back up.")
            return False

        try:
            shutil.copy2(self.config_file, self.backup_file)
            logger.info(f"Settings backed up to {self.backup_file}")
            return True
        except IOError as e:
            logger.error(f"Failed to back up settings: {e}")
            return False

    def restore_from_backup(self) -> dict:
        """Restores settings from the backup file."""
        if not os.path.isfile(self.backup_file):
            logger.warning("No backup file found to restore from.")
            return {}

        try:
            shutil.copy2(self.backup_file, self.config_file)
            logger.info(f"Settings restored from {self.backup_file}")
            return self.load_from_file()
        except IOError as e:
            logger.error(f"Failed to restore settings from backup: {e}")
            return {}

    def migrate_settings(self, old_settings: dict) -> dict:
        """Migrates old settings format to the new format."""
        # Add migration logic here if the settings format changes in the future
        return old_settings

    def validate_file_integrity(self) -> bool:
        """Validates the integrity of the settings file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, FileNotFoundError):
            return False

    def create_default_config(self) -> bool:
        """Creates a default configuration file."""
        return self.save_to_file({})

    def get_config_info(self) -> dict:
        """Returns information about the configuration file."""
        if not os.path.isfile(self.config_file):
            return {"status": "not_found"}

        return {
            "status": "found",
            "path": os.path.abspath(self.config_file),
            "size": os.path.getsize(self.config_file),
            "last_modified": os.path.getmtime(self.config_file),
        }
