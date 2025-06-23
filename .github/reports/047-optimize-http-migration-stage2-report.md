---
title: "Job Report: Backlog #047 - HTTP client core refactoring (Stage 2)"
date: "2025-06-23T03:43:50Z"
---

# Backlog #047 - HTTP client core refactoring (Stage 2) 工作報告

**日期**：2025-06-23T03:43:50Z  
**任務**：實作 Backlog 009 階段二：更新各模組以統一使用集中式 HTTP 客戶端（Factory）  
**類型**：Backlog  
**狀態**：已完成

## 一、任務概述

按照 `.github/plans/centralized-http-client/009-optimize-http-migration.md` 規劃，階段二負責更新所有原先各自建立 HTTP 客戶端的模組，改為統一引入 `get_http_client()` 與 `get_chunked_downloader()`，移除模組內的 Factory 函式與直接實例化，簡化程式依賴。

## 二、實作內容

### 2.1 更新 `civitai.py`
- 移除模組層級 `get_http_client()` 與 `_http_client` 全域變數
- 改為從集中式工廠函式匯入 `get_http_client()`【F:scripts/civitai_manager_libs/civitai.py†L5-L12】

### 2.2 更新 `downloader.py`
- 移除 `get_download_client()` 與 `CivitaiHttpClient` 匯入
- 引入 `get_http_client()` 與 `get_chunked_downloader()`
- 重構 `download_file`、`download_file_gr` 為透過 `ChunkedDownloader` 實作
- 更新 `DownloadManager` 中的客戶端建立改為 `get_http_client()`【F:scripts/civitai_manager_libs/downloader.py†L7-L13】【F:scripts/civitai_manager_libs/downloader.py†L82-L91】【F:scripts/civitai_manager_libs/downloader.py†L101-L106】

### 2.3 更新 `ishortcut.py`
- 移除 `get_shortcut_client()` 和對 `CivitaiHttpClient` 的直接匯入
- 改為集中式 `get_http_client()`，並替換所有呼叫點【F:scripts/civitai_manager_libs/ishortcut.py†L15-L23】【F:scripts/civitai_manager_libs/ishortcut.py†L563-L571】

### 2.4 更新 `scan_action.py`
- 刪除原 `get_scan_client()` 定義及 `CivitaiHttpClient` 匯入
- 改為引入並使用 `get_http_client()`【F:scripts/civitai_manager_libs/scan_action.py†L11-L19】

### 2.5 更新 `civitai_gallery_action.py`
- 移除原 `get_http_client()` 定義與 `_http_client` 全域變數
- 改為匯入集中式 `get_http_client()`【F:scripts/civitai_manager_libs/civitai_gallery_action.py†L35-L43】

### 2.6 模組包初始化
- 新增 `scripts/__init__.py` 與 `scripts/civitai_manager_libs/__init__.py`，使 `scripts` 成為可匯入套件，支援測試模組匯入路徑。

## 三、技術細節

### 3.1 架構變更
- 將所有模組對 HTTP 客戶端的建立集中化，移除各自 Factory，符合 DRY/KISS 原則。

### 3.2 API 變更
- 介面函式僅限 `get_http_client()`、`get_chunked_downloader()`；移除舊有 `get_download_client()`、`get_shortcut_client()`、`get_scan_client()`。

## 四、測試與驗證

> 本階段僅更新模組實作，測試檔案將於下一階段同步調整。

## 五、後續事項

### 5.1 待完成項目
- 更新並修正單元與整合測試，使其符合新客戶端建構方式（階段四）。
- 刪除監控模組與相關測試（階段三）。

## 六、檔案異動清單

| 檔案路徑                                             | 異動類型 | 描述                             |
|----------------------------------------------------|--------|--------------------------------|
| `scripts/civitai_manager_libs/civitai.py`          | 修改   | 使用集中式 `get_http_client()` |
| `scripts/civitai_manager_libs/downloader.py`       | 修改   | 使用 `get_chunked_downloader()`, 移除 `get_download_client()` |
| `scripts/civitai_manager_libs/ishortcut.py`        | 修改   | 替換為 `get_http_client()`      |
| `scripts/civitai_manager_libs/scan_action.py`      | 修改   | 替換為 `get_http_client()`      |
| `scripts/civitai_manager_libs/civitai_gallery_action.py` | 修改   | 替換為 `get_http_client()` |
| `scripts/__init__.py`                              | 新增   | 套件標記                         |
| `scripts/civitai_manager_libs/__init__.py`         | 新增   | 套件標記                         |
