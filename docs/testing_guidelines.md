# Testing Guidelines

This document provides guidelines for testing the Civitai Shortcut compatibility layer.

## Overview

The compatibility layer requires comprehensive testing to ensure functionality works correctly across both WebUI and standalone modes. This document outlines testing strategies, requirements, and best practices.

## Test Categories & Structure

### Unit Tests

- Environment detection (auto, forced, cache, markers)
- Interface implementation (public methods, error/fallback, parameter validation, thread safety)
- Compatibility layer (creation, singleton, mode switching, property access)

### Integration Tests

- Cross-component (path/config, metadata/parameter, UI bridge/sampler)
- End-to-end (model download, parameter extraction, UI component binding)

### Environment-Specific Tests

- WebUI mode (mock modules, WebUI features, graceful degradation)
- Standalone mode (pure standalone, fallback, config management)


### Test Files & Coverage (2025/07/11)

| Test File                                   | Coverage Target | Description                                 |
|---------------------------------------------|-----------------|---------------------------------------------|
| test_environment_detector.py                | 100%            | Environment detection                       |
| test_compat_layer.py                       | 95%             | Core interfaces                             |
| test_adapters.py                           | 95%             | Path/config/metadata adapters               |
| test_module_compatibility.py                | 90%             | Module compatibility                        |
| test_integration.py                        | 85%             | Integration tests                           |
| test_ui_adapter.py                         | 85%             | UI bridge                                   |
| test_main.py, test_cli.py, ...              | -               | Other tests                                 |
| test_settings_categories.py                 | 95%+            | SettingCategories unit tests (SRP)          |
| test_settings_validator.py                  | 95%+            | SettingValidator unit tests (SRP)           |
| test_settings_persistence.py                | 95%+            | SettingPersistence unit tests (SRP)         |
| test_settings_config_manager.py             | 95%+            | ConfigManager unit tests (SRP)              |
| test_settings_model_utils.py                | 95%+            | Model utils unit tests (SRP)                |
| test_settings_path_manager.py               | 95%+            | Path manager unit tests (SRP)               |
| test_settings_initialization.py             | 95%+            | Initialization logic unit tests (SRP)       |

> **Note:**
> - settings 相關測試已依 Single Responsibility Principle (SRP) 完全拆分，原 monolithic `test_settings.py` 已刪除。
> - 各檔案覆蓋率均超過 95%，總覆蓋率 96%。
> - 測試命名、結構與維護建議詳見下方「測試維護最佳實踐」。

