"""
Tests for command line interface functionality
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import tempfile
import json

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import after path setup
try:
    from main import create_argument_parser, apply_cli_overrides
except ImportError as e:
    print(f"Warning: Could not import main module: {e}")
    create_argument_parser = None
    apply_cli_overrides = None


class TestCommandLineInterface(unittest.TestCase):
    """Test cases for command line interface"""

    def setUp(self):
        """Set up test fixtures"""
        if create_argument_parser is None:
            self.skipTest("main module not available")
        self.parser = create_argument_parser()

    def test_help_output(self):
        """Test help output contains expected information"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['--help'])

    def test_version_output(self):
        """Test version output"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['--version'])

    def test_invalid_port(self):
        """Test invalid port number handling"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args(['--port', 'invalid'])

    def test_port_range_validation(self):
        """Test port range validation"""
        # Valid port
        args = self.parser.parse_args(['--port', '8080'])
        self.assertEqual(args.port, 8080)

        # Test with minimum port
        args = self.parser.parse_args(['--port', '1'])
        self.assertEqual(args.port, 1)

        # Test with maximum port
        args = self.parser.parse_args(['--port', '65535'])
        self.assertEqual(args.port, 65535)

    def test_config_file_path_validation(self):
        """Test config file path validation"""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"test": "config"}, f)
            temp_config = f.name

        try:
            args = self.parser.parse_args(['--config', temp_config])
            self.assertEqual(args.config, temp_config)
        finally:
            os.unlink(temp_config)

    def test_boolean_flags(self):
        """Test boolean flag handling"""
        # Test individual flags
        args = self.parser.parse_args(['--share'])
        self.assertTrue(args.share)
        self.assertFalse(args.debug)
        self.assertFalse(args.quiet)

        args = self.parser.parse_args(['--debug'])
        self.assertTrue(args.debug)
        self.assertFalse(args.share)

        args = self.parser.parse_args(['--quiet'])
        self.assertTrue(args.quiet)
        self.assertFalse(args.debug)

    def test_multiple_boolean_flags(self):
        """Test multiple boolean flags together"""
        args = self.parser.parse_args(['--share', '--debug', '--quiet'])
        self.assertTrue(args.share)
        self.assertTrue(args.debug)
        self.assertTrue(args.quiet)

    def test_path_arguments(self):
        """Test path argument parsing"""
        models_path = '/custom/models'
        output_path = '/custom/output'

        args = self.parser.parse_args(['--models-path', models_path, '--output-path', output_path])

        self.assertEqual(args.models_path, models_path)
        self.assertEqual(args.output_path, output_path)

    def test_complex_argument_combination(self):
        """Test complex argument combinations"""
        args = self.parser.parse_args(
            [
                '--host',
                '0.0.0.0',
                '--port',
                '8080',
                '--share',
                '--debug',
                '--config',
                'config.json',
                '--models-path',
                '/models',
                '--output-path',
                '/output',
            ]
        )

        self.assertEqual(args.host, '0.0.0.0')
        self.assertEqual(args.port, 8080)
        self.assertTrue(args.share)
        self.assertTrue(args.debug)
        self.assertEqual(args.config, 'config.json')
        self.assertEqual(args.models_path, '/models')
        self.assertEqual(args.output_path, '/output')


