# 中央化 HTTP 客戶端遷移計畫：移除 Factory 與 Monitor 設計

## 計畫概述

本計畫旨在簡化當前的 centralized HTTP client 架構，移除複雜的 Factory 設計模式和 Monitor 監控機制，統一使用 `OptimizedHTTPClient` 和 `ChunkedDownloader`，減少系統複雜度並消除冗餘設計。

## 背景分析

### 當前狀況

專案已完成 centralized HTTP client 的基礎建設（Backlog 01-07），但存在以下問題：

1. **多重 Factory 函數**：
   - `get_http_client()` in `civitai.py` - 返回 `CivitaiHttpClient`
   - `get_download_client()` in `downloader.py` - 返回 `CivitaiHttpClient`
   - `get_shortcut_client()` in `ishortcut.py` - 返回 `CivitaiHttpClient`
   - `get_http_client()` in `monitoring.py` - 返回 `OptimizedHTTPClient`

2. **複雜的類別層次**：
   - `CivitaiHttpClient` - 基礎客戶端
   - `OptimizedHTTPClient` - 優化版客戶端（繼承自 `CivitaiHttpClient`）
   - `ChunkedDownloader` - 依賴 `OptimizedHTTPClient`
   - `MemoryEfficientDownloader` - 記憶體監控（僅用於監控目的）

3. **監控模組冗餘**：
   - `monitoring.py` - 完整的監控系統和 UI
   - `HTTPClientMonitor` - 統計收集器
   - 監控 UI 在 WebUI 中不常使用

### 問題分析

1. **設計冗餘**：多個 Factory 函數本質上都在創建相同功能的 HTTP 客戶端
2. **技術債務**：`CivitaiHttpClient` 與 `OptimizedHTTPClient` 功能重疊
3. **複雜度過高**：Monitor 系統增加了不必要的系統複雜度
4. **未實際使用**：`OptimizedHTTPClient` 和 `ChunkedDownloader` 已實作但未廣泛使用

## 遷移目標

### 主要目標

1. **統一 HTTP 客戶端**：全面遷移到 `OptimizedHTTPClient`
2. **簡化工廠模式**：只保留一個全域 HTTP 客戶端獲取函數
3. **移除監控模組**：刪除 `monitoring.py` 和相關監控功能
4. **消除冗餘設計**：移除 `CivitaiHttpClient` 和 `MemoryEfficientDownloader`
5. **保留核心功能**：保留 `ChunkedDownloader` 的分段下載功能

### 技術原則

- **不考慮向前兼容**：直接替換，不保留舊介面
- **DRY 原則**：移除重複程式碼
- **KISS 原則**：保持設計簡單
- **完全遷移**：不留技術債務

## 實作規劃

### 階段一：重構 HTTP 客戶端結構

#### 1.1 簡化 `http_client.py`

**目標檔案**：`scripts/civitai_manager_libs/http_client.py`

**變更內容**：
1. 移除 `CivitaiHttpClient` 類別
2. 重新命名 `OptimizedHTTPClient` 為 `CivitaiHttpClient`
3. 移除 `MemoryEfficientDownloader` 類別
4. 移除 `IntelligentCache` 類別（如果存在）
5. 簡化 `ChunkedDownloader`，移除不必要的監控功能

**實作細節**：
```python
# 新的 http_client.py 結構
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from typing import Optional, Dict, Callable
import time
import threading
import random

from . import util, setting

class CivitaiHttpClient:
    """Optimized HTTP client with connection pooling, retries, and robust error handling."""
    
    def __init__(self, api_key: Optional[str] = None, timeout: Optional[int] = None, 
                 max_retries: Optional[int] = None, retry_delay: Optional[float] = None):
        # 合併原 OptimizedHTTPClient 的功能到此類別
        pass
    
    # 保留所有原 OptimizedHTTPClient 的方法
    # 移除監控相關的統計收集

class ChunkedDownloader:
    """Downloader supporting chunked and parallel file downloads."""
    
    def __init__(self, client: CivitaiHttpClient):
        # 簡化構造函數，移除監控依賴
        pass
    
    # 保留所有下載方法，移除監控功能
```

#### 1.2 建立統一的客戶端工廠

**目標檔案**：`scripts/civitai_manager_libs/http_client.py`

**新增內容**：
```python
# 全域客戶端實例
_global_http_client = None
_client_lock = threading.Lock()

def get_http_client() -> CivitaiHttpClient:
    """Get or create the global HTTP client instance."""
    global _global_http_client
    if _global_http_client is None:
        with _client_lock:
            if _global_http_client is None:
                _global_http_client = CivitaiHttpClient(
                    api_key=setting.civitai_api_key,
                    timeout=setting.http_timeout,
                    max_retries=setting.http_max_retries,
                    retry_delay=setting.http_retry_delay,
                )
    else:
        # 動態更新 API key
        if _global_http_client.api_key != setting.civitai_api_key:
            _global_http_client.update_api_key(setting.civitai_api_key)
    return _global_http_client

def get_chunked_downloader() -> ChunkedDownloader:
    """Get chunked downloader instance."""
    return ChunkedDownloader(get_http_client())
```

### 階段二：更新所有使用模組

#### 2.1 更新 `civitai.py`

**目標檔案**：`scripts/civitai_manager_libs/civitai.py`

**變更內容**：
1. 移除模組級別的 `_http_client` 和 `get_http_client()`
2. 直接從 `http_client` 模組匯入 `get_http_client`
3. 更新所有使用 HTTP 客戶端的函數

**實作細節**：
```python
# 更新匯入
from .http_client import get_http_client

# 移除舊的工廠函數和全域變數
# 直接使用 get_http_client()

def request_models(nsfw: str = "true", sort: str = "Highest Rated", limit: int = 20, 
                  page: int = 1, query: str = "", tag: str = "", types: list = None):
    client = get_http_client()
    return client.get_json(url, params=params) or {"items": [], "metadata": {}}
```

