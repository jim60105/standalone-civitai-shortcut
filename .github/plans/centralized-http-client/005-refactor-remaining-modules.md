# Backlog Item 005: 重構 ishortcut.py 和 scan_action.py 剩餘 HTTP 請求

## 工作描述

將 `ishortcut.py` 和 `scan_action.py` 模組中剩餘的 HTTP 請求重構為使用中央化的 `CivitaiHttpClient`，完成所有模組的 HTTP 請求統一化。

## 背景分析

通過程式碼分析，發現以下 HTTP 請求使用位置：

### ishortcut.py 模組
- **第 580 行**：在 `download_model_preview_image_by_model_info()` 函數中下載預覽圖片
- **第 616 行**：在同一函數的另一個分支中下載圖片
- **第 886 行**：在 `get_preview_image_by_model_info()` 函數中下載預覽圖片
- **第 914 行**：在同一函數的另一個分支中下載圖片

### scan_action.py 模組
- **第 195 行**：在掃描動作中下載圖片

這些都是與模型預覽圖片相關的下載功能。

## 具體需求

### 1. 整合 HTTP 客戶端

- **為兩個模組新增 HTTP 客戶端支援**：
  ```python
  # In ishortcut.py
  from .http_client import CivitaiHttpClient
  
  # Module-level HTTP client for shortcuts
  _shortcut_client = None
  
  def get_shortcut_client():
      """Get or create HTTP client for shortcut operations."""
      global _shortcut_client
      if _shortcut_client is None:
          _shortcut_client = CivitaiHttpClient(
              timeout=setting.image_download_timeout or 30,
              max_retries=setting.image_download_max_retries or 3
          )
      return _shortcut_client
  ```

### 2. 重構 ishortcut.py 中的圖片下載

#### 2.1 `download_model_preview_image_by_model_info()` 函數

**現狀分析**：
- 函數負責下載模型的預覽圖片
- 有兩個分支分別處理不同情況的圖片下載
- 直接使用 `requests.get(url, stream=True)`
- 錯誤處理較簡單

**重構目標**：
```python
def download_model_preview_image_by_model_info(model_info):
    """Download model preview image with improved error handling."""
    if not model_info:
        util.printD("[ishortcut] download_model_preview_image_by_model_info: model_info is None")
        return None
    
    model_id = model_info.get('id')
    if not model_id:
        util.printD("[ishortcut] download_model_preview_image_by_model_info: model_id not found")
        return None
    
    util.printD(f"[ishortcut] Downloading preview image for model: {model_id}")
    
    # Get the preview image URL
    preview_url = _get_preview_image_url(model_info)
    if not preview_url:
        util.printD("[ishortcut] No preview image URL found")
        return None
    
    # Generate local file path
    image_path = _get_preview_image_path(model_info)
    if not image_path:
        util.printD("[ishortcut] Failed to generate image path")
        return None
    
    # Skip if already exists
    if os.path.exists(image_path):
        util.printD(f"[ishortcut] Preview image already exists: {image_path}")
        return image_path
    
    # Download using centralized client
    client = get_shortcut_client()
    success = client.download_file(preview_url, image_path)
    
    if success:
        util.printD(f"[ishortcut] Successfully downloaded preview image: {image_path}")
        return image_path
    else:
        util.printD(f"[ishortcut] Failed to download preview image: {preview_url}")
        return None

def _get_preview_image_url(model_info) -> str:
    """Extract preview image URL from model info."""
    try:
        # Try to get from model versions
        if 'modelVersions' in model_info and model_info['modelVersions']:
            for version in model_info['modelVersions']:
                if 'images' in version and version['images']:
                    for image in version['images']:
                        if 'url' in image:
                            return image['url']
        
        # Try to get from direct images
        if 'images' in model_info and model_info['images']:
            for image in model_info['images']:
                if 'url' in image:
                    return image['url']
        
        return None
    except Exception as e:
        util.printD(f"[ishortcut] Error extracting preview URL: {e}")
        return None

def _get_preview_image_path(model_info) -> str:
    """Generate local path for preview image."""
    try:
        model_id = model_info.get('id')
        if not model_id:
            return None
        
        # Create directory if needed
        preview_dir = os.path.join(setting.shortcut_thumb_image_folder)
        os.makedirs(preview_dir, exist_ok=True)
        
        # Generate filename
        filename = f"model_{model_id}_preview.jpg"
        return os.path.join(preview_dir, filename)
    
    except Exception as e:
        util.printD(f"[ishortcut] Error generating image path: {e}")
        return None
```

#### 2.2 `get_preview_image_by_model_info()` 函數

