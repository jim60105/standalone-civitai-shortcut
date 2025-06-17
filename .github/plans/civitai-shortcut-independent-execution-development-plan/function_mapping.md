# Function Mapping and Alternative Solutions

## Overview

This document provides detailed mapping between AUTOMATIC1111 WebUI functions and their proposed alternatives for standalone execution. Each mapping includes implementation complexity, testing requirements, and migration strategy.

## Function Mapping Table

| Original Function | Current Usage | Alternative Solution | Implementation Effort | Compatibility Impact |
|------------------|---------------|---------------------|---------------------|---------------------|
| `scripts.basedir()` | Get extension base path | File-based path detection | Low (0.5 days) | None |
| `shared.cmd_opts.*` | Access command line options | Configuration system | Medium (2 days) | Medium |
| `shared.state.*` | WebUI state management | Custom state manager | High (3 days) | High |
| `shared.latent_upscale_modes` | UI dropdown options | Static configuration | Low (0.5 days) | Low |
| `shared.sd_upscalers` | UI dropdown options | Static configuration | Low (0.5 days) | Low |
| `script_callbacks.on_ui_tabs()` | UI registration | Gradio launcher | Medium (1.5 days) | Medium |
| `samplers/samplers_for_img2img` | Sampler options | Static list | Low (0.5 days) | Low |
| `parameters_copypaste.*` | Parameter transfer | Copy/export system | High (3 days) | High |
| `modules.extras.run_pnginfo()` | PNG metadata extraction | PIL implementation | Medium (1.5 days) | Low |

## Detailed Function Mappings

### 1. Path Management Functions

#### modules.scripts.basedir()

**Original Implementation:**
```python
from modules import scripts
extension_base = scripts.basedir()
```

**Alternative Implementation:**
```python
import os

def get_extension_base():
    """Get extension base directory path"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Usage
extension_base = get_extension_base()
```

**Testing Requirements:**
- Verify path correctness across different OS platforms
- Test resource loading from calculated path
- Validate relative path resolution

### 2. Configuration Management Functions

#### shared.cmd_opts.*

**Original Implementation:**
```python
from modules import shared

if shared.cmd_opts.embeddings_dir:
    model_folders['TextualInversion'] = shared.cmd_opts.embeddings_dir
```

**Alternative Implementation:**
```python
import json
import os

class ConfigurationManager:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file or environment"""
        # Try loading from file first
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        
        # Fallback to environment variables
        return {
            'embeddings_dir': os.environ.get('EMBEDDINGS_DIR'),
            'hypernetwork_dir': os.environ.get('HYPERNETWORK_DIR'),
            'ckpt_dir': os.environ.get('CKPT_DIR'),
            'lora_dir': os.environ.get('LORA_DIR'),
        }
    
    def get_model_folders(self):
        """Get model folder paths with configuration overrides"""
        default_folders = {
            'Checkpoint': os.path.join("models", "Stable-diffusion"),
            'LORA': os.path.join("models", "Lora"),
            'TextualInversion': os.path.join("embeddings"),
            'Hypernetwork': os.path.join("models", "hypernetworks"),
        }
        
        # Apply configuration overrides
        if self.config.get('embeddings_dir'):
            default_folders['TextualInversion'] = self.config['embeddings_dir']
        if self.config.get('hypernetwork_dir'):
            default_folders['Hypernetwork'] = self.config['hypernetwork_dir']
        if self.config.get('ckpt_dir'):
            default_folders['Checkpoint'] = self.config['ckpt_dir']
        if self.config.get('lora_dir'):
            default_folders['LORA'] = self.config['lora_dir']
            
        return default_folders

# Usage
config_manager = ConfigurationManager()
model_folders = config_manager.get_model_folders()
```

**Configuration File Example (config.json):**
```json
{
    "embeddings_dir": "/custom/path/embeddings",
    "hypernetwork_dir": "/custom/path/hypernetworks",
    "ckpt_dir": "/custom/path/models",
    "lora_dir": "/custom/path/lora",
    "hide_ui_dir_config": false,
    "api_key": "your_civitai_api_key"
}
```

**Testing Requirements:**
- Test configuration loading from file
- Test environment variable fallback
- Verify path resolution on different platforms
- Test configuration validation and error handling

