# Backlog Item 006: 整合測試與錯誤處理驗證

## 工作描述

對完成 HTTP 客戶端重構的所有模組進行全面的整合測試，驗證錯誤處理機制的正確性，並確保原有功能完全正常運作。

## 背景分析

經過前面 5 個工作項目的實作，我們已經：
1. 建立了中央化的 `CivitaiHttpClient`
2. 重構了 `civitai.py` 的 API 請求
3. 重構了 `civitai_gallery_action.py` 的圖片下載
4. 重構了 `downloader.py` 的檔案下載
5. 重構了 `ishortcut.py` 和 `scan_action.py` 的剩餘請求

現在需要進行全面的整合測試，確保所有組件能夠正確協作。

## 具體需求

### 1. 建立整合測試框架

#### 1.1 測試環境設定

**建立測試配置檔案 `tests/config/test_config.json`**：
```json
{
  "test_settings": {
    "mock_civitai_api": true,
    "test_timeout": 5,
    "test_retry_count": 2,
    "test_download_path": "tests/temp/downloads",
    "test_cache_path": "tests/temp/cache"
  },
  "mock_responses": {
    "model_info": {
      "id": 12345,
      "name": "Test Model",
      "description": "Test Description",
      "modelVersions": [
        {
          "id": 67890,
          "name": "Test Version",
          "images": [
            {
              "url": "https://example.com/test_image.jpg",
              "width": 512,
              "height": 512
            }
          ]
        }
      ]
    }
  }
}
```

#### 1.2 測試工具類別

**建立 `tests/utils/test_helpers.py`**：
```python
"""Test helper utilities for HTTP client integration tests."""

import os
import json
import tempfile
import shutil
from unittest.mock import Mock, patch
from typing import Dict, Any, Optional

class HTTPClientTestHelper:
    """Helper class for HTTP client integration tests."""
    
    def __init__(self):
        self.temp_dir = None
        self.mock_responses = {}
        self.setup_temp_environment()
    
    def setup_temp_environment(self):
        """Set up temporary test environment."""
        self.temp_dir = tempfile.mkdtemp(prefix="civitai_test_")
        
        # Create test directories
        os.makedirs(os.path.join(self.temp_dir, "downloads"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "cache"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "images"), exist_ok=True)
    
    def cleanup_temp_environment(self):
        """Clean up temporary test environment."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def mock_http_response(self, status_code: int = 200, 
                          json_data: Dict = None, 
                          headers: Dict = None,
                          content: bytes = None):
        """Create mock HTTP response."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.ok = status_code < 400
        mock_response.headers = headers or {}
        
        if json_data:
            mock_response.json.return_value = json_data
            mock_response.text = json.dumps(json_data)
        
        if content:
            mock_response.content = content
            mock_response.iter_content.return_value = [content[i:i+1024] for i in range(0, len(content), 1024)]
        
        return mock_response
    
    def simulate_network_error(self, error_type: str = "connection"):
        """Simulate different types of network errors."""
        import requests
        
        if error_type == "connection":
            return requests.exceptions.ConnectionError("Connection failed")
        elif error_type == "timeout":
            return requests.exceptions.Timeout("Request timeout")
        elif error_type == "http":
            return requests.exceptions.HTTPError("HTTP Error")
        else:
            return requests.exceptions.RequestException("Request failed")
```

### 2. API 請求整合測試

#### 2.1 civitai.py 模組整合測試

