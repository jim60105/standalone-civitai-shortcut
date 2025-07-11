"""Test for Civitai User Gallery Generate Info fix."""

from unittest.mock import Mock, patch
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
from civitai_manager_libs import civitai_gallery_action
from civitai_manager_libs.settings import config_manager


class TestCivitaiGalleryGenerateInfo:
    """Test cases for Civitai gallery generate info extraction."""

    def setup_method(self):
        """Set up test data."""
        # Mock image metadata from Civitai API
        self.mock_metadata = {
            'c065d13f-38b3-4cad-90e3-dbd0b8a4a23d': {
                'id': 83509145,
                'url': (
                    'https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/'
                    'c065d13f-38b3-4cad-90e3-dbd0b8a4a23d/width=1344/'
                    'c065d13f-38b3-4cad-90e3-dbd0b8a4a23d.jpeg'
                ),
                'meta': {
                    'prompt': 'test prompt',
                    'negativePrompt': 'test negative',
                    'sampler': 'DPM++ 2M',
                    'cfgScale': 7,
                },
            }
        }

    def test_on_gallery_select_with_metadata(self):
        """Test gallery select with valid Civitai metadata."""
        # Set global metadata
        civitai_gallery_action._current_page_metadata = self.mock_metadata

        # Create mock event
        mock_evt = Mock()
        mock_evt.index = 0

        # Create temporary file with UUID in name
        with tempfile.NamedTemporaryFile(
            suffix='-c065d13f-38b3-4cad-90e3-dbd0b8a4a23d.png', delete=False
        ) as tmp:
            temp_path = tmp.name

        try:
            # Mock civitai_images
            civitai_images = [temp_path]

            # Call the function
            result = civitai_gallery_action.on_gallery_select(mock_evt, civitai_images)

            # Verify results
            assert len(result) == 4
            img_index, hidden_path, tabs_update, png_info = result

            assert img_index == 0
            assert hidden_path == temp_path
            # Check for Auto1111 format: prompt first line, negative prompt second line,
            # params third line
            lines = png_info.split('\n')
            assert len(lines) >= 3
            assert lines[0] == 'test prompt'  # First line should be prompt without prefix
            assert lines[1] == 'Negative prompt: test negative'  # Second line with prefix
            assert 'Sampler: DPM++ 2M' in lines[2]  # Third line should contain sampler
            assert 'CFG scale: 7' in lines[2]  # Third line should contain CFG scale

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_on_gallery_select_no_metadata(self):
        """Test gallery select with no metadata available."""
        # Clear global metadata
        civitai_gallery_action._current_page_metadata = {}

        # Create mock event
        mock_evt = Mock()
        mock_evt.index = 0

        # Create temporary file with UUID in name
        with tempfile.NamedTemporaryFile(
            suffix='-c065d13f-38b3-4cad-90e3-dbd0b8a4a23d.png', delete=False
        ) as tmp:
            temp_path = tmp.name

        try:
            # Mock civitai_images
            civitai_images = [temp_path]

            # Call the function
            result = civitai_gallery_action.on_gallery_select(mock_evt, civitai_images)

            # Verify results
            assert len(result) == 4
            img_index, hidden_path, tabs_update, png_info = result

            assert img_index == 0
            assert hidden_path == temp_path
            assert 'Image metadata not found' in png_info

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_on_gallery_select_invalid_filename(self):
        """Test gallery select with invalid filename format."""
        # Clear global metadata
        civitai_gallery_action._current_page_metadata = {}

        # Create mock event
        mock_evt = Mock()
        mock_evt.index = 0

        # Create temporary file without UUID in name
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            temp_path = tmp.name

        try:
            # Mock civitai_images
            civitai_images = [temp_path]

            # Call the function
            result = civitai_gallery_action.on_gallery_select(mock_evt, civitai_images)

            # Verify results
            assert len(result) == 4
            img_index, hidden_path, tabs_update, png_info = result

            assert img_index == 0
            assert hidden_path == temp_path
            assert 'Could not extract image ID' in png_info

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_get_user_gallery_stores_metadata(self):
        """Test that get_user_gallery stores metadata globally."""
        # Mock image data from API
        mock_image_data = [
            {
                'id': 83509145,
                'url': (
                    'https://image.civitai.com/test/'
                    'c065d13f-38b3-4cad-90e3-dbd0b8a4a23d/test.jpeg'
                ),
                'nsfwLevel': 'None',  # Add required field
                'meta': {
                    'prompt': 'test prompt',
                    'sampler': 'DPM++ 2M',
                },
            }
        ]

        with (
            patch('civitai_manager_libs.civitai_gallery_action.get_image_page') as mock_get_page,
            patch.object(config_manager, 'get_setting') as mock_get_setting,
        ):
            # Configure the mock to return appropriate values for different settings
            def mock_setting_values(key, default=None):
                setting_values = {
                    'NSFW_filtering_enable': True,
                    'NSFW_level_user': 'None',
                }
                return setting_values.get(key, default)

            mock_get_setting.side_effect = mock_setting_values
            mock_get_page.return_value = mock_image_data

            # Call get_user_gallery
            images_url, images_list = civitai_gallery_action.get_user_gallery(
                'test_model', 'test_url', False
            )

            # Verify metadata was stored
            assert (
                'c065d13f-38b3-4cad-90e3-dbd0b8a4a23d'
                in civitai_gallery_action._current_page_metadata
            )
            stored_meta = civitai_gallery_action._current_page_metadata[
                'c065d13f-38b3-4cad-90e3-dbd0b8a4a23d'
            ]
            assert stored_meta['meta']['prompt'] == 'test prompt'
            assert stored_meta['meta']['sampler'] == 'DPM++ 2M'
