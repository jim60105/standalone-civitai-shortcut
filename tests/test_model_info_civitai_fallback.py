"""Test Model Information Civitai API fallback functionality."""

import os
import tempfile
import unittest
from unittest import mock

from PIL import Image

# Add the parent directory to the path for imports
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
from civitai_manager_libs import ishortcut_action


class TestModelInfoCivitaiFallback(unittest.TestCase):
    """Test Model Information tab Civitai API fallback functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_model_id = "12345"
        self.test_civitai_response = {
            "items": [
                {
                    "id": "img1",
                    "meta": {
                        "prompt": "A beautiful landscape",
                        "negativePrompt": "ugly, blurry",
                        "sampler": "DPM++ 2M Karras",
                        "cfgScale": 7,
                        "steps": 20,
                        "seed": 12345,
                        "Model": "test-model-v1",
                        "Size": "512x512",
                    },
                },
                {
                    "id": "img2",
                    "meta": {
                        "prompt": "Another test image",
                        "negativePrompt": "low quality",
                        "sampler": "Euler a",
                        "cfgScale": 8,
                        "steps": 25,
                        "seed": 67890,
                    },
                },
            ]
        }

    def test_civitai_api_fallback_success(self):
        """Test successful Civitai API fallback when PNG has no info."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Create a test PNG without parameters
            img = Image.new('RGB', (100, 100), color='red')
            img.save(temp_path)

            # Mock Civitai API call
            with mock.patch('civitai_manager_libs.civitai.request_models') as mock_api:
                mock_api.return_value = self.test_civitai_response

                # Create mock SelectData
                select_data = mock.MagicMock()
                select_data.index = 0

                civitai_images = [temp_path]

                # Call the function with model ID
                img_index, hidden_path, tab_update, png_info = ishortcut_action.on_gallery_select(
                    select_data, civitai_images, self.test_model_id
                )

                # Verify Civitai API was called
                mock_api.assert_called_once_with(
                    f"https://civitai.com/api/v1/images?limit=20&modelId={self.test_model_id}"
                    f"&nsfw=X"
                )

                # Verify PNG info contains Civitai data
                self.assertIn("Generated using example parameters from Civitai", png_info)
                self.assertIn("A beautiful landscape", png_info)
                self.assertIn("ugly, blurry", png_info)
                self.assertIn("DPM++ 2M Karras", png_info)
                self.assertIn("CFG scale: 7", png_info)
                self.assertIn("Steps: 20", png_info)
                self.assertIn("Seed: 12345", png_info)

        finally:
            os.unlink(temp_path)

    def test_civitai_api_fallback_no_model_id(self):
        """Test fallback behavior when no model ID is provided."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Create a test PNG without parameters
            img = Image.new('RGB', (100, 100), color='blue')
            img.save(temp_path)

            # Mock Civitai API call
            with mock.patch('civitai_manager_libs.civitai.request_models') as mock_api:
                mock_api.return_value = self.test_civitai_response

                # Create mock SelectData
                select_data = mock.MagicMock()
                select_data.index = 0

                civitai_images = [temp_path]

                # Call the function without model ID
                img_index, hidden_path, tab_update, png_info = ishortcut_action.on_gallery_select(
                    select_data, civitai_images, None
                )

                # Verify Civitai API was NOT called
                mock_api.assert_not_called()

                # Verify PNG info shows no parameters found
                self.assertIn("No generation parameters found", png_info)

        finally:
            os.unlink(temp_path)

    def test_civitai_api_fallback_api_error(self):
        """Test fallback behavior when Civitai API fails."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Create a test PNG without parameters
            img = Image.new('RGB', (100, 100), color='green')
            img.save(temp_path)

            # Mock Civitai API call to raise exception
            with mock.patch('civitai_manager_libs.civitai.request_models') as mock_api:
                mock_api.side_effect = Exception("API Error")

                # Create mock SelectData
                select_data = mock.MagicMock()
                select_data.index = 0

                civitai_images = [temp_path]

                # Call the function with model ID
                img_index, hidden_path, tab_update, png_info = ishortcut_action.on_gallery_select(
                    select_data, civitai_images, self.test_model_id
                )

                # Verify Civitai API was called
                mock_api.assert_called_once()

                # Verify PNG info shows no parameters found (graceful fallback)
                self.assertIn("No generation parameters found", png_info)

        finally:
            os.unlink(temp_path)

    def test_civitai_api_fallback_no_meta_data(self):
        """Test fallback behavior when Civitai API returns no meta data."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Create a test PNG without parameters
            img = Image.new('RGB', (100, 100), color='yellow')
            img.save(temp_path)

            # Mock Civitai API call with no meta data
            mock_response = {"items": [{"id": "img1", "meta": None}]}
            with mock.patch('civitai_manager_libs.civitai.request_models') as mock_api:
                mock_api.return_value = mock_response

                # Create mock SelectData
                select_data = mock.MagicMock()
                select_data.index = 0

                civitai_images = [temp_path]

                # Call the function with model ID
                img_index, hidden_path, tab_update, png_info = ishortcut_action.on_gallery_select(
                    select_data, civitai_images, self.test_model_id
                )

                # Verify Civitai API was called
                mock_api.assert_called_once()

                # Verify PNG info shows no parameters found
                self.assertIn("No generation parameters found", png_info)

        finally:
            os.unlink(temp_path)

    def test_png_info_takes_priority_over_civitai(self):
        """Test that PNG info takes priority over Civitai API."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Create a test PNG WITH parameters
            img = Image.new('RGB', (100, 100), color='purple')
            from PIL.PngImagePlugin import PngInfo

            pnginfo = PngInfo()
            pnginfo.add_text(
                "parameters", "Prompt: PNG embedded prompt\nNegative prompt: PNG negative"
            )
            img.save(temp_path, pnginfo=pnginfo)

            # Mock Civitai API call
            with mock.patch('civitai_manager_libs.civitai.request_models') as mock_api:
                mock_api.return_value = self.test_civitai_response

                # Create mock SelectData
                select_data = mock.MagicMock()
                select_data.index = 0

                civitai_images = [temp_path]

                # Call the function with model ID
                img_index, hidden_path, tab_update, png_info = ishortcut_action.on_gallery_select(
                    select_data, civitai_images, self.test_model_id
                )

                # Verify Civitai API was NOT called (PNG info takes priority)
                mock_api.assert_not_called()

                # Verify PNG info contains embedded data, not Civitai data
                self.assertIn("PNG embedded prompt", png_info)
                self.assertIn("PNG negative", png_info)
                self.assertNotIn("Generated using example parameters from Civitai", png_info)

        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    unittest.main()
