"""
shortcut_search_filter.py: Advanced search, filtering and sorting for shortcut collections.

This module provides the ShortcutSearchFilter class to perform multi-criteria
search, filtering, and sorting operations on shortcut collections managed by
ShortcutCollectionManager.
"""

from typing import Any, Dict, List, Optional

from ..logging_config import get_logger

from .model_processor import ModelProcessor
from .shortcut_collection_manager import ShortcutCollectionManager

from .. import settings
from .. import util
from .. import classification

logger = get_logger(__name__)


class ShortcutSearchFilter:
    """Advanced search, filtering and sorting for shortcut collections."""

    def __init__(
        self,
        collection_manager: ShortcutCollectionManager,
        model_processor: ModelProcessor,
    ):
        self._collection_manager = collection_manager
        self._model_processor = model_processor

    def get_shortcuts_list(self, shortcut_types: Optional[List[str]] = None) -> List[str]:
        """Get basic list of shortcuts with type filtering."""
        ISC = self._collection_manager.load_shortcuts()
        if not ISC:
            return []

        shortcuts = list(ISC.values())
        filtered = self._apply_type_filter(shortcuts, shortcut_types)
        return [settings.set_shortcutname(v['name'], v['id']) for v in filtered]

    def get_filtered_shortcuts(
        self,
        shortcut_types: Optional[List[str]] = None,
        search: Optional[str] = None,
        base_models: Optional[List[str]] = None,
        classifications: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Advanced filtering with multiple criteria."""
        ISC = self._collection_manager.load_shortcuts()
        if not ISC:
            return []

        result = list(ISC.values())

        # Classification filtering with AND logic
        result = self._apply_classification_filter(result, classifications)

        # Type filtering
        result = self._apply_type_filter(result, shortcut_types)

        # Keyword, tag, and note filtering
        keys, tags, notes = util.get_search_keyword(search)
        result = self._apply_keyword_filter(result, keys)
        result = self._apply_tag_filter(result, tags)
        result = self._apply_note_filter(result, notes)

        # Base model filtering
        result = self._apply_base_model_filter(result, base_models)

        return result

    def sort_shortcuts_by_value(
        self,
        shortcuts: Dict[str, Dict[str, Any]],
        key: str,
        reverse: bool = False,
    ) -> Dict[str, Dict[str, Any]]:
        """Sort shortcuts by specific field value."""
        sorted_data = sorted(shortcuts.items(), key=lambda x: x[1].get(key), reverse=reverse)
        return dict(sorted_data)

    def sort_shortcuts_by_model_id(
        self, shortcuts: Dict[str, Dict[str, Any]], reverse: bool = False
    ) -> Dict[str, Dict[str, Any]]:
        """Sort shortcuts by model ID."""
        sorted_data: Dict[str, Dict[str, Any]] = {}
        for k in sorted(shortcuts.keys(), reverse=reverse):
            sorted_data[k] = shortcuts[k]
        return sorted_data

    def extract_all_tags(self) -> List[str]:
        """Extract unique tags from all shortcuts."""
        ISC = self._collection_manager.load_shortcuts()
        if not ISC:
            return []

        tags_set = set()
        for item in ISC.values():
            if 'tags' in item and isinstance(item['tags'], list):
                for tag in item['tags']:
                    if isinstance(tag, dict) and 'name' in tag:
                        tags_set.add(tag['name'])
                    else:
                        tags_set.add(str(tag))

        return list(tags_set)

    def _apply_type_filter(
        self,
        shortcuts: List[Dict[str, Any]],
        types: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        """Apply model type filtering."""
        if not types:
            return shortcuts

        tmp_types = []
        for sc_type in types:
            try:
                tmp_types.append(settings.ui_typenames[sc_type])
            except Exception:
                continue

        return [v for v in shortcuts if v and v.get('type') in tmp_types]

    def _apply_keyword_filter(
        self,
        shortcuts: List[Dict[str, Any]],
        keywords: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        """Apply keyword search filtering."""
        if not keywords:
            return shortcuts

        result = []
        for v in shortcuts:
            if not v:
                continue
            name = v.get('name', '').lower()
            for key in keywords:
                if key in name:
                    result.append(v)
                    break

        return result

    def _apply_tag_filter(
        self,
        shortcuts: List[Dict[str, Any]],
        tags: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        """Apply tag-based filtering."""
        if not tags:
            return shortcuts

        result = []
        for v in shortcuts:
            if not v or 'tags' not in v or not v['tags']:
                continue

            v_tags = []
            for tag in v['tags']:
                if isinstance(tag, dict) and 'name' in tag:
                    v_tags.append(tag['name'].lower())
                else:
                    v_tags.append(str(tag).lower())

            if set(v_tags) & set(tags):
                result.append(v)

        return result

    def _apply_note_filter(
        self,
        shortcuts: List[Dict[str, Any]],
        notes: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        """Apply note content filtering."""
        if not notes:
            return shortcuts

        result = []
        for v in shortcuts:
            note_field = v.get('note')
            if not note_field:
                continue

            note_lower = str(note_field).lower()
            for note in notes:
                if note in note_lower:
                    result.append(v)
                    break

        return result

    def _apply_base_model_filter(
        self,
        shortcuts: List[Dict[str, Any]],
        base_models: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        """Apply base model filtering."""
        if not base_models:
            return shortcuts

        result = []
        for v in shortcuts:
            model_id = str(v.get('id'))
            try:
                is_base = self._model_processor.is_baseModel(model_id, base_models)
            except Exception:
                is_base = False

            if is_base:
                result.append(v)

        return result

    def _apply_classification_filter(
        self,
        shortcuts: List[Dict[str, Any]],
        classifications: Optional[List[str]],
    ) -> List[Dict[str, Any]]:
        """Apply classification-based filtering with AND logic."""
        if not classifications:
            return shortcuts

        clfs: List[Any] = []
        CISC = classification.load()
        if CISC:
            for name in classifications:
                name_list = classification.get_shortcut_list(CISC, name)
                if name_list:
                    if clfs:
                        clfs = list(set(clfs) & set(name_list))
                    else:
                        clfs = name_list
                else:
                    clfs = []
                    break

            clfs = list(set(clfs))

        if not clfs:
            return []

        key_set = set(str(mid) for mid in clfs)
        return [v for v in shortcuts if v and str(v.get('id')) in key_set]
