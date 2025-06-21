# Backlog Item 004: 重構 downloader.py 模組檔案下載邏輯

## 工作描述

將 `downloader.py` 模組中的檔案下載相關 HTTP 請求重構為使用中央化的 `CivitaiHttpClient`，統一大檔案下載的錯誤處理和進度追蹤機制。

## 背景分析

通過程式碼分析，`downloader.py` 模組中有 5 個 `requests.get` 使用位置：

1. **`download_image_file()` 函數**（第 263 行）：下載模型相關的圖片檔案
2. **`download_file()` 函數**（第 325 行）：下載大型模型檔案（主要下載函數）
3. **`download_file_gr()` 函數**（第 395 行）：具有 Gradio 進度條的檔案下載
4. **第 171 行**：在圖片下載流程中的另一個位置
5. **第 195 行**：在另一個圖片下載流程中

這個模組負責下載大型檔案（如 AI 模型），是最關鍵的下載組件，需要特別注意斷點續傳、進度追蹤和錯誤恢復。

## 具體需求

### 1. 整合 HTTP 客戶端

- **匯入並配置 HTTP 客戶端**：
  ```python
  from .http_client import CivitaiHttpClient
  
  # Module-level HTTP client instance for downloads
  _download_client = None
  
  def get_download_client():
      """Get or create HTTP client instance optimized for large file downloads."""
      global _download_client
      if _download_client is None:
          _download_client = CivitaiHttpClient(
              api_key=setting.civitai_api_key,
              timeout=setting.download_timeout or 300,  # 5 minutes for large files
              max_retries=setting.download_max_retries or 5,
              retry_delay=setting.download_retry_delay or 10
          )
      return _download_client
  ```

### 2. 重構大檔案下載函數

#### 2.1 `download_file()` 函數重構

**現狀問題**：
- 直接使用 `requests.get()` 進行大檔案下載
- 有重試機制但錯誤處理不完整
- 支援斷點續傳但實作複雜
- 沒有使用者友善的錯誤提示

**重構目標**：
```python
def download_file(url, file_name):
    """Download large files with robust error handling and resume capability."""
    util.printD(f"[downloader] Starting download: {url} -> {file_name}")
    
    client = get_download_client()
    
    # Create progress callback for internal use
    def progress_callback(downloaded: int, total: int, speed: str = ""):
        percentage = (downloaded / total * 100) if total > 0 else 0
        util.printD(f"[downloader] Progress: {percentage:.1f}% ({downloaded}/{total} bytes) {speed}")
    
    success = client.download_file_with_resume(
        url=url,
        filepath=file_name,
        progress_callback=progress_callback,
        headers={"Authorization": f"Bearer {setting.civitai_api_key}"}
    )
    
    if success:
        util.printD(f"[downloader] Successfully downloaded: {file_name}")
        print(f"{os.path.basename(file_name)} successfully downloaded.")
    else:
        util.printD(f"[downloader] Failed to download: {url}")
        print(f"Error: File download failed. {os.path.basename(file_name)}")
        
        # Show user-friendly error
        import gradio as gr
        gr.Error(f"檔案下載失敗 💥! {os.path.basename(file_name)}", duration=5)
    
    return success
```

#### 2.2 `download_file_gr()` 函數重構

**現狀問題**：
- 複製了大部分 `download_file()` 的邏輯
- Gradio 進度更新混雜在下載邏輯中
- 錯誤處理邏輯重複

**重構目標**：
```python
def download_file_gr(url, file_name, progress_gr=None):
    """Download files with Gradio progress bar integration."""
    util.printD(f"[downloader] Starting Gradio download: {url} -> {file_name}")
    
    client = get_download_client()
    
    # Create Gradio-specific progress callback
    def gradio_progress_callback(downloaded: int, total: int, speed: str = ""):
        if progress_gr:
            percentage = (downloaded / total * 100) if total > 0 else 0
            progress_gr(percentage / 100, f"下載中: {percentage:.1f}% {speed}")
    
    success = client.download_file_with_resume(
        url=url,
        filepath=file_name,
        progress_callback=gradio_progress_callback,
        headers={"Authorization": f"Bearer {setting.civitai_api_key}"}
    )
    
    if success:
        util.printD(f"[downloader] Gradio download completed: {file_name}")
        if progress_gr:
            progress_gr(1.0, "下載完成 ✅")
    else:
        util.printD(f"[downloader] Gradio download failed: {url}")
        if progress_gr:
            progress_gr(0, "下載失敗 ❌")
        
        # Show user-friendly error
        import gradio as gr
        gr.Error(f"檔案下載失敗 💥! 請檢查網路連線和存儲空間", duration=8)
    
    return success
```

