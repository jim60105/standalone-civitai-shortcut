import time
import json
from functools import wraps
from typing import Any, Callable, Optional, Type
from urllib.error import URLError

import requests

from scripts.civitai_manager_libs.exceptions import (
    CivitaiShortcutError,
    FileOperationError,
    NetworkError,
    ValidationError,
)
from scripts.civitai_manager_libs.logging_config import get_logger

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
            for attempt in range(retry_count + 1):
                try:
                    return func(*args, **kwargs)
                except exception_types as e:

                    if log_errors:
                        context = {
                            "function": func.__name__,
                            "module": func.__module__,
                            "attempt": attempt + 1,
                            "max_attempts": retry_count + 1,
                            "args": str(args)[:200],
                            "kwargs": str(kwargs)[:200],
                        }
                        logger.error(f"Error in {func.__name__}: {e}", extra=context)

                    if attempt < retry_count:
                        time.sleep(retry_delay)
                        continue

                    if user_message:
                        try:
                            import gradio as gr

                            gr.Error(user_message)
                        except Exception:
                            pass

                    if not isinstance(e, CivitaiShortcutError):
                        error_class = _map_exception_type(e)
                        raise error_class(message=str(e), context=context, cause=e) from e
                    raise

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
