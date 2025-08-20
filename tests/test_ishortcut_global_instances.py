"""
Test for ishortcut_core module exports.

This test focuses on verifying that the required exports are properly defined
without triggering full module initialization that depends on settings.
"""

import ast


def test_fileprocessor_in_init_file():
    """Test that fileprocessor is properly defined in __init__.py."""
    init_file = 'scripts/civitai_manager_libs/ishortcut_core/__init__.py'
    with open(init_file, 'r') as f:
        content = f.read()
    
    # Test that fileprocessor is in the global assignments
    assert 'fileprocessor = _file_processor' in content, "fileprocessor global instance not assigned"
    
    # Test that _file_processor is in the initialization function  
    assert '_file_processor = FileProcessor()' in content, "_file_processor not initialized"
    
    # Test that fileprocessor is in __all__
    assert '"fileprocessor",' in content, "fileprocessor not in __all__ list"


def test_syntax_correctness():
    """Test that the modified __init__.py file has correct Python syntax."""
    init_file = 'scripts/civitai_manager_libs/ishortcut_core/__init__.py'
    with open(init_file, 'r') as f:
        content = f.read()
    
    # This will raise SyntaxError if the file has syntax errors
    ast.parse(content)


def test_civitai_shortcut_changes():
    """Test that civitai_shortcut.py has the correct method call pattern."""
    civitai_file = 'scripts/civitai_shortcut.py'
    with open(civitai_file, 'r') as f:
        content = f.read()
    
    # Check that the old incorrect call is gone
    assert 'ishortcut.fileprocessor.write_model_information(modelid, False, None)' not in content, \
        "Old incorrect method call still present"
    
    # Check that the new correct pattern is there (allowing for multi-line formatting)
    assert 'ishortcut.modelprocessor.get_model_information(' in content, \
        "New model info retrieval pattern not found"
    
    assert 'ishortcut.fileprocessor.write_model_information(model_info, modelid, False)' in content, \
        "New correct method call not found"


def test_file_processor_method_signature():
    """Test that FileProcessor.write_model_information has the expected signature."""
    # Test by parsing the file instead of importing to avoid initialization issues
    file_processor_file = 'scripts/civitai_manager_libs/ishortcut_core/file_processor.py'
    with open(file_processor_file, 'r') as f:
        content = f.read()
    
    # Look for the method definition line
    assert 'def write_model_information(' in content, "write_model_information method not found"
    assert 'model_info: Dict' in content, "model_info parameter missing or incorrect type"
    assert 'modelid: str' in content, "modelid parameter missing or incorrect type"
    assert 'register_only_information: bool' in content, "register_only_information parameter missing or incorrect type"