### 3. State Management Functions

#### shared.state.*

**Original Implementation:**
```python
from modules import shared

shared.state.interrupt()
shared.state.need_restart = True
```

**Alternative Implementation:**
```python
import threading
import time
from enum import Enum

class AppState(Enum):
    IDLE = "idle"
    RUNNING = "running"  
    INTERRUPTED = "interrupted"
    RESTART_NEEDED = "restart_needed"

class StateManager:
    def __init__(self):
        self._state = AppState.IDLE
        self._interrupt_flag = threading.Event()
        self._restart_flag = threading.Event()
        self._lock = threading.Lock()
    
    @property
    def state(self):
        with self._lock:
            return self._state
    
    def interrupt(self):
        """Request interruption of current operation"""
        with self._lock:
            self._interrupt_flag.set()
            if self._state == AppState.RUNNING:
                self._state = AppState.INTERRUPTED
    
    def need_restart(self):
        """Signal that restart is needed"""
        with self._lock:
            self._restart_flag.set()
            self._state = AppState.RESTART_NEEDED
    
    def is_interrupted(self):
        """Check if interruption was requested"""
        return self._interrupt_flag.is_set()
    
    def is_restart_needed(self):
        """Check if restart is needed"""
        return self._restart_flag.is_set()
    
    def reset(self):
        """Reset all flags"""
        with self._lock:
            self._interrupt_flag.clear()
            self._restart_flag.clear()
            self._state = AppState.IDLE

# Global state manager instance
state = StateManager()

# Usage
state.interrupt()
state.need_restart()
```

**Testing Requirements:**
- Test thread safety of state operations
- Verify interrupt flag behavior
- Test state transitions
- Validate concurrent access scenarios

### 4. UI Option Functions

#### shared.latent_upscale_modes & shared.sd_upscalers

**Original Implementation:**
```python
from modules import shared

choices = [*shared.latent_upscale_modes, *[x.name for x in shared.sd_upscalers]]
```

**Alternative Implementation:**
```python
class UIOptions:
    """Static UI options for standalone mode"""
    
    LATENT_UPSCALE_MODES = [
        "Latent",
        "Latent (antialiased)",
        "Latent (bicubic)",
        "Latent (bicubic antialiased)",
        "Latent (nearest)",
        "Latent (nearest-exact)"
    ]
    
    SD_UPSCALERS = [
        {"name": "None"},
        {"name": "Lanczos"},
        {"name": "Nearest"},
        {"name": "ESRGAN_4x"},
        {"name": "LDSR"},
        {"name": "ScuNET GAN"},
        {"name": "ScuNET PSNR"},
        {"name": "SwinIR 4x"}
    ]
    
    @classmethod
    def get_upscaler_choices(cls):
        """Get combined upscaler choices for UI"""
        return [*cls.LATENT_UPSCALE_MODES, *[x["name"] for x in cls.SD_UPSCALERS]]

# Usage
choices = UIOptions.get_upscaler_choices()
```

**Configuration-based Alternative:**
```python
import json

def load_ui_options(config_file="ui_options.json"):
    """Load UI options from configuration file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return UIOptions.get_default_options()

class UIOptions:
    def __init__(self, config_file=None):
        self.options = load_ui_options(config_file) if config_file else self.get_default_options()
    
    @staticmethod
    def get_default_options():
        return {
            "latent_upscale_modes": [
                "Latent", "Latent (antialiased)", "Latent (bicubic)"
            ],
            "sd_upscalers": [
                "None", "Lanczos", "Nearest", "ESRGAN_4x"
            ]
        }
```

**Testing Requirements:**
- Verify option list completeness
- Test configuration loading
- Validate UI dropdown population

### 5. UI Registration Functions

#### script_callbacks.on_ui_tabs()

**Original Implementation:**
```python
from modules import script_callbacks

def on_ui_tabs():
    # UI construction code
    return (civitai_shortcut, "Civitai Shortcut", "civitai_shortcut"),

script_callbacks.on_ui_tabs(on_ui_tabs)
```

