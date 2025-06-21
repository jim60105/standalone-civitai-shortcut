#!/usr/bin/env python3
"""
Debug script to test the Send To Recipe flow end-to-end
"""

import sys
import os

# Add the scripts directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))


def test_parse_data():
    """Test the parse_data function directly"""
    print("\n=== Testing parse_data function ===")

    from scripts.civitai_manager_libs import prompt

    # Test case 1: With "Prompt:" prefix
    test_data_1 = """Prompt: Best quality, masterpiece, ultra high res, (photorealistic:1.4), girl, beautiful_face, detailed skin, upper body, <lora:caise2-000022:0.6>
Negative prompt: ng_deepnegative_v1_75t, badhandv4 (worst quality:2), (low quality:2), (normal quality:2), lowres, bad anatomy, bad hands, normal quality, ((monochrome)), ((grayscale))
Steps: 28, Sampler: DPM++ 2M Karras, CFG scale: 11, Seed: 2508416159, Size: 640x384, Model hash: 7af26c6c98, Model: 真人_xsmix_V04很好看, Denoising strength: 0.53, Hires upscale: 2, Hires steps: 20, Hires upscaler: 4x-UltraSharp, Dynamic thresholding enabled: True, Mimic scale: 7, Threshold percentile: 100"""

    print("\nTest 1: With 'Prompt:' prefix")
    print(f"Input: {repr(test_data_1)}")
    result_1 = prompt.parse_data(test_data_1)
    print(f"Result: {result_1}")

    # Test case 2: Without "Prompt:" prefix
    test_data_2 = """Best quality, masterpiece, ultra high res, (photorealistic:1.4), girl, beautiful_face, detailed skin, upper body, <lora:caise2-000022:0.6>
Negative prompt: ng_deepnegative_v1_75t, badhandv4 (worst quality:2), (low quality:2), (normal quality:2), lowres, bad anatomy, bad hands, normal quality, ((monochrome)), ((grayscale))
Steps: 28, Sampler: DPM++ 2M Karras, CFG scale: 11, Seed: 2508416159, Size: 640x384, Model hash: 7af26c6c98, Model: 真人_xsmix_V04很好看, Denoising strength: 0.53, Hires upscale: 2, Hires steps: 20, Hires upscaler: 4x-UltraSharp, Dynamic thresholding enabled: True, Mimic scale: 7, Threshold percentile: 100"""

    print("\nTest 2: Without 'Prompt:' prefix")
    print(f"Input: {repr(test_data_2)}")
    result_2 = prompt.parse_data(test_data_2)
    print(f"Result: {result_2}")

    return result_1, result_2


def test_analyze_prompt():
    """Test the analyze_prompt function"""
    print("\n=== Testing analyze_prompt function ===")

    from scripts.civitai_manager_libs import recipe_action

    # Test with "Prompt:" prefix
    test_data = """Prompt: Best quality, masterpiece, ultra high res, (photorealistic:1.4), girl, beautiful_face, detailed skin, upper body, <lora:caise2-000022:0.6>
Negative prompt: ng_deepnegative_v1_75t, badhandv4 (worst quality:2), (low quality:2), (normal quality:2), lowres, bad anatomy, bad hands, normal quality, ((monochrome)), ((grayscale))
Steps: 28, Sampler: DPM++ 2M Karras, CFG scale: 11, Seed: 2508416159, Size: 640x384, Model hash: 7af26c6c98, Model: 真人_xsmix_V04很好看, Denoising strength: 0.53, Hires upscale: 2, Hires steps: 20, Hires upscaler: 4x-UltraSharp, Dynamic thresholding enabled: True, Mimic scale: 7, Threshold percentile: 100"""

    print(f"Input: {repr(test_data)}")
    result = recipe_action.analyze_prompt(test_data)
    print(f"Result: {result}")

    return result


def test_on_recipe_input_change():
    """Test the on_recipe_input_change function"""
    print("\n=== Testing on_recipe_input_change function ===")

    from scripts.civitai_manager_libs import recipe_action

    # Test with combined data (as sent from send_to_recipe_click)
    test_recipe_input = """12345:test_image.png
Prompt: Best quality, masterpiece, ultra high res, (photorealistic:1.4), girl, beautiful_face, detailed skin, upper body, <lora:caise2-000022:0.6>
Negative prompt: ng_deepnegative_v1_75t, badhandv4 (worst quality:2), (low quality:2), (normal quality:2), lowres, bad anatomy, bad hands, normal quality, ((monochrome)), ((grayscale))
Steps: 28, Sampler: DPM++ 2M Karras, CFG scale: 11, Seed: 2508416159, Size: 640x384, Model hash: 7af26c6c98, Model: 真人_xsmix_V04很好看, Denoising strength: 0.53, Hires upscale: 2, Hires steps: 20, Hires upscaler: 4x-UltraSharp, Dynamic thresholding enabled: True, Mimic scale: 7, Threshold percentile: 100"""

    print(f"Input: {repr(test_recipe_input)}")
    result = recipe_action.on_recipe_input_change(test_recipe_input, None)
    print(f"Number of returned values: {len(result) if result else 0}")

    if result and len(result) >= 12:
        print(f"Positive prompt (index 8): {result[8]}")
        print(f"Negative prompt (index 9): {result[9]}")
        print(f"Options (index 10): {result[10]}")
        print(f"Recipe output (index 11): {result[11]}")

    return result


def main():
    """Main test function"""
    print("Starting Send To Recipe Debug Tests...")

    try:
        # Test parse_data
        parse_results = test_parse_data()

        # Test analyze_prompt
        analyze_result = test_analyze_prompt()

        # Test on_recipe_input_change
        recipe_result = test_on_recipe_input_change()

        print("\n=== Summary ===")
        print("All tests completed. Check the debug output above.")

        # Verify that both test cases produce the same positive prompt
        if parse_results and len(parse_results) >= 2:
            result_1, result_2 = parse_results
            if result_1.get('prompt') == result_2.get('prompt'):
                print("✅ Both prefixed and non-prefixed prompts produce the same result")
            else:
                print("❌ Prefixed and non-prefixed prompts produce different results")
                print(f"  Prefixed: {repr(result_1.get('prompt'))}")
                print(f"  Non-prefixed: {repr(result_2.get('prompt'))}")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
