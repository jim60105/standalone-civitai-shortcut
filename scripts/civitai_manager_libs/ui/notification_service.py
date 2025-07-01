from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import threading
import queue
import time


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

        # Gradio variables that will be used to trigger notifications in main thread
        self._error_trigger = None
        self._info_trigger = None
        self._warning_trigger = None

    def _is_main_thread(self) -> bool:
        """Check if we're currently in the main thread."""
        return threading.current_thread() is self._main_thread

    def set_gradio_triggers(self, error_trigger=None, info_trigger=None, warning_trigger=None):
        """Set Gradio state variables that can trigger notifications from main thread."""
        self._error_trigger = error_trigger
        self._info_trigger = info_trigger
        self._warning_trigger = warning_trigger

    def _execute_gradio_notification(self, notification_type: str, message: str, duration: int):
        """Execute the actual Gradio notification."""
        import gradio as gr

        if notification_type == "error":
            gr.Error(message, duration=duration)
        elif notification_type == "warning":
            gr.Warning(message, duration=duration)
        elif notification_type == "info":
            gr.Info(message, duration=duration)

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

        # Try to trigger via gradio state if available
        self._trigger_via_gradio_state(notification)

    def _trigger_via_gradio_state(self, notification: Dict[str, Any]):
        """Attempt to trigger notification via gradio state variables."""
        try:
            trigger_map = {
                'error': self._error_trigger,
                'info': self._info_trigger,
                'warning': self._warning_trigger,
            }

            trigger = trigger_map.get(notification['type'])
            if trigger is not None:
                # Update the trigger state to cause a UI update
                trigger.value = f"{notification['message']}|{notification['timestamp']}"
                return True
        except Exception:
            pass
        return False

    def _execute_notification(self, notification_type: str, message: str, duration: int):
        """Execute a notification, handling thread context appropriately."""
        if self._is_main_thread():
            # We're in the main thread, execute directly
            try:
                self._execute_gradio_notification(notification_type, message, duration)
            except Exception:
                # If direct execution fails, fall back to console
                print(f"[{notification_type.upper()}] {message}")
        else:
            # We're in a background thread, queue for later execution
            self._queue_notification(notification_type, message, duration)

            # Also print to console immediately for visibility
            print(f"[{notification_type.upper()} - QUEUED] {message}")

    def show_error(self, message: str, duration: int = 5) -> None:
        self._execute_notification("error", message, duration)

    def show_warning(self, message: str, duration: int = 3) -> None:
        self._execute_notification("warning", message, duration)

    def show_info(self, message: str, duration: int = 3) -> None:
        self._execute_notification("info", message, duration)

    def process_queued_notifications(self):
        """Process all queued notifications (should be called from main thread)."""
        processed = []

        try:
            while not self._notification_queue.empty():
                notification = self._notification_queue.get_nowait()
                try:
                    self._execute_gradio_notification(
                        notification['type'], notification['message'], notification['duration']
                    )
                    processed.append(notification)
                except Exception as e:
                    print(f"[ERROR] Failed to process queued notification: {e}")
                    print(f"[{notification['type'].upper()}] {notification['message']}")
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
