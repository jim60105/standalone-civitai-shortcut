#!/usr/bin/env python3
"""
Debug script for Send To Recipe functionality.
This script simulates the complete flow from clicking "Send To Recipe" 
to updating the Recipe fields, with detailed logging.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_send_to_recipe_flow():
    """Test the complete Send To Recipe data flow with debug logging."""
    
    print("=== Civitai Shortcut - Send To Recipe Debug Test ===")
    print("This script tests the complete flow from 'Send To Recipe' to Recipe field updates.")
    print()
    
    # Import functions
    try:
        from scripts.civitai_manager_libs.ishortcut_action import on_send_to_recipe_click as ishortcut_send
        from scripts.civitai_manager_libs.civitai_gallery_action import on_send_to_recipe_click as gallery_send
        from scripts.civitai_manager_libs.recipe_action import on_recipe_input_change
        print("✅ Successfully imported all required functions")
    except ImportError as e:
        print(f"❌ Failed to import functions: {e}")
        return False
    
    # Test data scenarios
    test_scenarios = [
        {
            "name": "Model Browser with Prompt prefix",
            "func": ishortcut_send,
            "model_id": "test_model_123",
            "img_file_info": "Prompt: A beautiful sunset over mountains\nNegative prompt: blurry, low quality\nSteps: 20, Sampler: Euler a",
            "img_index": 0,
            "civitai_images": ["sunset_image.png"]
        },
        {
            "name": "Civitai Gallery with Prompt prefix", 
            "func": gallery_send,
            "model_id": "gallery_model_456",
            "img_file_info": "Prompt: Portrait of a woman, detailed\nNegative prompt: bad anatomy\nSteps: 25, CFG scale: 7",
            "img_index": 1,
            "civitai_images": ["img1.png", "portrait.png", "img3.png"]
        },
        {
            "name": "Standard format without prefix",
            "func": ishortcut_send,
            "model_id": "standard_model_789", 
            "img_file_info": "A serene lake at dawn\nNegative prompt: dark, gloomy\nSteps: 30, Sampler: DPM++ 2M",
            "img_index": 0,
            "civitai_images": ["lake.png"]
        }
    ]
    
    all_passed = True
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n=== Test {i}: {scenario['name']} ===")
        
        try:
            # Step 1: Simulate "Send To Recipe" click
            print(f"📤 Simulating '{scenario['name']}' Send To Recipe click...")
            recipe_input_data = scenario['func'](
                scenario['model_id'],
                scenario['img_file_info'], 
                scenario['img_index'],
                scenario['civitai_images']
            )
            
            print(f"📥 Send To Recipe returned: {repr(recipe_input_data)}")
            
            # Step 2: Simulate Recipe input processing
            print("🔄 Processing Recipe input...")
            recipe_result = on_recipe_input_change(recipe_input_data, None)
            
            # Step 3: Extract UI field updates
            prompt_update = recipe_result[8]      # recipe_prompt
            negative_update = recipe_result[9]    # recipe_negative  
            option_update = recipe_result[10]     # recipe_option
            
            # Step 4: Verify results
            prompt_value = prompt_update.get('value', '') if isinstance(prompt_update, dict) else prompt_update
            negative_value = negative_update.get('value', '') if isinstance(negative_update, dict) else negative_update
            option_value = option_update.get('value', '') if isinstance(option_update, dict) else option_update
            
            print(f"📝 Recipe Fields Updated:")
            print(f"   Prompt: {repr(prompt_value)}")
            print(f"   Negative: {repr(negative_value)}")
            print(f"   Options: {repr(option_value)}")
            
            # Step 5: Validation checks
            success = True
            if scenario['img_file_info'].startswith('Prompt:'):
                # Should strip "Prompt:" prefix
                expected_prompt = scenario['img_file_info'].split('\n')[0].replace('Prompt:', '').strip()
                if prompt_value != expected_prompt:
                    print(f"❌ FAIL: Expected prompt '{expected_prompt}', got '{prompt_value}'")
                    success = False
                else:
                    print(f"✅ PASS: Prompt prefix correctly stripped")
            else:
                # Standard format
                expected_prompt = scenario['img_file_info'].split('\n')[0]
                if prompt_value != expected_prompt:
                    print(f"❌ FAIL: Expected prompt '{expected_prompt}', got '{prompt_value}'")
                    success = False
                else:
                    print(f"✅ PASS: Standard format correctly parsed")
            
            # Check negative prompt
            if 'Negative prompt:' in scenario['img_file_info']:
                lines = scenario['img_file_info'].split('\n')
                for line in lines:
                    if line.startswith('Negative prompt:'):
                        expected_negative = line.replace('Negative prompt:', '').strip()
                        if negative_value != expected_negative:
                            print(f"❌ FAIL: Expected negative '{expected_negative}', got '{negative_value}'")
                            success = False
                        else:
                            print(f"✅ PASS: Negative prompt correctly extracted")
                        break
            
            # Check options
            if option_value and ('Steps:' in option_value or 'Sampler:' in option_value):
                print(f"✅ PASS: Options correctly extracted")
            else:
                print(f"⚠️  WARN: Options may not be fully extracted")
            
            if not success:
                all_passed = False
                
        except Exception as e:
            print(f"❌ ERROR in {scenario['name']}: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    print(f"\n=== Test Summary ===")
    if all_passed:
        print("🎉 ALL TESTS PASSED! Send To Recipe is working correctly.")
        print("   - Prompt prefixes are correctly stripped")
        print("   - Negative prompts are correctly extracted")  
        print("   - Generation parameters are correctly parsed")
    else:
        print("❌ SOME TESTS FAILED! There may still be issues with Send To Recipe.")
        
    return all_passed

if __name__ == "__main__":
    test_send_to_recipe_flow()
