"""
UI Bridge Interface

Provides unified UI integration across WebUI and standalone execution modes.
"""

from abc import ABC, abstractmethod
from typing import Callable, Any, List


class IUIBridge(ABC):
    """Abstract interface for UI integration across different execution modes."""

    @abstractmethod
    def register_ui_tabs(self, callback: Callable) -> None:
        """
        Register UI tabs with the host application.

        Args:
            callback (Callable): Function that returns UI components
        """
        pass

    @abstractmethod
    def create_send_to_buttons(self, targets: List[str]) -> Any:
        """
        Create buttons for sending parameters to different targets.

        Args:
            targets (List[str]): List of target names (e.g., ['txt2img', 'img2img'])

        Returns:
            Any: UI components for send-to functionality
        """
        pass

    @abstractmethod
    def bind_send_to_buttons(self, buttons: Any, image_component: Any, text_component: Any) -> None:
        """
        Bind send-to button functionality.

        Args:
            buttons (Any): The send-to buttons created by create_send_to_buttons
            image_component (Any): The image component to bind
            text_component (Any): The text component to bind
        """
        pass

    @abstractmethod
    def launch_standalone(self, ui_callback: Callable, **kwargs) -> None:
        """
        Launch the UI in standalone mode.

        Args:
            ui_callback (Callable): Function that creates the UI
            **kwargs: Additional launch parameters
        """
        pass

    @abstractmethod
    def is_webui_mode(self) -> bool:
        """
        Check if running in WebUI mode.

        Returns:
            bool: True if in WebUI mode, False if standalone
        """
        pass

    @abstractmethod
    def interrupt_generation(self) -> None:
        """
        Interrupt ongoing generation process.
        Only applicable in WebUI mode.
        """
        pass

    @abstractmethod
    def request_restart(self) -> None:
        """
        Request application restart.
        Only applicable in WebUI mode.
        """
        pass

    @abstractmethod
    def get_ui_config(self, key: str, default: Any = None) -> Any:
        """
        Get UI-specific configuration values.

        Args:
            key (str): Configuration key
            default (Any): Default value if key doesn't exist

        Returns:
            Any: Configuration value
        """
        pass
