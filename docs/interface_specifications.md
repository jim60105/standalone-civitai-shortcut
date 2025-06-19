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
- **Purpose**: Returns the base path of the application or extension. In standalone mode, this is the root directory of the extension. In WebUI mode, this is the root directory of the WebUI environment.
- **Returns**: Absolute path to the base directory.
- **Thread Safety**: Safe.
- **Exceptions**: None (should always return a valid path).

##### `get_extension_path() -> str`
- **Purpose**: Returns the path to the extension directory. In standalone mode, this is the same as the base path. In WebUI mode, this is the directory where the extension is installed.
- **Returns**: Absolute path to the extension directory.
- **Thread Safety**: Safe.
- **Exceptions**: None (should always return a valid path).

##### `get_script_path() -> str`
- **Purpose**: Returns the main script path (WebUI script_path or extension base path).
- **Returns**: Absolute path to the script directory.
- **Thread Safety**: Safe.
- **Exceptions**: None (should always return a valid path).

##### `get_user_data_path() -> str`
- **Purpose**: Returns the user data directory path (WebUI data_path or extension data directory).
- **Returns**: Absolute path to the user data directory.
- **Thread Safety**: Safe.
- **Exceptions**: None.

##### `get_models_path() -> str`
- **Purpose**: Returns the models storage directory path (WebUI models_path or extension models directory).
- **Returns**: Absolute path to the models directory.
- **Thread Safety**: Safe.
- **Exceptions**: None.

##### `get_model_folder_path(model_type: str) -> str`
- **Purpose**: Returns the directory path for a specific model type.
- **Parameters**:
  - `model_type`: Model type identifier (e.g., 'Stable-diffusion', 'Lora', 'ControlNet').
- **Returns**: Absolute path to the model type directory.
- **Thread Safety**: Safe.
- **Exceptions**: None (should return default path if type unknown).

##### `get_config_path() -> str`
- **Purpose**: Returns the configuration file path.
- **Returns**: Absolute path to the configuration file.
- **Thread Safety**: Safe.
- **Exceptions**: None.

##### `ensure_directory_exists(path: str) -> bool`
- **Purpose**: Ensures a directory exists, creating it if necessary.
- **Parameters**:
  - `path`: Directory path to ensure exists.
- **Returns**: True if directory exists or was created successfully.
- **Thread Safety**: Safe with proper locking.
- **Exceptions**: Should handle and return False on errors.

##### `ensure_directories() -> bool`
- **Purpose**: Ensures all required directories for the application or extension exist (e.g., data, models, config folders). Creates them if necessary.
- **Returns**: True if all directories exist or were created successfully.
- **Thread Safety**: Safe with proper locking.
- **Exceptions**: Should handle and return False on errors.

##### `get_model_path(model_type: str, model_name: str) -> str`
- **Purpose**: Returns the absolute path to a specific model file by type and name.
- **Parameters**:
  - `model_type`: Model type identifier (e.g., 'Stable-diffusion', 'Lora', etc.)
  - `model_name`: The filename of the model (with extension)
- **Returns**: Absolute path to the model file.
- **Thread Safety**: Safe.
- **Exceptions**: None (should return a valid path even if the file does not exist).


### IConfigManager

**Purpose**: Manages application configuration across different execution environments.

**Location**: `interfaces/iconfig_manager.py`

#### Methods

##### `get_config(key: str, default: Any = None) -> Any`
- **Purpose**: Retrieve a configuration value by key.
- **Parameters**:
  - `key`: Configuration key identifier.
  - `default`: Value to return if the key does not exist.
- **Returns**: Configuration value or default.
- **Thread Safety**: Safe for reads.
- **Exceptions**: Should not raise exceptions, return default instead.

##### `set_config(key: str, value: Any) -> None`
- **Purpose**: Set a configuration value by key.
- **Parameters**:
  - `key`: Configuration key identifier.
  - `value`: Value to set.
- **Returns**: None.
- **Thread Safety**: Safe with proper locking.
- **Exceptions**: Should handle errors gracefully.

