"""
Unit tests for WebUIMetadataProcessor
(scripts/civitai_manager_libs/compat/webui_adapters/webui_metadata_processor.py)
"""

import sys
import os
import types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import unittest
from unittest.mock import patch, MagicMock
from civitai_manager_libs.compat.webui_adapters.webui_metadata_processor import (
    WebUIMetadataProcessor,
)


class TestWebUIMetadataProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = WebUIMetadataProcessor()
        # Inject dummy modules for patching
        self._modules_backup = dict(sys.modules)
        sys.modules['modules'] = types.ModuleType('modules')
        sys.modules['modules.extras'] = types.ModuleType('modules.extras')
        sys.modules['modules.infotext_utils'] = types.ModuleType('modules.infotext_utils')
        sys.modules['modules.script_callbacks'] = types.ModuleType('modules.script_callbacks')
        sys.modules['modules.shared'] = types.ModuleType('modules.shared')
        # Add required attributes for patching
        sys.modules['modules.extras'].run_pnginfo = MagicMock(return_value=(None, None, None))
        sys.modules['modules.infotext_utils'].parse_generation_parameters = lambda x: {}
        # Make modules.infotext_utils accessible as attribute of modules
        sys.modules['modules'].infotext_utils = sys.modules['modules.infotext_utils']
        sys.modules['modules'].shared = sys.modules['modules.shared']
        sys.modules['modules'].extras = sys.modules['modules.extras']
        sys.modules['modules'].script_callbacks = sys.modules['modules.script_callbacks']

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._modules_backup)

    def test_extract_png_info_webui_success(self):
        sys.modules['modules.extras'].run_pnginfo = MagicMock(
            return_value=("info1", {"parameters": "p"}, "info3")
        )
        with patch('modules.extras.run_pnginfo') as mock_run:
            mock_run.return_value = ("info1", {"parameters": "p"}, "info3")
            geninfo, params, info3 = self.processor.extract_png_info('fake.png')
            self.assertEqual(geninfo, "info1")
            self.assertEqual(params, {"parameters": "p"})
            self.assertEqual(info3, "info3")

    def test_extract_png_info_webui_fail_fallback(self):
        with patch('modules.extras.run_pnginfo', side_effect=ImportError):
            with patch.object(
                self.processor, '_extract_png_info_fallback', return_value=(None, None, None)
            ) as fallback:
                result = self.processor.extract_png_info('fake.png')
                self.assertEqual(result, (None, None, None))
                fallback.assert_called_once()

    def test_extract_parameters_from_png(self):
        with patch.object(
            self.processor, 'extract_png_info', return_value=(None, {"parameters": "abc"}, None)
        ):
            self.assertEqual(self.processor.extract_parameters_from_png('f.png'), "abc")
        with patch.object(self.processor, 'extract_png_info', return_value=("info1", None, None)):
            self.assertEqual(self.processor.extract_parameters_from_png('f.png'), "info1")
        with patch.object(self.processor, 'extract_png_info', return_value=(None, None, None)):
            self.assertIsNone(self.processor.extract_parameters_from_png('f.png'))

    def test_parse_generation_parameters_webui(self):
        fake_parse = MagicMock(return_value={"Steps": 20})
        with patch('modules.infotext_utils.parse_generation_parameters', fake_parse):
            with patch('modules.infotext_utils', create=True) as m:
                m.parse_generation_parameters = fake_parse
                result = self.processor.parse_generation_parameters("txt")
                self.assertEqual(result, {"Steps": 20})

    def test_parse_generation_parameters_fallback(self):
        # No modules.infotext_utils, fallback to local
        import sys

        sys_modules_backup = dict(sys.modules)
        sys.modules.pop('modules.infotext_utils', None)
        sys.modules.pop('modules', None)
        try:
            result = self.processor.parse_generation_parameters(
                "prompt\nNegative prompt: bad\nSteps: 10, Sampler: Euler"
            )
            self.assertIn("prompt", result)
            self.assertIn("negative_prompt", result)
            self.assertIn("steps", result)
        finally:
            sys.modules.clear()
            sys.modules.update(sys_modules_backup)

    def test_extract_prompt_from_parameters(self):
        text = "prompt\nNegative prompt: bad"
        pos, neg = self.processor.extract_prompt_from_parameters(text)
        self.assertEqual(pos, "prompt")
        self.assertEqual(neg, "bad")

    def test_format_parameters_for_display(self):
        params = {"Prompt": "p", "Negative prompt": "n", "Steps": "10", "Sampler": "Euler"}
        display = self.processor.format_parameters_for_display(params)
        self.assertIn("p", display)
        self.assertIn("Negative prompt: n", display)
        self.assertIn("Steps", display)
        self.assertIn("Sampler", display)


if __name__ == '__main__':
    unittest.main()
