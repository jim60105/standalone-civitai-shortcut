"""
shortcut_collection_manager.py - Manages shortcut collections with CRUD operations and persistence.

This module provides collection management for shortcuts, including loading,
saving, adding, deleting, and updating shortcuts with proper cleanup and backup.
"""

import os
import json
import datetime

from tqdm import tqdm

from ..logging_config import get_logger
from .. import setting
from .model_factory import ModelFactory
from .file_processor import FileProcessor
from .image_processor import ImageProcessor
from ..civitai import Url_Page

logger = get_logger(__name__)


class ShortcutCollectionManager:
    """Manages shortcut collections with CRUD operations and persistence."""

    def __init__(self):
        self._model_factory = ModelFactory()
        self._file_processor = FileProcessor()
        self._image_processor = ImageProcessor()

    def load_shortcuts(self) -> dict:
        """Load shortcuts from persistent storage."""
        if not os.path.isfile(setting.shortcut):
            logger.debug("Shortcut file not found, initializing empty collection.")
            return {}
        try:
            with open(setting.shortcut, 'r') as f:
                data = json.load(f)
        except Exception:
            logger.error(f"Error loading shortcut file: {setting.shortcut}", exc_info=True)
            return {}
        return data or {}

    def save_shortcuts(self, shortcuts: dict) -> str:
        """Save shortcuts to persistent storage with error handling."""
        try:
            with open(setting.shortcut, 'w') as f:
                json.dump(shortcuts, f, indent=4)
        except Exception:
            logger.error(f"Error writing shortcut file: {setting.shortcut}", exc_info=True)
            return ""
        return f"Civitai Internet Shortcut saved to: {setting.shortcut}"

    def add_shortcut(
        self, shortcuts: dict, model_id: str, register_information_only: bool = False, progress=None
    ) -> dict:
        """Add a single shortcut to collection."""
        if not model_id:
            return shortcuts
        if shortcuts is None:
            shortcuts = {}
        # Create or update the shortcut via ModelFactory
        new_entries = (
            self._model_factory.create_model_shortcut(
                str(model_id), register_information_only, progress
            )
            or {}
        )
        if str(model_id) in new_entries:
            shortcuts.update(new_entries)
        return shortcuts

    def delete_shortcut(self, shortcuts: dict, model_id: str) -> dict:
        """Remove shortcut and clean up associated files."""
        if not model_id or not shortcuts:
            return shortcuts
        entry = shortcuts.pop(str(model_id), None)
        # Backup URL mapping for deleted shortcut
        if entry and 'name' in entry and 'id' in entry:
            try:
                backup = None
                try:
                    with open(setting.shortcut_civitai_internet_shortcut_url, 'r') as f:
                        backup = json.load(f)
                except Exception:
                    backup = {}
                backup[f"url={Url_Page()}{entry['id']}"] = entry['name']
                with open(setting.shortcut_civitai_internet_shortcut_url, 'w') as f:
                    json.dump(backup, f, indent=4)
            except Exception:
                err_file = setting.shortcut_civitai_internet_shortcut_url
                logger.error(
                    f"Error backing up URL mapping: {err_file}",
                    exc_info=True,
                )
        # Cleanup associated files
        try:
            self._image_processor.delete_thumbnail_image(model_id)
        except Exception:
            logger.warning(f"Failed to delete thumbnail for shortcut {model_id}", exc_info=True)
        try:
            self._file_processor.delete_model_information(model_id)
        except Exception:
            logger.warning(
                f"Failed to delete model information for shortcut {model_id}", exc_info=True
            )
        return shortcuts

    def delete_shortcut_model(self, model_id: str):
        """Delete a shortcut model and save changes."""
        if not model_id:
            return
        shortcuts = self.load_shortcuts()
        shortcuts = self.delete_shortcut(shortcuts, model_id)
        self.save_shortcuts(shortcuts)

    def update_shortcut(self, model_id: str, progress=None):
        """Update existing shortcut preserving user data."""
        if not model_id:
            return
        shortcuts = self.load_shortcuts()
        existing = shortcuts.get(str(model_id), {})
        result = self._model_factory.create_model_shortcut(str(model_id), False, progress) or {}
        entry = result.get(str(model_id))
        if entry:
            # Preserve note and date
            if 'note' in existing:
                entry['note'] = existing['note']
            # Preserve or set date
            entry['date'] = existing.get('date') or datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            # Ensure nsfw field
            entry.setdefault('nsfw', False)
            shortcuts.update({str(model_id): entry})
            self.save_shortcuts(shortcuts)

    def update_multiple_shortcuts(self, model_ids: list, progress):
        """Batch update multiple shortcuts."""
        if not model_ids:
            return
        for mid in tqdm(model_ids, desc="Updating Shortcuts", disable=progress is None):
            self.update_shortcut(mid, progress)

    def update_all_shortcuts(self, progress):
        """Update all shortcuts."""
        shortcuts = self.load_shortcuts()
        if not shortcuts:
            return
        model_ids = list(shortcuts.keys())
        self.update_multiple_shortcuts(model_ids, progress)

    def get_shortcut(self, model_id: str) -> dict:
        """Get specific shortcut by model ID."""
        if not model_id:
            return {}
        shortcuts = self.load_shortcuts()
        return shortcuts.get(str(model_id), {})

    def update_shortcut_note(self, model_id: str, note: str):
        """Update note for specific shortcut."""
        if not model_id:
            return
        shortcuts = self.load_shortcuts()
        entry = shortcuts.get(str(model_id))
        if entry is not None:
            entry['note'] = str(note)
            self.save_shortcuts(shortcuts)

    def get_shortcut_note(self, model_id: str) -> str:
        """Get note for specific shortcut."""
        if not model_id:
            return ''
        shortcuts = self.load_shortcuts()
        entry = shortcuts.get(str(model_id))
        return entry.get('note', '') if entry else ''
