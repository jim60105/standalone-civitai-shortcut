# Backlog 003: WebUI 功能模擬與獨立模式適配器實作

## 優先級
**高 (Critical)** - 核心功能實作，讓獨立模式具備完整功能

## 估算工作量
**8-12 工作天**

## 目標描述
實作 AUTOMATIC1111 WebUI 特定功能的模擬器和替代實作，確保在獨立模式下能夠提供等價的功能。重點包括 PNG 中繼資料處理、參數解析、採樣器資訊等核心功能。

## 接受標準 (Definition of Done)
1. ✅ 完成所有核心 WebUI 功能的模擬實作
2. ✅ PNG 中繼資料處理功能完全等價
3. ✅ 參數解析和格式化功能正常運作
4. ✅ 採樣器和其他選項清單正確載入
5. ✅ 通過功能對等性測試
6. ✅ 效能符合要求（不超過原生功能的 200% 時間）
7. ✅ 建立完整的測試套件

## 詳細任務

### 任務 3.1: PNG 中繼資料處理器實作
**預估時間：3 天**

1. **分析 AUTOMATIC1111 PNG 資訊格式**
   ```python
   # 研究 modules.extras.run_pnginfo 的行為
   # 了解 PNG 中繼資料的儲存格式和結構
   # 識別需要處理的特殊欄位
   ```

2. **實作獨立 PNG 處理器**
   ```python
   # standalone_png_processor.py
   import json
   from PIL import Image
   from PIL.PngImagePlugin import PngInfo
   from typing import Dict, Optional, Tuple
   
   class StandalonePngProcessor:
       """獨立模式的 PNG 中繼資料處理器"""
       
       def extract_png_info(self, image_path: str) -> Dict[str, any]:
           """
           提取 PNG 圖片的中繼資料
           
           Args:
               image_path: 圖片檔案路徑
               
           Returns:
               包含中繼資料的字典，格式與 AUTOMATIC1111 相容
           """
           try:
               with Image.open(image_path) as img:
                   return self._parse_png_metadata(img)
           except Exception as e:
               self._log_error(f"Failed to extract PNG info from {image_path}: {e}")
               return {}
       
       def _parse_png_metadata(self, img: Image.Image) -> Dict[str, any]:
           """解析 PNG 中繼資料"""
           metadata = {}
           
           # 處理標準 PNG 文字塊
           if hasattr(img, 'text'):
               for key, value in img.text.items():
                   metadata[key] = value
           
           # 處理 AUTOMATIC1111 特定欄位
           if 'parameters' in metadata:
               metadata['params'] = self._parse_parameters(metadata['parameters'])
           
           return metadata
       
       def _parse_parameters(self, param_string: str) -> Dict[str, any]:
           """解析參數字串為結構化資料"""
           # 實作參數解析邏輯
           pass
   ```

3. **建立測試資料集**
   - 收集不同類型的 PNG 圖片樣本
   - 包含各種參數組合的測試檔案
   - 建立對照組測試（WebUI 輸出 vs 獨立實作輸出）

### 任務 3.2: 參數處理系統實作
**預估時間：3 天**

1. **參數解析器實作**
   ```python
   # parameter_parser.py
   import re
   from typing import Dict, List, Optional
   
   class ParameterParser:
       """參數字串解析器"""
       
       def __init__(self):
           self._setup_patterns()
       
       def _setup_patterns(self):
           """設定正規表達式模式"""
           self.patterns = {
               'prompt': r'Prompt:\s*(.+?)(?=\n[A-Z]|\nSteps:|$)',
               'negative_prompt': r'Negative prompt:\s*(.+?)(?=\n[A-Z]|\nSteps:|$)',
               'steps': r'Steps:\s*(\d+)',
               'sampler': r'Sampler:\s*([^,\n]+)',
               'cfg_scale': r'CFG scale:\s*([\d.]+)',
               'seed': r'Seed:\s*(\d+)',
               'size': r'Size:\s*(\d+x\d+)',
               'model_hash': r'Model hash:\s*([a-fA-F0-9]+)',
               'model': r'Model:\s*([^,\n]+)',
           }
       
       def parse(self, text: str) -> Dict[str, any]:
           """
           解析參數文字為結構化資料
           
           Args:
               text: 參數文字字串
               
           Returns:
               解析後的參數字典
           """
           params = {}
           
           for key, pattern in self.patterns.items():
               match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
               if match:
                   params[key] = match.group(1).strip()
           
           # 後處理特殊欄位
           self._post_process_params(params)
           
           return params
       
       def _post_process_params(self, params: Dict[str, any]):
           """後處理參數值"""
           # 轉換數值型別
           if 'steps' in params:
               params['steps'] = int(params['steps'])
           if 'cfg_scale' in params:
               params['cfg_scale'] = float(params['cfg_scale'])
           if 'seed' in params:
               params['seed'] = int(params['seed'])
           
           # 解析尺寸
           if 'size' in params:
               width, height = params['size'].split('x')
               params['width'] = int(width)
               params['height'] = int(height)
   ```

