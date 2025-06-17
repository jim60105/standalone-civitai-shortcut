"""
WebUI UI Bridge

Provides UI integration using AUTOMATIC1111 WebUI modules.
"""

from typing import Callable, Any, List
from ..interfaces.iui_bridge import IUIBridge


class WebUIUIBridge(IUIBridge):
    """UI bridge implementation using WebUI modules."""

    def register_ui_tabs(self, callback: Callable) -> None:
        """Register UI tabs with WebUI."""
        try:
            from modules import script_callbacks

            script_callbacks.on_ui_tabs(callback)
        except (ImportError, AttributeError):
            # WebUI not available, ignore
            pass

    def create_send_to_buttons(self, targets: List[str]) -> Any:
        """Create send-to buttons using WebUI's parameter copypaste."""
        try:
            import modules.infotext_utils as parameters_copypaste

            return parameters_copypaste.create_buttons(targets)
        except (ImportError, AttributeError):
            # Fallback to simple buttons
            return self._create_simple_buttons(targets)

    def bind_send_to_buttons(self, buttons: Any, image_component: Any, text_component: Any) -> None:
        """Bind send-to button functionality."""
        try:
            import modules.infotext_utils as parameters_copypaste

            parameters_copypaste.bind_buttons(buttons, image_component, text_component)
        except (ImportError, AttributeError):
            # Fallback binding
            self._bind_simple_buttons(buttons, image_component, text_component)

    def launch_standalone(self, ui_callback: Callable, **kwargs) -> None:
        """Launch UI in standalone mode (not applicable for WebUI mode)."""
        # In WebUI mode, this is handled by the WebUI itself
        pass

    def is_webui_mode(self) -> bool:
        """Check if running in WebUI mode."""
        return True

    def interrupt_generation(self) -> None:
        """Interrupt generation using WebUI state."""
        try:
            from modules import shared

            if hasattr(shared, "state"):
                shared.state.interrupt()
        except (ImportError, AttributeError):
            pass

    def request_restart(self) -> None:
        """Request WebUI restart."""
        try:
            from modules import shared

            if hasattr(shared, "state"):
                shared.state.need_restart = True
        except (ImportError, AttributeError):
            pass

    def get_ui_config(self, key: str, default: Any = None) -> Any:
        """Get UI configuration from WebUI."""
        try:
            from modules import shared

            if hasattr(shared, "opts"):
                return getattr(shared.opts, key, default)
        except (ImportError, AttributeError):
            pass

        return default

    def _create_simple_buttons(self, targets: List[str]) -> Any:
        """Create simple buttons as fallback."""
        try:
            import gradio as gr

            buttons = {}
            for target in targets:
                buttons[target] = gr.Button(f"Send to {target}", size="sm")
            return buttons
        except ImportError:
            return None

    def _bind_simple_buttons(self, buttons: Any, image_component: Any, text_component: Any) -> None:
        """Bind simple buttons with basic functionality."""
        if not buttons:
            return

        try:
            import gradio as gr

            def copy_to_clipboard(text):
                # Simple copy functionality - user will need to paste manually
                return gr.update(value=f"Copied: {text}")

            for target, button in buttons.items():
                if hasattr(button, "click"):
                    button.click(
                        fn=copy_to_clipboard,
                        inputs=[text_component] if text_component else [],
                        outputs=[text_component] if text_component else [],
                    )
        except (ImportError, AttributeError):
            pass