**Alternative Implementation:**
```python
import gradio as gr

class UILauncher:
    def __init__(self, standalone_mode=False):
        self.standalone_mode = standalone_mode
    
    def register_ui_tabs(self, ui_callback):
        """Register UI tabs based on execution mode"""
        if self.standalone_mode:
            self.launch_standalone(ui_callback)
        else:
            self.register_webui_tabs(ui_callback)
    
    def launch_standalone(self, ui_callback):
        """Launch as standalone Gradio application"""
        ui_components = ui_callback()
        if isinstance(ui_components, tuple):
            interface, title, _ = ui_components
            interface.launch(
                server_name="0.0.0.0",
                server_port=7861,
                share=False,
                debug=False
            )
        else:
            ui_components.launch()
    
    def register_webui_tabs(self, ui_callback):
        """Register with WebUI if available"""
        try:
            from modules import script_callbacks
            script_callbacks.on_ui_tabs(ui_callback)
        except ImportError:
            print("WebUI not available, falling back to standalone mode")
            self.standalone_mode = True
            self.launch_standalone(ui_callback)

# Environment detection
def detect_execution_mode():
    """Detect if running in WebUI or standalone mode"""
    try:
        import modules.shared
        return False  # WebUI mode
    except ImportError:
        return True   # Standalone mode

# Usage
launcher = UILauncher(standalone_mode=detect_execution_mode())
launcher.register_ui_tabs(on_ui_tabs)
```

**Testing Requirements:**
- Test WebUI integration mode
- Test standalone launch mode
- Verify environment detection
- Test graceful fallback

### 6. Sampler Functions

#### modules.sd_samplers

**Original Implementation:**
```python
from modules.sd_samplers import samplers, samplers_for_img2img

choices = [x.name for x in samplers]
```

**Alternative Implementation:**
```python
class SamplerManager:
    """Manage available samplers for both modes"""
    
    DEFAULT_SAMPLERS = [
        {"name": "Euler", "aliases": ["euler"]},
        {"name": "Euler a", "aliases": ["euler_ancestral"]},
        {"name": "LMS", "aliases": ["lms"]},
        {"name": "Heun", "aliases": ["heun"]},
        {"name": "DPM2", "aliases": ["dpm2"]},
        {"name": "DPM2 a", "aliases": ["dpm2_ancestral"]},
        {"name": "DPM++ 2S a", "aliases": ["dpmpp_2s_ancestral"]},
        {"name": "DPM++ 2M", "aliases": ["dpmpp_2m"]},
        {"name": "DPM++ SDE", "aliases": ["dpmpp_sde"]},
        {"name": "DPM fast", "aliases": ["dpm_fast"]},
        {"name": "DPM adaptive", "aliases": ["dpm_adaptive"]},
        {"name": "LMS Karras", "aliases": ["lms_karras"]},
        {"name": "DPM2 Karras", "aliases": ["dpm2_karras"]},
        {"name": "DPM2 a Karras", "aliases": ["dpm2_ancestral_karras"]},
        {"name": "DPM++ 2S a Karras", "aliases": ["dpmpp_2s_ancestral_karras"]},
        {"name": "DPM++ 2M Karras", "aliases": ["dpmpp_2m_karras"]},
        {"name": "DDIM", "aliases": ["ddim"]},
        {"name": "PLMS", "aliases": ["plms"]}
    ]
    
    def __init__(self):
        self.samplers = self.load_samplers()
    
    def load_samplers(self):
        """Load samplers from WebUI or use defaults"""
        try:
            from modules.sd_samplers import samplers
            return [{"name": x.name, "aliases": getattr(x, 'aliases', [])} for x in samplers]
        except ImportError:
            return self.DEFAULT_SAMPLERS
    
    def get_sampler_names(self):
        """Get list of sampler names for UI"""
        return [sampler["name"] for sampler in self.samplers]
    
    def get_sampler_by_name(self, name):
        """Find sampler by name or alias"""
        for sampler in self.samplers:
            if sampler["name"] == name or name in sampler.get("aliases", []):
                return sampler
        return None

# Usage
sampler_manager = SamplerManager()
choices = sampler_manager.get_sampler_names()
```

**Testing Requirements:**
- Test sampler list loading
- Verify name resolution and aliases
- Test fallback to default list

### 7. Parameter Transfer Functions

#### modules.infotext_utils (parameters_copypaste)