#### 2.3 `download_image_file()` 函數重構

**重構目標**：
```python
def download_image_file(model_name, image_urls, progress_gr=None):
    """Download model-related images with improved error handling."""
    if not model_name:
        util.printD("[downloader] download_image_file: model_name is empty")
        return
    
    model_folder = util.make_download_image_folder(model_name)
    if not model_folder:
        util.printD("[downloader] Failed to create download folder")
        return
    
    save_folder = os.path.join(model_folder, "images")
    os.makedirs(save_folder, exist_ok=True)
    
    if not image_urls or len(image_urls) == 0:
        util.printD("[downloader] No image URLs to download")
        return
    
    client = get_download_client()
    success_count = 0
    total_count = len(image_urls)
    
    util.printD(f"[downloader] Starting download of {total_count} images for model: {model_name}")
    
    for image_count, img_url in enumerate(image_urls, start=1):
        if progress_gr:
            progress_gr((image_count - 1) / total_count, f"下載圖片 {image_count}/{total_count}")
        
        result = util.is_url_or_filepath(img_url)
        
        if result == "filepath":
            # Handle local file copying
            if os.path.basename(img_url) != setting.no_card_preview_image:
                description_img = os.path.join(save_folder, os.path.basename(img_url))
                try:
                    shutil.copyfile(img_url, description_img)
                    success_count += 1
                except Exception as e:
                    util.printD(f"[downloader] Failed to copy image {img_url}: {e}")
        
        elif result == "url":
            # Handle URL download
            img_name = f"image_{image_count:03d}.jpg"
            img_path = os.path.join(save_folder, img_name)
            
            if client.download_file(img_url, img_path):
                success_count += 1
                util.printD(f"[downloader] Downloaded image: {img_path}")
            else:
                util.printD(f"[downloader] Failed to download image: {img_url}")
    
    util.printD(f"[downloader] Image download complete: {success_count}/{total_count} successful")
    
    if progress_gr:
        if success_count == total_count:
            progress_gr(1.0, f"圖片下載完成 ✅ ({success_count}/{total_count})")
        else:
            progress_gr(1.0, f"部分圖片下載完成 ⚠️ ({success_count}/{total_count})")
    
    if success_count < total_count:
        import gradio as gr
        failed_count = total_count - success_count
        gr.Error(f"部分圖片下載失敗 ({failed_count} 個) 💥!", duration=5)
```

### 3. 增強 HTTP 客戶端支援大檔案下載

#### 3.1 斷點續傳功能

在 `http_client.py` 中新增：

```python
def download_file_with_resume(self, url: str, filepath: str, 
                              progress_callback: Callable = None,
                              headers: dict = None) -> bool:
    """Download file with resume capability and progress tracking."""
    
    # Check if file exists and get current size
    resume_pos = 0
    if os.path.exists(filepath):
        resume_pos = os.path.getsize(filepath)
        util.printD(f"[http_client] Resuming download from position: {resume_pos}")
    
    # Set up headers for resume
    download_headers = headers.copy() if headers else {}
    if resume_pos > 0:
        download_headers['Range'] = f'bytes={resume_pos}-'
    
    try:
        response = self._make_request('GET', url, headers=download_headers, stream=True)
        if not response:
            return False
        
        # Get total file size
        total_size = int(response.headers.get('Content-Length', 0))
        if resume_pos > 0:
            total_size += resume_pos
        
        # Download with progress tracking
        mode = 'ab' if resume_pos > 0 else 'wb'
        with open(filepath, mode) as f:
            downloaded = resume_pos
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if progress_callback:
                        speed = self._calculate_speed(downloaded, time.time())
                        progress_callback(downloaded, total_size, speed)
        
        # Verify download completion
        final_size = os.path.getsize(filepath)
        if total_size > 0 and final_size < total_size:
            util.printD(f"[http_client] Incomplete download: {final_size}/{total_size}")
            return False
        
        return True
        
    except Exception as e:
        self._handle_error(e, url)
        return False
```

#### 3.2 速度計算和統計

