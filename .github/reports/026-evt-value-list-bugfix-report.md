---
title: "Job Report: Bug Fix #026 - Gradio Gallery evt.value List 型態處理修正"
date: "2025-06-21T01:15:40Z"
---

# Bug Fix #026 - Gradio Gallery evt.value List 型態處理修正 工作報告

**日期**：2025-06-21T01:15:40Z  
**任務**：修正 Gradio Gallery evt.value 回傳 list 型態時導致 TypeError 的問題，並強化相關資料存取流程的型態防禦。  
**類型**：Bug Fix  
**狀態**：已完成

## 一、任務概述

近期於 Civitai Shortcut 專案中，Gradio Gallery 元件的選擇事件 `evt.value` 可能回傳 list（如 `[image_url, shortcut_name]`），而原本程式僅預期為 string，導致在多處以 dict key 查詢時觸發 `TypeError: unhashable type: 'list'`。本次任務目標為：
- 修正所有受影響的事件處理與資料查詢函式，確保支援 string 與 list 兩種格式。
- 增加防禦性程式設計，避免未來同類型錯誤。
- 增加完整測試覆蓋。

## 二、實作內容

### 2.1 Gallery 選擇事件型態防禦
- 於 `on_recipe_gallery_select`、`on_classification_list_select` 等事件處理函式，加入型態判斷與正確值提取邏輯。
- 當 `evt.value` 為 list 時，自動取第二元素（shortcut name）；為 string 時直接使用。
- 若型態異常，回傳預設空值並記錄 debug log。
- 【F:scripts/civitai_manager_libs/recipe_action.py†L905-L920】
- 【F:scripts/civitai_manager_libs/classification_action.py†L735-L750】

```python
if isinstance(evt.value, list) and len(evt.value) > 1:
    select_name = evt.value[1]
elif isinstance(evt.value, str):
    select_name = evt.value
else:
    util.printD(f"[RECIPE] Unexpected evt.value format: {evt.value}")
    return ("", "", "", "", "", "", None, [])
```

### 2.2 資料查詢函式型態防禦
- 於 `get_recipe`、`get_recipe_shortcuts`、`get_classification_info`、`get_classification_shortcuts` 等函式，加入型態檢查與 None 檢查，避免 list 被當作 dict key。
- 若收到 list，直接回傳 None 並記錄 debug log。
- 【F:scripts/civitai_manager_libs/recipe.py†L195-L210】【F:scripts/civitai_manager_libs/recipe.py†L105-L125】
- 【F:scripts/civitai_manager_libs/classification.py†L115-L135】【F:scripts/civitai_manager_libs/classification.py†L70-L85】

### 2.3 測試覆蓋與驗證
- 新增 `tests/test_evt_value_list_fix.py`，涵蓋 14 項測試，包含：
  - 直接呼叫底層函式傳入 list
  - 事件處理函式傳入 string、list、異常型態
  - 邊界條件（空 list、單元素 list）
  - 正常 string 輸入
- 【F:tests/test_evt_value_list_fix.py†L1-L200】

## 三、技術細節

### 3.1 架構變更
- 無架構層級變更，僅於事件處理與資料查詢層加強型態防禦。

### 3.2 API 變更
- 無對外 API 變更。

### 3.3 配置變更
- 無配置或環境變數變更。

## 四、測試與驗證

### 4.1 程式碼品質檢查
```bash
black --line-length=100 --skip-string-normalization tests
black --line-length=100 --skip-string-normalization scripts/civitai_manager_libs/compat
flake8 tests
flake8 scripts/civitai_manager_libs/compat
pytest -v
```

### 4.2 功能測試
- 手動於 WebUI 及 Standalone 模式下，進行 Gallery 選擇操作，確認不再出現 TypeError，並能正確取得資料。
- 測試異常型態（如空 list、dict、int）時，能安全降級並記錄 debug log。

### 4.3 覆蓋率測試（如適用）
```bash
pytest --cov=scripts/civitai_manager_libs/compat --cov-report=term --cov-report=html
```

## 五、影響評估

### 5.1 向後相容性
- 完全向後相容，未更動任何外部 API 或資料結構。
- 僅加強型態防禦與異常處理。

### 5.2 使用者體驗
- 避免因 Gallery 選擇型態異常導致的崩潰，提升穩定性。
- 錯誤時有明確 debug log，便於追蹤。

## 六、問題與解決方案

### 6.1 遇到的問題
- **問題描述**：Gradio Gallery evt.value 可能為 list，原本僅支援 string，導致 dict 查詢時觸發 TypeError。
- **解決方案**：於所有相關事件與查詢函式加強型態判斷與防禦，並補齊測試。

### 6.2 技術債務
- 無新增技術債務。

## 七、後續事項

### 7.1 待完成項目
- [ ] 持續追蹤其他 UI 事件型態異常的潛在風險
- [ ] 針對更多複合型態輸入進行壓力測試

### 7.2 相關任務
- #025 gallery-select-bugfix-report

### 7.3 建議的下一步
- 建議將此型態防禦模式推廣至所有 Gradio 互動元件事件處理
- 增加自動化型態檢查工具於 CI 流程

## 八、檔案異動清單

| 檔案路徑 | 異動類型 | 描述 |
|---------|----------|------|
| `scripts/civitai_manager_libs/recipe_action.py` | 修改 | Gallery 選擇事件型態防禦 |
| `scripts/civitai_manager_libs/classification_action.py` | 修改 | Gallery 選擇事件型態防禦 |
| `scripts/civitai_manager_libs/recipe.py` | 修改 | 資料查詢函式型態防禦 |
| `scripts/civitai_manager_libs/classification.py` | 修改 | 資料查詢函式型態防禦 |
| `tests/test_evt_value_list_fix.py` | 新增 | evt.value 型態防禦測試覆蓋 |
