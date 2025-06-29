"""
UI Controllers Module

Manages UI state, component interactions, and interface control logic.
Handles UI updates, state synchronization, and component coordination.
"""

from typing import Any, Dict, List, Optional
from ..logging_config import get_logger
from ..error_handler import with_error_handling

logger = get_logger(__name__)


class UIControllers:
    """
    Manages UI state and component interactions.
    Controls interface updates, state management, and component coordination.
    """

    def __init__(self):
        """Initialize UI controllers."""
        self._ui_state = {}
        self._component_registry = {}
        self._update_callbacks = {}

    @with_error_handling("Failed to update UI state")
    def update_ui_state(self, key: str, value: Any, notify: bool = True) -> bool:
        """
        Update UI state.

        Args:
            key: State key
            value: New value
            notify: Whether to notify callbacks

        Returns:
            bool: True if successful, False otherwise
        """
        old_value = self._ui_state.get(key)
        self._ui_state[key] = value

        logger.debug(f"Updated UI state: {key} = {value}")

        if notify and key in self._update_callbacks:
            for callback in self._update_callbacks[key]:
                try:
                    callback(key, value, old_value)
                except Exception as e:
                    logger.error(f"Error in UI state callback for {key}: {e}")

        return True

    def get_ui_state(self, key: str, default: Any = None) -> Any:
        """
        Get UI state value.

        Args:
            key: State key
            default: Default value if not found

        Returns:
            Any: State value or default
        """
        return self._ui_state.get(key, default)

    def get_all_ui_state(self) -> Dict[str, Any]:
        """
        Get all UI state.

        Returns:
            Dict[str, Any]: Complete UI state
        """
        return self._ui_state.copy()

    @with_error_handling("Failed to register UI component")
    def register_component(self, component_id: str, component: Any) -> bool:
        """
        Register UI component.

        Args:
            component_id: Unique component identifier
            component: Component object

        Returns:
            bool: True if successful, False otherwise
        """
        self._component_registry[component_id] = component
        logger.debug(f"Registered UI component: {component_id}")
        return True

    def get_component(self, component_id: str) -> Optional[Any]:
        """
        Get registered component.

        Args:
            component_id: Component identifier

        Returns:
            Optional[Any]: Component object or None
        """
        return self._component_registry.get(component_id)

    def remove_component(self, component_id: str) -> bool:
        """
        Remove component from registry.

        Args:
            component_id: Component identifier

        Returns:
            bool: True if removed, False if not found
        """
        if component_id in self._component_registry:
            del self._component_registry[component_id]
            logger.debug(f"Removed UI component: {component_id}")
            return True
        return False

    @with_error_handling("Failed to register state callback")
    def register_state_callback(self, key: str, callback: callable) -> bool:
        """
        Register callback for state changes.

        Args:
            key: State key to monitor
            callback: Function to call on change

        Returns:
            bool: True if successful, False otherwise
        """
        if key not in self._update_callbacks:
            self._update_callbacks[key] = []

        self._update_callbacks[key].append(callback)
        logger.debug(f"Registered state callback for: {key}")
        return True

    @with_error_handling("Failed to update component visibility")
    def update_component_visibility(self, component_id: str, visible: bool) -> bool:
        """
        Update component visibility.

        Args:
            component_id: Component identifier
            visible: Whether component should be visible

        Returns:
            bool: True if successful, False otherwise
        """
        component = self.get_component(component_id)
        if component is None:
            logger.warning(f"Component not found: {component_id}")
            return False

        try:
            if hasattr(component, 'visible'):
                component.visible = visible
            elif hasattr(component, 'update'):
                component.update(visible=visible)
            else:
                logger.warning(f"Cannot update visibility for component: {component_id}")
                return False

            logger.debug(f"Updated {component_id} visibility to {visible}")
            return True
        except Exception as e:
            logger.error(f"Failed to update component visibility: {e}")
            return False

    @with_error_handling("Failed to update component value")
    def update_component_value(self, component_id: str, value: Any) -> bool:
        """
        Update component value.

        Args:
            component_id: Component identifier
            value: New value

        Returns:
            bool: True if successful, False otherwise
        """
        component = self.get_component(component_id)
        if component is None:
            logger.warning(f"Component not found: {component_id}")
            return False

        try:
            if hasattr(component, 'value'):
                component.value = value
            elif hasattr(component, 'update'):
                component.update(value=value)
            else:
                logger.warning(f"Cannot update value for component: {component_id}")
                return False

            logger.debug(f"Updated {component_id} value to {value}")
            return True
        except Exception as e:
            logger.error(f"Failed to update component value: {e}")
            return False

    def reset_ui_state(self) -> None:
        """Reset all UI state to defaults."""
        self._ui_state.clear()
        logger.info("UI state reset")

    def get_component_ids(self) -> List[str]:
        """
        Get all registered component IDs.

        Returns:
            List[str]: List of component IDs
        """
        return list(self._component_registry.keys())