**建立 `tests/integration/test_civitai_integration.py`**：
```python
"""Integration tests for civitai.py module."""

import pytest
import json
from unittest.mock import patch, Mock
from tests.utils.test_helpers import HTTPClientTestHelper

class TestCivitaiIntegration:
    """Integration tests for civitai module."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = HTTPClientTestHelper()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup_temp_environment()
    
    @patch('civitai_manager_libs.civitai.requests.get')
    def test_get_model_info_success(self, mock_get):
        """Test successful model info retrieval."""
        # Arrange
        mock_response = self.helper.mock_http_response(
            status_code=200,
            json_data={"id": 12345, "name": "Test Model"}
        )
        mock_get.return_value.__enter__.return_value = mock_response
        
        # Act
        from civitai_manager_libs import civitai
        result = civitai.get_model_info("12345")
        
        # Assert
        assert result is not None
        assert result["id"] == 12345
        assert result["name"] == "Test Model"
    
    @patch('civitai_manager_libs.civitai.requests.get')
    def test_get_model_info_http_error(self, mock_get):
        """Test model info retrieval with HTTP error."""
        # Arrange
        mock_response = self.helper.mock_http_response(status_code=404)
        mock_get.return_value.__enter__.return_value = mock_response
        
        # Act
        from civitai_manager_libs import civitai
        result = civitai.get_model_info("99999")
        
        # Assert
        assert result is None
    
    @patch('civitai_manager_libs.civitai.requests.get')
    def test_get_model_info_network_error(self, mock_get):
        """Test model info retrieval with network error."""
        # Arrange
        mock_get.side_effect = self.helper.simulate_network_error("connection")
        
        # Act
        from civitai_manager_libs import civitai
        result = civitai.get_model_info("12345")
        
        # Assert
        assert result is None
    
    @patch('civitai_manager_libs.civitai.requests.get')
    def test_request_models_with_pagination(self, mock_get):
        """Test paginated model requests."""
        # Arrange
        mock_response = self.helper.mock_http_response(
            status_code=200,
            json_data={
                "items": [{"id": 1}, {"id": 2}],
                "metadata": {"nextPage": "next_url"}
            }
        )
        mock_get.return_value.__enter__.return_value = mock_response
        
        # Act
        from civitai_manager_libs import civitai
        result = civitai.request_models("test_url")
        
        # Assert
        assert result is not None
        assert "items" in result
        assert len(result["items"]) == 2
        assert "metadata" in result
```

#### 2.2 錯誤處理端到端測試

**建立 `tests/integration/test_error_handling.py`**：
```python
"""End-to-end error handling tests."""

import pytest
from unittest.mock import patch, Mock
import gradio as gr
from tests.utils.test_helpers import HTTPClientTestHelper

class TestErrorHandlingIntegration:
    """Test error handling across all modules."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = HTTPClientTestHelper()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup_temp_environment()
    
    @patch('civitai_manager_libs.http_client.requests.get')
    @patch('gradio.Error')
    def test_524_error_handling(self, mock_gradio_error, mock_get):
        """Test specific handling of 524 Cloudflare error."""
        # Arrange - Simulate 524 error
        mock_response = self.helper.mock_http_response(status_code=524)
        mock_get.return_value = mock_response
        
        # Act
        from civitai_manager_libs import civitai
        result = civitai.request_models("test_url")
        
        # Assert
        assert result is not None  # Should return empty structure, not None
        assert "items" in result
        assert result["items"] == []
        
        # Check that user-friendly error was shown
        mock_gradio_error.assert_called_once()
        error_message = mock_gradio_error.call_args[0][0]
        assert "連線超時" in error_message or "524" in error_message
    
    @patch('civitai_manager_libs.http_client.requests.get')
    @patch('gradio.Error')
    def test_timeout_error_handling(self, mock_gradio_error, mock_get):
        """Test timeout error handling."""
        # Arrange
        mock_get.side_effect = self.helper.simulate_network_error("timeout")
        
        # Act
        from civitai_manager_libs import civitai
        result = civitai.get_model_info("12345")
        
        # Assert
        assert result is None
        
        # Check that user-friendly error was shown
        mock_gradio_error.assert_called_once()
        error_message = mock_gradio_error.call_args[0][0]
        assert "超時" in error_message
    
    @patch('civitai_manager_libs.http_client.requests.get')
    def test_none_response_handling(self, mock_get):
        """Test handling of None responses to prevent TypeError."""
        # Arrange - Simulate scenario that previously caused TypeError
        mock_get.return_value = None
        
        # Act
        from civitai_manager_libs.civitai_gallery_action import get_paging_information_working
        result = get_paging_information_working("12345")
        
        # Assert - Should not raise TypeError
        assert result is not None
        assert "totalPages" in result
        assert result["totalPages"] == 0
```

