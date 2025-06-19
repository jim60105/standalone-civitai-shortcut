"""
Unit tests for WebUIParameterProcessor (scripts/civitai_manager_libs/compat/webui_adapters/webui_parameter_processor.py)
"""

import sys
import os
import types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import unittest
from unittest.mock import patch, MagicMock
from civitai_manager_libs.compat.webui_adapters.webui_parameter_processor import (
    WebUIParameterProcessor,
)


class TestWebUIParameterProcessor(unittest.TestCase):
    def setUp(self):
        self.proc = WebUIParameterProcessor()
        # Inject dummy modules for patching
        self._modules_backup = dict(sys.modules)
        sys.modules['modules'] = types.ModuleType('modules')
        sys.modules['modules.extras'] = types.ModuleType('modules.extras')
        sys.modules['modules.infotext_utils'] = types.ModuleType('modules.infotext_utils')
        sys.modules['modules.script_callbacks'] = types.ModuleType('modules.script_callbacks')
        sys.modules['modules.shared'] = types.ModuleType('modules.shared')
        # Add required attributes for patching
        sys.modules['modules.infotext_utils'].parse_generation_parameters = lambda x: {}
        sys.modules['modules'].infotext_utils = sys.modules['modules.infotext_utils']
        sys.modules['modules'].shared = sys.modules['modules.shared']
        sys.modules['modules'].extras = sys.modules['modules.extras']
        sys.modules['modules'].script_callbacks = sys.modules['modules.script_callbacks']

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._modules_backup)

    def test_parse_parameters_webui(self):
        fake_parse = MagicMock(return_value={"Steps": 20})
        with patch('modules.infotext_utils.parse_generation_parameters', fake_parse):
            with patch('modules.infotext_utils', create=True) as m:
                m.parse_generation_parameters = fake_parse
                result = self.proc.parse_parameters("txt")
                self.assertEqual(result, {"Steps": 20})

    def test_parse_parameters_fallback(self):
        import sys

        sys_modules_backup = dict(sys.modules)
        sys.modules.pop('modules.infotext_utils', None)
        sys.modules.pop('modules', None)
        try:
            text = "prompt\nNegative prompt: bad\nSteps: 10, Sampler: Euler"
            result = self.proc.parse_parameters(text)
            self.assertIn("prompt", result)
            self.assertIn("negative_prompt", result)
            self.assertIn("steps", result)
            self.assertIn("sampler_name", result)
        finally:
            sys.modules.clear()
            sys.modules.update(sys_modules_backup)

    def test_format_parameters(self):
        params = {"prompt": "p", "negative_prompt": "n", "steps": 10, "sampler_name": "Euler"}
        out = self.proc.format_parameters(params)
        self.assertIn("p", out)
        self.assertIn("Negative prompt: n", out)
        self.assertIn("Steps: 10", out)
        self.assertIn("Sampler: Euler", out)

    def test_extract_prompt_and_negative(self):
        text = "good\nNegative prompt: bad\nSteps: 10"
        pos, neg = self.proc.extract_prompt_and_negative(text)
        self.assertEqual(pos, "good")
        self.assertEqual(neg, "bad")

    def test_merge_parameters(self):
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        merged = self.proc.merge_parameters(base, override)
        self.assertEqual(merged, {"a": 1, "b": 3, "c": 4})

    def test_split_parameter_line(self):
        line = "Steps: 20, Sampler: Euler, Size: 512x512"
        pairs = self.proc._split_parameter_line(line)
        self.assertIn(("Steps", "20"), pairs)
        self.assertIn(("Sampler", "Euler"), pairs)
        self.assertIn(("Size", "512x512"), pairs)

    def test_normalize_parameter_key(self):
        self.assertEqual(self.proc._normalize_parameter_key("CFG scale"), "cfg_scale")
        self.assertEqual(self.proc._normalize_parameter_key("Model Hash"), "model_hash")
        self.assertEqual(self.proc._normalize_parameter_key("Custom Key"), "custom_key")

    def test_parse_parameter_value(self):
        self.assertEqual(self.proc._parse_parameter_value("steps", "10"), 10)
        self.assertEqual(self.proc._parse_parameter_value("cfg_scale", "2.5"), 2.5)
        self.assertEqual(
            self.proc._parse_parameter_value("size", "128x256"), {"width": 128, "height": 256}
        )
        self.assertEqual(self.proc._parse_parameter_value("other", "abc"), "abc")

    def test_format_parameter_key(self):
        self.assertEqual(self.proc._format_parameter_key("cfg_scale"), "CFG scale")
        self.assertEqual(self.proc._format_parameter_key("sampler_name"), "Sampler")
        self.assertEqual(self.proc._format_parameter_key("custom_key"), "Custom Key")


if __name__ == '__main__':
    unittest.main()
