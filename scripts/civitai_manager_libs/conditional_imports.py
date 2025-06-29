"""
Conditional Import Manager

This module provides conditional import management to handle optional dependencies
on AUTOMATIC1111 WebUI modules while maintaining compatibility with standalone mode.
"""

from typing import Any, Optional, Dict, Callable
import importlib


class ConditionalImportManager:
    """Conditional import management for WebUI modules."""

    def __init__(self):
        self._webui_available = None
        self._module_cache: Dict[str, Any] = {}

    def is_webui_available(self) -> bool:
        """Check if WebUI modules are available."""
        # Determine availability by attempting to import via importlib to allow mocking
        if self._webui_available is None:
            try:
                importlib.import_module('modules.scripts')
                self._webui_available = True
            except ImportError:
                self._webui_available = False
        return self._webui_available

    def try_import(self, module_name: str, fallback: Any = None) -> Any:
        """
        Try to import a module with fallback.

        Args:
            module_name (str): Full module name to import
            fallback (Any): Fallback value if import fails

        Returns:
            Any: Imported module or fallback value
        """
        # If no fallback provided and cached, return cached module
        if module_name in self._module_cache and fallback is None:
            return self._module_cache[module_name]

        try:
            module = importlib.import_module(module_name)
            self._module_cache[module_name] = module
            return module
        except ImportError:
            self._module_cache[module_name] = fallback
            return fallback

    def get_webui_module(self, module_name: str, attr_name: Optional[str] = None) -> Any:
        """
        Get WebUI module or attribute safely.

        Args:
            module_name (str): WebUI module name (without 'modules.' prefix)
            attr_name (Optional[str]): Specific attribute name to get

        Returns:
            Any: Module, attribute, or None if not available
        """
        if not self.is_webui_available():
            return None

        module = self.try_import(f'modules.{module_name}')
        if module and attr_name:
            return getattr(module, attr_name, None)
        return module

    def get_webui_function(
        self, module_name: str, function_name: str, fallback_fn: Optional[Callable] = None
    ) -> Callable:
        """
        Get WebUI function with fallback.

        Args:
            module_name (str): WebUI module name
            function_name (str): Function name
            fallback_fn (callable): Fallback function

        Returns:
            callable: WebUI function or fallback function
        """
        module = self.get_webui_module(module_name)
        if module:
            func = getattr(module, function_name, None)
            if func and callable(func):
                return func

        return fallback_fn if fallback_fn else lambda *args, **kwargs: None

    def has_webui_module(self, module_name: str) -> bool:
        """Check if WebUI module is available."""
        return self.get_webui_module(module_name) is not None

    def clear_cache(self):
        """Clear the module cache."""
        self._module_cache.clear()
        self._webui_available = None


# Global instance
import_manager = ConditionalImportManager()
