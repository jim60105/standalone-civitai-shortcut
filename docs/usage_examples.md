# Usage Examples

This document provides practical examples of how to use the Civitai Shortcut compatibility layer.

## Basic Usage

### Getting Started

```python
from civitai_manager_libs.compat import get_compatibility_layer

# Get the compatibility layer (auto-detects environment)
compat = get_compatibility_layer()

# Check current mode
if compat.is_webui_mode():
    print("Running in WebUI mode")
else:
    print("Running in standalone mode")
```

### Forcing a Specific Mode

```python
from civitai_manager_libs.compat import get_compatibility_layer

# Force WebUI mode (useful for testing)
compat = get_compatibility_layer(mode='webui')

# Force standalone mode
compat = get_compatibility_layer(mode='standalone')
```

## Path Management Examples

### Basic Path Operations

```python
from civitai_manager_libs.compat import get_compatibility_layer

compat = get_compatibility_layer()
path_manager = compat.path_manager

# Get application paths
script_path = path_manager.get_script_path()
user_data_path = path_manager.get_user_data_path()
models_path = path_manager.get_models_path()

print(f"Script path: {script_path}")
print(f"User data path: {user_data_path}")
print(f"Models path: {models_path}")
```

### Model-Specific Paths

```python
# Get paths for specific model types
checkpoint_path = path_manager.get_model_folder_path('Stable-diffusion')
lora_path = path_manager.get_model_folder_path('Lora')
controlnet_path = path_manager.get_model_folder_path('ControlNet')
embedding_path = path_manager.get_model_folder_path('embeddings')

print(f"Checkpoints: {checkpoint_path}")
print(f"LoRA models: {lora_path}")
print(f"ControlNet: {controlnet_path}")
print(f"Embeddings: {embedding_path}")

# Ensure directories exist
path_manager.ensure_directory_exists(checkpoint_path)
path_manager.ensure_directory_exists(lora_path)
```

## Configuration Management Examples

### Reading Configuration

```python
from civitai_manager_libs.compat import get_compatibility_layer

compat = get_compatibility_layer()
config = compat.config_manager

# Get configuration values
api_key = config.get_config('civitai_api_key', '')
max_downloads = config.get_config('max_download_concurrent', 3)
nsfw_filter = config.get_config('nsfw_filter', False)

print(f"API Key set: {'Yes' if api_key else 'No'}")
print(f"Max concurrent downloads: {max_downloads}")
print(f"NSFW filter: {nsfw_filter}")
```

### Writing Configuration

```python
# Set configuration values
config.set_config('civitai_api_key', 'your_api_key_here')
config.set_config('max_download_concurrent', 5)
config.set_config('nsfw_filter', True)

# Save configuration
if config.save_config():
    print("Configuration saved successfully")
else:
    print("Failed to save configuration")
```

### Model Folder Configuration

```python
# Get model folder mappings
model_folders = config.get_model_folders()
for model_type, folder_path in model_folders.items():
    print(f"{model_type}: {folder_path}")

# Get all configuration values
all_config = config.get_all_config()
print("All configuration:", all_config)

# Get WebUI-specific directories (WebUI mode only)
embeddings_dir = config.get_embeddings_dir()
if embeddings_dir:
    print(f"Custom embeddings directory: {embeddings_dir}")
```

## Metadata Processing Examples

### Extract PNG Metadata

```python
from civitai_manager_libs.compat import get_compatibility_layer

compat = get_compatibility_layer()
metadata_processor = compat.metadata_processor

# Extract metadata from PNG file
image_path = "path/to/generated_image.png"
info1, generate_data, info3 = metadata_processor.extract_png_info(image_path)

if generate_data:
    print("Generation parameters found:")
    for key, value in generate_data.items():
        print(f"  {key}: {value}")
else:
    print("No generation parameters found")
```

### Parse Generation Parameters