class TestConfigurationOverrides(unittest.TestCase):
    """Test cases for configuration overrides"""

    def setUp(self):
        """Set up test fixtures"""
        if apply_cli_overrides is None:
            self.skipTest("main module not available")

        self.mock_app = MagicMock()
        self.mock_config_manager = MagicMock()
        self.mock_app.compat_layer.config_manager = self.mock_config_manager

    def test_no_overrides(self):
        """Test when no overrides are specified"""
        import argparse

        args = argparse.Namespace(
            models_path=None,
            output_path=None,
            debug=False,
            quiet=False,
            host='127.0.0.1',
            port=7860,
            share=False,
        )

        apply_cli_overrides(self.mock_app, args)

        # Should still set server settings
        self.mock_config_manager.set.assert_any_call('server.host', '127.0.0.1')
        self.mock_config_manager.set.assert_any_call('server.port', 7860)
        self.mock_config_manager.set.assert_any_call('server.share', False)

    def test_path_overrides(self):
        """Test path configuration overrides"""
        import argparse

        args = argparse.Namespace(
            models_path='/custom/models',
            output_path='/custom/output',
            debug=False,
            quiet=False,
            host='127.0.0.1',
            port=7860,
            share=False,
        )

        apply_cli_overrides(self.mock_app, args)

        self.mock_config_manager.set.assert_any_call('paths.models', '/custom/models')
        self.mock_config_manager.set.assert_any_call('paths.output', '/custom/output')

    def test_debug_override(self):
        """Test debug mode override"""
        import argparse

        args = argparse.Namespace(
            models_path=None,
            output_path=None,
            debug=True,
            quiet=False,
            host='127.0.0.1',
            port=7860,
            share=False,
        )

        with patch('main.logging') as mock_logging:
            apply_cli_overrides(self.mock_app, args)

            self.mock_config_manager.set.assert_any_call('debug.enabled', True)
            # Check that logging level was set
            mock_logging.getLogger.return_value.setLevel.assert_called()

    def test_quiet_override(self):
        """Test quiet mode override"""
        import argparse

        args = argparse.Namespace(
            models_path=None,
            output_path=None,
            debug=False,
            quiet=True,
            host='127.0.0.1',
            port=7860,
            share=False,
        )

        with patch('main.logging') as mock_logging:
            apply_cli_overrides(self.mock_app, args)

            # Check that logging level was set to WARNING
            mock_logging.getLogger.return_value.setLevel.assert_called_with(mock_logging.WARNING)

    def test_server_overrides(self):
        """Test server configuration overrides"""
        import argparse

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

    def test_all_overrides(self):
        """Test all configuration overrides together"""
        import argparse

        args = argparse.Namespace(
            models_path='/custom/models',
            output_path='/custom/output',
            debug=True,
            quiet=False,  # debug should override quiet
            host='0.0.0.0',
            port=8080,
            share=True,
        )

        with patch('main.logging') as mock_logging:
            apply_cli_overrides(self.mock_app, args)

            # Check all overrides were applied
            expected_calls = [
                ('paths.models', '/custom/models'),
                ('paths.output', '/custom/output'),
                ('debug.enabled', True),
                ('server.host', '0.0.0.0'),
                ('server.port', 8080),
                ('server.share', True),
            ]

            for key, value in expected_calls:
                self.mock_config_manager.set.assert_any_call(key, value)


class TestArgumentValidation(unittest.TestCase):
    """Test cases for argument validation"""

    def setUp(self):
        """Set up test fixtures"""
        if create_argument_parser is None:
            self.skipTest("main module not available")

    def test_host_validation(self):
        """Test host argument validation"""
        parser = create_argument_parser()

        # Valid hosts
        valid_hosts = ['127.0.0.1', '0.0.0.0', 'localhost', '192.168.1.1']
        for host in valid_hosts:
            args = parser.parse_args(['--host', host])
            self.assertEqual(args.host, host)

    def test_port_validation(self):
        """Test port argument validation"""
        parser = create_argument_parser()

        # Valid ports
        valid_ports = [1, 80, 443, 8080, 65535]
        for port in valid_ports:
            args = parser.parse_args(['--port', str(port)])
            self.assertEqual(args.port, port)

    def test_config_file_extension(self):
        """Test config file extension handling"""
        parser = create_argument_parser()

        # Should accept various config file extensions
        config_files = ['config.json', 'settings.json', '/path/to/config.json', 'my-config.json']

        for config_file in config_files:
            args = parser.parse_args(['--config', config_file])
            self.assertEqual(args.config, config_file)


if __name__ == '__main__':
    unittest.main()
