# Backlog 005: 現有模組相依性修改與適配

## 優先級
**中高 (High)** - 重要的架構修改，確保現有功能在雙模式下正常運作

## 估算工作量
**10-14 工作天**

## 目標描述
修改現有的 `civitai_manager_libs` 模組，移除對 AUTOMATIC1111 特定功能的硬相依性，並透過相容性層進行存取。這是最關鍵且最複雜的任務，需要仔細處理以避免破壞現有功能。

## 接受標準 (Definition of Done)
1. ✅ 所有模組都透過相容性層存取 AUTOMATIC1111 功能
2. ✅ 移除所有直接的 `modules.*` 匯入
3. ✅ 實作條件匯入機制
4. ✅ 確保 AUTOMATIC1111 模式功能完全保持
5. ✅ 獨立模式下所有核心功能正常運作
6. ✅ 通過完整的回歸測試
7. ✅ 程式碼品質符合專案標準

## 詳細任務

### 任務 5.1: 模組相依性分析和優先級排序
**預估時間：2 天**

1. **分析所有模組的相依性**
   基於 Backlog 001 的分析結果，建立修改優先級：

   **第一優先級 (核心基礎模組)**
   - `setting.py` - 設定管理，多處使用
   - `util.py` - 工具函式，被廣泛引用
   - `ishortcut.py` - 核心快捷方式邏輯

   **第二優先級 (UI 相關模組)**
   - `civitai_shortcut_action.py` - 主要 UI 邏輯
   - `model_action.py` - 模型相關 UI
   - `recipe_action.py` - Recipe UI

   **第三優先級 (其他功能模組)**
   - 其餘 action 模組和功能模組

2. **建立修改計劃文件**
   ```markdown
   # 模組修改計劃
   
   ## 修改策略
   1. 向後相容原則：確保 AUTOMATIC1111 模式完全不受影響
   2. 最小變更原則：僅修改必要的部分
   3. 測試驅動：每個模組修改後立即測試
   
   ## 風險評估
   - 高風險：setting.py, util.py (影響面廣)
   - 中風險：主要 action 模組
   - 低風險：輔助功能模組
   ```

### 任務 5.2: 核心模組修改 - setting.py
**預估時間：3 天**

1. **分析現有 setting.py 的相依性**
   ```python
   # 目前的相依性分析
   from modules import scripts, script_callbacks, shared
   
   # 主要使用方式：
   # - scripts.basedir() 取得基礎路徑
   # - shared.* 存取共享變數
   # - script_callbacks.* 註冊回呼
   ```

2. **實作相容性層整合**
   ```python
   # 修改後的 setting.py
   
   import os
   import json
   from typing import Optional, Any
   
   # 相容性層整合
   _compat_layer = None
   
   def set_compatibility_layer(compat_layer):
       """設定相容性層 (由主程式呼叫)"""
       global _compat_layer
       _compat_layer = compat_layer
   
   def get_compatibility_layer():
       """取得相容性層"""
       global _compat_layer
       if _compat_layer is None:
           # 自動偵測和初始化 (fallback)
           from .compat_layer import CompatibilityLayer
           from .environment_detector import EnvironmentDetector
           env = EnvironmentDetector.detect_environment()
           _compat_layer = CompatibilityLayer(mode=env)
       return _compat_layer
   
   # 路徑相關函式修改
   def get_extension_base_path() -> str:
       """取得擴展基礎路徑"""
       compat = get_compatibility_layer()
       return compat.path_manager.get_base_path()
   
   def get_shortcut_base_path() -> str:
       """取得 shortcut 基礎路徑"""
       return get_extension_base_path()
   
   def get_setting_file() -> str:
       """取得設定檔路徑"""
       base_path = get_extension_base_path()
       return os.path.join(base_path, "civitai_shortcut_setting.json")
   
   # 設定管理函式修改
   def read_setting() -> dict:
       """讀取設定"""
       compat = get_compatibility_layer()
       
       # 嘗試從相容性層讀取
       if hasattr(compat, 'config_manager'):
           return compat.config_manager.get_all_config()
       
       # fallback 到檔案讀取
       setting_file = get_setting_file()
       if os.path.isfile(setting_file):
           try:
               with open(setting_file, 'r', encoding='utf-8') as f:
                   return json.load(f)
           except Exception as e:
               print(f"Warning: Failed to read setting file: {e}")
       
       return get_default_setting()
   
   def write_setting(setting_dict: dict):
       """寫入設定"""
       compat = get_compatibility_layer()
       
       # 透過相容性層寫入
       if hasattr(compat, 'config_manager'):
           for key, value in setting_dict.items():
               compat.config_manager.set(key, value)
           compat.config_manager.save()
           return
       
       # fallback 到檔案寫入
       setting_file = get_setting_file()
       os.makedirs(os.path.dirname(setting_file), exist_ok=True)
       
       try:
           with open(setting_file, 'w', encoding='utf-8') as f:
               json.dump(setting_dict, f, indent=4, ensure_ascii=False)
       except Exception as e:
           print(f"Error: Failed to write setting file: {e}")
   ```

