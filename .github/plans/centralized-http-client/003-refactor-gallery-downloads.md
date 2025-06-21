# Backlog Item 003: 重構 civitai_gallery_action.py 圖片下載邏輯

## 工作描述

將 `civitai_gallery_action.py` 模組中的圖片下載相關 HTTP 請求重構為使用中央化的 `CivitaiHttpClient`，解決圖片下載失敗和錯誤處理不當的問題。

## 背景分析

通過程式碼分析，`civitai_gallery_action.py` 模組中有 3 個 `requests.get` 使用位置：

1. **`download_images()` 函數**（第 594 行）：下載圖庫預覽圖片
2. **第 788 行**：在某個圖片處理流程中的下載
3. **第 847 行**：在另一個圖片處理流程中的下載

## 具體需求

### 1. 整合 HTTP 客戶端

- **匯入並使用 HTTP 客戶端**：
  ```python
  from .http_client import CivitaiHttpClient
  
  # Module-level HTTP client instance
  _http_client = None
  
  def get_http_client():
      """Get or create HTTP client instance for gallery operations."""
      global _http_client
      if _http_client is None:
          _http_client = CivitaiHttpClient(
              timeout=setting.http_timeout,
              max_retries=setting.http_max_retries
          )
      return _http_client
  ```

### 2. 重構圖片下載函數

#### 2.1 `download_images()` 函數重構

**現狀問題**：
- 直接使用 `requests.get(img_url, stream=True)`
- 只檢查 `img_r.ok`，錯誤處理不完整
- 下載失敗時直接 `continue`，沒有錯誤記錄或使用者提示

**重構目標**：
```python
def download_images(dn_image_list: list):
    """Download images for gallery with improved error handling."""
    if not dn_image_list:
        return
    
    client = get_http_client()
    util.printD(f"[civitai_gallery_action] Starting download of {len(dn_image_list)} images")
    
    success_count = 0
    failed_count = 0
    
    for img_url in dn_image_list:
        gallery_img_file = setting.get_image_url_to_gallery_file(img_url)
        
        if os.path.isfile(gallery_img_file):
            util.printD(f"[civitai_gallery_action] Image already exists: {gallery_img_file}")
            continue
        
        util.printD(f"[civitai_gallery_action] Downloading image: {img_url}")
        
        # Use centralized HTTP client for download
        if client.download_file(img_url, gallery_img_file):
            success_count += 1
            util.printD(f"[civitai_gallery_action] Successfully downloaded: {gallery_img_file}")
        else:
            failed_count += 1
            util.printD(f"[civitai_gallery_action] Failed to download: {img_url}")
    
    util.printD(f"[civitai_gallery_action] Download complete: {success_count} success, {failed_count} failed")
    
    if failed_count > 0:
        # Show user-friendly error message without breaking the UI
        import gradio as gr
        gr.Error(f"部分圖片下載失敗 ({failed_count} 個)，請檢查網路連線 💥!", duration=3)
```

#### 2.2 其他圖片下載位置重構

**識別並重構所有圖片下載邏輯**：

```python
def _download_single_image(img_url: str, save_path: str) -> bool:
    """Download a single image with proper error handling."""
    client = get_http_client()
    
    util.printD(f"[civitai_gallery_action] Downloading image from: {img_url}")
    util.printD(f"[civitai_gallery_action] Saving to: {save_path}")
    
    success = client.download_file(img_url, save_path)
    
    if success:
        util.printD(f"[civitai_gallery_action] Successfully downloaded image: {save_path}")
    else:
        util.printD(f"[civitai_gallery_action] Failed to download image: {img_url}")
    
    return success
```

### 3. 處理特殊的串流下載情況

#### 3.1 支援自訂寫入邏輯

某些下載可能需要特殊的處理（如使用 `shutil.copyfileobj`），HTTP 客戶端需要支援：

