"""
WebUI Path Manager

Provides path management using AUTOMATIC1111 WebUI modules.
"""

import os

from .. import paths
from ..interfaces.ipath_manager import IPathManager

try:
    from modules import paths as webui_paths
    from modules.paths_internal import (
        models_path as webui_models_path,
        script_path as webui_script_path,
        data_path as webui_data_path,
        extensions_dir,
        extensions_builtin_dir,
        default_output_dir,
    )
    from modules import shared

    WEBUI_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    webui_paths = None
    webui_models_path = None
    webui_script_path = None
    webui_data_path = None
    extensions_dir = None
    extensions_builtin_dir = None
    default_output_dir = None
    shared = None
    WEBUI_AVAILABLE = False


class WebUIPathManager(IPathManager):
    """Path manager implementation using WebUI modules."""

    def get_script_path(self) -> str:
        """
        Gets the absolute path to the main WebUI script directory.
        This follows AUTOMATIC1111's paths_internal.script_path pattern.
        """
        if WEBUI_AVAILABLE and webui_script_path:
            return webui_script_path
        return str(paths.script_path)

    def get_user_data_path(self) -> str:
        """
        Gets the data path from WebUI.
        This follows AUTOMATIC1111's paths_internal.data_path pattern.
        """
        if WEBUI_AVAILABLE and webui_data_path:
            return webui_data_path
        return str(paths.data_path)

    def get_models_path(self) -> str:
        """
        Gets the main models path from the WebUI.
        This follows AUTOMATIC1111's paths_internal.models_path pattern.
        """
        if WEBUI_AVAILABLE and webui_models_path:
            return webui_models_path
        return str(paths.models_path)

    def get_extensions_dir(self) -> str:
        """
        Gets the extensions directory path.
        This follows AUTOMATIC1111's paths_internal.extensions_dir pattern.
        """
        if WEBUI_AVAILABLE and extensions_dir:
            return extensions_dir
        return os.path.join(self.get_user_data_path(), "extensions")

    def get_extensions_builtin_dir(self) -> str:
        """
        Gets the built-in extensions directory path.
        This follows AUTOMATIC1111's paths_internal.extensions_builtin_dir pattern.
        """
        if WEBUI_AVAILABLE and extensions_builtin_dir:
            return extensions_builtin_dir
        return os.path.join(self.get_script_path(), "extensions-builtin")

    def get_output_dir(self) -> str:
        """
        Gets the default output directory path.
        This follows AUTOMATIC1111's paths_internal.default_output_dir pattern.
        """
        if WEBUI_AVAILABLE and default_output_dir:
            return default_output_dir
        return os.path.join(self.get_user_data_path(), "outputs")

    def get_model_folder_path(self, model_type: str) -> str:
        """
        Get specific model folder path.
        Uses WebUI's standard model directory structure.
        """
        return os.path.join(self.get_models_path(), model_type)

    def get_config_path(self) -> str:
        """
        Get configuration file path.
        Stores in the data directory following WebUI patterns.
        """
        return os.path.join(self.get_user_data_path(), "setting.json")

    def ensure_directory_exists(self, path: str) -> bool:
        """
        Ensure directory exists.
        Uses os.makedirs with exist_ok=True following WebUI patterns.
        """
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception:
            return False

    def is_webui_available(self) -> bool:
        """
        Check if running within AUTOMATIC1111 WebUI environment.
        """
        return WEBUI_AVAILABLE