### Test Execution

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run all tests
pytest tests/ -v
# Run specific test modules
pytest tests/test_environment_detector.py -v
pytest tests/test_compat_layer.py -v
pytest tests/test_adapters.py -v
pytest tests/test_integration.py -v
# Run test coverage analysis
pytest --cov
# Run specific type of tests
pytest tests/test_integration.py::TestIntegration::test_full_webui_compatibility -v
pytest tests/test_integration.py::TestIntegration::test_full_standalone_functionality -v
```

## Test Requirements

### Coverage Requirements

- **Environment Detection**: 100% line coverage (implemented in `test_environment_detector.py`)
- **Core Interfaces**: 95% line coverage (implemented in `test_compat_layer.py`)
- **Path Management**: 95% line coverage (implemented in `test_adapters.py`)
- **Configuration Management**: 95% line coverage (implemented in `test_adapters.py`)
- **Metadata Processing**: 90% line coverage (implemented in `test_adapters.py`)
- **UI Bridge**: 85% line coverage (implemented in `test_ui_adapter.py`)
- **Module Compatibility**: 90% line coverage (implemented in `test_module_compatibility.py`)
- **Integration Tests**: 85% line coverage (implemented in `test_integration.py`)

### Performance Requirements

- Environment detection should complete in < 10ms
- Path operations should complete in < 5ms
- Configuration operations should complete in < 20ms
- Metadata extraction should complete in < 100ms per image
- Application startup should complete in < 3 seconds

### Reliability Requirements

- All tests must pass consistently
- No flaky tests (intermittent failures)
- Tests must be independent (no order dependencies)
- Tests must clean up after themselves

## Testing Infrastructure


### Test Structure (2025/07/11)

```
tests/
├── test_environment_detector.py           # ✅ Environment detection
├── test_compat_layer.py                  # ✅ Main compatibility layer
├── test_adapters.py                      # ✅ Adapter implementations
├── test_module_compatibility.py          # ✅ Module compatibility
├── test_integration.py                   # ✅ Integration tests
├── test_ui_adapter.py                    # ✅ UI bridge
├── test_main.py                          # ✅ Main program
├── test_cli.py                           # ✅ CLI functions
├── test_path_manager_verification.py      # ✅ Path manager verification
├── test_webui_function_simulation.py      # ✅ WebUI simulation
├── test_settings_categories.py            # ✅ SettingCategories (SRP)
├── test_settings_validator.py             # ✅ SettingValidator (SRP)
├── test_settings_persistence.py           # ✅ SettingPersistence (SRP)
├── test_settings_config_manager.py        # ✅ ConfigManager (SRP)
├── test_settings_model_utils.py           # ✅ Model utils (SRP)
├── test_settings_path_manager.py          # ✅ Path manager (SRP)
└── test_settings_initialization.py        # ✅ Initialization logic (SRP)
```

> **SRP 拆分說明：**
> - 每個 settings 子模組皆有獨立測試檔案，命名規則 `test_settings_<module>.py`。
> - 測試數量 114，全數通過，覆蓋率 96%。
## 測試維護最佳實踐（SRP 拆分後建議）

- **單一職責原則（SRP）**：每個測試檔案僅測一個邏輯模組，便於維護與擴充。
- **命名規範**：`test_settings_<module>.py`，對應 `scripts/civitai_manager_libs/settings/<module>.py`。
- **覆蓋率要求**：所有 settings 測試檔案目標覆蓋率 95% 以上。
- **測試獨立性**：每個測試用例獨立，使用 setUp/tearDown 管理狀態。
- **錯誤與邊界測試**：涵蓋異常、I/O、型別、配置錯誤等情境。
- **自動化驗證**：重構後務必執行 pytest + coverage，確保所有測試通過且覆蓋率達標。
- **文件同步**：每次大幅重構或新增測試時，務必同步更新本指引。

## Mocking Strategy

- Use unittest.mock for mocking WebUI modules and environment detection.
- Example:

```python
from unittest.mock import patch, MagicMock
from civitai_manager_libs.compat.environment_detector import EnvironmentDetector
from civitai_manager_libs.compat.compat_layer import get_compatibility_layer

@patch.dict('sys.modules', {'modules.scripts': MagicMock(), 'modules.shared': MagicMock()})
def test_webui_functionality():
    from civitai_manager_libs.compat.webui_adapters.webui_path_manager import WebUIPathManager
    assert WebUIPathManager().get_script_path() is not None

with patch.object(EnvironmentDetector, 'detect_environment', return_value='webui'):
    compat = get_compatibility_layer()
    assert compat.is_webui_mode()
```

## Test Best Practices

### 0. Public API Docstring Example

All public API functions must include a clear, concise English docstring following the [PEP 257](https://peps.python.org/pep-0257/) convention. This ensures that Intellisense and documentation tools provide helpful information to users and developers.

**Example:**

```python
def download_model(model_id: str, save_path: str, overwrite: bool = False) -> bool:
    """
    Download a model file from Civitai and save it to the specified path.

    Args:
        model_id (str): The unique identifier of the model to download.
        save_path (str): The local file path where the model will be saved.
        overwrite (bool, optional): Whether to overwrite the file if it already exists. Defaults to False.

    Returns:
        bool: True if the download succeeds, False otherwise.

    Raises:
        ValueError: If the model_id is invalid or save_path is not writable.
        NetworkError: If the download fails due to network issues.
    """
    # ...function implementation...
```

**Guidelines:**

- Always describe the function's purpose in the first line.
- List and describe all arguments and return values.
- Document possible exceptions.
- Use English for all docstrings and comments.

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

______________________________________________________________________

This comprehensive testing approach ensures the compatibility layer works reliably across all supported environments and use cases.
