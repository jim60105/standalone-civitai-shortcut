# Backlog Item 002: 重構 civitai.py 模組使用中央化 HTTP 客戶端

## 工作描述

將 `civitai.py` 模組中的所有直接 `requests.get` 呼叫替換為使用新建立的 `CivitaiHttpClient`，確保 API 請求的一致性和錯誤處理。

## 背景分析

通過程式碼分析，`civitai.py` 模組中有 4 個 `requests.get` 使用位置：

1. **`request_models()` 函數**（第 41 行）：用於獲取模型列表和分頁資料
2. **`get_model_info()` 函數**（第 63 行）：根據模型 ID 獲取模型資訊
3. **`get_version_info_by_hash()` 函數**（第 98 行）：根據雜湊值獲取版本資訊  
4. **`get_version_info_by_version_id()` 函數**（第 126 行）：根據版本 ID 獲取版本資訊

## 具體需求

### 1. 整合 HTTP 客戶端

- **匯入新的 HTTP 客戶端**：
  ```python
  from .http_client import CivitaiHttpClient
  ```

- **建立模組級別的客戶端實例**：
  ```python
  # Module-level HTTP client instance
  _http_client = None

  def get_http_client():
      """Get or create HTTP client instance."""
      global _http_client
      if _http_client is None:
          _http_client = CivitaiHttpClient(
              api_key=setting.civitai_api_key,
              timeout=setting.http_timeout,
              max_retries=setting.http_max_retries
          )
      return _http_client
  ```

### 2. 重構現有函數

#### 2.1 `request_models()` 函數

**現狀問題**：
- 直接使用 `requests.get(api_url)`
- 簡單的狀態碼檢查，但錯誤處理不完整
- 當失敗時回傳 `None`，但沒有使用者友善的錯誤提示

**重構目標**：
```python
def request_models(api_url=None):
    """Request models from Civitai API with robust error handling."""
    util.printD(f"[civitai] request_models() called with api_url: {api_url}")
    
    if not api_url:
        util.printD("[civitai] request_models: api_url is None or empty")
        return None
    
    client = get_http_client()
    data = client.get_json(api_url)
    
    if data is None:
        util.printD(f"[civitai] request_models: Failed to get data from {api_url}")
        return None
    
    util.printD(f"[civitai] Response data loaded successfully from {api_url}")
    return data
```

#### 2.2 `get_model_info()` 函數

**現狀問題**：
- 直接使用 `requests.get(url)`
- 只檢查回應中是否包含 'id' 欄位
- 例外處理過於簡單

**重構目標**：
```python
def get_model_info(id: str) -> dict:
    """Get model information by model ID."""
    util.printD(f"[civitai] get_model_info() called with id: {id}")
    
    if not id:
        util.printD("[civitai] get_model_info: id is None or empty")
        return None
    
    url = Url_ModelId() + str(id)
    util.printD(f"[civitai] Requesting model info from URL: {url}")
    
    client = get_http_client()
    content = client.get_json(url)
    
    if content is None:
        util.printD(f"[civitai] get_model_info: Failed to get data for id {id}")
        return None
    
    if 'id' not in content:
        util.printD(f"[civitai] get_model_info: 'id' not in response content for id {id}")
        return None
    
    util.printD(f"[civitai] get_model_info: Successfully retrieved model info for id {id}")
    return content
```

#### 2.3 `get_version_info_by_hash()` 函數

**重構目標**：
```python
def get_version_info_by_hash(hash_value) -> dict:
    """Get version information by hash value."""
    util.printD(f"[civitai] get_version_info_by_hash() called with hash: {hash_value}")
    
    if not hash_value:
        util.printD("[civitai] get_version_info_by_hash: hash is None or empty")
        return None
    
    url = f"{Url_Hash()}{hash_value}"
    util.printD(f"[civitai] Requesting version info by hash from URL: {url}")
    
    client = get_http_client()
    content = client.get_json(url)
    
    if content is None:
        util.printD(f"[civitai] get_version_info_by_hash: Failed to get data for hash {hash_value}")
        return None
    
    if 'id' not in content:
        util.printD(f"[civitai] get_version_info_by_hash: 'id' not in response content for hash {hash_value}")
        return None
    
    util.printD(f"[civitai] get_version_info_by_hash: Successfully retrieved version info for hash {hash_value}")
    return content
```

#### 2.4 `get_version_info_by_version_id()` 函數

**重構目標**：
```python
def get_version_info_by_version_id(version_id: str) -> dict:
    """Get version information by version ID."""
    util.printD(f"[civitai] get_version_info_by_version_id() called with version_id: {version_id}")
    
    if not version_id:
        util.printD("[civitai] get_version_info_by_version_id: version_id is None or empty")
        return None
    
    url = Url_VersionId() + str(version_id)
    util.printD(f"[civitai] Requesting version info from URL: {url}")
    
    client = get_http_client()
    content = client.get_json(url)
    
    if content is None:
        util.printD(f"[civitai] get_version_info_by_version_id: Failed to get data for version_id {version_id}")
        return None
    
    if 'id' not in content:
        util.printD(f"[civitai] get_version_info_by_version_id: 'id' not in response content for version_id {version_id}")
        return None
    
    util.printD(f"[civitai] get_version_info_by_version_id: Successfully retrieved version info for version_id {version_id}")
    return content
```

### 3. 處理特殊情況

#### 3.1 修復 `get_paging_information_working` 錯誤

