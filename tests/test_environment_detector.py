"""
Test Environment Detector.

Unit tests for the environment detection functionality.
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add the scripts directory to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from civitai_manager_libs.compat.environment_detector import EnvironmentDetector  # noqa: E402


class TestEnvironmentDetector(unittest.TestCase):
    """Test cases for EnvironmentDetector class."""

    def setUp(self):
        """Set up test fixtures."""
        # Reset cache before each test
        EnvironmentDetector.reset_cache()

    def tearDown(self):
        """Clean up after each test."""
        EnvironmentDetector.reset_cache()

    def test_detect_environment_webui_modules_available(self):
        """Test detection when WebUI modules are available."""
        # Reset cache to ensure clean test
        EnvironmentDetector.reset_cache()

        # Create proper mock modules
        mock_modules_scripts = MagicMock()
        # Mock basedir as a callable function that returns a valid path
        mock_modules_scripts.basedir = MagicMock(return_value='/fake/webui/path')

        mock_modules_shared = MagicMock()

        # Also need to mock the modules package itself
        mock_modules = MagicMock()
        mock_modules.scripts = mock_modules_scripts
        mock_modules.shared = mock_modules_shared

        with patch.dict(
            'sys.modules',
            {
                'modules': mock_modules,
                'modules.scripts': mock_modules_scripts,
                'modules.shared': mock_modules_shared,
            },
        ), patch('os.path.exists') as mock_exists:
            # Mock os.path.exists to return True for our fake webui path
            mock_exists.return_value = True

            # Clear any import cache and force re-detection
            EnvironmentDetector.reset_cache()
            result = EnvironmentDetector.detect_environment()
            self.assertEqual(result, 'webui')

    def test_detect_environment_webui_modules_unavailable(self):
        """Test detection when WebUI modules are not available."""
        # Ensure modules are not available
        if 'modules.scripts' in sys.modules:
            del sys.modules['modules.scripts']
        if 'modules.shared' in sys.modules:
            del sys.modules['modules.shared']

        # Mock _check_webui_markers to return False
        with patch.object(EnvironmentDetector, '_check_webui_markers', return_value=False):
            result = EnvironmentDetector.detect_environment()
            self.assertEqual(result, 'standalone')

    def test_detect_environment_webui_markers_present(self):
        """Test detection when WebUI markers are present."""
        with patch.object(EnvironmentDetector, '_check_webui_markers', return_value=True):
            result = EnvironmentDetector.detect_environment()
            self.assertEqual(result, 'webui')

    def test_is_webui_mode(self):
        """Test is_webui_mode method."""
        with patch.object(EnvironmentDetector, 'detect_environment', return_value='webui'):
            self.assertTrue(EnvironmentDetector.is_webui_mode())

        with patch.object(EnvironmentDetector, 'detect_environment', return_value='standalone'):
            self.assertFalse(EnvironmentDetector.is_webui_mode())

    def test_is_standalone_mode(self):
        """Test is_standalone_mode method."""
        with patch.object(EnvironmentDetector, 'detect_environment', return_value='standalone'):
            self.assertTrue(EnvironmentDetector.is_standalone_mode())

        with patch.object(EnvironmentDetector, 'detect_environment', return_value='webui'):
            self.assertFalse(EnvironmentDetector.is_standalone_mode())

    def test_force_environment(self):
        """Test force_environment method."""
        EnvironmentDetector.force_environment('webui')
        self.assertEqual(EnvironmentDetector.detect_environment(), 'webui')

        EnvironmentDetector.force_environment('standalone')
        self.assertEqual(EnvironmentDetector.detect_environment(), 'standalone')

    def test_caching_behavior(self):
        """Test that environment detection is cached."""
        with patch.object(
            EnvironmentDetector, '_check_webui_markers', return_value=False
        ) as mock_check:
            # First call should trigger detection
            result1 = EnvironmentDetector.detect_environment()
            self.assertEqual(result1, 'standalone')
            self.assertEqual(mock_check.call_count, 1)

            # Second call should use cache
            result2 = EnvironmentDetector.detect_environment()
            self.assertEqual(result2, 'standalone')
            self.assertEqual(mock_check.call_count, 1)  # Still 1, not called again

    def test_reset_cache(self):
        """Test cache reset functionality."""
        # Set cache
        EnvironmentDetector.force_environment('webui')
        self.assertEqual(EnvironmentDetector.detect_environment(), 'webui')

        # Reset cache
        EnvironmentDetector.reset_cache()

        # Should detect again
        with patch.object(EnvironmentDetector, '_check_webui_markers', return_value=False):
            result = EnvironmentDetector.detect_environment()
            self.assertEqual(result, 'standalone')

    def test_check_webui_markers_webui_file_exists(self):
        """Test _check_webui_markers with webui.py file present."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.side_effect = lambda path: path.endswith('webui.py')

            result = EnvironmentDetector._check_webui_markers()
            self.assertTrue(result)

    def test_check_webui_markers_launch_file_exists(self):
        """Test _check_webui_markers with launch.py file present."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.side_effect = lambda path: path.endswith('launch.py')

            result = EnvironmentDetector._check_webui_markers()
            self.assertTrue(result)

    def test_check_webui_markers_extensions_dir_exists(self):
        """Test _check_webui_markers with extensions directory present."""
        with patch('os.path.exists') as mock_exists, patch('os.path.isdir') as mock_isdir:
            mock_exists.side_effect = lambda path: path.endswith('extensions')
            mock_isdir.return_value = True

            result = EnvironmentDetector._check_webui_markers()
            self.assertTrue(result)

    def test_check_webui_markers_environment_variable(self):
        """Test _check_webui_markers with environment variable set."""
        with patch.dict(os.environ, {'WEBUI_MODE': '1'}):
            result = EnvironmentDetector._check_webui_markers()
            self.assertTrue(result)

    def test_check_webui_markers_none_present(self):
        """Test _check_webui_markers when no markers are present."""
        with patch('os.path.exists', return_value=False), patch(
            'os.path.isdir', return_value=False
        ), patch.dict(os.environ, {}, clear=True):

            result = EnvironmentDetector._check_webui_markers()
            self.assertFalse(result)

    def test_get_environment_info(self):
        """Test get_environment_info method."""
        with patch.object(EnvironmentDetector, 'detect_environment', return_value='standalone'):
            info = EnvironmentDetector.get_environment_info()

            self.assertIsInstance(info, dict)
            self.assertEqual(info['environment'], 'standalone')
            self.assertIn('python_version', info)
            self.assertIn('working_directory', info)
            self.assertIn('python_path', info)

    def test_get_environment_info_webui_mode(self):
        """Test get_environment_info in WebUI mode."""
        # Reset cache and force WebUI mode
        EnvironmentDetector.reset_cache()
        EnvironmentDetector.force_environment('webui')

        # Create proper mock modules
        mock_modules_scripts = MagicMock()
        mock_modules_scripts.basedir = MagicMock(return_value='/fake/webui')

        mock_modules_shared = MagicMock()
        mock_modules_shared.cmd_opts = 'fake_cmd_opts'

        # Mock the modules package itself
        mock_modules = MagicMock()
        mock_modules.scripts = mock_modules_scripts
        mock_modules.shared = mock_modules_shared

        with patch.dict(
            'sys.modules',
            {
                'modules': mock_modules,
                'modules.scripts': mock_modules_scripts,
                'modules.shared': mock_modules_shared,
            },
        ):
            info = EnvironmentDetector.get_environment_info()

            self.assertEqual(info['environment'], 'webui')
            self.assertEqual(info['webui_base_dir'], '/fake/webui')
            self.assertEqual(info['webui_cmd_opts'], 'fake_cmd_opts')


if __name__ == '__main__':
    unittest.main()