```python
# Extract just the parameters string
parameters_text = metadata_processor.extract_parameters_from_png(image_path)

if parameters_text:
    # Parse into structured data
    params = metadata_processor.parse_generation_parameters(parameters_text)
    
    # Extract prompts using the correct method
    positive_prompt, negative_prompt = metadata_processor.extract_prompt_from_parameters(parameters_text)
    
    print(f"Positive prompt: {positive_prompt}")
    print(f"Negative prompt: {negative_prompt}")
    print(f"Parsed parameters: {params}")
```

### Format Parameters for Display

```python
# Create parameters dictionary
params = {
    'prompt': 'beautiful landscape, detailed',
    'negative_prompt': 'blurry, low quality',
    'steps': 20,
    'cfg_scale': 7.5,
    'sampler_name': 'Euler a',
    'width': 512,
    'height': 512
}

# Format for display
formatted = metadata_processor.format_parameters_for_display(params)
print(formatted)
# Output:
# beautiful landscape, detailed
# Negative prompt: blurry, low quality
# Steps: 20, CFG scale: 7.5, Sampler: Euler a, Width: 512, Height: 512
```

## UI Integration Examples

### Register UI Components (WebUI Mode)

```python
from civitai_manager_libs.compat import get_compatibility_layer
import gradio as gr

def create_ui():
    with gr.Blocks() as ui:
        gr.Markdown("# Civitai Shortcut")
        # Your UI components here
    return ui

compat = get_compatibility_layer()
ui_bridge = compat.ui_bridge

# Register with WebUI (WebUI mode only)
def on_ui_tabs():
    ui = create_ui()
    return [(ui, "Civitai Shortcut", "civitai_shortcut")]

ui_bridge.register_ui_tabs(on_ui_tabs)
```

### Create Send-to Buttons

```python
# Create send-to buttons for parameter transfer
targets = ["txt2img", "img2img", "inpaint", "extras"]
send_buttons = ui_bridge.create_send_to_buttons(targets)

# Create UI components
with gr.Blocks() as ui:
    image_component = gr.Image()
    text_component = gr.Textbox()
    
    # Add send-to buttons
    if send_buttons:
        with gr.Row():
            for target, button in send_buttons.items():
                button.render()

# Bind button functionality
ui_bridge.bind_send_to_buttons(send_buttons, image_component, text_component)
```

### Launch Standalone Mode

```python
# Using the UI adapter (recommended)
from ui_adapter import create_civitai_shortcut_ui

compat = get_compatibility_layer()
if compat.is_standalone_mode():
    ui_bridge = compat.ui_bridge
    
    # Create UI using the adapter
    def create_ui():
        import gradio as gr
        with gr.Blocks(title="Civitai Shortcut") as ui:
            create_civitai_shortcut_ui(compat)
        return ui
    
    ui_bridge.launch_standalone(
        create_ui,
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )

# Or using the main application directly
from main import CivitaiShortcutApp

app = CivitaiShortcutApp()
app.launch(host="0.0.0.0", port=7860, share=False, debug=False)
```

## Sampler Information Examples

### Get Available Samplers  

```python
from civitai_manager_libs.compat import get_compatibility_layer

compat = get_compatibility_layer()
sampler_provider = compat.sampler_provider

# Get sampler lists
samplers = sampler_provider.get_samplers()
img2img_samplers = sampler_provider.get_samplers_for_img2img()
upscale_modes = sampler_provider.get_upscale_modes()
sd_upscalers = sampler_provider.get_sd_upscalers()
all_upscalers = sampler_provider.get_all_upscalers()

print("Available samplers:")
for sampler in samplers:
    print(f"  - {sampler}")

print("\nImg2Img samplers:")
for sampler in img2img_samplers:
    print(f"  - {sampler}")

print("\nUpscale modes:")
for mode in upscale_modes:
    print(f"  - {mode}")

print("\nSD Upscalers:")
for upscaler in sd_upscalers:
    print(f"  - {upscaler}")
```

### Use in UI Components

```python
import gradio as gr

samplers = sampler_provider.get_samplers()
upscalers = sampler_provider.get_all_upscalers()
default_sampler = sampler_provider.get_default_sampler()

with gr.Blocks() as ui:
    sampler_dropdown = gr.Dropdown(
        label="Sampling method",
        choices=samplers,
        value=default_sampler
    )
    
    upscaler_dropdown = gr.Dropdown(
        label="Upscaler",
        choices=upscalers,
        value="None"
    )
```

