from abc import ABC, abstractmethod
from typing import Optional


class NotificationService(ABC):
    """Abstract interface for UI notification services."""

    @abstractmethod
    def show_error(self, message: str, duration: int = 5) -> None:
        """Display an error message to the user."""
        pass

    @abstractmethod
    def show_warning(self, message: str, duration: int = 3) -> None:
        """Display a warning message to the user."""
        pass

    @abstractmethod
    def show_info(self, message: str, duration: int = 3) -> None:
        """Display an informational message to the user."""
        pass


class GradioNotificationService(NotificationService):
    """Notification service implementation for Gradio UI."""

    def show_error(self, message: str, duration: int = 5) -> None:
        try:
            import gradio as gr

            gr.Error(message, duration=duration)
        except Exception:
            print(f"[ERROR] {message}")

    def show_warning(self, message: str, duration: int = 3) -> None:
        try:
            import gradio as gr

            gr.Warning(message, duration=duration)
        except Exception:
            print(f"[WARNING] {message}")

    def show_info(self, message: str, duration: int = 3) -> None:
        try:
            import gradio as gr

            gr.Info(message, duration=duration)
        except Exception:
            print(f"[INFO] {message}")


class ConsoleNotificationService(NotificationService):
    """Console notification service for non-UI environments."""

    def show_error(self, message: str, duration: int = 5) -> None:
        print(f"[ERROR] {message}")

    def show_warning(self, message: str, duration: int = 3) -> None:
        print(f"[WARNING] {message}")

    def show_info(self, message: str, duration: int = 3) -> None:
        print(f"[INFO] {message}")


class SilentNotificationService(NotificationService):
    """Silent notification service (no output), useful for testing."""

    def show_error(self, message: str, duration: int = 5) -> None:
        pass

    def show_warning(self, message: str, duration: int = 3) -> None:
        pass

    def show_info(self, message: str, duration: int = 3) -> None:
        pass


# Global notification service instance
_notification_service: Optional[NotificationService] = None


def get_notification_service() -> Optional[NotificationService]:
    """Get the current global notification service instance."""
    return _notification_service


def set_notification_service(service: NotificationService) -> None:
    """Set the global notification service instance."""
    global _notification_service
    _notification_service = service


# Initialize default notification service to Gradio implementation
set_notification_service(GradioNotificationService())
