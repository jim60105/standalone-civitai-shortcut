"""
Global HTTP client instance management.
"""

import threading

from .client import CivitaiHttpClient
from .file_downloader import FileDownloadMixin
from .. import settings
from ..settings import config_manager

# Create a complete client class that includes file download capabilities
class CompleteCivitaiHttpClient(CivitaiHttpClient, FileDownloadMixin):
    """Complete HTTP client with all download capabilities."""
    pass

# Global HTTP client instance
_global_http_client = None
_client_lock = threading.Lock()


def get_http_client() -> CompleteCivitaiHttpClient:
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


def _create_new_http_client() -> CompleteCivitaiHttpClient:
    """Create a new HTTP client with current settings."""
    return CompleteCivitaiHttpClient(
        api_key=settings.civitai_api_key,
        timeout=settings.http_timeout,
        max_retries=settings.http_max_retries,
        retry_delay=settings.http_retry_delay,
    )


def _update_client_configuration(client: CompleteCivitaiHttpClient) -> None:
    """Update client configuration to match current settings."""
    # Batch configuration updates to reduce redundant checks
    config_updates = [
        (client.api_key != settings.civitai_api_key, 'api_key'),
        (client.timeout != settings.http_timeout, 'timeout'),
        (client.max_retries != settings.http_max_retries, 'max_retries'),
        (client.retry_delay != settings.http_retry_delay, 'retry_delay'),
    ]

    for needs_update, config_name in config_updates:
        if needs_update:
            if config_name == 'api_key':
                client.update_api_key(config_manager.get_setting('civitai_api_key'))
            else:
                setattr(client, config_name, getattr(settings, f'http_{config_name}'))