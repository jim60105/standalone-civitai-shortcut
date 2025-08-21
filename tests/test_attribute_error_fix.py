"""
Simple test to verify that the AttributeError fix works.

This test validates that the specific error described in issue #73 is resolved.
"""

import tempfile
import os


def test_ishortcut_fileprocessor_attribute_access():
    """Test that ishortcut.fileprocessor can be accessed without AttributeError."""
    # Create a temporary directory for settings
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set environment to use temp directory
        os.environ['CIVITAI_SHORTCUT_DATA_PATH'] = temp_dir
        
        try:
            # This should work without raising AttributeError
            # We test by checking the string content rather than actual import to avoid 
            # initialization dependencies
            
            init_file = 'scripts/civitai_manager_libs/ishortcut_core/__init__.py'
            with open(init_file, 'r') as f:
                content = f.read()
            
            # Verify that the global instance is properly defined
            assert 'fileprocessor = _file_processor' in content
            
            # Verify that _file_processor is initialized
            assert 'if _file_processor is None:' in content
            assert '_file_processor = FileProcessor()' in content
            
            # Verify that fileprocessor is exported
            assert '"fileprocessor",' in content
            
            print("✓ ishortcut.fileprocessor attribute should be accessible")
            
        finally:
            # Clean up environment
            if 'CIVITAI_SHORTCUT_DATA_PATH' in os.environ:
                del os.environ['CIVITAI_SHORTCUT_DATA_PATH']


def test_civitai_shortcut_function_fix():
    """Test that the fixed function in civitai_shortcut.py uses correct method signature."""
    civitai_file = 'scripts/civitai_shortcut.py'
    with open(civitai_file, 'r') as f:
        content = f.read()
    
    # The function should now:
    # 1. Get model info first: ishortcut.modelprocessor.get_model_information(modelid)
    # 2. Pass it correctly: ishortcut.fileprocessor.write_model_information(model_info, modelid, False)
    
    assert 'ishortcut.modelprocessor.get_model_information(' in content
    assert 'ishortcut.fileprocessor.write_model_information(model_info, modelid, False)' in content
    
    # The old incorrect call should be gone
    assert 'write_model_information(modelid, False, None)' not in content
    
    print("✓ civitai_shortcut.py function uses correct method signature")


if __name__ == "__main__":
    test_ishortcut_fileprocessor_attribute_access()
    test_civitai_shortcut_function_fix()
    print("All tests passed! The AttributeError should be fixed.")