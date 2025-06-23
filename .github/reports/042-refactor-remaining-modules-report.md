---
title: "Job Report: [Backlog] #005 - Refactor Remaining Modules for Centralized HTTP Client"
date: "2025-06-23T00:48:44Z"
---

# [Backlog] #005 - Refactor Remaining Modules for Centralized HTTP Client 工作報告

**日期**：2025-06-23T00:48:44Z  
**任務**：依據 `.github/plans/centralized-http-client/005-refactor-remaining-modules.md` 完成 `ishortcut.py` 中所有 HTTP 請求重構，移除手動 `requests.get` 區段，並使用中央化 HTTP 客戶端統一下載邏輯。  
**類型**：Refactor  
**狀態**：已完成

> 本任務依據 `.github/plans/centralized-http-client/005-refactor-remaining-modules.md` 執行。
【F:.github/plans/centralized-http-client/005-refactor-remaining-modules.md†L1-L240】

## 一、任務概述

原有 `ishortcut.py` 中仍存在多處手動使用 `requests.get` 下載模型與預覽圖的程式片段，增加維護負擔且無法統一錯誤與重試行為。此任務目標為：
- 移除所有手動 HTTP 請求敘述
- 改以中央化 `CivitaiHttpClient` 與 `util.download_image_safe` 處理
- 簡化程式流程並保持向後相容

## 二、實作內容

### 2.1 移除舊有縮圖下載實作，改以 `download_image_safe`
- 刪除 `download_thumbnail_image_old` 與原始 `download_thumbnail_image` 實作  
【F:scripts/civitai_manager_libs/ishortcut.py†L839-L891】
- 實作全新 `download_thumbnail_image`，使用 `get_shortcut_client` 與 `util.download_image_safe`，完成縮圖生成  
【F:scripts/civitai_manager_libs/ishortcut.py†L839-L891】

### 2.2 重構 `add()` 中批次圖片下載邏輯
- 移除原先分支與 `requests.get` Raw 複製邏輯
- 使用迴圈與 `util.download_image_safe` 統一下載並計數  
【F:scripts/civitai_manager_libs/ishortcut.py†L574-L647】

## 三、技術細節

- 使用 `get_shortcut_client()` 取得單例客戶端，統一超時、重試與進度回調。
- `util.download_image_safe` 統一錯誤處理與 Gradio 報錯介面，自動建立目錄。
- 縮圖生成保留原功能，加入錯誤輸出以協助偵錯。

## 四、測試與驗證

### 4.1 程式碼品質檢查
```bash
black --line-length=100 --skip-string-normalization scripts/civitai_manager_libs/ishortcut.py
flake8 scripts/civitai_manager_libs/ishortcut.py
pytest -q tests/test_ishortcut_http.py tests/test_scan_action_http.py
```

### 4.2 單元測試結果
- `test_download_model_preview_image`, `test_get_preview_image_by_model_info`、`test_download_scan_image` 測試皆通過。

## 五、影響評估

### 5.1 向後相容性
- 維持原有 public API 與檔案結構，使用者介面與快捷鍵資料不受影響。

### 5.2 維護性
- 統一 HTTP 請求邏輯，減少重複程式碼並集中錯誤處理。

## 六、問題與解決方案

**問題描述**：手動 Raw copy 增加程式複雜度且無統一錯誤機制。
**解決方案**：集中使用 `CivitaiHttpClient.download_file` 及 `util.download_image_safe`，失敗時依場景自動退回預設行為。

## 七、後續事項

- [ ] 增加整合測試覆蓋 `add()` 批次下載錯誤與中斷情境。

## 八、檔案異動清單

| 檔案路徑                                        | 異動類型 | 描述                                    |
|-----------------------------------------------|---------|---------------------------------------|
| `scripts/civitai_manager_libs/ishortcut.py`   | 修改    | 移除手動 HTTP 請求，改用中央化下載邏輯 |
| `.github/plans/centralized-http-client/005-refactor-remaining-modules.md` | 參考    | 本次實作依據                           |
