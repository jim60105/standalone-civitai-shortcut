from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import threading
import queue
import time

from ..logging_config import get_logger
logger = get_logger(__name__)

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
    """
    Notification service implementation for Gradio UI with thread-safe execution.

    This service uses a queue-based approach to ensure notifications are executed
    in the appropriate context, even when called from background threads.
    """

    def __init__(self):
        self._main_thread = threading.main_thread()
        self._notification_queue = queue.Queue()
        self._pending_notifications: List[Dict[str, Any]] = []

    def _is_main_thread(self) -> bool:
        """Check if we're currently in the main thread."""
        return threading.current_thread() is self._main_thread

    def _execute_gradio_notification(self, notification_type: str, message: str, duration: int):
        """Execute the actual Gradio notification."""
        try:
            import gradio as gr

            if notification_type == "error":
                raise gr.Error(message, duration=duration)
            elif notification_type == "warning":
                gr.Warning(message, duration=duration)
            elif notification_type == "info":
                gr.Info(message, duration=duration)
            return True
        except ImportError:
            # If gradio is not available or fails, fall back to console
            logger.info(f"[{notification_type.upper()}] {message}")
            return False

    def _queue_notification(self, notification_type: str, message: str, duration: int):
        """Queue a notification for later execution in main thread."""
        notification = {
            'type': notification_type,
            'message': message,
            'duration': duration,
            'thread': threading.current_thread().name,
            'timestamp': time.time(),
        }

        # Store in both queue and list
        self._notification_queue.put(notification)
        self._pending_notifications.append(notification)

        # Also logger.debug to console immediately for visibility
        logger.debug(f"[{notification_type.upper()} - QUEUED] {message}")

    def _execute_notification(self, notification_type: str, message: str, duration: int):
        """Execute a notification, handling thread context appropriately."""
        if self._is_main_thread():
            # We're in the main thread, try direct execution
            success = self._execute_gradio_notification(notification_type, message, duration)
            if not success:
                # If gradio execution failed, also log to console
                logger.info(f"[{notification_type.upper()}] {message}")
                # Also queue it for later execution in a proper gradio context
                self._queue_notification(notification_type, message, duration)
        else:
            # We're in a background thread, queue for later execution
            self._queue_notification(notification_type, message, duration)

    def show_error(self, message: str, duration: int = 5) -> None:
        # Raise exception directly
        self._execute_gradio_notification("error", message, duration)

    def show_warning(self, message: str, duration: int = 3) -> None:
        self._execute_notification("warning", message, duration)

    def show_info(self, message: str, duration: int = 3) -> None:
        self._execute_notification("info", message, duration)

    def process_queued_notifications(self):
        """
        Process all queued notifications by executing them in current context.
        This should be called from within a gradio event handler in main thread.
        """
        processed = []

        try:
            while not self._notification_queue.empty():
                notification = self._notification_queue.get_nowait()
                success = self._execute_gradio_notification(
                    notification['type'], notification['message'], notification['duration']
                )
                if success:
                    processed.append(notification)
                else:
                    # Execution failed, but still count as processed since we logged to console
                    processed.append(notification)

        except queue.Empty:
            pass

        return processed

    def get_pending_notifications(self):
        """Get and clear pending notifications (for debugging)."""
        notifications = self._pending_notifications.copy()
        self._pending_notifications.clear()
        return notifications


class ConsoleNotificationService(NotificationService):
    """Console notification service for non-UI environments."""

    def show_error(self, message: str, duration: int = 5) -> None:
        logger.error(f"[ERROR] {message}")

    def show_warning(self, message: str, duration: int = 3) -> None:
        logger.warning(f"[WARNING] {message}")

    def show_info(self, message: str, duration: int = 3) -> None:
        logger.info(f"[INFO] {message}")


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
