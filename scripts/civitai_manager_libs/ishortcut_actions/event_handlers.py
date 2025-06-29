"""
Event Handlers Module

Core event handling logic and utilities for UI interactions.
Handles general event processing, validation, and coordination.
"""

from typing import Any, Callable, Dict, List, Optional
from ..logging_config import get_logger
from ..error_handler import with_error_handling

logger = get_logger(__name__)


class EventHandlers:
    """
    Core event handling system for UI interactions.
    Manages event registration, processing, and coordination.
    """

    def __init__(self):
        """Initialize event handlers."""
        self._event_listeners = {}
        self._event_history = []
        self._max_history_size = 100

    @with_error_handling("Failed to register event listener")
    def register_event_listener(
        self, event_name: str, callback: Callable, priority: int = 0
    ) -> bool:
        """
        Register an event listener.

        Args:
            event_name: Name of the event to listen for
            callback: Function to call when event occurs
            priority: Priority level (higher = earlier execution)

        Returns:
            bool: True if successful, False otherwise
        """
        if event_name not in self._event_listeners:
            self._event_listeners[event_name] = []

        listener_info = {'callback': callback, 'priority': priority, 'id': id(callback)}

        self._event_listeners[event_name].append(listener_info)
        self._event_listeners[event_name].sort(key=lambda x: x['priority'], reverse=True)

        logger.debug(f"Registered event listener for '{event_name}' with priority {priority}")
        return True

    @with_error_handling("Failed to emit event")
    def emit_event(self, event_name: str, *args, **kwargs) -> List[Any]:
        """
        Emit an event to all registered listeners.

        Args:
            event_name: Name of the event to emit
            *args: Positional arguments for event handlers
            **kwargs: Keyword arguments for event handlers

        Returns:
            List[Any]: Results from all event handlers
        """
        results = []

        # Add to event history
        self._add_to_history(event_name, args, kwargs)

        if event_name not in self._event_listeners:
            logger.debug(f"No listeners registered for event '{event_name}'")
            return results

        logger.debug(
            f"Emitting event '{event_name}' to {len(self._event_listeners[event_name])} listeners"
        )

        for listener_info in self._event_listeners[event_name]:
            try:
                callback = listener_info['callback']
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Error in event listener for '{event_name}': {e}")
                results.append(None)

        return results

    def remove_event_listener(self, event_name: str, callback: Callable) -> bool:
        """
        Remove an event listener.

        Args:
            event_name: Name of the event
            callback: Callback function to remove

        Returns:
            bool: True if removed, False if not found
        """
        if event_name not in self._event_listeners:
            return False

        callback_id = id(callback)
        original_count = len(self._event_listeners[event_name])

        self._event_listeners[event_name] = [
            listener
            for listener in self._event_listeners[event_name]
            if listener['id'] != callback_id
        ]

        removed = len(self._event_listeners[event_name]) < original_count
        if removed:
            logger.debug(f"Removed event listener for '{event_name}'")

        return removed

    def get_event_listeners(self, event_name: str) -> List[Dict[str, Any]]:
        """
        Get all listeners for an event.

        Args:
            event_name: Name of the event

        Returns:
            List[Dict[str, Any]]: List of listener info
        """
        return self._event_listeners.get(event_name, []).copy()

    def clear_event_listeners(self, event_name: Optional[str] = None) -> None:
        """
        Clear event listeners.

        Args:
            event_name: Specific event name to clear, or None for all
        """
        if event_name is None:
            self._event_listeners.clear()
            logger.info("Cleared all event listeners")
        elif event_name in self._event_listeners:
            del self._event_listeners[event_name]
            logger.info(f"Cleared event listeners for '{event_name}'")

    def get_event_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get event history.

        Args:
            limit: Maximum number of events to return

        Returns:
            List[Dict[str, Any]]: Event history
        """
        history = self._event_history.copy()
        if limit is not None:
            history = history[-limit:]
        return history

    def _add_to_history(self, event_name: str, args: tuple, kwargs: dict) -> None:
        """
        Add event to history.

        Args:
            event_name: Name of the event
            args: Event arguments
            kwargs: Event keyword arguments
        """
        import time

        event_record = {
            'name': event_name,
            'timestamp': time.time(),
            'args': args,
            'kwargs': kwargs,
        }

        self._event_history.append(event_record)

        # Maintain history size limit
        if len(self._event_history) > self._max_history_size:
            self._event_history = self._event_history[-self._max_history_size :]


class EventValidator:
    """Validates event data and parameters."""

    @staticmethod
    def validate_event_name(event_name: str) -> bool:
        """
        Validate event name format.

        Args:
            event_name: Event name to validate

        Returns:
            bool: True if valid, False otherwise
        """
        return bool(event_name and isinstance(event_name, str) and len(event_name.strip()) > 0)

    @staticmethod
    def validate_callback(callback: Any) -> bool:
        """
        Validate callback function.

        Args:
            callback: Callback to validate

        Returns:
            bool: True if valid, False otherwise
        """
        return callable(callback)

    @staticmethod
    def validate_priority(priority: Any) -> bool:
        """
        Validate priority value.

        Args:
            priority: Priority to validate

        Returns:
            bool: True if valid, False otherwise
        """
        return isinstance(priority, int)


class EventFilters:
    """Provides event filtering capabilities."""

    @staticmethod
    def filter_by_name_pattern(events: List[Dict[str, Any]], pattern: str) -> List[Dict[str, Any]]:
        """
        Filter events by name pattern.

        Args:
            events: List of events
            pattern: Pattern to match

        Returns:
            List[Dict[str, Any]]: Filtered events
        """
        import re

        try:
            regex = re.compile(pattern, re.IGNORECASE)
            return [event for event in events if regex.search(event.get('name', ''))]
        except re.error:
            logger.warning(f"Invalid regex pattern: {pattern}")
            return []

    @staticmethod
    def filter_by_time_range(
        events: List[Dict[str, Any]],
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Filter events by time range.

        Args:
            events: List of events
            start_time: Start timestamp
            end_time: End timestamp

        Returns:
            List[Dict[str, Any]]: Filtered events
        """
        filtered_events = []
        for event in events:
            timestamp = event.get('timestamp', 0)

            if start_time is not None and timestamp < start_time:
                continue
            if end_time is not None and timestamp > end_time:
                continue

            filtered_events.append(event)

        return filtered_events

    @staticmethod
    def get_recent_events(events: List[Dict[str, Any]], seconds: float) -> List[Dict[str, Any]]:
        """
        Get events from the last N seconds.

        Args:
            events: List of events
            seconds: Number of seconds to look back

        Returns:
            List[Dict[str, Any]]: Recent events
        """
        import time

        cutoff_time = time.time() - seconds
        return EventFilters.filter_by_time_range(events, start_time=cutoff_time)


