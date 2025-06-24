---
title: "Job Report: Backlog #003 - Refactor Gallery Downloads"
date: "2025-06-22T21:29:00Z"
---

# [Backlog] #003 - Refactor Gallery Downloads 工作報告

**日期**：2025-06-22T21:29:00Z  
**任務**：重構 `civitai_gallery_action.py` 圖片下載邏輯，整合中央化 HTTP 客戶端並完善錯誤處理、重試與使用者回饋機制  
**類型**：Backlog  
**狀態**：已完成

## 一、任務概述
專案中 `civitai_gallery_action.py` 於多處直接採用 `requests.get(..., stream=True)` 實作圖片下載，
缺乏統一錯誤處理、重試機制與進度回饋，且下載失敗未提供使用者提示，影響穩定性與使用體驗。
本任務需將所有下載邏輯遷移至中央化的 `CivitaiHttpClient`，並依照 Backlog 要求重構：
- 整合 HTTP 客戶端實例  
- 重構 `download_images()`、`gallery_loading()`、`download_user_gallery_images()` 等下載流程  
- 支援串流回應與批次、重試管理  
- 加入進度/錯誤提示  

## 二、實作內容

### 2.1 整合 HTTP 客戶端
- 新增 `get_http_client()` 以單一模組級別實例管理 `CivitaiHttpClient`，統一超時與重試設定【F:scripts/civitai_manager_libs/civitai_gallery_action.py†L38-L51】
- 引入 `CivitaiHttpClient` 並置於頂層，消除分散 `requests.get` 呼叫【F:scripts/civitai_manager_libs/civitai_gallery_action.py†L38-L41】

### 2.2 實作單圖下載助手
- 新增 `_download_single_image()`，封裝下載失敗與日誌記錄，供各下載流程共用【F:scripts/civitai_manager_libs/civitai_gallery_action.py†L53-L64】

### 2.3 重構批量下載函式 `download_images()`
- 取代原生 `requests.get`，使用 `client.download_file()`；計算成功/失敗數目並顯示錯誤提示【F:scripts/civitai_manager_libs/civitai_gallery_action.py†L770-L801】

### 2.4 重構清單與用戶畫廊下載流程
- `gallery_loading()` 與 `download_user_gallery_images()` 改以 `_download_single_image()` 處理 URL 下載，失敗改以預設佔位圖替換【F:scripts/civitai_manager_libs/civitai_gallery_action.py†L1019-L1023】【F:scripts/civitai_manager_libs/civitai_gallery_action.py†L1063-L1070】

### 2.5 支援串流回應與自訂寫入
- 在 `CivitaiHttpClient` 中加入 `get_stream_response()` 供自訂串流處理使用【F:scripts/civitai_manager_libs/http_client.py†L172-L174】

### 2.6 增加設定項目
- `setting.py` 中新增下載批次大小、逾時與最大併發設定，以便後續擴充批次下載與速率限制【F:scripts/civitai_manager_libs/setting.py†L215-L218】

## 三、技術細節

1. 刪減各處重複下載邏輯，由 `_download_single_image()` 統一呼叫  
2. `download_images()` 加入成功/失敗計數與 3 秒錯誤提示  
3. `gallery_loading()` 與 `download_user_gallery_images()` 維持原 API 介面不改變  

## 四、測試與驗證

### 4.1 程式碼品質檢查
```bash
black --line-length=100 --skip-string-normalization \
  scripts/civitai_manager_libs/civitai_gallery_action.py \
  scripts/civitai_manager_libs/http_client.py \
  scripts/civitai_manager_libs/setting.py \
  tests/test_civitai_gallery_action.py
flake8 scripts/civitai_manager_libs/civitai_gallery_action.py \
  scripts/civitai_manager_libs/http_client.py \
  scripts/civitai_manager_libs/setting.py \
  tests/test_civitai_gallery_action.py
pytest -q --disable-warnings --maxfail=1 tests/test_civitai_gallery_action.py
```

### 4.2 功能測試
- 單元測試涵蓋：
  - `_download_single_image()` 的成功/失敗行為  
  - `download_images()` 正常與部分失敗下載行為  
  - `gallery_loading()` URL 下載失敗替換與回傳格式  
  - `download_user_gallery_images()` 資料夾結構與檔案生成  

## 五、影響評估

- 向後相容：不改變外部函式簽名，僅優化內部下載實作  
- 使用者體驗：下載失敗明確提示，預期下載更穩定  

## 六、後續事項

- 建議將其他模組（如 `downloader.py`、`ishortcut.py`）下載邏輯續行中央化遷移

## 七、檔案異動清單

| 檔案路徑                                                         | 異動類型 | 描述                                           |
|-----------------------------------------------------------------|--------|----------------------------------------------|
| `scripts/civitai_manager_libs/civitai_gallery_action.py`         | 修改   | 統一下載邏輯，整合 HTTP 客戶端，改用 `_download_single_image()` |
| `scripts/civitai_manager_libs/http_client.py`                   | 修改   | 新增 `get_stream_response()` 方法              |
| `scripts/civitai_manager_libs/setting.py`                       | 修改   | 新增下載批次與逾時等設定項                    |
| `tests/test_civitai_gallery_action.py`                          | 新增   | 單元測試：覆蓋核心下載流程與錯誤處理行為         |
