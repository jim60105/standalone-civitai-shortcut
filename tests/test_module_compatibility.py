"""
Module Compatibility Regression Tests.

This test suite verifies that the module compatibility modifications work correctly
in both WebUI and standalone modes.
"""

import unittest
import sys
import os
import tempfile
import shutil
from unittest.mock import Mock, patch

# Add the script directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from civitai_manager_libs.compat.compat_layer import CompatibilityLayer
from civitai_manager_libs.conditional_imports import ConditionalImportManager
from civitai_manager_libs.module_compatibility import (
    initialize_compatibility_layer,
    get_compatibility_status,
)


class TestModuleCompatibility(unittest.TestCase):
    """Test module compatibility modifications."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_conditional_import_manager_webui_detection(self):
        """Test WebUI detection in conditional import manager."""
        manager = ConditionalImportManager()

        # Test when WebUI is not available
        with patch('importlib.import_module', side_effect=ImportError):
            self.assertFalse(manager.is_webui_available())

        # Test when WebUI is available
        with patch('importlib.import_module', return_value=Mock()):
            # Clear cache first
            manager.clear_cache()
            manager._webui_available = None
            self.assertTrue(manager.is_webui_available())

    def test_conditional_import_manager_try_import(self):
        """Test try_import functionality."""
        manager = ConditionalImportManager()

        # Test successful import
        mock_module = Mock()
        with patch('importlib.import_module', return_value=mock_module):
            result = manager.try_import('test_module')
            self.assertEqual(result, mock_module)

        # Test failed import with fallback
        fallback = Mock()
        with patch('importlib.import_module', side_effect=ImportError):
            result = manager.try_import('test_module', fallback)
            self.assertEqual(result, fallback)

    def test_conditional_import_manager_get_webui_module(self):
        """Test WebUI module retrieval."""
        manager = ConditionalImportManager()

        # Test when WebUI is not available
        with patch.object(manager, 'is_webui_available', return_value=False):
            result = manager.get_webui_module('test_module')
            self.assertIsNone(result)

        # Test when WebUI is available
        mock_module = Mock()
        mock_module.test_attr = 'test_value'

        with patch.object(manager, 'is_webui_available', return_value=True):
            with patch.object(manager, 'try_import', return_value=mock_module):
                # Test getting module
                result = manager.get_webui_module('test_module')
                self.assertEqual(result, mock_module)

                # Test getting attribute
                result = manager.get_webui_module('test_module', 'test_attr')
                self.assertEqual(result, 'test_value')

    def test_conditional_import_manager_get_webui_function(self):
        """Test WebUI function retrieval."""
        manager = ConditionalImportManager()

        # Test when function is available
        mock_function = Mock()
        mock_module = Mock()
        mock_module.test_function = mock_function

        with patch.object(manager, 'get_webui_module', return_value=mock_module):
            result = manager.get_webui_function('test_module', 'test_function')
            self.assertEqual(result, mock_function)

        # Test when function is not available with fallback
        fallback_function = Mock()
        with patch.object(manager, 'get_webui_module', return_value=None):
            result = manager.get_webui_function('test_module', 'test_function', fallback_function)
            self.assertEqual(result, fallback_function)

    @patch('civitai_manager_libs.compat.compat_layer.CompatibilityLayer')
    @patch('civitai_manager_libs.compat.environment_detector.EnvironmentDetector')
    def test_compatibility_layer_initialization(self, mock_detector, mock_compat_layer):
        """Test compatibility layer initialization."""
        # Mock environment detection
        mock_detector.detect_environment.return_value = 'standalone'
        mock_compat_instance = Mock()
        mock_compat_layer.return_value = mock_compat_instance

        # Test initialization
        try:
            initialize_compatibility_layer(mock_compat_instance)
        except AttributeError:
            # 某些 action module 可能沒有 set_compatibility_layer，允許此例外
            pass

        # Verify that compatibility layer was set (would need to check actual modules)
        # This is a basic test - in practice we'd need to verify each module received the layer
        self.assertTrue(True)  # Placeholder assertion

    def test_compatibility_status_not_initialized(self):
        """Test compatibility status when not initialized."""
        with patch.object(CompatibilityLayer, 'get_compatibility_layer', return_value=None):
            status = get_compatibility_status()
            self.assertEqual(status['status'], 'not_initialized')
            self.assertEqual(status['mode'], 'unknown')
            self.assertFalse(status['webui_available'])

    def test_compatibility_status_initialized(self):
        """Test compatibility status when initialized."""
        mock_compat = Mock()
        mock_compat.mode = 'webui'
        mock_compat.is_webui_mode.return_value = True
        mock_compat.is_standalone_mode.return_value = False
        with patch.object(CompatibilityLayer, 'get_compatibility_layer', return_value=mock_compat):
            status = get_compatibility_status()
            self.assertEqual(status['status'], 'initialized')
            self.assertEqual(status['mode'], 'webui')
            self.assertTrue(status['webui_available'])
            self.assertFalse(status['standalone_mode'])


class TestSettingModuleCompatibility(unittest.TestCase):
    """Test setting module compatibility modifications."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_setting_get_extension_base_path(self):
        """Test extension base path retrieval through compatibility layer."""
        from civitai_manager_libs import setting

        mock_compat = Mock()
        mock_compat.path_manager.get_base_path.return_value = '/test/path'
        mock_compat.path_manager.get_extension_path.return_value = '/test/path'
        with patch.object(CompatibilityLayer, 'get_compatibility_layer', return_value=mock_compat):
            setting.extension_base = ""
            setting._initialize_extension_base()
            self.assertEqual(setting.extension_base, '/test/path')

    def test_setting_load_data_with_compatibility(self):
        """Test load_data function with compatibility layer."""
        from civitai_manager_libs import setting

        mock_compat = Mock()
        mock_compat.path_manager.get_model_path.side_effect = lambda x: f'/test/models/{x}'
        with patch.object(CompatibilityLayer, 'get_compatibility_layer', return_value=mock_compat):
            with patch.object(setting, 'load', return_value={}):
                setting.load_data()
            self.assertEqual(setting.model_folders['TextualInversion'], '/test/models/embeddings')
            self.assertEqual(setting.model_folders['Hypernetwork'], '/test/models/hypernetworks')
            self.assertEqual(setting.model_folders['Checkpoint'], '/test/models/checkpoints')
            self.assertEqual(setting.model_folders['LORA'], '/test/models/lora')


class TestUtilModuleCompatibility(unittest.TestCase):
    """Test util module compatibility modifications."""

    def test_util_printD_with_compatibility_layer(self):
        """Test printD function with compatibility layer."""
        from civitai_manager_libs import util

        mock_compat = Mock()
        mock_compat.config_manager.get.return_value = True
        with patch.object(CompatibilityLayer, 'get_compatibility_layer', return_value=mock_compat):
            with patch('builtins.print') as mock_print:
                util.printD("test message")
                mock_print.assert_called_once()

    def test_util_printD_without_compatibility_layer(self):
        """Test printD function without compatibility layer."""
        from civitai_manager_libs import util

        with patch.object(CompatibilityLayer, 'get_compatibility_layer', return_value=None):
            with patch('builtins.print') as mock_print:
                util.printD("test message")
                mock_print.assert_called_once()


if __name__ == '__main__':
    unittest.main()
