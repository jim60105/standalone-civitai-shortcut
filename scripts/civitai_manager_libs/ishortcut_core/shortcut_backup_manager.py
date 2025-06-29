"""
shortcut_backup_manager.py - Manages backup and restore operations for shortcuts.

This module provides the ShortcutBackupManager class to handle backup, restore,
and cleanup of shortcut data and URL mappings.
"""

import os
import json
import datetime

from ..logging_config import get_logger
from .. import setting

logger = get_logger(__name__)


class ShortcutBackupManager:
    """Manages backup and restore operations for shortcuts."""

    def __init__(self):
        # Ensure the URL mapping directory exists
        os.makedirs(os.path.dirname(setting.shortcut_civitai_internet_shortcut_url), exist_ok=True)

    def backup_shortcut(self, shortcut_data: dict) -> bool:
        """Backup single shortcut data to a timestamped backup file."""
        if not shortcut_data or "id" not in shortcut_data:
            return False

        model_id = str(shortcut_data["id"])
        try:
            backup_dir = setting.shortcut_info_folder
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            backup_file = os.path.join(backup_dir, f"{model_id}_{timestamp}.json")
            with open(backup_file, "w") as f:
                json.dump(shortcut_data, f, indent=4)
            logger.info(f"Shortcut backup created: {backup_file}")
            return True
        except Exception:
            logger.error(f"Failed to backup shortcut {model_id}", exc_info=True)
            return False

    def backup_url_mapping(self, name: str, url: str) -> bool:
        """Backup URL mapping for deleted shortcuts."""
        if not name or not url:
            return False

        try:
            mapping_file = setting.shortcut_civitai_internet_shortcut_url
            try:
                with open(mapping_file, "r") as f:
                    mapping = json.load(f)
            except Exception:
                mapping = {}

            mapping[f"url={url}"] = name
            with open(mapping_file, "w") as f:
                json.dump(mapping, f, indent=4)
            logger.info(f"URL mapping backed up: {url}")
            return True
        except Exception:
            logger.error("Error backing up URL mapping", exc_info=True)
            return False

    def restore_from_backup(self, model_id: str) -> dict:
        """Restore shortcut data from the latest backup if available."""
        try:
            backup_dir = setting.shortcut_info_folder
            files = [
                f
                for f in os.listdir(backup_dir)
                if f.startswith(f"{model_id}_") and f.endswith(".json")
            ]
            if not files:
                return {}

            files.sort(reverse=True)
            latest = files[0]
            path = os.path.join(backup_dir, latest)
            with open(path, "r") as f:
                data = json.load(f)
            logger.info(f"Restored shortcut from backup: {path}")
            return data
        except Exception:
            logger.error(f"Failed to restore backup for {model_id}", exc_info=True)
            return {}

    def get_backup_list(self) -> list:
        """Get list of available shortcut backups with timestamps."""
        backups = []
        try:
            backup_dir = setting.shortcut_info_folder
            for f in os.listdir(backup_dir):
                if f.endswith(".json"):
                    model_id, ts = f.rsplit("_", 1)
                    timestamp = ts.rsplit(".json", 1)[0]
                    backups.append({"model_id": model_id, "timestamp": timestamp, "file": f})
        except Exception:
            logger.error("Error listing shortcut backups", exc_info=True)
        return backups

    def cleanup_old_backups(self, days_old: int = 30) -> int:
        """Clean up backup files older than the specified number of days."""
        removed = 0
        try:
            cutoff = datetime.datetime.now() - datetime.timedelta(days=days_old)
            backup_dir = setting.shortcut_info_folder
            for f in os.listdir(backup_dir):
                if not f.endswith(".json"):
                    continue
                path = os.path.join(backup_dir, f)
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
                if mtime < cutoff:
                    os.remove(path)
                    removed += 1
                    logger.info(f"Removed old backup: {path}")
        except Exception:
            logger.error("Error cleaning up old backups", exc_info=True)
        return removed
