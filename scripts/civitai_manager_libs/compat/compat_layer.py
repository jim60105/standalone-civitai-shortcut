"""Main Compatibility Layer.

This module provides the main CompatibilityLayer class that unifies access
to all functionality across WebUI and standalone execution modes.
"""

from typing import Optional

from .environment_detector import EnvironmentDetector, EnvironmentType
from .interfaces import (
    IPathManager,
    IConfigManager,
    IMetadataProcessor,
    IUIBridge,
    ISamplerProvider,
    IParameterProcessor,
)


class CompatibilityLayer:
    """
    Main compatibility layer that provides unified access.

    to all functionality across WebUI and standalone modes.
    """

    _compat_layer: Optional["CompatibilityLayer"] = None

    def __init__(self, mode: Optional[EnvironmentType] = None):
        """
        Initialize the compatibility layer.

        Args:
            mode (Optional[EnvironmentType]): Force specific mode, auto-detect if None.
        """
        if mode is None:
            self.mode = EnvironmentDetector.detect_environment()
        else:
            self.mode = mode
            EnvironmentDetector.force_environment(mode)

        # Initialize all components
        self._path_manager = self._create_path_manager()
        self._config_manager = self._create_config_manager()
        self._metadata_processor = self._create_metadata_processor()
        self._ui_bridge = self._create_ui_bridge()
        self._sampler_provider = self._create_sampler_provider()
        self._parameter_processor = self._create_parameter_processor()

    @property
    def path_manager(self) -> IPathManager:
        """Get the path manager instance."""
        return self._path_manager

    @property
    def config_manager(self) -> IConfigManager:
        """Get the configuration manager instance."""
        return self._config_manager

    @property
    def metadata_processor(self) -> IMetadataProcessor:
        """Get the metadata processor instance."""
        return self._metadata_processor

    @property
    def ui_bridge(self) -> IUIBridge:
        """Get the UI bridge instance."""
        return self._ui_bridge

    @property
    def sampler_provider(self) -> ISamplerProvider:
        """Get the sampler provider instance."""
        return self._sampler_provider

    @property
    def parameter_processor(self) -> IParameterProcessor:
        """Get the parameter processor instance."""
        return self._parameter_processor

    def is_webui_mode(self) -> bool:
        """Check if running in WebUI mode."""
        return self.mode == "webui"

    def is_standalone_mode(self) -> bool:
        """Check if running in standalone mode."""
        return self.mode == "standalone"

    def _create_path_manager(self) -> IPathManager:
        """Create appropriate path manager for current mode."""
        if self.mode == "webui":
            from .webui_adapters.webui_path_manager import WebUIPathManager

            return WebUIPathManager()
        else:
            from .standalone_adapters.standalone_path_manager import (
                StandalonePathManager,
            )

            return StandalonePathManager()

    def _create_config_manager(self) -> IConfigManager:
        """Create appropriate config manager for current mode."""
        if self.mode == "webui":
            from .webui_adapters.webui_config_manager import WebUIConfigManager

            return WebUIConfigManager()
        else:
            from .standalone_adapters.standalone_config_manager import (
                StandaloneConfigManager,
            )

            return StandaloneConfigManager()

    def _create_metadata_processor(self) -> IMetadataProcessor:
        """Create appropriate metadata processor for current mode."""
        if self.mode == "webui":
            from .webui_adapters.webui_metadata_processor import WebUIMetadataProcessor

            return WebUIMetadataProcessor()
        else:
            from .standalone_adapters.standalone_metadata_processor import (
                StandaloneMetadataProcessor,
            )

            return StandaloneMetadataProcessor()

    def _create_ui_bridge(self) -> IUIBridge:
        """Create appropriate UI bridge for current mode."""
        if self.mode == "webui":
            from .webui_adapters.webui_ui_bridge import WebUIUIBridge

            return WebUIUIBridge()
        else:
            from .standalone_adapters.standalone_ui_bridge import StandaloneUIBridge

            return StandaloneUIBridge()

    def _create_sampler_provider(self) -> ISamplerProvider:
        """Create appropriate sampler provider for current mode."""
        if self.mode == "webui":
            from .webui_adapters.webui_sampler_provider import WebUISamplerProvider

            return WebUISamplerProvider()
        else:
            from .standalone_adapters.standalone_sampler_provider import (
                StandaloneSamplerProvider,
            )

            return StandaloneSamplerProvider()

    def _create_parameter_processor(self) -> IParameterProcessor:
        """Create appropriate parameter processor for current mode."""
        if self.mode == "webui":
            from .webui_adapters.webui_parameter_processor import (
                WebUIParameterProcessor,
            )

            return WebUIParameterProcessor()
        else:
            from .standalone_adapters.standalone_parameter_processor import (
                StandaloneParameterProcessor,
            )

            return StandaloneParameterProcessor()

    @staticmethod
    def get_compatibility_layer(
        mode: Optional[EnvironmentType] = None,
    ) -> "CompatibilityLayer":
        """
        Get the global compatibility layer instance.

        Args:
            mode (Optional[EnvironmentType]): Force specific mode, auto-detect if None

        Returns:
            CompatibilityLayer: The compatibility layer instance.
        """
        if CompatibilityLayer._compat_layer is None or (
            mode is not None and CompatibilityLayer._compat_layer.mode != mode
        ):
            CompatibilityLayer._compat_layer = CompatibilityLayer(mode)
        return CompatibilityLayer._compat_layer

    @staticmethod
    def reset_compatibility_layer() -> None:
        """Reset the global compatibility layer instance."""
        CompatibilityLayer._compat_layer = None
        EnvironmentDetector.reset_cache()
