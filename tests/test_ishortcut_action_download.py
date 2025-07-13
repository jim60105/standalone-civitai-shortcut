import sys
import os
from unittest.mock import Mock, patch

# Ensure project root is on path
sys.path.insert(0, os.getcwd())

# Import the function under test
from scripts.civitai_manager_libs.ishortcut_action import on_download_model_click
from scripts.civitai_manager_libs import settings


class TestDownloadModelClick:
    """Test the on_download_model_click function"""

    @patch('scripts.civitai_manager_libs.ishortcut_action.downloader.download_file_thread_async')
    @patch('scripts.civitai_manager_libs.ishortcut_action.get_notification_service')
    @patch('scripts.civitai_manager_libs.ishortcut_action.datetime')
    def test_download_model_click_with_create_model_folder(
        self, mock_datetime, mock_get_notification_service, mock_download_async
    ):
        """Test download with CREATE_MODEL_FOLDER setting"""
        # Setup mocks
        mock_time = Mock()
        mock_datetime.datetime.now.return_value = mock_time
        mock_notification_service = Mock()
        mock_get_notification_service.return_value = mock_notification_service

        # Test parameters
        model_id = "12345"
        version_id = "67890"
        file_name = ["1:test_model.safetensors"]
        vs_folder = True
        vs_foldername = "version_folder"  # Use string instead of bytes
        cs_foldername = settings.CREATE_MODEL_FOLDER
        ms_foldername = "test_model_folder"

        # Call the function
        result = on_download_model_click(
            model_id, version_id, file_name, vs_folder, vs_foldername, cs_foldername, ms_foldername
        )

        # Verify download_file_thread_async was called with correct parameters
        mock_download_async.assert_called_once_with(
            file_name,
            version_id,
            True,
            vs_folder,
            vs_foldername.encode('utf-8'),
            None,
            ms_foldername,
        )

        # Verify return values (they are gr.update objects which don't have a simple type check)
        assert len(result) == 2

    @patch('scripts.civitai_manager_libs.ishortcut_action.downloader.download_file_thread_async')
    @patch('scripts.civitai_manager_libs.ishortcut_action.get_notification_service')
    @patch('scripts.civitai_manager_libs.ishortcut_action.datetime')
    def test_download_model_click_with_custom_folder(
        self, mock_datetime, mock_get_notification_service, mock_download_async
    ):
        """Test download with custom classification folder"""
        # Setup mocks
        mock_time = Mock()
        mock_datetime.datetime.now.return_value = mock_time
        mock_notification_service = Mock()
        mock_get_notification_service.return_value = mock_notification_service

        # Test parameters
        model_id = "12345"
        version_id = "67890"
        file_name = ["1:test_model.safetensors"]
        vs_folder = False
        vs_foldername = None
        cs_foldername = "custom_classification"
        ms_foldername = "test_model_folder"

        # Call the function
        result = on_download_model_click(
            model_id, version_id, file_name, vs_folder, vs_foldername, cs_foldername, ms_foldername
        )

        # Verify download_file_thread_async was called with correct parameters
        mock_download_async.assert_called_once_with(
            file_name, version_id, False, False, None, cs_foldername, ms_foldername
        )

        # Verify return values (they are gr.update objects which don't have a simple type check)
        assert len(result) == 2

    @patch('scripts.civitai_manager_libs.ishortcut_action.downloader.download_file_thread_async')
    @patch('scripts.civitai_manager_libs.ishortcut_action.get_notification_service')
    def test_download_model_click_missing_parameters(
        self, mock_get_notification_service, mock_download_async
    ):
        """Test download with missing parameters"""
        # Setup mocks
        mock_notification_service = Mock()
        mock_get_notification_service.return_value = mock_notification_service

        # Test with missing version_id
        result1 = on_download_model_click(
            "12345", None, ["1:test.file"], True, "folder", settings.CREATE_MODEL_FOLDER, "model"
        )

        # Test with missing model_id
        result2 = on_download_model_click(
            None, "67890", ["1:test.file"], True, "folder", settings.CREATE_MODEL_FOLDER, "model"
        )

        # Verify download_file_thread_async was NOT called
        mock_download_async.assert_not_called()

        # Verify return values
        assert len(result1) == 2
        assert len(result2) == 2

    @patch('scripts.civitai_manager_libs.ishortcut_action.downloader.download_file_thread_async')
    @patch('scripts.civitai_manager_libs.ishortcut_action.get_notification_service')
    @patch('scripts.civitai_manager_libs.ishortcut_action.datetime')
    def test_download_model_click_notification_processing(
        self, mock_datetime, mock_get_notification_service, mock_download_async
    ):
        """Test that notification processing is called"""
        # Setup mocks
        mock_time = Mock()
        mock_datetime.datetime.now.return_value = mock_time
        mock_notification_service = Mock()
        mock_notification_service.process_queued_notifications = Mock()
        mock_get_notification_service.return_value = mock_notification_service

        # Test parameters
        model_id = "12345"
        version_id = "67890"
        file_name = ["1:test_model.safetensors"]
        vs_folder = True
        vs_foldername = "version_folder"  # Use string instead of bytes
        cs_foldername = settings.CREATE_MODEL_FOLDER
        ms_foldername = "test_model_folder"

        # Call the function
        on_download_model_click(
            model_id, version_id, file_name, vs_folder, vs_foldername, cs_foldername, ms_foldername
        )

        # Verify process_queued_notifications was called
        mock_notification_service.process_queued_notifications.assert_called_once()