**重構目標**：
```python
def get_preview_image_by_model_info(model_info):
    """Get preview image, download if not exists."""
    if not model_info:
        util.printD("[ishortcut] get_preview_image_by_model_info: model_info is None")
        return setting.no_card_preview_image
    
    # Try to get existing image first
    image_path = _get_preview_image_path(model_info)
    if image_path and os.path.exists(image_path):
        util.printD(f"[ishortcut] Using existing preview image: {image_path}")
        return image_path
    
    # Download if not exists
    downloaded_path = download_model_preview_image_by_model_info(model_info)
    if downloaded_path:
        return downloaded_path
    
    # Return fallback image
    util.printD("[ishortcut] Using fallback preview image")
    return setting.no_card_preview_image
```

#### 2.3 圖片下載的統一處理

**建立通用的圖片下載函數**：
```python
def download_image_with_fallback(url: str, save_path: str, fallback_path: str = None) -> str:
    """Download image with fallback handling."""
    if not url:
        util.printD("[ishortcut] download_image_with_fallback: URL is empty")
        return fallback_path or setting.no_card_preview_image
    
    if os.path.exists(save_path):
        util.printD(f"[ishortcut] Image already exists: {save_path}")
        return save_path
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    client = get_shortcut_client()
    success = client.download_file(url, save_path)
    
    if success:
        util.printD(f"[ishortcut] Successfully downloaded image: {save_path}")
        return save_path
    else:
        util.printD(f"[ishortcut] Failed to download image: {url}")
        return fallback_path or setting.no_card_preview_image
```

### 3. 重構 scan_action.py 中的 HTTP 請求

#### 3.1 分析現有掃描功能

**程式碼位置分析**：
- 掃描動作主要用於檢查本地模型文件的更新
- 需要下載相關的預覽圖片或元資料

**重構目標**：
```python
# In scan_action.py
from .http_client import CivitaiHttpClient

def get_scan_client():
    """Get HTTP client for scan operations."""
    return CivitaiHttpClient(
        timeout=setting.scan_timeout or 30,
        max_retries=setting.scan_max_retries or 2
    )

def download_scan_image(url: str, save_path: str) -> bool:
    """Download image during scan operation."""
    util.printD(f"[scan_action] Downloading scan image: {url}")
    
    client = get_scan_client()
    success = client.download_file(url, save_path)
    
    if success:
        util.printD(f"[scan_action] Scan image downloaded: {save_path}")
    else:
        util.printD(f"[scan_action] Failed to download scan image: {url}")
        # For scan operations, we don't show user errors unless critical
    
    return success
```

### 4. 統一圖片下載介面

#### 4.1 建立共用的圖片下載工具

**在 util.py 中新增工具函數**：
```python
def download_image_safe(url: str, save_path: str, 
                       client: 'CivitaiHttpClient' = None,
                       show_error: bool = True) -> bool:
    """Safely download image with consistent error handling."""
    if not url:
        printD("[util] download_image_safe: URL is empty")
        return False
    
    if os.path.exists(save_path):
        printD(f"[util] Image already exists: {save_path}")
        return True
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Use provided client or create new one
    if client is None:
        from .http_client import CivitaiHttpClient
        client = CivitaiHttpClient()
    
    success = client.download_file(url, save_path)
    
    if success:
        printD(f"[util] Successfully downloaded image: {save_path}")
    else:
        printD(f"[util] Failed to download image: {url}")
        if show_error:
            import gradio as gr
            gr.Error("圖片下載失敗 💥!", duration=3)
    
    return success
```

#### 4.2 整合到現有工作流程

**更新現有的圖片處理函數**：
```python
# In ishortcut.py
def download_model_preview_image_by_model_info(model_info):
    """Simplified version using common utility."""
    if not model_info:
        return None
    
    preview_url = _get_preview_image_url(model_info)
    if not preview_url:
        return None
    
    image_path = _get_preview_image_path(model_info)
    if not image_path:
        return None
    
    client = get_shortcut_client()
    success = util.download_image_safe(preview_url, image_path, client, show_error=False)
    
    return image_path if success else None
```

### 5. 錯誤處理和重試策略

#### 5.1 圖片下載特定錯誤處理

```python
def handle_image_download_error(error: Exception, url: str, context: str = ""):
    """Handle image download errors specifically."""
    error_msg = ""
    
    if isinstance(error, requests.exceptions.Timeout):
        error_msg = "圖片下載超時"
    elif isinstance(error, requests.exceptions.ConnectionError):
        error_msg = "網路連線失敗"
    elif hasattr(error, 'response') and error.response:
        status_code = error.response.status_code
        if status_code == 404:
            error_msg = "圖片不存在"
        elif status_code == 403:
            error_msg = "圖片存取被拒絕"
        else:
            error_msg = f"圖片下載失敗 (HTTP {status_code})"
    else:
        error_msg = "圖片下載發生未知錯誤"
    
    util.printD(f"[image_download] {context}: {error_msg} - {url}")
    
    # Only show error to user for important operations
    if context in ["preview", "model_image"]:
        import gradio as gr
        gr.Error(f"{error_msg} 💥!", duration=3)
```

#### 5.2 重試和快取策略

