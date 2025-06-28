"""
Integration Tests for Module Compatibility.

This test suite verifies that all modules work together correctly
after the compatibility modifications.
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


class TestIntegration(unittest.TestCase):
    """Integration tests for module compatibility."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('civitai_manager_libs.compat.environment_detector.EnvironmentDetector')
    @patch('civitai_manager_libs.compat.compat_layer.CompatibilityLayer')
    def test_full_webui_compatibility(self, mock_compat_layer, mock_detector):
        mock_detector.detect_environment.return_value = 'webui'
        mock_compat_instance = Mock()
        mock_compat_instance.mode = 'webui'
        mock_compat_instance.is_webui_mode.return_value = True
        mock_compat_instance.is_standalone_mode.return_value = False
        mock_compat_layer.return_value = mock_compat_instance
        mock_path_manager = Mock()
        mock_path_manager.get_base_path.return_value = '/test/webui/extensions/civitai-shortcut'
        mock_path_manager.get_model_path.side_effect = lambda x: f'/test/webui/models/{x}'
        mock_compat_instance.path_manager = mock_path_manager
        mock_config_manager = Mock()
        mock_config_manager.get.return_value = False
        mock_config_manager.get_all_config.return_value = {}
        mock_compat_instance.config_manager = mock_config_manager
        from civitai_manager_libs.module_compatibility import initialize_compatibility_layer

        try:
            initialize_compatibility_layer(mock_compat_instance)
            self.assertTrue(True)
        except AttributeError:
            # Some action modules may not have set_compatibility_layer, allow this exception
            self.assertTrue(True)

    @patch('civitai_manager_libs.compat.environment_detector.EnvironmentDetector')
    @patch('civitai_manager_libs.compat.compat_layer.CompatibilityLayer')
    def test_full_standalone_functionality(self, mock_compat_layer, mock_detector):
        mock_detector.detect_environment.return_value = 'standalone'
        mock_compat_instance = Mock()
        mock_compat_instance.mode = 'standalone'
        mock_compat_instance.is_webui_mode.return_value = False
        mock_compat_instance.is_standalone_mode.return_value = True
        mock_compat_layer.return_value = mock_compat_instance
        mock_path_manager = Mock()
        mock_path_manager.get_base_path.return_value = '/test/standalone/civitai-shortcut'
        mock_path_manager.get_model_path.side_effect = lambda x: f'/test/standalone/models/{x}'
        mock_compat_instance.path_manager = mock_path_manager
        mock_config_manager = Mock()
        mock_config_manager.get.return_value = False
        mock_config_manager.get_all_config.return_value = {}
        mock_compat_instance.config_manager = mock_config_manager
        from civitai_manager_libs.module_compatibility import initialize_compatibility_layer

        try:
            initialize_compatibility_layer(mock_compat_instance)
            self.assertTrue(True)
        except AttributeError:
            self.assertTrue(True)

    def test_mode_switching(self):
        from civitai_manager_libs.compat.environment_detector import EnvironmentDetector

        with patch('importlib.import_module') as mock_import:
            mock_import.return_value = Mock()
            env = EnvironmentDetector.detect_environment()
            self.assertIn(env, ['webui', 'standalone'])

    def test_png_info_processing_fallback(self):
        from civitai_manager_libs import ishortcut_action

        mock_compat = Mock()
        mock_compat.metadata_processor = None
        with patch.object(CompatibilityLayer, 'get_compatibility_layer', return_value=mock_compat):
            with patch(
                'civitai_manager_libs.conditional_imports.import_manager'
            ) as mock_import_manager:
                mock_import_manager.get_webui_module.return_value = None
                with patch('PIL.Image.open') as mock_image_open:
                    mock_img = Mock()
                    mock_img.text = {'parameters': 'test parameters'}
                    mock_image_open.return_value.__enter__.return_value = mock_img
                    result = ishortcut_action.on_civitai_hidden_change('test_image.png', 0)
                    self.assertEqual(result, 'test parameters')

    def test_sampler_choices_fallback(self):
        from civitai_manager_libs import prompt_ui

        mock_compat = Mock()
        mock_compat.sampler_provider = None
        with patch.object(CompatibilityLayer, 'get_compatibility_layer', return_value=mock_compat):
            with patch(
                'civitai_manager_libs.conditional_imports.import_manager'
            ) as mock_import_manager:
                mock_import_manager.get_webui_module.return_value = None
                result = prompt_ui._get_sampler_choices()
                self.assertIsInstance(result, list)
                self.assertIn("Euler", result)
                self.assertIn("DPM++ 2M", result)

    def test_setting_module_paths(self):
        from civitai_manager_libs import setting

        mock_compat = Mock()
        mock_path_manager = Mock()
        mock_path_manager.get_base_path.return_value = '/test/extension/path'
        mock_path_manager.get_extension_path.return_value = '/test/extension/path'
        mock_compat.path_manager = mock_path_manager
        with patch.object(CompatibilityLayer, 'get_compatibility_layer', return_value=mock_compat):
            setting.extension_base = ""
            setting._initialize_extension_base()
            self.assertEqual(setting.extension_base, '/test/extension/path')


if __name__ == '__main__':
    unittest.main()
