from scripts.civitai_manager_libs.ishortcut_action import on_send_to_recipe_click as send_shortcut
from scripts.civitai_manager_libs.civitai_gallery_action import (
    on_send_to_recipe_click as send_gallery,
)
from scripts.civitai_manager_libs.recipe_action import on_recipe_input_change, analyze_prompt


def test_send_to_recipe_click_shortcut_with_metadata():
    model_id = "m1"
    img_file_info = "Prompt: A sample prompt\nNegative prompt: B sample negative\nSteps: 10"
    img_index = 0
    civitai_images = ["img1.png"]
    result = send_shortcut(model_id, img_file_info, img_index, civitai_images)
    # Expect image info header and metadata separated by newline
    assert isinstance(result, str)
    header, metadata = result.split("\n", 1)
    assert header == f"{model_id}:img1.png"
    assert metadata == img_file_info


def test_send_to_recipe_click_shortcut_without_metadata():
    model_id = "m2"
    img_file_info = ""
    img_index = 0
    civitai_images = ["img2.png"]
    result = send_shortcut(model_id, img_file_info, img_index, civitai_images)
    assert result == f"{model_id}:img2.png"


def test_send_to_recipe_click_gallery_with_metadata():
    model_id = "g1"
    img_file_info = "Prompt: Gallery prompt\nNegative prompt: Gallery negative\nSteps: 20"
    img_index = 1
    civitai_images = ["imgA.png", "imgB.png"]
    result = send_gallery(model_id, img_file_info, img_index, civitai_images)
    assert isinstance(result, str)
    header, metadata = result.split("\n", 1)
    assert header == f"{model_id}:imgB.png"
    assert metadata == img_file_info


def test_recipe_input_change_with_combined_data():
    # Prepare combined input: image info and metadata
    metadata = """
TestPrompt text
Negative prompt: TestNeg text
Steps: 5, Sampler: TestSampler
"""
    first_line = "scid123:sample_image.png"
    recipe_input = first_line + "\n" + metadata
    # Invoke recipe input change handler
    output = on_recipe_input_change(recipe_input, None)
    # output structure: [selected_name, drop_image, image, generate_data, input, …]
    # followed by prompt, negative, option, output, and remaining fields
    # Check image values
    drop_image = output[1]
    recipe_image = output[2]
    assert drop_image == "sample_image.png"
    assert recipe_image == "sample_image.png"
    # Check prompt fields are updated via analyze_prompt
    prompt_update = output[8]
    negative_update = output[9]
    option_update = output[10]
    output_update = output[11]
    # Ensure we got update dictionaries and correct values
    assert isinstance(prompt_update, dict) and "value" in prompt_update
    assert isinstance(negative_update, dict) and "value" in negative_update
    assert isinstance(option_update, dict) and "value" in option_update
    assert isinstance(output_update, dict) and "value" in output_update
    # Compare values: prompt fields from analyze_prompt, output raw metadata preserved
    ap, an, ao, ag = analyze_prompt(metadata)
    assert prompt_update["value"] == (ap or "")
    assert negative_update["value"] == (an or "")
    assert option_update["value"] == (ao or "")
    # recipe_output should contain the raw metadata string
    assert output_update["value"] == metadata


def test_recipe_input_change_with_prompt_prefix():
    """Test parsing data that includes 'Prompt:' prefix"""
    # Test data with "Prompt:" prefix - this format may come from certain sources
    metadata = """Prompt: Beautiful landscape, detailed, masterpiece
Negative prompt: blurry, low quality
Steps: 25, Sampler: DPM++ 2M Karras, CFG scale: 7"""

    first_line = "test_model:test_image.png"
    recipe_input = first_line + "\n" + metadata

    # Invoke recipe input change handler
    output = on_recipe_input_change(recipe_input, None)

    # Check prompt fields are updated correctly
    prompt_update = output[8]
    negative_update = output[9]
    option_update = output[10]

    # Verify the "Prompt:" prefix is correctly stripped
    assert prompt_update["value"] == "Beautiful landscape, detailed, masterpiece"
    assert negative_update["value"] == "blurry, low quality"
    assert "Steps:25" in option_update["value"]
    assert "Sampler:DPM++ 2M Karras" in option_update["value"]


def test_recipe_input_change_with_standard_format():
    """Test parsing standard SD format without 'Prompt:' prefix"""
    # Test standard format without "Prompt:" prefix
    metadata = """Beautiful landscape, detailed, masterpiece
Negative prompt: blurry, low quality
Steps: 25, Sampler: DPM++ 2M Karras, CFG scale: 7"""

    first_line = "test_model2:test_image2.png"
    recipe_input = first_line + "\n" + metadata

    # Invoke recipe input change handler
    output = on_recipe_input_change(recipe_input, None)

    # Check prompt fields are updated correctly
    prompt_update = output[8]
    negative_update = output[9]
    option_update = output[10]

    # Verify standard format is parsed correctly
    assert prompt_update["value"] == "Beautiful landscape, detailed, masterpiece"
    assert negative_update["value"] == "blurry, low quality"
    assert "Steps:25" in option_update["value"]
    assert "Sampler:DPM++ 2M Karras" in option_update["value"]
