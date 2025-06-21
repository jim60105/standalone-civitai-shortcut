---
title: "Job Report: Bug Fix #002 - Send To Recipe Prompt Extraction Bug"
date: "2025-06-21T12:41:43Z"
---

# Bug Fix #002 - Send To Recipe Prompt Extraction Bug 工作報告

**日期**：2025-06-21T12:41:43Z  
**任務**：修正 Send To Recipe 功能無法自動提取與填充圖像提示詞、負面提示詞與生成參數的問題，確保三種入口（Model Browser、Civitai User Gallery、拖拽圖像）皆能正確自動填充。  
**類型**：Bug Fix  
**狀態**：已完成

## 一、任務概述

Send To Recipe 是 Civitai Shortcut 主要用戶流程之一。原有流程中，當用戶從 Model Browser 或 Civitai User Gallery 點擊 Send To Recipe 按鈕時，雖然圖像能正確顯示於 Reference Image，但圖像元數據（提示詞、負面提示詞、生成參數）未能自動提取並填入 Prompt Recipe 對應欄位，導致用戶需手動複製貼上，嚴重影響體驗。本次任務目標為修正資料流，確保自動提取與填充功能於所有入口皆可用。

## 二、實作內容

### 2.1 流程與資料流分析
- 詳細分析 on_send_to_recipe_click、on_recipe_input_change、on_recipe_generate_data_change 的資料流與事件觸發，確認問題根因為 recipe_generate_data 被設為 current_time（時間戳）而非圖像對象。
- 【F:scripts/civitai_manager_libs/recipe_action.py†L790-L820】

### 2.2 修正資料傳遞與元數據提取
- 修改 on_recipe_input_change()，將 recipe_generate_data 設為 recipe_image（圖像對象），確保 on_recipe_generate_data_change 能正確提取元數據。
- 驗證拖拽圖像進入 Recipe 頁籤時的行為一致。
- 【F:scripts/civitai_manager_libs/recipe_action.py†L790-L820】

### 2.3 測試設計與驗證
- 新增/更新 tests/test_send_to_recipe_fix.py，覆蓋 on_recipe_input_change、on_recipe_generate_data_change 的資料流與欄位填充。
- 手動測試三種入口（Model Browser、Civitai User Gallery、拖拽圖像）流程。
- 【F:tests/test_send_to_recipe_fix.py†L1-L80】

## 三、技術細節

### 3.1 架構變更
- 無架構層級變更，僅修正資料流與事件傳遞。

### 3.2 API 變更
- 無對外 API 變更。

### 3.3 配置變更
- 無配置檔或環境變數變更。

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
- 於 Model Browser、Civitai User Gallery、拖拽圖像三種入口，點擊 Send To Recipe 或拖拽圖像，Prompt、Negative prompt、Parameter 欄位皆能自動正確填充。
- Reference Image 正確顯示圖像。
- WebUI 與 Standalone 模式皆正常運作。

### 4.3 覆蓋率測試（如適用）
```bash
pytest --cov=scripts/civitai_manager_libs/recipe_action --cov-report=term --cov-report=html
```

## 五、影響評估

### 5.1 向後相容性
- 修正不會破壞現有功能，現有 recipe 數據格式與 UI 佈局保持不變。

### 5.2 使用者體驗
- 用戶無需手動複製貼上，三個欄位自動正確填充，顯著提升 Recipe 編輯效率與體驗。

## 六、問題與解決方案

### 6.1 遇到的問題
- **問題描述**：資料流設計錯誤，recipe_generate_data 被設為時間戳，導致無法提取圖像元數據。
- **解決方案**：將 recipe_generate_data 改為傳遞圖像對象，確保 on_recipe_generate_data_change 能正確提取元數據。

### 6.2 技術債務
- 無新增技術債務。

## 七、後續事項

### 7.1 待完成項目
- [ ] 增強元數據解析容錯能力，支援更多圖像格式
- [ ] 提供用戶自定義欄位映射選項

### 7.2 相關任務
- 002-send-to-recipe-prompt-extraction-bug

### 7.3 建議的下一步
- 統一圖像元數據提取邏輯，擴展自動提取支援更多生成器與格式

## 八、檔案異動清單

| 檔案路徑 | 異動類型 | 描述 |
|---------|----------|------|
| `scripts/civitai_manager_libs/recipe_action.py` | 修改 | 修正 on_recipe_input_change() 的資料傳遞與元數據提取 |
| `tests/test_send_to_recipe_fix.py` | 新增/修改 | 添加/更新單元測試與整合測試 |
| `.github/plans/bugs/002-send-to-recipe-prompt-extraction-bug.md` | 新增 | 詳細 backlog 文件 |
