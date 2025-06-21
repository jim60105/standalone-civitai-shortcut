---
title: "Job Report: Bug Fix #036 - Send To Recipe Prompt Prefix Parsing Fix"
date: "2025-06-21T20:26:43Z"
---

# Bug Fix #036 - Send To Recipe Prompt Prefix Parsing Fix 工作報告

**日期**：2025-06-21T20:26:43Z  
**任務**：修復 Send To Recipe 功能中提示詞前綴解析問題，確保含有 "Prompt:" 前綴的生成參數能被正確解析  
**類型**：Bug Fix  
**狀態**：已完成

## 一、任務概述

前次修復 (#002) 雖然解決了 Send To Recipe 功能的數據傳遞問題，但發現當生成參數包含 "Prompt:" 前綴時，解析功能無法正確分離提示詞內容，導致 Recipe 頁面中顯示 "Prompt: 實際提示詞" 而不是 "實際提示詞"。此問題影響了用戶體驗，需要進一步修復提示詞解析邏輯。

## 二、實作內容

### 2.1 問題分析與診斷
- 透過單元測試發現 `parse_data` 函數無法正確處理含有 "Prompt:" 前綴的格式
- 確認問題出現在 `scripts/civitai_manager_libs/prompt.py` 的 `parse_data` 函數
- 驗證 `analyze_prompt` 和 `on_recipe_input_change` 函數依賴正確的 `parse_data` 輸出

### 2.2 修復提示詞解析邏輯
- 【F:scripts/civitai_manager_libs/prompt.py†L73-L83】更新 `parse_data` 函數，新增對 "Prompt:" 前綴的檢測和處理
- 在解析第一行時檢查是否包含 "Prompt:" 前綴，若有則使用正則表達式提取實際內容
- 保持對標準格式（無前綴）的兼容性

```python
# Handle "Prompt: " prefix on the first line
if count == 0 and line.startswith('Prompt:'):
    prompt_match = re.search(r'Prompt:\s*(.+)', line)
    if prompt_match:
        parsed_data['prompt'] = prompt_match.group(1)
    else:
        parsed_data['prompt'] = line
```

### 2.3 增強測試覆蓋
- 【F:tests/test_send_to_recipe_fix.py†L78-L120】新增 `test_recipe_input_change_with_prompt_prefix` 測試
- 【F:tests/test_send_to_recipe_fix.py†L78-L120】新增 `test_recipe_input_change_with_standard_format` 測試
- 驗證兩種格式（含前綴和標準格式）都能正確解析

## 三、技術細節

### 3.1 解析邏輯改進
- 使用正則表達式 `r'Prompt:\s*(.+)'` 精確提取 "Prompt:" 後的內容
- 保持現有邏輯不變，僅在第一行且包含 "Prompt:" 時觸發特殊處理
- 確保多行提示詞的連接邏輯不受影響

### 3.2 兼容性考慮
- 修改後的函數仍完全兼容標準 Stable Diffusion 參數格式
- 不影響現有的負面提示詞和參數解析邏輯
- 保持 API 接口不變，無需修改調用方代碼

## 四、測試與驗證

### 4.1 程式碼品質檢查
```bash
black --line-length=100 --skip-string-normalization scripts/civitai_manager_libs/prompt.py
black --line-length=100 --skip-string-normalization tests/test_send_to_recipe_fix.py
flake8 tests/test_send_to_recipe_fix.py --config=.flake8
pytest tests/test_send_to_recipe_fix.py -v
```

執行結果：✅ 所有檢查通過，無格式問題和 lint 警告

### 4.2 功能測試
- **含前綴格式測試**：
  - 輸入：`"Prompt: Beautiful landscape\nNegative prompt: blurry\nSteps: 20"`
  - 輸出：提示詞正確解析為 `"Beautiful landscape"`（不含前綴）
  
- **標準格式測試**：
  - 輸入：`"Beautiful landscape\nNegative prompt: blurry\nSteps: 20"`
  - 輸出：提示詞正確解析為 `"Beautiful landscape"`
  
- **完整數據流測試**：
  - 從 `on_send_to_recipe_click` 到 `on_recipe_input_change` 的完整流程
  - 驗證 Recipe 頁面中各欄位正確填充

### 4.3 回歸測試
```bash
pytest tests/ -k "prompt or recipe" -v
```
執行結果：✅ 24 個相關測試全部通過，無回歸問題

## 五、影響評估

### 5.1 向後相容性
- ✅ 完全向後兼容，不影響現有標準格式的解析
- ✅ 不改變任何公共 API 接口
- ✅ 現有 Recipe 和參數處理流程無需變更

### 5.2 使用者體驗
- ✅ 修復了 Recipe 頁面提示詞顯示問題
- ✅ 支持更多來源的生成參數格式
- ✅ 提升了 Send To Recipe 功能的可靠性

## 六、問題與解決方案

### 6.1 遇到的問題
- **問題描述**：初始測試發現 `parse_data` 函數沒有識別 "Prompt:" 標籤，將其作為提示詞內容的一部分
- **解決方案**：在解析邏輯中新增正則表達式匹配，專門處理第一行包含 "Prompt:" 的情況

### 6.2 技術債務
- ✅ 解決了參數解析不一致的問題
- ✅ 增強了測試覆蓋率，減少未來類似問題的風險

## 七、後續事項

### 7.1 待完成項目
- [x] 修復提示詞前綴解析問題
- [x] 新增相關測試用例
- [x] 驗證所有格式兼容性

### 7.2 相關任務
- 關聯 Bug #002：Send To Recipe Prompt Extraction Bug
- 此修復是對 #002 的完善，解決了遺留的解析問題

### 7.3 建議的下一步
- 考慮支持更多生成器的參數格式（如 ComfyUI、NovelAI 等）
- 優化參數解析性能，考慮緩存常用格式的解析結果

## 八、檔案異動清單

| 檔案路徑 | 異動類型 | 描述 |
|---------|----------|------|
| `scripts/civitai_manager_libs/prompt.py` | 修改 | 修復 parse_data 函數，支持 "Prompt:" 前綴解析 |
| `tests/test_send_to_recipe_fix.py` | 修改 | 新增兩個測試函數，覆蓋前綴和標準格式解析 |

## 九、驗證命令

### 完整測試執行
```bash
# 運行所有 Send To Recipe 相關測試
pytest tests/test_send_to_recipe_fix.py -v

# 運行所有 prompt 和 recipe 相關測試
pytest tests/ -k "prompt or recipe" -v

# 程式碼品質檢查
black --check --line-length=100 --skip-string-normalization scripts/civitai_manager_libs/prompt.py tests/test_send_to_recipe_fix.py
flake8 tests/test_send_to_recipe_fix.py --config=.flake8
```

### 手動驗證
```python
# 測試前綴格式解析
from scripts.civitai_manager_libs.prompt import parse_data
result = parse_data("Prompt: test prompt\nNegative prompt: bad\nSteps: 20")
assert result['prompt'] == "test prompt"  # 不應包含 "Prompt: "

# 測試標準格式解析
result = parse_data("test prompt\nNegative prompt: bad\nSteps: 20") 
assert result['prompt'] == "test prompt"  # 標準格式仍正常
```

**修復狀態**：✅ 完成  
**測試狀態**：✅ 全部通過  
**品質檢查**：✅ 無警告
