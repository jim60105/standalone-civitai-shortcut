"""
Model Handlers Module

Manages model-specific UI events and operations.
Handles model loading, processing, and model-related interactions.
"""

from typing import Any, Dict, List
from ..logging_config import get_logger
from ..error_handler import with_error_handling

logger = get_logger(__name__)


class ModelHandlers:
    """
    Manages model-specific UI events and operations.
    Handles model loading, processing, and model-related interactions.
    """

    def __init__(self, ui_controllers=None):
        """
        Initialize model handlers.

        Args:
            ui_controllers: UI controllers instance
        """
        self.ui_controllers = ui_controllers
        self._loaded_models = {}
        self._model_cache = {}
        self._selected_model = None

    @with_error_handling("Failed to load model")
    def load_model(self, model_id: str, model_data: Dict[str, Any]) -> bool:
        """
        Load model data.

        Args:
            model_id: Model identifier
            model_data: Model data to load

        Returns:
            bool: True if successful, False otherwise
        """
        if not self._validate_model_data(model_data):
            logger.error(f"Invalid model data for {model_id}")
            return False

        # Process model data
        processed_data = self._process_model_data(model_data)
        self._loaded_models[model_id] = processed_data

        # Cache for quick access
        self._model_cache[model_id] = processed_data

        # Update UI state
        if self.ui_controllers:
            self.ui_controllers.update_ui_state('loaded_models', self._loaded_models)

        logger.info(f"Loaded model: {model_id}")
        return True

    @with_error_handling("Failed to select model")
    def select_model(self, model_id: str) -> bool:
        """
        Select a model.

        Args:
            model_id: Model identifier

        Returns:
            bool: True if successful, False otherwise
        """
        if model_id not in self._loaded_models:
            logger.warning(f"Model not loaded: {model_id}")
            return False

        self._selected_model = model_id

        # Update UI state
        if self.ui_controllers:
            self.ui_controllers.update_ui_state('selected_model', model_id)
            self.ui_controllers.update_ui_state(
                'selected_model_data', self._loaded_models[model_id]
            )

        logger.debug(f"Selected model: {model_id}")
        return True

    def get_selected_model(self) -> Dict[str, Any]:
        """
        Get currently selected model data.

        Returns:
            Dict[str, Any]: Selected model data or empty dict
        """
        if self._selected_model and self._selected_model in self._loaded_models:
            return self._loaded_models[self._selected_model].copy()
        return {}

    def get_loaded_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all loaded models.

        Returns:
            Dict[str, Dict[str, Any]]: Loaded models
        """
        return self._loaded_models.copy()

    @with_error_handling("Failed to unload model")
    def unload_model(self, model_id: str) -> bool:
        """
        Unload a model.

        Args:
            model_id: Model identifier

        Returns:
            bool: True if successful, False otherwise
        """
        if model_id not in self._loaded_models:
            return False

        # Remove from loaded models
        del self._loaded_models[model_id]

        # Remove from cache
        if model_id in self._model_cache:
            del self._model_cache[model_id]

        # Clear selection if this model was selected
        if self._selected_model == model_id:
            self._selected_model = None
            if self.ui_controllers:
                self.ui_controllers.update_ui_state('selected_model', None)

        # Update UI state
        if self.ui_controllers:
            self.ui_controllers.update_ui_state('loaded_models', self._loaded_models)

        logger.info(f"Unloaded model: {model_id}")
        return True

    @with_error_handling("Failed to update model data")
    def update_model_data(self, model_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update model data.

        Args:
            model_id: Model identifier
            updates: Data updates

        Returns:
            bool: True if successful, False otherwise
        """
        if model_id not in self._loaded_models:
            logger.warning(f"Model not loaded: {model_id}")
            return False

        # Apply updates
        model_data = self._loaded_models[model_id]
        model_data.update(updates)

        # Update cache
        self._model_cache[model_id] = model_data

        # Update UI state if this is the selected model
        if self._selected_model == model_id and self.ui_controllers:
            self.ui_controllers.update_ui_state('selected_model_data', model_data)

        logger.debug(f"Updated model data for: {model_id}")
        return True

    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Get model information.

        Args:
            model_id: Model identifier

        Returns:
            Dict[str, Any]: Model information
        """
        if model_id in self._loaded_models:
            return self._loaded_models[model_id].copy()
        return {}

    def search_models(self, query: str) -> List[Dict[str, Any]]:
        """
        Search loaded models.

        Args:
            query: Search query

        Returns:
            List[Dict[str, Any]]: Matching models
        """
        if not query:
            return list(self._loaded_models.values())

        query_lower = query.lower()
        matching_models = []

        for model_data in self._loaded_models.values():
            # Search in name
            name = model_data.get('name', '').lower()
            if query_lower in name:
                matching_models.append(model_data)
                continue

            # Search in description
            description = model_data.get('description', '').lower()
            if query_lower in description:
                matching_models.append(model_data)
                continue

            # Search in tags
            tags = model_data.get('tags', [])
            if any(query_lower in tag.lower() for tag in tags):
                matching_models.append(model_data)

        return matching_models

    def filter_models_by_type(self, model_type: str) -> List[Dict[str, Any]]:
        """
        Filter models by type.

        Args:
            model_type: Model type to filter by

        Returns:
            List[Dict[str, Any]]: Models of specified type
        """
        filtered_models = []
        for model_data in self._loaded_models.values():
            if model_data.get('type') == model_type:
                filtered_models.append(model_data)
        return filtered_models

    def get_model_types(self) -> List[str]:
        """
        Get list of available model types.

        Returns:
            List[str]: Model types
        """
        types = set()
        for model_data in self._loaded_models.values():
            model_type = model_data.get('type')
            if model_type:
                types.add(model_type)
        return sorted(list(types))

    def get_model_statistics(self) -> Dict[str, Any]:
        """
        Get model statistics.

        Returns:
            Dict[str, Any]: Model statistics
        """
        total_models = len(self._loaded_models)
        type_counts = {}

        for model_data in self._loaded_models.values():
            model_type = model_data.get('type', 'Unknown')
            type_counts[model_type] = type_counts.get(model_type, 0) + 1

        return {
            'total_models': total_models,
            'type_counts': type_counts,
            'selected_model': self._selected_model,
            'cache_size': len(self._model_cache),
        }

    def clear_model_cache(self) -> None:
        """Clear model cache."""
        self._model_cache.clear()
        logger.info("Model cache cleared")

    def _validate_model_data(self, model_data: Dict[str, Any]) -> bool:
        """
        Validate model data structure.

        Args:
            model_data: Model data to validate

        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['id', 'name']
        for field in required_fields:
            if field not in model_data:
                logger.error(f"Missing required field: {field}")
                return False

        return True

    def _process_model_data(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process model data for loading.

        Args:
            model_data: Raw model data

        Returns:
            Dict[str, Any]: Processed model data
        """
        processed_data = model_data.copy()

        # Add processing timestamp
        import time

        processed_data['loaded_at'] = time.time()

        # Ensure required fields have defaults
        processed_data.setdefault('description', '')
        processed_data.setdefault('tags', [])
        processed_data.setdefault('type', 'Unknown')
        processed_data.setdefault('stats', {})

        # Process versions if present
        if 'modelVersions' in processed_data:
            processed_data['versions'] = self._process_model_versions(
                processed_data['modelVersions']
            )

        return processed_data

    def _process_model_versions(self, versions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process model versions.

        Args:
            versions: Model versions data

        Returns:
            List[Dict[str, Any]]: Processed versions
        """
        processed_versions = []
        for version in versions:
            processed_version = version.copy()
            processed_version.setdefault('files', [])
            processed_version.setdefault('images', [])
            processed_versions.append(processed_version)

        return processed_versions


class ModelValidator:
    """Validates model data and operations."""

    @staticmethod
    def validate_model_id(model_id: str) -> bool:
        """
        Validate model ID format.

        Args:
            model_id: Model ID to validate

        Returns:
            bool: True if valid, False otherwise
        """
        return bool(model_id and isinstance(model_id, str) and len(model_id.strip()) > 0)

    @staticmethod
    def validate_model_structure(model_data: Dict[str, Any]) -> List[str]:
        """
        Validate model data structure.

        Args:
            model_data: Model data to validate

        Returns:
            List[str]: List of validation errors
        """
        errors = []

        # Check required fields
        required_fields = ['id', 'name', 'type']
        for field in required_fields:
            if field not in model_data:
                errors.append(f"Missing required field: {field}")
            elif not model_data[field]:
                errors.append(f"Empty required field: {field}")

        # Validate data types
        if 'id' in model_data and not isinstance(model_data['id'], (str, int)):
            errors.append("Model ID must be string or integer")

        if 'name' in model_data and not isinstance(model_data['name'], str):
            errors.append("Model name must be string")

        if 'tags' in model_data and not isinstance(model_data['tags'], list):
            errors.append("Model tags must be list")

        return errors


class ModelFormatter:
    """Formats model data for display."""

    @staticmethod
    def format_model_for_display(model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format model data for UI display.

        Args:
            model_data: Model data to format

        Returns:
            Dict[str, Any]: Formatted model data
        """
        formatted_data = {
            'id': model_data.get('id', ''),
            'name': model_data.get('name', 'Untitled'),
            'description': model_data.get('description', ''),
            'type': model_data.get('type', 'Unknown'),
            'tags': model_data.get('tags', []),
            'stats': model_data.get('stats', {}),
            'created_at': model_data.get('createdAt', ''),
            'updated_at': model_data.get('updatedAt', ''),
            'version_count': len(model_data.get('modelVersions', [])),
            'image_count': len(model_data.get('images', [])),
            'rating': model_data.get('stats', {}).get('rating', 0),
            'download_count': model_data.get('stats', {}).get('downloadCount', 0),
        }

        return formatted_data

    @staticmethod
    def format_model_list(models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format list of models for display.

        Args:
            models: List of model data

        Returns:
            List[Dict[str, Any]]: Formatted model list
        """
        return [ModelFormatter.format_model_for_display(model) for model in models]

    @staticmethod
    def get_model_summary(model_data: Dict[str, Any]) -> str:
        """
        Get model summary string.

        Args:
            model_data: Model data

        Returns:
            str: Model summary
        """
        name = model_data.get('name', 'Untitled')
        model_type = model_data.get('type', 'Unknown')
        rating = model_data.get('stats', {}).get('rating', 0)
        downloads = model_data.get('stats', {}).get('downloadCount', 0)

        return f"{name} ({model_type}) - Rating: {rating:.1f}, Downloads: {downloads:,}"
