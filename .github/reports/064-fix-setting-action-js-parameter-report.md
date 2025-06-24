---
title: "Job Report: Bug Fix #064 - Fix JS parameter in reload button click"
date: "2025-06-24T06:50:04Z"
---

# Bug Fix #064 - Fix JS parameter in reload button click 工作報告

**日期**：2025-06-24T06:50:04Z  
**任務**：修復在 standalone 模式下，reload 按鈕使用 Gradio click 方法時因使用 `_js` 參數導致的 TypeError  
**類型**：Bug Fix  
**狀態**：已完成

## 一、任務概述

在執行 `timeout 30 python3 main.py --debug` 時，介面初始化過程中因 Gradio 4.x 移除 `_js` 參數，使 `reload_btn.click` 調用產生 `TypeError`，需將 `_js` 更新為 `js` 以符合新 API。

## 二、實作內容

### 2.1 更新 reload_btn.click 參數
- 將 `scripts/civitai_manager_libs/setting_action.py` 中的 `_js='restart_reload'` 改為 `js='restart_reload'`【F:scripts/civitai_manager_libs/setting_action.py†L326】

## 三、技術細節

### 3.1 架構變更
- 無

### 3.2 API 變更
- Gradio click 事件 API：參數 `_js` 改為 `js`

### 3.3 配置變更
- 無

## 四、測試與驗證

### 4.1 程式碼品質檢查
```bash
black --line-length=100 --skip-string-normalization scripts/civitai_manager_libs/setting_action.py
flake8 scripts/civitai_manager_libs/setting_action.py || true
pytest tests/test_main.py tests/test_ui_adapter.py -q
timeout 5 python3 main.py --debug
```

### 4.2 功能測試
- 執行 `timeout 30 python3 main.py --debug` 不再報錯，介面正常初始化。

### 4.3 覆蓋率測試
- 不適用

## 五、影響評估

### 5.1 向後相容性
- 無影響，僅更新內部事件調用。

### 5.2 使用者體驗
- 修復啟動錯誤，改善在 standalone 模式的使用流程。

## 六、問題與解決方案

### 6.1 遇到的問題
- **問題描述**：Gradio 4.x 移除 `_js` 參數，導致 `TypeError: event_trigger() got an unexpected keyword argument '_js'`。
- **解決方案**：將 `_js` 參數改為 `js`。

### 6.2 技術債務
- 無

## 七、後續事項

### 7.1 建議的下一步
- 檢查其他 Action 模組的 click/js 參數使用情況以確保相容性。

## 八、檔案異動清單

| 檔案路徑                                         | 異動類型 | 描述                              |
|------------------------------------------------|--------|----------------------------------|
| `scripts/civitai_manager_libs/setting_action.py` | 修改     | 將 `_js` 參數更新為 `js` 以符合 Gradio 4.x API |
