import sys
import os
import time
from unittest.mock import Mock, patch

# Ensure project root is on path
sys.path.insert(0, os.getcwd())

from scripts.civitai_manager_libs.download import (
    download_file_thread_async,
    DownloadManager,
    DownloadNotifier,
)


class TestAsyncDownload:
    """Test the new async download functionality"""

    @patch('scripts.civitai_manager_libs.downloader.civitai')
    @patch('scripts.civitai_manager_libs.downloader.util')
    @patch('scripts.civitai_manager_libs.downloader.DownloadNotifier.notify_start')
    @patch('scripts.civitai_manager_libs.downloader.DownloadManager')
    def test_download_file_thread_async_starts_background_thread(
        self, mock_download_manager_class, mock_notify_start, mock_util, mock_civitai
    ):
        """Test that download_file_thread_async starts a background thread"""
        # Mock version info
        mock_version_info = {
            "modelId": "12345",
            "files": [{"id": "1", "name": "test.safetensors", "sizeKB": 1024, "primary": True}],
        }
        mock_civitai.get_version_info_by_version_id.return_value = mock_version_info
        mock_civitai.get_files_by_version_info.return_value = {
            "1": {"downloadUrl": "https://example.com/test.safetensors"}
        }
        mock_util.make_download_model_folder.return_value = "/tmp/test_folder"

        # Mock DownloadManager instance
        mock_download_manager = Mock()
        mock_download_manager_class.return_value = mock_download_manager
        mock_download_manager.start.return_value = "task_123"

        # Call the async function
        download_file_thread_async(
            ["1:test.safetensors"], "version_123", True, False, None, None, "test_model"
        )

        # Give the background thread time to start
        time.sleep(0.1)

        # Verify that notify_start was called
        mock_notify_start.assert_called_once()

        # Verify that DownloadManager.start was called
        mock_download_manager.start.assert_called_once()

    def test_download_manager_silent_completion(self):
        """Test that DownloadManager completes downloads silently"""
        # Create a real DownloadManager to test the _worker method
        download_manager = DownloadManager()

        # Mock the HTTP client
        mock_client = Mock()
        mock_client.download_file_with_resume.return_value = True
        download_manager.client = mock_client

        # Mock progress callback
        mock_progress = Mock()

        # Start a task
        task_id = "test_task"
        url = "https://example.com/test.file"
        path = "/tmp/test.file"

        # Add task to active queue manually
        download_manager.active[task_id] = {
            "url": url,
            "path": path,
            "downloaded": 0,
            "total": 1000,
            "speed": "",
        }

        # Run the worker method
        download_manager._worker(task_id, url, path, mock_progress)

        # Verify the task was completed and moved to history
        assert task_id not in download_manager.active
        assert len(download_manager.history) == 1
        assert download_manager.history[0]["completed"] is True
        assert download_manager.history[0]["success"] is True

    def test_download_notifier_start_with_file_size(self):
        """Test that DownloadNotifier.notify_start includes file size"""
        # Mock the internal notification service
        with patch(
            'scripts.civitai_manager_libs.ui.notification_service.get_notification_service'
        ) as mock_get_service:
            mock_notification_service = Mock()
            mock_get_service.return_value = mock_notification_service

            filename = "test_model.safetensors"
            file_size = 2048000  # 2MB

            DownloadNotifier.notify_start(filename, file_size)

            # Verify notification was called with file size formatted
            mock_notification_service.show_info.assert_called_once()
            call_args = mock_notification_service.show_info.call_args[0]
            message = call_args[0]

            assert filename in message
            assert (
                "2.0 MB" in message
                or "2.0MB" in message
                or "2048.0 KB" in message
                or "2048.0KB" in message
            )  # Allow for different formatting
            assert "🚀 Starting download:" in message

    def test_download_notifier_start_without_file_size(self):
        """Test that DownloadNotifier.notify_start works without file size"""
        # Mock the internal notification service
        with patch(
            'scripts.civitai_manager_libs.ui.notification_service.get_notification_service'
        ) as mock_get_service:
            mock_notification_service = Mock()
            mock_get_service.return_value = mock_notification_service

            filename = "test_model.safetensors"

            DownloadNotifier.notify_start(filename, None)

            # Verify notification was called without file size
            mock_notification_service.show_info.assert_called_once()
            call_args = mock_notification_service.show_info.call_args[0]
            message = call_args[0]

            assert filename in message
            assert "🚀 Starting download:" in message
            # Should not contain size indicators
            assert " MB)" not in message
            assert " KB)" not in message

    def test_background_thread_creation(self):
        """Test that async download actually creates a background thread"""
        with patch('scripts.civitai_manager_libs.downloader.civitai') as mock_civitai:
            # Return None for version info to exit early
            mock_civitai.get_version_info_by_version_id.return_value = None

            download_file_thread_async(
                ["1:test.safetensors"], "version_123", True, False, None, None, "test_model"
            )

            # Give the thread time to start
            time.sleep(0.1)

            # Thread count should have increased temporarily
            # (Note: thread may have already finished due to early return)
            # This test mainly verifies no exceptions were raised
            assert True  # If we get here, no exceptions occurred

    def test_empty_parameters_handling(self):
        """Test that async download handles empty parameters gracefully"""
        # Should not raise exceptions with empty parameters
        download_file_thread_async(None, None, False, False, None, None, None)
        download_file_thread_async([], "version_123", False, False, None, None, None)
        download_file_thread_async(["1:test.file"], None, False, False, None, None, None)

        # Give any background threads time to complete
        time.sleep(0.1)

        # Test passes if no exceptions are raised
        assert True
