"""
Unified event handling system for UI interactions and async operations.
Supports both WebUI and standalone modes.
"""

import gradio as gr
import threading
from typing import Callable, Dict, List, Any, Optional

from .logging_config import get_logger

logger = get_logger(__name__)


class EventHandler:
    """Centralized event dispatcher and async operation handler."""

    def __init__(self, mode: str = 'webui'):
        self.mode = mode
        self._callbacks: Dict[str, List[Callable]] = {}

    def register_callback(self, event_name: str, callback: Callable) -> None:
        """Register a callback for a named event."""
        self._callbacks.setdefault(event_name, []).append(callback)

    def trigger_event(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        """Invoke all callbacks registered for the event."""
        for cb in self._callbacks.get(event_name, []):
            try:
                cb(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in callback '{event_name}': {e}")

    def setup_component_events(
        self, components: Dict[str, gr.Component], actions: Dict[str, Callable]
    ) -> None:
        """Bind Gradio components to action functions with unified UI error prompt handling."""
        for name, comp in components.items():
            if name in actions:
                action = actions[name]

                # Wrap action with error handling to prevent connection disruption
                def create_wrapped_action(original_action, action_name):
                    def wrapped_action(*args, **kwargs):
                        try:
                            return original_action(*args, **kwargs)
                        except Exception as e:
                            # Log the error and display a unified UI error prompt,
                            # then return a safe fallback
                            logger.error(f"Error in action {action_name}: {e}", exc_info=True)
                            
                            # Use notification service instead of direct Gradio call
                            from .ui.notification_service import get_notification_service
                            notification_service = get_notification_service()
                            if notification_service:
                                notification_service.show_error(f"Error in {action_name}: {e}")
                            
                            return gr.update()

                    return wrapped_action

                wrapped_action = create_wrapped_action(action, name)

                if isinstance(comp, gr.Button):
                    comp.click(fn=wrapped_action)
                elif isinstance(comp, gr.Slider) or isinstance(comp, gr.Dropdown):
                    comp.change(fn=wrapped_action)
                elif isinstance(comp, gr.Textbox):
                    comp.change(fn=wrapped_action)
                    if hasattr(comp, 'submit'):
                        comp.submit(fn=wrapped_action)

    def handle_async_operation(
        self,
        operation: Callable,
        success_callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None,
    ) -> threading.Thread:
        """Execute an operation asynchronously with optional callbacks."""

        def runner() -> None:
            try:
                result = operation()
                if success_callback:
                    success_callback(result)
            except Exception as e:
                if error_callback:
                    error_callback(e)
                else:
                    logger.error(f"Async operation error: {e}")

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()
        return thread
