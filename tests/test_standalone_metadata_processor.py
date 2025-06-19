"""
Unit tests for StandaloneMetadataProcessor
(scripts/civitai_manager_libs/compat/standalone_adapters/standalone_metadata_processor.py)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import unittest
import tempfile
from PIL import Image, PngImagePlugin

from civitai_manager_libs.compat.standalone_adapters.standalone_metadata_processor import (
    StandaloneMetadataProcessor,
)


class TestStandaloneMetadataProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = StandaloneMetadataProcessor()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.img_path = os.path.join(self.temp_dir.name, 'test.png')
        # 建立一個帶有 metadata 的 PNG
        img = Image.new('RGB', (64, 64), color='red')
        meta = PngImagePlugin.PngInfo()
        meta.add_text("parameters", "prompt\nNegative prompt: bad\nSteps: 20, Sampler: Euler")
        img.save(self.img_path, pnginfo=meta)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_extract_png_info_success(self):
        geninfo, params, info_text = self.processor.extract_png_info(self.img_path)
        self.assertIn("prompt", geninfo)
        # Steps 只會在 Negative prompt 字串內
        self.assertIn("Steps", geninfo)
        self.assertIn("Negative prompt", params)
        self.assertIn("parameters", info_text)

    def test_extract_png_info_file_not_exist(self):
        geninfo, params, info_text = self.processor.extract_png_info("/not/exist.png")
        self.assertIsNone(geninfo)
        self.assertIsNone(params)
        self.assertIsNone(info_text)

    def test_extract_png_info_invalid_image(self):
        # 建立一個非圖片檔案
        bad_path = os.path.join(self.temp_dir.name, 'bad.txt')
        with open(bad_path, 'w') as f:
            f.write('not an image')
        geninfo, params, info_text = self.processor.extract_png_info(bad_path)
        self.assertIsNone(geninfo)
        self.assertIsNone(params)
        self.assertIsNone(info_text)

    def test_extract_parameters_from_png(self):
        result = self.processor.extract_parameters_from_png(self.img_path)
        self.assertIn("prompt", result)

    def test_parse_generation_parameters(self):
        text = "prompt\nNegative prompt: bad\nSteps: 20, Sampler: Euler, Size: 512x512"
        params = self.processor.parse_generation_parameters(text)
        self.assertEqual(params["Steps"], "20")
        self.assertEqual(params["Sampler"], "Euler")
        self.assertEqual(params["Size-1"], "512")
        self.assertEqual(params["Size-2"], "512")
        self.assertEqual(params["Negative prompt"], "bad")

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
