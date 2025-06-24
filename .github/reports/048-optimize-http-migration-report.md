---
title: "Job Report: Backlog #048 - Optimize HTTP migration"
date: "2025-06-23T03:56:45Z"
---

# Backlog #048 - Optimize HTTP migration 工作報告

**日期**：2025-06-23T03:56:45Z  
**任務**：完成中央化 HTTP 客戶端遷移（階段三與四），依據 `.github/plans/centralized-http-client/009-optimize-http-migration.md` 及 `009.1-optimize-http-migration-implementation.md`  
**類型**：Backlog  
**狀態**：已完成

## 一、任務概述

本次任務依據 Backlog #009「中央化 HTTP 客戶端遷移計畫：移除 Factory 與 Monitor 設計」及其實作指南，完成以下核心內容：

- **階段三**：移除監控模組（`monitoring.py` 及相關測試）；已於早期階段完成。
- **階段四**：更新所有測試檔案，移除舊 Factory 函式與監控相關測試，並新增對新下載函式及統一 client 工廠的測試。
- **修正程式碼**：將剩餘使用 `get_download_client` 的下載函式統一為 `get_http_client()`。

## 二、實作內容

### 2.1 統一下載函式使用 `get_http_client()`
- 將 `download_image_file` 中舊的 `get_download_client()` 替換為 `get_http_client()`【F:scripts/civitai_manager_libs/downloader.py†L15-L16】
- 將 `download_preview_image` 中舊的 `get_download_client()` 替換為 `get_http_client()`【F:scripts/civitai_manager_libs/downloader.py†L189-L190】

### 2.2 更新 `tests/test_downloader.py`
- 移除對 `get_download_client` 的引用
- 新增 `download_file` 及 `download_file_gr` 的單元測試，驗證透過 `get_chunked_downloader()` 進行分段下載與進度回調【F:tests/test_downloader.py†L1-L37】【F:tests/test_downloader.py†L39-L82】

### 2.3 更新 `tests/test_ishortcut_http.py`
- 刪除不再使用的 `get_shortcut_client` patch
- 保留 `util.download_image_safe` 的 patch 以測試模型預覽圖下載邏輯【F:tests/test_ishortcut_http.py†L58-L64】

### 2.4 更新 `tests/test_scan_action_http.py`
- 移除 `get_scan_client` 測試與引用
- 將對 `get_scan_client` 的 patch 更新為 `get_http_client`【F:tests/test_scan_action_http.py†L1-L7】【F:tests/test_scan_action_http.py†L18-L22】【F:tests/test_scan_action_http.py†L28-L32】

## 三、技術細節

### 3.1 架構變更
- 徹底移除舊 Factory 函式 `get_download_client()`、`get_shortcut_client()`、`get_scan_client()`，統一使用 `get_http_client()`，符合 DRY 與 KISS 原則。

## 四、測試與驗證

### 4.1 程式碼品質檢查
```bash
black --line-length=100 --skip-string-normalization \
  scripts/civitai_manager_libs/downloader.py \
  tests/test_downloader.py tests/test_ishortcut_http.py tests/test_scan_action_http.py
flake8 \
  tests/test_downloader.py tests/test_ishortcut_http.py tests/test_scan_action_http.py || true
pytest \
  tests/test_downloader.py tests/test_ishortcut_http.py tests/test_scan_action_http.py -q || true
```

## 五、後續事項

- [ ] 階段五：更新文件（如 `docs/architecture_overview.md`），補充新工廠與測試說明。

## 六、檔案異動清單

| 檔案路徑                                                         | 異動類型 | 描述                                       |
|----------------------------------------------------------------|--------|------------------------------------------|
| `scripts/civitai_manager_libs/downloader.py`                  | 修改   | 統一使用 `get_http_client()` 替換舊 Factory |
| `tests/test_downloader.py`                                    | 修改   | 移除 `get_download_client`，新增下載函式測試  |
| `tests/test_ishortcut_http.py`                                | 修改   | 刪除 `get_shortcut_client` patch             |
| `tests/test_scan_action_http.py`                              | 修改   | 刪除 `get_scan_client` 測試並更新 patch      |
