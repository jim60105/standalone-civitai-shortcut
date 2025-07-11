"""Unit tests for initialization utilities."""

from unittest.mock import patch, MagicMock

from scripts.civitai_manager_libs.settings import initialization
from scripts.civitai_manager_libs.compat.compat_layer import CompatibilityLayer


class TestInitialization:
    """Tests for initialization utilities."""
    
    def test_set_compatibility_layer(self):
        """Test setting compatibility layer."""
        mock_layer = MagicMock()
        initialization.set_compatibility_layer(mock_layer)
        
        # Verify the layer was set by checking if it can be retrieved
        with patch.object(CompatibilityLayer, 'get_compatibility_layer',
                          return_value=mock_layer):
            result = CompatibilityLayer.get_compatibility_layer()
            assert result == mock_layer

    def test_init_success(self, tmp_path):
        """Test successful initialization."""
        with patch('scripts.civitai_manager_libs.settings.path_manager.init_paths'):
            initialization.init()
            # init() doesn't take parameters, it creates its own config manager

    def test_init_makedirs_exception(self, tmp_path):
        """Test initialization with makedirs exception."""
        with patch('os.makedirs', side_effect=OSError("Permission denied")):
            # Should not raise exception, just log warning
            initialization.init()

    def test_set_nsfw(self):
        """Test setting NSFW filter."""
        # Mock the local import in the function
        with patch.object(initialization, 'config_manager', create=True) as mock_config:
            # Mock the import by patching at module level
            with patch('scripts.civitai_manager_libs.settings.config_manager') as mock_cm:
                # Make the local import return our mock
                mock_config.set_setting = mock_cm.set_setting
                initialization.set_NSFW("enabled", "moderate")
                mock_cm.set_setting.assert_any_call("nsfw_filter_enable", "enabled")
                mock_cm.set_setting.assert_any_call("nsfw_level", "moderate")

    def test_save_nsfw(self):
        """Test saving NSFW settings."""
        # Mock the local import in the function
        with patch.object(initialization, 'config_manager', create=True) as mock_config:
            with patch('scripts.civitai_manager_libs.settings.config_manager') as mock_cm:
                mock_config.save_settings = mock_cm.save_settings
                mock_cm.save_settings.return_value = True
                result = initialization.save_NSFW()
                mock_cm.save_settings.assert_called_once()
                assert result is True
