"""
Standalone Configuration Manager

Provides comprehensive configuration management for standalone execution without WebUI dependencies.
Enhanced with validation, type conversion, and advanced configuration features.
"""

import json
import os
from typing import Any, Dict, Optional, List, Union
from ..interfaces.iconfig_manager import IConfigManager


class StandaloneConfigManager(IConfigManager):
    """
    Enhanced configuration manager implementation for standalone mode.
    
    Provides comprehensive configuration management including:
    - Hierarchical configuration keys (dot notation)
    - Type validation and conversion
    - Configuration schema validation
    - Backup and restore functionality
    - Environment variable integration
    - Configuration versioning
    """
    
    def __init__(self, config_file_path: Optional[str] = None):
        """
        Initialize the standalone configuration manager.
        
        Args:
            config_file_path: Optional custom path to configuration file
        """
        self._config_cache: Dict[str, Any] = {}
        self._config_loaded = False
        self._config_file_path = config_file_path or self._get_config_file_path()
        self._model_folders = self._get_default_model_folders()
        self._debug_mode = False
        self._config_version = "1.0"
        
        # Load configuration on initialization
        self.load_config()
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key with enhanced dot notation support.
        
        Args:
            key: Configuration key (supports dot notation like 'ui.theme')
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        if not self._config_loaded:
            self.load_config()
        
        # Handle dot notation keys
        if '.' in key:
            return self._get_nested_value(key, default)
        
        return self._config_cache.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """
        Set configuration value with enhanced validation and type conversion.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set (will be validated and converted if needed)
        """
        if not self._config_loaded:
            self.load_config()
        
        # Validate and convert value
        converted_value = self._validate_and_convert_value(key, value)
        
        # Handle dot notation keys
        if '.' in key:
            self._set_nested_value(key, converted_value)
        else:
            self._config_cache[key] = converted_value
    
    def save_config(self) -> bool:
        """
        Save configuration to file with backup functionality.
        
        Returns:
            True if saved successfully
        """
        try:
            # Create backup if original exists
            if os.path.exists(self._config_file_path):
                backup_path = f"{self._config_file_path}.backup"
                import shutil
                shutil.copy2(self._config_file_path, backup_path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self._config_file_path), exist_ok=True)
            
            # Add metadata
            config_to_save = self._config_cache.copy()
            config_to_save['_metadata'] = {
                'version': self._config_version,
                'created_by': 'StandaloneConfigManager',
                'last_modified': self._get_current_timestamp()
            }
            
            # Save configuration
            with open(self._config_file_path, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            
            self._log_debug(f"Configuration saved to {self._config_file_path}")
            return True
            
        except Exception as e:
            self._log_debug(f"Error saving configuration: {e}")
            return False
    
    def load_config(self) -> bool:
        """
        Load configuration from file with migration support.
        
        Returns:
            True if loaded successfully
        """
        try:
            if os.path.exists(self._config_file_path):
                with open(self._config_file_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # Handle metadata
                if '_metadata' in loaded_config:
                    metadata = loaded_config.pop('_metadata')
                    self._handle_config_migration(metadata.get('version', '1.0'))
                
                self._config_cache = loaded_config
                self._log_debug(f"Configuration loaded from {self._config_file_path}")
            else:
                self._config_cache = self._get_default_config()
                self._log_debug("Using default configuration")
            
            # Merge with environment variables
            self._load_environment_variables()
            
            self._config_loaded = True
            return True
            
        except Exception as e:
            self._log_debug(f"Error loading configuration: {e}")
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
        
        if '.' in key:
            try:
                self._get_nested_value(key, None)
                return True
            except KeyError:
                return False
        
        return key in self._config_cache
    
    def get_model_folders(self) -> Dict[str, str]:
        """Get model folder configurations."""
        custom_folders = self.get_config('model_folders', {})
        if custom_folders:
            merged_folders = self._model_folders.copy()
            merged_folders.update(custom_folders)
            return merged_folders
        
        return self._model_folders.copy()
    
    def update_model_folder(self, model_type: str, path: str) -> bool:
        """
        Update model folder path for specific type.
        
        Args:
            model_type: Type of model
            path: New path for the model type
            
        Returns:
            True if updated successfully
        """
        try:
            current_folders = self.get_config('model_folders', {})
            current_folders[model_type] = path
            self.set_config('model_folders', current_folders)
            return True
        except Exception as e:
            self._log_debug(f"Error updating model folder: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to default values.
        
        Returns:
            True if reset successfully
        """
        try:
            self._config_cache = self._get_default_config()
            return self.save_config()
        except Exception as e:
            self._log_debug(f"Error resetting configuration: {e}")
            return False
    
    def export_config(self, export_path: str) -> bool:
        """
        Export configuration to specified path.
        
        Args:
            export_path: Path to export configuration
            
        Returns:
            True if exported successfully
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self._config_cache, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            self._log_debug(f"Error exporting configuration: {e}")
            return False
    
    def import_config(self, import_path: str, merge: bool = True) -> bool:
        """
        Import configuration from specified path.
        
        Args:
            import_path: Path to import configuration from
            merge: If True, merge with existing config; if False, replace
            
        Returns:
            True if imported successfully
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            if merge:
                self._config_cache.update(imported_config)
            else:
                self._config_cache = imported_config
            
            return self.save_config()
        except Exception as e:
            self._log_debug(f"Error importing configuration: {e}")
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        Get information about the configuration.
        
        Returns:
            Dictionary with configuration metadata
        """
        return {
            'config_file_path': self._config_file_path,
            'config_loaded': self._config_loaded,
            'config_version': self._config_version,
            'total_keys': len(self._config_cache),
            'file_exists': os.path.exists(self._config_file_path),
            'last_modified': self._get_file_modified_time() if os.path.exists(self._config_file_path) else None
        }
    
    # Legacy compatibility methods
    def get_embeddings_dir(self) -> Optional[str]:
        """Get embeddings directory path (legacy compatibility)."""
        return self.get_config('paths.embeddings_dir', None)
    
    def get_hypernetwork_dir(self) -> Optional[str]:
        """Get hypernetwork directory path (legacy compatibility)."""
        return self.get_config('paths.hypernetwork_dir', None)
    
    def get_ckpt_dir(self) -> Optional[str]:
        """Get checkpoint directory path (legacy compatibility)."""
        return self.get_config('paths.ckpt_dir', None)
    
    def get_lora_dir(self) -> Optional[str]:
        """Get LoRA directory path (legacy compatibility)."""
        return self.get_config('paths.lora_dir', None)
    
    # Private helper methods
    def _get_nested_value(self, key: str, default: Any = None) -> Any:
        """Get nested configuration value using dot notation."""
        keys = key.split('.')
        value = self._config_cache
        
        try:
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        except (KeyError, TypeError):
            return default
    
    def _set_nested_value(self, key: str, value: Any):
        """Set nested configuration value using dot notation."""
        keys = key.split('.')
        config = self._config_cache
        
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def _validate_and_convert_value(self, key: str, value: Any) -> Any:
        """Validate and convert configuration value based on key."""
        # Define validation rules for specific keys
        validation_rules = {
            'server.port': lambda x: max(1024, min(65535, int(x))),
            'civitai.cache_size_mb': lambda x: max(100, min(5000, int(x))),
            'download.max_concurrent': lambda x: max(1, min(10, int(x))),
            'ui.page_size': lambda x: max(5, min(100, int(x))),
        }
        
        if key in validation_rules:
            try:
                return validation_rules[key](value)
            except (ValueError, TypeError):
                self._log_debug(f"Invalid value for {key}: {value}, using original")
                return value
        
        return value
    
    def _load_environment_variables(self):
        """Load configuration from environment variables."""
        env_prefix = 'CIVITAI_'
        
        env_mappings = {
            f'{env_prefix}API_KEY': 'civitai.api_key',
            f'{env_prefix}HOST': 'server.host',
            f'{env_prefix}PORT': 'server.port',
            f'{env_prefix}SHARE': 'server.share',
            f'{env_prefix}DOWNLOAD_PATH': 'civitai.download_path',
            f'{env_prefix}CACHE_ENABLED': 'civitai.cache_enabled',
            f'{env_prefix}NSFW_FILTER': 'ui.nsfw_filter',
            f'{env_prefix}LANGUAGE': 'ui.language',
        }
        
        for env_var, config_key in env_mappings.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                # Convert string values to appropriate types
                converted_value = self._convert_env_value(env_value)
                self.set_config(config_key, converted_value)
                self._log_debug(f"Loaded {config_key} from environment variable")
    
    def _convert_env_value(self, value: str) -> Any:
        """Convert environment variable string to appropriate type."""
        # Boolean conversion
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Integer conversion
        if value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
            return int(value)
        
        # Float conversion
        try:
            return float(value)
        except ValueError:
            pass
        
        # String (default)
        return value
    
    def _handle_config_migration(self, version: str):
        """Handle configuration migration from older versions."""
        if version != self._config_version:
            self._log_debug(f"Migrating configuration from version {version} to {self._config_version}")
            # Add migration logic here if needed in the future
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_file_modified_time(self) -> str:
        """Get file modification time."""
        try:
            from datetime import datetime
            mtime = os.path.getmtime(self._config_file_path)
            return datetime.fromtimestamp(mtime).isoformat()
        except Exception:
            return None
    
    def get_lora_dir(self) -> Optional[str]:
        """Get LoRA directory path (legacy compatibility)."""
        return self.get_config('paths.lora_dir', None)
    
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
        """Get comprehensive default configuration values."""
        return {
            'civitai': {
                'api_key': '',
                'download_path': 'models',
                'cache_enabled': True,
                'cache_size_mb': 500,
                'auto_update_check': True,
                'download_timeout': 300,
                'max_retries': 3,
            },
            'server': {
                'host': '127.0.0.1',
                'port': 7860,
                'share': False,
                'auth_enabled': False,
                'ssl_enabled': False,
            },
            'ui': {
                'theme': 'default',
                'language': 'en',
                'page_size': 20,
                'show_nsfw': False,
                'nsfw_filter': False,
                'auto_refresh': True,
                'animation_enabled': True,
            },
            'download': {
                'max_concurrent': 3,
                'auto_create_folder': True,
                'verify_downloads': True,
                'keep_incomplete': False,
                'preview_image_download': True,
                'info_file_download': True,
            },
            'paths': {
                'base_path': '',
                'models_path': 'models',
                'outputs_path': 'outputs',
                'cache_path': 'cache',
                'logs_path': 'logs',
            },
            'advanced': {
                'debug_mode': False,
                'log_level': 'INFO',
                'performance_monitoring': False,
                'experimental_features': False,
            },
            'model_folders': self._model_folders,
            'shortcuts': {
                'update_on_start': True,
                'auto_scan_folders': True,
                'scan_interval_hours': 24,
            }
        }
    
    def _log_debug(self, message: str):
        """Log debug message if debug mode is enabled."""
        if self._debug_mode:
            print(f"StandaloneConfigManager: {message}")
    
    def set_debug_mode(self, enabled: bool):
        """Enable or disable debug mode."""
        self._debug_mode = enabled
        self.set_config('advanced.debug_mode', enabled)
