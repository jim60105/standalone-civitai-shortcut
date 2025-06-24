---
title: "Job Report: Backlog #038 - Centralized HTTP Client Implementation"
date: "2025-06-22T21:00:18Z"
---

# [Backlog] #038 - Centralized HTTP Client Implementation 工作報告

**日期**：2025-06-22T21:00:18Z  
**任務**：實作 Backlog 001 與 002，建立核心 HTTP 客戶端並重構 civitai 模組以使用中央化客戶端  
**類型**：Backlog  
**狀態**：已完成

## 一、任務概述
由於專案中 HTTP 請求分散且缺乏統一的錯誤處理、超時與重試機制，
需建立中央化的 `CivitaiHttpClient`，並將 `civitai.py` 模組中所有直接的 `requests.get/post`
呼叫改為透過此客戶端，以達成一致性及優雅降級。

## 二、實作內容

### 2.1 建立核心 HTTP 客戶端 (Backlog 001)
- 實作 `CivitaiHttpClient` 類別，支援 GET/POST、timeout、retry、Bearer token 驗證與串流下載
- 統一錯誤處理，並依 HTTP 狀態碼顯示使用者友善的訊息
- 新增設定項目於 `setting.py`：`http_timeout`, `http_max_retries`, `http_retry_delay`
- 測試 `http_client` 核心功能與錯誤案例

```python
# Example usage
client = CivitaiHttpClient(api_key="KEY", timeout=20, max_retries=3)
data = client.get_json(url)
``` 

- 檔案變更：
  - 新增 `scripts/civitai_manager_libs/http_client.py`【F:scripts/civitai_manager_libs/http_client.py†L1-L170】
  - 更新 `scripts/civitai_manager_libs/setting.py`【F:scripts/civitai_manager_libs/setting.py†L66-L68】
  - 新增對應單元測試 `tests/test_http_client.py`【F:tests/test_http_client.py†L1-L160】

### 2.2 重構 civitai 模組使用中央化 HTTP 客戶端 (Backlog 002)
- 匯入 `CivitaiHttpClient`，並實作 `get_http_client()`：模組級別單一實例管理與動態更新 API key
- 將 `request_models()`, `get_model_info()`, `get_version_info_by_hash()`, `get_version_info_by_version_id()` 等函式
  重構為透過客戶端呼叫 `get_json()`，並維持原有簽名與行為
- 修正 `request_models()` 失敗時回傳空資料結構以避免下游錯誤
- 新增 `get_http_client` 行為測試

```python
# refactored example
client = get_http_client()
data = client.get_json(endpoint)
``` 

- 檔案變更：
  - 修改 `scripts/civitai_manager_libs/civitai.py`【F:scripts/civitai_manager_libs/civitai.py†L1-L110】
  - 更新 `tests/test_civitai.py` 新增 `get_http_client` 測試 【F:tests/test_civitai.py†L85-L105】

## 三、技術細節

### 3.1 架構變更
- 新增 HTTP 層抽象 `http_client.py`，集中管理所有網路請求與錯誤邏輯

### 3.2 API 變更
- 對外提供 `CivitaiHttpClient.get_json/post_json/get_stream/download_file` 方法
- `civitai.py` 對外 API 保持原介面，僅內部呼叫路徑改變

### 3.3 配置變更
- 在 `setting.py` 中新增 `http_timeout`, `http_max_retries`, `http_retry_delay` 設定

## 四、測試與驗證

### 4.1 程式碼品質檢查
```bash
black --line-length=100 --skip-string-normalization \
  scripts/civitai_manager_libs/http_client.py tests/test_http_client.py tests/test_civitai.py
flake8 scripts/civitai_manager_libs/http_client.py tests/test_http_client.py tests/test_civitai.py
pytest --disable-warnings --maxfail=1 tests/test_http_client.py tests/test_civitai.py
```

### 4.2 功能測試
- 單元測試覆蓋 HTTP 客戶端正常與錯誤情境
- 確認 `get_http_client()` 正確初始化與 API key 動態更新

### 4.3 覆蓋率測試
```bash
pytest --cov=scripts/civitai_manager_libs/http_client --cov-report=term
```

## 五、影響評估

### 5.1 向後相容性
- 所有 `civitai.py` 函式簽名與行為保持不變

### 5.2 使用者體驗
- 統一錯誤訊息與超時/重試機制，提升穩定性與可用性

## 六、問題與解決方案

### 6.1 遇到的問題
- 單元測試中 `_STATUS_CODE_MESSAGES` 未被使用導致 flake8 警告，補充對應測試以移除冗餘警告

### 6.2 技術債務
- 待將其餘模組(下載、畫廊、掃描)的 HTTP 呼叫陸續移植至此客戶端

## 七、後續事項

### 7.1 待完成項目
- [ ] 遷移 `downloader.py`, `ishortcut.py`, `scan_action.py` 中所有直接 HTTP 呼叫

### 7.2 相關任務
- Backlog 003-006: 完成剩餘模組中央化 HTTP 客戶端遷移

### 7.3 建議的下一步
- 實作使用者介面顯示請求重試進度等進階功能

## 八、檔案異動清單
| 檔案路徑                                              | 異動類型 | 描述                                   |
|------------------------------------------------------|----------|----------------------------------------|
| `scripts/civitai_manager_libs/http_client.py`        | 新增     | 核心 HTTP 客戶端實作                   |
| `scripts/civitai_manager_libs/setting.py`            | 修改     | 新增 HTTP client 設定                  |
| `scripts/civitai_manager_libs/civitai.py`            | 修改     | 重構為使用中央化 HTTP 客戶端           |
| `tests/test_http_client.py`                         | 修改     | 新增單元測試，涵蓋 GET/POST/串流/下載等 |
| `tests/test_civitai.py`                             | 修改     | 新增 `get_http_client` 初始化測試      |
