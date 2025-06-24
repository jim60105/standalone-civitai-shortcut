---
title: "Job Report: Backlog #046 - HTTP client core refactoring (Stage 1)"
date: "2025-06-23T03:06:28Z"
---

# Backlog #046 - HTTP client core refactoring (Stage 1) 工作報告

**日期**：2025-06-23T03:06:28Z  
**任務**：實作 Backlog 009 階段一：重構核心 HTTP client 模組，移除監控與過度設計，增設統一工廠函式  
**類型**：Backlog  
**狀態**：已完成

## 一、任務概述

按照 `.github/plans/centralized-http-client/009-optimize-http-migration.md` 規劃，階段一於 `http_client.py` 中移除冗餘的性能與監控類別，並在 `util.py` 中消除對 `CivitaiHttpClient` 的直接引用，引入全域工廠函式以簡化架構並解決循環依賴問題。

## 二、實作內容

### 2.1 重構 `http_client.py`
- 移除過度的性能與監控擴展類別：`OptimizedHTTPClient`、`MemoryEfficientDownloader`、`IntelligentCache`
- 更新 `ChunkedDownloader` 構造函數，使用 `CivitaiHttpClient` 作為依賴【F:scripts/civitai_manager_libs/http_client.py†L280-L283】
- 新增全域工廠函式 `get_http_client()` 與 `get_chunked_downloader()`【F:scripts/civitai_manager_libs/http_client.py†L410-L428】
- 移除未使用的匯入：`random`、`HTTPAdapter`、`Retry`【F:scripts/civitai_manager_libs/http_client.py†L11-L13】

### 2.2 更新 `util.py`
- 刪除模組層級對 `CivitaiHttpClient` 的匯入，改於函式內使用 `get_http_client()`【F:scripts/civitai_manager_libs/util.py†L8-L9】【F:scripts/civitai_manager_libs/util.py†L469-L472】
- 調整 `download_with_cache_and_retry()`，改採 `get_http_client()` 而非直接實例化，破除循環依賴【F:scripts/civitai_manager_libs/util.py†L543-L547】
- 修正多處裸 `except` 及過長註解以通過 Flake8 檢查【F:scripts/civitai_manager_libs/util.py†L97-L102】【F:scripts/civitai_manager_libs/util.py†L215-L218】【F:scripts/civitai_manager_libs/util.py†L372-L377】

## 三、技術細節

### 3.1 架構變更
集中統一使用單一 `CivitaiHttpClient`，消除複雜監控與擴展設計，符合 DRY/KISS 原則。

### 3.2 API 變更
- 引入 `get_http_client()` 與 `get_chunked_downloader()` 函式做為全域工廠
- 移除不再使用的 `OptimizedHTTPClient`、`MemoryEfficientDownloader`、`IntelligentCache` 類別

## 四、測試與驗證

### 4.1 程式碼品質檢查
```bash
black --line-length=100 --skip-string-normalization \
  scripts/civitai_manager_libs/http_client.py scripts/civitai_manager_libs/util.py
flake8 scripts/civitai_manager_libs/http_client.py scripts/civitai_manager_libs/util.py
```

### 4.2 單元測試
```bash
python3 -m pytest \
  tests/test_http_client.py tests/test_downloader.py \
  tests/test_ishortcut_http.py tests/test_civitai.py -q
```
所有相關單元測試皆已通過。

## 五、影響評估

### 5.1 向後相容性
僅內部重構，對外呼叫介面僅新增工廠函式，保留原 `CivitaiHttpClient` 方法，不影響現有使用方式。

### 5.2 使用者體驗
程式最終行為一致，使用者操作無差異。

## 六、問題與解決方案

無重大阻礙，過程順利完成。

## 七、後續事項

### 7.1 待完成項目
- [ ] 將其他模組依賴改為工廠函式（階段二）
- [ ] 刪除 `monitoring.py` 及相關性能測試檔案
- [ ] 更新 `setting.py` 移除監控參數
- [ ] 更新整合測試

## 八、檔案異動清單

| 檔案路徑                                        | 異動類型 | 描述                                       |
|-----------------------------------------------|--------|------------------------------------------|
| `scripts/civitai_manager_libs/http_client.py` | 修改   | 重構 HTTP client，移除監控/擴展類別，新增工廠函式 |
| `scripts/civitai_manager_libs/util.py`        | 修改   | 移除直接實例化，改用 `get_http_client()`，修正裸 `except` |