2. **參數格式化器實作**
   ```python
   class ParameterFormatter:
       """參數格式化器"""
       
       def format(self, params: Dict[str, any]) -> str:
           """將參數字典格式化為文字"""
           lines = []
           
           # 主要參數
           if 'prompt' in params:
               lines.append(f"Prompt: {params['prompt']}")
           
           if 'negative_prompt' in params:
               lines.append(f"Negative prompt: {params['negative_prompt']}")
           
           # 技術參數
           tech_params = []
           if 'steps' in params:
               tech_params.append(f"Steps: {params['steps']}")
           if 'sampler' in params:
               tech_params.append(f"Sampler: {params['sampler']}")
           # ... 其他參數
           
           if tech_params:
               lines.append(', '.join(tech_params))
           
           return '\n'.join(lines)
   ```

### 任務 3.3: 採樣器和選項管理器實作
**預估時間：2 天**

1. **採樣器清單管理**
   ```python
   # sampler_manager.py
   class SamplerManager:
       """採樣器管理器"""
       
       def __init__(self):
           self.samplers = self._load_samplers()
       
       def _load_samplers(self) -> List[Dict[str, str]]:
           """載入可用的採樣器清單"""
           # 預設採樣器清單
           default_samplers = [
               {"name": "Euler", "alias": "euler"},
               {"name": "Euler a", "alias": "euler_a"},
               {"name": "LMS", "alias": "lms"},
               {"name": "Heun", "alias": "heun"},
               {"name": "DPM2", "alias": "dpm2"},
               {"name": "DPM2 a", "alias": "dpm2_a"},
               {"name": "DPM++ 2S a", "alias": "dpm_plus_plus_2s_a"},
               {"name": "DPM++ 2M", "alias": "dpm_plus_plus_2m"},
               {"name": "DPM++ SDE", "alias": "dpm_plus_plus_sde"},
               {"name": "DPM fast", "alias": "dpm_fast"},
               {"name": "DPM adaptive", "alias": "dpm_adaptive"},
               {"name": "LMS Karras", "alias": "lms_karras"},
               {"name": "DPM2 Karras", "alias": "dpm2_karras"},
               {"name": "DPM2 a Karras", "alias": "dpm2_a_karras"},
               {"name": "DPM++ 2S a Karras", "alias": "dpm_plus_plus_2s_a_karras"},
               {"name": "DPM++ 2M Karras", "alias": "dpm_plus_plus_2m_karras"},
               {"name": "DPM++ SDE Karras", "alias": "dpm_plus_plus_sde_karras"},
               {"name": "DDIM", "alias": "ddim"},
               {"name": "PLMS", "alias": "plms"},
           ]
           
           return default_samplers
       
       def get_sampler_names(self) -> List[str]:
           """取得採樣器名稱清單"""
           return [sampler["name"] for sampler in self.samplers]
       
       def get_sampler_by_name(self, name: str) -> Optional[Dict[str, str]]:
           """根據名稱取得採樣器資訊"""
           for sampler in self.samplers:
               if sampler["name"] == name or sampler["alias"] == name:
                   return sampler
           return None
   ```

### 任務 3.4: 路徑和檔案管理器增強
**預估時間：2 天**

1. **擴充路徑管理功能**
   ```python
   # enhanced_path_manager.py
   class EnhancedPathManager:
       """增強型路徑管理器"""
       
       def __init__(self, base_path: str):
           self.base_path = base_path
           self._ensure_directories()
       
       def _ensure_directories(self):
           """確保必要目錄存在"""
           directories = [
               'models',
               'outputs',
               'cache',
               'config',
               'logs'
           ]
           
           for directory in directories:
               path = os.path.join(self.base_path, directory)
               os.makedirs(path, exist_ok=True)
       
       def get_model_path(self, model_type: str = 'checkpoints') -> str:
           """取得模型路徑"""
           model_paths = {
               'checkpoints': 'models/Stable-diffusion',
               'lora': 'models/Lora',
               'textual_inversion': 'models/embeddings',
               'hypernetwork': 'models/hypernetworks',
               'vae': 'models/VAE',
           }
           
           path = os.path.join(self.base_path, model_paths.get(model_type, 'models'))
           os.makedirs(path, exist_ok=True)
           return path
   ```

### 任務 3.5: 設定管理系統實作
**預估時間：2 天**

