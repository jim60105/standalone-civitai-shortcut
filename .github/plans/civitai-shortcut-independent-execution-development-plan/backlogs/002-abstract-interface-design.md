# Backlog 002: 抽象介面設計與相容性層架構

## 優先級
**高 (Critical)** - 核心架構設計，為整個雙模式系統奠定基礎

## 估算工作量
**6-10 工作天**

## 目標描述
根據相依性分析結果，設計並實作抽象介面系統，建立相容性層 (Compatibility Layer)，讓應用程式能夠在 AUTOMATIC1111 模式和獨立模式之間無縫切換。

## 接受標準 (Definition of Done)
1. ✅ 完成抽象介面設計文件
2. ✅ 建立 `CompatibilityLayer` 類別的完整實作
3. ✅ 實作環境偵測機制
4. ✅ 建立單元測試確保介面正確性
5. ✅ 提供使用範例和最佳實務文件
6. ✅ 通過兩種模式下的基本功能測試

## 詳細任務

### 任務 2.1: 抽象介面設計
**預估時間：3 天**

1. **設計核心抽象介面**
   根據 Backlog 001 的分析結果，設計以下核心介面：

   ```python
   # 介面設計範例
   class IPathManager:
       """路徑管理抽象介面"""
       def get_base_path(self) -> str:
           """取得應用程式基礎路徑"""
           pass
       
       def get_extension_path(self) -> str:
           """取得擴展程式路徑"""
           pass
       
       def get_models_path(self) -> str:
           """取得模型儲存路徑"""
           pass

   class IConfigManager:
       """設定管理抽象介面"""
       def get_config(self, key: str, default=None):
           """取得設定值"""
           pass
       
       def set_config(self, key: str, value):
           """設定值"""
           pass
       
       def save_config(self):
           """儲存設定"""
           pass
   ```

2. **設計介面規格文件**
   建立 `interface_specifications.md`，包含：
   - 每個介面的職責範圍
   - 方法簽名和參數說明
   - 回傳值規格
   - 例外處理規範
   - 執行緒安全性要求

### 任務 2.2: 環境偵測機制實作
**預估時間：2 天**

1. **建立環境偵測器**
   ```python
   # environment_detector.py
   class EnvironmentDetector:
       @staticmethod
       def detect_environment() -> str:
           """
           偵測當前執行環境
           
           Returns:
               'webui': 在 AUTOMATIC1111 環境中
               'standalone': 獨立執行環境
           """
           try:
               import modules.scripts
               # 嘗試存取 AUTOMATIC1111 特定功能
               modules.scripts.basedir()
               return 'webui'
           except (ImportError, AttributeError):
               return 'standalone'
       
       @staticmethod
       def is_webui_mode() -> bool:
           """檢查是否為 WebUI 模式"""
           return EnvironmentDetector.detect_environment() == 'webui'
       
       @staticmethod  
       def is_standalone_mode() -> bool:
           """檢查是否為獨立模式"""
           return EnvironmentDetector.detect_environment() == 'standalone'
   ```

2. **建立環境驗證機制**
   - 驗證環境偵測的準確性
   - 處理邊緣情況（部分相依性存在）
   - 提供環境資訊給除錯使用

### 任務 2.3: 相容性層核心實作
**預估時間：4 天**

1. **建立主要相容性層類別**
   ```python
   # compat_layer.py
   class CompatibilityLayer:
       def __init__(self, mode: str = None):
           if mode is None:
               from .environment_detector import EnvironmentDetector
               mode = EnvironmentDetector.detect_environment()
           
           self.mode = mode
           self._path_manager = self._create_path_manager()
           self._config_manager = self._create_config_manager()
           self._metadata_processor = self._create_metadata_processor()
           self._ui_bridge = self._create_ui_bridge()
       
       def _create_path_manager(self) -> IPathManager:
           if self.mode == 'webui':
               from .webui_path_manager import WebUIPathManager
               return WebUIPathManager()
           else:
               from .standalone_path_manager import StandalonePathManager
               return StandalonePathManager()
   ```

2. **實作 WebUI 模式處理器**
   ```python
   # webui_path_manager.py
   class WebUIPathManager(IPathManager):
       def get_base_path(self) -> str:
           from modules import scripts
           return scripts.basedir()
       
       def get_extension_path(self) -> str:
           return self.get_base_path()
       
       def get_models_path(self) -> str:
           from modules import shared
           return getattr(shared, 'models_path', './models')
   ```

