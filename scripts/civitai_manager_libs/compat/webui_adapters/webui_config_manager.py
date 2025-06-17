"""
WebUI Configuration Manager

Provides configuration management using AUTOMATIC1111 WebUI modules.
"""

import json
import os
from typing import Any, Dict, Optional

from ..interfaces.iconfig_manager import IConfigManager


class WebUIConfigManager(IConfigManager):
    """Configuration manager implementation using WebUI modules and local storage."""

    def __init__(self):
        """Initialize the WebUI configuration manager."""
        self._config_cache: Dict[str, Any] = {}
        self._config_loaded = False
        self._config_file_path = self._get_config_file_path()

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
            with open(self._config_file_path, "w", encoding="utf-8") as f:
                json.dump(self._config_cache, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def load_config(self) -> bool:
        """Load configuration from file."""
        try:
            if os.path.exists(self._config_file_path):
                with open(self._config_file_path, "r", encoding="utf-8") as f:
                    self._config_cache = json.load(f)
            else:
                self._config_cache = {}

            self._config_loaded = True
            return True
        except Exception:
            self._config_cache = {}
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
        """Get model folder configurations from WebUI."""
        model_folders = {
            "Checkpoint": os.path.join("models", "Stable-diffusion"),
            "LORA": os.path.join("models", "Lora"),
            "LoCon": os.path.join("models", "LyCORIS"),
            "TextualInversion": os.path.join("embeddings"),
            "Hypernetwork": os.path.join("models", "hypernetworks"),
            "AestheticGradient": os.path.join(
                "extensions",
                "stable-diffusion-webui-aesthetic-gradients",
                "aesthetic_embeddings",
            ),
            "Controlnet": os.path.join("models", "ControlNet"),
            "Poses": os.path.join("models", "Poses"),
            "Wildcards": os.path.join("extensions", "sd-dynamic-prompts", "wildcards"),
            "Other": os.path.join("models", "Other"),
            "VAE": os.path.join("models", "VAE"),
            "ANLORA": os.path.join("extensions", "sd-webui-additional-networks", "models", "lora"),
            "Unknown": os.path.join("models", "Unknown"),
        }

        # Override with WebUI command line options if available
        try:
            from modules import shared

            cmd_opts = getattr(shared, "cmd_opts", None)
            if cmd_opts:
                if hasattr(cmd_opts, "embeddings_dir") and cmd_opts.embeddings_dir:
                    model_folders["TextualInversion"] = cmd_opts.embeddings_dir
                if hasattr(cmd_opts, "hypernetwork_dir") and cmd_opts.hypernetwork_dir:
                    model_folders["Hypernetwork"] = cmd_opts.hypernetwork_dir
                if hasattr(cmd_opts, "ckpt_dir") and cmd_opts.ckpt_dir:
                    model_folders["Checkpoint"] = cmd_opts.ckpt_dir
                if hasattr(cmd_opts, "lora_dir") and cmd_opts.lora_dir:
                    model_folders["LORA"] = cmd_opts.lora_dir
        except (ImportError, AttributeError):
            # WebUI modules not available, use defaults
            pass

        return model_folders

    def get_embeddings_dir(self) -> Optional[str]:
        """Get embeddings directory from WebUI."""
        try:
            from modules import shared

            cmd_opts = getattr(shared, "cmd_opts", None)
            if cmd_opts and hasattr(cmd_opts, "embeddings_dir"):
                return cmd_opts.embeddings_dir
        except (ImportError, AttributeError):
            pass

        return None

    def get_hypernetwork_dir(self) -> Optional[str]:
        """Get hypernetwork directory from WebUI."""
        try:
            from modules import shared

            cmd_opts = getattr(shared, "cmd_opts", None)
            if cmd_opts and hasattr(cmd_opts, "hypernetwork_dir"):
                return cmd_opts.hypernetwork_dir
        except (ImportError, AttributeError):
            pass

        return None

    def get_ckpt_dir(self) -> Optional[str]:
        """Get checkpoint directory from WebUI."""
        try:
            from modules import shared

            cmd_opts = getattr(shared, "cmd_opts", None)
            if cmd_opts and hasattr(cmd_opts, "ckpt_dir"):
                return cmd_opts.ckpt_dir
        except (ImportError, AttributeError):
            pass

        return None

    def get_lora_dir(self) -> Optional[str]:
        """Get LoRA directory from WebUI."""
        try:
            from modules import shared

            cmd_opts = getattr(shared, "cmd_opts", None)
            if cmd_opts and hasattr(cmd_opts, "lora_dir"):
                return cmd_opts.lora_dir
        except (ImportError, AttributeError):
            pass

        return None

    def _get_config_file_path(self) -> str:
        """Get the path to the configuration file."""
        try:
            from modules import scripts

            extension_base = scripts.basedir()
            return os.path.join(extension_base, "setting.json")
        except (ImportError, AttributeError):
            # Fallback to current directory
            return os.path.join(os.getcwd(), "setting.json")
