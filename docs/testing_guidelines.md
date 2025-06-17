# Testing Guidelines

This document provides guidelines for testing the Civitai Shortcut compatibility layer.

## Overview

The compatibility layer requires comprehensive testing to ensure functionality works correctly across both WebUI and standalone modes. This document outlines testing strategies, requirements, and best practices.

## Test Categories

### 1. Unit Tests
Test individual components in isolation.

#### Environment Detection Tests
- Test automatic environment detection
- Test forced environment modes
- Test caching behavior
- Test environment markers detection

#### Interface Implementation Tests
- Test all public methods of each adapter
- Test error handling and fallback behavior
- Test parameter validation
- Test thread safety where applicable

#### Compatibility Layer Tests
- Test component creation and initialization
- Test singleton behavior
- Test mode switching
- Test property access

### 2. Integration Tests
Test component interactions and workflows.

#### Cross-Component Tests
- Test path manager with config manager
- Test metadata processor with parameter processor
- Test UI bridge with sampler provider

#### End-to-End Workflows
- Test complete model download workflow
- Test parameter extraction and processing
- Test UI component creation and binding

### 3. Environment-Specific Tests
Test functionality in different execution environments.

#### WebUI Mode Tests
- Test with mock WebUI modules
- Test WebUI-specific functionality
- Test graceful degradation when WebUI features unavailable

#### Standalone Mode Tests
- Test pure standalone functionality
- Test fallback implementations
- Test configuration management

## Test Requirements

### Coverage Requirements
- **Environment Detection**: 100% line coverage
- **Core Interfaces**: 95% line coverage
- **Path Management**: 95% line coverage
- **Configuration Management**: 95% line coverage
- **Metadata Processing**: 90% line coverage
- **UI Bridge**: 85% line coverage (UI components are harder to test)

### Performance Requirements
- Environment detection should complete in < 10ms
- Path operations should complete in < 5ms
- Configuration operations should complete in < 20ms
- Metadata extraction should complete in < 100ms per image

### Reliability Requirements
- All tests must pass consistently
- No flaky tests (intermittent failures)
- Tests must be independent (no order dependencies)
- Tests must clean up after themselves

## Testing Infrastructure

### Test Structure
```
tests/
├── __init__.py
├── test_environment_detector.py      # Environment detection tests
├── test_compat_layer.py             # Main compatibility layer tests
├── test_adapters.py                 # Adapter implementation tests
├── test_integration.py              # Integration tests
├── fixtures/                       # Test data and fixtures
│   ├── sample_images/              # PNG files with metadata
│   ├── config_files/               # Sample configuration files
│   └── mock_webui/                 # Mock WebUI modules
└── utils/                          # Test utilities
    ├── mock_helpers.py             # Mock object helpers
    └── test_base.py                # Base test classes
```

### Test Data
- **Sample Images**: PNG files with various metadata formats
- **Configuration Files**: Valid and invalid configuration examples
- **Mock Data**: Simulated WebUI state and responses

## Running Tests

### Local Testing
```bash
# Run all tests
python -m unittest discover tests/

# Run specific test file
python -m unittest tests.test_environment_detector

# Run with coverage (requires coverage.py)
coverage run -m unittest discover tests/
coverage report -m
```

### Continuous Integration
Tests should be run automatically on:
- Pull requests
- Main branch commits
- Release preparations

### Test Environments
Tests should run in:
- Python 3.8+ environments
- With and without optional dependencies (PIL, gradio)
- Simulated WebUI and standalone environments

## Mocking Strategy

### WebUI Module Mocking
```python
import unittest
from unittest.mock import patch, MagicMock

class TestWebUIAdapter(unittest.TestCase):
    
    @patch.dict('sys.modules', {
        'modules.scripts': MagicMock(),
        'modules.shared': MagicMock(),
        'modules.extras': MagicMock()
    })
    def test_webui_functionality(self):
        # Test with mocked WebUI modules
        pass
```

