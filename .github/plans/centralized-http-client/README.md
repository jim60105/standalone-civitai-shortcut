# 中央化 Civitai HTTP 客戶端實作計劃

## 專案概述

目前專案中的 HTTP 請求分散在多個模組中，缺乏統一的錯誤處理、超時機制和重試邏輯。本計劃旨在建立一個中央化的 HTTP 客戶端，提供一致的 API 並妥善處理各種網路錯誤狀況。

## 背景分析

### 現狀問題

通過程式碼分析發現以下問題：

1. **分散的 HTTP 請求處理**：在以下檔案中找到 16 個 `requests.get` 使用位置：
   - `civitai.py` - 4 個位置（API 請求）
   - `civitai_gallery_action.py` - 3 個位置（圖片下載）
   - `downloader.py` - 5 個位置（檔案和圖片下載）
   - `ishortcut.py` - 3 個位置（圖片下載）
   - `scan_action.py` - 1 個位置（圖片下載）

2. **不一致的錯誤處理**：各模組都有自己的錯誤處理邏輯，某些模組只檢查狀態碼，其他則有簡單的例外處理

3. **缺乏超時控制**：所有 HTTP 請求都沒有設定超時參數

4. **錯誤回報不完整**：當發生像 524（Cloudflare 錯誤）等 HTTP 錯誤時，沒有適當的使用者友善錯誤提示

5. **重試機制不一致**：只有 `downloader.py` 中的某些函數有重試邏輯

### 目標錯誤案例

```
[Civitai Shortcut] [civitai] Request failed with status code: 524
Traceback (most recent call last):
  ...
  File "/workspaces/civitai-shortcut/scripts/civitai_manager_libs/civitai_gallery_action.py", line 724, in get_paging_information_working
    item_list.extend(json_data['items'])
                     ~~~~~~~~~^^^^^^^^^
TypeError: 'NoneType' object is not subscriptable
```

這個錯誤顯示：
- HTTP 524 錯誤沒有被妥善處理
- 回傳的 `json_data` 為 `None`，導致後續存取失敗
- 缺乏使用者友善的錯誤提示

## 解決方案架構

### 核心設計原則

1. **中央化管理**：建立單一的 HTTP 客戶端類別處理所有 Civitai API 請求
2. **統一錯誤處理**：所有 HTTP 錯誤都透過中央處理器處理，提供一致的錯誤回報
3. **優雅降級**：當請求失敗時，提供合理的預設值而非拋出例外
4. **使用者友善**：使用 `gradio.Error` 提供清楚的錯誤訊息給使用者
5. **可設定性**：允許設定超時時間、重試次數等參數

### 實作範圍

1. **建立中央化 HTTP 客戶端**：`CivitaiHttpClient` 類別
2. **更新所有現有模組**：逐步替換分散的 `requests.get` 呼叫
3. **增強錯誤處理**：處理所有常見的 HTTP 錯誤狀況
4. **加入設定選項**：允許使用者自訂超時和重試設定
5. **完整測試覆蓋**：確保所有錯誤情況都有相應的測試

## 實作階段

本計劃分為 8 個循序漸進的工作項目，每個項目都有明確的交付目標和驗收標準。

## 相關檔案清單

- **需要建立的新檔案**：
  - `scripts/civitai_manager_libs/http_client.py`
  - `tests/test_http_client.py`

- **需要修改的現有檔案**：
  - `scripts/civitai_manager_libs/civitai.py`
  - `scripts/civitai_manager_libs/civitai_gallery_action.py`
  - `scripts/civitai_manager_libs/downloader.py`
  - `scripts/civitai_manager_libs/ishortcut.py`
  - `scripts/civitai_manager_libs/scan_action.py`
  - `scripts/civitai_manager_libs/setting.py`

## 技術要求

- Python 3.7+
- requests 庫
- gradio 庫（用於錯誤訊息顯示）
- pytest（用於測試）
- 相容於 AUTOMATIC1111 WebUI 和 standalone 模式

## 品質保證

- 所有程式碼遵循 PEP 8 標準
- 使用 `black --line-length=100 --skip-string-normalization` 格式化
- 使用 `flake8` 進行程式碼檢查
- 達成 90% 以上的測試涵蓋率
- 所有註解和文件使用英文撰寫
