"""
Test fallback paths for compatibility layer (paths.py).

Covers scripts/civitai_manager_libs/compat/paths.py for coverage.
"""

import unittest
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


class TestCompatPaths(unittest.TestCase):
    """Test class for TestCompatPaths."""

    def test_paths_are_path_objects_and_exist(self):
        """Test paths are path objects and exist."""
        from civitai_manager_libs.compat import paths

        # All should be Path objects
        self.assertIsInstance(paths.script_path, Path)
        self.assertIsInstance(paths.data_path, Path)
        self.assertIsInstance(paths.models_path, Path)
        # script_path should exist (project root)
        self.assertTrue(paths.script_path.exists())
        # data_path and models_path may not exist, but should be joinable
        self.assertEqual(paths.data_path, paths.script_path / "data")
        self.assertEqual(paths.models_path, paths.data_path / "models")

    def test_paths_string_equivalence(self):
        """Test paths string equivalence."""
        from civitai_manager_libs.compat import paths

        # The string version should match the Path version
        self.assertEqual(str(paths.data_path), os.path.join(str(paths.script_path), "data"))
        self.assertEqual(str(paths.models_path), os.path.join(str(paths.data_path), "models"))


if __name__ == '__main__':
    unittest.main()
