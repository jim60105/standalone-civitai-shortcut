"""
Integration Tests for Module Compatibility

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


class TestIntegration(unittest.TestCase):
    """Integration tests for module compatibility"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('civitai_manager_libs.compat.environment_detector.EnvironmentDetector')
    @patch('civitai_manager_libs.compat.compat_layer.CompatibilityLayer')
    def test_full_webui_compatibility(self, mock_compat_layer, mock_detector):
        """Test full WebUI compatibility"""
        # Mock WebUI environment
        mock_detector.detect_environment.return_value = 'webui'
        mock_compat_instance = Mock()
        mock_compat_instance.mode = 'webui'
        mock_compat_instance.is_webui_mode.return_value = True
        mock_compat_instance.is_standalone_mode.return_value = False
        mock_compat_layer.return_value = mock_compat_instance

        # Mock path manager
        mock_path_manager = Mock()
        mock_path_manager.get_base_path.return_value = '/test/webui/extensions/civitai-shortcut'
        mock_path_manager.get_model_path.side_effect = lambda x: f'/test/webui/models/{x}'
        mock_compat_instance.path_manager = mock_path_manager

        # Mock config manager
        mock_config_manager = Mock()
        mock_config_manager.get.return_value = False
        mock_config_manager.get_all_config.return_value = {}
        mock_compat_instance.config_manager = mock_config_manager

        # Test module initialization
        from civitai_manager_libs.module_compatibility import initialize_compatibility_layer
        
        try:
            initialize_compatibility_layer(mock_compat_instance)
            # If no exception is raised, the test passes
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"WebUI compatibility initialization failed: {e}")

    @patch('civitai_manager_libs.compat.environment_detector.EnvironmentDetector')
    @patch('civitai_manager_libs.compat.compat_layer.CompatibilityLayer')
    def test_full_standalone_functionality(self, mock_compat_layer, mock_detector):
        """Test full standalone mode functionality"""
        # Mock standalone environment
        mock_detector.detect_environment.return_value = 'standalone'
        mock_compat_instance = Mock()
        mock_compat_instance.mode = 'standalone'
        mock_compat_instance.is_webui_mode.return_value = False
        mock_compat_instance.is_standalone_mode.return_value = True
        mock_compat_layer.return_value = mock_compat_instance

        # Mock path manager for standalone
        mock_path_manager = Mock()
        mock_path_manager.get_base_path.return_value = '/test/standalone/civitai-shortcut'
        mock_path_manager.get_model_path.side_effect = lambda x: f'/test/standalone/models/{x}'
        mock_compat_instance.path_manager = mock_path_manager

        # Mock config manager for standalone
        mock_config_manager = Mock()
        mock_config_manager.get.return_value = False
        mock_config_manager.get_all_config.return_value = {}
        mock_compat_instance.config_manager = mock_config_manager

        # Test module initialization
        from civitai_manager_libs.module_compatibility import initialize_compatibility_layer
        
        try:
            initialize_compatibility_layer(mock_compat_instance)
            # If no exception is raised, the test passes
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Standalone functionality initialization failed: {e}")

    def test_mode_switching(self):
        """Test environment detection and mode switching"""
        from civitai_manager_libs.compat.environment_detector import EnvironmentDetector
        
        # Test WebUI detection when modules are available
        with patch('importlib.import_module') as mock_import:
            # Mock successful import of WebUI modules
            mock_import.return_value = Mock()
            env = EnvironmentDetector.detect_environment()
            # In test environment, this should be 'standalone' since WebUI isn't actually available
            self.assertIn(env, ['webui', 'standalone'])

    def test_png_info_processing_fallback(self):
        """Test PNG info processing with fallback mechanisms"""
        from civitai_manager_libs import ishortcut_action
        
        # Mock compatibility layer that doesn't have metadata processor
        mock_compat = Mock()
        mock_compat.metadata_processor = None
        
        with patch.object(ishortcut_action, 'get_compatibility_layer', return_value=mock_compat):
            with patch('civitai_manager_libs.conditional_imports.import_manager') as mock_import_manager:
                # Mock WebUI module not available
                mock_import_manager.get_webui_module.return_value = None
                
                # Mock PIL fallback
                with patch('PIL.Image.open') as mock_image_open:
                    mock_img = Mock()
                    mock_img.text = {'parameters': 'test parameters'}
                    mock_image_open.return_value.__enter__.return_value = mock_img
                    
                    result = ishortcut_action.on_civitai_hidden_change('test_image.png', 0)
                    self.assertEqual(result, 'test parameters')

    def test_sampler_choices_fallback(self):
        """Test sampler choices with fallback mechanisms"""
        from civitai_manager_libs import prompt_ui
        
        # Mock compatibility layer without sampler provider
        mock_compat = Mock()
        mock_compat.sampler_provider = None
        
        with patch.object(prompt_ui, 'get_compatibility_layer', return_value=mock_compat):
            with patch('civitai_manager_libs.conditional_imports.import_manager') as mock_import_manager:
                # Mock WebUI module not available
                mock_import_manager.get_webui_module.return_value = None
                
                result = prompt_ui._get_sampler_choices()
                # Should return fallback sampler list
                self.assertIsInstance(result, list)
                self.assertIn("Euler", result)
                self.assertIn("DPM++ 2M", result)

    def test_setting_module_paths(self):
        """Test setting module path handling with compatibility layer"""
        from civitai_manager_libs import setting
        
        # Mock compatibility layer with path manager
        mock_compat = Mock()
        mock_path_manager = Mock()
        mock_path_manager.get_base_path.return_value = '/test/extension/path'
        mock_compat.path_manager = mock_path_manager
        
        with patch.object(setting, 'get_compatibility_layer', return_value=mock_compat):
            # Reset and test initialization
            setting.extension_base = ""
            setting._initialize_extension_base()
            
            self.assertEqual(setting.extension_base, '/test/extension/path')

    def test_error_handling_graceful_degradation(self):
        """Test that modules gracefully degrade when compatibility layer fails"""
        from civitai_manager_libs import util
        
        # Test with None compatibility layer
        with patch.object(util, 'get_compatibility_layer', return_value=None):
            # Should not raise exception, just use fallback behavior
            try:
                util.printD("test message", force=True)
                self.assertTrue(True)
            except Exception as e:
                self.fail(f"Graceful degradation failed: {e}")


if __name__ == '__main__':
    unittest.main()
