"""Tests for main.py functionality."""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import argparse

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import after path setup to avoid import errors
try:
    from main import CivitaiShortcutApp, create_argument_parser, apply_cli_overrides, main
except ImportError as e:
    # Handle import errors gracefully in test environment
    print(f"Warning: Could not import main module: {e}")
    CivitaiShortcutApp = None
    create_argument_parser = None
    apply_cli_overrides = None
    main = None


class TestCivitaiShortcutApp(unittest.TestCase):
    """Test cases for CivitaiShortcutApp class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_config_path = os.path.join(project_root, 'config', 'default_config.json')

    @patch('scripts.civitai_manager_libs.compat.compat_layer.CompatibilityLayer')
    def test_app_initialization(self, mock_compat_layer):
        """Test application initialization."""
        mock_compat_layer.return_value = MagicMock()

        app = CivitaiShortcutApp()

        self.assertIsNotNone(app)
        self.assertIsNotNone(app.logger)
        mock_compat_layer.assert_called_once_with(mode='standalone')

    @patch('scripts.civitai_manager_libs.compat.compat_layer.CompatibilityLayer')
    def test_app_initialization_with_config(self, mock_compat_layer):
        """Test application initialization with custom config."""
        mock_compat_layer.return_value = MagicMock()

        app = CivitaiShortcutApp(config_path=self.test_config_path)

        self.assertIsNotNone(app)
        self.assertEqual(app.config_path, self.test_config_path)

    @patch('ui_adapter.create_civitai_shortcut_ui')
    @patch('gradio.Blocks')
    @patch('scripts.civitai_manager_libs.compat.compat_layer.CompatibilityLayer')
    def test_create_interface(self, mock_compat_layer, mock_blocks, mock_create_ui):
        """Test interface creation."""
        mock_compat_layer.return_value = MagicMock()
        mock_blocks_instance = MagicMock()
        mock_blocks.return_value.__enter__.return_value = mock_blocks_instance

        app = CivitaiShortcutApp()
        result = app.create_interface()

        self.assertEqual(result, mock_blocks_instance)
        mock_create_ui.assert_called_once_with(app.compat_layer)


class TestArgumentParser(unittest.TestCase):
    """Test cases for command line argument parsing."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = create_argument_parser()

    def test_default_arguments(self):
        """Test parsing with default arguments."""
        args = self.parser.parse_args([])

        self.assertEqual(args.host, '0.0.0.0')
        self.assertEqual(args.port, 7860)
        self.assertFalse(args.share)
        self.assertFalse(args.debug)
        self.assertFalse(args.quiet)

    def test_host_argument(self):
        """Test host argument parsing."""
        args = self.parser.parse_args(['--host', '0.0.0.0'])
        self.assertEqual(args.host, '0.0.0.0')

    def test_port_argument(self):
        """Test port argument parsing."""
        args = self.parser.parse_args(['--port', '8080'])
        self.assertEqual(args.port, 8080)

    def test_share_argument(self):
        """Test share argument parsing."""
        args = self.parser.parse_args(['--share'])
        self.assertTrue(args.share)

    def test_debug_argument(self):
        """Test debug argument parsing."""
        args = self.parser.parse_args(['--debug'])
        self.assertTrue(args.debug)

    def test_config_argument(self):
        """Test config argument parsing."""
        config_path = '/path/to/config.json'
        args = self.parser.parse_args(['--config', config_path])
        self.assertEqual(args.config, config_path)

    def test_models_path_argument(self):
        """Test models-path argument parsing."""
        models_path = '/path/to/models'
        args = self.parser.parse_args(['--models-path', models_path])
        self.assertEqual(args.models_path, models_path)

    def test_multiple_arguments(self):
        """Test parsing multiple arguments."""
        args = self.parser.parse_args(
            ['--host', '0.0.0.0', '--port', '8080', '--share', '--debug', '--config', 'config.json']
        )

        self.assertEqual(args.host, '0.0.0.0')
        self.assertEqual(args.port, 8080)
        self.assertTrue(args.share)
        self.assertTrue(args.debug)
        self.assertEqual(args.config, 'config.json')


class TestCliOverrides(unittest.TestCase):
    """Test cases for CLI configuration overrides."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_app = MagicMock()
        self.mock_config_manager = MagicMock()
        self.mock_app.compat_layer.config_manager = self.mock_config_manager

    def test_apply_models_path(self):
        """Test applying models path override."""
        args = argparse.Namespace(
            models_path='/custom/models',
            output_path=None,
            debug=False,
            quiet=False,
            host='0.0.0.0',
            port=7860,
            share=False,
        )

        apply_cli_overrides(self.mock_app, args)

        self.mock_config_manager.set.assert_any_call('paths.models', '/custom/models')

    def test_apply_debug_mode(self):
        """Test applying debug mode override."""
        args = argparse.Namespace(
            models_path=None,
            output_path=None,
            debug=True,
            quiet=False,
            host='0.0.0.0',
            port=7860,
            share=False,
        )

        with patch('main.logging') as mock_logging:
            apply_cli_overrides(self.mock_app, args)

            self.mock_config_manager.set.assert_any_call('debug.enabled', True)
            mock_logging.getLogger.return_value.setLevel.assert_called_with(mock_logging.DEBUG)

    def test_apply_server_settings(self):
        """Test applying server settings."""
        args = argparse.Namespace(
            models_path=None,
            output_path=None,
            debug=False,
            quiet=False,
            host='0.0.0.0',
            port=8080,
            share=True,
        )

        apply_cli_overrides(self.mock_app, args)

        self.mock_config_manager.set.assert_any_call('server.host', '0.0.0.0')
        self.mock_config_manager.set.assert_any_call('server.port', 8080)
        self.mock_config_manager.set.assert_any_call('server.share', True)


class TestMainFunction(unittest.TestCase):
    """Test cases for main function."""

    @patch('main.CivitaiShortcutApp')
    @patch('main.create_argument_parser')
    def test_main_function_success(self, mock_parser, mock_app):
        """Test successful main function execution."""
        # Setup mocks
        mock_args = MagicMock()
        mock_args.config = None
        mock_args.host = '0.0.0.0'
        mock_args.port = 7860
        mock_args.share = False
        mock_args.debug = False

        mock_parser.return_value.parse_args.return_value = mock_args
        mock_app_instance = MagicMock()
        mock_app.return_value = mock_app_instance

        # Mock sys.argv to avoid actual argument parsing
        with patch('sys.argv', ['main.py']):
            try:
                main()
            except SystemExit:
                pass  # Expected when mocking

        # Verify application was created and configured
        mock_app.assert_called_once()
        mock_app_instance.create_interface.assert_called_once()

    @patch('main.create_argument_parser')
    def test_main_function_keyboard_interrupt(self, mock_parser):
        """Test main function handles KeyboardInterrupt."""
        mock_parser.return_value.parse_args.side_effect = KeyboardInterrupt()

        with patch('sys.exit') as mock_exit:
            with patch('builtins.print') as mock_print:
                main()

                mock_print.assert_called_with("\nApplication stopped")
                mock_exit.assert_called_with(0)


if __name__ == '__main__':
    unittest.main()
