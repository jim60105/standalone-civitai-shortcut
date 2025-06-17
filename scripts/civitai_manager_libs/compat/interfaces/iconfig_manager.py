"""
Configuration Manager Interface

Provides unified access to configuration management across execution modes.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Dict


class IConfigManager(ABC):
    """Abstract interface for configuration management across different execution modes."""
    
    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key (str): The configuration key
            default (Any): Default value if key doesn't exist
            
        Returns:
            Any: The configuration value
        """
        pass
    
    @abstractmethod
    def set_config(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key (str): The configuration key
            value (Any): The value to set
        """
        pass
    
    @abstractmethod
    def save_config(self) -> bool:
        """
        Save the configuration to persistent storage.
        
        Returns:
            bool: True if saved successfully
        """
        pass
    
    @abstractmethod
    def load_config(self) -> bool:
        """
        Load configuration from persistent storage.
        
        Returns:
            bool: True if loaded successfully
        """
        pass
    
    @abstractmethod
    def get_all_configs(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns:
            Dict[str, Any]: Dictionary of all configuration values
        """
        pass
    
    @abstractmethod
    def has_config(self, key: str) -> bool:
        """
        Check if a configuration key exists.
        
        Args:
            key (str): The configuration key to check
            
        Returns:
            bool: True if key exists
        """
        pass
    
    @abstractmethod
    def get_model_folders(self) -> Dict[str, str]:
        """
        Get model folder configurations.
        
        Returns:
            Dict[str, str]: Mapping of model types to folder paths
        """
        pass
    
    @abstractmethod
    def get_embeddings_dir(self) -> Optional[str]:
        """
        Get embeddings directory path.
        
        Returns:
            Optional[str]: Embeddings directory path or None
        """
        pass
    
    @abstractmethod
    def get_hypernetwork_dir(self) -> Optional[str]:
        """
        Get hypernetwork directory path.
        
        Returns:
            Optional[str]: Hypernetwork directory path or None
        """
        pass
    
    @abstractmethod
    def get_ckpt_dir(self) -> Optional[str]:
        """
        Get checkpoint directory path.
        
        Returns:
            Optional[str]: Checkpoint directory path or None
        """
        pass
    
    @abstractmethod
    def get_lora_dir(self) -> Optional[str]:
        """
        Get LoRA directory path.
        
        Returns:
            Optional[str]: LoRA directory path or None
        """
        pass