##### `save_config() -> bool`
- **Purpose**: Persist the current configuration to storage.
- **Returns**: True if saved successfully, False otherwise.
- **Thread Safety**: Safe with proper locking.
- **Exceptions**: Should handle and return False on errors.

##### `load_config() -> bool`
- **Purpose**: Load configuration from persistent storage.
- **Returns**: True if loaded successfully, False otherwise.
- **Thread Safety**: Safe.
- **Exceptions**: Should handle and return False on errors.

##### `get_all_configs() -> Dict[str, Any]`
- **Purpose**: Retrieve all configuration key-value pairs.
- **Returns**: Dictionary of all configuration keys and their values.
- **Thread Safety**: Safe for reads.
- **Exceptions**: Should return empty dict on errors.

##### `has_config(key: str) -> bool`
- **Purpose**: Check if a configuration key exists in the configuration data.
- **Parameters**:
  - `key`: Configuration key identifier.
- **Returns**: True if the key exists, False otherwise.
- **Thread Safety**: Safe for reads.
- **Exceptions**: Should not raise exceptions.

##### `get_model_folders() -> Dict[str, str]`
- **Purpose**: Retrieve the mapping of model types to their corresponding folder paths.
- **Returns**: Dictionary mapping model type identifiers to folder paths.
- **Thread Safety**: Safe for reads.
- **Exceptions**: Should return empty dict on errors.

##### `get_embeddings_dir() -> Optional[str]`
- **Purpose**: Retrieve the embeddings directory path.
- **Returns**: Embeddings directory path or None.
- **Thread Safety**: Safe.
- **Exceptions**: Should return None on errors.

##### `get_hypernetwork_dir() -> Optional[str]`
- **Purpose**: Retrieve the hypernetwork directory path.
- **Returns**: Hypernetwork directory path or None.
- **Thread Safety**: Safe.
- **Exceptions**: Should return None on errors.

##### `get_ckpt_dir() -> Optional[str]`
- **Purpose**: Retrieve the checkpoint (Stable Diffusion) directory path.
- **Returns**: Checkpoint directory path or None.
- **Thread Safety**: Safe.
- **Exceptions**: Should return None on errors.

##### `get_lora_dir() -> Optional[str]`
- **Purpose**: Retrieve the LoRA model directory path.
- **Returns**: LoRA directory path or None.
- **Thread Safety**: Safe.
- **Exceptions**: Should return None on errors.

##### `get(key: str, default: Any = None) -> Any`
- **Purpose**: Alias for `get_config()`. Retrieve a configuration value by key.
- **Parameters**:
  - `key`: Configuration key identifier.
  - `default`: Value to return if the key does not exist.
- **Returns**: Configuration value or default.
- **Thread Safety**: Safe for reads.
- **Exceptions**: Should not raise exceptions, return default instead.

##### `set(key: str, value: Any) -> None`
- **Purpose**: Alias for `set_config()`. Set a configuration value by key.
- **Parameters**:
  - `key`: Configuration key identifier.
  - `value`: Value to set.
- **Returns**: None.
- **Thread Safety**: Safe with proper locking.
- **Exceptions**: Should handle errors gracefully.

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

##### `parse_generation_parameters(parameters_text: str) -> Dict[str, Any]`
- **Purpose**: Parses generation parameters text into structured data
- **Parameters**:
  - `parameters_text`: Raw parameters text
- **Returns**: Dictionary of parsed parameters
- **Thread Safety**: Safe
- **Exceptions**: Should return empty dict on errors

##### `extract_prompt_from_parameters(parameters_text: str) -> Tuple[str, str]`
- **Purpose**: Extracts positive and negative prompts from parameters text
- **Parameters**:
  - `parameters_text`: Raw parameters text
- **Returns**: Tuple of (positive_prompt, negative_prompt)
- **Thread Safety**: Safe
- **Exceptions**: Should return empty strings on errors

##### `format_parameters_for_display(params: Dict[str, Any]) -> str`
- **Purpose**: Formats parameter dictionary for display
- **Parameters**:
  - `params`: Parameters dictionary
- **Returns**: Formatted parameters string
- **Thread Safety**: Safe
- **Exceptions**: Should return empty string on errors

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

