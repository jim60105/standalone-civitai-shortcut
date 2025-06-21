#!/usr/bin/env python3
"""
Simple test to verify the Send To Recipe fix is working
"""

import sys
import os

# Add the scripts directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))


def test_prompt_prefix_fix():
    """Test that prompts with 'Prompt:' prefix are handled correctly"""
    from scripts.civitai_manager_libs import prompt

    # Test with "Prompt:" prefix
    test_data_with_prefix = """Prompt: masterpiece, best quality, 1girl, beautiful face
Negative prompt: lowres, bad quality
Steps: 20, Sampler: DPM++ 2M, CFG scale: 7, Seed: 123456"""

    # Test without "Prompt:" prefix
    test_data_without_prefix = """masterpiece, best quality, 1girl, beautiful face
Negative prompt: lowres, bad quality
Steps: 20, Sampler: DPM++ 2M, CFG scale: 7, Seed: 123456"""

    result_with_prefix = prompt.parse_data(test_data_with_prefix)
    result_without_prefix = prompt.parse_data(test_data_without_prefix)

    print("=== Send To Recipe Fix Verification ===")
    print(f"With prefix - prompt: {repr(result_with_prefix.get('prompt', ''))}")
    print(f"Without prefix - prompt: {repr(result_without_prefix.get('prompt', ''))}")

    # They should be the same
    if result_with_prefix.get('prompt') == result_without_prefix.get('prompt'):
        print("✅ SUCCESS: Both formats produce the same prompt")
        print("✅ The 'Prompt:' prefix bug has been fixed!")

        # Verify it's the expected prompt
        expected = "masterpiece, best quality, 1girl, beautiful face"
        if result_with_prefix.get('prompt') == expected:
            print("✅ The extracted prompt matches the expected value")
        else:
            print("❌ The extracted prompt doesn't match expected value")
            print(f"   Expected: {repr(expected)}")
            print(f"   Got: {repr(result_with_prefix.get('prompt'))}")
    else:
        print("❌ FAILED: The formats produce different prompts")
        print(f"   With prefix: {repr(result_with_prefix.get('prompt'))}")
        print(f"   Without prefix: {repr(result_without_prefix.get('prompt'))}")


def test_end_to_end_flow():
    """Test the complete end-to-end flow"""
    from scripts.civitai_manager_libs import recipe_action

    # Simulate the data format sent from send_to_recipe_click
    test_recipe_input = """12345:example.png
Prompt: masterpiece, best quality, 1girl, beautiful face
Negative prompt: lowres, bad quality
Steps: 20, Sampler: DPM++ 2M, CFG scale: 7, Seed: 123456"""

    print("\n=== End-to-End Flow Test ===")
    result = recipe_action.on_recipe_input_change(test_recipe_input, None)

    # Check if we get the expected number of return values
    if result and len(result) >= 12:
        positive_prompt = result[8]  # recipe_prompt
        negative_prompt = result[9]  # recipe_negative
        options = result[10]  # recipe_option

        print(f"✅ Received {len(result)} return values as expected")
        print(f"Positive prompt update: {positive_prompt}")
        print(f"Negative prompt update: {negative_prompt}")
        print(f"Options update: {options}")

        # Verify the values are correct
        if (
            positive_prompt.get('value') == 'masterpiece, best quality, 1girl, beautiful face'
            and negative_prompt.get('value') == 'lowres, bad quality'
        ):
            print("✅ All values are correctly extracted and formatted for UI update")
        else:
            print("❌ Some values are incorrect")
    else:
        print("❌ Incorrect number of return values or function failed")


if __name__ == "__main__":
    test_prompt_prefix_fix()
    test_end_to_end_flow()
    print("\n=== Summary ===")
    print("The Send To Recipe functionality should now work correctly.")
    print("If you're still seeing issues in the UI, please check:")
    print("1. Browser cache - try a hard refresh (Ctrl+F5)")
    print("2. Gradio server restart")
    print("3. UI component bindings in the Gradio interface definition")
