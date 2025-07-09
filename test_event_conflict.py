#!/usr/bin/env python3
"""
Test script to investigate recipe_input and recipe_gallery event conflicts.
This script simulates the event flow to identify potential conflicts.
"""

import os
import sys
import json

# Add the scripts directory to the path
sys.path.insert(0, '/workspaces/civitai-shortcut/scripts')


class MockGradioUpdate:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        
    def __repr__(self):
        return f"gr.update({self.kwargs})"


class MockSelectData:
    def __init__(self, value, index=0):
        self.value = value
        self.index = index


class MockGradio:
    @staticmethod
    def update(**kwargs):
        return MockGradioUpdate(**kwargs)
    
    SelectData = MockSelectData


# Monkey patch gradio
sys.modules['gradio'] = MockGradio
import gradio as gr

# Set up test environment
os.chdir('/workspaces/civitai-shortcut')

def test_recipe_gallery_select_event():
    """Test recipe gallery select event in isolation."""
    print("=== Testing recipe_gallery.select event ===")
    
    # Import the required modules
    from scripts.civitai_manager_libs.recipe_actions.recipe_gallery import RecipeGallery
    from scripts.civitai_manager_libs.logging_config import get_logger
    
    # Set up logger to debug level
    logger = get_logger('test')
    logger.setLevel(10)  # DEBUG level
    
    gallery = RecipeGallery()
    
    # Test with a known recipe (using the first one from the data file)
    data_file = '/workspaces/civitai-shortcut/data_sc/CivitaiShortCutRecipeCollection.json'
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            recipes = json.load(f)
        
        if recipes:
            recipe_name = list(recipes.keys())[0]
            print(f"Testing with recipe: {recipe_name}")
            
            # Create a mock SelectData event
            evt = gr.SelectData(value=recipe_name)
            
            # Call the event handler
            print("Calling on_recipe_gallery_select...")
            result = gallery.on_recipe_gallery_select(evt)
            
            print(f"Result type: {type(result)}")
            print(f"Result length: {len(result)}")
            print("Result components:")
            for i, component in enumerate(result):
                if hasattr(component, 'kwargs') and 'value' in component.kwargs:
                    value = component.kwargs['value']
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:50] + "..."
                    print(f"  [{i}]: {value}")
                else:
                    print(f"  [{i}]: {component}")
            
            # Check the recipe_prompt component (index 3)
            if len(result) > 3:
                prompt_update = result[3]
                if hasattr(prompt_update, 'kwargs') and 'value' in prompt_update.kwargs:
                    prompt_value = prompt_update.kwargs['value']
                    print(f"\nrecipe_prompt value: {prompt_value}")
                    if prompt_value:
                        print("✓ recipe_prompt has content")
                    else:
                        print("✗ recipe_prompt is empty")
                else:
                    print("✗ recipe_prompt update format unexpected")
    else:
        print("Recipe data file not found")

def test_recipe_input_change_event():
    """Test recipe_input change event in isolation."""
    print("\n=== Testing recipe_input.change event ===")
    
    from scripts.civitai_manager_libs.recipe_actions.recipe_browser import RecipeBrowser
    
    browser = RecipeBrowser()
    
    # Test with empty string (should not change anything)
    print("Testing with empty string...")
    result = browser.on_recipe_input_change("", [])
    print(f"Empty string result length: {len(result)}")
    
    # Test with a sample input
    print("Testing with sample recipe input...")
    result = browser.on_recipe_input_change("test_recipe", [])
    print(f"Sample input result length: {len(result)}")
    
    # Check the recipe_prompt component (index 8)
    if len(result) > 8:
        prompt_update = result[8]
        if hasattr(prompt_update, 'kwargs') and 'value' in prompt_update.kwargs:
            prompt_value = prompt_update.kwargs['value']
            print(f"recipe_prompt value from recipe_input.change: {prompt_value}")

def test_event_sequence():
    """Test the sequence of events that might occur."""
    print("\n=== Testing event sequence ===")
    
    # Simulate: user clicks recipe gallery -> recipe_gallery.select fires
    print("1. Simulating recipe_gallery.select...")
    test_recipe_gallery_select_event()
    
    # Simulate: some other action triggers recipe_input.change
    print("2. Simulating recipe_input.change with empty value...")
    test_recipe_input_change_event()

if __name__ == "__main__":
    print("Event Conflict Investigation")
    print("=" * 40)
    
    test_recipe_gallery_select_event()
    test_recipe_input_change_event()
    test_event_sequence()
    
    print("\n" + "=" * 40)
    print("Investigation complete")
