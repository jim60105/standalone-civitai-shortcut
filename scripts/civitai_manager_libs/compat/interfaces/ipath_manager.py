"""Path Manager Interface.

Provides unified access to path information across WebUI and standalone modes.
"""

from abc import ABC, abstractmethod


class IPathManager(ABC):
    """Abstract interface for path management across different execution modes."""

    @abstractmethod
    def get_base_path(self) -> str:
        """
        Get the base path of the application or extension.

        In standalone mode, this is the root directory of the extension.
        In WebUI mode, this is the root directory of the WebUI environment.

        Returns:
            str: The base directory path.
        """
        pass

    @abstractmethod
    def get_extension_path(self) -> str:
        """
        Get the extension directory path.

        In standalone mode, this is the same as the base path.
        In WebUI mode, this is the directory where the extension is installed.

        Returns:
            str: The extension directory path.
        """
        pass

    @abstractmethod
    def ensure_directories(self) -> bool:
        """
        Ensure that all required directories for the application or extension exist.

        This should create any necessary directories for operation, such as data, models, and config
        folders.

        Returns:
            bool: True if all directories exist or were created successfully, False otherwise.
        """
        pass

    @abstractmethod
    def get_model_path(self, model_type: str) -> str:
        """
        Get the directory path for a specific model type.

        Args:
            model_type: The type of model (e.g., 'Stable-diffusion', 'Lora', etc.)

        Returns:
            str: The absolute path to the model type directory.
        """
        pass

    @abstractmethod
    def get_script_path(self) -> str:
        """
        Get the main script path.

        In WebUI mode, this returns the WebUI's script_path.
        In standalone mode, this returns our extension's base path.

        Returns:
            str: The script path.
        """
        pass

    @abstractmethod
    def get_user_data_path(self) -> str:
        """
        Get the user data directory path.

        In WebUI mode, this returns the WebUI's data_path.
        In standalone mode, this returns our extension's data directory.

        Returns:
            str: The user data directory path.
        """
        pass

    @abstractmethod
    def get_models_path(self) -> str:
        """
        Get the models directory path.

        In WebUI mode, this returns the WebUI's models_path.
        In standalone mode, this returns our extension's models directory.

        Returns:
            str: The models directory path.
        """
        pass

    @abstractmethod
    def get_model_folder_path(self, model_type: str) -> str:
        """
        Get specific model folder path for a given model type.

        Args:
            model_type: The type of model (e.g., 'Stable-diffusion', 'Lora', etc.)

        Returns:
            str: The model folder path.
        """
        pass

    @abstractmethod
    def get_config_path(self) -> str:
        """
        Get the configuration file path.

        Returns:
            str: The configuration file path.
        """
        pass

    @abstractmethod
    def ensure_directory_exists(self, path: str) -> bool:
        """
        Ensure that a directory exists, creating it if necessary.

        Args:
            path: The directory path to ensure exists

        Returns:
            bool: True if directory exists or was created successfully, False otherwise.
        """
        pass