```python
# In http_client.py
def get_stream_response(self, url: str, headers: dict = None) -> Optional[requests.Response]:
    """Get streaming response for custom processing."""
    try:
        response = self._make_request('GET', url, headers=headers, stream=True)
        if response and response.ok:
            return response
        return None
    except Exception as e:
        self._handle_error(e, url)
        return None
```

#### 3.2 使用串流回應

```python
def download_images(dn_image_list: list):
    """Download images with streaming support."""
    client = get_http_client()
    
    for img_url in dn_image_list:
        gallery_img_file = setting.get_image_url_to_gallery_file(img_url)
        
        if os.path.isfile(gallery_img_file):
            continue
        
        # Get streaming response
        response = client.get_stream_response(img_url)
        if response is None:
            continue
        
        try:
            with open(gallery_img_file, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)
            
            util.printD(f"[civitai_gallery_action] Downloaded: {gallery_img_file}")
        except Exception as e:
            util.printD(f"[civitai_gallery_action] Error writing file {gallery_img_file}: {e}")
            # Clean up partial file
            if os.path.exists(gallery_img_file):
                os.remove(gallery_img_file)
        finally:
            response.close()
```

### 4. 改善使用者體驗

#### 4.1 進度追蹤

```python
def download_images_with_progress(dn_image_list: list, progress_callback=None):
    """Download images with progress tracking."""
    if not dn_image_list:
        return
    
    total_images = len(dn_image_list)
    completed = 0
    
    for i, img_url in enumerate(dn_image_list):
        gallery_img_file = setting.get_image_url_to_gallery_file(img_url)
        
        if not os.path.isfile(gallery_img_file):
            client = get_http_client()
            client.download_file(img_url, gallery_img_file)
        
        completed += 1
        
        if progress_callback:
            progress_callback(completed, total_images, f"下載圖片 {completed}/{total_images}")
```

#### 4.2 批次下載限制

```python
def download_images_batch(dn_image_list: list, batch_size: int = 5):
    """Download images in batches to avoid overwhelming the server."""
    if not dn_image_list:
        return
    
    client = get_http_client()
    
    for i in range(0, len(dn_image_list), batch_size):
        batch = dn_image_list[i:i + batch_size]
        
        util.printD(f"[civitai_gallery_action] Processing batch {i//batch_size + 1}, {len(batch)} images")
        
        for img_url in batch:
            gallery_img_file = setting.get_image_url_to_gallery_file(img_url)
            
            if not os.path.isfile(gallery_img_file):
                client.download_file(img_url, gallery_img_file)
        
        # Small delay between batches to be respectful to the server
        time.sleep(0.5)
```

### 5. 錯誤恢復機制

#### 5.1 失敗重試列表

```python
class GalleryDownloadManager:
    """Manage gallery image downloads with retry capability."""
    
    def __init__(self):
        self.failed_downloads = []
        self.client = get_http_client()
    
    def download_with_retry(self, img_url: str, save_path: str, max_retries: int = 2) -> bool:
        """Download image with retry on failure."""
        for attempt in range(max_retries + 1):
            if self.client.download_file(img_url, save_path):
                return True
            
            if attempt < max_retries:
                util.printD(f"[civitai_gallery_action] Retry {attempt + 1} for: {img_url}")
                time.sleep(1)
        
        # Record failed download for later retry
        self.failed_downloads.append((img_url, save_path))
        return False
    
    def retry_failed_downloads(self):
        """Retry all previously failed downloads."""
        if not self.failed_downloads:
            return
        
        util.printD(f"[civitai_gallery_action] Retrying {len(self.failed_downloads)} failed downloads")
        
        retry_list = self.failed_downloads.copy()
        self.failed_downloads.clear()
        
        for img_url, save_path in retry_list:
            self.download_with_retry(img_url, save_path, max_retries=1)
```

## 測試要求

### 1. 單元測試

在 `tests/test_civitai_gallery_action.py` 中新增：

