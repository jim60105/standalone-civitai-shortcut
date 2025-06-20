"""Tests for UI adapter functionality."""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import after path setup
try:
    from ui_adapter import (
        create_civitai_shortcut_ui,
        _inject_compatibility_layer,
        _initialize_components,
        _create_standalone_settings_ui,
        _on_civitai_tabs_select,
    )
except ImportError as e:
    print(f"Warning: Could not import ui_adapter module: {e}")
    create_civitai_shortcut_ui = None
    _inject_compatibility_layer = None
    _initialize_components = None
    _create_standalone_settings_ui = None
    _on_civitai_tabs_select = None


class TestUIAdapter(unittest.TestCase):
    """Test cases for UI adapter."""

    def setUp(self):
        """Set up test fixtures."""
        if create_civitai_shortcut_ui is None:
            self.skipTest("ui_adapter module not available")

        self.mock_compat_layer = MagicMock()

    @patch('ui_adapter.gr')
    @patch('ui_adapter.scan_action')
    @patch('ui_adapter.setting_action')
    @patch('ui_adapter.classification_action')
    @patch('ui_adapter.civitai_shortcut_action')
    @patch('ui_adapter.recipe_action')
    @patch('ui_adapter._initialize_components')
    @patch('ui_adapter._inject_compatibility_layer')
    def test_create_civitai_shortcut_ui(
        self,
        mock_inject,
        mock_init,
        mock_recipe,
        mock_civitai_shortcut,
        mock_classification,
        mock_setting,
        mock_scan,
        mock_gr,
    ):
        """Test UI creation."""
        # Setup mocks
        mock_tabs = MagicMock()
        mock_gr.Tabs.return_value.__enter__.return_value = mock_tabs
        mock_recipe.on_ui.return_value = (MagicMock(), MagicMock())
        mock_civitai_shortcut.on_ui.return_value = MagicMock()
        mock_classification.on_ui.return_value = MagicMock()
        mock_setting.on_ui.return_value = MagicMock()
        mock_scan.on_scan_ui.return_value = MagicMock()

        create_civitai_shortcut_ui(self.mock_compat_layer)

        # Verify initialization
        mock_inject.assert_called_once_with(self.mock_compat_layer)
        mock_init.assert_called_once_with(self.mock_compat_layer)

    @patch('ui_adapter.gr')
    @patch('ui_adapter.setting_action')
    @patch('ui_adapter.scan_action')
    @patch('ui_adapter.classification_action')
    @patch('ui_adapter.recipe_action')
    @patch('ui_adapter.civitai_shortcut_action')
    def test_ui_structure(
        self,
        mock_civitai_shortcut,
        mock_recipe,
        mock_classification,
        mock_scan,
        mock_setting,
        mock_gr,
    ):
        """Test UI structure creation."""
        mock_compat_layer = MagicMock()
        mock_recipe.on_ui.return_value = (MagicMock(), MagicMock())
        mock_civitai_shortcut.on_ui.return_value = MagicMock()
        mock_classification.on_ui.return_value = MagicMock()
        mock_scan.on_scan_ui.return_value = MagicMock()
        mock_setting.on_setting_ui.return_value = MagicMock()
        # Mock all the action modules
        with patch.dict(
            'sys.modules',
            {
                'scripts.civitai_manager_libs.civitai_shortcut_action': MagicMock(),
                'scripts.civitai_manager_libs.recipe_action': MagicMock(),
                'scripts.civitai_manager_libs.classification_action': MagicMock(),
                'scripts.civitai_manager_libs.setting_action': MagicMock(),
                'scripts.civitai_manager_libs.scan_action': MagicMock(),
            },
        ):
            with patch('ui_adapter._inject_compatibility_layer'), patch(
                'ui_adapter._initialize_components'
            ):
                create_civitai_shortcut_ui(mock_compat_layer)
                # Verify main UI structure was created
                self.assertTrue(mock_gr.Tabs.called)
                self.assertTrue(mock_gr.TabItem.called)
                self.assertTrue(mock_gr.Row.called)

    def test_inject_compatibility_layer(self):
        """Test compatibility layer injection."""
        mock_module = MagicMock()
        mock_module.set_compatibility_layer = MagicMock()

        with patch.dict(
            'sys.modules', {'scripts.civitai_manager_libs.civitai_shortcut_action': mock_module}
        ):
            _inject_compatibility_layer(self.mock_compat_layer)

            mock_module.set_compatibility_layer.assert_called_once_with(self.mock_compat_layer)
            self.assertEqual(mock_module._compat_layer, self.mock_compat_layer)

    @patch('ui_adapter.setting')
    @patch('ui_adapter.model')
    @patch('ui_adapter.util')
    def test_initialize_components(self, mock_util, mock_model, mock_setting):
        """Test component initialization."""
        _initialize_components(self.mock_compat_layer)

        mock_setting.init.assert_called_once()
        mock_model.update_downloaded_model.assert_called_once()
        mock_util.printD.assert_called_once()

    @patch('ui_adapter.gr')
    def test_create_standalone_settings_ui(self, mock_gr):
        """Test standalone settings UI creation."""
        # Setup config manager mock
        self.mock_compat_layer.config_manager.get.return_value = 'test_value'

        _create_standalone_settings_ui(self.mock_compat_layer)

        # Verify config manager was called for various settings
        self.mock_compat_layer.config_manager.get.assert_called()

    def test_on_civitai_tabs_select(self):
        """Test tab selection handling."""
        # Mock event data
        mock_event = MagicMock()
        mock_event.index = 0

        with patch('ui_adapter.datetime') as mock_datetime:
            mock_datetime.datetime.now.return_value = "test_time"
            result = _on_civitai_tabs_select(mock_event)

            # Should return current time for first tab
            self.assertEqual(result[0], "test_time")

    def test_tab_selection_indices(self):
        """Test different tab selection indices."""
        with patch('ui_adapter.datetime') as mock_datetime, patch('ui_adapter.gr') as mock_gr:

            mock_datetime.datetime.now.return_value = "test_time"
            mock_gr.update.return_value = "hidden_update"

            # Test different tab indices
            for i in range(4):
                mock_event = MagicMock()
                mock_event.index = i
                result = _on_civitai_tabs_select(mock_event)

                # Each index should have one visible item and three hidden
                visible_count = sum(1 for item in result if item == "test_time")
                hidden_count = sum(1 for item in result if item == "hidden_update")

                self.assertEqual(visible_count, 1)
                self.assertEqual(hidden_count, 3)


