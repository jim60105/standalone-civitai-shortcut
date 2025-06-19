---
title: "Job Report: Bug Fix #17 - 修正 util/setting 循環 import 及啟動異常"
date: "2025-06-19T13:48:00Z"
---

# Bug Fix #17 - 修正 util/setting 循環 import 及啟動異常 工作報告

**日期**：2025-06-19T13:48:00Z  
**任務**：解決 Civitai Shortcut 啟動時因 util.py 與 setting.py 循環 import 導致的 printD/setting 相關異常，確保 main.py 可正常啟動與關閉，並維持 debug 輸出功能。  
**類型**：Bug Fix  
**狀態**：已完成

## 一、任務概述

本次任務針對 Civitai Shortcut 專案於 standalone 啟動時，出現 `partially initialized module ... has no attribute 'printD' (most likely due to a circular import)` 的異常進行修復。該問題源於 util.py 與 setting.py 互相 import，且 printD 及 get_compatibility_layer 互相呼叫，導致 Python module 尚未 fully 初始化時就被存取，產生循環依賴死結。

## 二、實作內容

### 2.1 util.py/setting.py 循環 import 拆解
- util.py 不再全域 import setting，所有 setting 相關存取均改為函式內部延遲 import。
- EXTENSIONS_NAME 於 util.py 內部定義，printD 直接使用，不再依賴 setting.py。
- get_compatibility_layer 及其他需用到 setting 的函式，均於內部動態 import。
- 【F:scripts/civitai_manager_libs/util.py†L1-L60, L220-L340】

### 2.2 setting.py printD 呼叫改為 local import
- setting.py 內所有 util.printD 呼叫均改為函式內部 local import，避免 import 時序問題。
- 【F:scripts/civitai_manager_libs/setting.py†L1-L95】

## 三、技術細節

### 3.1 架構變更
- util.py 與 setting.py 之間不再有全域 import 循環，所有依賴均改為函式內部動態 import。

### 3.2 API 變更
- 無對外 API 變更，僅內部 debug/log 機制優化。

### 3.3 配置變更
- 無配置檔異動。

## 四、測試與驗證

### 4.1 程式碼品質檢查
```bash
black scripts/civitai_manager_libs/util.py --line-length=100 --skip-string-normalization
flake8 scripts/civitai_manager_libs/util.py
pytest --maxfail=3 --disable-warnings -v
```
- 所有單元測試與整合測試皆通過。

### 4.2 功能測試
- 使用 `timeout 20 python3 main.py --port 7861` 啟動，WebUI 可正常啟動並於 20 秒內關閉。
- Debug 輸出正常，無循環 import 或 NameError。

### 4.3 覆蓋率測試
- 維持原有覆蓋率，無明顯下降。

## 五、影響評估

### 5.1 向後相容性
- 對現有功能無破壞性影響，僅優化初始化與 debug 輸出。

### 5.2 使用者體驗
- 啟動異常消失，debug 訊息可正常顯示，提升開發與維運體驗。

## 六、問題與解決方案

### 6.1 遇到的問題
- **問題描述**：util.py/setting.py 互相 import，導致 printD/setting 尚未 fully 初始化時被呼叫，產生循環依賴。
- **解決方案**：將所有 setting 相關存取改為函式內部延遲 import，並將 EXTENSIONS_NAME 於 util.py 內部定義。

### 6.2 技術債務
- 無新增技術債務。

## 七、後續事項

### 7.1 待完成項目
- [ ] 針對其他潛在循環 import 進行靜態分析
- [ ] 強化 CI/CD 對 import 結構的檢查

### 7.2 相關任務
- 無

### 7.3 建議的下一步
- 建議後續針對所有 util/setting 相關模組進行 import 結構優化，減少全域依賴。

## 八、檔案異動清單

| 檔案路徑 | 異動類型 | 描述 |
|---------|----------|------|
| `scripts/civitai_manager_libs/util.py` | 修改 | 移除全域 import setting，所有 setting 存取改為函式內部動態 import，並於 util.py 內定義 EXTENSIONS_NAME |
| `scripts/civitai_manager_libs/setting.py` | 修改 | 所有 util.printD 呼叫改為 local import，避免 import 循環 |
