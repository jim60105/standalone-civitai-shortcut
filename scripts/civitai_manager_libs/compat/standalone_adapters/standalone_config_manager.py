"""
Standalone Configuration Manager

Provides configuration management for standalone execution without WebUI dependencies.
"""

import json
import os
from typing import Any, Dict, Optional

from ..interfaces.iconfig_manager import IConfigManager


class StandaloneConfigManager(IConfigManager):
    """Configuration manager implementation for standalone mode."""
    
    def __init__(self):
        """Initialize the standalone configuration manager."""
        self._config_cache: Dict[str, Any] = {}
        self._config_loaded = False
        self._config_file_path = self._get_config_file_path()
        self._model_folders = self._get_default_model_folders()
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        if not self._config_loaded:
            self.load_config()
        
        return self._config_cache.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value."""
        if not self._config_loaded:
            self.load_config()
        
        self._config_cache[key] = value
    
    def save_config(self) -> bool:
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(self._config_file_path), exist_ok=True)
            with open(self._config_file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config_cache, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def load_config(self) -> bool:
        """Load configuration from file."""
        try:
            if os.path.exists(self._config_file_path):
                with open(self._config_file_path, 'r', encoding='utf-8') as f:
                    self._config_cache = json.load(f)
            else:
                self._config_cache = self._get_default_config()
            
            self._config_loaded = True
            return True
        except Exception:
            self._config_cache = self._get_default_config()
            self._config_loaded = True
            return False
    
    def get_all_configs(self) -> Dict[str, Any]:
        """Get all configuration values."""
        if not self._config_loaded:
            self.load_config()
        
        return self._config_cache.copy()
    
    def has_config(self, key: str) -> bool:
        """Check if configuration key exists."""
        if not self._config_loaded:
            self.load_config()
        
        return key in self._config_cache
    
    def get_model_folders(self) -> Dict[str, str]:
        """Get model folder configurations."""
        # Check for custom model folders in config
        custom_folders = self.get_config('model_folders', {})
        if custom_folders:
            merged_folders = self._model_folders.copy()
            merged_folders.update(custom_folders)
            return merged_folders
        
        return self._model_folders.copy()
    
    def get_embeddings_dir(self) -> Optional[str]:
        """Get embeddings directory path (not applicable in standalone mode)."""
        return self.get_config('embeddings_dir', None)
    
    def get_hypernetwork_dir(self) -> Optional[str]:
        """Get hypernetwork directory path (not applicable in standalone mode)."""
        return self.get_config('hypernetwork_dir', None)
    
    def get_ckpt_dir(self) -> Optional[str]:
        """Get checkpoint directory path (not applicable in standalone mode)."""
        return self.get_config('ckpt_dir', None)
    
    def get_lora_dir(self) -> Optional[str]:
        """Get LoRA directory path (not applicable in standalone mode)."""
        return self.get_config('lora_dir', None)
    
    def _get_config_file_path(self) -> str:
        """Get the path to the configuration file."""
        # Detect base path similar to path manager
        current_file = os.path.abspath(__file__)
        base_path = current_file
        for _ in range(4):  # Go up 4 levels
            base_path = os.path.dirname(base_path)
        
        return os.path.join(os.path.dirname(base_path), 'setting.json')
    
    def _get_default_model_folders(self) -> Dict[str, str]:
        """Get default model folder configuration."""
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
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            'civitai_api_key': '',
            'shortcut_update_when_start': True,
            'model_folders': self._model_folders,
            'ui_language': 'en',
            'download_path': 'models',
            'max_download_concurrent': 3,
            'auto_create_model_folder': True,
            'nsfw_filter': False,
            'preview_image_download': True,
            'info_file_download': True,
        }
