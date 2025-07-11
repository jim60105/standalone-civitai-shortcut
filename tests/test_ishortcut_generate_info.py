#!/usr/bin/env python3
"""Test cases for Model Information tab generate info extraction."""

import os
import sys
import tempfile
import unittest.mock as mock
from PIL import Image, PngImagePlugin

# Add the project root to the path for module imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'scripts'))

from scripts.civitai_manager_libs import ishortcut_action
from scripts.civitai_manager_libs.compat.compat_layer import CompatibilityLayer


class TestIshortcutGenerateInfo:
    """Test cases for Model Information tab generate info extraction."""

    def setup_method(self):
        """Set up test data."""
        self.test_images = ["test1.png", "test2.png"]
        # Create a fake PNG image with parameters
        self.test_png_params = (
            "Prompt: test prompt\n"
            "Negative prompt: test negative\n"
            "Steps: 20, Sampler: DPM++ 2M, CFG scale: 7, Seed: 123456, "
            "Size: 512x512, Model hash: abcd1234"
        )

    def test_on_gallery_select_with_png_info(self):
        """Test gallery select with PNG info."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Create a test PNG with parameters
            img = Image.new('RGB', (100, 100), color='red')
            pnginfo = PngImagePlugin.PngInfo()
            pnginfo.add_text("parameters", self.test_png_params)
            img.save(temp_path, pnginfo=pnginfo)

            # Create mock SelectData
            select_data = mock.MagicMock()
            select_data.index = 0

            civitai_images = [temp_path]

            # Call the function
            img_index, hidden_path, tab_update, png_info = ishortcut_action.on_gallery_select(
                select_data, civitai_images, "12345"
            )

            # Verify results
            assert img_index == 0
            assert hidden_path == temp_path
            assert 'test prompt' in png_info
            assert 'test negative' in png_info
            assert 'DPM++ 2M' in png_info
            assert 'CFG scale: 7' in png_info

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_on_gallery_select_no_png_info(self):
        """Test gallery select with no PNG info."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Create a test PNG without parameters
            img = Image.new('RGB', (100, 100), color='blue')
            img.save(temp_path)

            # Create mock SelectData
            select_data = mock.MagicMock()
            select_data.index = 0

            civitai_images = [temp_path]

            # Call the function
            img_index, hidden_path, tab_update, png_info = ishortcut_action.on_gallery_select(
                select_data, civitai_images, "12345"
            )

            # Verify results
            assert img_index == 0
            assert hidden_path == temp_path
            assert "No generation parameters found" in png_info

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_on_gallery_select_url_conversion(self):
        """Test gallery select with URL that needs conversion."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Create a test PNG with parameters
            img = Image.new('RGB', (100, 100), color='green')
            pnginfo = PngImagePlugin.PngInfo()
            pnginfo.add_text("parameters", self.test_png_params)
            img.save(temp_path, pnginfo=pnginfo)

            # Mock the URL to file conversion
            test_url = "http://example.com/test.png"

            with mock.patch(
                'scripts.civitai_manager_libs.settings.get_image_url_to_gallery_file',
                return_value=temp_path,
            ):
                # Create mock SelectData
                select_data = mock.MagicMock()
                select_data.index = 0

                civitai_images = [test_url]

                # Call the function
                img_index, hidden_path, tab_update, png_info = ishortcut_action.on_gallery_select(
                    select_data, civitai_images, "12345"
                )

                # Verify results
                assert img_index == 0
                assert hidden_path == temp_path
                assert 'test prompt' in png_info

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_on_gallery_select_compatibility_layer_fallback(self):
        """Test gallery select with compatibility layer fallback."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Create a test PNG without parameters
            img = Image.new('RGB', (100, 100), color='yellow')
            img.save(temp_path)

            # Mock compatibility layer
            mock_compat = mock.MagicMock()
            mock_processor = mock.MagicMock()
            mock_processor.extract_png_info.return_value = (self.test_png_params, None)
            mock_compat.metadata_processor = mock_processor

            with mock.patch.object(
                CompatibilityLayer, 'get_compatibility_layer', return_value=mock_compat
            ):
                # Create mock SelectData
                select_data = mock.MagicMock()
                select_data.index = 0

                civitai_images = [temp_path]

                # Call the function
                img_index, hidden_path, tab_update, png_info = ishortcut_action.on_gallery_select(
                    select_data, civitai_images, "12345"
                )

                # Verify results
                assert img_index == 0
                assert hidden_path == temp_path
                assert 'test prompt' in png_info
                assert 'test negative' in png_info

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_on_gallery_select_error_handling(self):
        """Test gallery select error handling."""
        # Create mock SelectData with invalid index
        select_data = mock.MagicMock()
        select_data.index = 0

        civitai_images = ["non_existent_file.png"]

        # Call the function
        img_index, hidden_path, tab_update, png_info = ishortcut_action.on_gallery_select(
            select_data, civitai_images, "12345"
        )

        # Verify error handling
        assert img_index == 0
        assert hidden_path == "non_existent_file.png"
        assert "Image file not accessible" in png_info
