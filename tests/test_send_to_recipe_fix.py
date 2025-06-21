"""Test for Send To Recipe prompt extraction functionality."""

import unittest
from unittest.mock import patch
import tempfile
import os
from PIL import Image
from PIL.PngImagePlugin import PngInfo

from scripts.civitai_manager_libs import recipe_action


class TestSendToRecipePromptExtraction(unittest.TestCase):
    """Test Send To Recipe prompt extraction functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_prompt = "beautiful landscape, detailed, masterpiece"
        self.test_negative = "blurry, low quality, worst quality"
        self.test_parameters = "Steps: 20, Sampler: Euler a, CFG scale: 7.0"

        # Create test image with metadata
        self.test_image_path = self._create_test_image_with_metadata()

    def tearDown(self):
        """Clean up test fixtures."""
        if hasattr(self, 'test_image_path') and os.path.exists(self.test_image_path):
            os.unlink(self.test_image_path)

    def _create_test_image_with_metadata(self):
        """Create a test image with PNG metadata."""
        # Create a temporary PNG file with metadata
        temp_fd, temp_path = tempfile.mkstemp(suffix='.png')
        os.close(temp_fd)

        # Create image with metadata
        img = Image.new('RGB', (512, 512), color='white')
        pnginfo = PngInfo()

        # Add generation parameters in the format expected by the system
        full_params = f"""{self.test_prompt}
Negative prompt: {self.test_negative}
{self.test_parameters}"""

        pnginfo.add_text("parameters", full_params)
        img.save(temp_path, pnginfo=pnginfo)

        return temp_path

    @patch('scripts.civitai_manager_libs.recipe_action.setting')
    def test_on_recipe_input_change_triggers_metadata_extraction(self, mock_setting):
        """Test that on_recipe_input_change properly triggers metadata extraction."""
        # Mock setting functions
        mock_setting.get_imagefn_and_shortcutid_from_recipe_image.return_value = (
            "test_id",
            self.test_image_path,
        )
        mock_setting.PLACEHOLDER = "PLACEHOLDER"
        mock_setting.NEWRECIPE = "New Recipe"

        # Mock recipe module
        with patch('scripts.civitai_manager_libs.recipe_action.recipe') as mock_recipe:
            mock_recipe.get_classifications.return_value = ["test_class"]

            # Call the function
            result = recipe_action.on_recipe_input_change("test_recipe_input", None)

            # Verify the result structure
            self.assertEqual(len(result), 18)  # Check expected number of outputs

            # Verify that recipe_generate_data (4th element) gets the image path
            # This should trigger metadata extraction
            recipe_generate_data_value = result[3]
            self.assertEqual(recipe_generate_data_value, self.test_image_path)

    def test_on_recipe_generate_data_change_extracts_prompts(self):
        """Test that on_recipe_generate_data_change correctly extracts prompts from image."""
        # Test the metadata extraction function directly
        result = recipe_action.on_recipe_generate_data_change(self.test_image_path)

        # Should return 4 gradio updates: prompt, negative, options, output
        self.assertEqual(len(result), 4)

        # Extract the values from the gradio updates
        prompt_update = result[0]
        negative_update = result[1]
        # options_update = result[2]  # Not used in this test
        # output_update = result[3]   # Not used in this test

        # Verify that prompts were extracted
        self.assertIn('value', prompt_update)
        self.assertIn('value', negative_update)

        # The extracted prompt should contain our test data
        extracted_prompt = prompt_update['value']
        extracted_negative = negative_update['value']

        self.assertIsNotNone(extracted_prompt)
        self.assertIsNotNone(extracted_negative)

        # Should contain the test prompt content
        self.assertIn("beautiful landscape", extracted_prompt)
        self.assertIn("blurry", extracted_negative)

    @patch('scripts.civitai_manager_libs.recipe_action.setting')
    def test_send_to_recipe_complete_workflow(self, mock_setting):
        """Test the complete Send To Recipe workflow."""
        # Mock setting functions
        mock_setting.get_imagefn_and_shortcutid_from_recipe_image.return_value = (
            "test_id",
            self.test_image_path,
        )
        mock_setting.PLACEHOLDER = "PLACEHOLDER"
        mock_setting.NEWRECIPE = "New Recipe"

        with patch('scripts.civitai_manager_libs.recipe_action.recipe') as mock_recipe:
            mock_recipe.get_classifications.return_value = ["test_class"]

            # Step 1: Simulate recipe_input.change
            input_result = recipe_action.on_recipe_input_change("test_recipe_input", None)

            # Step 2: Extract the image path that should be passed to recipe_generate_data
            recipe_image_for_metadata = input_result[3]

            # Step 3: Simulate recipe_generate_data.change
            metadata_result = recipe_action.on_recipe_generate_data_change(
                recipe_image_for_metadata
            )

            # Verify that metadata extraction worked
            self.assertEqual(len(metadata_result), 4)

            # Check that prompts were extracted
            prompt_update = metadata_result[0]
            negative_update = metadata_result[1]

            self.assertIn('value', prompt_update)
            self.assertIn('value', negative_update)

            # Verify content
            extracted_prompt = prompt_update['value']
            extracted_negative = negative_update['value']

            self.assertIsNotNone(extracted_prompt)
            self.assertIsNotNone(extracted_negative)
            self.assertIn("beautiful landscape", extracted_prompt)


if __name__ == '__main__':
    unittest.main()