## Parameter Processing Examples

### Parse and Validate Parameters

```python
from civitai_manager_libs.compat import get_compatibility_layer

compat = get_compatibility_layer()
param_processor = compat.parameter_processor

# Parse parameters text
parameters_text = """
beautiful landscape, detailed
Negative prompt: blurry, low quality
Steps: 20, Sampler: Euler a, CFG scale: 7.5, Seed: 123456789, Size: 512x768
"""

parsed_params = param_processor.parse_parameters(parameters_text)
print("Parsed parameters:", parsed_params)

# Validate parameters
validated_params = param_processor.validate_parameters(parsed_params)
print("Validated parameters:", validated_params)
```

### Extract and Merge Parameters

```python
# Extract prompts using the correct method name
positive, negative = param_processor.extract_prompt_and_negative(parameters_text)
print(f"Positive: {positive}")
print(f"Negative: {negative}")

# Validate parameters
validated_params = param_processor.validate_parameters(parsed_params)
print("Validated parameters:", validated_params)

# Merge parameters
base_params = {'steps': 20, 'cfg_scale': 7.5}
override_params = {'steps': 30, 'sampler_name': 'DPM++ 2M'}

merged = param_processor.merge_parameters(base_params, override_params)
print("Merged parameters:", merged)
# Output: {'steps': 30, 'cfg_scale': 7.5, 'sampler_name': 'DPM++ 2M'}
```

### Format Parameters

```python
# Format parameters for display
params = {
    'prompt': 'anime character, detailed',
    'negative_prompt': 'bad anatomy',
    'steps': 25,
    'cfg_scale': 8.0,
    'sampler_name': 'DPM++ 2M Karras'
}

formatted_text = param_processor.format_parameters(params)
print(formatted_text)
```

## Error Handling Examples

### Graceful Degradation

```python
from civitai_manager_libs.compat import get_compatibility_layer

try:
    compat = get_compatibility_layer()
    
    # Try to extract metadata
    metadata_processor = compat.metadata_processor
    info = metadata_processor.extract_png_info("nonexistent_file.png")
    
    if info[0] is None:
        print("No metadata found or file doesn't exist")
    else:
        print("Metadata extracted successfully")
        
except Exception as e:
    print(f"Error occurred: {e}")
    # Fallback behavior
```

### Configuration Fallbacks

```python
config = compat.config_manager

# Use safe defaults when configuration is missing
api_key = config.get_config('civitai_api_key', '')
if not api_key:
    print("Warning: No API key configured")
    
max_downloads = config.get_config('max_download_concurrent', 3)
if max_downloads < 1 or max_downloads > 10:
    print("Warning: Invalid download count, using default")
    max_downloads = 3
```

## Advanced Usage Examples

### Custom Adapter Implementation

```python
# Example of extending the compatibility layer with custom adapters
from civitai_manager_libs.compat.interfaces import IPathManager

class CustomPathManager(IPathManager):
    """Custom path manager implementation."""
    
    def get_base_path(self) -> str:
        return "/custom/application/path"
    
    def get_extension_path(self) -> str:
        return "/custom/extension/path"
    
    # Implement other required methods...

# Use custom adapter (advanced usage)
compat = CompatibilityLayer(mode='standalone')
compat._path_manager = CustomPathManager()
```

### Environment-Specific Logic

```python
from civitai_manager_libs.compat import get_compatibility_layer

compat = get_compatibility_layer()

if compat.is_webui_mode():
    # WebUI-specific functionality
    ui_bridge = compat.ui_bridge
    if hasattr(ui_bridge, 'request_restart'):
        ui_bridge.request_restart()       # Request WebUI restart
    
    # Access WebUI-specific features
    config = compat.config_manager
    webui_embeddings = config.get_embeddings_dir()
    if webui_embeddings:
        print(f"Using WebUI embeddings directory: {webui_embeddings}")
    
else:
    # Standalone-specific functionality
    print("Running in standalone mode")
    print("WebUI integration features not available")
    
    # Use standalone features
    from main import CivitaiShortcutApp
    app = CivitaiShortcutApp()
    print("Standalone application initialized")
```

