"""
Unit tests for WebUIPathManager (scripts/civitai_manager_libs/compat/webui_adapters/webui_path_manager.py)
"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import unittest
from civitai_manager_libs.compat.webui_adapters.webui_path_manager import WebUIPathManager


class TestWebUIPathManager(unittest.TestCase):
    def setUp(self):
        self.manager = WebUIPathManager()
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_validate_path(self):
        self.assertFalse(self.manager.validate_path(None))
        self.assertFalse(self.manager.validate_path(123))
        self.assertFalse(self.manager.validate_path('/not/exist/path'))
        self.assertTrue(self.manager.validate_path(self.temp_dir.name))

    def test_add_model_folder(self):
        # Valid path
        self.assertTrue(self.manager.add_model_folder('Test', self.temp_dir.name))
        # Invalid path (should create)
        new_dir = os.path.join(self.temp_dir.name, 'new_model_dir')
        self.assertTrue(self.manager.add_model_folder('Test', new_dir))
        self.assertTrue(os.path.isdir(new_dir))

    def test_get_all_model_paths(self):
        paths = self.manager.get_all_model_paths()
        self.assertIsInstance(paths, dict)
        # 檢查 key 不區分大小寫
        keys_lower = [k.lower() for k in paths.keys()]
        self.assertIn('lora', keys_lower)

    def test_get_script_user_models_paths(self):
        # These methods should return a string path
        self.assertIsInstance(self.manager.get_script_path(), str)
        self.assertIsInstance(self.manager.get_user_data_path(), str)
        self.assertIsInstance(self.manager.get_models_path(), str)

    def test_get_model_folder_path(self):
        path = self.manager.get_model_folder_path('Lora')
        self.assertIsInstance(path, str)

    def test_get_config_path(self):
        path = self.manager.get_config_path()
        self.assertIsInstance(path, str)

    def test_ensure_directory_exists(self):
        new_dir = os.path.join(self.temp_dir.name, 'ensure_dir')
        self.assertTrue(self.manager.ensure_directory_exists(new_dir))
        self.assertTrue(os.path.isdir(new_dir))


if __name__ == '__main__':
    unittest.main()
