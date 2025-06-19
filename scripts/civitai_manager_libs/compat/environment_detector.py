"""Environment Detection for Civitai Shortcut.

Provides automatic detection of execution environment (WebUI vs Standalone).
"""

import os
import sys
from typing import Literal, Optional


EnvironmentType = Literal["webui", "standalone"]


class EnvironmentDetector:
    """Detects and manages execution environment information."""

    _cached_environment: Optional[EnvironmentType] = None

    @classmethod
    def detect_environment(cls) -> EnvironmentType:
        """
        Detect the current execution environment.

        Returns:
            EnvironmentType: 'webui' if running in AUTOMATIC1111 environment,
                           'standalone' if running independently.
        """
        if cls._cached_environment is not None:
            return cls._cached_environment

        # Try to detect AUTOMATIC1111 WebUI environment
        try:
            # Check if modules package exists and can be imported
            import modules.scripts
            import modules.shared

            # Try to access specific WebUI functionality
            try:
                # This should work in a proper WebUI environment
                base_dir = modules.scripts.basedir()
                if base_dir and os.path.exists(base_dir):
                    cls._cached_environment = "webui"
                    return "webui"
            except (AttributeError, TypeError):
                # modules exist but don't work as expected
                pass

        except ImportError:
            # modules package not available
            pass

        # Check for specific WebUI environment markers
        if cls._check_webui_markers():
            cls._cached_environment = "webui"
            return "webui"

        # Default to standalone mode
        cls._cached_environment = "standalone"
        return "standalone"

    @classmethod
    def _check_webui_markers(cls) -> bool:
        """
        Check for specific markers that indicate WebUI environment.

        Returns:
            bool: True if WebUI markers are found.
        """
        # Check for webui.py in the current working directory or parent directories
        current_dir = os.getcwd()
        for _ in range(3):  # Check up to 3 levels up
            webui_file = os.path.join(current_dir, "webui.py")
            launch_file = os.path.join(current_dir, "launch.py")

            if os.path.exists(webui_file) or os.path.exists(launch_file):
                return True

            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:  # Reached root
                break
            current_dir = parent_dir

        # Check for extensions directory structure
        extensions_dir = os.path.join(os.getcwd(), "extensions")
        if os.path.exists(extensions_dir) and os.path.isdir(extensions_dir):
            return True

        # Check environment variables
        if os.environ.get("WEBUI_MODE") == "1":
            return True

        return False

    @classmethod
    def is_webui_mode(cls) -> bool:
        """
        Check if currently running in WebUI mode.

        Returns:
            bool: True if in WebUI mode.
        """
        return cls.detect_environment() == "webui"

    @classmethod
    def is_standalone_mode(cls) -> bool:
        """
        Check if currently running in standalone mode.

        Returns:
            bool: True if in standalone mode.
        """
        return cls.detect_environment() == "standalone"

    @classmethod
    def force_environment(cls, env_type: EnvironmentType) -> None:
        """
        Force a specific environment type (mainly for testing).

        Args:
            env_type (EnvironmentType): The environment type to force.
        """
        cls._cached_environment = env_type

    @classmethod
    def reset_cache(cls) -> None:
        """Reset the cached environment detection result."""
        cls._cached_environment = None

    @classmethod
    def get_environment_info(cls) -> dict:
        """
        Get detailed environment information for debugging.

        Returns:
            dict: Environment information including detection details.
        """
        env_type = cls.detect_environment()

        info = {
            "environment": env_type,
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "python_path": sys.path,
        }

        # Add WebUI-specific information if available
        if env_type == "webui":
            try:
                import modules.scripts

                info["webui_base_dir"] = modules.scripts.basedir()
            except (ImportError, AttributeError):
                info["webui_base_dir"] = "Not available"

            try:
                import modules.shared

                info["webui_cmd_opts"] = str(getattr(modules.shared, "cmd_opts", "Not available"))
            except (ImportError, AttributeError):
                info["webui_cmd_opts"] = "Not available"

        return info
