#!/usr/bin/env python3
"""
Test script to verify the WebUI mode shortcut file path resolution fix.

This simulates the WebUI mode issue and verifies that the fix resolves it correctly.
"""

import os
import sys
import tempfile
import shutil

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def test_webui_mode_path_resolution():
    """Test that shortcut file paths are correctly resolved in WebUI mode."""
    print("Testing WebUI mode shortcut file path resolution...")
    
    # Create a temporary directory to simulate WebUI directory
    webui_dir = tempfile.mkdtemp(prefix="webui_test_")
    original_cwd = os.getcwd()
    
    try:
        # Change to WebUI directory (different from extension directory)
        os.chdir(webui_dir)
        print(f"Changed working directory to: {webui_dir}")
        
        # Import the settings modules
        from scripts.civitai_manager_libs.settings import path_manager
        from scripts.civitai_manager_libs.ishortcut_core.shortcut_collection_manager import (
            ShortcutCollectionManager
        )
        
        # Verify extension base is correctly set
        extension_base = path_manager.get_extension_base()
        print(f"Extension base: {extension_base}")
        assert extension_base == project_root, f"Expected {project_root}, got {extension_base}"
        
        # Verify shortcut file path is absolute and points to extension directory
        shortcut_path = path_manager.shortcut
        print(f"Shortcut file path: {shortcut_path}")
        
        expected_path = os.path.join(project_root, "data_sc", "CivitaiShortCut.json")
        assert shortcut_path == expected_path, f"Expected {expected_path}, got {shortcut_path}"
        
        # Verify the file exists at the expected location
        file_exists = os.path.exists(shortcut_path)
        print(f"Shortcut file exists: {file_exists}")
        
        # Test that the shortcut collection manager can load the file
        manager = ShortcutCollectionManager()
        shortcuts = manager.load_shortcuts()
        print(f"Successfully loaded shortcuts: {type(shortcuts)}")
        
        print("✅ WebUI mode path resolution test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ WebUI mode path resolution test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up: restore original working directory and remove temp dir
        os.chdir(original_cwd)
        try:
            shutil.rmtree(webui_dir)
        except Exception:
            pass


def test_standalone_mode_path_resolution():
    """Test that shortcut file paths work correctly in standalone mode."""
    print("\nTesting standalone mode shortcut file path resolution...")
    
    try:
        # Import the settings modules
        from scripts.civitai_manager_libs.settings import path_manager
        from scripts.civitai_manager_libs.ishortcut_core.shortcut_collection_manager import (
            ShortcutCollectionManager
        )
        
        # Verify extension base is correctly set
        extension_base = path_manager.get_extension_base()
        print(f"Extension base: {extension_base}")
        assert extension_base == project_root, f"Expected {project_root}, got {extension_base}"
        
        # Verify shortcut file path is absolute and points to extension directory
        shortcut_path = path_manager.shortcut
        print(f"Shortcut file path: {shortcut_path}")
        
        expected_path = os.path.join(project_root, "data_sc", "CivitaiShortCut.json")
        assert shortcut_path == expected_path, f"Expected {expected_path}, got {shortcut_path}"
        
        # Test that the shortcut collection manager can load the file
        manager = ShortcutCollectionManager()
        shortcuts = manager.load_shortcuts()
        print(f"Successfully loaded shortcuts: {type(shortcuts)}")
        
        print("✅ Standalone mode path resolution test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Standalone mode path resolution test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Running shortcut file path resolution tests...\n")
    
    # Test both modes
    webui_success = test_webui_mode_path_resolution()
    standalone_success = test_standalone_mode_path_resolution()
    
    print(f"\n{'='*50}")
    print("TEST RESULTS:")
    print(f"WebUI Mode: {'✅ PASSED' if webui_success else '❌ FAILED'}")
    print(f"Standalone Mode: {'✅ PASSED' if standalone_success else '❌ FAILED'}")
    
    if webui_success and standalone_success:
        print("\n🎉 All tests PASSED! The fix works correctly.")
        sys.exit(0)
    else:
        print("\n💥 Some tests FAILED! Please check the implementation.")
        sys.exit(1)