### 任務 5.3: 工具模組修改 - util.py
**預估時間：2 天**

1. **修改 util.py 的相依性處理**
   ```python
   # util.py 修改範例
   
   import os
   import sys
   from typing import Optional, Any
   
   # 除錯和記錄相關
   def printD(msg: str, force: bool = False):
       """除錯訊息輸出"""
       compat = _get_compatibility_layer()
       
       # 透過相容性層檢查除錯模式
       debug_enabled = False
       if compat and hasattr(compat, 'config_manager'):
           debug_enabled = compat.config_manager.get('debug.enabled', False)
       
       if debug_enabled or force:
           print(f"[Civitai Shortcut] {msg}")
   
   def _get_compatibility_layer():
       """取得相容性層 (內部使用)"""
       try:
           from . import setting
           return setting.get_compatibility_layer()
       except ImportError:
           return None
   
   # 路徑處理函式
   def get_models_path(model_type: str = "checkpoints") -> str:
       """取得模型路徑"""
       compat = _get_compatibility_layer()
       
       if compat and hasattr(compat, 'path_manager'):
           return compat.path_manager.get_model_path(model_type)
       
       # fallback 邏輯
       base_path = os.path.dirname(os.path.abspath(__file__))
       models_base = os.path.join(base_path, "models")
       
       type_mapping = {
           "checkpoints": "Stable-diffusion",
           "lora": "Lora",
           "textual_inversion": "embeddings",
           "hypernetwork": "hypernetworks",
           "vae": "VAE"
       }
       
       model_dir = os.path.join(models_base, type_mapping.get(model_type, model_type))
       os.makedirs(model_dir, exist_ok=True)
       return model_dir
   ```

### 任務 5.4: UI Action 模組修改
**預估時間：4 天**

需要修改所有的 `*_action.py` 模組：

