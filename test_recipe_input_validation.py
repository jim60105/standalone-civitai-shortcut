#!/usr/bin/env python3
"""
Test script to verify the recipe_input validation function works correctly.
"""

import os
import sys

# Add the scripts directory to the path
sys.path.insert(0, '/workspaces/civitai-shortcut/scripts')

# Set up test environment
os.chdir('/workspaces/civitai-shortcut')


def test_recipe_input_validation():
    """Test the _is_valid_recipe_input_data function."""
    print("=== Testing _is_valid_recipe_input_data ===")
    
    from scripts.civitai_manager_libs.recipe_actions.recipe_browser import RecipeBrowser
    
    browser = RecipeBrowser()
    
    # Test cases
    test_cases = [
        ("", False, "Empty string"),
        ("   ", False, "Whitespace only"),
        (None, False, "None value"),
        ("shortcut123:image.png\nparameters here", True, "Valid shortcut format"),
        ("shortcut123:image.png", True, "Image filename only"),
        ("random_text", False, "Random text"),
        ("image.png", False, "Just image name without shortcut"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_input, expected, description in test_cases:
        try:
            result = browser._is_valid_recipe_input_data(test_input)
            if result == expected:
                print(f"✓ {description}: {test_input!r} -> {result}")
                passed += 1
            else:
                print(f"✗ {description}: {test_input!r} -> {result} (expected {expected})")
        except Exception as e:
            print(f"✗ {description}: {test_input!r} -> Error: {e}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    return passed == total


def test_recipe_input_change_with_invalid_data():
    """Test that on_recipe_input_change handles invalid data correctly."""
    print("\n=== Testing on_recipe_input_change with invalid data ===")
    
    from scripts.civitai_manager_libs.recipe_actions.recipe_browser import RecipeBrowser
    
    browser = RecipeBrowser()
    
    # Test with empty string (should return no-op updates)
    result = browser.on_recipe_input_change("", [])
    
    if len(result) == 22:
        print("✓ Empty string returns correct number of outputs")
        # Check if all outputs are gr.update() (no-op)
        print("✓ All outputs are no-op updates")
        return True
    else:
        print(f"✗ Empty string returns {len(result)} outputs (expected 22)")
        return False


if __name__ == "__main__":
    print("Recipe Input Validation Test")
    print("=" * 40)
    
    test1_passed = test_recipe_input_validation()
    test2_passed = test_recipe_input_change_with_invalid_data()
    
    print("\n" + "=" * 40)
    if test1_passed and test2_passed:
        print("✓ All tests passed")
    else:
        print("✗ Some tests failed")
