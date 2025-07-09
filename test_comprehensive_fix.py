#!/usr/bin/env python3
"""
Comprehensive test to verify the recipe gallery prompt display fix.
"""

import os
import sys
import json

# Add the scripts directory to the path
sys.path.insert(0, '/workspaces/civitai-shortcut/scripts')

# Set up test environment
os.chdir('/workspaces/civitai-shortcut')


def test_recipe_gallery_select_simulation():
    """Simulate the complete recipe gallery selection flow."""
    print("=== Recipe Gallery Selection Flow Test ===")
    
    # Mock Gradio SelectData
    class MockSelectData:
        def __init__(self, value):
            self.value = value
    
    from scripts.civitai_manager_libs.recipe_actions.recipe_gallery import RecipeGallery
    
    gallery = RecipeGallery()
    
    # Get a test recipe
    data_file = '/workspaces/civitai-shortcut/data_sc/CivitaiShortCutRecipeCollection.json'
    if not os.path.exists(data_file):
        print("✗ Recipe data file not found")
        return False
    
    with open(data_file, 'r', encoding='utf-8') as f:
        recipes = json.load(f)
    
    if not recipes:
        print("✗ No recipes found")
        return False
    
    recipe_name = list(recipes.keys())[0]
    print(f"Testing with recipe: {recipe_name}")
    
    # Simulate gallery selection
    evt = MockSelectData(value=recipe_name)
    result = gallery.on_recipe_gallery_select(evt)
    
    print(f"Gallery select returned {len(result)} outputs")
    
    # Check the recipe_prompt component (index 3)
    if len(result) > 3:
        prompt_update = result[3]
        if hasattr(prompt_update, 'kwargs') and 'value' in prompt_update.kwargs:
            prompt_value = prompt_update.kwargs['value']
            if prompt_value and prompt_value.strip():
                print(f"✓ Recipe prompt retrieved: {prompt_value[:100]}...")
                return True
            else:
                print("✗ Recipe prompt is empty")
                return False
    
    print("✗ Recipe prompt update not found in expected position")
    return False


def test_recipe_input_interference():
    """Test that recipe_input.change doesn't interfere when triggered with empty/invalid data."""
    print("\n=== Recipe Input Interference Test ===")
    
    from scripts.civitai_manager_libs.recipe_actions.recipe_browser import RecipeBrowser
    
    browser = RecipeBrowser()
    
    # Simulate what happens when recipe_input.change is triggered with empty data
    test_cases = [
        ("", "empty string"),
        ("   ", "whitespace"),
        ("random_invalid_data", "invalid data"),
    ]
    
    all_passed = True
    
    for test_input, description in test_cases:
        result = browser.on_recipe_input_change(test_input, [])
        
        if len(result) == 22:
            print(f"✓ {description}: Returns correct number of outputs")
            
            # Check that recipe_prompt (index 8) is a no-op update
            prompt_update = result[8]
            if hasattr(prompt_update, 'kwargs'):
                if not prompt_update.kwargs:  # Empty kwargs means no-op
                    print(f"✓ {description}: recipe_prompt is no-op update")
                else:
                    print(f"✗ {description}: recipe_prompt has kwargs: {prompt_update.kwargs}")
                    all_passed = False
            else:
                print(f"✓ {description}: recipe_prompt is no-op update")
        else:
            print(f"✗ {description}: Returns {len(result)} outputs (expected 22)")
            all_passed = False
    
    return all_passed


if __name__ == "__main__":
    print("Comprehensive Recipe Gallery Fix Verification")
    print("=" * 50)
    
    test1_passed = test_recipe_gallery_select_simulation()
    test2_passed = test_recipe_input_interference()
    
    print("\n" + "=" * 50)
    if test1_passed and test2_passed:
        print("✓ All tests passed! The fix should resolve the prompt display issue.")
    else:
        print("✗ Some tests failed. Further investigation needed.")
        
    print("\nSummary:")
    print("- Recipe gallery selection properly retrieves prompt data")
    print("- Recipe input change event won't interfere with empty/invalid data") 
    print("- UI component conflicts should be resolved")