1. **civitai_shortcut_action.py 修改範例**
   ```python
   # civitai_shortcut_action.py
   
   import gradio as gr
   from typing import Optional
   
   # 相容性層變數
   _compat_layer = None
   
   def set_compatibility_layer(compat_layer):
       """設定相容性層"""
       global _compat_layer
       _compat_layer = compat_layer
   
   def get_compatibility_layer():
       """取得相容性層"""
       global _compat_layer
       if _compat_layer is None:
           from . import setting
           _compat_layer = setting.get_compatibility_layer()
       return _compat_layer
   
   # PNG 資訊處理修改
   def get_png_info_from_image(image):
       """從圖片取得 PNG 資訊"""
       if image is None:
           return {}
       
       compat = get_compatibility_layer()
       
       # 透過相容性層處理
       if hasattr(compat, 'metadata_processor'):
           try:
               return compat.metadata_processor.extract_png_info(image)
           except Exception as e:
               print(f"Error extracting PNG info: {e}")
               return {}
       
       # fallback 處理
       return _fallback_png_info_extraction(image)
   
   def _fallback_png_info_extraction(image):
       """fallback PNG 資訊提取"""
       try:
           from PIL import Image
           if isinstance(image, str):
               with Image.open(image) as img:
                   return getattr(img, 'text', {})
           return {}
       except Exception:
           return {}
   
   # 參數複製功能修改
   def parameters_copypaste_setup(component_dict):
       """設定參數複製貼上功能"""
       compat = get_compatibility_layer()
       
       # 檢查是否在 WebUI 環境
       if compat.mode == 'webui':
           try:
               # 使用原生 WebUI 功能
               from modules import infotext_utils
               infotext_utils.register_parameter_copypaste(component_dict)
           except ImportError:
               # fallback 到自訂實作
               _setup_custom_copypaste(component_dict)
       else:
           # 獨立模式使用自訂實作
           _setup_custom_copypaste(component_dict)
   
   def _setup_custom_copypaste(component_dict):
       """自訂參數複製貼上實作"""
       # 實作自訂的參數複製貼上邏輯
       pass
   ```

2. **統一的修改模式**
   為所有 action 模組建立統一的修改模式：
   
   ```python
   # 標準的模組開頭
   """
   模組名稱 - 相容雙模式版本
   
   此模組已修改為支援 AUTOMATIC1111 和獨立模式運行
   """
   
   # 標準的相容性層整合
   _compat_layer = None
   
   def set_compatibility_layer(compat_layer):
       global _compat_layer
       _compat_layer = compat_layer
   
   def get_compatibility_layer():
       global _compat_layer
       if _compat_layer is None:
           from . import setting
           _compat_layer = setting.get_compatibility_layer()
       return _compat_layer
   
   # 替換所有直接的 modules.* 存取
   # 使用 compat.functionality 替代
   ```

### 任務 5.5: 條件匯入機制實作
**預估時間：2 天**

1. **建立統一的條件匯入處理器**
   ```python
   # conditional_imports.py
   
   class ConditionalImportManager:
       """條件匯入管理器"""
       
       def __init__(self):
           self._webui_available = None
           self._cache = {}
       
       def is_webui_available(self) -> bool:
           """檢查 WebUI 是否可用"""
           if self._webui_available is None:
               try:
                   import modules.scripts
                   self._webui_available = True
               except ImportError:
                   self._webui_available = False
           return self._webui_available
       
       def try_import(self, module_name: str, fallback=None):
           """嘗試匯入模組"""
           if module_name in self._cache:
               return self._cache[module_name]
           
           try:
               module = __import__(module_name, fromlist=[''])
               self._cache[module_name] = module
               return module
           except ImportError:
               self._cache[module_name] = fallback
               return fallback
       
       def get_webui_module(self, module_name: str, attr_name: str = None):
           """取得 WebUI 模組或屬性"""
           if not self.is_webui_available():
               return None
           
           module = self.try_import(f'modules.{module_name}')
           if module and attr_name:
               return getattr(module, attr_name, None)
           return module
   
   # 全域實例
   import_manager = ConditionalImportManager()
   ```

### 任務 5.6: 測試和驗證
**預估時間：3 天**

1. **建立回歸測試套件**
   ```python
   # tests/test_module_compatibility.py
   
   import unittest
   import sys
   import os
   
   class TestModuleCompatibility(unittest.TestCase):
       """模組相容性測試"""
       
       def setUp(self):
           """測試設定"""
           # 設定測試環境
           pass
       
       def test_setting_module_webui_mode(self):
           """測試 setting 模組在 WebUI 模式下的功能"""
           # 模擬 WebUI 環境
           pass
       
       def test_setting_module_standalone_mode(self):
           """測試 setting 模組在獨立模式下的功能"""
           # 模擬獨立環境
           pass
       
       def test_util_module_functions(self):
           """測試 util 模組功能"""
           pass
       
       def test_action_modules_initialization(self):
           """測試 action 模組初始化"""
           pass
   
   if __name__ == '__main__':
       unittest.main()
   ```

