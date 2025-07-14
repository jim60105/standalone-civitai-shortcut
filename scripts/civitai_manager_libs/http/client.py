"""
Core HTTP client for Civitai API requests with unified error handling,
timeout and retry mechanisms.
"""

import json
import time
from typing import Dict, Optional
import urllib.parse

import requests

from ..logging_config import get_logger
from ..exceptions import (
    NetworkError,
    HTTPError,
    ConnectionError,
    TimeoutError,
)
from ..error_handler import with_error_handling
from ..ui.notification_service import get_notification_service

from .. import settings
from ..settings.constants import DEFAULT_HEADERS


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
        self.api_key = api_key or settings.civitai_api_key
        self.timeout = timeout or settings.http_timeout
        self.max_retries = max_retries or settings.http_max_retries
        self.retry_delay = retry_delay or settings.http_retry_delay
        # Prepare HTTP session
        self.session = requests.Session()
        # Default headers including user-agent and optional authorization
        self.session.headers.update(DEFAULT_HEADERS or {})
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def update_api_key(self, api_key: str) -> None:
        """Update the bearer token for authorization."""
        self.api_key = api_key
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        elif 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']

    @with_error_handling(
        fallback_value=None,
        exception_types=(Exception,),
        retry_count=0,
        retry_delay=0,
        user_message=None,
    )
    def get_json(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Enhanced GET request with unified error handling."""
        response = self.session.get(url, params=params, timeout=self.timeout)
        self._handle_response_error(response)
        return response.json()

    def _handle_response_error(self, response: requests.Response) -> None:
        """Convert HTTP errors to custom exceptions instead of showing UI."""
        if response.status_code >= 400:
            error_msg = _STATUS_CODE_MESSAGES.get(
                response.status_code, f"HTTP {response.status_code}"
            )
            raise HTTPError(
                message=error_msg,
                status_code=response.status_code,
                url=str(response.url),
            )

    def _handle_connection_error(self, error: Exception, url: str) -> None:
        """Handle connection errors by raising custom exceptions."""
        if isinstance(error, requests.exceptions.Timeout):
            # TimeoutError does not accept url directly
            raise TimeoutError(
                message=f"Request timeout for {url}",
                timeout_duration=self.timeout,
            )
        elif isinstance(error, requests.exceptions.ConnectionError):
            raise ConnectionError(
                message=f"Failed to connect to {url}",
                retry_after=self.retry_delay,
            )
        else:
            raise NetworkError(
                message=f"Network error: {error}",
                cause=error,
                context={"url": url},
            )

    @with_error_handling(
        fallback_value=None,
        exception_types=(Exception,),
        retry_count=0,
        retry_delay=0,
        user_message=None,
    )
    def post_json(self, url: str, json_data: Optional[Dict] = None) -> Optional[Dict]:
        """Make POST request with JSON payload and return JSON response or None on error."""
        for attempt in range(self.max_retries):
            result = self._attempt_post_request(url, json_data, attempt)
            if result is not None or not self._should_retry_post(result, attempt):
                return result
            time.sleep(self.retry_delay)
        return None

    def _attempt_post_request(
        self, url: str, json_data: Optional[Dict], attempt: int
    ) -> Optional[Dict]:
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

    def _handle_post_connection_error(self, error: Exception, attempt: int) -> Optional[Dict]:
        """Handle connection errors for POST requests."""
        logger.warning(f"[http_client] Connection error: {error}")
        if attempt == self.max_retries - 1:
            return None
        return None

    def _handle_post_json_error(self, error: json.JSONDecodeError) -> None:
        """Handle JSON decode errors for POST requests."""
        logger.error(f"[http_client] JSON decode error: {error}")
        return None

    def _handle_post_request_error(self, error: requests.RequestException) -> None:
        """Handle general request errors for POST requests."""
        logger.error(f"[http_client] Request exception: {error}")
        return None

    def _should_retry_post(self, result: Optional[Dict], attempt: int) -> bool:
        """Determine if POST request should be retried."""
        return result is None and attempt < self.max_retries - 1

    def get_stream(
        self, url: str, headers: Optional[Dict] = None, _origin_host: Optional[str] = None
    ) -> Optional[requests.Response]:
        """Make GET request for streaming download and return response or None on error.
        On redirect to a different host, remove Authorization header.
        """
        try:
            logger.debug(f"[http_client] STREAM {url}")
            # Determine host for redirect logic
            parsed_url = urllib.parse.urlparse(url)
            current_host = parsed_url.netloc
            if _origin_host is None:
                _origin_host = current_host

            # Prepare headers (copy to avoid mutating caller's dict)
            req_headers = dict(headers) if headers else {}

            # If this is a redirect to a different host, remove Authorization header
            if current_host != _origin_host:
                if 'Authorization' in req_headers:
                    logger.debug(
                        f"[http_client] Removing Authorization header for cross-domain redirect: "
                        f"{_origin_host} -> {current_host}"
                    )
                    req_headers.pop('Authorization')

                # Temporarily remove Authorization from session headers for cross-domain requests
                original_auth = self.session.headers.pop('Authorization', None)
                try:
                    response = self.session.get(
                        url,
                        headers=req_headers,
                        stream=True,
                        timeout=self.timeout,
                        allow_redirects=False,
                    )
                finally:
                    # Restore original Authorization header if it existed
                    if original_auth is not None:
                        self.session.headers['Authorization'] = original_auth
            else:
                response = self.session.get(
                    url,
                    headers=req_headers,
                    stream=True,
                    timeout=self.timeout,
                    allow_redirects=False,
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
                    return self.get_stream(location, headers=req_headers, _origin_host=_origin_host)
                else:
                    logger.error("[http_client] Redirect without Location header")
                    return None

            return response
        except (requests.ConnectionError, requests.Timeout) as e:
            logger.warning(f"[http_client] Stream connection error: {e}")
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
        """Handle authentication or login redirect errors.

        Aborts in main thread or raises in background threads.
        """
        from ..exceptions import AuthenticationError

        raise AuthenticationError(
            message=f"Authentication required for {response.url}",
            status_code=response.status_code,
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
        notification_service = get_notification_service()
        if notification_service:
            notification_service.show_error(f"Request failed: {msg}")
        return False

    @with_error_handling(
        fallback_value=None,
        exception_types=(Exception,),
        retry_count=0,
        retry_delay=0,
        user_message=None,
    )
    def get_stream_response(self, url: str, headers: dict = None) -> Optional[requests.Response]:
        """Get streaming response for custom processing."""
        return self.get_stream(url, headers)
