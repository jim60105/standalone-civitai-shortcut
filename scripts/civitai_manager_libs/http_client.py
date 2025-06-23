"""
Centralized HTTP client for Civitai API requests with unified error handling,
timeout and retry mechanisms.
"""

import json
import time
from typing import Callable, Dict, Optional

import threading
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import requests
import gradio as gr
import os

from . import util, setting

# Mapping of HTTP status codes to user-friendly error messages
_STATUS_CODE_MESSAGES: Dict[int, str] = {
    400: "Bad Request: The request was malformed.",
    401: "Unauthorized: Invalid or expired API key.",
    403: "Forbidden: You don't have permission to access this resource.",
    404: "Not Found: Resource not found.",
    429: "Too Many Requests: Rate limit exceeded.",
    500: "Internal Server Error: An error occurred on the server.",
    502: "Bad Gateway: Received an invalid response from upstream.",
    503: "Service Unavailable: The server is temporarily unavailable.",
    504: "Gateway Timeout: The server did not respond in time.",
    524: "Cloudflare Timeout: The request timed out.",
}


class CivitaiHttpClient:
    """
    HTTP client for Civitai with support for GET/POST requests,
    timeout, retries, bearer token authentication, and streaming.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[float] = None,
    ):
        # Initialize configuration from settings when not provided
        self.api_key = api_key or setting.civitai_api_key
        self.timeout = timeout or setting.http_timeout
        self.max_retries = max_retries or setting.http_max_retries
        self.retry_delay = retry_delay or setting.http_retry_delay
        # Prepare HTTP session
        self.session = requests.Session()
        # Default headers including user-agent and optional authorization
        self.session.headers.update(setting.headers or {})
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def update_api_key(self, api_key: str) -> None:
        """Update the bearer token for authorization."""
        self.api_key = api_key
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def get_json(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make GET request and return JSON response or None on error."""
        for attempt in range(self.max_retries):
            try:
                util.printD(f"[http_client] GET {url} attempt {attempt + 1}")
                response = self.session.get(url, params=params, timeout=self.timeout)
                util.printD(f"[http_client] Response status: {response.status_code}")
                if response.status_code >= 400:
                    msg = _STATUS_CODE_MESSAGES.get(
                        response.status_code,
                        f"HTTP {response.status_code} Error",
                    )
                    util.printD(f"[http_client] {msg}")
                    gr.Error(f"Request failed: {msg}")
                    return None
                return response.json()
            except (requests.ConnectionError, requests.Timeout) as e:
                util.printD(f"[http_client] Connection error: {e}")
                if attempt == self.max_retries - 1:
                    gr.Error(f"Network error: {type(e).__name__}")
                    return None
                time.sleep(self.retry_delay)
            except json.JSONDecodeError as e:
                util.printD(f"[http_client] JSON decode error: {e}")
                gr.Error("Failed to parse JSON response")
                return None
            except requests.RequestException as e:
                util.printD(f"[http_client] Request exception: {e}")
                gr.Error(f"Request error: {e}")
                return None

    def post_json(self, url: str, json_data: Dict = None) -> Optional[Dict]:
        """Make POST request with JSON payload and return JSON response or None on error."""
        for attempt in range(self.max_retries):
            try:
                util.printD(f"[http_client] POST {url} attempt {attempt + 1}")
                response = self.session.post(url, json=json_data, timeout=self.timeout)
                util.printD(f"[http_client] Response status: {response.status_code}")
                if response.status_code >= 400:
                    msg = _STATUS_CODE_MESSAGES.get(
                        response.status_code,
                        f"HTTP {response.status_code} Error",
                    )
                    util.printD(f"[http_client] {msg}")
                    gr.Error(f"Request failed: {msg}")
                    return None
                return response.json()
            except (requests.ConnectionError, requests.Timeout) as e:
                util.printD(f"[http_client] Connection error: {e}")
                if attempt == self.max_retries - 1:
                    gr.Error(f"Network error: {type(e).__name__}")
                    return None
                time.sleep(self.retry_delay)
            except json.JSONDecodeError as e:
                util.printD(f"[http_client] JSON decode error: {e}")
                gr.Error("Failed to parse JSON response")
                return None
            except requests.RequestException as e:
                util.printD(f"[http_client] Request exception: {e}")
                gr.Error(f"Request error: {e}")
                return None

    def get_stream(self, url: str, headers: Dict = None) -> Optional[requests.Response]:
        """Make GET request for streaming download and return response or None on error."""
        try:
            util.printD(f"[http_client] STREAM {url}")
            response = self.session.get(
                url, headers=headers or {}, stream=True, timeout=self.timeout
            )
            util.printD(f"[http_client] Response status: {response.status_code}")
            if response.status_code >= 400:
                msg = _STATUS_CODE_MESSAGES.get(
                    response.status_code,
                    f"HTTP {response.status_code} Error",
                )
                util.printD(f"[http_client] {msg}")
                gr.Error(f"Request failed: {msg}")
                return None
            return response
        except (requests.ConnectionError, requests.Timeout) as e:
            util.printD(f"[http_client] Stream connection error: {e}")
            gr.Error(f"Network error: {type(e).__name__}")
            return None

    def download_file(
        self,
        url: str,
        filepath: str,
        progress_callback: Callable[[int, int], None] = None,
    ) -> bool:
        """Download file with progress tracking. Returns True on success."""
        response = self.get_stream(url)
        if not response:
            return False
        total = int(response.headers.get("content-length", 0))
        downloaded = 0
        try:
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if not chunk:
                        continue
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total)
            return True
        except Exception as e:
            util.printD(f"[http_client] File write error: {e}")
            gr.Error(f"Failed to write file: {e}")
            return False

    def get_stream_response(self, url: str, headers: dict = None) -> Optional[requests.Response]:
        """Get streaming response for custom processing."""
        return self.get_stream(url, headers)

    def download_file_with_resume(
        self,
        url: str,
        filepath: str,
        progress_callback: Callable = None,
        headers: dict = None,
    ) -> bool:
        """Download file with resume capability and progress tracking."""
        resume_pos = 0
        if setting.download_resume_enabled and os.path.exists(filepath):
            resume_pos = os.path.getsize(filepath)
            util.printD(f"[http_client] Resuming download from position: {resume_pos}")

        # Prepare headers for resume
        download_headers = headers.copy() if headers else {}
        if resume_pos > 0:
            download_headers["Range"] = f"bytes={resume_pos}-"

        try:
            response = self.get_stream(url, headers=download_headers)
            if not response:
                return False

            total_size = int(response.headers.get("Content-Length", 0))
            if resume_pos > 0:
                total_size += resume_pos

            mode = "ab" if resume_pos > 0 else "wb"
            with open(filepath, mode) as f:
                downloaded = resume_pos
                start_time = time.time()
                for chunk in response.iter_content(chunk_size=setting.download_chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            speed = self._calculate_speed(
                                downloaded - resume_pos, time.time() - start_time
                            )
                            progress_callback(downloaded, total_size, speed)

            final_size = os.path.getsize(filepath)
            if total_size > 0 and final_size < total_size:
                util.printD(f"[http_client] Incomplete download: {final_size}/{total_size}")
                return False

            return True

        except Exception as e:
            return self._handle_download_error(e, url, filepath)

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

    def _handle_download_error(self, error: Exception, url: str, filepath: str) -> bool:
        """Handle download errors with recovery strategies."""
        if isinstance(error, requests.exceptions.Timeout):
            util.printD(f"[http_client] Download timeout for {url}")
            gr.Error("下載超時，請檢查網路連線 💥!", duration=5)
        elif isinstance(error, requests.exceptions.ConnectionError):
            util.printD(f"[http_client] Connection error for {url}")
            gr.Error("網路連線失敗，請檢查網路設定 💥!", duration=5)
        elif hasattr(error, "response") and error.response:
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
            util.printD(f"[http_client] Unknown download error: {error}")
            gr.Error("下載發生未知錯誤 💥!", duration=5)

        # Clean up partial file if empty
        try:
            if os.path.exists(filepath) and os.path.getsize(filepath) == 0:
                os.remove(filepath)
        except Exception:
            pass

        return False


# ------------------------------------------------------------------------------
# Performance optimization and monitoring extensions


class OptimizedHTTPClient(CivitaiHttpClient):
    """Optimized HTTP client with connection pooling, retries, and monitoring."""

    def __init__(self, api_key: str = None, timeout: int = None, max_retries: int = None):
        super().__init__(api_key, timeout, max_retries)

        # Connection pool settings
        self.pool_connections = setting.http_pool_connections
        self.pool_maxsize = setting.http_pool_maxsize
        self.pool_block = setting.http_pool_block

        # Monitoring data
        self._stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_bytes_downloaded': 0,
            'total_time_spent': 0,
            'error_counts': {},
            'active_downloads': {},
            'request_history': [],
        }
        self._stats_lock = threading.Lock()

        # Initialize optimized session
        self._setup_optimized_session()

    def _setup_optimized_session(self):
        """Set up requests session with optimized settings and retry strategy."""
        self.session = requests.Session()

        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504, 524],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
        )
        adapter = HTTPAdapter(
            pool_connections=self.pool_connections,
            pool_maxsize=self.pool_maxsize,
            pool_block=self.pool_block,
            max_retries=retry_strategy,
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.session.headers.update(
            {
                'User-Agent': f"{setting.Extensions_Name}/{setting.Extensions_Version}",
                'Accept': 'application/json, image/*, */*',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
        )

    def _make_request_with_smart_retry(
        self, method: str, url: str, **kwargs
    ) -> Optional[requests.Response]:
        """Make HTTP request with smart retry logic and collect statistics."""
        start_time = time.time()
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                with self._stats_lock:
                    self._stats['total_requests'] += 1

                response = self.session.request(method, url, timeout=self.timeout, **kwargs)
                if response.ok:
                    elapsed = time.time() - start_time
                    with self._stats_lock:
                        self._stats['successful_requests'] += 1
                        self._stats['total_time_spent'] += elapsed
                    util.printD(
                        f"[http_client] Request successful: {method} {url} ({response.status_code})"
                    )
                    return response

                self._handle_http_error(response, url, attempt)
                last_error = Exception(f"HTTP {response.status_code}")
                if not self._should_retry_status(response.status_code):
                    break

            except (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.RequestException,
            ) as e:
                self._handle_network_error(e, url, attempt)
                last_error = e
                if attempt < self.max_retries:
                    wait = min(self.retry_delay * (2**attempt), 60)
                    jitter = wait * 0.1 * (random.random() - 0.5)
                    time.sleep(wait + jitter)

        elapsed = time.time() - start_time
        with self._stats_lock:
            self._stats['failed_requests'] += 1
            self._stats['total_time_spent'] += elapsed

        self._handle_final_failure(last_error, url)
        return None

    def _should_retry_status(self, status_code: int) -> bool:
        """Determine if retry should be attempted based on HTTP status code."""
        if 400 <= status_code < 500 and status_code != 429:
            return False
        return status_code >= 500 or status_code == 429

    def _handle_http_error(self, response: requests.Response, url: str, attempt: int):
        """Handle HTTP errors by logging and updating error counts."""
        code = response.status_code
        with self._stats_lock:
            key = f'http_{code}'
            self._stats['error_counts'][key] = self._stats['error_counts'].get(key, 0) + 1
        util.printD(f"[http_client] HTTP {code} error for {url} (attempt {attempt+1})")
        if code == 429:
            util.printD("[http_client] Rate limited, retrying later")
        elif code == 524:
            util.printD("[http_client] Cloudflare timeout, retrying")

    def _handle_network_error(self, error: Exception, url: str, attempt: int):
        """Handle network errors by logging and updating error counts."""
        err_name = type(error).__name__
        with self._stats_lock:
            key = f'network_{err_name}'
            self._stats['error_counts'][key] = self._stats['error_counts'].get(key, 0) + 1
        util.printD(f"[http_client] Network error for {url} (attempt {attempt+1}): {error}")

    def _handle_final_failure(self, error: Exception, url: str):
        """Handle the final failure after all retries."""
        util.printD(f"[http_client] Final failure for {url}: {error}")


class ChunkedDownloader:
    """Downloader supporting chunked and parallel file downloads."""

    def __init__(self, client: OptimizedHTTPClient):
        self.client = client
        self.chunk_size = setting.http_chunk_size
        self.max_parallel = setting.http_max_parallel_chunks

    def download_large_file(
        self, url: str, filepath: str, progress_callback: Optional[Callable] = None
    ) -> bool:
        """Download large file with optional parallel chunks."""
        try:
            head = self.client.session.head(url, timeout=self.client.timeout)
            if not head.ok:
                return self._fallback_download(url, filepath, progress_callback)
            total = int(head.headers.get('Content-Length', 0))
            supports = 'bytes' in head.headers.get('Accept-Ranges', '')
        except Exception as e:
            util.printD(f"[chunked_downloader] Failed to get file info: {e}")
            return self._fallback_download(url, filepath, progress_callback)

        if supports and total > 10 * setting.http_chunk_size and self.max_parallel > 1:
            return self._parallel_download(url, filepath, total, progress_callback)
        return self._sequential_download(url, filepath, total, progress_callback)

    # TODO: implement _fallback_download, _sequential_download, _parallel_download methods


class MemoryEfficientDownloader:
    """Downloader that adapts chunk size based on memory usage."""

    def __init__(self, max_memory: int = setting.http_max_memory_usage_mb * 1024 * 1024):
        self.max_memory = max_memory
        self.active = {}
        if setting.http_memory_monitor_enabled:
            monitor = threading.Thread(target=self._monitor_memory, daemon=True)
            monitor.start()

    def _monitor_memory(self):
        """Background thread to monitor memory and adjust downloads."""
        import psutil

        while True:
            try:
                proc = psutil.Process()
                usage = proc.memory_info().rss
                if usage > self.max_memory:
                    util.printD(f"[memory_monitor] High memory usage: {usage}")
                    self._reduce_chunk_sizes()
                time.sleep(setting.http_memory_check_interval)
            except Exception as e:
                util.printD(f"[memory_monitor] Error: {e}")
                time.sleep(setting.http_memory_check_interval)

    def _reduce_chunk_sizes(self):
        """Reduce chunk sizes for active downloads when memory is high."""
        for dl in self.active.values():
            if hasattr(dl, 'chunk_size'):
                dl.chunk_size = max(8192, dl.chunk_size // 2)
                util.printD("[memory_monitor] Reduced chunk size for download")


class IntelligentCache:
    """LRU cache for HTTP responses with size limit and TTL."""

    def __init__(self, max_size: int = setting.http_cache_max_size_mb * 1024 * 1024):
        self.max_size = max_size
        self.current = 0
        self.cache: Dict[str, bytes] = {}
        self.access: Dict[str, float] = {}
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[bytes]:
        """Retrieve data from cache if available."""
        with self.lock:
            if key in self.cache:
                self.access[key] = time.time()
                util.printD(f"[cache] Hit for {key}")
                return self.cache[key]
            util.printD(f"[cache] Miss for {key}")
        return None

    def put(self, key: str, data: bytes, ttl: int = setting.http_cache_default_ttl):
        """Store data in cache, evicting LRU items if necessary."""
        size = len(data)
        with self.lock:
            while self.current + size > self.max_size and self.cache:
                self._evict_lru()
            self.cache[key] = data
            self.access[key] = time.time()
            self.current += size
            util.printD(f"[cache] Cached {size} bytes for {key}")

    def _evict_lru(self):
        """Evict the least recently used cache entry."""
        if not self.access:
            return
        oldest = min(self.access, key=self.access.get)
        data = self.cache.pop(oldest, None)
        self.access.pop(oldest, None)
        if data:
            self.current -= len(data)
            util.printD(f"[cache] Evicted LRU item: {oldest}")