**目標錯誤案例**：
```python
# 在 civitai_gallery_action.py 第 724 行
item_list.extend(json_data['items'])  # json_data 為 None 時會出錯
```

**解決方案**：確保 `request_models()` 永遠不回傳 `None`，而是回傳空的字典：
```python
def request_models(api_url=None):
    # ... existing code ...
    
    data = client.get_json(api_url)
    
    if data is None:
        util.printD(f"[civitai] request_models: Failed to get data from {api_url}")
        # Return empty structure instead of None to prevent TypeError
        return {'items': [], 'metadata': {}}
    
    return data
```

#### 3.2 API 金鑰處理

**支援動態 API 金鑰更新**：
```python
def get_http_client():
    """Get or create HTTP client instance."""
    global _http_client
    if _http_client is None:
        _http_client = CivitaiHttpClient(
            api_key=setting.civitai_api_key,
            timeout=setting.http_timeout,
            max_retries=setting.http_max_retries
        )
    else:
        # Update API key if it has changed
        if _http_client.api_key != setting.civitai_api_key:
            _http_client.update_api_key(setting.civitai_api_key)
    
    return _http_client
```

## 測試要求

### 1. 單元測試

在 `tests/test_civitai.py` 中新增或更新測試：

- **模型資訊獲取測試**：
  - 正常情況下的模型資訊獲取
  - 無效模型 ID 的處理
  - 網路錯誤時的處理

- **版本資訊獲取測試**：
  - 通過版本 ID 獲取版本資訊
  - 通過雜湊值獲取版本資訊
  - 無效參數的處理

- **分頁資料請求測試**：
  - 正常的分頁資料請求
  - API 錯誤時的處理
  - 空回應的處理

### 2. 整合測試

- **與 HTTP 客戶端整合**：
  - 確保 HTTP 客戶端正確初始化
  - 確保 API 金鑰正確傳遞
  - 確保超時設定正確應用

- **錯誤處理整合**：
  - 模擬各種 HTTP 錯誤狀況
  - 確保錯誤訊息正確顯示
  - 確保不會拋出未處理的例外

### 3. 回歸測試

- **功能不變性**：
  - 確保所有公開函數的回傳值格式不變
  - 確保現有的呼叫程式碼不需要修改
  - 確保錯誤情況下的行為一致

## 實作細節

### 1. 程式碼結構

```python
# At the top of civitai.py
from .http_client import CivitaiHttpClient

# Module-level client instance
_http_client = None

def get_http_client():
    """Get or create HTTP client instance."""
    # Implementation as described above

# Updated functions using the HTTP client
def request_models(api_url=None):
    # New implementation

def get_model_info(id: str) -> dict:
    # New implementation

# ... other functions
```

### 2. 保持向後相容性

- **函數簽名不變**：所有現有函數的參數和回傳值保持不變
- **行為一致性**：錯誤情況下的回傳值保持一致
- **除錯輸出格式**：保持現有的 `util.printD()` 輸出格式

### 3. 效能考慮

- **客戶端重用**：使用模組級別的客戶端實例避免重複建立
- **連接池**：HTTP 客戶端內部應該使用連接池
- **記憶體效率**：避免不必要的資料複製

## 驗收標準

### 1. 功能完整性

- [ ] 所有現有的 `civitai.py` 函數功能正常
- [ ] HTTP 錯誤有適當的處理和使用者提示
- [ ] 所有直接的 `requests.get` 呼叫都已移除
- [ ] API 金鑰認證正常運作

### 2. 錯誤處理

- [ ] 網路錯誤時不會拋出未處理的例外
- [ ] HTTP 4xx/5xx 錯誤有使用者友善的訊息
- [ ] 超時錯誤有適當的處理
- [ ] `get_paging_information_working` 錯誤已修復

### 3. 測試覆蓋

- [ ] 所有重構的函數都有對應的測試
- [ ] 錯誤情況都有測試覆蓋
- [ ] 整合測試通過
- [ ] 回歸測試通過

### 4. 程式碼品質

- [ ] 通過 `black --line-length=100 --skip-string-normalization` 格式檢查
- [ ] 通過 `flake8` 程式碼品質檢查
- [ ] 所有註解和文件使用英文
- [ ] 遵循現有的程式碼風格

### 5. 向後相容性

- [ ] 所有現有的呼叫方式仍然正常運作
- [ ] 函數回傳值格式保持不變
- [ ] 錯誤處理行為保持一致

## 風險與注意事項

### 1. 中斷風險

- **API 行為變更**：需要確保 HTTP 客戶端的行為與原來的 `requests.get` 一致
- **錯誤處理變更**：新的錯誤處理可能會改變原有的錯誤流程

### 2. 效能影響

- **額外抽象層**：新的 HTTP 客戶端可能會增加一些效能開銷
- **記憶體使用**：需要注意客戶端實例的記憶體使用

### 3. 測試挑戰

- **網路依賴**：需要mock HTTP 請求進行測試
- **狀態管理**：模組級別的客戶端實例需要適當的測試清理

## 相關檔案

- **修改**：`scripts/civitai_manager_libs/civitai.py`
- **新建立或更新**：`tests/test_civitai.py`
- **依賴**：`scripts/civitai_manager_libs/http_client.py`（來自 001 工作項目）

## 後續工作

完成此項目後，接下來將重構其他模組中的 HTTP 請求，包括 `civitai_gallery_action.py`、`downloader.py` 等。