### 3. 檔案下載整合測試

#### 3.1 大檔案下載測試

**建立 `tests/integration/test_file_download_integration.py`**：
```python
"""Integration tests for file download functionality."""

import pytest
import os
import tempfile
from unittest.mock import patch, Mock
from tests.utils.test_helpers import HTTPClientTestHelper

class TestFileDownloadIntegration:
    """Integration tests for file download."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = HTTPClientTestHelper()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup_temp_environment()
    
    @patch('civitai_manager_libs.http_client.requests.get')
    def test_large_file_download_with_resume(self, mock_get):
        """Test large file download with resume capability."""
        # Arrange
        test_content = b"test content" * 1000  # Simulate large file
        mock_response = self.helper.mock_http_response(
            status_code=200,
            content=test_content,
            headers={"Content-Length": str(len(test_content))}
        )
        mock_get.return_value = mock_response
        
        test_file = os.path.join(self.helper.temp_dir, "test_download.bin")
        
        # Act
        from civitai_manager_libs import downloader
        success = downloader.download_file("http://test.com/file", test_file)
        
        # Assert
        assert success is True
        assert os.path.exists(test_file)
        assert os.path.getsize(test_file) == len(test_content)
        
        with open(test_file, 'rb') as f:
            assert f.read() == test_content
    
    @patch('civitai_manager_libs.http_client.requests.get')
    def test_download_with_insufficient_space(self, mock_get):
        """Test download failure due to insufficient disk space."""
        # This test would need platform-specific implementation
        # to simulate disk space issues
        pass
    
    @patch('civitai_manager_libs.http_client.requests.get')
    def test_download_with_progress_callback(self, mock_get):
        """Test download with progress tracking."""
        # Arrange
        test_content = b"test" * 1000
        mock_response = self.helper.mock_http_response(
            status_code=200,
            content=test_content,
            headers={"Content-Length": str(len(test_content))}
        )
        mock_get.return_value = mock_response
        
        progress_calls = []
        
        def progress_callback(downloaded, total, speed):
            progress_calls.append((downloaded, total, speed))
        
        test_file = os.path.join(self.helper.temp_dir, "test_progress.bin")
        
        # Act
        from civitai_manager_libs import downloader
        success = downloader.download_file_gr("http://test.com/file", test_file, progress_callback)
        
        # Assert
        assert success is True
        assert len(progress_calls) > 0
        assert progress_calls[-1][0] == len(test_content)  # Final progress should be total size
```

### 4. 圖片下載整合測試

#### 4.1 圖片下載和快取測試

