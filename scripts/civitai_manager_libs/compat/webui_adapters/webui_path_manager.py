"""
WebUI Path Manager

Provides path management using AUTOMATIC1111 WebUI modules.
"""

import os
from typing import Dict

from ..interfaces.ipath_manager import IPathManager


class WebUIPathManager(IPathManager):
    """Path manager implementation using WebUI modules."""
    
    def __init__(self):
        """Initialize the WebUI path manager."""
        self._model_folders = self._initialize_model_folders()
    
    def get_base_path(self) -> str:
        """Get the base path using WebUI scripts module."""
        try:
            from modules import scripts
            return scripts.basedir()
        except (ImportError, AttributeError) as e:
            # Fallback to file-based detection
            return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    def get_extension_path(self) -> str:
        """Get the extension path."""
        return self.get_base_path()
    
    def get_models_path(self) -> str:
        """Get models path from WebUI shared module."""
        try:
            from modules import shared
            models_path = getattr(shared, 'models_path', None)
            if models_path:
                return models_path
        except (ImportError, AttributeError):
            pass
        
        # Fallback to default models directory
        return os.path.join(self.get_base_path(), '..', 'models')
    
    def get_model_folder_path(self, model_type: str) -> str:
        """Get specific model folder path."""
        if model_type in self._model_folders:
            folder_path = self._model_folders[model_type]
            if os.path.isabs(folder_path):
                return folder_path
            else:
                # Relative to base path
                base_path = self.get_base_path()
                parent_dir = os.path.dirname(base_path)
                return os.path.join(parent_dir, folder_path)
        
        # Default fallback
        return os.path.join(self.get_models_path(), model_type)
    
    def get_config_path(self) -> str:
        """Get configuration file path."""
        return os.path.join(self.get_extension_path(), 'setting.json')
    
    def ensure_directory_exists(self, path: str) -> bool:
        """Ensure directory exists."""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception:
            return False
    
    def _initialize_model_folders(self) -> Dict[str, str]:
        """Initialize model folder configuration using WebUI settings."""
        # Default model folders
        model_folders = {
            'Checkpoint': os.path.join("models", "Stable-diffusion"),
            'LORA': os.path.join("models", "Lora"),
            'LoCon': os.path.join("models", "LyCORIS"),
            'TextualInversion': os.path.join("embeddings"),
            'Hypernetwork': os.path.join("models", "hypernetworks"),
            'AestheticGradient': os.path.join("extensions", "stable-diffusion-webui-aesthetic-gradients", "aesthetic_embeddings"),
            'Controlnet': os.path.join("models", "ControlNet"),
            'Poses': os.path.join("models", "Poses"),
            'Wildcards': os.path.join("extensions", "sd-dynamic-prompts", "wildcards"),
            'Other': os.path.join("models", "Other"),
            'VAE': os.path.join("models", "VAE"),
            'ANLORA': os.path.join("extensions", "sd-webui-additional-networks", "models", "lora"),
            'Unknown': os.path.join("models", "Unknown"),
        }
        
        # Update with WebUI command line options if available
        try:
            from modules import shared
            cmd_opts = getattr(shared, 'cmd_opts', None)
            if cmd_opts:
                if hasattr(cmd_opts, 'embeddings_dir') and cmd_opts.embeddings_dir:
                    model_folders['TextualInversion'] = cmd_opts.embeddings_dir
                if hasattr(cmd_opts, 'hypernetwork_dir') and cmd_opts.hypernetwork_dir:
                    model_folders['Hypernetwork'] = cmd_opts.hypernetwork_dir
                if hasattr(cmd_opts, 'ckpt_dir') and cmd_opts.ckpt_dir:
                    model_folders['Checkpoint'] = cmd_opts.ckpt_dir
                if hasattr(cmd_opts, 'lora_dir') and cmd_opts.lora_dir:
                    model_folders['LORA'] = cmd_opts.lora_dir
        except (ImportError, AttributeError):
            # WebUI modules not available, use defaults
            pass
        
        return model_folders