- **圖片下載測試**：
  - 正常下載情況
  - 網路錯誤情況
  - 檔案寫入錯誤情況
  - 重複下載處理

- **批次下載測試**：
  - 小批次下載
  - 大批次下載
  - 部分失敗情況

- **串流下載測試**：
  - 正常串流下載
  - 串流中斷處理
  - 檔案部分下載清理

### 2. 整合測試

- **與 HTTP 客戶端整合**：
  - 確保正確使用 HTTP 客戶端
  - 確保錯誤處理正確傳遞
  - 確保進度回報正常

- **與設定系統整合**：
  - 確保使用正確的下載路徑
  - 確保遵守下載限制設定

### 3. 效能測試

- **大量圖片下載**：
  - 測試下載 100+ 圖片的情況
  - 記憶體使用情況
  - 下載速度對比

## 實作細節

### 1. 保持現有 API 介面

```python
# Keep existing function signatures unchanged
def download_images(dn_image_list: list):
    """Original function signature maintained for compatibility."""
    pass

def pre_loading(usergal_page_url, paging_information):
    """Keep existing pre-loading logic."""
    pass
```

### 2. 設定整合

```python
# Add gallery-specific settings to setting.py
gallery_download_batch_size = 5
gallery_download_timeout = 30
gallery_max_concurrent_downloads = 3
```

### 3. 記憶體最佳化

```python
def download_large_image(img_url: str, save_path: str, chunk_size: int = 8192) -> bool:
    """Download large images with memory-efficient streaming."""
    client = get_http_client()
    response = client.get_stream_response(img_url)
    
    if response is None:
        return False
    
    try:
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        util.printD(f"[civitai_gallery_action] Error downloading large image: {e}")
        if os.path.exists(save_path):
            os.remove(save_path)
        return False
    finally:
        response.close()
```

## 驗收標準

### 1. 功能完整性

- [ ] 所有圖片下載功能正常運作
- [ ] 批次下載機制正常
- [ ] 失敗重試機制正常
- [ ] 進度追蹤功能正常

### 2. 錯誤處理

- [ ] 網路錯誤時有適當的使用者提示
- [ ] 部分下載失敗時不影響整體功能
- [ ] 檔案寫入錯誤有適當處理
- [ ] 重複下載有適當處理

### 3. 效能最佳化

- [ ] 大量圖片下載不會造成記憶體問題
- [ ] 下載速度符合預期
- [ ] 併發下載控制正常

### 4. 使用者體驗

- [ ] 下載進度有適當的回饋
- [ ] 錯誤訊息清楚且有用
- [ ] 不會阻塞使用者介面

### 5. 程式碼品質

- [ ] 通過 `black --line-length=100 --skip-string-normalization` 格式檢查
- [ ] 通過 `flake8` 程式碼品質檢查
- [ ] 所有註解和文件使用英文
- [ ] 遵循現有的程式碼風格

## 風險與注意事項

### 1. 下載效能

- **網路頻寬**：大量圖片下載可能會佔用過多頻寬
- **伺服器負載**：需要控制併發請求避免對 Civitai 伺服器造成壓力

### 2. 儲存空間

- **磁碟空間**：需要檢查可用空間避免填滿磁碟
- **檔案清理**：失敗的部分下載需要適當清理

### 3. 錯誤處理

- **網路不穩定**：需要適當的重試機制
- **權限問題**：檔案寫入權限可能會導致問題

## 相關檔案

- **修改**：`scripts/civitai_manager_libs/civitai_gallery_action.py`
- **新建立或更新**：`tests/test_civitai_gallery_action.py`
- **修改**：`scripts/civitai_manager_libs/setting.py`（新增圖庫下載設定）
- **依賴**：`scripts/civitai_manager_libs/http_client.py`（來自 001 工作項目）

## 後續工作

完成此項目後，接下來將重構 `downloader.py` 模組中的檔案下載邏輯。
