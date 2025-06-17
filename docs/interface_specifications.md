# Interface Specifications

This document provides detailed specifications for all abstract interfaces in the Civitai Shortcut compatibility layer.

## Overview

The compatibility layer provides unified access to functionality across WebUI and standalone execution modes through a set of abstract interfaces. Each interface defines a contract that implementations must follow.

## Core Interfaces

### IPathManager

**Purpose**: Manages file and directory paths across different execution environments.

**Location**: `interfaces/ipath_manager.py`

#### Methods

##### `get_base_path() -> str`
- **Purpose**: Returns the base application directory path
- **Returns**: Absolute path to the application base directory
- **Thread Safety**: Safe
- **Exceptions**: None (should always return a valid path)

##### `get_extension_path() -> str`
- **Purpose**: Returns the extension installation directory path
- **Returns**: Absolute path to the extension directory
- **Thread Safety**: Safe
- **Exceptions**: None

##### `get_models_path() -> str`
- **Purpose**: Returns the models storage directory path
- **Returns**: Absolute path to the models directory
- **Thread Safety**: Safe
- **Exceptions**: None

##### `get_model_folder_path(model_type: str) -> str`
- **Purpose**: Returns the directory path for a specific model type
- **Parameters**:
  - `model_type`: Model type identifier (e.g., 'Checkpoint', 'LORA')
- **Returns**: Absolute path to the model type directory
- **Thread Safety**: Safe
- **Exceptions**: None (should return default path if type unknown)

##### `get_config_path() -> str`
- **Purpose**: Returns the configuration file path
- **Returns**: Absolute path to the configuration file
- **Thread Safety**: Safe
- **Exceptions**: None

##### `ensure_directory_exists(path: str) -> bool`
- **Purpose**: Ensures a directory exists, creating it if necessary
- **Parameters**:
  - `path`: Directory path to ensure exists
- **Returns**: True if directory exists or was created successfully
- **Thread Safety**: Safe with proper locking
- **Exceptions**: Should handle and return False on errors

### IConfigManager

**Purpose**: Manages application configuration across different execution environments.

**Location**: `interfaces/iconfig_manager.py`

#### Methods

##### `get_config(key: str, default: Any = None) -> Any`
- **Purpose**: Retrieves a configuration value by key
- **Parameters**:
  - `key`: Configuration key identifier
  - `default`: Default value if key doesn't exist
- **Returns**: Configuration value or default
- **Thread Safety**: Safe for reads
- **Exceptions**: Should not raise exceptions, return default instead

##### `set_config(key: str, value: Any) -> None`
- **Purpose**: Sets a configuration value
- **Parameters**:
  - `key`: Configuration key identifier
  - `value`: Value to set
- **Thread Safety**: Safe with proper locking
- **Exceptions**: Should handle errors gracefully

##### `save_config() -> bool`
- **Purpose**: Persists configuration to storage
- **Returns**: True if saved successfully
- **Thread Safety**: Safe with proper locking
- **Exceptions**: Should handle and return False on errors

##### `load_config() -> bool`
- **Purpose**: Loads configuration from storage
- **Returns**: True if loaded successfully
- **Thread Safety**: Safe
- **Exceptions**: Should handle and return False on errors

### IMetadataProcessor

**Purpose**: Processes image metadata and generation parameters.

**Location**: `interfaces/imetadata_processor.py`

#### Methods

##### `extract_png_info(image_path: str) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]`
- **Purpose**: Extracts metadata from PNG files (compatible with WebUI format)
- **Parameters**:
  - `image_path`: Path to PNG image file
- **Returns**: Tuple of (info_text, parameters_dict, additional_info)
- **Thread Safety**: Safe (read-only operation)
- **Exceptions**: Should handle errors and return None values

##### `extract_parameters_from_png(image_path: str) -> Optional[str]`
- **Purpose**: Extracts generation parameters string from PNG
- **Parameters**:
  - `image_path`: Path to PNG image file
- **Returns**: Parameters string or None
- **Thread Safety**: Safe
- **Exceptions**: Should handle errors and return None

### IUIBridge

**Purpose**: Provides UI integration across different execution modes.

**Location**: `interfaces/iui_bridge.py`

#### Methods

##### `register_ui_tabs(callback: Callable) -> None`
- **Purpose**: Registers UI tabs with the host application
- **Parameters**:
  - `callback`: Function that creates UI components
- **Thread Safety**: Should be called from main thread only
- **Exceptions**: Should handle errors gracefully

##### `create_send_to_buttons(targets: List[str]) -> Any`
- **Purpose**: Creates buttons for parameter transfer functionality
- **Parameters**:
  - `targets`: List of target names (e.g., ['txt2img', 'img2img'])
- **Returns**: UI components for send-to functionality
- **Thread Safety**: UI thread only
- **Exceptions**: Should return None on errors

### ISamplerProvider

**Purpose**: Provides sampler and upscaler information.

**Location**: `interfaces/isampler_provider.py`

#### Methods

##### `get_samplers() -> List[str]`
- **Purpose**: Returns list of available samplers
- **Returns**: List of sampler names
- **Thread Safety**: Safe
- **Exceptions**: Should return empty list on errors

##### `get_upscale_modes() -> List[str]`
- **Purpose**: Returns list of available upscaling modes
- **Returns**: List of upscale mode names
- **Thread Safety**: Safe
- **Exceptions**: Should return empty list on errors

### IParameterProcessor

**Purpose**: Processes generation parameters and text.

**Location**: `interfaces/iparameter_processor.py`

#### Methods

##### `parse_parameters(text: str) -> Dict[str, Any]`
- **Purpose**: Parses parameter string into structured data
- **Parameters**:
  - `text`: Raw parameters text
- **Returns**: Dictionary of parsed parameters
- **Thread Safety**: Safe
- **Exceptions**: Should return empty dict on errors

##### `format_parameters(params: Dict[str, Any]) -> str`
- **Purpose**: Formats parameter dictionary into text string
- **Parameters**:
  - `params`: Parameters dictionary
- **Returns**: Formatted parameters string
- **Thread Safety**: Safe
- **Exceptions**: Should return empty string on errors

## Implementation Requirements

### Error Handling
- All methods should handle errors gracefully
- No method should raise exceptions unless explicitly documented
- Return appropriate default values on errors

### Thread Safety
- Read-only operations must be thread-safe
- Write operations should use appropriate locking mechanisms
- UI operations should only be called from the UI thread

### Performance
- Methods should be efficiently implemented
- Caching should be used where appropriate
- Avoid blocking operations in UI methods

### Compatibility
- WebUI implementations should maintain compatibility with existing WebUI functionality
- Standalone implementations should provide equivalent functionality where possible
- Graceful degradation should be implemented for unavailable features

## Testing Requirements

Each interface implementation must include:

1. **Unit tests** covering all public methods
2. **Error handling tests** for edge cases
3. **Thread safety tests** for concurrent access
4. **Integration tests** with the compatibility layer
5. **Performance tests** for critical paths

## Versioning

Interface changes follow semantic versioning:
- **Major**: Breaking changes to method signatures
- **Minor**: New methods added
- **Patch**: Implementation improvements, bug fixes