**建立 `tests/integration/test_image_download_integration.py`**：
```python
"""Integration tests for image download functionality."""

import pytest
import os
from unittest.mock import patch, Mock, MagicMock
from tests.utils.test_helpers import HTTPClientTestHelper

class TestImageDownloadIntegration:
    """Integration tests for image download."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = HTTPClientTestHelper()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup_temp_environment()
    
    @patch('civitai_manager_libs.http_client.requests.get')
    def test_preview_image_download(self, mock_get):
        """Test model preview image download."""
        # Arrange
        test_image_data = b"fake_image_data"
        mock_response = self.helper.mock_http_response(
            status_code=200,
            content=test_image_data,
            headers={"Content-Type": "image/jpeg"}
        )
        mock_get.return_value = mock_response
        
        model_info = {
            "id": 12345,
            "name": "Test Model",
            "modelVersions": [{
                "images": [{"url": "http://test.com/image.jpg"}]
            }]
        }
        
        # Act
        from civitai_manager_libs import ishortcut
        result = ishortcut.download_model_preview_image_by_model_info(model_info)
        
        # Assert
        assert result is not None
        assert os.path.exists(result)
        
        with open(result, 'rb') as f:
            assert f.read() == test_image_data
    
    @patch('civitai_manager_libs.http_client.requests.get')
    def test_gallery_image_batch_download(self, mock_get):
        """Test batch download of gallery images."""
        # Arrange
        test_urls = [
            "http://test.com/image1.jpg",
            "http://test.com/image2.jpg",
            "http://test.com/image3.jpg"
        ]
        
        mock_response = self.helper.mock_http_response(
            status_code=200,
            content=b"test_image_data",
            headers={"Content-Type": "image/jpeg"}
        )
        mock_get.return_value = mock_response
        
        # Act
        from civitai_manager_libs import civitai_gallery_action
        civitai_gallery_action.download_images(test_urls)
        
        # Assert
        mock_get.assert_called()
        assert mock_get.call_count == len(test_urls)
```

### 5. 效能和負載測試

#### 5.1 併發請求測試

**建立 `tests/integration/test_performance.py`**：
```python
"""Performance and load tests for HTTP client."""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch, Mock
from tests.utils.test_helpers import HTTPClientTestHelper

class TestPerformanceIntegration:
    """Performance tests for HTTP client."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = HTTPClientTestHelper()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup_temp_environment()
    
    @patch('civitai_manager_libs.http_client.requests.get')
    def test_concurrent_requests(self, mock_get):
        """Test concurrent HTTP requests."""
        # Arrange
        mock_response = self.helper.mock_http_response(
            status_code=200,
            json_data={"id": 12345, "name": "Test Model"}
        )
        mock_get.return_value = mock_response
        
        # Act
        from civitai_manager_libs import civitai
        
        def make_request(model_id):
            return civitai.get_model_info(str(model_id))
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        
        # Assert
        assert len(results) == 10
        assert all(result is not None for result in results)
        assert end_time - start_time < 5.0  # Should complete within 5 seconds
    
    def test_timeout_handling(self):
        """Test timeout handling under load."""
        # This test would simulate slow responses and verify timeout behavior
        pass
    
    def test_memory_usage(self):
        """Test memory usage during large downloads."""
        # This test would monitor memory usage during large file downloads
        pass
```

### 6. 回歸測試套件

#### 6.1 端到端功能測試

**建立 `tests/integration/test_end_to_end.py`**：
```python
"""End-to-end regression tests."""

import pytest
from unittest.mock import patch, Mock, MagicMock
from tests.utils.test_helpers import HTTPClientTestHelper

class TestEndToEndRegression:
    """End-to-end regression tests."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = HTTPClientTestHelper()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup_temp_environment()
    
    @patch('civitai_manager_libs.http_client.requests.get')
    def test_complete_model_workflow(self, mock_get):
        """Test complete model download workflow."""
        # Arrange
        model_response = self.helper.mock_http_response(
            status_code=200,
            json_data={
                "id": 12345,
                "name": "Test Model",
                "modelVersions": [{
                    "id": 67890,
                    "name": "v1.0",
                    "files": [{
                        "name": "model.safetensors",
                        "downloadUrl": "http://test.com/model.safetensors"
                    }],
                    "images": [{
                        "url": "http://test.com/preview.jpg"
                    }]
                }]
            }
        )
        
        file_response = self.helper.mock_http_response(
            status_code=200,
            content=b"fake_model_data",
            headers={"Content-Length": "15"}
        )
        
        image_response = self.helper.mock_http_response(
            status_code=200,
            content=b"fake_image_data",
            headers={"Content-Type": "image/jpeg"}
        )
        
        # Configure mock to return different responses based on URL
        def mock_get_side_effect(url, **kwargs):
            if "api/v1/models" in url:
                return model_response
            elif "model.safetensors" in url:
                return file_response
            elif "preview.jpg" in url:
                return image_response
            else:
                return self.helper.mock_http_response(status_code=404)
        
        mock_get.side_effect = mock_get_side_effect
        
        # Act & Assert
        # Test 1: Get model info
        from civitai_manager_libs import civitai
        model_info = civitai.get_model_info("12345")
        assert model_info is not None
        assert model_info["id"] == 12345
        
        # Test 2: Download preview image
        from civitai_manager_libs import ishortcut
        preview_path = ishortcut.download_model_preview_image_by_model_info(model_info)
        assert preview_path is not None
        
        # Test 3: Download model file
        from civitai_manager_libs import downloader
        model_file = os.path.join(self.helper.temp_dir, "model.safetensors")
        success = downloader.download_file("http://test.com/model.safetensors", model_file)
        assert success is True
        assert os.path.exists(model_file)
```