```python
def _calculate_speed(self, bytes_downloaded: int, elapsed_time: float) -> str:
    """Calculate download speed in human-readable format."""
    if elapsed_time <= 0:
        return ""
    
    speed_bps = bytes_downloaded / elapsed_time
    
    if speed_bps < 1024:
        return f"{speed_bps:.1f} B/s"
    elif speed_bps < 1024 * 1024:
        return f"{speed_bps / 1024:.1f} KB/s"
    else:
        return f"{speed_bps / (1024 * 1024):.1f} MB/s"
```

### 4. 下載管理和監控

#### 4.1 下載任務管理器

```python
class DownloadManager:
    """Manage multiple download tasks with monitoring and control."""
    
    def __init__(self):
        self.active_downloads = {}
        self.download_history = []
        self.client = get_download_client()
    
    def start_download(self, url: str, filepath: str, 
                      progress_callback: Callable = None) -> str:
        """Start a new download task and return task ID."""
        task_id = f"download_{int(time.time())}_{len(self.active_downloads)}"
        
        def wrapped_callback(downloaded, total, speed):
            if progress_callback:
                progress_callback(downloaded, total, speed)
            
            # Update internal tracking
            self.active_downloads[task_id] = {
                'url': url,
                'filepath': filepath,
                'downloaded': downloaded,
                'total': total,
                'speed': speed,
                'start_time': time.time()
            }
        
        # Start download in background thread
        thread = threading.Thread(
            target=self._download_worker,
            args=(task_id, url, filepath, wrapped_callback)
        )
        thread.daemon = True
        thread.start()
        
        return task_id
    
    def _download_worker(self, task_id: str, url: str, filepath: str, 
                        progress_callback: Callable):
        """Worker function for background downloads."""
        try:
            success = self.client.download_file_with_resume(
                url, filepath, progress_callback
            )
            
            # Record completion
            task_info = self.active_downloads.pop(task_id, {})
            task_info['completed'] = True
            task_info['success'] = success
            task_info['end_time'] = time.time()
            
            self.download_history.append(task_info)
            
        except Exception as e:
            util.printD(f"[downloader] Download worker error for {task_id}: {e}")
            self.active_downloads.pop(task_id, None)
    
    def get_active_downloads(self) -> dict:
        """Get information about all active downloads."""
        return self.active_downloads.copy()
    
    def cancel_download(self, task_id: str) -> bool:
        """Cancel an active download task."""
        if task_id in self.active_downloads:
            # Note: This is a simplified cancellation
            # Full implementation would need thread interruption
            self.active_downloads.pop(task_id)
            return True
        return False
```

### 5. 設定和最佳化

#### 5.1 新增下載相關設定

在 `setting.py` 中新增：

```python
# Download settings
download_timeout = 300  # 5 minutes for large files
download_max_retries = 5
download_retry_delay = 10  # seconds
download_chunk_size = 8192  # bytes
download_max_concurrent = 3  # maximum concurrent downloads
download_resume_enabled = True
download_verify_checksum = False  # future feature
```

#### 5.2 磁碟空間檢查

```python
def check_disk_space(filepath: str, required_size: int) -> bool:
    """Check if there's enough disk space for download."""
    try:
        stat = shutil.disk_usage(os.path.dirname(filepath))
        available = stat.free
        
        # Add 10% buffer for safety
        required_with_buffer = required_size * 1.1
        
        if available < required_with_buffer:
            util.printD(f"[downloader] Insufficient disk space: {available} < {required_with_buffer}")
            import gradio as gr
            gr.Error("磁碟空間不足，無法下載檔案 💥!", duration=8)
            return False
        
        return True
    except Exception as e:
        util.printD(f"[downloader] Error checking disk space: {e}")
        return True  # Assume OK if can't check
```

## 測試要求

### 1. 單元測試

在 `tests/test_downloader.py` 中新增：

- **大檔案下載測試**：
  - 正常下載流程
  - 斷點續傳功能
  - 網路中斷恢復
  - 磁碟空間不足處理

- **圖片下載測試**：
  - 批次圖片下載
  - 混合 URL 和本地檔案處理
  - 部分下載失敗處理

- **進度追蹤測試**：
  - Gradio 進度條整合
  - 速度計算準確性
  - 進度回調功能

### 2. 整合測試

- **與 HTTP 客戶端整合**：
  - 大檔案下載效能
  - 錯誤處理一致性
  - 超時處理

