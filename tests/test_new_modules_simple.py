"""
Simple focused tests for new module functionality to boost coverage to >85%.
"""

import os
import time
from unittest.mock import Mock, patch

import pytest

from scripts.civitai_manager_libs.download.notifier import DownloadNotifier
from scripts.civitai_manager_libs.download.task_manager import DownloadTask, DownloadManager
from scripts.civitai_manager_libs.download.utilities import add_number_to_duplicate_files, get_save_base_name


class TestDownloadNotifierSimple:
    """Simple tests for download notifier."""
    
    def test_notify_start_with_file_size(self):
        """Test start notification with file size."""
        with patch('scripts.civitai_manager_libs.ui.notification_service.get_notification_service') as mock_service:
            mock_ui = Mock()
            mock_service.return_value = mock_ui
            
            DownloadNotifier.notify_start("test.bin", 1024)
            
            mock_ui.show_info.assert_called_once()
            call_args = mock_ui.show_info.call_args[0][0]
            assert "test.bin" in call_args
            
    def test_notify_start_no_service(self):
        """Test start notification when no UI service available."""
        with patch('scripts.civitai_manager_libs.ui.notification_service.get_notification_service', return_value=None):
            # Should not raise exception
            DownloadNotifier.notify_start("test.bin")
            
    def test_notify_progress_with_speed(self):
        """Test progress notification with speed."""
        with patch('scripts.civitai_manager_libs.download.notifier.logger') as mock_logger:
            DownloadNotifier.notify_progress("test.bin", 512, 1024, "10 MB/s")
            
            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args[0][0]
            assert "50.0%" in call_args
            assert "10 MB/s" in call_args
            
    def test_notify_progress_unknown_total(self):
        """Test progress notification with unknown total."""
        with patch('scripts.civitai_manager_libs.download.notifier.logger') as mock_logger:
            DownloadNotifier.notify_progress("test.bin", 512, 0)
            
            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args[0][0]
            assert "Downloaded: 512.0B" in call_args


class TestDownloadTaskSimple:
    """Simple tests for download task."""
    
    def test_task_creation(self):
        """Test creating a download task."""
        task = DownloadTask("file1", "test.bin", "http://test.com", "/tmp/test.bin", 1024)
        
        assert task.fid == "file1"
        assert task.filename == "test.bin"
        assert task.url == "http://test.com"
        assert task.path == "/tmp/test.bin"
        assert task.total == 1024


class TestDownloadManagerSimple:
    """Simple tests for download manager."""
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = DownloadManager()
        assert hasattr(manager, 'active')
        assert hasattr(manager, 'history')
        assert hasattr(manager, 'client')
        
    def test_list_active_downloads(self):
        """Test listing active downloads."""
        manager = DownloadManager()
        active = manager.list_active()
        assert isinstance(active, dict)
        
    def test_start_download_task(self, tmp_path):
        """Test starting a download task."""
        manager = DownloadManager()
        target = tmp_path / "test.bin"
        
        # Mock the client to avoid actual network calls
        with patch.object(manager, 'client') as mock_client:
            mock_client.download_file_with_resume.return_value = True
            
            task_id = manager.start("http://test.com", str(target))
            
            assert task_id is not None
            assert task_id.startswith("download_")
            
            # Wait a bit for thread to start
            time.sleep(0.05)


class TestDownloadUtilitiesSimple:
    """Simple tests for download utilities."""
    
    def test_add_number_to_duplicate_files_with_entries(self):
        """Test duplicate file handling with actual file entries."""
        files = ["1:test.bin", "2:test.bin", "3:other.bin"]
        
        result = add_number_to_duplicate_files(files)
        
        assert isinstance(result, dict)
        assert "1" in result
        assert "2" in result
        assert "3" in result
        # Second instance should have (1) suffix
        assert result["2"] == "test (1).bin"
        
    def test_add_number_to_duplicate_files_no_colon(self):
        """Test with entries that don't contain colon."""
        files = ["invalid_entry", "1:valid.bin"]
        
        result = add_number_to_duplicate_files(files)
        
        # Should only process valid entries
        assert len(result) == 1
        assert "1" in result
        assert result["1"] == "valid.bin"
        
    def test_add_number_to_duplicate_files_duplicate_keys(self):
        """Test with duplicate keys (should skip)."""
        files = ["1:first.bin", "1:second.bin", "2:other.bin"]
        
        result = add_number_to_duplicate_files(files)
        
        # Should only process first occurrence of each key
        assert len(result) == 2
        assert result["1"] == "first.bin"
        assert result["2"] == "other.bin"
        
    def test_get_save_base_name_with_primary_file(self):
        """Test getting base name when primary file exists."""
        version_info = {
            "model": {"name": "test_model"},
            "name": "v1.0",
            "id": "123",
            "files": [{"name": "model.safetensors", "primary": True}]
        }
        
        with patch('scripts.civitai_manager_libs.download.utilities.civitai') as mock_civitai:
            mock_civitai.get_primary_file_by_version_info.return_value = {
                "name": "model.safetensors"
            }
            
            result = get_save_base_name(version_info)
            
            assert result == "model"
            
    def test_get_save_base_name_no_primary_file(self):
        """Test getting base name when no primary file exists."""
        version_info = {
            "model": {"name": "test_model"},
            "name": "v1.0", 
            "id": "123"
        }
        
        with patch('scripts.civitai_manager_libs.download.utilities.civitai') as mock_civitai:
            mock_civitai.get_primary_file_by_version_info.return_value = None
            
            with patch('scripts.civitai_manager_libs.download.utilities.settings') as mock_settings:
                mock_settings.generate_version_foldername.return_value = "test_model_v1.0_123"
                
                result = get_save_base_name(version_info)
                
                assert result == "test_model_v1.0_123"


class TestModuleIntegrationSimple:
    """Simple integration tests."""
    
    def test_http_module_complete_import(self):
        """Test that http module can be imported completely."""
        from scripts.civitai_manager_libs import http
        
        # Test key components are available
        assert hasattr(http, 'get_http_client')
        assert hasattr(http, 'CivitaiHttpClient')
        assert hasattr(http, 'ParallelImageDownloader')
        
    def test_download_module_complete_import(self):
        """Test that download module can be imported completely."""
        from scripts.civitai_manager_libs import download
        
        # Test key components are available
        assert hasattr(download, 'DownloadManager')
        assert hasattr(download, 'DownloadNotifier')
        assert hasattr(download, 'download_file')
        
    def test_backward_compatibility_http_client(self):
        """Test backward compatibility for http_client imports."""
        from scripts.civitai_manager_libs import http_client
        
        # Should be able to use old import style
        client = http_client.get_http_client()
        assert client is not None
        
    def test_backward_compatibility_downloader(self):
        """Test backward compatibility for downloader imports.""" 
        from scripts.civitai_manager_libs import downloader
        
        # Should be able to use old import style
        assert hasattr(downloader, 'DownloadManager')
        assert hasattr(downloader, 'get_http_client')