# Backlog Item 001: 建立核心 HTTP 客戶端類別

## 工作描述

建立一個中央化的 `CivitaiHttpClient` 類別，提供統一的 HTTP 請求介面，包含完整的錯誤處理、超時控制和重試機制。

## 具體需求

### 1. 核心功能要求

- **建立 `CivitaiHttpClient` 類別**：
  - 支援 GET 和 POST 請求
  - 內建超時控制（預設 20 秒）
  - 自動重試機制（預設 3 次）
  - 支援 Bearer token 驗證
  - 支援串流下載

- **錯誤處理機制**：
  - 處理所有 HTTP 狀態碼錯誤（4xx, 5xx）
  - 處理網路連線錯誤
  - 處理超時錯誤
  - 處理 JSON 解析錯誤
  - 使用 `gradio.Error` 顯示使用者友善的錯誤訊息

- **回傳值設計**：
  - 成功時回傳預期的資料結構
  - 失敗時回傳 `None` 或空的資料結構
  - 不拋出例外，而是記錄錯誤並優雅降級

### 2. 設定整合

- **從 `setting.py` 讀取設定**：
  - API 金鑰 (`civitai_api_key`)
  - 請求超時時間 (`http_timeout`)
  - 重試次數 (`http_max_retries`)
  - 重試延遲時間 (`http_retry_delay`)

- **新增設定項目**：
  ```python
  # HTTP client settings
  http_timeout = 20  # seconds
  http_max_retries = 3
  http_retry_delay = 1  # seconds between retries
  ```

### 3. API 介面設計

```python
class CivitaiHttpClient:
    def __init__(self, api_key: str = None, timeout: int = 20, max_retries: int = 3):
        """Initialize HTTP client with configuration."""
        pass
    
    def get_json(self, url: str, params: dict = None) -> Optional[Dict]:
        """Make GET request and return JSON response."""
        pass
    
    def get_stream(self, url: str, headers: dict = None) -> Optional[requests.Response]:
        """Make GET request for streaming download."""
        pass
    
    def download_file(self, url: str, filepath: str, 
                      progress_callback: Callable = None) -> bool:
        """Download file with progress tracking."""
        pass
```

### 4. 錯誤分類處理

- **4xx 錯誤**：
  - 400 Bad Request: "請求格式不正確"
  - 401 Unauthorized: "API 金鑰無效或已過期"
  - 403 Forbidden: "無權限存取此資源"
  - 404 Not Found: "資源不存在"
  - 429 Too Many Requests: "請求過於頻繁，請稍後再試"

- **5xx 錯誤**：
  - 500 Internal Server Error: "伺服器內部錯誤"
  - 502 Bad Gateway: "閘道錯誤"
  - 503 Service Unavailable: "服務暫時無法使用"
  - 504 Gateway Timeout: "閘道超時"
  - 524 (Cloudflare): "連線超時"

- **網路錯誤**：
  - ConnectionError: "網路連線失敗"
  - Timeout: "請求超時"
  - RequestException: "網路請求異常"

## 實作細節

### 1. 檔案結構

```
scripts/civitai_manager_libs/
├── http_client.py          # 新建立的 HTTP 客戶端
└── setting.py              # 新增 HTTP 相關設定
```

### 2. 核心實作要點

- **使用 `util.printD()` 記錄詳細的除錯資訊**：
  ```python
  util.printD(f"[http_client] Making request to: {url}")
  util.printD(f"[http_client] Response status: {response.status_code}")
  ```

- **錯誤訊息格式化**：
  ```python
  error_msg = f"Request failed: {error_description} (Status: {status_code})"
  util.printD(f"[http_client] {error_msg}")
  gr.Error(f"網路請求失敗 💥! {error_description}", duration=5)
  ```

- **重試邏輯**：
  ```python
  for attempt in range(max_retries):
      try:
          # Make request
          break
      except (ConnectionError, Timeout) as e:
          if attempt == max_retries - 1:
              # Last attempt failed
              return None
          time.sleep(retry_delay)
  ```

### 3. 與現有系統整合

- **保持向後相容**：原有的 `civitai.py` 中的函數介面保持不變
- **逐步遷移**：先建立 HTTP 客戶端，後續工作項目再逐步替換使用
- **設定預設值**：確保沒有設定時使用合理的預設值

## 測試要求

### 1. 單元測試

建立 `tests/test_http_client.py`，包含：

- **基本功能測試**：
  - 正常 GET 請求
  - 正常 POST 請求
  - 串流下載
  - 檔案下載

- **錯誤處理測試**：
  - 各種 HTTP 狀態碼錯誤
  - 網路連線錯誤
  - 超時錯誤
  - JSON 解析錯誤

- **設定測試**：
  - 自訂超時時間
  - 自訂重試次數
  - API 金鑰驗證

### 2. 模擬測試

使用 `unittest.mock` 模擬：
- `requests.get` 和 `requests.post` 回應
- 網路錯誤情況
- 超時情況
- 不同的 HTTP 狀態碼

### 3. 整合測試

- 確保與現有的 `setting.py` 正確整合
- 確保 `util.printD()` 正確記錄除錯資訊
- 確保 `gradio.Error` 正確顯示錯誤訊息

## 驗收標準

### 1. 功能完整性

- [ ] `CivitaiHttpClient` 類別能處理所有基本 HTTP 請求
- [ ] 所有 HTTP 錯誤都有適當的處理和使用者友善的訊息
- [ ] 超時機制正常運作（20 秒預設）
- [ ] 重試機制正常運作（3 次預設）
- [ ] 檔案下載功能正常運作
- [ ] 支援 Bearer token 驗證

### 2. 錯誤處理

- [ ] 所有 4xx 和 5xx 錯誤都有對應的中文錯誤訊息
- [ ] 網路連線錯誤有適當的處理
- [ ] 超時錯誤有適當的處理
- [ ] 錯誤時不拋出例外，而是優雅降級

### 3. 設定整合

- [ ] 能從 `setting.py` 正確讀取設定
- [ ] 設定項目有合理的預設值
- [ ] 支援執行時期動態調整設定

### 4. 測試覆蓋

- [ ] 單元測試涵蓋率達到 90% 以上
- [ ] 所有錯誤情況都有對應的測試
- [ ] 所有公開方法都有測試

### 5. 程式碼品質

- [ ] 通過 `black --line-length=100 --skip-string-normalization` 格式檢查
- [ ] 通過 `flake8` 程式碼品質檢查
- [ ] 所有註解和文件使用英文
- [ ] 遵循 PEP 8 命名規範

## 注意事項

1. **不要破壞現有功能**：此階段只是建立基礎設施，不要修改現有的呼叫方式
2. **確保相容性**：需要同時支援 WebUI 和 standalone 模式
3. **效能考慮**：HTTP 客戶端需要是輕量級的，不要影響現有效能
4. **除錯支援**：確保有足夠的除錯資訊幫助問題排查

## 相關檔案

- **新建立**：`scripts/civitai_manager_libs/http_client.py`
- **新建立**：`tests/test_http_client.py`
- **修改**：`scripts/civitai_manager_libs/setting.py`（新增 HTTP 設定）

## 後續工作

完成此項目後，接下來的工作項目將逐步將現有的 HTTP 請求遷移到這個中央化的客戶端。
