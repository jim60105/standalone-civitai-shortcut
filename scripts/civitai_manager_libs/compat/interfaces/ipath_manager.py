"""
Path Manager Interface

Provides unified access to path information across WebUI and standalone modes.
"""

from abc import ABC, abstractmethod


class IPathManager(ABC):
    """Abstract interface for path management across different execution modes."""

    @abstractmethod
    def get_base_path(self) -> str:
        """
        Get the base path of the application.

        Returns:
            str: The base directory path
        """
        pass

    @abstractmethod
    def get_extension_path(self) -> str:
        """
        Get the extension installation path.

        Returns:
            str: The extension directory path
        """
        pass

    @abstractmethod
    def get_models_path(self) -> str:
        """
        Get the models directory path.

        Returns:
            str: The models directory path
        """
        pass

    @abstractmethod
    def get_model_folder_path(self, model_type: str) -> str:
        """
        Get the specific folder path for a model type.

        Args:
            model_type (str): The type of model (e.g., 'Checkpoint', 'LORA')

        Returns:
            str: The folder path for the specified model type
        """
        pass

    @abstractmethod
    def get_config_path(self) -> str:
        """
        Get the configuration file path.

        Returns:
            str: The configuration file path
        """
        pass

    @abstractmethod
    def ensure_directory_exists(self, path: str) -> bool:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            path (str): The directory path to ensure exists

        Returns:
            bool: True if directory exists or was created successfully
        """
        pass
