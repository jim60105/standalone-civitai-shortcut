# Backlog 007: 測試和品質保證

## 優先級
**中 (Medium)** - 確保新實作功能的穩定性

## 估算工作量
**5-7 工作天**

## 目標描述
針對本計劃實作的新功能建立測試，確保獨立執行模式和相容性層的正確性。專注於測試本計劃新增的程式碼，不對既有的 Civitai Shortcut 功能撰寫測試。

## 接受標準 (Definition of Done)
1. ✅ 環境偵測機制測試完成
2. ✅ 相容性層功能測試完成
3. ✅ 獨立模式啟動測試完成
4. ✅ 雙模式切換驗證完成
5. ✅ 新增模組的單元測試完成
6. ✅ 基本整合測試通過
7. ✅ 跨平台啟動測試完成

## 詳細任務

### 任務 7.1: 測試環境建立
**預估時間：1 天**

1. **建立測試專案結構**（僅針對新功能）
   ```
   tests/
   ├── __init__.py
   ├── conftest.py                 # pytest 設定檔
   ├── requirements-test.txt       # 測試相依套件
   ├── new_features/               # 新功能測試
   │   ├── __init__.py
   │   ├── test_environment_detector.py
   │   ├── test_compat_layer.py
   │   ├── test_webui_mock.py
   │   ├── test_config_manager.py
   │   └── test_standalone_launcher.py
   ├── integration/                # 整合測試
   │   ├── __init__.py
   │   ├── test_mode_switching.py
   │   └── test_standalone_startup.py
   └── fixtures/                   # 測試資料
       ├── mock_responses/
       └── sample_configs/
   ```

2. **建立最小測試設定檔**
   ```python
   # tests/conftest.py
   
   import pytest
   import os
   import sys
   import tempfile
   from unittest.mock import Mock, patch
   
   # 添加專案根目錄到 Python 路徑
   sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
   
   @pytest.fixture
   def temp_dir():
       """臨時目錄"""
       temp_dir = tempfile.mkdtemp()
       yield temp_dir
       import shutil
       shutil.rmtree(temp_dir)
   
   @pytest.fixture
   def mock_webui_environment():
       """模擬 WebUI 環境"""
       with patch.dict('sys.modules', {
           'modules.scripts': Mock(),
           'modules.shared': Mock(),
           'modules.script_callbacks': Mock()
       }):
           yield
   ```

3. **測試相依套件設定**
   ```
   # tests/requirements-test.txt
   pytest>=7.0.0
   pytest-cov>=4.0.0
   pytest-mock>=3.10.0
   ```

### 任務 7.2: 新功能單元測試
**預估時間：3 天**

1. **環境偵測測試**
   ```python
   # tests/new_features/test_environment_detector.py
   
   import pytest
   from unittest.mock import patch, Mock
   
   def test_detect_webui_environment(mock_webui_environment):
       """測試 WebUI 環境偵測"""
       from environment_detector import detect_environment
       assert detect_environment() == 'webui'
   
   def test_detect_standalone_environment():
       """測試獨立環境偵測"""
       with patch.dict('sys.modules', {}):
           from environment_detector import detect_environment
           assert detect_environment() == 'standalone'
   ```

2. **相容性層測試**
   ```python
   # tests/new_features/test_compat_layer.py
   
   import pytest
   import tempfile
   import os
   from unittest.mock import Mock, patch
   
   def test_compat_layer_webui_mode(mock_webui_environment):
       """測試 WebUI 模式相容性層"""
       from compat_layer import CompatibilityLayer
       
       compat = CompatibilityLayer(mode='webui')
       assert compat.mode == 'webui'
       # 測試路徑取得等功能
   
   def test_compat_layer_standalone_mode(temp_dir):
       """測試獨立模式相容性層"""
       from compat_layer import CompatibilityLayer
       
       compat = CompatibilityLayer(mode='standalone')
       assert compat.mode == 'standalone'
       # 測試獨立模式功能
   ```

3. **WebUI 模擬功能測試**
   ```python
   # tests/new_features/test_webui_mock.py
   
   import pytest
   import os
   
   def test_mock_basedir():
       """測試基礎目錄模擬"""
       from webui_mock import mock_basedir
       result = mock_basedir()
       assert os.path.exists(result)
   
   def test_mock_run_pnginfo():
       """測試 PNG 資訊處理模擬"""
       from webui_mock import mock_run_pnginfo
       # 使用測試圖片進行測試
   ```

### 任務 7.3: 整合測試
**預估時間：2 天**

1. **模式切換測試**
   ```python
   # tests/integration/test_mode_switching.py
   
   import pytest
   from unittest.mock import patch
   
   def test_automatic_mode_detection():
       """測試自動模式偵測"""
       # 測試環境偵測和模式切換邏輯
       pass
   
   def test_manual_mode_setting():
       """測試手動模式設定"""
       # 測試手動指定模式的功能
       pass
   ```

2. **獨立模式啟動測試**
   ```python
   # tests/integration/test_standalone_startup.py
   
   import pytest
   
   def test_standalone_launcher_import():
       """測試獨立啟動器導入"""
       try:
           import main
           assert True
       except ImportError as e:
           pytest.fail(f"Failed to import standalone launcher: {e}")
   
   def test_gradio_interface_creation():
       """測試 Gradio 介面建立"""
       # 測試 UI 介面建立但不啟動伺服器
       pass
   ```

### 任務 7.4: 跨平台測試
**預估時間：1 天**

1. **啟動測試**
   - Windows 環境獨立模式啟動
   - Linux 環境獨立模式啟動
   - macOS 環境獨立模式啟動（如果可行）

2. **路徑處理測試**
   - 不同作業系統的路徑處理
   - 設定檔位置測試

## 測試執行指南

### 本地測試執行
```bash
# 安裝測試相依套件
uv pip install -r tests/requirements-test.txt

# 執行所有新功能測試
pytest tests/new_features/ -v

# 執行整合測試
pytest tests/integration/ -v

# 產生覆蓋率報告（僅針對新功能）
pytest tests/ --cov=environment_detector --cov=compat_layer --cov=webui_mock --cov=main -v
```

### 最小品質標準
1. 所有新功能單元測試通過
2. 基本整合測試通過
3. 至少一個平台的跨平台測試通過
4. 新增程式碼測試覆蓋率 > 70%

## 風險與限制
1. **範圍限制**：僅測試新實作功能，現有功能依賴其原有的品質保證
2. **平台限制**：可能無法在所有平台上進行完整測試
3. **環境相依**：某些測試可能需要特定的開發環境設定
