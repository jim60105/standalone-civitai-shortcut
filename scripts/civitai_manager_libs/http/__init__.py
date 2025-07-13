"""
HTTP module for Civitai API interactions.

This module provides a refactored HTTP client implementation following SRP principles.
All components maintain the same public API for backward compatibility.
"""

# Import all public classes and functions to maintain backward compatibility
from .client import CivitaiHttpClient
from .image_downloader import ParallelImageDownloader
from .client_manager import get_http_client, CompleteCivitaiHttpClient

# Expose the same public API as the original http_client.py
# Note: We expose CivitaiHttpClient but get_http_client() returns CompleteCivitaiHttpClient
__all__ = [
    'CivitaiHttpClient',
    'ParallelImageDownloader', 
    'get_http_client',
]