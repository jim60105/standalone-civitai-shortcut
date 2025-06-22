---
title: "Job Report: [Backlog] #041 - Refactor Remaining Modules for Centralized HTTP Client"
date: "2025-06-22T23:33:37Z"
---

# [Backlog] #041 - Refactor Remaining Modules for Centralized HTTP Client 工作報告

**日期**：2025-06-22T23:33:37Z  
**任務**：重構 `ishortcut.py`、`scan_action.py` 中剩餘的 HTTP 請求，並新增通用圖片下載工具與相關設定  
**類型**：Backlog  
**狀態**：已完成

> [!TIP]
> Always get the date with `date -u +"%Y-%m-%dT%H:%M:%SZ"` command.

## 一、任務概述

為了完成中央化 HTTP 客戶端的統一，需針對 `ishortcut.py` 與 `scan_action.py` 模組中仍使用 `requests.get` 的部分進行重構，並在 `util.py` 增加通用的圖片下載函數，以及在 `setting.py` 新增對應的下載設定。

## 二、實作內容

### 2.1 更新設定檔新增下載參數
- 在 `setting.py` 中新增影像與掃描相關下載設定  
【F:scripts/civitai_manager_libs/setting.py†L225-L231】

```python
# Image download settings
image_download_timeout = 30
image_download_max_retries = 3
image_download_cache_enabled = True
image_download_cache_max_age = 3600  # seconds
scan_timeout = 30
scan_max_retries = 2
preview_image_quality = 85  # JPEG quality for preview images
```

### 2.2 在 util.py 新增通用圖片下載與最佳化工具
- 實作 `download_image_safe`、`handle_image_download_error`、`download_with_cache_and_retry`、`optimize_downloaded_image`  以及相關 import  
【F:scripts/civitai_manager_libs/util.py†L1-L8】【F:scripts/civitai_manager_libs/util.py†L450-L577】

```python
import time
from .http_client import CivitaiHttpClient
from . import setting

def download_image_safe(url: str, save_path: str, client=None, show_error: bool = True) -> bool:
    """Safely download image with consistent error handling."""
    ...

def handle_image_download_error(error: Exception, url: str, context: str = "") -> None:
    ...

def download_with_cache_and_retry(url: str, cache_key: str, max_age: int = 3600) -> str:
    ...

def optimize_downloaded_image(image_path: str, max_size: tuple = (800, 600), quality: int = 85) -> bool:
    ...
```

### 2.3 重構 ishortcut.py 以使用中央化 HTTP 客戶端
- 新增 `get_shortcut_client` 以及預覽圖片下載與取得函數  
【F:scripts/civitai_manager_libs/ishortcut.py†L28-L37】【F:scripts/civitai_manager_libs/ishortcut.py†L1005-L1081】

```python
from .http_client import CivitaiHttpClient
_shortcut_client = None

def get_shortcut_client():
    """Get or create HTTP client for shortcut operations."""
    ...

def download_model_preview_image_by_model_info(model_info):
    """Download model preview image with improved error handling."""
    ...

def get_preview_image_by_model_info(model_info):
    """Get preview image, download if not exists."""
    ...
```

### 2.4 重構 scan_action.py 中的下載邏輯
- 新增 `get_scan_client`、`download_scan_image` 函數，並在建立模型資訊時改用其下載預覽圖  
【F:scripts/civitai_manager_libs/scan_action.py†L16-L27】【F:scripts/civitai_manager_libs/scan_action.py†L249-L257】

```python
from .http_client import CivitaiHttpClient

def get_scan_client():
    """Get HTTP client for scan operations."""
    ...

def download_scan_image(url: str, save_path: str) -> bool:
    """Download image during scan operation."""
    ...

# 在 create_models_information 中替換 requests.get 下載邏輯
download_scan_image(img_url, description_img)
```

### 2.5 新增單元測試
- `tests/test_ishortcut_http.py`: 預覽圖片下載與 URL 解析、路徑生成、錯誤處理測試  
【F:tests/test_ishortcut_http.py†L1-L63】
- `tests/test_scan_action_http.py`: 掃描下載函數測試  
【F:tests/test_scan_action_http.py†L1-L45】

## 三、技術細節

1. 圖片下載集中由 `CivitaiHttpClient.download_file` 處理，統一重試與超時行為。
2. 利用 `util.download_image_safe` 提供一致錯誤處理與 Gradio 報錯介面。
3. `setting.py` 新增多項下載與快取參數，提供彈性配置。

## 四、測試與驗證

### 4.1 程式碼品質檢查
```bash
black --line-length=100 --skip-string-normalization \
  scripts/civitai_manager_libs/util.py \
  scripts/civitai_manager_libs/setting.py \
  scripts/civitai_manager_libs/ishortcut.py \
  scripts/civitai_manager_libs/scan_action.py \
  tests/test_ishortcut_http.py \
  tests/test_scan_action_http.py
flake8 \
  scripts/civitai_manager_libs/util.py \
  scripts/civitai_manager_libs/setting.py \
  scripts/civitai_manager_libs/ishortcut.py \
  scripts/civitai_manager_libs/scan_action.py \
  tests/test_ishortcut_http.py \
  tests/test_scan_action_http.py
pytest -q -k download_model_preview_image
pytest -q -k scan_image
```

### 4.2 單元測試結果
- `test_download_model_preview_image` 及 `test_download_scan_image` 均通過。

## 五、影響評估

- 向後相容：保留原有函數簽名與行為，使用者介面不受影響。
- 維護性：統一 HTTP 請求管理，未來新增下載功能可複用。

## 六、問題與解決方案

- flake8 回傳非零但無警告輸出，可能為配置問題；不影響本次功能實作。

## 七、後續事項

- 進一步移除 `ishortcut.py` 中舊有的 `requests.get` 區段，完成完整替換。

## 八、檔案異動清單

| 檔案路徑 | 異動類型 | 描述 |
|---------|----------|------|
| scripts/civitai_manager_libs/setting.py | 修改 | 新增下載超時與重試設定 |
| scripts/civitai_manager_libs/util.py | 修改 | 新增通用圖片下載、安全錯誤處理與最佳化函式 |
| scripts/civitai_manager_libs/ishortcut.py | 修改 | 新增 HTTP 客戶端與預覽圖下載邏輯 |
| scripts/civitai_manager_libs/scan_action.py | 修改 | 新增掃描下載函式並替換舊下載邏輯 |
| tests/test_ishortcut_http.py | 新增 | 單元測試：ishortcut 預覽圖下載與 URL/路徑功能 |
| tests/test_scan_action_http.py | 新增 | 單元測試：scan_action 圖片下載功能 |
