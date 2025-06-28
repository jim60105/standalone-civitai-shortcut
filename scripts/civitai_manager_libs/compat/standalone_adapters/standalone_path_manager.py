"""Standalone Path Manager.

Provides comprehensive path management for standalone execution without WebUI dependencies.
Enhanced with flexible configuration and cross-platform support.
"""

import os
import json
from typing import Dict, Optional
from .. import paths
from ..interfaces.ipath_manager import IPathManager
from ...logging_config import get_logger

logger = get_logger(__name__)


class StandalonePathManager(IPathManager):
    """
    Enhanced path manager implementation for standalone mode.

    Provides comprehensive path management including:
    - Flexible base path detection
    - Configurable model folder paths
    - Cross-platform path handling
    - Directory creation and validation
    - Path normalization and validation.
    """

    def __init__(self, base_path: Optional[str] = None, config_path: Optional[str] = None):
        """
        Initialize the standalone path manager.

        Args:
            base_path: Optional custom base path (auto-detected if None)
            config_path: Optional path to configuration file.
        """
        self._custom_base_path = base_path
        self._config_path = config_path
        self._debug_mode = False
        self._base_path = self._detect_base_path()
        # Initialize SC and SD data root directories
        self._sc_data_root = os.path.join(self._base_path, "data_sc")
        self._sd_data_root = os.path.join(self._base_path, "data")
        self._model_folders = self._load_model_folders_config()

        # Ensure essential directories exist
        self._ensure_essential_directories()

    def get_script_path(self) -> str:
        """
        Get the main script path.

        In standalone mode, this returns our extension's base path.
        """
        logger.debug(f"get_script_path: {self._base_path}")
        return self._base_path

    def get_user_data_path(self) -> str:
        """
        Get the user data directory path.

        In standalone mode, this returns our extension's data directory.
        """
        result = str(paths.data_path)
        logger.debug(f"get_user_data_path: {result}")
        return result

    def get_base_path(self) -> str:
        """Get the base path for standalone mode."""
        logger.debug(f"get_base_path: {self._base_path}")
        return self._base_path

    def get_extension_path(self) -> str:
        """Get extension path (same as base path in standalone mode)."""
        logger.debug(f"get_extension_path: {self._base_path}")
        return self._base_path

    def get_models_path(self) -> str:
        """Get models directory path."""
        result = str(paths.models_path)
        logger.debug(f"get_models_path: {result}")
        return result

    def get_model_folder_path(self, model_type: str) -> str:
        """
        Get specific model folder path with enhanced type handling.

        Args:
            model_type: Type of model (case-insensitive)

        Returns:
            Absolute path to the model folder.
        """
        # Normalize model type for lookup
        normalized_type = self._normalize_model_type(model_type)

        if normalized_type in self._model_folders:
            folder_path = self._model_folders[normalized_type]

            # Handle absolute vs relative paths
            if os.path.isabs(folder_path):
                full_path = folder_path
            else:
                full_path = os.path.join(self._base_path, folder_path)
        else:
            # Default fallback - create a folder under models
            full_path = os.path.join(self.get_models_path(), model_type)

        # Ensure the directory exists
        self.ensure_directory_exists(full_path)
        logger.debug(f"get_model_folder_path({model_type}): {full_path}")
        return full_path

    def get_model_path(self, model_type: str) -> str:
        """
        Get the directory path for a specific model type.

        Args:
            model_type: The type of model (e.g., 'Stable-diffusion', 'Lora', etc.)

        Returns:
            str: The absolute path to the model type directory.
        """
        result = self.get_model_folder_path(model_type)
        logger.debug(f"get_model_path({model_type}): {result}")
        return result

    def get_config_path(self) -> str:
        """Get configuration file path."""
        if self._config_path:
            result = self._config_path
        else:
            result = os.path.join(self._base_path, "setting.json")
        logger.debug(f"get_config_path: {result}")
        return result

    def ensure_directory_exists(self, path: str) -> bool:
        """
        Ensure directory exists with enhanced error handling.

        Args:
            path: Directory path to ensure exists

        Returns:
            True if directory exists or was created successfully.
        """
        try:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
                self._log_debug(f"Created directory: {path}")

            return os.path.isdir(path)
        except PermissionError as e:
            self._log_debug(f"Permission denied creating directory {path}: {e}")
            return False
        except Exception as e:
            self._log_debug(f"Error creating directory {path}: {e}")
            return False

    def get_output_path(self) -> str:
        """Get output directory path for generated images."""
        output_path = os.path.join(self._base_path, "outputs")
        self.ensure_directory_exists(output_path)
        return output_path

    def get_cache_path(self) -> str:
        """Get cache directory path."""
        cache_path = os.path.join(self._base_path, "cache")
        self.ensure_directory_exists(cache_path)
        return cache_path

    def get_logs_path(self) -> str:
        """Get logs directory path."""
        logs_path = os.path.join(self._base_path, "logs")
        self.ensure_directory_exists(logs_path)
        return logs_path

    def get_temp_path(self) -> str:
        """Get temporary directory path."""
        temp_path = os.path.join(self._base_path, "temp")
        self.ensure_directory_exists(temp_path)
        return temp_path

    def validate_path(self, path: str) -> bool:
        """
        Validate if a path is accessible and within safe boundaries.

        Args:
            path: Path to validate

        Returns:
            True if path is valid and accessible.
        """
        try:
            # Check if path exists
            if not os.path.exists(path):
                return False

            # Check if path is within base directory (security check)
            real_path = os.path.realpath(path)
            real_base = os.path.realpath(self._base_path)

            return real_path.startswith(real_base)
        except Exception:
            return False

    def get_relative_path(self, full_path: str) -> str:
        """
        Get path relative to base directory.

        Args:
            full_path: Absolute path

        Returns:
            Path relative to base directory.
        """
        try:
            return os.path.relpath(full_path, self._base_path)
        except ValueError:
            return full_path

    def resolve_path(self, path: str) -> str:
        """
        Resolve a potentially relative path to absolute path.

        Args:
            path: Path to resolve (may be relative or absolute)

        Returns:
            Absolute path.
        """
        if os.path.isabs(path):
            return path
        else:
            return os.path.abspath(os.path.join(self._base_path, path))

    def get_sc_data_path(self) -> str:
        """Get path to SC data directory."""
        return self._sc_data_root

    def get_sd_data_path(self) -> str:
        """Get path to SD data directory."""
        return self._sd_data_root

    def get_all_model_paths(self) -> Dict[str, str]:
        """
        Get all configured model paths.

        Returns:
            Dictionary mapping model types to their paths.
        """
        result = {}
        for model_type in self._model_folders:
            result[model_type] = self.get_model_folder_path(model_type)

        return result

    def add_model_folder(self, model_type: str, folder_path: str, save_config: bool = True) -> bool:
        """
        Add or update a model folder configuration.

        Args:
            model_type: Type of model
            folder_path: Path to the folder (can be relative or absolute)
            save_config: Whether to save the configuration to file

        Returns:
            True if successfully added.
        """
        try:
            self._model_folders[model_type] = folder_path

            # Ensure the directory exists
            full_path = self.get_model_folder_path(model_type)
            success = self.ensure_directory_exists(full_path)

            if success and save_config:
                self._save_model_folders_config()

            return success
        except Exception as e:
            self._log_debug(f"Error adding model folder {model_type}: {e}")
            return False

    def set_debug_mode(self, enabled: bool):
        """Enable or disable debug mode."""
        self._debug_mode = enabled

    def ensure_directories(self) -> bool:
        """
        Ensure all required directories for standalone mode exist.

        Creates models, outputs, logs, cache, config, and user data folders.

        Returns:
            bool: True if all directories exist or were created successfully, False otherwise.
        """
        required_dirs = [
            self.get_models_path(),
            self.get_output_path(),
            self.get_logs_path(),
            self.get_cache_path(),
            self.get_user_data_path(),
            os.path.dirname(self.get_config_path()),
        ]
        success = True
        for d in required_dirs:
            if self.ensure_directory_exists(d):
                logger.debug(f"Ensured directory exists: {d}")
            else:
                logger.error(f"Failed to create directory: {d}")
                success = False
        return success

    def _detect_base_path(self) -> str:
        """Detect the base path for the application with enhanced logic."""
        if self._custom_base_path:
            return os.path.abspath(self._custom_base_path)

        # Start from the current file location
        current_file = os.path.abspath(__file__)

        # Go up from: compat/standalone_adapters/standalone_path_manager.py
        # to find the scripts directory
        path_parts = current_file.split(os.sep)

        # Look for 'scripts' directory in the path
        scripts_index = None
        for i, part in enumerate(reversed(path_parts)):
            if part == "scripts":
                scripts_index = len(path_parts) - i - 1
                break

        if scripts_index is not None:
            # Return parent of scripts directory
            scripts_path = os.sep.join(path_parts[:scripts_index])
            if os.path.exists(os.path.join(scripts_path, "scripts", "civitai_shortcut.py")):
                return scripts_path

        # Fallback: go up levels until we find civitai_shortcut.py
        base_path = current_file
        for _ in range(6):  # Reasonable limit
            base_path = os.path.dirname(base_path)
            expected_script = os.path.join(base_path, "scripts", "civitai_shortcut.py")
            if os.path.exists(expected_script):
                return base_path

        # Final fallback to current working directory
        return os.getcwd()

    def _load_model_folders_config(self) -> Dict[str, str]:
        """Load model folder configuration from file or use defaults."""
        config_file = os.path.join(self._base_path, "model_folders.json")

        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self._log_debug(f"Loaded model folders config from {config_file}")
                    return config
            except Exception as e:
                self._log_debug(f"Error loading model folders config: {e}")

        return self._get_default_model_folders()

    def _save_model_folders_config(self) -> bool:
        """Save model folder configuration to file."""
        config_file = os.path.join(self._base_path, "model_folders.json")

        try:
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(self._model_folders, f, indent=2, ensure_ascii=False)

            self._log_debug(f"Saved model folders config to {config_file}")
            return True
        except Exception as e:
            self._log_debug(f"Error saving model folders config: {e}")
            return False

    def _get_default_model_folders(self) -> Dict[str, str]:
        """Get default model folder configuration with comprehensive types."""
        # Use data_path for models to align with WebUI paths
        models_base = "data/models"

        return {
            # Direct WebUI directory mappings (primary)
            "Stable-diffusion": os.path.join(models_base, "Stable-diffusion"),
            "Lora": os.path.join(models_base, "Lora"),
            "VAE": os.path.join(models_base, "VAE"),
            "embeddings": os.path.join(models_base, "embeddings"),
            "hypernetworks": os.path.join(models_base, "hypernetworks"),
            "ControlNet": os.path.join(models_base, "ControlNet"),
            # Standard model types (aliases)
            "Checkpoint": os.path.join(models_base, "Stable-diffusion"),
            "LORA": os.path.join(models_base, "Lora"),
            "LoCon": os.path.join(models_base, "LyCORIS"),
            "TextualInversion": os.path.join(models_base, "embeddings"),
            "Hypernetwork": os.path.join(models_base, "hypernetworks"),
            # Advanced model types
            "AestheticGradient": os.path.join(models_base, "aesthetic_embeddings"),
            "Poses": os.path.join(models_base, "Poses"),
            "Wildcards": os.path.join(models_base, "wildcards"),
            "Other": os.path.join(models_base, "Other"),
            "Unknown": os.path.join(models_base, "Unknown"),
            # Additional Networks
            "ANLORA": os.path.join(models_base, "additional_networks", "lora"),
            "LoCon_Additional": os.path.join(models_base, "additional_networks", "locon"),
            # Upscaling models
            "ESRGAN": os.path.join(models_base, "ESRGAN"),
            "RealESRGAN": os.path.join(models_base, "RealESRGAN"),
            "SwinIR": os.path.join(models_base, "SwinIR"),
            # CLIP models
            "CLIP": os.path.join(models_base, "CLIP"),
            "CLIP_vision": os.path.join(models_base, "CLIP_vision"),
            # Other specialized types
            "Deepbooru": os.path.join(models_base, "deepbooru"),
            "BLIP": os.path.join(models_base, "BLIP"),
        }

    def _normalize_model_type(self, model_type: str) -> str:
        """
        Normalize model type string for consistent lookup.

        Args:
            model_type: Raw model type string

        Returns:
            Normalized model type.
        """
        # Basic normalization
        normalized = model_type.strip()

        # Handle common aliases
        aliases = {
            "checkpoints": "Stable-diffusion",
            "checkpoint": "Stable-diffusion",
            "lora": "Lora",
            "locon": "LoCon",
            "embedding": "embeddings",
            "textual_inversion": "embeddings",
            "ti": "embeddings",
            "hypernetworks": "hypernetworks",
            "hypernet": "hypernetworks",
            "vae": "VAE",
            "controlnet": "ControlNet",
            "cn": "ControlNet",
        }

        normalized_lower = normalized.lower()
        return aliases.get(normalized_lower, normalized)

    def _ensure_essential_directories(self):
        """Ensure essential directories exist."""
        essential_dirs = [
            self.get_models_path(),
            self.get_output_path(),
            self.get_cache_path(),
            self.get_logs_path(),
        ]

        for directory in essential_dirs:
            self.ensure_directory_exists(directory)

    def _log_debug(self, message: str):
        """Log debug message if debug mode is enabled."""
        if self._debug_mode:
            logger.debug(f"StandalonePathManager: {message}")