1. **獨立設定管理器**
   ```python
   # standalone_config.py
   import json
   import os
   from typing import Any, Dict, Optional
   
   class StandaloneConfig:
       """獨立模式設定管理器"""
       
       def __init__(self, config_path: str = None):
           if config_path is None:
               config_path = os.path.join(
                   os.path.dirname(__file__), 
                   'config', 
                   'config.json'
               )
           
           self.config_path = config_path
           self._config = self._load_config()
       
       def _load_config(self) -> Dict[str, Any]:
           """載入設定檔"""
           if os.path.exists(self.config_path):
               try:
                   with open(self.config_path, 'r', encoding='utf-8') as f:
                       return json.load(f)
               except (json.JSONDecodeError, IOError) as e:
                   print(f"Warning: Failed to load config from {self.config_path}: {e}")
           
           return self._get_default_config()
       
       def _get_default_config(self) -> Dict[str, Any]:
           """取得預設設定"""
           return {
               'server': {
                   'host': '127.0.0.1',
                   'port': 7860,
                   'share': False
               },
               'civitai': {
                   'api_key': '',
                   'download_path': './models',
                   'cache_enabled': True,
                   'cache_size_mb': 500
               },
               'ui': {
                   'theme': 'default',
                   'language': 'en',
                   'page_size': 20
               }
           }
       
       def get(self, key: str, default: Any = None) -> Any:
           """取得設定值"""
           keys = key.split('.')
           value = self._config
           
           for k in keys:
               if isinstance(value, dict) and k in value:
                   value = value[k]
               else:
                   return default
           
           return value
       
       def set(self, key: str, value: Any):
           """設定值"""
           keys = key.split('.')
           config = self._config
           
           for k in keys[:-1]:
               if k not in config:
                   config[k] = {}
               config = config[k]
           
           config[keys[-1]] = value
       
       def save(self):
           """儲存設定"""
           os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
           
           with open(self.config_path, 'w', encoding='utf-8') as f:
               json.dump(self._config, f, indent=2, ensure_ascii=False)
   ```

## 交付物

### 主要模組
1. **`standalone_png_processor.py`** - PNG 中繼資料處理器
2. **`parameter_parser.py`** - 參數解析和格式化
3. **`sampler_manager.py`** - 採樣器管理
4. **`enhanced_path_manager.py`** - 增強路徑管理
5. **`standalone_config.py`** - 獨立設定管理

### 資源檔案
1. **`data/samplers.json`** - 採樣器定義檔
2. **`config/default_config.json`** - 預設設定檔
3. **`data/model_types.json`** - 模型類型定義

### 測試檔案
1. **`tests/test_png_processor.py`** - PNG 處理器測試
2. **`tests/test_parameter_parser.py`** - 參數解析器測試
3. **`tests/test_sampler_manager.py`** - 採樣器管理器測試
4. **`tests/test_config_manager.py`** - 設定管理器測試

### 測試資料
1. **`test_data/sample_images/`** - 測試用 PNG 圖片
2. **`test_data/parameters/`** - 參數文字樣本
3. **`test_data/expected_outputs/`** - 預期輸出結果

## 品質保證

### 功能對等性測試
1. **建立對照測試**
   - 相同輸入在 WebUI 和獨立模式下產生相同輸出
   - 比較解析結果的完整性和準確性

2. **邊緣情況測試**
   - 處理損壞的 PNG 檔案
   - 處理不完整的參數字串
   - 處理非標準格式的中繼資料

### 效能測試
1. **處理速度測試**
   - PNG 處理時間不得超過原生功能的 200%
   - 參數解析時間不得超過 100ms（一般大小參數）

2. **記憶體使用測試**
   - 處理大型 PNG 檔案時記憶體使用合理
   - 無記憶體洩漏

### 相容性測試
1. **檔案格式相容性**
   - 支援各種 PNG 格式和壓縮等級
   - 支援不同來源的參數格式

2. **跨平台測試**
   - Windows、Linux、macOS 環境測試
   - 不同 Python 版本測試

## 錯誤處理策略

### 優雅降級
1. **PNG 處理失敗**
   - 記錄錯誤但不中斷執行
   - 提供基本的中繼資料資訊

2. **參數解析失敗**
   - 部分解析，儘可能提取有效資訊
   - 提供錯誤資訊給使用者

### 記錄和除錯
1. **詳細記錄**
   - 記錄處理過程中的關鍵步驟
   - 包含錯誤詳情和堆疊追蹤

2. **除錯模式**
   - 提供詳細的除錯輸出
   - 保存中間處理結果供分析

## 常見問題與解答

**Q: 如何確保 PNG 處理結果與 AUTOMATIC1111 完全一致？**
A: 建立全面的測試資料集，包含各種類型的圖片和參數組合，進行對照測試。

**Q: 當遇到新的參數格式時如何處理？**
A: 設計可擴充的解析器架構，支援新增自訂解析規則。

**Q: 如何處理效能問題？**
A: 實作快取機制，避免重複處理相同檔案，並使用非同步處理大型檔案。

## 後續連接
完成此項目後，繼續執行：
- **Backlog 004**: 獨立執行入口建立
- **Backlog 005**: 現有模組相依性修改