#### 2.2 更新 `downloader.py`

**目標檔案**：`scripts/civitai_manager_libs/downloader.py`

**變更內容**：
1. 移除 `_download_client` 和 `get_download_client()`
2. 使用統一的 `get_http_client()` 和 `get_chunked_downloader()`
3. 更新所有下載函數

**實作細節**：
```python
# 更新匯入
from .http_client import get_http_client, get_chunked_downloader

# 移除舊的工廠函數

def download_file(url: str, file_path: str) -> bool:
    """Download large files using chunked downloader."""
    downloader = get_chunked_downloader()
    return downloader.download_large_file(url, file_path)

def download_file_gr(url: str, file_path: str, progress_gr=None) -> bool:
    """Download files with Gradio progress integration."""
    downloader = get_chunked_downloader()
    return downloader.download_large_file(url, file_path, progress_callback=progress_gr)
```

#### 2.3 更新 `ishortcut.py`

**目標檔案**：`scripts/civitai_manager_libs/ishortcut.py`

**變更內容**：
1. 移除 `_shortcut_client` 和 `get_shortcut_client()`
2. 使用統一的 `get_http_client()`

#### 2.4 更新 `util.py`

**目標檔案**：`scripts/civitai_manager_libs/util.py`

**變更內容**：
1. 移除直接實例化 `CivitaiHttpClient` 的程式碼
2. 使用統一的 `get_http_client()`

#### 2.5 更新其他模組

**目標檔案**：
- `scripts/civitai_manager_libs/scan_action.py`
- `scripts/civitai_manager_libs/civitai_gallery_action.py`

**變更內容**：統一使用 `get_http_client()`

### 階段三：移除監控模組

#### 3.1 刪除監控檔案

**要刪除的檔案**：
- `scripts/civitai_manager_libs/monitoring.py`
- `tests/monitoring/test_monitoring.py`
- `tests/performance/test_http_performance.py`

#### 3.2 更新設定檔

**目標檔案**：`scripts/civitai_manager_libs/setting.py`

**變更內容**：
1. 移除監控相關設定：
   - `http_memory_monitor_enabled`
   - `http_max_memory_usage_mb`
   - `http_memory_check_interval`
   - 其他監控相關設定

2. 保留必要設定：
   - `http_pool_connections`
   - `http_pool_maxsize`
   - `http_pool_block`
   - `http_chunk_size`
   - `http_max_parallel_chunks`

### 階段四：更新測試

#### 4.1 更新單元測試

**目標檔案**：
- `tests/test_http_client.py`
- `tests/test_civitai.py`
- `tests/test_downloader.py`
- `tests/test_ishortcut_http.py`

**變更內容**：
1. 更新測試以使用新的 `CivitaiHttpClient`
2. 移除 `OptimizedHTTPClient` 相關測試
3. 更新工廠函數測試
4. 新增 `ChunkedDownloader` 測試

#### 4.2 更新整合測試

**目標檔案**：`tests/integration/`

**變更內容**：
1. 更新所有整合測試以使用新架構
2. 移除監控相關測試

## 實作順序

### 第一步：準備工作
1. 備份當前程式碼
2. 建立遷移測試分支
3. 確認所有現有測試通過

### 第二步：核心重構
1. 重構 `http_client.py`
2. 建立統一工廠函數
3. 運行核心測試確認基本功能

### 第三步：模組更新
1. 更新 `civitai.py`
2. 更新 `downloader.py`
3. 更新 `ishortcut.py`
4. 更新 `util.py`
5. 更新其他模組

### 第四步：清理工作
1. 刪除監控模組
2. 更新設定檔
3. 清理測試檔案

### 第五步：測試驗證
1. 運行所有單元測試
2. 運行整合測試
3. 程式碼品質檢查
4. 功能回歸測試

## 風險評估

### 主要風險

1. **功能回歸**：移除舊程式碼可能影響現有功能
2. **測試覆蓋**：大量程式碼變更可能導致測試遺漏
3. **效能影響**：統一客戶端可能影響特定場景的效能

### 風險緩解

1. **漸進式遷移**：分階段進行，每階段都進行測試
2. **完整測試**：確保測試覆蓋所有變更的程式碼路徑
3. **效能測試**：在遷移完成後進行效能基準測試

## 後續維護

### 文件更新

1. 更新 `docs/architecture_overview.md`
2. 更新相關 README 檔案
3. 更新 API 文件

### 程式碼品質

1. 確保所有程式碼通過 `black` 和 `flake8` 檢查
2. 運行完整測試套件
3. 檢查測試覆蓋率

## 預期效果

### 正面影響

1. **簡化架構**：減少不必要的抽象層
2. **降低複雜度**：統一 HTTP 客戶端使用方式
3. **提升性能**：使用優化版客戶端作為唯一實作
4. **減少維護成本**：移除冗餘程式碼和監控系統

### 功能保留

1. **連線池功能**：保留 `OptimizedHTTPClient` 的連線池特性
2. **智慧重試**：保留重試邏輯和錯誤處理
3. **分段下載**：保留 `ChunkedDownloader` 的高效下載功能
4. **進度回調**：保留下載進度報告功能

## 結論

本遷移計畫將徹底簡化 centralized HTTP client 的架構，移除不必要的設計複雜度，統一使用優化版的 HTTP 客戶端。通過系統性的重構，我們將獲得更簡潔、更高效的 HTTP 客戶端系統，同時保留所有必要的功能特性。

此計畫符合 DRY 和 KISS 原則，將為專案的長期維護和發展打下堅實基礎。
