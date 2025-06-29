import json
from functools import wraps
from typing import Any, Callable, Optional, Type
from urllib.error import URLError

import requests

from .exceptions import (
    CivitaiShortcutError,
    FileOperationError,
    NetworkError,
    APIError,
    ValidationError,
)
from .logging_config import get_logger

logger = get_logger(__name__)


def with_error_handling(
    fallback_value: Any = None,
    exception_types: tuple = (Exception,),
    retry_count: int = 0,
    retry_delay: float = 1.0,
    log_errors: bool = True,
    user_message: Optional[str] = None,
) -> Callable:
    """Decorator for unified exception handling with retry logic."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_types as e:
                # Log the error with minimal context
                if log_errors:
                    logger.error(
                        f"Error in {func.__name__}: {e}",
                        extra={"func_name": func.__name__, "module_name": func.__module__},
                    )
                # Special-case Cloudflare timeout (524): show specific message and fallback
                if isinstance(e, APIError) and getattr(e, "status_code", None) == 524:
                    try:
                        import gradio as gr

                        gr.Error(str(e))
                    except Exception:
                        pass
                    return fallback_value
                # General error handling: show exception class name for user-friendly error
                try:
                    import gradio as gr

                    gr.Error(type(e).__name__)
                except Exception:
                    pass
                return fallback_value

        return wrapper

    return decorator


def _map_exception_type(original_exception: Exception) -> Type[CivitaiShortcutError]:
    """Map standard exceptions to our custom exception types."""
    if isinstance(original_exception, (IOError, OSError, FileNotFoundError)):
        return FileOperationError
    if isinstance(original_exception, (requests.RequestException, URLError)):
        return NetworkError
    if isinstance(original_exception, (json.JSONDecodeError, ValueError)):
        return ValidationError
    return CivitaiShortcutError