##### `bind_send_to_buttons(buttons: Any, image_component: Any, text_component: Any) -> None`
- **Purpose**: Binds send-to button functionality to UI components
- **Parameters**:
  - `buttons`: The send-to buttons created by create_send_to_buttons
  - `image_component`: The image component to bind
  - `text_component`: The text component to bind
- **Thread Safety**: UI thread only
- **Exceptions**: Should handle errors gracefully

##### `launch_standalone(ui_callback: Callable, **kwargs) -> None`
- **Purpose**: Launches standalone UI application
- **Parameters**:
  - `ui_callback`: Function that creates UI components
  - `**kwargs`: Additional launch parameters
- **Thread Safety**: Main thread only
- **Exceptions**: Should handle errors gracefully

##### `is_webui_mode() -> bool`
- **Purpose**: Checks if running in WebUI mode
- **Returns**: True if in WebUI mode
- **Thread Safety**: Safe
- **Exceptions**: Should not raise exceptions

##### `request_restart() -> None`
- **Purpose**: Requests application restart (WebUI mode only)
- **Thread Safety**: UI thread only
- **Exceptions**: Should handle errors gracefully

### ISamplerProvider

**Purpose**: Provides sampler and upscaler information.

**Location**: `interfaces/isampler_provider.py`

#### Methods

##### `get_samplers() -> List[str]`
- **Purpose**: Returns list of available samplers
- **Returns**: List of sampler names
- **Thread Safety**: Safe
- **Exceptions**: Should return empty list on errors

##### `get_samplers_for_img2img() -> List[str]`
- **Purpose**: Returns list of samplers available for img2img
- **Returns**: List of sampler names for img2img
- **Thread Safety**: Safe
- **Exceptions**: Should return empty list on errors

##### `get_upscale_modes() -> List[str]`
- **Purpose**: Returns list of available upscaling modes
- **Returns**: List of upscale mode names
- **Thread Safety**: Safe
- **Exceptions**: Should return empty list on errors

##### `get_sd_upscalers() -> List[str]`
- **Purpose**: Returns list of available SD upscalers
- **Returns**: List of SD upscaler names
- **Thread Safety**: Safe
- **Exceptions**: Should return empty list on errors

##### `get_all_upscalers() -> List[str]`
- **Purpose**: Returns list of all available upscalers
- **Returns**: List of all upscaler names
- **Thread Safety**: Safe
- **Exceptions**: Should return empty list on errors

##### `get_txt2img_samplers() -> List[str]`
- **Purpose**: Returns list of samplers available for txt2img
- **Returns**: List of sampler names for txt2img
- **Thread Safety**: Safe
- **Exceptions**: Should return empty list on errors

##### `get_default_sampler() -> str`
- **Purpose**: Returns the default sampler name
- **Returns**: Default sampler name
- **Thread Safety**: Safe
- **Exceptions**: Should return fallback sampler name

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

##### `extract_prompt_and_negative(text: str) -> Tuple[str, str]`
- **Purpose**: Extracts positive and negative prompts from parameters text
- **Parameters**:
  - `text`: Raw parameters text containing prompts
- **Returns**: Tuple of (positive_prompt, negative_prompt)
- **Thread Safety**: Safe
- **Exceptions**: Should return empty strings on errors

##### `validate_parameters(params: Dict[str, Any]) -> Dict[str, Any]`
- **Purpose**: Validates and corrects parameter values
- **Parameters**:
  - `params`: Parameters dictionary to validate
- **Returns**: Validated parameters dictionary
- **Thread Safety**: Safe
- **Exceptions**: Should return corrected values on errors

##### `merge_parameters(base_params: Dict[str, Any], override_params: Dict[str, Any]) -> Dict[str, Any]`
- **Purpose**: Merges two parameter dictionaries
- **Parameters**:
  - `base_params`: Base parameters dictionary
  - `override_params`: Override parameters dictionary
- **Returns**: Merged parameters dictionary
- **Thread Safety**: Safe
- **Exceptions**: Should return base_params on errors

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