class TabController:
    """Controls tab interface and navigation."""

    def __init__(self, ui_controllers: UIControllers):
        """
        Initialize tab controller.

        Args:
            ui_controllers: UI controllers instance
        """
        self.ui_controllers = ui_controllers
        self._active_tab = None
        self._tab_history = []
        self._max_history = 10

    @with_error_handling("Failed to switch tab")
    def switch_tab(self, tab_id: str) -> bool:
        """
        Switch to specified tab.

        Args:
            tab_id: Tab identifier

        Returns:
            bool: True if successful, False otherwise
        """
        if self._active_tab == tab_id:
            return True

        old_tab = self._active_tab
        self._active_tab = tab_id

        # Add to history
        if old_tab is not None:
            self._tab_history.append(old_tab)
            if len(self._tab_history) > self._max_history:
                self._tab_history = self._tab_history[-self._max_history :]

        # Update UI state
        self.ui_controllers.update_ui_state('active_tab', tab_id)

        logger.debug(f"Switched tab from {old_tab} to {tab_id}")
        return True

    def get_active_tab(self) -> Optional[str]:
        """
        Get currently active tab.

        Returns:
            Optional[str]: Active tab ID or None
        """
        return self._active_tab

    def go_back(self) -> bool:
        """
        Go back to previous tab.

        Returns:
            bool: True if successful, False if no history
        """
        if not self._tab_history:
            return False

        previous_tab = self._tab_history.pop()
        return self.switch_tab(previous_tab)

    def get_tab_history(self) -> List[str]:
        """
        Get tab navigation history.

        Returns:
            List[str]: Tab history
        """
        return self._tab_history.copy()


class ComponentValidator:
    """Validates UI component operations."""

    @staticmethod
    def validate_component_id(component_id: str) -> bool:
        """
        Validate component ID format.

        Args:
            component_id: Component ID to validate

        Returns:
            bool: True if valid, False otherwise
        """
        return bool(
            component_id and isinstance(component_id, str) and len(component_id.strip()) > 0
        )

    @staticmethod
    def validate_component(component: Any) -> bool:
        """
        Validate component object.

        Args:
            component: Component to validate

        Returns:
            bool: True if valid, False otherwise
        """
        return component is not None

    @staticmethod
    def validate_state_key(key: str) -> bool:
        """
        Validate state key format.

        Args:
            key: State key to validate

        Returns:
            bool: True if valid, False otherwise
        """
        return bool(key and isinstance(key, str) and len(key.strip()) > 0)


class UIStateManager:
    """Advanced UI state management utilities."""

    def __init__(self, ui_controllers: UIControllers):
        """
        Initialize state manager.

        Args:
            ui_controllers: UI controllers instance
        """
        self.ui_controllers = ui_controllers
        self._state_snapshots = {}

    def create_snapshot(self, snapshot_name: str) -> bool:
        """
        Create snapshot of current UI state.

        Args:
            snapshot_name: Name for the snapshot

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            current_state = self.ui_controllers.get_all_ui_state()
            self._state_snapshots[snapshot_name] = current_state.copy()
            logger.info(f"Created UI state snapshot: {snapshot_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create snapshot: {e}")
            return False

    def restore_snapshot(self, snapshot_name: str) -> bool:
        """
        Restore UI state from snapshot.

        Args:
            snapshot_name: Name of snapshot to restore

        Returns:
            bool: True if successful, False otherwise
        """
        if snapshot_name not in self._state_snapshots:
            logger.warning(f"Snapshot not found: {snapshot_name}")
            return False

        try:
            snapshot_state = self._state_snapshots[snapshot_name]
            for key, value in snapshot_state.items():
                self.ui_controllers.update_ui_state(key, value, notify=False)
            logger.info(f"Restored UI state from snapshot: {snapshot_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore snapshot: {e}")
            return False

    def get_snapshots(self) -> List[str]:
        """
        Get list of available snapshots.

        Returns:
            List[str]: Snapshot names
        """
        return list(self._state_snapshots.keys())

    def delete_snapshot(self, snapshot_name: str) -> bool:
        """
        Delete a snapshot.

        Args:
            snapshot_name: Name of snapshot to delete

        Returns:
            bool: True if deleted, False if not found
        """
        if snapshot_name in self._state_snapshots:
            del self._state_snapshots[snapshot_name]
            logger.info(f"Deleted snapshot: {snapshot_name}")
            return True
        return False