### Environment Mocking
```python
from unittest.mock import patch
from civitai_manager_libs.compat import EnvironmentDetector

class TestEnvironmentSpecific(unittest.TestCase):
    
    def test_webui_mode(self):
        with patch.object(EnvironmentDetector, 'detect_environment', return_value='webui'):
            # Test WebUI-specific behavior
            pass
    
    def test_standalone_mode(self):
        with patch.object(EnvironmentDetector, 'detect_environment', return_value='standalone'):
            # Test standalone-specific behavior
            pass
```

## Test Best Practices

### 1. Test Independence
- Each test should be independent
- Use setUp() and tearDown() for test fixtures
- Reset global state between tests

### 2. Clear Test Names
```python
def test_detect_environment_with_webui_modules_available(self):
    """Test environment detection when WebUI modules are available."""
    pass

def test_config_save_with_invalid_path(self):
    """Test configuration save when path is invalid."""
    pass
```

### 3. Comprehensive Error Testing
```python
def test_extract_png_info_with_nonexistent_file(self):
    """Test PNG info extraction with non-existent file."""
    processor = StandaloneMetadataProcessor()
    result = processor.extract_png_info('/nonexistent/file.png')
    self.assertEqual(result, (None, None, None))

def test_config_load_with_corrupted_file(self):
    """Test configuration loading with corrupted JSON file."""
    # Create corrupted config file
    # Test graceful handling
    pass
```

### 4. Performance Testing
```python
import time
import unittest

class TestPerformance(unittest.TestCase):
    
    def test_environment_detection_performance(self):
        """Test that environment detection is fast."""
        start_time = time.time()
        EnvironmentDetector.detect_environment()
        end_time = time.time()
        
        self.assertLess(end_time - start_time, 0.01)  # < 10ms
```

### 5. Thread Safety Testing
```python
import threading
import unittest

class TestThreadSafety(unittest.TestCase):
    
    def test_concurrent_config_access(self):
        """Test concurrent access to configuration."""
        config = StandaloneConfigManager()
        results = []
        
        def worker():
            result = config.get_config('test_key', 'default')
            results.append(result)
        
        threads = [threading.Thread(target=worker) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # All results should be consistent
        self.assertEqual(len(set(results)), 1)
```

## Test Data Management

### Sample Images
Create PNG files with embedded metadata:
```python
from PIL import Image
from PIL.PngImagePlugin import PngInfo

def create_test_image_with_metadata():
    img = Image.new('RGB', (100, 100), color='red')
    metadata = PngInfo()
    metadata.add_text("parameters", "test prompt\nNegative prompt: bad\nSteps: 20, Sampler: Euler")
    img.save('test_image.png', pnginfo=metadata)
```

### Configuration Files
```json
{
  "valid_config.json": {
    "civitai_api_key": "test_key",
    "max_download_concurrent": 3,
    "nsfw_filter": false
  },
  "invalid_config.json": {
    "corrupted": "json content...
  }
}
```

## Error Scenarios to Test

### File System Errors
- Non-existent directories
- Permission denied errors
- Disk full conditions
- Network unavailable (for remote resources)

### Configuration Errors
- Missing configuration files
- Corrupted JSON files
- Invalid configuration values
- Version compatibility issues

### Environment Errors
- Missing optional dependencies
- Partial WebUI installations
- Version mismatches
- Import failures

### Data Errors
- Corrupted image files
- Invalid metadata formats
- Unsupported file types
- Empty or malformed parameter strings

## Debugging Tests

### Test Debugging
```python
import logging
import unittest

class TestWithDebug(unittest.TestCase):
    
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
    
    def test_with_detailed_logging(self):
        # Enable detailed logging for debugging
        pass
```

### Test Isolation
```python
import unittest
from civitai_manager_libs.compat import reset_compatibility_layer

class TestIsolated(unittest.TestCase):
    
    def setUp(self):
        reset_compatibility_layer()
    
    def tearDown(self):
        reset_compatibility_layer()
```

## Continuous Integration Integration

### GitHub Actions Example
```yaml
name: Test Compatibility Layer

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pillow  # Optional dependency
        # Don't install gradio to test standalone mode
    
    - name: Run tests
      run: |
        python -m unittest discover tests/
```

This comprehensive testing approach ensures the compatibility layer works reliably across all supported environments and use cases.