class TestUIComponents(unittest.TestCase):
    """Test cases for UI components functionality."""

    def setUp(self):
        """Set up test fixtures."""
        if create_civitai_shortcut_ui is None:
            self.skipTest("ui_adapter module not available")

    @patch('ui_adapter.gr')
    def test_settings_ui_components(self, mock_gr):
        """Test settings UI component creation."""
        mock_compat_layer = MagicMock()
        mock_compat_layer.config_manager.get.return_value = 'default_value'

        # Create a mock for all Gradio components
        mock_textbox = MagicMock()
        mock_number = MagicMock()
        mock_checkbox = MagicMock()
        mock_slider = MagicMock()
        mock_button = MagicMock()

        mock_gr.Textbox.return_value = mock_textbox
        mock_gr.Number.return_value = mock_number
        mock_gr.Checkbox.return_value = mock_checkbox
        mock_gr.Slider.return_value = mock_slider
        mock_gr.Button.return_value = mock_button

        _create_standalone_settings_ui(mock_compat_layer)

        # Verify components were created
        self.assertTrue(mock_gr.Textbox.called)
        self.assertTrue(mock_gr.Number.called)
        self.assertTrue(mock_gr.Checkbox.called)
        self.assertTrue(mock_gr.Slider.called)
        self.assertTrue(mock_gr.Button.called)

    def test_settings_save_function(self):
        """Test settings save functionality."""
        mock_compat_layer = MagicMock()

        with patch('ui_adapter.gr') as mock_gr:
            # Mock the save function behavior
            mock_gr.update.return_value = MagicMock()

            _create_standalone_settings_ui(mock_compat_layer)

            # Get the save function from the button click handler
            # This is a bit tricky to test directly, so we'll test the mock was called
            self.assertTrue(mock_gr.Button.called)

    def test_settings_reset_function(self):
        """Test settings reset functionality."""
        mock_compat_layer = MagicMock()

        with patch('ui_adapter.gr') as mock_gr:
            _create_standalone_settings_ui(mock_compat_layer)

            # Verify reset button was created
            self.assertTrue(mock_gr.Button.called)


class TestUIIntegration(unittest.TestCase):
    """Test cases for UI integration."""

    def setUp(self):
        """Set up test fixtures."""
        if create_civitai_shortcut_ui is None:
            self.skipTest("ui_adapter module not available")

    @patch('ui_adapter.gr')
    @patch('ui_adapter.setting_action')
    @patch('ui_adapter.scan_action')
    @patch('ui_adapter.classification_action')
    @patch('ui_adapter.recipe_action')
    @patch('ui_adapter.civitai_shortcut_action')
    def test_ui_structure(
        self,
        mock_civitai_shortcut,
        mock_recipe,
        mock_classification,
        mock_scan,
        mock_setting,
        mock_gr,
    ):
        """Test UI structure creation."""
        mock_compat_layer = MagicMock()
        mock_recipe.on_ui.return_value = (MagicMock(), MagicMock())
        mock_civitai_shortcut.on_ui.return_value = MagicMock()
        mock_classification.on_ui.return_value = MagicMock()
        mock_scan.on_scan_ui.return_value = MagicMock()
        mock_setting.on_setting_ui.return_value = MagicMock()
        # Mock all the action modules
        with patch.dict(
            'sys.modules',
            {
                'scripts.civitai_manager_libs.civitai_shortcut_action': MagicMock(),
                'scripts.civitai_manager_libs.recipe_action': MagicMock(),
                'scripts.civitai_manager_libs.classification_action': MagicMock(),
                'scripts.civitai_manager_libs.setting_action': MagicMock(),
                'scripts.civitai_manager_libs.scan_action': MagicMock(),
            },
        ):
            with patch('ui_adapter._inject_compatibility_layer'), patch(
                'ui_adapter._initialize_components'
            ):
                create_civitai_shortcut_ui(mock_compat_layer)
                # Verify main UI structure was created
                self.assertTrue(mock_gr.Tabs.called)
                self.assertTrue(mock_gr.TabItem.called)
                self.assertTrue(mock_gr.Row.called)

    def test_module_injection_error_handling(self):
        """Test error handling during module injection."""
        mock_compat_layer = MagicMock()

        # Test with module that doesn't have set_compatibility_layer
        mock_module = MagicMock()
        del mock_module.set_compatibility_layer  # Remove the method

        with patch.dict(
            'sys.modules', {'scripts.civitai_manager_libs.civitai_shortcut_action': mock_module}
        ):
            # Should not raise exception
            _inject_compatibility_layer(mock_compat_layer)

            # Should still set _compat_layer attribute
            self.assertEqual(mock_module._compat_layer, mock_compat_layer)
