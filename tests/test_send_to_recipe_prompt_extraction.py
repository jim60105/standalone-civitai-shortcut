"""
Test cases for the Send To Recipe prompt extraction fix.

This module tests the parsing logic in prompt.py to ensure that
both Civitai format and standard PNG info format are correctly parsed.
"""

from scripts.civitai_manager_libs import prompt


class TestSendToRecipePromptExtraction:
    """Test the Send To Recipe prompt extraction fix."""

    def test_civitai_format_parsing(self):
        """Test parsing of Civitai format data with proper field extraction."""
        test_data = """Generated using example parameters from Civitai:

Prompt: (ultra_realistic:1.1), ((4K ULTRA HD)), crisp lines, woman with blue eyes
Negative prompt: bad quality, worst quality, low quality
Sampler: Euler a
CFG scale: 6
Steps: 30
Seed: 4294967297
Size: 832x1216"""

        result = prompt.parse_data(test_data)

        # Verify all components are extracted
        assert 'prompt' in result
        assert 'negativePrompt' in result
        assert 'options' in result

        # Check prompt extraction (should not include the title line)
        expected_prompt = (
            "(ultra_realistic:1.1), ((4K ULTRA HD)), crisp lines, woman with blue eyes"
        )
        assert result['prompt'] == expected_prompt

        # Check negative prompt extraction (should not include parameters)
        expected_negative = "bad quality, worst quality, low quality"
        assert result['negativePrompt'] == expected_negative

        # Check that all parameters are captured
        assert 'Sampler' in result['options']
        assert 'CFG scale' in result['options']
        assert 'Steps' in result['options']
        assert 'Seed' in result['options']
        assert 'Size' in result['options']

        assert result['options']['Sampler'] == 'Euler a'
        assert result['options']['CFG scale'] == '6'
        assert result['options']['Steps'] == '30'

    def test_standard_format_parsing(self):
        """Test parsing of standard PNG info format."""
        test_data = """Best quality, masterpiece, girl, beautiful face
Negative prompt: bad quality, normal quality, ((monochrome))
Steps: 28, Sampler: DPM++ 2M Karras, CFG scale: 11, Seed: 2508416159"""

        result = prompt.parse_data(test_data)

        # Verify all components are extracted
        assert 'prompt' in result
        assert 'negativePrompt' in result
        assert 'options' in result

        # Check prompt extraction
        expected_prompt = "Best quality, masterpiece, girl, beautiful face"
        assert result['prompt'] == expected_prompt

        # Check negative prompt extraction
        expected_negative = "bad quality, normal quality, ((monochrome))"
        assert result['negativePrompt'] == expected_negative

        # Check parameters
        assert 'Steps' in result['options']
        assert 'Sampler' in result['options']
        assert 'CFG scale' in result['options']
        assert 'Seed' in result['options']

    def test_prompt_only_format(self):
        """Test parsing when only prompt is present."""
        test_data = "Best quality, masterpiece, beautiful girl"

        result = prompt.parse_data(test_data)

        assert 'prompt' in result
        assert result['prompt'] == "Best quality, masterpiece, beautiful girl"
        assert 'negativePrompt' not in result or not result['negativePrompt']
        assert 'options' not in result or not result['options']

    def test_prompt_with_negative_only(self):
        """Test parsing when prompt and negative prompt are present but no parameters."""
        test_data = """Best quality, masterpiece
Negative prompt: bad quality, worst quality"""

        result = prompt.parse_data(test_data)

        assert 'prompt' in result
        assert 'negativePrompt' in result
        assert result['prompt'] == "Best quality, masterpiece"
        assert result['negativePrompt'] == "bad quality, worst quality"

    def test_parameters_only_format(self):
        """Test parsing when only parameters are present."""
        test_data = """Steps: 30, Sampler: Euler a, CFG scale: 7"""

        result = prompt.parse_data(test_data)

        assert 'options' in result
        assert 'Steps' in result['options']
        assert 'Sampler' in result['options']
        assert 'CFG scale' in result['options']

    def test_multiline_prompt(self):
        """Test parsing of multiline prompts."""
        test_data = """Prompt: First line of prompt,
second line of prompt
Negative prompt: bad quality
Steps: 30"""

        result = prompt.parse_data(test_data)

        assert 'prompt' in result
        expected_prompt = "First line of prompt, second line of prompt"
        assert result['prompt'] == expected_prompt

    def test_empty_input(self):
        """Test parsing of empty input."""
        result = prompt.parse_data("")
        assert result == {}

    def test_parse_option_data(self):
        """Test the parse_option_data function."""
        option_data = "Steps: 28, Sampler: DPM++ 2M Karras, CFG scale: 11, Seed: 2508416159"
        result = prompt.parse_option_data(option_data)

        expected = {
            'Steps': '28',
            'Sampler': 'DPM++ 2M Karras',
            'CFG scale': '11',
            'Seed': '2508416159',
        }

        assert result == expected

    def test_complex_civitai_format(self):
        """Test complex Civitai format with multiple parameters."""
        test_data = """Generated using example parameters from Civitai:

Prompt: masterpiece, best quality, 1girl, solo, long hair, beautiful eyes
Negative prompt: (worst quality:2), (low quality:2), bad anatomy, bad hands
Sampler: Euler a
CFG scale: 7.5
Steps: 30
Seed: 1234567890
Size: 768x1024
Model hash: abc123def
Denoising strength: 0.7
Hires upscale: 2
Hires steps: 15"""

        result = prompt.parse_data(test_data)

        # Verify basic components
        assert 'prompt' in result
        assert 'negativePrompt' in result
        assert 'options' in result

        # Check that complex parameters are captured
        assert 'Model hash' in result['options']
        assert 'Denoising strength' in result['options']
        assert 'Hires upscale' in result['options']
        assert 'Hires steps' in result['options']

        # Verify values
        assert result['options']['CFG scale'] == '7.5'
        assert result['options']['Model hash'] == 'abc123def'
        assert result['options']['Denoising strength'] == '0.7'

    def test_trailing_comma_removal(self):
        """Test that trailing commas are properly removed from negative prompts."""
        test_data = """Prompt: good quality
Negative prompt: bad quality, worst quality,
Steps: 30"""

        result = prompt.parse_data(test_data)

        # The trailing comma should be removed
        assert result['negativePrompt'] == "bad quality, worst quality"