### Testing with Forced Environment

```python
import unittest
from civitai_manager_libs.compat import get_compatibility_layer, reset_compatibility_layer
from civitai_manager_libs.compat.environment_detector import EnvironmentDetector

class TestCivitaiFeatures(unittest.TestCase):
    
    def setUp(self):
        """Reset compatibility layer before each test."""
        reset_compatibility_layer()
        EnvironmentDetector.reset_cache()
    
    def test_webui_mode_features(self):
        """Test features in WebUI mode."""
        # Force WebUI mode for testing
        compat = get_compatibility_layer(mode='webui')
        self.assertTrue(compat.is_webui_mode())
        
        # Test WebUI-specific functionality
        path_manager = compat.path_manager
        script_path = path_manager.get_script_path()
        self.assertIsNotNone(script_path)
    
    def test_standalone_mode_features(self):
        """Test features in standalone mode."""
        # Force standalone mode for testing
        compat = get_compatibility_layer(mode='standalone')
        self.assertTrue(compat.is_standalone_mode())
        
        # Test standalone-specific functionality
        config_manager = compat.config_manager
        config_manager.set_config('test_key', 'test_value')
        self.assertEqual(config_manager.get_config('test_key'), 'test_value')
```
        compat = get_compatibility_layer(mode='webui')
        
        # Test WebUI-specific functionality
        self.assertTrue(compat.is_webui_mode())
        
        # Test components
        path_manager = compat.path_manager
        self.assertIsNotNone(path_manager.get_base_path())
    
    def test_standalone_mode_features(self):
        """Test features in standalone mode."""
        reset_compatibility_layer()
        compat = get_compatibility_layer(mode='standalone')
        
        # Test standalone functionality
        self.assertTrue(compat.is_standalone_mode())
        
        # Test components
        config_manager = compat.config_manager
        self.assertIsNotNone(config_manager.get_all_configs())
```

## Best Practices

### 1. Always Use the Compatibility Layer

```python
# Good: Use compatibility layer
from civitai_manager_libs.compat import get_compatibility_layer
compat = get_compatibility_layer()
path_manager = compat.path_manager

# Bad: Direct import of WebUI modules
# from modules import scripts  # This will fail in standalone mode
```

### 2. Handle Both Modes Gracefully

```python
compat = get_compatibility_layer()

if compat.is_webui_mode():
    # WebUI-specific features
    ui_bridge = compat.ui_bridge
    send_buttons = ui_bridge.create_send_to_buttons(["txt2img", "img2img"])
else:
    # Standalone alternatives
    print("Send-to functionality not available in standalone mode")
    send_buttons = None
```

### 3. Use Configuration Defaults

```python
config = compat.config_manager

# Always provide sensible defaults
download_path = config.get_config('download_path', 'models')
max_concurrent = config.get_config('max_download_concurrent', 3)
nsfw_filter = config.get_config('nsfw_filter', False)
```

### 4. Validate User Input

```python
param_processor = compat.parameter_processor

# Always validate parameters before use
user_params = {'steps': 150, 'cfg_scale': 50}  # Invalid values
validated = param_processor.validate_parameters(user_params)
# validated will have corrected values: {'steps': 100, 'cfg_scale': 20}
```

### 5. Proper Error Handling

```python
try:
    compat = get_compatibility_layer()
    metadata_processor = compat.metadata_processor
    
    # Try to extract metadata
    info = metadata_processor.extract_png_info("image.png")
    if info[1]:  # Check if generation data exists
        params = info[1]
        print("Parameters found:", params)
    else:
        print("No generation parameters found")
        
except Exception as e:
    print(f"Error processing image: {e}")
    # Implement fallback behavior
```

This documentation provides comprehensive examples for using the compatibility layer effectively across both WebUI and standalone modes.
