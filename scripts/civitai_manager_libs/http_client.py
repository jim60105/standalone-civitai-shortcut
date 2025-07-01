"""
Centralized HTTP client for Civitai API requests with unified error handling,
timeout and retry mechanisms.
"""

import json
import time
from typing import Callable, Dict, Optional, List, Tuple

import threading
import concurrent.futures

import requests
import os

# Legacy gradio stub for tests' monkeypatch fixtures
class _GrStub:
    """Stub namespace to allow test monkeypatching of gr.Error and gr.Warning."""
    pass

gr = _GrStub()

from .logging_config import get_logger
from .exceptions import APIError, AuthenticationError
from .error_handler import with_error_handling

from . import setting

logger = get_logger(__name__)

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
    307: "Temporary Redirect: Login required for this resource.",
    416: "Range Not Satisfiable: Authentication may be required.",
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

    @with_error_handling(
        fallback_value=None,
        exception_types=(Exception,),
        retry_count=0,
        retry_delay=0,
        user_message=None,
    )
    def get_json(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Enhanced GET request with unified error handling."""
        response = self.session.get(url, params=params, timeout=self.timeout)
        self._handle_response_error(response)
        return response.json()

    def _handle_response_error(self, response: requests.Response) -> None:
        """Convert HTTP errors to our custom exceptions."""
        if response.status_code >= 400:
            error_msg = _STATUS_CODE_MESSAGES.get(
                response.status_code, f"HTTP {response.status_code}"
            )
            raise APIError(message=error_msg, status_code=response.status_code)

    def post_json(self, url: str, json_data: Dict = None) -> Optional[Dict]:
        """Make POST request with JSON payload and return JSON response or None on error."""
        for attempt in range(self.max_retries):
            result = self._attempt_post_request(url, json_data, attempt)
            if result is not None or not self._should_retry_post(result, attempt):
                return result
            time.sleep(self.retry_delay)
        return None

    def _attempt_post_request(self, url: str, json_data: Dict, attempt: int) -> Optional[Dict]:
        """Attempt a single POST request."""
        try:
            logger.debug(f"[http_client] POST {url} attempt {attempt + 1}")
            response = self.session.post(url, json=json_data, timeout=self.timeout)
            logger.debug(f"[http_client] Response status: {response.status_code}")

            if response.status_code >= 400:
                self._handle_post_error_response(response)
                return None

            return response.json()

        except (requests.ConnectionError, requests.Timeout) as e:
            return self._handle_post_connection_error(e, attempt)
        except json.JSONDecodeError as e:
            return self._handle_post_json_error(e)
        except requests.RequestException as e:
            return self._handle_post_request_error(e)

    def _handle_post_error_response(self, response: requests.Response) -> None:
        """Handle HTTP error responses for POST requests."""
        msg = _STATUS_CODE_MESSAGES.get(response.status_code, f"HTTP {response.status_code} Error")
        logger.debug(f"[http_client] {msg}")
        # Removed UI calls: errors are handled via exceptions

    def _handle_post_connection_error(self, error: Exception, attempt: int) -> Optional[Dict]:
        """Handle connection errors for POST requests."""
        logger.warning(f"[http_client] Connection error: {error}")
        if attempt == self.max_retries - 1:
            # No UI notification; signal failure
            return None
        return "retry"  # Signal to retry

    def _handle_post_json_error(self, error: json.JSONDecodeError) -> None:
        """Handle JSON decode errors for POST requests."""
        logger.error(f"[http_client] JSON decode error: {error}")
        # Removed UI calls: errors are handled via exceptions
        return None

    def _handle_post_request_error(self, error: requests.RequestException) -> None:
        """Handle general request errors for POST requests."""
        logger.error(f"[http_client] Request exception: {error}")
        # Removed UI calls: errors are handled via exceptions
        return None

    def _should_retry_post(self, result: Optional[Dict], attempt: int) -> bool:
        """Determine if POST request should be retried."""
        return result == "retry" and attempt < self.max_retries - 1

    def get_stream(self, url: str, headers: Dict = None) -> Optional[requests.Response]:
        """Make GET request for streaming download and return response or None on error."""
        try:
            logger.debug(f"[http_client] STREAM {url}")
            response = self.session.get(
                url, headers=headers or {}, stream=True, timeout=self.timeout, allow_redirects=False
            )
            logger.debug(f"[http_client] Response status: {response.status_code}")

            # Handle authentication and error responses
            if not self._is_stream_response_valid(response):
                return None

            # Handle redirects manually only after validation passes
            if response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location', '')
                if location:
                    logger.debug(f"[http_client] Following redirect to: {location}")
                    return self.get_stream(location, headers)
                else:
                    logger.error("[http_client] Redirect without Location header")
                    return None

            return response
        except (requests.ConnectionError, requests.Timeout) as e:
            logger.warning(f"[http_client] Stream connection error: {e}")
            # Removed UI calls: errors are handled via exceptions
            return None

    def _is_stream_response_valid(self, response: requests.Response) -> bool:
        """Validate streaming response and handle specific status codes."""
        # Handle authentication errors (both 307 login redirects and 416 range errors)
        if response.status_code == 416:
            return self._handle_authentication_error(response, "HTTP 416")
        elif response.status_code == 307:
            location = response.headers.get('Location', '')
            if 'login' in location.lower():
                return self._handle_authentication_error(response, "HTTP 307 login redirect")
            else:
                # Non-login 307 redirects are handled as normal redirects
                return self._handle_redirect_response(response)
        elif response.status_code in [301, 302, 303, 308]:
            return self._handle_redirect_response(response)
        elif response.status_code >= 400:
            return self._handle_stream_error_response(response)

        return True

    def _handle_authentication_error(self, response: requests.Response, error_type: str) -> bool:
        """Handle authentication errors from both 307 login redirects and 416 range errors."""
        if error_type.startswith("HTTP 307"):
            location = response.headers.get('Location', '')
            logger.warning(
                f"[http_client] Authentication required - redirected to login page: {location}"
            )
        else:
            logger.warning(
                f"[http_client] Authentication required - {error_type} for: {response.url}"
            )

        # Prepare authentication error message
        if not self.api_key:
            auth_msg = (
                "🔐 This resource requires authentication. "
                "Please configure your Civitai API key in settings to download this file."
            )
        else:
            auth_msg = (
                "🔐 Authentication failed. Your API key may be invalid, expired, "
                "or lack access to this resource. Please check your Civitai API key."
            )

        # Show error message only if we're in main thread (Gradio context)
        # Otherwise, throw exception to propagate to main thread caller
        # Determine execution context: main thread indicates UI environment
        import threading
        if threading.current_thread() is threading.main_thread():
            # Removed UI calls: errors are handled via exceptions
            return False
        # In background thread - throw exception to propagate to main thread
        logger.debug("[http_client] Throwing AuthenticationError from background thread")
        raise AuthenticationError(
            message=auth_msg,
            status_code=response.status_code,
            requires_api_key=(not self.api_key),
            context={"url": str(response.url), "error_type": error_type},
        )

    def _handle_redirect_response(self, response: requests.Response) -> bool:
        """Handle non-login redirect responses."""
        location = response.headers.get('Location', '')
        logger.debug(f"[http_client] Valid redirect from {response.url} to {location}")
        return True

    def _handle_stream_error_response(self, response: requests.Response) -> bool:
        """Handle general error responses for streaming requests."""
        msg = _STATUS_CODE_MESSAGES.get(response.status_code, f"HTTP {response.status_code} Error")
        logger.debug(f"[http_client] {msg}")
        # Removed UI calls: errors are handled via exceptions
        return False

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
            # Validate file size after download
            if not self._validate_download_size(filepath, total):
                return False
            return True
        except Exception as e:
            logger.error(f"[http_client] File write error: {e}")
            # Removed UI calls: errors are handled via exceptions
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
        resume_pos = self._get_resume_position(filepath)
        download_headers = self._prepare_download_headers(headers, resume_pos)

        try:
            response = self.get_stream(url, headers=download_headers)
            if not response:
                return False

            total_size = self._calculate_total_size(response, resume_pos)
            return self._perform_resume_download(
                filepath, response, resume_pos, total_size, progress_callback
            )

        except Exception as e:
            return self._handle_download_error(e, url, filepath)

    def _get_resume_position(self, filepath: str) -> int:
        """Get the position to resume download from."""
        if setting.download_resume_enabled and os.path.exists(filepath):
            resume_pos = os.path.getsize(filepath)
            logger.debug(f"[http_client] Resuming download from position: {resume_pos}")
            return resume_pos
        return 0

    def _prepare_download_headers(self, headers: dict, resume_pos: int) -> dict:
        """Prepare headers for resume download."""
        download_headers = headers.copy() if headers else {}
        if resume_pos > 0:
            download_headers["Range"] = f"bytes={resume_pos}-"
        return download_headers

    def _calculate_total_size(self, response: requests.Response, resume_pos: int) -> int:
        """Calculate total file size including resume position."""
        total_size = int(response.headers.get("Content-Length", 0))
        if resume_pos > 0:
            total_size += resume_pos
        return total_size

    def _perform_resume_download(
        self,
        filepath: str,
        response: requests.Response,
        resume_pos: int,
        total_size: int,
        progress_callback: Callable,
    ) -> bool:
        """Perform the actual download with resume capability."""
        mode = "ab" if resume_pos > 0 else "wb"

        with open(filepath, mode) as f:
            downloaded = resume_pos
            download_tracker = self._create_download_tracker()

            for chunk in response.iter_content(chunk_size=setting.download_chunk_size):
                if not chunk:
                    continue

                f.write(chunk)
                downloaded += len(chunk)

                if progress_callback:
                    self._update_download_progress(
                        progress_callback, downloaded, total_size, resume_pos, download_tracker
                    )

            # Final progress update
            if progress_callback:
                self._send_final_download_progress(
                    progress_callback, downloaded, total_size, resume_pos, download_tracker
                )

        # Validate downloaded file
        return self._validate_download_size(filepath, total_size)

    def _create_download_tracker(self) -> dict:
        """Create a tracker for download progress timing."""
        return {'start_time': time.time(), 'last_update': time.time(), 'update_interval': 2.0}

    def _update_download_progress(
        self,
        progress_callback: Callable,
        downloaded: int,
        total_size: int,
        resume_pos: int,
        tracker: dict,
    ) -> None:
        """Update download progress if enough time has passed."""
        current_time = time.time()
        if current_time - tracker['last_update'] >= tracker['update_interval']:
            speed = self._calculate_speed(
                downloaded - resume_pos, current_time - tracker['start_time']
            )
            progress_callback(downloaded, total_size, speed)
            tracker['last_update'] = current_time

    def _send_final_download_progress(
        self,
        progress_callback: Callable,
        downloaded: int,
        total_size: int,
        resume_pos: int,
        tracker: dict,
    ) -> None:
        """Send final progress update after download completion."""
        total_time = time.time() - tracker['start_time']
        final_speed = self._calculate_speed(downloaded - resume_pos, total_time)
        progress_callback(downloaded, total_size, final_speed)

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
        # Re-raise AuthenticationError to let caller handle it properly
        if isinstance(error, AuthenticationError):
            logger.debug("[http_client] Re-raising AuthenticationError for proper handling")
            raise error

        error_handled = self._process_download_error_type(error, url)

        if not error_handled:
            logger.error(f"[http_client] Unknown download error: {error}")
            # Removed UI calls: errors are handled via exceptions
        self._cleanup_failed_download(filepath)
        return False

    def _process_download_error_type(self, error: Exception, url: str) -> bool:
        """Process different types of download errors."""
        if isinstance(error, requests.exceptions.Timeout):
            return self._handle_timeout_error(url)
        elif isinstance(error, requests.exceptions.ConnectionError):
            return self._handle_connection_error(url)
        elif hasattr(error, "response") and error.response:
            return self._handle_download_response_error(error.response)
        return False

    def _handle_timeout_error(self, url: str) -> bool:
        """Handle download timeout errors."""
        logger.warning(f"[http_client] Download timeout for {url}")
        # Removed UI calls: errors are handled via exceptions
        return True

    def _handle_connection_error(self, url: str) -> bool:
        """Handle download connection errors."""
        logger.warning(f"[http_client] Connection error for {url}")
        # Removed UI calls: errors are handled via exceptions
        return True

    def _handle_download_response_error(self, response: requests.Response) -> bool:
        """Handle HTTP response errors during download."""
        status_code = response.status_code

        # Removed UI calls: errors are handled via exceptions
        return True

    def _cleanup_failed_download(self, filepath: str) -> None:
        """Clean up partial file if download failed."""
        try:
            if os.path.exists(filepath) and os.path.getsize(filepath) == 0:
                os.remove(filepath)
        except Exception:
            pass

    def _validate_download_size(
        self, filepath: str, expected_size: int, tolerance: float = 0.1
    ) -> bool:
        """Validate downloaded file size against expected size."""
        if not os.path.exists(filepath):
            return False

        actual_size = os.path.getsize(filepath)
        if expected_size <= 0:
            return True  # Cannot validate if expected size unknown

        size_diff_ratio = abs(actual_size - expected_size) / expected_size
        if size_diff_ratio > tolerance:
            from . import util

            expected_size_str = util.format_file_size(expected_size)
            actual_size_str = util.format_file_size(actual_size)
            logger.warning(
                f"[http_client] File size mismatch: expected {expected_size}, got {actual_size}"
            )
            gr.Warning(
                f"⚠️ Downloaded file size differs significantly from expected. "
                f"Expected: {expected_size_str}, Actual: {actual_size_str}. "
                f"Please verify the download."
            )
            return False

        return True


class ParallelImageDownloader:
    """Parallel image downloader with thread-safe progress tracking."""

    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.progress_lock = threading.Lock()
        self.completed_count = 0
        self.total_count = 0

        # Progress throttling mechanism
        self.last_progress_update = 0.0
        self.progress_update_interval = 0.1  # 100ms throttle interval
        self.pending_update = False

    def download_images(
        self,
        image_tasks: List[Tuple[str, str]],
        progress_callback: Optional[Callable] = None,
        client=None,
    ) -> int:
        """Download images using ThreadPoolExecutor with progress tracking and throttling."""
        if not image_tasks:
            return 0

        self.total_count = len(image_tasks)
        self.completed_count = 0
        # Initialize throttling state
        self.last_progress_update = time.time()
        self.pending_update = False
        # Initialize authentication error tracking
        self._auth_errors = []
        success_count = 0

        client = client or get_http_client()

        # Start periodic progress update timer
        progress_timer = None
        if progress_callback:
            progress_timer = self._start_progress_timer(progress_callback)

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_task = {
                    executor.submit(self._download_single_image, url, filepath, client): (
                        url,
                        filepath,
                    )
                    for url, filepath in image_tasks
                }
                for future in concurrent.futures.as_completed(future_to_task):
                    url, filepath = future_to_task[future]
                    try:
                        if future.result():
                            success_count += 1
                            logger.info(
                                f"[parallel_downloader] Successfully downloaded: {filepath}"
                            )
                        else:
                            logger.error(f"[parallel_downloader] Failed to download: {url}")
                            # Note: Individual image download failures are often auth-related
                            # Authentication errors are now collected and handled below
                    except Exception as e:
                        logger.error(f"[parallel_downloader] Download exception for {url}: {e}")
                    finally:
                        self._update_progress(progress_callback)

            # Show authentication error if any images failed due to auth issues
            if self._auth_errors:
                # Show the first authentication error message in a toast
                first_auth_error = self._auth_errors[0]
                try:
                    gr.Error(str(first_auth_error))
                except Exception:
                    pass
                auth_count = len(self._auth_errors)
                logger.error(
                    f"[parallel_downloader] {auth_count} image(s) failed due to authentication"
                )

            return success_count
        finally:
            # Stop periodic timer and send final update
            if progress_timer:
                self._stop_progress_timer(progress_timer)
            if progress_callback:
                self._send_final_progress_update(progress_callback)

    def _download_single_image(self, url: str, filepath: str, client) -> bool:
        """Download single image with error handling."""
        try:
            return client.download_file(url, filepath)
        except AuthenticationError as e:
            # Log authentication error and let the caller handle it
            logger.warning(f"[parallel_downloader] Authentication error for {url}: {e}")
            # Store the error for the main thread to handle
            if not hasattr(self, '_auth_errors'):
                self._auth_errors = []
            self._auth_errors.append(e)
            return False

    def _update_progress(self, progress_callback: Optional[Callable]):
        """Thread-safe progress update with throttling mechanism."""
        if not progress_callback:
            return

        with self.progress_lock:
            self.completed_count += 1
            current_time = time.time()

            should_update = self._should_send_progress_update(current_time)
            if should_update:
                self._send_progress_update(progress_callback, current_time)
            else:
                self.pending_update = True

    def _should_send_progress_update(self, current_time: float) -> bool:
        """Determine if progress update should be sent now."""
        is_final_update = self.completed_count >= self.total_count
        time_since_last = current_time - self.last_progress_update
        return time_since_last >= self.progress_update_interval or is_final_update

    def _send_progress_update(self, progress_callback: Callable, current_time: float) -> None:
        """Send progress update to callback."""
        done = self.completed_count
        total = self.total_count
        desc = f"Downloading image {done}/{total}"
        progress_callback(done, total, desc)
        self.last_progress_update = current_time
        self.pending_update = False

    def _start_progress_timer(self, progress_callback: Callable) -> threading.Timer:
        """Start periodic progress update timer."""

        def periodic_update():
            with self.progress_lock:
                if self.pending_update and self.completed_count < self.total_count:
                    done = self.completed_count
                    total = self.total_count
                    desc = f"Downloading image {done}/{total}"
                    progress_callback(done, total, desc)
                    self.last_progress_update = time.time()
                    self.pending_update = False

            # Schedule next update if not complete
            if self.completed_count < self.total_count:
                timer = threading.Timer(self.progress_update_interval, periodic_update)
                timer.daemon = True
                timer.start()
                return timer
            return None

        timer = threading.Timer(self.progress_update_interval, periodic_update)
        timer.daemon = True
        timer.start()
        return timer

    def _stop_progress_timer(self, timer: threading.Timer):
        """Stop progress update timer."""
        if timer:
            timer.cancel()

    def _send_final_progress_update(self, progress_callback: Callable):
        """Send final progress update."""
        with self.progress_lock:
            if self.completed_count > 0:
                done = self.completed_count
                total = self.total_count
                desc = f"Downloaded {done}/{total} images"
                progress_callback(done, total, desc)


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
            logger.error(f"[chunked_downloader] Failed to get file info: {e}")
            return self._fallback_download(url, filepath, progress_callback)

        if supports and total > 10 * setting.http_chunk_size and self.max_parallel > 1:
            return self._parallel_download(url, filepath, total, progress_callback)
        return self._sequential_download(url, filepath, total, progress_callback)

    def _fallback_download(
        self, url: str, filepath: str, progress_callback: Optional[Callable] = None
    ) -> bool:
        """Fallback to standard download when chunked download is not applicable."""
        logger.info(f"[chunked_downloader] Fallback to single-stream download: {url}")
        return self.client.download_file(url, filepath, progress_callback)

    def _sequential_download(
        self, url: str, filepath: str, total_size: int, progress_callback: Optional[Callable] = None
    ) -> bool:
        """Download file sequentially in a single stream."""
        logger.info(f"[chunked_downloader] Starting sequential download: {url}")
        downloaded = 0
        try:
            # Use the client's get_stream method to ensure proper error handling
            response = self.client.get_stream(url)
            if not response:
                logger.error(
                    "[chunked_downloader] Sequential download failed: get_stream returned None"
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
            logger.info(f"[chunked_downloader] Sequential download completed: {filepath}")
            return True
        except Exception as e:
            logger.error(f"[chunked_downloader] Sequential download error: {e}")
            return False

    def _parallel_download(
        self, url: str, filepath: str, total_size: int, progress_callback: Optional[Callable] = None
    ) -> bool:
        """Download file using parallel chunked requests."""
        logger.info(f"[chunked_downloader] Starting parallel download: {url}")

        ranges = self._calculate_download_ranges(total_size)
        chunk_progress, chunk_files = self._initialize_parallel_tracking(len(ranges))

        # Execute parallel downloads
        threads = self._start_parallel_downloads(
            url, filepath, ranges, chunk_progress, progress_callback, total_size
        )
        self._wait_for_downloads(threads)

        # Combine downloaded parts
        return self._combine_download_parts(filepath, ranges)

    def _calculate_download_ranges(self, total_size: int) -> List[Tuple[int, int]]:
        """Calculate byte ranges for parallel downloading."""
        chunk_count = self.max_parallel
        base = total_size // chunk_count
        ranges = []

        for i in range(chunk_count):
            start = i * base
            end = start + base - 1 if i < chunk_count - 1 else total_size - 1
            ranges.append((start, end))

        return ranges

    def _initialize_parallel_tracking(self, chunk_count: int) -> Tuple[List[int], List[str]]:
        """Initialize tracking structures for parallel downloads."""
        chunk_progress = [0] * chunk_count
        chunk_files = []
        return chunk_progress, chunk_files

    def _start_parallel_downloads(
        self,
        url: str,
        filepath: str,
        ranges: List[Tuple[int, int]],
        chunk_progress: List[int],
        progress_callback: Optional[Callable],
        total_size: int,
    ) -> List[threading.Thread]:
        """Start all parallel download threads."""
        threads = []

        for i, (start, end) in enumerate(ranges):

            def create_download_task(idx, s, e):
                return lambda: self._download_chunk(
                    url, filepath, idx, s, e, chunk_progress, progress_callback, total_size
                )

            download_func = create_download_task(i, start, end)
            thread = threading.Thread(target=download_func)
            thread.start()
            threads.append(thread)

        return threads

    def _wait_for_downloads(self, threads: List[threading.Thread]) -> None:
        """Wait for all download threads to complete."""
        for thread in threads:
            thread.join()

    def _download_chunk(
        self,
        url: str,
        filepath: str,
        idx: int,
        start: int,
        end: int,
        chunk_progress: List[int],
        progress_callback: Optional[Callable],
        total_size: int,
    ) -> None:
        """Download a single chunk of the file."""
        part_file = f"{filepath}.part{idx}"

        try:
            headers = {'Range': f'bytes={start}-{end}'}
            response = self.client.session.get(url, headers=headers, stream=True)

            if response.ok:
                self._write_chunk_data(
                    part_file, response, idx, chunk_progress, progress_callback, total_size
                )
            else:
                logger.error(f"[chunked_downloader] Chunk {idx} HTTP {response.status_code}")

        except Exception as e:
            logger.error(f"[chunked_downloader] Chunk {idx} failed: {e}")

    def _write_chunk_data(
        self,
        part_file: str,
        response: requests.Response,
        idx: int,
        chunk_progress: List[int],
        progress_callback: Optional[Callable],
        total_size: int,
    ) -> None:
        """Write chunk data to file and update progress."""
        with open(part_file, 'wb') as pf:
            for data in response.iter_content(chunk_size=8192):
                pf.write(data)
                chunk_progress[idx] += len(data)

                if progress_callback:
                    total_dl = sum(chunk_progress)
                    progress_callback(total_dl, total_size)

    def _combine_download_parts(self, filepath: str, ranges: List[Tuple[int, int]]) -> bool:
        """Combine all downloaded parts into final file."""
        try:
            with open(filepath, 'wb') as out:
                for i in range(len(ranges)):
                    part_file = f"{filepath}.part{i}"
                    if os.path.exists(part_file):
                        with open(part_file, 'rb') as pf:
                            out.write(pf.read())
                        os.remove(part_file)

            logger.info(f"[chunked_downloader] Parallel download completed: {filepath}")
            return True

        except Exception as e:
            logger.error(f"[chunked_downloader] Failed to combine chunks: {e}")
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

    # Early return if client exists and update configuration
    if _global_http_client is not None:
        _update_client_configuration(_global_http_client)
        return _global_http_client

    # Create new client with thread safety
    with _client_lock:
        # Double-check after acquiring lock
        if _global_http_client is None:
            _global_http_client = _create_new_http_client()

    return _global_http_client


def _create_new_http_client() -> CivitaiHttpClient:
    """Create a new HTTP client with current settings."""
    return CivitaiHttpClient(
        api_key=setting.civitai_api_key,
        timeout=setting.http_timeout,
        max_retries=setting.http_max_retries,
        retry_delay=setting.http_retry_delay,
    )


def _update_client_configuration(client: CivitaiHttpClient) -> None:
    """Update client configuration to match current settings."""
    # Batch configuration updates to reduce redundant checks
    config_updates = [
        (client.api_key != setting.civitai_api_key, 'api_key'),
        (client.timeout != setting.http_timeout, 'timeout'),
        (client.max_retries != setting.http_max_retries, 'max_retries'),
        (client.retry_delay != setting.http_retry_delay, 'retry_delay'),
    ]

    for needs_update, config_name in config_updates:
        if needs_update:
            if config_name == 'api_key':
                client.update_api_key(setting.civitai_api_key)
            else:
                setattr(client, config_name, getattr(setting, f'http_{config_name}'))


def get_chunked_downloader() -> ChunkedDownloader:
    """Get chunked downloader instance using the global HTTP client."""
    return ChunkedDownloader(get_http_client())
