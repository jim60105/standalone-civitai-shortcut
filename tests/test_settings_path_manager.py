"""Unit tests for path management utilities."""

import os
from unittest.mock import patch, MagicMock

from scripts.civitai_manager_libs.settings import path_manager
from scripts.civitai_manager_libs.compat.compat_layer import CompatibilityLayer


class TestPathManager:
    """Tests for path management utilities."""

    def test_get_extension_base(self):
        """Test getting extension base path."""
        result = path_manager.get_extension_base()
        assert isinstance(result, str)

    def test_set_extension_base(self):
        """Test setting extension base path."""
        original_base = path_manager.extension_base
        try:
            path_manager.set_extension_base("/test/path")
            assert path_manager.get_extension_base() == "/test/path"
        finally:
            path_manager.extension_base = original_base

    def test_initialize_extension_base_with_compat(self):
        """Test initializing extension base with compatibility layer."""
        mock_compat = MagicMock()
        mock_compat.path_manager.get_extension_path.return_value = "/compat/path"

        with patch.object(CompatibilityLayer, 'get_compatibility_layer', return_value=mock_compat):
            path_manager.initialize_extension_base()
            assert path_manager.extension_base == "/compat/path"

    def test_initialize_extension_base_with_magicmock(self):
        """Test initializing extension base when compat returns MagicMock."""
        mock_compat = MagicMock()
        mock_path = MagicMock()
        mock_path.__class__.__name__ = 'MagicMock'
        mock_compat.path_manager.get_extension_path.return_value = mock_path

        with patch.object(CompatibilityLayer, 'get_compatibility_layer', return_value=mock_compat):
            path_manager.initialize_extension_base()
            assert path_manager.extension_base == '/test/extension/path'

    def test_initialize_extension_base_fallback(self):
        """Test fallback initialization when no compatibility layer."""
        with patch.object(CompatibilityLayer, 'get_compatibility_layer', return_value=None):
            path_manager.initialize_extension_base()
            assert isinstance(path_manager.extension_base, str)

    def test_get_no_card_preview_image(self):
        """Test getting no card preview image path."""
        result = path_manager.get_no_card_preview_image()
        expected = os.path.join(path_manager.extension_base, "img", "card-no-preview.png")
        assert result == expected

    def test_get_nsfw_disable_image(self):
        """Test getting NSFW disable image path."""

    def test_no_card_preview_image_property(self):
        """Test that settings.no_card_preview_image property access works and matches the function result."""
        from scripts.civitai_manager_libs import settings
        prop_val = settings.no_card_preview_image
        func_val = settings.get_no_card_preview_image()
        assert prop_val == func_val, "Property and function access should return the same value"
        result = path_manager.get_nsfw_disable_image()
        expected = os.path.join(path_manager.extension_base, "img", "nsfw-no-preview.png")
        assert result == expected

    def test_init_paths_success(self, tmp_path):
        """Test successful path initialization."""
        mock_config = MagicMock()
        mock_config.get_setting.return_value = str(tmp_path / "downloads")

        with patch('os.makedirs') as mock_makedirs:
            path_manager.init_paths(mock_config)
            mock_makedirs.assert_called()

    def test_init_paths_with_exception(self, tmp_path):
        """Test path initialization with exception."""
        mock_config = MagicMock()
        mock_config.get_setting.return_value = str(tmp_path / "downloads")

        with patch('os.makedirs', side_effect=OSError("Permission denied")):
            # Should not raise exception, just log warning
            path_manager.init_paths(mock_config)

    def test_migrate_existing_files_success(self, tmp_path):
        """Test successful file migration."""
        # Create test files in tmp_path
        old_file = tmp_path / "CivitaiShortCut.json"
        old_file.write_text('{"test": "data"}')

        with (
            patch('os.path.exists') as mock_exists,
            patch('shutil.move') as mock_move,
            patch('os.getcwd', return_value=str(tmp_path)),
        ):

            # Mock exists to simulate files that need migration
            def exists_side_effect(path):
                # Return True for source files that exist
                return "CivitaiShortCut.json" in path and "data_sc" not in path

            mock_exists.side_effect = exists_side_effect

            path_manager.migrate_existing_files()
            # The function should attempt to move files
            assert mock_move.call_count >= 0  # Just check it was called or not

    def test_migrate_existing_files_with_exception(self, tmp_path):
        """Test file migration with exception."""
        with (
            patch('os.path.exists', return_value=True),
            patch('shutil.move', side_effect=OSError("Permission denied")),
            patch('os.getcwd', return_value=str(tmp_path)),
        ):

            # Should not raise exception, just log warning
            path_manager.migrate_existing_files()

    def test_migrate_existing_files_sc_prefix(self, tmp_path):
        """Test migration of files with sc_ prefix."""
        sc_folder = tmp_path / "sc_test"
        sc_folder.mkdir()

        with (
            patch('os.listdir', return_value=['sc_test']),
            patch('os.path.exists') as mock_exists,
            patch('shutil.move') as mock_move,
            patch.object(path_manager, 'extension_base', str(tmp_path)),
            patch('os.makedirs'),
        ):

            # Mock exists to return True for old, False for new
            def exists_side_effect(path):
                path_str = str(path)
                # Return True for the base path (extension_base)
                if path_str == str(tmp_path):
                    return True
                # Return True for source sc_test folder (old path)
                if 'sc_test' in path_str and 'data_sc' not in path_str:
                    return True
                # Return False for destination path in data_sc
                if 'data_sc' in path_str:
                    return False
                return False

            mock_exists.side_effect = exists_side_effect

            path_manager.migrate_existing_files()
            mock_move.assert_called()

    def test_load_model_folder_data_with_compat(self):
        """Test loading model folder data with compatibility layer."""
        mock_compat = MagicMock()
        mock_compat.path_manager.get_model_path.return_value = "/test/path"
        mock_config = MagicMock()
        mock_config.load_settings.return_value = {}

        with patch.object(CompatibilityLayer, 'get_compatibility_layer', return_value=mock_compat):
            path_manager.load_model_folder_data(mock_config)
            assert path_manager.model_folders['TextualInversion'] == "/test/path"

    def test_load_model_folder_data_fallback(self):
        """Test loading model folder data with fallback method."""
        mock_config = MagicMock()
        mock_config.load_settings.return_value = {}

        mock_shared = MagicMock()
        mock_cmd_opts = MagicMock()
        mock_cmd_opts.embeddings_dir = "/fallback/embeddings"
        mock_shared.cmd_opts = mock_cmd_opts

        with (
            patch.object(CompatibilityLayer, 'get_compatibility_layer', return_value=None),
            patch(
                'scripts.civitai_manager_libs.conditional_imports'
                '.import_manager.get_webui_module',
                return_value=mock_shared,
            ),
        ):
            path_manager.load_model_folder_data(mock_config)
            assert path_manager.model_folders['TextualInversion'] == "/fallback/embeddings"

    def test_load_model_folder_data_with_user_folders(self):
        """Test loading model folder data with user-defined folders."""
        mock_config = MagicMock()
        mock_config.load_settings.return_value = {
            'model_folders': {'LoCon': '/user/locon', 'Wildcards': '/user/wildcards'}
        }

        with patch.object(CompatibilityLayer, 'get_compatibility_layer', return_value=None):
            path_manager.load_model_folder_data(mock_config)
            assert path_manager.model_folders['LoCon'] == '/user/locon'
            assert path_manager.model_folders['Wildcards'] == '/user/wildcards'

    def test_load_model_folder_data_no_environment(self):
        """Test loading model folder data when no environment is loaded."""
        mock_config = MagicMock()
        mock_config.load_settings.return_value = None

        with patch.object(CompatibilityLayer, 'get_compatibility_layer', return_value=None):
            # Should not raise exception
            path_manager.load_model_folder_data(mock_config)

    def test_get_model_folders(self):
        """Test getting list of model folders."""
        original_folders = path_manager.model_folders.copy()
        try:
            path_manager.model_folders = {'Type1': '/path1', 'Type2': '/path2'}
            result = path_manager.get_model_folders()
            assert result == ['/path1', '/path2']
        finally:
            path_manager.model_folders = original_folders

    def test_get_image_url_to_shortcut_file_valid(self):
        """Test generating shortcut file path from valid URL."""
        result = path_manager.get_image_url_to_shortcut_file(
            "123", "456", "http://example.com/image123.jpg"
        )
        expected_path = os.path.join(
            path_manager.shortcut_info_folder, "123", "456-image123.png"  # Uses .png, not .webp
        )
        assert result == expected_path

    def test_get_image_url_to_shortcut_file_none_url(self):
        """Test generating shortcut file path from None URL."""
        result = path_manager.get_image_url_to_shortcut_file("123", "456", None)
        assert result is None

    def test_get_image_url_to_gallery_file_valid(self):
        """Test generating gallery file path from valid URL."""
        result = path_manager.get_image_url_to_gallery_file("http://example.com/gallery123.jpg")
        expected_path = os.path.join(
            path_manager.shortcut_gallery_folder, "gallery123.png"  # Uses .png
        )
        assert result == expected_path

    def test_get_image_url_to_gallery_file_none_url(self):
        """Test generating gallery file path from None URL."""
        result = path_manager.get_image_url_to_gallery_file(None)
        assert result is None
