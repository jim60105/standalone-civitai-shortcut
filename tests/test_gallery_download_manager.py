import os
import pytest
from unittest.mock import MagicMock, patch, call
from scripts.civitai_manager_libs.gallery.download_manager import GalleryDownloadManager
from scripts.civitai_manager_libs import settings


@pytest.fixture
def download_manager():
    """Fixture for GalleryDownloadManager."""
    with patch(
        'scripts.civitai_manager_libs.gallery.download_manager.get_http_client'
    ) as mock_get_client:
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        manager = GalleryDownloadManager()
        manager.client = mock_client
        yield manager


def test_download_single_image_success(download_manager: GalleryDownloadManager):
    """Test successful download of a single image."""
    # Arrange
    img_url = "http://example.com/image.jpg"
    save_path = "/tmp/image.jpg"
    download_manager.client.download_file.return_value = True

    with patch('os.path.exists', return_value=True):
        # Act
        result = download_manager.download_single_image(img_url, save_path)

        # Assert
        assert result is True
        download_manager.client.download_file.assert_called_once_with(img_url, save_path)


def test_download_single_image_failed(download_manager: GalleryDownloadManager):
    """Test failed download of a single image."""
    # Arrange
    img_url = "http://example.com/image.jpg"
    save_path = "/tmp/image.jpg"
    download_manager.client.download_file.return_value = False

    with patch('os.path.exists', return_value=True):
        # Act
        result = download_manager.download_single_image(img_url, save_path)

        # Assert
        assert result is False
        download_manager.client.download_file.assert_called_once_with(img_url, save_path)


def test_download_single_image_creates_directory(download_manager: GalleryDownloadManager):
    """Test that the save directory is created if it doesn't exist."""
    # Arrange
    img_url = "http://example.com/image.jpg"
    save_path = "/tmp/new_dir/image.jpg"
    download_manager.client.download_file.return_value = True

    with (
        patch('os.path.exists', side_effect=[False, True]) as mock_exists,
        patch('os.makedirs') as mock_makedirs,
    ):
        # Act
        download_manager.download_single_image(img_url, save_path)

        # Assert
        mock_makedirs.assert_called_once_with(os.path.dirname(save_path), exist_ok=True)


def test_download_images_batch_empty_list(download_manager: GalleryDownloadManager):
    """Test batch download with an empty list."""
    # Arrange
    dn_image_list = []

    # Act
    result = download_manager.download_images_batch(dn_image_list)

    # Assert
    assert result == 0


def test_download_images_batch_success(download_manager: GalleryDownloadManager):
    """Test successful batch download."""
    # Arrange
    dn_image_list = ["http://example.com/1.jpg", "http://example.com/2.jpg"]
    download_manager.client.download_file.return_value = True

    with (
        patch('os.path.isfile', return_value=False),
        patch(
            'scripts.civitai_manager_libs.gallery.download_manager.settings.get_setting',
            return_value=2,
        ),
    ):
        # Act
        result = download_manager.download_images_batch(dn_image_list)

        # Assert
        assert result == 2
        assert download_manager.client.download_file.call_count == 2


def test_download_images_simple_already_exists(download_manager: GalleryDownloadManager):
    """Test simple download where images already exist."""
    # Arrange
    dn_image_list = ["http://example.com/1.jpg"]

    with patch('os.path.isfile', return_value=True):
        # Act
        result = download_manager.download_images_simple(dn_image_list)

        # Assert
        assert result == 0
        download_manager.client.download_file.assert_not_called()


def test_retry_failed_downloads_empty(download_manager: GalleryDownloadManager):
    """Test retrying with no failed downloads."""
    # Act
    result = download_manager.retry_failed_downloads()

    # Assert
    assert result == 0


def test_retry_failed_downloads_success(download_manager: GalleryDownloadManager):
    """Test successful retry of failed downloads."""
    # Arrange
    failed = [("http://example.com/1.jpg", "/tmp/1.jpg")]
    download_manager.failed_downloads = failed.copy()
    download_manager.client.download_file.return_value = True

    with patch('os.path.exists', return_value=True):
        # Act
        result = download_manager.retry_failed_downloads()

        # Assert
        assert result == 1
        assert len(download_manager.failed_downloads) == 0


def test_retry_failed_downloads_still_fails(download_manager: GalleryDownloadManager):
    """Test when retried downloads still fail."""
    # Arrange
    failed = [("http://example.com/1.jpg", "/tmp/1.jpg")]
    download_manager.failed_downloads = failed.copy()
    download_manager.client.download_file.return_value = False

    with patch('os.path.exists', return_value=True):
        # Act
        result = download_manager.retry_failed_downloads()

        # Assert
        assert result == 0
        assert len(download_manager.failed_downloads) == 1


def test_get_download_statistics(download_manager: GalleryDownloadManager):
    """Test getting download statistics."""
    # Arrange
    download_manager.failed_downloads = [("http://example.com/1.jpg", "/tmp/1.jpg")]
    download_manager.active_downloads = {"task1": "active"}

    # Act
    stats = download_manager.get_download_statistics()

    # Assert
    assert stats['failed_downloads'] == 1
    assert stats['active_downloads'] == 1
    assert stats['failed_urls'] == ["http://example.com/1.jpg"]


def test_cleanup_incomplete_downloads_no_folder(download_manager: GalleryDownloadManager):
    """Test cleanup when gallery folder doesn't exist."""
    # Arrange
    with patch('os.path.exists', return_value=False):
        # Act
        result = download_manager.cleanup_incomplete_downloads()

        # Assert
        assert result == 0


