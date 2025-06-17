"""
Standalone Path Manager

Provides path management for standalone execution without WebUI dependencies.
"""

import os
from typing import Dict

from ..interfaces.ipath_manager import IPathManager


class StandalonePathManager(IPathManager):
    """Path manager implementation for standalone mode."""
    
    def __init__(self):
        """Initialize the standalone path manager."""
        self._base_path = self._detect_base_path()
        self._model_folders = self._initialize_model_folders()
    
    def get_base_path(self) -> str:
        """Get the base path for standalone mode."""
        return self._base_path
    
    def get_extension_path(self) -> str:
        """Get extension path (same as base path in standalone mode)."""
        return self._base_path
    
    def get_models_path(self) -> str:
        """Get models directory path."""
        return os.path.join(self._base_path, 'models')
    
    def get_model_folder_path(self, model_type: str) -> str:
        """Get specific model folder path."""
        if model_type in self._model_folders:
            folder_path = self._model_folders[model_type]
            if os.path.isabs(folder_path):
                return folder_path
            else:
                return os.path.join(self._base_path, folder_path)
        
        # Default fallback
        return os.path.join(self.get_models_path(), model_type)
    
    def get_config_path(self) -> str:
        """Get configuration file path."""
        return os.path.join(self._base_path, 'setting.json')
    
    def ensure_directory_exists(self, path: str) -> bool:
        """Ensure directory exists."""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception:
            return False
    
    def _detect_base_path(self) -> str:
        """Detect the base path for the application."""
        # Start from the current file location and go up to find the script directory
        current_file = os.path.abspath(__file__)
        
        # Go up from: compat/standalone_adapters/standalone_path_manager.py
        # to: scripts/civitai_manager_libs/
        base_path = current_file
        for _ in range(4):  # Go up 4 levels
            base_path = os.path.dirname(base_path)
        
        # Verify this is the correct path by checking for civitai_shortcut.py
        expected_script = os.path.join(base_path, 'civitai_shortcut.py')
        if os.path.exists(expected_script):
            return os.path.dirname(base_path)  # Return the scripts directory parent
        
        # Fallback to current working directory
        return os.getcwd()
    
    def _initialize_model_folders(self) -> Dict[str, str]:
        """Initialize default model folder configuration for standalone mode."""
        return {
            'Checkpoint': os.path.join("models", "Stable-diffusion"),
            'LORA': os.path.join("models", "Lora"),
            'LoCon': os.path.join("models", "LyCORIS"),
            'TextualInversion': os.path.join("models", "embeddings"),
            'Hypernetwork': os.path.join("models", "hypernetworks"),
            'AestheticGradient': os.path.join("models", "aesthetic_embeddings"),
            'Controlnet': os.path.join("models", "ControlNet"),
            'Poses': os.path.join("models", "Poses"),
            'Wildcards': os.path.join("models", "wildcards"),
            'Other': os.path.join("models", "Other"),
            'VAE': os.path.join("models", "VAE"),
            'ANLORA': os.path.join("models", "additional_networks", "lora"),
            'Unknown': os.path.join("models", "Unknown"),
        }
