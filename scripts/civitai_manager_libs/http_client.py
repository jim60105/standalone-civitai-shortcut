"""
Centralized HTTP client for Civitai API requests with unified error handling,
timeout and retry mechanisms.
"""

import json
import time
from typing import Callable, Dict, Optional, List

import threading

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
        # Handle Content-Length header case-insensitively for streaming downloads
        header_len = response.headers.get(
            "content-length", response.headers.get("Content-Length", 0)
        )
        total = int(header_len or 0)
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
                last_update = start_time
                update_interval = 2.0  # seconds between progress notifications

                for chunk in response.iter_content(chunk_size=setting.download_chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            current_time = time.time()
                            if current_time - last_update >= update_interval:
                                speed = self._calculate_speed(
                                    downloaded - resume_pos, current_time - start_time
                                )
                                progress_callback(downloaded, total_size, speed)
                                last_update = current_time

                # Final progress update after download completes
                if progress_callback:
                    total_time = time.time() - start_time
                    final_speed = self._calculate_speed(downloaded - resume_pos, total_time)
                    progress_callback(downloaded, total_size, final_speed)

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
            gr.Error("Download timeout, please check your network connection 💥!", duration=5)
        elif isinstance(error, requests.exceptions.ConnectionError):
            util.printD(f"[http_client] Connection error for {url}")
            gr.Error(
                "Network connection failed, please check your network settings 💥!", duration=5
            )
        elif hasattr(error, "response") and error.response:
            status_code = error.response.status_code
            if status_code == 403:
                gr.Error("Access denied, please check your API key 💥!", duration=8)
            elif status_code == 404:
                gr.Error("File does not exist or has been removed 💥!", duration=5)
            elif status_code >= 500:
                gr.Error("Server error, please try again later 💥!", duration=5)
            else:
                gr.Error(f"Download failed (HTTP {status_code}) 💥!", duration=5)
        else:
            util.printD(f"[http_client] Unknown download error: {error}")
            gr.Error("Unknown error occurred during download 💥!", duration=5)

        # Clean up partial file if empty
        try:
            if os.path.exists(filepath) and os.path.getsize(filepath) == 0:
                os.remove(filepath)
        except Exception:
            pass

        return False


# ------------------------------------------------------------------------------
# Performance optimization and monitoring extensions


class ChunkedDownloader:
    """Downloader supporting chunked and parallel file downloads."""

    def __init__(self, client: CivitaiHttpClient):
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

    def _fallback_download(
        self, url: str, filepath: str, progress_callback: Optional[Callable] = None
    ) -> bool:
        """Fallback to standard download when chunked download is not applicable."""
        util.printD(f"[chunked_downloader] Fallback to single-stream download: {url}")
        return self.client.download_file(url, filepath, progress_callback)

    def _sequential_download(
        self, url: str, filepath: str, total_size: int, progress_callback: Optional[Callable] = None
    ) -> bool:
        """Download file sequentially in a single stream."""
        util.printD(f"[chunked_downloader] Starting sequential download: {url}")
        downloaded = 0
        try:
            response = self.client.session.get(url, stream=True)
            if not response.ok:
                util.printD(
                    f"[chunked_downloader] Sequential download failed: HTTP {response.status_code}"
                )
                return False
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    if not chunk:
                        continue
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total_size)
            util.printD(f"[chunked_downloader] Sequential download completed: {filepath}")
            return True
        except Exception as e:
            util.printD(f"[chunked_downloader] Sequential download error: {e}")
            return False

    def _parallel_download(
        self, url: str, filepath: str, total_size: int, progress_callback: Optional[Callable] = None
    ) -> bool:
        """Download file using parallel chunked requests."""
        util.printD(f"[chunked_downloader] Starting parallel download: {url}")
        # divide into chunks
        chunk_count = self.max_parallel
        base = total_size // chunk_count
        ranges = []
        for i in range(chunk_count):
            start = i * base
            end = start + base - 1 if i < chunk_count - 1 else total_size - 1
            ranges.append((start, end))
        # progress tracking
        chunk_progress: List[int] = [0] * chunk_count
        chunk_files: List[str] = []

        def _download_chunk(idx: int, start: int, end: int):
            part_file = f"{filepath}.part{idx}"
            chunk_files.append(part_file)
            try:
                headers = {'Range': f'bytes={start}-{end}'}
                resp = self.client.session.get(url, headers=headers, stream=True)
                if resp.ok:
                    with open(part_file, 'wb') as pf:
                        for data in resp.iter_content(chunk_size=8192):
                            pf.write(data)
                            chunk_progress[idx] += len(data)
                            if progress_callback:
                                total_dl = sum(chunk_progress)
                                progress_callback(total_dl, total_size)
                else:
                    util.printD(f"[chunked_downloader] Chunk {idx} HTTP {resp.status_code}")
            except Exception as e:
                util.printD(f"[chunked_downloader] Chunk {idx} failed: {e}")

        # launch threads
        threads: List[threading.Thread] = []
        for i, (s, e) in enumerate(ranges):
            t = threading.Thread(target=_download_chunk, args=(i, s, e))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        # combine parts
        try:
            with open(filepath, 'wb') as out:
                for i in range(len(ranges)):
                    part_file = f"{filepath}.part{i}"
                    if os.path.exists(part_file):
                        with open(part_file, 'rb') as pf:
                            out.write(pf.read())
                        os.remove(part_file)
            util.printD(f"[chunked_downloader] Parallel download completed: {filepath}")
            return True
        except Exception as e:
            util.printD(f"[chunked_downloader] Failed to combine chunks: {e}")
            return False


"""
Cleanup legacy monitoring and cache classes.
"""

# Global HTTP client instance
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
        if _global_http_client.api_key != setting.civitai_api_key:
            _global_http_client.update_api_key(setting.civitai_api_key)
    return _global_http_client


def get_chunked_downloader() -> ChunkedDownloader:
    """Get chunked downloader instance using the global HTTP client."""
    return ChunkedDownloader(get_http_client())
