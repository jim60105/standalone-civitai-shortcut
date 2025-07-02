import time
from typing import Optional, Dict, Any

from scripts.civitai_manager_libs.logging_config import get_logger

logger = get_logger(__name__)


class CivitaiShortcutError(Exception):
    """Base exception for all Civitai Shortcut errors."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[Any, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.context = context or {}
        self.cause = cause
        self.timestamp = time.time()


class NetworkError(CivitaiShortcutError):
    """Network-related errors (API calls, downloads)."""

    pass


class FileOperationError(CivitaiShortcutError):
    """File I/O related errors."""

    pass


class ConfigurationError(CivitaiShortcutError):
    """Configuration and settings related errors."""

    pass


class ValidationError(CivitaiShortcutError):
    """Data validation errors."""

    pass


class DataValidationError(CivitaiShortcutError):
    """Data validation errors for metadata processing."""

    pass


class APIError(NetworkError):
    """Civitai API specific errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.status_code = status_code


class AuthenticationError(APIError):
    """Authentication errors (401, 403, 307, 416 requiring auth)."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        requires_api_key: bool = True,
        **kwargs,
    ):
        super().__init__(message, status_code, **kwargs)
        self.requires_api_key = requires_api_key


class HTTPError(NetworkError):
    """HTTP request related error."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        url: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.url = url


class ConnectionError(NetworkError):
    """Network connection error."""

    def __init__(
        self,
        message: str,
        retry_after: Optional[float] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class TimeoutError(NetworkError):
    """Request timeout error."""

    def __init__(
        self,
        message: str,
        timeout_duration: Optional[float] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.timeout_duration = timeout_duration


class DownloadError(FileOperationError):
    """File download error."""

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        bytes_downloaded: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.file_path = file_path
        self.bytes_downloaded = bytes_downloaded


class AuthenticationRequiredError(APIError):
    """Authentication required error (inherits APIError)."""

    def __init__(
        self,
        message: str,
        resource_url: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.resource_url = resource_url
        self.should_abort_process = True