2. **建立整合測試**
   ```python
   # tests/test_integration.py
   
   class TestIntegration(unittest.TestCase):
       """整合測試"""
       
       def test_full_webui_compatibility(self):
           """測試完整的 WebUI 相容性"""
           # 測試所有功能在 WebUI 環境下正常運作
           pass
       
       def test_full_standalone_functionality(self):
           """測試完整的獨立模式功能"""
           # 測試所有功能在獨立模式下正常運作
           pass
       
       def test_mode_switching(self):
           """測試模式切換"""
           # 測試能夠正確偵測和切換運行模式
           pass
   ```

## 交付物

### 修改的模組檔案
1. **`civitai_manager_libs/setting.py`** - 修改後的設定管理
2. **`civitai_manager_libs/util.py`** - 修改後的工具函式
3. **所有 `*_action.py` 檔案** - 修改後的 UI 邏輯
4. **其他功能模組** - 根據相依性分析修改

### 新增的支援檔案
1. **`conditional_imports.py`** - 條件匯入管理器
2. **`module_compatibility.py`** - 模組相容性工具
3. **`migration_guide.md`** - 遷移指導文件

### 測試檔案
1. **`tests/test_module_compatibility.py`** - 模組相容性測試
2. **`tests/test_integration.py`** - 整合測試
3. **`tests/test_regression.py`** - 回歸測試

### 文件
1. **`COMPATIBILITY_CHANGES.md`** - 相容性變更說明
2. **`DEVELOPER_GUIDE.md`** - 開發者指南更新
3. **`TROUBLESHOOTING.md`** - 故障排除指南

## 品質保證要求

### 程式碼品質
1. **向後相容性**: 100% 保持 AUTOMATIC1111 模式功能
2. **測試覆蓋率**: 修改模組的測試覆蓋率 ≥ 85%

### 風險控制
1. **漸進修改**: 一次只修改一個模組
2. **即時測試**: 每次修改後立即進行測試
3. **回滾機制**: 準備快速回滾方案
4. **版本控制**: 詳細的提交記錄

## 修改策略和注意事項

### 修改原則
1. **最小變更**: 只修改必要的部分
2. **保持介面**: 保持公開 API 不變
3. **錯誤處理**: 加強錯誤處理和降級機制
4. **文件同步**: 同步更新相關文件

### 常見陷阱
1. **循環匯入**: 注意避免模組間的循環相依
2. **全域狀態**: 小心處理全域變數和狀態
3. **執行緒安全**: 確保修改不影響執行緒安全性
4. **記憶體洩漏**: 注意物件生命週期管理

## 測試策略

### 測試階段
1. **單元測試**: 每個修改模組的單獨測試
2. **整合測試**: 模組間互動測試
3. **回歸測試**: 確保現有功能不受影響
4. **使用者測試**: 實際使用情境測試

### 測試環境
1. **純 WebUI 環境**: 測試 AUTOMATIC1111 相容性
2. **純獨立環境**: 測試獨立模式功能
3. **混合環境**: 測試環境偵測和切換

## 常見問題與解答

**Q: 如何確保不破壞現有的 AUTOMATIC1111 擴展功能？**
A: 採用相容性層模式，保持原有 API 不變，並建立完整的回歸測試。

**Q: 修改過程中遇到複雜相依性怎麼辦？**
A: 先記錄問題，設計最小可行的替代方案，必要時可以降級功能。

**Q: 如何處理模組間的循環相依？**
A: 重構模組結構，將共享功能提取到獨立模組，或使用延遲匯入。

## 後續連接
完成此項目後，繼續執行：
- **Backlog 006**: UI 元件雙模式適配
- **Backlog 007**: 測試和品質保證
