"""
Test Compatibility Layer.

Unit tests for the main compatibility layer functionality.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock


# Add the scripts directory to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from civitai_manager_libs.compat.compat_layer import (  # noqa: E402
    CompatibilityLayer,
    get_compatibility_layer,
    reset_compatibility_layer,
)
from civitai_manager_libs.compat.environment_detector import (  # noqa: E402
    EnvironmentDetector,
)


class TestCompatibilityLayer(unittest.TestCase):
    """Test cases for CompatibilityLayer class."""

    def setUp(self):
        """Set up test fixtures."""
        reset_compatibility_layer()
        EnvironmentDetector.reset_cache()

    def tearDown(self):
        """Clean up after each test."""
        reset_compatibility_layer()
        EnvironmentDetector.reset_cache()

    def test_init_webui_mode(self):
        """Test initialization in WebUI mode."""
        with patch.object(EnvironmentDetector, 'detect_environment', return_value='webui'):
            compat = CompatibilityLayer()
            self.assertEqual(compat.mode, 'webui')
            self.assertTrue(compat.is_webui_mode())
            self.assertFalse(compat.is_standalone_mode())

    def test_init_standalone_mode(self):
        """Test initialization in standalone mode."""
        with patch.object(EnvironmentDetector, 'detect_environment', return_value='standalone'):
            compat = CompatibilityLayer()
            self.assertEqual(compat.mode, 'standalone')
            self.assertFalse(compat.is_webui_mode())
            self.assertTrue(compat.is_standalone_mode())

    def test_forced_mode(self):
        """Test forced mode initialization."""
        compat_webui = CompatibilityLayer(mode='webui')
        self.assertEqual(compat_webui.mode, 'webui')

        compat_standalone = CompatibilityLayer(mode='standalone')
        self.assertEqual(compat_standalone.mode, 'standalone')

    @patch('civitai_manager_libs.compat.compat_layer.CompatibilityLayer._create_path_manager')
    @patch('civitai_manager_libs.compat.compat_layer.CompatibilityLayer._create_config_manager')
    @patch('civitai_manager_libs.compat.compat_layer.CompatibilityLayer._create_metadata_processor')
    @patch('civitai_manager_libs.compat.compat_layer.CompatibilityLayer._create_ui_bridge')
    @patch('civitai_manager_libs.compat.compat_layer.CompatibilityLayer._create_sampler_provider')
    @patch(
        'civitai_manager_libs.compat.compat_layer.CompatibilityLayer._create_parameter_processor'
    )
    def test_component_creation(
        self, mock_param, mock_sampler, mock_ui, mock_meta, mock_config, mock_path
    ):
        """Test that all components are created during initialization."""
        # Mock all component creation methods
        mock_path.return_value = MagicMock()
        mock_config.return_value = MagicMock()
        mock_meta.return_value = MagicMock()
        mock_ui.return_value = MagicMock()
        mock_sampler.return_value = MagicMock()
        mock_param.return_value = MagicMock()

        CompatibilityLayer(mode='standalone')

        # Verify all creation methods were called
        mock_path.assert_called_once()
        mock_config.assert_called_once()
        mock_meta.assert_called_once()
        mock_ui.assert_called_once()
        mock_sampler.assert_called_once()
        mock_param.assert_called_once()

    def test_property_access(self):
        """Test property access methods."""
        with patch.object(CompatibilityLayer, '_create_path_manager') as mock_path, patch.object(
            CompatibilityLayer, '_create_config_manager'
        ) as mock_config, patch.object(
            CompatibilityLayer, '_create_metadata_processor'
        ) as mock_meta, patch.object(
            CompatibilityLayer, '_create_ui_bridge'
        ) as mock_ui, patch.object(
            CompatibilityLayer, '_create_sampler_provider'
        ) as mock_sampler, patch.object(
            CompatibilityLayer, '_create_parameter_processor'
        ) as mock_param:

            # Create mock objects
            mock_path_obj = MagicMock()
            mock_config_obj = MagicMock()
            mock_meta_obj = MagicMock()
            mock_ui_obj = MagicMock()
            mock_sampler_obj = MagicMock()
            mock_param_obj = MagicMock()

            mock_path.return_value = mock_path_obj
            mock_config.return_value = mock_config_obj
            mock_meta.return_value = mock_meta_obj
            mock_ui.return_value = mock_ui_obj
            mock_sampler.return_value = mock_sampler_obj
            mock_param.return_value = mock_param_obj

            compat = CompatibilityLayer(mode='standalone')

            # Test property access
            self.assertEqual(compat.path_manager, mock_path_obj)
            self.assertEqual(compat.config_manager, mock_config_obj)
            self.assertEqual(compat.metadata_processor, mock_meta_obj)
            self.assertEqual(compat.ui_bridge, mock_ui_obj)
            self.assertEqual(compat.sampler_provider, mock_sampler_obj)
            self.assertEqual(compat.parameter_processor, mock_param_obj)

    def test_get_compatibility_layer_singleton(self):
        """Test singleton behavior of get_compatibility_layer."""
        with patch.object(EnvironmentDetector, 'detect_environment', return_value='standalone'):
            compat1 = get_compatibility_layer()
            compat2 = get_compatibility_layer()

            # Should be the same instance
            self.assertIs(compat1, compat2)

    def test_get_compatibility_layer_mode_change(self):
        """Test that specifying different mode creates new instance."""
        with patch.object(EnvironmentDetector, 'detect_environment', return_value='standalone'):
            compat1 = get_compatibility_layer()
            compat2 = get_compatibility_layer(mode='webui')

            # Should be different instances
            self.assertIsNot(compat1, compat2)
            self.assertEqual(compat1.mode, 'standalone')
            self.assertEqual(compat2.mode, 'webui')

    def test_reset_compatibility_layer(self):
        """Test reset functionality."""
        with patch.object(EnvironmentDetector, 'detect_environment', return_value='standalone'):
            compat1 = get_compatibility_layer()
            reset_compatibility_layer()
            compat2 = get_compatibility_layer()

            # Should be different instances after reset
            self.assertIsNot(compat1, compat2)


class TestCompatibilityLayerComponentCreation(unittest.TestCase):
    """Test component creation methods in isolation."""

    def setUp(self):
        """Set up test fixtures."""
        reset_compatibility_layer()
        EnvironmentDetector.reset_cache()

    def tearDown(self):
        """Clean up after each test."""
        reset_compatibility_layer()
        EnvironmentDetector.reset_cache()

    def test_create_webui_components(self):
        """Test creation of WebUI components."""
        with patch(
            'civitai_manager_libs.compat.webui_adapters.webui_path_manager.' 'WebUIPathManager'
        ) as mock_path, patch(
            'civitai_manager_libs.compat.webui_adapters.webui_config_manager.' 'WebUIConfigManager'
        ) as mock_config:
            CompatibilityLayer(mode='webui')
            # Verify WebUI adapters are imported and instantiated
            mock_path.assert_called_once()
            mock_config.assert_called_once()
            # Note: This test verifies the import attempt, actual instantiation
            # depends on the mocked modules being available

    def test_create_standalone_components(self):
        """Test creation of standalone components."""
        with patch(
            'civitai_manager_libs.compat.standalone_adapters.standalone_path_manager.'
            'StandalonePathManager'
        ) as mock_path, patch(
            'civitai_manager_libs.compat.standalone_adapters.standalone_config_manager.'
            'StandaloneConfigManager'
        ) as mock_config:
            CompatibilityLayer(mode='standalone')
            # Verify standalone adapters are imported and instantiated
            mock_path.assert_called_once()
            mock_config.assert_called_once()
            # Note: This test verifies the import attempt


if __name__ == '__main__':
    unittest.main()
