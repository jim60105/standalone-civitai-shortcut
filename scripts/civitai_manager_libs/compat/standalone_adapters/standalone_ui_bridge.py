"""
Standalone UI Bridge

Provides UI integration for standalone execution without WebUI dependencies.
"""

import json
import os
from typing import Callable, Any, List

from ..interfaces.iui_bridge import IUIBridge


class StandaloneUIBridge(IUIBridge):
    """UI bridge implementation for standalone mode."""
    
    def __init__(self):
        """Initialize the standalone UI bridge."""
        self._config = {}
    
    def register_ui_tabs(self, callback: Callable) -> None:
        """Register UI tabs for standalone mode."""
        # In standalone mode, we don't need to register with WebUI
        # The UI will be launched directly
        pass
    
    def create_send_to_buttons(self, targets: List[str]) -> Any:
        """Create send-to buttons for standalone mode."""
        try:
            import gradio as gr
            
            # Create simple copy buttons since we can't send to WebUI tabs
            buttons = {}
            for target in targets:
                buttons[target] = gr.Button(f"Copy for {target}", size="sm", variant="secondary")
            
            return buttons
        except ImportError:
            return None
    
    def bind_send_to_buttons(self, buttons: Any, image_component: Any, text_component: Any) -> None:
        """Bind send-to button functionality for standalone mode."""
        if not buttons:
            return
        
        try:
            import gradio as gr
            
            def copy_parameters(text):
                """Copy parameters to clipboard or save to file."""
                if text:
                    # Save to a temporary file that can be imported
                    self._save_parameters_for_export(text)
                    return gr.update(value="Parameters copied! Check exported_parameters.txt")
                return gr.update()
            
            # Bind each button
            for target, button in buttons.items():
                if hasattr(button, 'click'):
                    button.click(
                        fn=copy_parameters,
                        inputs=[text_component] if text_component else [],
                        outputs=[text_component] if text_component else []
                    )
        except (ImportError, AttributeError):
            pass
    
    def launch_standalone(self, ui_callback: Callable, **kwargs) -> None:
        """Launch the UI in standalone mode."""
        try:
            import gradio as gr
            
            # Create the UI
            with gr.Blocks(title="Civitai Shortcut - Standalone Mode") as app:
                ui_callback()
            
            # Launch with default settings
            launch_kwargs = {
                'server_name': kwargs.get('server_name', '0.0.0.0'),
                'server_port': kwargs.get('server_port', 7860),
                'share': kwargs.get('share', False),
                'debug': kwargs.get('debug', False),
                'show_error': True,
                'quiet': kwargs.get('quiet', False),
            }
            
            app.launch(**launch_kwargs)
            
        except ImportError:
            print("Gradio is not available. Cannot launch standalone UI.")
        except Exception as e:
            print(f"Error launching standalone UI: {e}")
    
    def is_webui_mode(self) -> bool:
        """Check if running in WebUI mode."""
        return False
    
    def interrupt_generation(self) -> None:
        """Interrupt generation (not applicable in standalone mode)."""
        # No generation to interrupt in standalone mode
        pass
    
    def request_restart(self) -> None:
        """Request restart (not applicable in standalone mode)."""
        # No restart mechanism in standalone mode
        pass
    
    def get_ui_config(self, key: str, default: Any = None) -> Any:
        """Get UI configuration value."""
        return self._config.get(key, default)
    
    def _save_parameters_for_export(self, parameters_text: str) -> None:
        """Save parameters to a file for manual import."""
        try:
            export_file = os.path.join(os.getcwd(), 'exported_parameters.txt')
            with open(export_file, 'w', encoding='utf-8') as f:
                f.write(parameters_text)
            
            # Also save as JSON for easier processing
            try:
                # Parse parameters into structured format
                from .standalone_parameter_processor import StandaloneParameterProcessor
                processor = StandaloneParameterProcessor()
                params = processor.parse_parameters(parameters_text)
                
                json_file = os.path.join(os.getcwd(), 'exported_parameters.json')
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(params, f, indent=2, ensure_ascii=False)
            except Exception:
                # If JSON export fails, just continue with text export
                pass
                
        except Exception:
            # If export fails, just continue silently
            pass