**Original Implementation:**
```python
import modules.infotext_utils as parameters_copypaste

send_to_buttons = parameters_copypaste.create_buttons(["txt2img","img2img", "inpaint", "extras"])
parameters_copypaste.bind_buttons(send_to_buttons, image_component, text_component)
```

**Alternative Implementation:**
```python
import gradio as gr
import json
import os
from datetime import datetime

class ParameterManager:
    """Manage parameter copying and export functionality"""
    
    def __init__(self, export_dir="exported_parameters"):
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
    
    def create_buttons(self, targets=None):
        """Create parameter transfer buttons"""
        if targets is None:
            targets = ["copy", "export", "save"]
        
        buttons = {}
        for target in targets:
            if target == "copy":
                buttons[target] = gr.Button(f"📋 Copy to Clipboard", variant="secondary")
            elif target == "export":
                buttons[target] = gr.Button(f"💾 Export Parameters", variant="secondary")
            elif target == "save":
                buttons[target] = gr.Button(f"💾 Save Recipe", variant="secondary")
            else:
                buttons[target] = gr.Button(f"📤 Send to {target.title()}", variant="secondary")
        
        return buttons
    
    def bind_buttons(self, buttons, image_component, text_component):
        """Bind button functionality"""
        for target, button in buttons.items():
            if target == "copy":
                button.click(
                    fn=self.copy_to_clipboard,
                    inputs=[text_component],
                    outputs=[gr.update()]  # Could show a temporary message
                )
            elif target == "export":
                button.click(
                    fn=self.export_parameters,
                    inputs=[text_component],
                    outputs=[gr.File()]
                )
            elif target == "save":
                button.click(
                    fn=self.save_recipe,
                    inputs=[text_component, image_component],
                    outputs=[gr.update()]
                )
    
    def copy_to_clipboard(self, parameters):
        """Copy parameters to clipboard (simulation)"""
        # In a real implementation, this would use a JavaScript callback
        # to copy to clipboard. For now, we return the text for display.
        return gr.update(value=f"Copied: {parameters[:100]}...")
    
    def export_parameters(self, parameters):
        """Export parameters to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"parameters_{timestamp}.txt"
        filepath = os.path.join(self.export_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(parameters)
        
        return filepath
    
    def save_recipe(self, parameters, image=None):
        """Save parameters as recipe"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        recipe_data = {
            "timestamp": timestamp,
            "parameters": parameters,
            "has_image": image is not None
        }
        
        filename = f"recipe_{timestamp}.json"
        filepath = os.path.join(self.export_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(recipe_data, f, indent=2)
        
        if image:
            image_path = os.path.join(self.export_dir, f"recipe_{timestamp}.png")
            image.save(image_path)
        
        return gr.update(value=f"Recipe saved: {filename}")

# Usage
param_manager = ParameterManager()
send_to_buttons = param_manager.create_buttons(["copy", "export", "save"])
param_manager.bind_buttons(send_to_buttons, image_component, text_component)
```

**JavaScript Integration for Clipboard:**
```javascript
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        console.log('Copying to clipboard was successful!');
    }, function(err) {
        console.error('Could not copy text: ', err);
    });
}
```

**Testing Requirements:**
- Test parameter extraction and formatting
- Verify file export functionality  
- Test recipe saving and loading
- Validate clipboard integration

### 8. Image Processing Functions

#### modules.extras.run_pnginfo()

**Original Implementation:**
```python
import modules

info1,generate_data,info3 = modules.extras.run_pnginfo(image)
```