def test_cleanup_incomplete_downloads(download_manager: GalleryDownloadManager):
    """Test cleanup of incomplete downloads."""
    # Arrange
    gallery_folder = "/tmp/gallery"
    settings.shortcut_gallery_folder = gallery_folder
    files = ["complete.jpg", "incomplete.jpg", "empty.jpg"]
    file_paths = [os.path.join(gallery_folder, f) for f in files]

    with (
        patch('os.path.exists', return_value=True),
        patch('os.listdir', return_value=files),
        patch('os.path.isfile', return_value=True),
        patch('os.path.getsize', side_effect=[1024, 50, 0]),
        patch('os.remove') as mock_remove,
    ):

        # Act
        result = download_manager.cleanup_incomplete_downloads()

        # Assert
        assert result == 2
        assert mock_remove.call_count == 2
        mock_remove.assert_any_call(file_paths[1])
        mock_remove.assert_any_call(file_paths[2])


def test_download_user_gallery_success(download_manager: GalleryDownloadManager):
    '''Test successful download of a user gallery.'''
    # Arrange
    model_id = "123"
    image_urls = ["http://example.com/gallery.jpg"]
    model_info = {'name': 'TestModel'}

    with (
        patch(
            'scripts.civitai_manager_libs.ishortcut_core.model_processor.ModelProcessor'
        ) as mock_model_processor,
        patch(
            'scripts.civitai_manager_libs.util.make_download_image_folder',
            return_value="/tmp/TestModel",
        ) as mock_make_folder,
        patch('os.path.exists', return_value=True),
        patch('shutil.copyfile'),
        patch(
            'scripts.civitai_manager_libs.gallery.download_manager.ParallelImageDownloader'
        ) as mock_downloader,
    ):

        mock_model_processor.return_value.get_model_info.return_value = model_info
        mock_downloader.return_value.download_images.return_value = 1

        # Act
        result = download_manager.download_user_gallery(model_id, image_urls)

        # Assert
        assert result == "/tmp/TestModel"
        mock_make_folder.assert_called_once_with('TestModel')


def test_download_user_gallery_no_model_id(download_manager: GalleryDownloadManager):
    '''Test download_user_gallery with no model_id.'''
    assert download_manager.download_user_gallery(None, []) is None


def test_download_user_gallery_no_model_info(download_manager: GalleryDownloadManager):
    '''Test download_user_gallery with no model_info.'''
    with patch(
        'scripts.civitai_manager_libs.ishortcut_core.model_processor.ModelProcessor'
    ) as mock_model_processor:
        mock_model_processor.return_value.get_model_info.return_value = None
        assert download_manager.download_user_gallery("123", []) is None


def test_load_gallery_images_success(download_manager: GalleryDownloadManager):
    '''Test successful loading of gallery images with parallel download.'''
    # Arrange
    images_url = ["http://example.com/image1.jpg"]
    progress_mock = MagicMock()
    progress_mock.tqdm.return_value = MagicMock()  # Mock tqdm object

    with patch.object(
        download_manager, 'download_images_parallel', return_value=1
    ) as mock_parallel_download:
        # Act
        dn_list, img_list, time = download_manager.load_gallery_images(images_url, progress_mock)

        # Assert
        assert dn_list is not None
        assert img_list is not None
        assert time is not None
        mock_parallel_download.assert_called_once()


def test_load_gallery_images_empty(download_manager: GalleryDownloadManager):
    '''Test load_gallery_images with an empty list.'''
    dn_list, img_list, visible = download_manager.load_gallery_images([], MagicMock())
    assert dn_list is None
    assert img_list is None
    assert visible == {'visible': False, '__type__': 'update'}


def test_preload_next_page_disabled(download_manager: GalleryDownloadManager):
    '''Test that preloading does not run when disabled in settings.'''
    # Arrange
    with patch(
        'scripts.civitai_manager_libs.gallery.download_manager.settings.usergallery_preloading',
        False,
    ):
        # Act
        download_manager.preload_next_page("some_url", {})

        # Assert
        # No calls to civitai or other functions should be made


def test_preload_next_page_success(download_manager: GalleryDownloadManager):
    '''Test successful preloading of the next page.'''
    # Arrange
    with (
        patch(
            'scripts.civitai_manager_libs.gallery.download_manager.settings.usergallery_preloading',
            True,
        ),
        patch('scripts.civitai_manager_libs.civitai.request_models') as mock_request,
        patch('threading.Thread') as mock_thread,
    ):

        mock_request.return_value = {'items': [{'url': 'http://example.com/preload.jpg'}]}

        # Act
        download_manager.preload_next_page(
            "some_url", {'totalPageUrls': ["url1", "url2"], 'nextPage': 'url2'}
        )

        # Assert
        mock_request.assert_called_once()
        mock_thread.assert_called_once()


def test_download_images_parallel_success(download_manager: GalleryDownloadManager):
    '''Test successful parallel download.'''
    # Arrange
    dn_image_list = ["http://example.com/1.jpg", "http://example.com/2.jpg"]

    with patch(
        'scripts.civitai_manager_libs.gallery.download_manager.ParallelImageDownloader'
    ) as mock_downloader:
        mock_downloader.return_value.download_images.return_value = 2

        # Act
        result = download_manager.download_images_parallel(dn_image_list)

        # Assert
        assert result == 2
        mock_downloader.return_value.download_images.assert_called_once()