```python
def download_with_cache_and_retry(url: str, cache_key: str, 
                                 max_age: int = 3600) -> str:
    """Download with caching and retry logic."""
    cache_path = os.path.join(setting.cache_folder, f"{cache_key}.jpg")
    
    # Check if cached version is still valid
    if os.path.exists(cache_path):
        if time.time() - os.path.getmtime(cache_path) < max_age:
            util.printD(f"[cache] Using cached image: {cache_path}")
            return cache_path
    
    # Download new version
    client = get_shortcut_client()
    success = client.download_file(url, cache_path)
    
    if success:
        return cache_path
    else:
        # Return old cached version if download fails
        if os.path.exists(cache_path):
            util.printD("[cache] Using stale cached image due to download failure")
            return cache_path
        else:
            return setting.no_card_preview_image
```

### 6. 設定和最佳化

#### 6.1 新增圖片下載設定

在 `setting.py` 中新增：
```python
# Image download settings
image_download_timeout = 30
image_download_max_retries = 3
image_download_cache_enabled = True
image_download_cache_max_age = 3600  # 1 hour
scan_timeout = 30
scan_max_retries = 2
preview_image_quality = 85  # JPEG quality for preview images
```

#### 6.2 圖片最佳化

```python
def optimize_downloaded_image(image_path: str, max_size: tuple = (800, 600), 
                            quality: int = 85) -> bool:
    """Optimize downloaded image size and quality."""
    try:
        from PIL import Image
        
        with Image.open(image_path) as img:
            # Resize if too large
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save with optimized quality
            img.save(image_path, format='JPEG', quality=quality, optimize=True)
            
        util.printD(f"[image_optimize] Optimized image: {image_path}")
        return True
        
    except Exception as e:
        util.printD(f"[image_optimize] Failed to optimize {image_path}: {e}")
        return False
```

## 測試要求

### 1. 單元測試

**測試檔案：`tests/test_ishortcut_http.py`**
- 預覽圖片下載測試
- 圖片 URL 提取測試
- 本地路徑生成測試
- 錯誤處理測試

**測試檔案：`tests/test_scan_action_http.py`**
- 掃描圖片下載測試
- 掃描錯誤處理測試

### 2. 整合測試

- **與 HTTP 客戶端整合**
- **與檔案系統整合**
- **與快取系統整合**

### 3. 回歸測試

- **確保現有功能不受影響**
- **確保圖片顯示正常**
- **確保掃描功能正常**

## 實作細節

### 1. 保持向後相容性

```python
# Maintain existing function signatures
def download_model_preview_image_by_model_info(model_info):
    """Keep existing signature for compatibility."""
    pass

def get_preview_image_by_model_info(model_info):
    """Keep existing signature for compatibility."""
    pass
```

### 2. 效能最佳化

- **圖片快取機制**
- **批次下載支援**
- **記憶體使用最佳化**
- **磁碟空間管理**

### 3. 錯誤恢復

- **使用快取的舊版本**
- **降級到預設圖片**
- **重試機制**

## 驗收標準

### 1. 功能完整性

- [ ] 所有模型預覽圖片功能正常
- [ ] 掃描功能中的圖片下載正常
- [ ] 快取機制正常運作
- [ ] 圖片最佳化功能正常

### 2. 錯誤處理

- [ ] 網路錯誤有適當處理
- [ ] 圖片不存在時有適當降級
- [ ] 磁碟空間不足有適當處理
- [ ] 權限錯誤有適當處理

### 3. 效能最佳化

- [ ] 圖片下載速度合理
- [ ] 快取機制有效減少重複下載
- [ ] 記憶體使用合理
- [ ] 磁碟空間使用合理

### 4. 使用者體驗

- [ ] 圖片載入速度快
- [ ] 錯誤訊息清楚
- [ ] 不會阻塞使用者介面
- [ ] 圖片品質適中

### 5. 程式碼品質

- [ ] 通過所有程式碼品質檢查
- [ ] 測試涵蓋率達到 80% 以上
- [ ] 文件完整且清楚
- [ ] 遵循現有程式碼風格

## 風險與注意事項

### 1. 圖片處理

- **格式相容性**：需要支援多種圖片格式
- **檔案大小**：需要控制圖片檔案大小

### 2. 快取管理

- **快取過期**：需要適當的快取更新機制
- **磁碟空間**：快取可能佔用大量空間

### 3. 網路效能

- **同時下載數量**：避免過多同時下載
- **頻寬使用**：控制頻寬使用

## 相關檔案

- **修改**：`scripts/civitai_manager_libs/ishortcut.py`
- **修改**：`scripts/civitai_manager_libs/scan_action.py`
- **修改**：`scripts/civitai_manager_libs/util.py`（新增圖片下載工具）
- **修改**：`scripts/civitai_manager_libs/setting.py`（新增圖片設定）
- **新建立**：`tests/test_ishortcut_http.py`
- **新建立**：`tests/test_scan_action_http.py`

## 後續工作

完成此項目後，所有模組的 HTTP 請求都已經中央化，接下來將進行整合測試和文件更新。