### 7. 測試自動化和 CI 整合

#### 7.1 測試執行腳本

**建立 `tests/run_integration_tests.py`**：
```python
"""Script to run integration tests with proper setup."""

import os
import sys
import pytest
import tempfile
import shutil

def setup_test_environment():
    """Set up test environment."""
    # Create temporary directories
    temp_base = tempfile.mkdtemp(prefix="civitai_integration_test_")
    
    # Set environment variables for testing
    os.environ["CIVITAI_TEST_MODE"] = "1"
    os.environ["CIVITAI_TEST_TEMP_DIR"] = temp_base
    
    return temp_base

def cleanup_test_environment(temp_base):
    """Clean up test environment."""
    if os.path.exists(temp_base):
        shutil.rmtree(temp_base)
    
    # Clean up environment variables
    os.environ.pop("CIVITAI_TEST_MODE", None)
    os.environ.pop("CIVITAI_TEST_TEMP_DIR", None)

def main():
    """Run integration tests."""
    temp_base = setup_test_environment()
    
    try:
        # Run tests
        test_args = [
            "tests/integration/",
            "-v",
            "--tb=short",
            "--durations=10"
        ]
        
        result = pytest.main(test_args)
        return result
        
    finally:
        cleanup_test_environment(temp_base)

if __name__ == "__main__":
    sys.exit(main())
```

## 驗收標準

### 1. 測試覆蓋率

- [ ] 所有重構的模組都有對應的整合測試
- [ ] 所有錯誤情況都有測試覆蓋
- [ ] 整合測試涵蓋率達到 80% 以上
- [ ] 所有測試都能穩定通過

### 2. 錯誤處理驗證

- [ ] 524 錯誤不再導致 TypeError
- [ ] 所有 HTTP 錯誤都有使用者友善的提示
- [ ] 網路錯誤不會導致程式崩潰
- [ ] 超時錯誤有適當的處理和提示

### 3. 功能完整性

- [ ] 所有原有功能都正常運作
- [ ] 下載功能正常且穩定
- [ ] 圖片顯示正常
- [ ] API 請求正常

### 4. 效能要求

- [ ] HTTP 請求響應時間合理
- [ ] 大檔案下載效能符合預期
- [ ] 記憶體使用量合理
- [ ] 併發請求處理正常

### 5. 使用者體驗

- [ ] 錯誤訊息清楚且有用
- [ ] 載入和下載有適當的進度指示
- [ ] 介面響應速度快
- [ ] 不會出現無法處理的錯誤

## 相關檔案

- **新建立**：`tests/integration/` 目錄下的所有測試檔案
- **新建立**：`tests/utils/test_helpers.py`
- **新建立**：`tests/config/test_config.json`
- **新建立**：`tests/run_integration_tests.py`
- **修改**：`pytest.ini`（如果需要）

## 後續工作

完成此項目後，將進行文件更新和使用者指南撰寫。