3. **實作獨立模式處理器**
   ```python
   # standalone_path_manager.py  
   class StandalonePathManager(IPathManager):
       def __init__(self):
           self._base_path = os.path.dirname(os.path.abspath(__file__))
       
       def get_base_path(self) -> str:
           return self._base_path
       
       def get_extension_path(self) -> str:
           return self._base_path
       
       def get_models_path(self) -> str:
           return os.path.join(self._base_path, 'models')
   ```

### 任務 2.4: 中繼資料處理器實作
**預估時間：2 天**

1. **PNG 資訊處理抽象化**
   ```python
   # metadata_processor.py
   class IMetadataProcessor:
       def extract_png_info(self, image_path: str) -> dict:
           """從 PNG 圖片提取中繼資料"""
           pass
   
   class WebUIMetadataProcessor(IMetadataProcessor):
       def extract_png_info(self, image_path: str) -> dict:
           from modules import extras
           return extras.run_pnginfo(image_path)
   
   class StandaloneMetadataProcessor(IMetadataProcessor):
       def extract_png_info(self, image_path: str) -> dict:
           from PIL import Image
           from PIL.ExifTags import TAGS
           # 使用 PIL 實作 PNG 資訊提取
           with Image.open(image_path) as img:
               return self._extract_metadata_from_pil(img)
   ```

2. **參數處理抽象化**
   ```python
   class IParameterProcessor:
       def parse_parameters(self, text: str) -> dict:
           """解析參數字串"""
           pass
       
       def format_parameters(self, params: dict) -> str:
           """格式化參數為字串"""
           pass
   ```

### 任務 2.5: UI 橋接層設計
**預估時間：1 天**

1. **設計 UI 橋接介面**
   ```python
   class IUIBridge:
       def setup_ui_callbacks(self):
           """設定 UI 回呼函式"""
           pass
       
       def register_components(self, components: dict):
           """註冊 UI 元件"""
           pass
   ```

2. **實作 WebUI 和獨立模式的 UI 橋接**

## 交付物

### 主要檔案
1. **`compat_layer.py`** - 主要相容性層實作
2. **`environment_detector.py`** - 環境偵測機制
3. **`interfaces/`** 目錄包含所有抽象介面定義
4. **`webui_adapters/`** 目錄包含 AUTOMATIC1111 模式適配器
5. **`standalone_adapters/`** 目錄包含獨立模式適配器

### 設計文件
1. **`interface_specifications.md`** - 介面規格說明
2. **`architecture_overview.md`** - 整體架構概覽
3. **`usage_examples.md`** - 使用範例
4. **`testing_guidelines.md`** - 測試指導原則

### 測試檔案
1. **`tests/test_compat_layer.py`** - 相容性層單元測試
2. **`tests/test_environment_detector.py`** - 環境偵測測試
3. **`tests/test_adapters.py`** - 適配器測試

## 架構設計原則

### 設計模式應用
1. **橋接模式 (Bridge Pattern)**: 分離抽象介面與具體實作
2. **策略模式 (Strategy Pattern)**: 根據環境選擇不同的實作策略
3. **工廠模式 (Factory Pattern)**: 根據環境建立適當的物件實例
4. **單例模式 (Singleton Pattern)**: 確保相容性層的唯一實例

### 程式碼品質要求
1. **類型提示**: 所有公開方法都必須有完整的類型提示
2. **文件字串**: 每個類別和方法都要有清楚的 docstring
3. **例外處理**: 適當的例外處理和錯誤訊息
4. **記錄**: 關鍵操作要有適當的記錄輸出

## 測試要求

### 單元測試覆蓋率
- 環境偵測: 100%
- 路徑管理: 95%
- 設定管理: 95%
- 中繼資料處理: 90%

### 整合測試
1. **雙環境測試**: 同一套測試在兩種環境下都要通過
2. **切換測試**: 測試環境切換的正確性
3. **降級測試**: 測試功能降級時的行為

## 安全考量
1. **路徑安全**: 防止路徑遍歷攻擊
2. **設定驗證**: 驗證設定值的合法性
3. **例外安全**: 確保例外不會洩漏敏感資訊

## 常見問題與解答

**Q: 如何確保兩種模式下功能的一致性？**
A: 透過統一的抽象介面和全面的測試套件，確保行為一致性。

**Q: 當某些功能在獨立模式下無法實作時怎麼辦？**
A: 設計適當的降級機制，並清楚記錄功能差異。

## 後續連接
完成此項目後，繼續執行：
- **Backlog 003**: WebUI 功能模擬實作
- **Backlog 004**: 獨立執行入口建立