**Alternative Implementation:**
```python
from PIL import Image
import json
import re

class ImageInfoExtractor:
    """Extract generation information from images"""
    
    def __init__(self):
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.webp']
    
    def run_pnginfo(self, image_input):
        """Extract PNG info similar to WebUI extras module"""
        try:
            if isinstance(image_input, str):
                # File path
                image = Image.open(image_input)
            else:
                # PIL Image object
                image = image_input
            
            # Extract text metadata
            info_text = self.extract_text_info(image)
            generation_params = self.parse_generation_params(info_text)
            
            # Return format similar to WebUI: (info1, generation_data, info3)
            return "", generation_params, ""
            
        except Exception as e:
            print(f"Error extracting image info: {e}")
            return "", "", ""
    
    def extract_text_info(self, image):
        """Extract text information from image metadata"""
        info_dict = {}
        
        # Try PNG text chunks
        if hasattr(image, 'text'):
            info_dict.update(image.text)
        
        # Try EXIF data
        if hasattr(image, '_getexif') and image._getexif():
            exif_dict = image._getexif()
            if exif_dict:
                info_dict.update({str(k): str(v) for k, v in exif_dict.items()})
        
        # Look for common parameter keys
        parameter_keys = ['parameters', 'Parameters', 'prompt', 'Prompt']
        for key in parameter_keys:
            if key in info_dict:
                return info_dict[key]
        
        return ""
    
    def parse_generation_params(self, info_text):
        """Parse generation parameters from info text"""
        if not info_text:
            return ""
        
        # Try to parse as structured parameters
        try:
            # Look for pattern like "Prompt: ... Negative prompt: ... Steps: ..."
            return self.parse_structured_params(info_text)
        except:
            # Return raw text if parsing fails
            return info_text
    
    def parse_structured_params(self, text):
        """Parse structured parameter text"""
        # This is a simplified parser - expand based on actual parameter formats
        params = {}
        
        # Extract sections
        sections = re.split(r'\n(?=[A-Z][a-z]+ prompt:|Steps:|Sampler:|CFG scale:)', text)
        
        for section in sections:
            if section.strip():
                # Parse key-value pairs
                if ':' in section:
                    parts = section.split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        params[key] = value
        
        return json.dumps(params, indent=2) if params else text

# Usage
extractor = ImageInfoExtractor()
info1, generation_data, info3 = extractor.run_pnginfo(image)
```

**Advanced Implementation with Multiple Format Support:**
```python
import exifread
from PIL import Image
from PIL.ExifTags import TAGS

class AdvancedImageInfoExtractor(ImageInfoExtractor):
    """Advanced image info extraction with multiple format support"""
    
    def extract_metadata_comprehensive(self, image_path):
        """Comprehensive metadata extraction"""
        metadata = {}
        
        try:
            # PIL-based extraction
            with Image.open(image_path) as img:
                # Basic info
                metadata['format'] = img.format
                metadata['size'] = img.size
                metadata['mode'] = img.mode
                
                # Text chunks (PNG)
                if hasattr(img, 'text'):
                    metadata['text'] = img.text
                
                # EXIF data
                if hasattr(img, '_getexif'):
                    exif = img._getexif()
                    if exif:
                        metadata['exif'] = {TAGS.get(k, k): v for k, v in exif.items()}
            
            # ExifRead-based extraction (more comprehensive)
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
                if tags:
                    metadata['exifread'] = {str(k): str(v) for k, v in tags.items()}
        
        except Exception as e:
            print(f"Error in comprehensive metadata extraction: {e}")
        
        return metadata
```

**Testing Requirements:**
- Test with various image formats (PNG, JPG, WebP)
- Verify parameter extraction accuracy
- Test with images containing no metadata
- Validate error handling for corrupted images

## Migration Strategy

### Phase 1: Core Infrastructure (2-3 days)
1. Implement `get_extension_base()` function
2. Create `ConfigurationManager` class
3. Set up basic testing framework

### Phase 2: State and UI Management (3-4 days)  
1. Implement `StateManager` class
2. Create `UILauncher` with mode detection
3. Implement `UIOptions` configuration system

### Phase 3: Advanced Features (4-5 days)
1. Build `ParameterManager` with export functionality
2. Implement `ImageInfoExtractor` with PIL
3. Create `SamplerManager` with fallback support

### Testing and Integration (2-3 days)
1. Comprehensive unit testing
2. Integration testing for both modes  
3. Documentation and examples

**Total Estimated Effort:** 11-15 days

## Backward Compatibility

All alternative implementations maintain backward compatibility through:

1. **Feature Detection**: Automatic detection of WebUI availability
2. **Graceful Degradation**: Fallback to standalone functionality when WebUI features unavailable
3. **Configuration Override**: Ability to force standalone mode even when WebUI is available
4. **API Compatibility**: Maintain same function signatures where possible

## Performance Considerations

- **Lazy Loading**: Load heavy dependencies only when needed
- **Caching**: Cache frequently accessed configuration and state
- **Memory Management**: Proper cleanup of resources in standalone mode
- **Error Handling**: Robust error handling prevents crashes from missing dependencies
