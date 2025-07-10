"""
Unit tests for StandalonePathManager.

(scripts/civitai_manager_libs/compat/standalone_adapters/standalone_path_manager.py)
"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import unittest
from civitai_manager_libs.compat.standalone_adapters.standalone_path_manager import (
    StandalonePathManager,
)
from civitai_manager_libs.settings import config_manager


class TestStandalonePathManager(unittest.TestCase):
    """Test class for TestStandalonePathManager."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = self.temp_dir.name
        self.manager = StandalonePathManager(base_path=self.base_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_get_base_and_script_path(self):
        """Test get base and script path."""
        self.assertEqual(self.manager.get_base_path(), self.base_path)
        self.assertEqual(self.manager.get_script_path(), self.base_path)
        self.assertEqual(self.manager.get_extension_path(), self.base_path)

    def test_get_models_path(self):
        """Test get models path."""
        models_path = self.manager.get_models_path()
        self.assertTrue(models_path.endswith('models'))

    def test_get_model_folder_path(self):
        """Test get model folder path."""
        folder = self.manager.get_model_folder_path('Lora')
        self.assertTrue(os.path.exists(folder))
        self.assertIn('Lora', folder)

    def test_ensure_directory_exists(self):
        """Test ensure directory exists."""
        new_dir = os.path.join(self.base_path, 'newdir')
        self.assertTrue(self.manager.ensure_directory_exists(new_dir))
        self.assertTrue(os.path.isdir(new_dir))

    def test_validate_path(self):
        """Test validate path."""
        valid = self.manager.validate_path(self.base_path)
        self.assertTrue(valid)
        invalid = self.manager.validate_path('/not/exist/path')
        self.assertFalse(invalid)

    def test_get_relative_and_resolve_path(self):
        """Test get relative and resolve path."""
        rel = self.manager.get_relative_path(os.path.join(self.base_path, 'foo'))
        self.assertEqual(rel, 'foo')
        abs_path = self.manager.resolve_path('bar')
        self.assertTrue(abs_path.startswith(self.base_path))

    def test_add_model_folder(self):
        """Test add model folder."""
        result = self.manager.add_model_folder('TestType', 'custom_models')
        self.assertTrue(result)
        folder = self.manager.get_model_folder_path('TestType')
        self.assertTrue(os.path.exists(folder))

    def test_get_all_model_paths(self):
        """Test get all model paths."""
        paths = self.manager.get_all_model_paths()
        self.assertIsInstance(paths, dict)
        self.assertIn('Lora', paths)

    def test_get_output_cache_logs_temp(self):
        """Test get output cache logs temp."""
        self.assertTrue(os.path.exists(self.manager.get_output_path()))
        self.assertTrue(os.path.exists(self.manager.get_cache_path()))
        self.assertTrue(os.path.exists(self.manager.get_logs_path()))
        self.assertTrue(os.path.exists(self.manager.get_temp_path()))

    def test_get_config_path(self):
        """Test get config path."""
        config_path = self.manager.get_config_path()
        self.assertTrue(config_manager.get_setting('config_path').endswith('settings.json'))


if __name__ == '__main__':
    unittest.main()
