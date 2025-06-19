"""Configuration Manager Interface.

Provides unified access to configuration management across execution modes.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict


class IConfigManager(ABC):
    """
    Abstract interface for configuration management across different execution modes.

    This interface defines the contract for configuration managers, ensuring unified access to
    configuration data, persistence, and model folder mappings across both WebUI and standalone
    execution environments. All implementations must provide robust error handling and thread safety
    as specified in the project documentation.
    """

    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a configuration value by key.

        Args:
            key (str): The configuration key identifier.
            default (Any, optional): Value to return if the key does not exist. Defaults to None.

        Returns:
            Any: The configuration value if found, otherwise the default value.
        """
        pass

    @abstractmethod
    def set_config(self, key: str, value: Any) -> None:
        """
        Set a configuration value by key.

        Args:
            key (str): The configuration key identifier.
            value (Any): The value to set for the configuration key.

        Returns:
            None
        """
        pass

    @abstractmethod
    def save_config(self) -> bool:
        """
        Persist the current configuration to storage (e.g., file system).

        Returns:
            bool: True if the configuration was saved successfully, False otherwise.
        """
        pass

    @abstractmethod
    def load_config(self) -> bool:
        """
        Load configuration from persistent storage.

        Returns:
            bool: True if the configuration was loaded successfully, False otherwise.
        """
        pass

    @abstractmethod
    def get_all_configs(self) -> Dict[str, Any]:
        """
        Retrieve all configuration key-value pairs.

        Returns:
            Dict[str, Any]: Dictionary containing all configuration keys and their values.
        """
        pass

    @abstractmethod
    def has_config(self, key: str) -> bool:
        """
        Check if a configuration key exists in the configuration data.

        Args:
            key (str): The configuration key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        pass

    @abstractmethod
    def get_model_folders(self) -> Dict[str, str]:
        """
        Retrieve the mapping of model types to their corresponding folder paths.

        Returns:
            Dict[str, str]: Dictionary mapping model type identifiers to folder paths.
        """
        pass

    @abstractmethod
    def get_embeddings_dir(self) -> Optional[str]:
        """
        Retrieve the embeddings directory path.

        Returns:
            Optional[str]: The embeddings directory path if configured, otherwise None.
        """
        pass

    @abstractmethod
    def get_hypernetwork_dir(self) -> Optional[str]:
        """
        Retrieve the hypernetwork directory path.

        Returns:
            Optional[str]: The hypernetwork directory path if configured, otherwise None.
        """
        pass

    @abstractmethod
    def get_ckpt_dir(self) -> Optional[str]:
        """
        Retrieve the checkpoint (Stable Diffusion) directory path.

        Returns:
            Optional[str]: The checkpoint directory path if configured, otherwise None.
        """
        pass

    @abstractmethod
    def get_lora_dir(self) -> Optional[str]:
        """
        Retrieve the LoRA model directory path.

        Returns:
            Optional[str]: The LoRA directory path if configured, otherwise None.
        """
        pass

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """
        Alias for get_config().

        Args:
            key (str): The configuration key identifier.
            default (Any, optional): Value to return if the key does not exist. Defaults to None.

        Returns:
            Any: The configuration value if found, otherwise the default value.
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        Alias for set_config().

        Args:
            key (str): The configuration key identifier.
            value (Any): The value to set for the configuration key.

        Returns:
            None
        """
        pass
