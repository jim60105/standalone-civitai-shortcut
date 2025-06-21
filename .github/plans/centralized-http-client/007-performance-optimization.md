# Backlog Item 007: 效能最佳化與監控機制

## 工作描述

對中央化 HTTP 客戶端進行效能最佳化，新增監控和統計功能，確保在高負載情況下仍能穩定運作，並提供豐富的診斷資訊。

## 背景分析

經過前面的實作和整合測試，我們已經有了一個功能完整的中央化 HTTP 客戶端。但在實際使用中，可能會遇到以下效能問題：

1. **高併發請求**：多個模組同時發起 HTTP 請求
2. **大檔案下載**：長時間佔用連線資源
3. **網路不穩定**：需要智慧重試和連線管理
4. **記憶體使用**：大量下載可能導致記憶體不足
5. **缺乏監控**：無法了解 HTTP 請求的效能和錯誤情況

## 具體需求

### 1. 連線池最佳化

#### 1.1 實作連線池管理

**更新 `http_client.py`**：
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.poolmanager import PoolManager
import threading
import time
from typing import Dict, List, Optional

class OptimizedHTTPClient(CivitaiHttpClient):
    """Optimized HTTP client with connection pooling and monitoring."""
    
    def __init__(self, api_key: str = None, timeout: int = 20, max_retries: int = 3):
        super().__init__(api_key, timeout, max_retries)
        
        # Connection pool settings
        self.pool_connections = 10
        self.pool_maxsize = 20
        self.pool_block = False
        
        # Monitoring data
        self._stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_bytes_downloaded': 0,
            'total_time_spent': 0,
            'error_counts': {},
            'active_downloads': {},
            'request_history': []
        }
        self._stats_lock = threading.Lock()
        
        # Initialize session with optimized settings
        self._setup_optimized_session()
    
    def _setup_optimized_session(self):
        """Set up requests session with optimized settings."""
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504, 524],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        
        # Set up HTTP adapter with connection pooling
        adapter = HTTPAdapter(
            pool_connections=self.pool_connections,
            pool_maxsize=self.pool_maxsize,
            pool_block=self.pool_block,
            max_retries=retry_strategy
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': f'CivitaiShortcut/{setting.version}',
            'Accept': 'application/json, image/*, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
```

#### 1.2 智慧重試機制

```python
def _make_request_with_smart_retry(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
    """Make request with smart retry logic."""
    start_time = time.time()
    last_error = None
    
    for attempt in range(self.max_retries + 1):
        try:
            # Update statistics
            with self._stats_lock:
                self._stats['total_requests'] += 1
            
            # Make request
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            
            # Check if response is successful
            if response.ok:
                # Update success statistics
                elapsed_time = time.time() - start_time
                with self._stats_lock:
                    self._stats['successful_requests'] += 1
                    self._stats['total_time_spent'] += elapsed_time
                
                util.printD(f"[http_client] Request successful: {method} {url} ({response.status_code})")
                return response
            
            else:
                # Handle HTTP errors
                self._handle_http_error(response, url, attempt)
                last_error = requests.exceptions.HTTPError(f"HTTP {response.status_code}")
                
                if not self._should_retry_status(response.status_code):
                    break
        
        except (requests.exceptions.Timeout, 
                requests.exceptions.ConnectionError,
                requests.exceptions.RequestException) as e:
            
            self._handle_network_error(e, url, attempt)
            last_error = e
            
            if attempt < self.max_retries:
                # Exponential backoff with jitter
                wait_time = min(self.retry_delay * (2 ** attempt), 60)
                jitter = wait_time * 0.1 * (random.random() - 0.5)
                time.sleep(wait_time + jitter)
    
    # All retries failed
    elapsed_time = time.time() - start_time
    with self._stats_lock:
        self._stats['failed_requests'] += 1
        self._stats['total_time_spent'] += elapsed_time
    
    self._handle_final_failure(last_error, url)
    return None

def _should_retry_status(self, status_code: int) -> bool:
    """Determine if we should retry based on status code."""
    # Don't retry client errors (except 429)
    if 400 <= status_code < 500 and status_code != 429:
        return False
    
    # Retry server errors and 429
    return status_code >= 500 or status_code == 429

def _handle_http_error(self, response: requests.Response, url: str, attempt: int):
    """Handle HTTP errors with detailed logging."""
    status_code = response.status_code
    
    with self._stats_lock:
        self._stats['error_counts'][f'http_{status_code}'] = \
            self._stats['error_counts'].get(f'http_{status_code}', 0) + 1
    
    util.printD(f"[http_client] HTTP {status_code} error for {url} (attempt {attempt + 1})")
    
    # Special handling for specific status codes
    if status_code == 429:
        util.printD("[http_client] Rate limited, will retry with longer delay")
    elif status_code == 524:
        util.printD("[http_client] Cloudflare timeout, will retry")
```

### 2. 下載效能最佳化

#### 2.1 分段下載和並行處理

```python
class ChunkedDownloader:
    """Optimized downloader with chunked and parallel download support."""
    
    def __init__(self, client: OptimizedHTTPClient):
        self.client = client
        self.chunk_size = 1024 * 1024  # 1MB chunks
        self.max_parallel_chunks = 4
    
    def download_large_file(self, url: str, filepath: str, 
                           progress_callback: Optional[Callable] = None,
                           enable_parallel: bool = True) -> bool:
        """Download large file with optional parallel chunking."""
        
        # First, get file size
        try:
            head_response = self.client.session.head(url, timeout=30)
            if not head_response.ok:
                return self._fallback_download(url, filepath, progress_callback)
            
            total_size = int(head_response.headers.get('Content-Length', 0))
            supports_range = 'bytes' in head_response.headers.get('Accept-Ranges', '')
            
        except Exception as e:
            util.printD(f"[chunked_downloader] Failed to get file info: {e}")
            return self._fallback_download(url, filepath, progress_callback)
        
        # Decide whether to use parallel download
        if (enable_parallel and 
            supports_range and 
            total_size > 10 * 1024 * 1024 and  # > 10MB
            self.max_parallel_chunks > 1):
            
            return self._parallel_download(url, filepath, total_size, progress_callback)
        else:
            return self._sequential_download(url, filepath, total_size, progress_callback)
    
    def _parallel_download(self, url: str, filepath: str, total_size: int,
                          progress_callback: Optional[Callable]) -> bool:
        """Download file using parallel chunks."""
        util.printD(f"[chunked_downloader] Starting parallel download: {url}")
        
        # Calculate chunk sizes
        chunk_size = total_size // self.max_parallel_chunks
        chunks = []
        
        for i in range(self.max_parallel_chunks):
            start = i * chunk_size
            end = start + chunk_size - 1 if i < self.max_parallel_chunks - 1 else total_size - 1
            chunks.append((start, end))
        
        # Download chunks in parallel
        chunk_files = []
        completed_chunks = threading.Event()
        chunk_progress = [0] * len(chunks)
        
        def download_chunk(chunk_index: int, start: int, end: int):
            chunk_file = f"{filepath}.part{chunk_index}"
            chunk_files.append(chunk_file)
            
            try:
                headers = {'Range': f'bytes={start}-{end}'}
                response = self.client.session.get(url, headers=headers, stream=True)
                
                if response.ok:
                    with open(chunk_file, 'wb') as f:
                        for data in response.iter_content(chunk_size=8192):
                            f.write(data)
                            chunk_progress[chunk_index] += len(data)
                            
                            # Update overall progress
                            if progress_callback:
                                total_downloaded = sum(chunk_progress)
                                progress_callback(total_downloaded, total_size)
                
            except Exception as e:
                util.printD(f"[chunked_downloader] Chunk {chunk_index} failed: {e}")
        
        # Start parallel downloads
        threads = []
        for i, (start, end) in enumerate(chunks):
            thread = threading.Thread(target=download_chunk, args=(i, start, end))
            thread.start()
            threads.append(thread)
        
        # Wait for all chunks to complete
        for thread in threads:
            thread.join()
        
        # Combine chunks
        try:
            with open(filepath, 'wb') as outfile:
                for i in range(len(chunks)):
                    chunk_file = f"{filepath}.part{i}"
                    if os.path.exists(chunk_file):
                        with open(chunk_file, 'rb') as infile:
                            outfile.write(infile.read())
                        os.remove(chunk_file)
            
            util.printD(f"[chunked_downloader] Parallel download completed: {filepath}")
            return True
            
        except Exception as e:
            util.printD(f"[chunked_downloader] Failed to combine chunks: {e}")
            return False
```

#### 2.2 記憶體使用最佳化

```python
class MemoryEfficientDownloader:
    """Memory-efficient downloader for large files."""
    
    def __init__(self, max_memory_usage: int = 50 * 1024 * 1024):  # 50MB
        self.max_memory_usage = max_memory_usage
        self.active_downloads = {}
        self.memory_monitor = threading.Thread(target=self._monitor_memory, daemon=True)
        self.memory_monitor.start()
    
    def _monitor_memory(self):
        """Monitor memory usage and adjust download parameters."""
        import psutil
        
        while True:
            try:
                process = psutil.Process()
                memory_info = process.memory_info()
                memory_usage = memory_info.rss
                
                # If memory usage is high, reduce chunk sizes
                if memory_usage > self.max_memory_usage:
                    util.printD(f"[memory_monitor] High memory usage detected: {memory_usage / 1024 / 1024:.1f}MB")
                    self._reduce_chunk_sizes()
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                util.printD(f"[memory_monitor] Error monitoring memory: {e}")
                time.sleep(30)
    
    def _reduce_chunk_sizes(self):
        """Reduce chunk sizes to save memory."""
        for download_id, download_info in self.active_downloads.items():
            if 'chunk_size' in download_info:
                download_info['chunk_size'] = max(8192, download_info['chunk_size'] // 2)
                util.printD(f"[memory_monitor] Reduced chunk size for {download_id}")
```

### 3. 監控和統計系統

#### 3.1 請求統計收集

```python
class HTTPClientMonitor:
    """Monitor HTTP client performance and statistics."""
    
    def __init__(self):
        self.stats = {
            'requests_by_hour': {},
            'error_rates': {},
            'download_speeds': [],
            'response_times': [],
            'bandwidth_usage': 0,
            'cache_hit_rate': 0
        }
        self.start_time = time.time()
    
    def record_request(self, url: str, method: str, status_code: int, 
                      response_time: float, bytes_transferred: int = 0):
        """Record request statistics."""
        current_hour = time.strftime('%Y-%m-%d %H:00:00')
        
        # Update hourly request counts
        if current_hour not in self.stats['requests_by_hour']:
            self.stats['requests_by_hour'][current_hour] = {
                'total': 0, 'success': 0, 'error': 0
            }
        
        self.stats['requests_by_hour'][current_hour]['total'] += 1
        
        if status_code < 400:
            self.stats['requests_by_hour'][current_hour]['success'] += 1
        else:
            self.stats['requests_by_hour'][current_hour]['error'] += 1
        
        # Update response times
        self.stats['response_times'].append(response_time)
        if len(self.stats['response_times']) > 1000:
            self.stats['response_times'] = self.stats['response_times'][-1000:]
        
        # Update bandwidth usage
        self.stats['bandwidth_usage'] += bytes_transferred
        
        # Calculate download speed if applicable
        if bytes_transferred > 0 and response_time > 0:
            speed = bytes_transferred / response_time
            self.stats['download_speeds'].append(speed)
            if len(self.stats['download_speeds']) > 100:
                self.stats['download_speeds'] = self.stats['download_speeds'][-100:]
    
    def get_performance_report(self) -> Dict:
        """Generate performance report."""
        now = time.time()
        uptime = now - self.start_time
        
        # Calculate averages
        avg_response_time = (
            sum(self.stats['response_times']) / len(self.stats['response_times'])
            if self.stats['response_times'] else 0
        )
        
        avg_download_speed = (
            sum(self.stats['download_speeds']) / len(self.stats['download_speeds'])
            if self.stats['download_speeds'] else 0
        )
        
        total_requests = sum(
            hour_data['total'] for hour_data in self.stats['requests_by_hour'].values()
        )
        
        total_errors = sum(
            hour_data['error'] for hour_data in self.stats['requests_by_hour'].values()
        )
        
        error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'uptime_seconds': uptime,
            'total_requests': total_requests,
            'error_rate_percent': error_rate,
            'avg_response_time_ms': avg_response_time * 1000,
            'avg_download_speed_mbps': avg_download_speed / 1024 / 1024 * 8,
            'total_bandwidth_mb': self.stats['bandwidth_usage'] / 1024 / 1024,
            'requests_per_minute': total_requests / (uptime / 60) if uptime > 0 else 0
        }
```

#### 3.2 即時監控介面

```python
def create_monitoring_ui():
    """Create Gradio interface for HTTP client monitoring."""
    import gradio as gr
    
    def get_status_info():
        """Get current HTTP client status."""
        monitor = get_http_monitor()
        report = monitor.get_performance_report()
        
        status_text = f"""
        ### HTTP 客戶端狀態監控
        
        **運行時間**: {report['uptime_seconds']:.0f} 秒
        **總請求數**: {report['total_requests']}
        **錯誤率**: {report['error_rate_percent']:.2f}%
        **平均響應時間**: {report['avg_response_time_ms']:.1f} ms
        **平均下載速度**: {report['avg_download_speed_mbps']:.2f} Mbps
        **總流量使用**: {report['total_bandwidth_mb']:.2f} MB
        **每分鐘請求數**: {report['requests_per_minute']:.1f}
        """
        
        return status_text
    
    def get_error_statistics():
        """Get error statistics."""
        client = get_http_client()
        if hasattr(client, '_stats'):
            error_counts = client._stats.get('error_counts', {})
            
            if error_counts:
                error_text = "### 錯誤統計\n\n"
                for error_type, count in sorted(error_counts.items()):
                    error_text += f"**{error_type}**: {count} 次\n"
                return error_text
            else:
                return "### 錯誤統計\n\n目前沒有錯誤記錄 ✅"
        
        return "### 錯誤統計\n\n監控資料不可用"
    
    def clear_statistics():
        """Clear all statistics."""
        client = get_http_client()
        if hasattr(client, '_stats'):
            with client._stats_lock:
                client._stats = {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'total_bytes_downloaded': 0,
                    'total_time_spent': 0,
                    'error_counts': {},
                    'active_downloads': {},
                    'request_history': []
                }
        
        monitor = get_http_monitor()
        monitor.stats = {
            'requests_by_hour': {},
            'error_rates': {},
            'download_speeds': [],
            'response_times': [],
            'bandwidth_usage': 0,
            'cache_hit_rate': 0
        }
        
        return "統計資料已清除 ✅"
    
    with gr.Blocks(title="HTTP Client Monitor") as monitor_interface:
        gr.Markdown("## HTTP 客戶端監控面板")
        
        with gr.Row():
            with gr.Column():
                status_display = gr.Markdown(get_status_info())
                refresh_btn = gr.Button("刷新狀態", variant="primary")
                
            with gr.Column():
                error_display = gr.Markdown(get_error_statistics())
                clear_btn = gr.Button("清除統計", variant="secondary")
        
        # Auto-refresh every 30 seconds
        refresh_btn.click(
            fn=get_status_info,
            outputs=[status_display]
        )
        
        refresh_btn.click(
            fn=get_error_statistics,
            outputs=[error_display]
        )
        
        clear_btn.click(
            fn=clear_statistics,
            outputs=[gr.Textbox(value="統計資料已清除", visible=False)]
        )
    
    return monitor_interface
```

### 4. 快取最佳化

#### 4.1 智慧快取系統

```python
class IntelligentCache:
    """Intelligent caching system for HTTP responses."""
    
    def __init__(self, max_size: int = 100 * 1024 * 1024):  # 100MB
        self.max_size = max_size
        self.current_size = 0
        self.cache = {}
        self.access_times = {}
        self.cache_lock = threading.Lock()
    
    def get(self, key: str) -> Optional[bytes]:
        """Get cached response."""
        with self.cache_lock:
            if key in self.cache:
                self.access_times[key] = time.time()
                util.printD(f"[cache] Cache hit for: {key}")
                return self.cache[key]
            
            util.printD(f"[cache] Cache miss for: {key}")
            return None
    
    def put(self, key: str, data: bytes, ttl: int = 3600):
        """Put response in cache with TTL."""
        data_size = len(data)
        
        with self.cache_lock:
            # Check if we need to evict items
            while self.current_size + data_size > self.max_size and self.cache:
                self._evict_lru()
            
            # Store data
            self.cache[key] = data
            self.access_times[key] = time.time()
            self.current_size += data_size
            
            util.printD(f"[cache] Cached {data_size} bytes for: {key}")
    
    def _evict_lru(self):
        """Evict least recently used item."""
        if not self.access_times:
            return
        
        # Find least recently used key
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        
        # Remove from cache
        if lru_key in self.cache:
            data_size = len(self.cache[lru_key])
            del self.cache[lru_key]
            del self.access_times[lru_key]
            self.current_size -= data_size
            
            util.printD(f"[cache] Evicted LRU item: {lru_key}")
```

### 5. 設定最佳化

#### 5.1 效能相關設定

在 `setting.py` 中新增：
```python
# HTTP Client Performance Settings
http_pool_connections = 10
http_pool_maxsize = 20
http_enable_chunked_download = True
http_max_parallel_chunks = 4
http_chunk_size = 1024 * 1024  # 1MB

# Monitoring Settings
http_enable_monitoring = True
http_stats_retention_hours = 24
http_performance_log_level = "INFO"

# Cache Settings
http_cache_enabled = True
http_cache_max_size_mb = 100
http_cache_default_ttl = 3600  # 1 hour

# Memory Management
http_max_memory_usage_mb = 200
http_memory_monitor_enabled = True
http_memory_check_interval = 10  # seconds
```

## 測試要求

### 1. 效能測試

**建立 `tests/performance/test_http_performance.py`**：
```python
"""Performance tests for optimized HTTP client."""

import pytest
import time
import threading
from concurrent.futures import ThreadPoolExecutor

class TestHTTPPerformance:
    """Performance tests for HTTP client."""
    
    def test_concurrent_request_performance(self):
        """Test performance under concurrent load."""
        # Test with multiple concurrent requests
        pass
    
    def test_large_file_download_performance(self):
        """Test large file download performance."""
        # Test download speed and memory usage
        pass
    
    def test_cache_performance(self):
        """Test cache hit rates and performance."""
        # Test cache effectiveness
        pass
    
    def test_memory_usage_under_load(self):
        """Test memory usage under heavy load."""
        # Monitor memory usage during stress test
        pass
```

### 2. 監控測試

**建立 `tests/monitoring/test_monitoring.py`**：
```python
"""Tests for monitoring and statistics."""

class TestMonitoring:
    """Tests for monitoring functionality."""
    
    def test_statistics_collection(self):
        """Test statistics collection accuracy."""
        pass
    
    def test_performance_reporting(self):
        """Test performance report generation."""
        pass
    
    def test_error_tracking(self):
        """Test error tracking and reporting."""
        pass
```

## 驗收標準

### 1. 效能指標

- [ ] 併發請求處理能力提升 50% 以上
- [ ] 大檔案下載速度提升 30% 以上
- [ ] 記憶體使用量減少 25% 以上
- [ ] 錯誤恢復時間縮短 40% 以上

### 2. 監控功能

- [ ] 即時統計資料準確
- [ ] 效能報告完整且有用
- [ ] 錯誤追蹤詳細
- [ ] 監控介面使用者友善

### 3. 穩定性

- [ ] 長時間運行穩定
- [ ] 高負載下不崩潰
- [ ] 記憶體洩漏檢查通過
- [ ] 錯誤恢復機制有效

### 4. 使用者體驗

- [ ] 下載速度明顯提升
- [ ] 介面響應更快
- [ ] 錯誤提示更及時
- [ ] 監控資訊清楚

## 相關檔案

- **修改**：`scripts/civitai_manager_libs/http_client.py`
- **新建立**：`scripts/civitai_manager_libs/monitoring.py`
- **修改**：`scripts/civitai_manager_libs/setting.py`
- **新建立**：`tests/performance/` 目錄下的效能測試
- **新建立**：`tests/monitoring/` 目錄下的監控測試

## 後續工作

完成此項目後，將進行最終的文件更新和部署準備。
