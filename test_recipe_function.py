#!/usr/bin/env python3
"""
Simple test to verify recipe gallery selection works correctly.
"""

import os
import sys
import json

# Add the scripts directory to the path
sys.path.insert(0, '/workspaces/civitai-shortcut/scripts')

# Set up test environment
os.chdir('/workspaces/civitai-shortcut')

def test_recipe_gallery_function():
    """Test the recipe gallery select function directly."""
    print("=== Testing RecipeUtilities.get_recipe_information ===")
    
    # Import the required modules
    from scripts.civitai_manager_libs.recipe_actions.recipe_utilities import RecipeUtilities
    
    # Test with a known recipe (using the first one from the data file)
    data_file = '/workspaces/civitai-shortcut/data_sc/CivitaiShortCutRecipeCollection.json'
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            recipes = json.load(f)
        
        if recipes:
            recipe_name = list(recipes.keys())[0]
            print(f"Testing with recipe: {recipe_name}")
            
            # Test get_recipe_information
            result = RecipeUtilities.get_recipe_information(recipe_name)
            description, prompt, negativePrompt, options, gen_string, classification, imagefile = result
            
            print(f"Result:")
            print(f"  description: {description}")
            print(f"  prompt: {prompt[:100] if prompt else None}...")
            print(f"  negativePrompt: {negativePrompt[:50] if negativePrompt else None}...")
            print(f"  options: {options[:50] if options else None}...")
            print(f"  classification: {classification}")
            print(f"  imagefile: {imagefile}")
            
            if prompt:
                print("✓ Recipe information retrieved successfully")
                return True
            else:
                print("✗ No prompt found in recipe")
                return False
    else:
        print("✗ Recipe data file not found")
        return False

if __name__ == "__main__":
    print("Recipe Functionality Test")
    print("=" * 40)
    
    success = test_recipe_gallery_function()
    
    print("\n" + "=" * 40)
    if success:
        print("✓ Test passed: Recipe functionality works correctly")
    else:
        print("✗ Test failed: Recipe functionality has issues")
