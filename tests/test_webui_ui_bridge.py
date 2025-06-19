"""
Unit tests for WebUIUIBridge.

(scripts/civitai_manager_libs/compat/webui_adapters/webui_ui_bridge.py)
"""

import sys
import os
import types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import unittest
from unittest.mock import patch, MagicMock
from civitai_manager_libs.compat.webui_adapters.webui_ui_bridge import WebUIUIBridge


class TestWebUIUIBridge(unittest.TestCase):
    """Test class for TestWebUIUIBridge."""

    def setUp(self):
        self.bridge = WebUIUIBridge()
        # Inject dummy modules for patching
        self._modules_backup = dict(sys.modules)
        sys.modules['modules'] = types.ModuleType('modules')
        sys.modules['modules.extras'] = types.ModuleType('modules.extras')
        sys.modules['modules.infotext_utils'] = types.ModuleType('modules.infotext_utils')
        sys.modules['modules.script_callbacks'] = types.ModuleType('modules.script_callbacks')
        sys.modules['modules.shared'] = types.ModuleType('modules.shared')
        sys.modules['gradio'] = types.ModuleType('gradio')
        # Add required attributes for patching
        sys.modules['modules.infotext_utils'].create_buttons = lambda *a, **kw: {}
        sys.modules['modules.infotext_utils'].bind_buttons = lambda *a, **kw: None
        sys.modules['modules.script_callbacks'].on_ui_tabs = lambda *a, **kw: None
        sys.modules['modules'].infotext_utils = sys.modules['modules.infotext_utils']
        sys.modules['modules'].shared = sys.modules['modules.shared']
        sys.modules['modules'].extras = sys.modules['modules.extras']
        sys.modules['modules'].script_callbacks = sys.modules['modules.script_callbacks']

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._modules_backup)

    def test_register_ui_tabs_webui(self):
        """Test register ui tabs webui."""
        with patch('modules.script_callbacks.on_ui_tabs') as cb:
            self.bridge.register_ui_tabs(lambda: None)
            cb.assert_called_once()

    def test_register_ui_tabs_importerror(self):
        """Test register ui tabs importerror."""
        with patch('modules.script_callbacks.on_ui_tabs', side_effect=ImportError):
            # Should not raise
            self.bridge.register_ui_tabs(lambda: None)

    def test_create_send_to_buttons_webui(self):
        """Test create send to buttons webui."""
        fake_create = MagicMock(return_value={'A': 1})
        with patch('modules.infotext_utils.create_buttons', fake_create):
            with patch('modules.infotext_utils', create=True) as m:
                m.create_buttons = fake_create
                result = self.bridge.create_send_to_buttons(['A'])
                self.assertEqual(result, {'A': 1})

    def test_create_send_to_buttons_fallback(self):
        """Test create send to buttons fallback."""
        with patch('modules.infotext_utils.create_buttons', side_effect=ImportError):
            with patch.object(
                self.bridge, '_create_simple_buttons', return_value={'B': 2}
            ) as fallback:
                result = self.bridge.create_send_to_buttons(['B'])
                self.assertEqual(result, {'B': 2})
                fallback.assert_called_once()

    def test_bind_send_to_buttons_webui(self):
        """Test bind send to buttons webui."""
        fake_bind = MagicMock()
        with patch('modules.infotext_utils.bind_buttons', fake_bind):
            with patch('modules.infotext_utils', create=True) as m:
                m.bind_buttons = fake_bind
                self.bridge.bind_send_to_buttons({'A': 1}, None, None)
                fake_bind.assert_called_once()

    def test_bind_send_to_buttons_fallback(self):
        """Test bind send to buttons fallback."""
        with patch('modules.infotext_utils.bind_buttons', side_effect=ImportError):
            with patch.object(self.bridge, '_bind_simple_buttons') as fallback:
                self.bridge.bind_send_to_buttons({'B': 2}, None, None)
                fallback.assert_called_once()

    def test_is_webui_mode(self):
        """Test is webui mode."""
        self.assertTrue(self.bridge.is_webui_mode())

    def test_interrupt_generation(self):
        """Test interrupt generation."""
        fake_state = MagicMock()
        with patch('modules.shared', create=True) as m:
            m.state = fake_state
            self.bridge.interrupt_generation()
            fake_state.interrupt.assert_called_once()

    def test_interrupt_generation_importerror(self):
        """Test interrupt generation importerror."""
        with patch('modules.shared', side_effect=ImportError):
            # Should not raise
            self.bridge.interrupt_generation()

    def test_request_restart(self):
        """Test request restart."""
        fake_state = MagicMock()
        with patch('modules.shared', create=True) as m:
            m.state = fake_state
            self.bridge.request_restart()
            self.assertTrue(fake_state.need_restart)

    def test_request_restart_importerror(self):
        """Test request restart importerror."""
        with patch('modules.shared', side_effect=ImportError):
            # Should not raise
            self.bridge.request_restart()

    def test_get_ui_config(self):
        """Test get ui config."""
        fake_opts = MagicMock()
        fake_opts.foo = 123
        with patch('modules.shared', create=True) as m:
            m.opts = fake_opts
            val = self.bridge.get_ui_config('foo', 0)
            self.assertEqual(val, 123)

    def test_get_ui_config_importerror(self):
        """Test get ui config importerror."""
        import sys

        sys_modules_backup = dict(sys.modules)
        sys.modules.pop('modules.shared', None)
        try:
            val = self.bridge.get_ui_config('bar', 99)
            self.assertEqual(val, 99)
        finally:
            sys.modules.clear()
            sys.modules.update(sys_modules_backup)

    def test_create_simple_buttons_importerror(self):
        """Test create simple buttons importerror."""
        # Patch gradio, set Button to raise ImportError
        import gradio

        orig_button = getattr(gradio, 'Button', None)

        class Dummy:
            def __init__(*a, **kw):
                raise ImportError()

        setattr(gradio, 'Button', Dummy)
        try:
            val = self.bridge._create_simple_buttons(['A'])
            self.assertIsNone(val)
        finally:
            if orig_button is not None:
                setattr(gradio, 'Button', orig_button)
            else:
                delattr(gradio, 'Button')

    def test_bind_simple_buttons_importerror(self):
        """Test bind simple buttons importerror."""
        # Should not raise
        self.bridge._bind_simple_buttons(None, None, None)


if __name__ == '__main__':
    unittest.main()
