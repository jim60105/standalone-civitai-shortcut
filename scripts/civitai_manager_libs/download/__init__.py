"""
Download module for file and image downloading functionality.

This module provides a refactored download implementation following SRP principles.
All components maintain the same public API for backward compatibility.
"""

# Import all public classes and functions to maintain backward compatibility
from .notifier import DownloadNotifier
from .task_manager import DownloadTask, DownloadManager
from .utilities import (
    add_number_to_duplicate_files,
    get_save_base_name,
    download_preview_image,
    download_file_thread_async,
)

# Import main download functions
from .task_manager import (
    download_file_with_auth_handling,
    download_file_with_retry,
    download_file_with_file_handling,
    download_file_with_notifications,
    download_image_file,
    download_file,
    download_file_gr,
)

# Expose the same public API as the original downloader.py
__all__ = [
    'DownloadNotifier',
    'DownloadTask',
    'DownloadManager',
    'download_file_with_auth_handling',
    'download_file_with_retry', 
    'download_file_with_file_handling',
    'download_file_with_notifications',
    'download_image_file',
    'download_file',
    'download_file_gr',
    'add_number_to_duplicate_files',
    'get_save_base_name',
    'download_preview_image',
    'download_file_thread_async',
]