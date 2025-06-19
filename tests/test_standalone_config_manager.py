"""
Unit tests for StandaloneConfigManager.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import unittest
import tempfile

from civitai_manager_libs.compat.standalone_adapters.standalone_config_manager import (
    StandaloneConfigManager,
    OptionInfo,
)


class TestStandaloneConfigManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, 'test_config.json')

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_init_and_default_options(self):
        mgr = StandaloneConfigManager(config_file_path=self.config_path)
        self.assertIsInstance(mgr.data, dict)
        self.assertIsInstance(mgr.data_labels, dict)

    def test_set_and_get_config(self):
        mgr = StandaloneConfigManager(config_file_path=self.config_path)
        # Add a new option
        mgr.data_labels['foo'] = OptionInfo(default=123)
        mgr.data['foo'] = 123
        mgr.foo = 456
        self.assertEqual(mgr.foo, 456)
        self.assertEqual(mgr.data['foo'], 456)

    def test_save_and_load(self):
        mgr = StandaloneConfigManager(config_file_path=self.config_path)
        mgr.data_labels['bar'] = OptionInfo(default='abc')
        mgr.data['bar'] = 'abc'
        mgr.bar = 'xyz'
        mgr.save(self.config_path)
        # Reload
        mgr2 = StandaloneConfigManager(config_file_path=self.config_path)
        self.assertEqual(mgr2.bar, 'xyz')

    def test_onchange_callback(self):
        called = {}

        def cb():
            called['ok'] = True

        mgr = StandaloneConfigManager(config_file_path=self.config_path)
        mgr.data_labels['baz'] = OptionInfo(default=1, onchange=cb)
        mgr.data['baz'] = 1
        mgr.baz = 2
        self.assertTrue(called.get('ok'))

    def test_do_not_save(self):
        mgr = StandaloneConfigManager(config_file_path=self.config_path)
        mgr.data_labels['tmp'] = OptionInfo(default=5, do_not_save=True)
        mgr.data['tmp'] = 5
        mgr.tmp = 10
        # Should not update data
        self.assertEqual(mgr.data['tmp'], 5)

    def test_invalid_component_args(self):
        mgr = StandaloneConfigManager(config_file_path=self.config_path)
        mgr.data_labels['hidden'] = OptionInfo(default=1, component_args={'visible': False})
        mgr.data['hidden'] = 1
        with self.assertRaises(RuntimeError):
            mgr.hidden = 2

    def test_corrupted_config_file(self):
        # Write invalid JSON
        with open(self.config_path, 'w') as f:
            f.write('{invalid json')
        mgr = StandaloneConfigManager(config_file_path=self.config_path)
        # Should not raise, fallback to defaults
        self.assertIsInstance(mgr.data, dict)


if __name__ == '__main__':
    unittest.main()