- **與檔案系統整合**：
  - 目錄建立和權限
  - 檔案覆寫處理
  - 臨時檔案清理

### 3. 效能測試

- **大檔案下載效能**：
  - 1GB+ 檔案下載測試
  - 記憶體使用監控
  - 下載速度基準測試

## 實作細節

### 1. 向後相容性

```python
# Maintain existing function signatures
def download_file(url, file_name):
    """Maintain compatibility with existing calls."""
    pass

def download_file_gr(url, file_name, progress_gr=None):
    """Maintain Gradio integration compatibility."""
    pass

def download_image_file(model_name, image_urls, progress_gr=None):
    """Maintain image download compatibility."""
    pass
```

### 2. 錯誤恢復策略

```python
def _handle_download_error(self, error: Exception, url: str, filepath: str) -> bool:
    """Handle download errors with recovery strategies."""
    
    if isinstance(error, requests.exceptions.Timeout):
        util.printD(f"[downloader] Download timeout for {url}")
        gr.Error("下載超時，請檢查網路連線 💥!", duration=5)
    
    elif isinstance(error, requests.exceptions.ConnectionError):
        util.printD(f"[downloader] Connection error for {url}")
        gr.Error("網路連線失敗，請檢查網路設定 💥!", duration=5)
    
    elif hasattr(error, 'response') and error.response:
        status_code = error.response.status_code
        if status_code == 403:
            gr.Error("存取被拒絕，請檢查 API 金鑰 💥!", duration=8)
        elif status_code == 404:
            gr.Error("檔案不存在或已被移除 💥!", duration=5)
        elif status_code >= 500:
            gr.Error("伺服器錯誤，請稍後再試 💥!", duration=5)
        else:
            gr.Error(f"下載失敗 (HTTP {status_code}) 💥!", duration=5)
    
    else:
        util.printD(f"[downloader] Unknown download error: {error}")
        gr.Error("下載發生未知錯誤 💥!", duration=5)
    
    # Clean up partial files
    if os.path.exists(filepath) and os.path.getsize(filepath) == 0:
        os.remove(filepath)
    
    return False
```

## 驗收標準

### 1. 功能完整性

- [ ] 大檔案下載功能正常（支援 GB 級檔案）
- [ ] 斷點續傳功能正常
- [ ] 進度追蹤準確
- [ ] 批次圖片下載正常
- [ ] Gradio 進度條整合正常

### 2. 錯誤處理

- [ ] 網路錯誤有適當的使用者提示
- [ ] 磁碟空間不足有適當處理
- [ ] 檔案寫入錯誤有適當處理
- [ ] 部分下載檔案有適當清理

### 3. 效能最佳化

- [ ] 下載速度符合預期
- [ ] 記憶體使用合理（不會因大檔案而爆記憶體）
- [ ] 併發下載控制正常
- [ ] 斷點續傳節省頻寬

### 4. 使用者體驗

- [ ] 下載進度清楚顯示
- [ ] 錯誤訊息有用且友善
- [ ] 下載完成有適當提示
- [ ] 不會阻塞使用者介面

### 5. 程式碼品質

- [ ] 通過所有程式碼品質檢查
- [ ] 測試涵蓋率達到 85% 以上
- [ ] 所有文件使用英文
- [ ] 遵循現有程式碼風格

## 風險與注意事項

### 1. 大檔案處理

- **記憶體限制**：需要確保大檔案下載不會佔用過多記憶體
- **磁碟 I/O**：頻繁的檔案寫入可能影響效能

### 2. 網路穩定性

- **長時間下載**：大檔案下載時間長，網路中斷機率高
- **頻寬限制**：需要考慮使用者的頻寬限制

### 3. 伺服器負載

- **API 配額**：需要遵守 Civitai API 的配額限制
- **禮貌性原則**：避免對伺服器造成過大負載

## 相關檔案

- **修改**：`scripts/civitai_manager_libs/downloader.py`
- **修改**：`scripts/civitai_manager_libs/http_client.py`（新增大檔案下載支援）
- **修改**：`scripts/civitai_manager_libs/setting.py`（新增下載設定）
- **新建立或更新**：`tests/test_downloader.py`

## 後續工作

完成此項目後，接下來將重構 `ishortcut.py` 和 `scan_action.py` 中剩餘的 HTTP 請求。