class EventMetrics:
    """Provides event metrics and analytics."""

    @staticmethod
    def get_event_counts(events: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get count of each event type.

        Args:
            events: List of events

        Returns:
            Dict[str, int]: Event counts by name
        """
        counts = {}
        for event in events:
            name = event.get('name', 'unknown')
            counts[name] = counts.get(name, 0) + 1
        return counts

    @staticmethod
    def get_event_frequency(events: List[Dict[str, Any]], time_window: float) -> Dict[str, float]:
        """
        Get event frequency (events per second).

        Args:
            events: List of events
            time_window: Time window in seconds

        Returns:
            Dict[str, float]: Event frequencies
        """
        if not events or time_window <= 0:
            return {}

        counts = EventMetrics.get_event_counts(events)
        return {name: count / time_window for name, count in counts.items()}

    @staticmethod
    def get_peak_activity_time(events: List[Dict[str, Any]]) -> Optional[float]:
        """
        Get timestamp of peak activity.

        Args:
            events: List of events

        Returns:
            Optional[float]: Timestamp of peak activity
        """
        if not events:
            return None

        # Group events by minute
        minute_counts = {}
        for event in events:
            timestamp = event.get('timestamp', 0)
            minute = int(timestamp // 60)
            minute_counts[minute] = minute_counts.get(minute, 0) + 1

        if not minute_counts:
            return None

        peak_minute = max(minute_counts, key=minute_counts.get)
        return float(peak_minute * 60)
