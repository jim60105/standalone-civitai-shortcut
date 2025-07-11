"""Additional focused tests to reach 85%+ coverage for gallery module."""

import os
import tempfile
from unittest.mock import Mock, MagicMock, patch, mock_open
import pytest
import gradio as gr

from scripts.civitai_manager_libs.gallery import (
    GalleryDataProcessor,
    GalleryDownloadManager,
    GalleryEventHandlers,
    GalleryUtilities,
)


class TestGalleryDataProcessorEdgeCases:
    """Test edge cases and error conditions in data processor."""

    def setup_method(self):
        self.data_processor = GalleryDataProcessor()

    @patch('scripts.civitai_manager_libs.gallery.data_processor.civitai.request_models')
    def test_get_pagination_info_detailed(self, mock_request):
        """Test detailed pagination information."""
        mock_request.return_value = {'items': [{'id': i} for i in range(1, 21)]}  # 20 items

        result = self.data_processor.get_pagination_info('model123', 'version456', True)
        assert isinstance(result, dict)
        assert 'totalPages' in result
        assert 'totalPageUrls' in result

    @patch('scripts.civitai_manager_libs.gallery.data_processor.civitai.request_models')
    def test_get_pagination_info_empty(self, mock_request):
        """Test pagination with no items."""
        mock_request.return_value = {'items': []}

        result = self.data_processor.get_pagination_info('model123')
        assert result['totalPages'] == 0

    def test_format_metadata_comprehensive(self):
        """Test comprehensive metadata formatting."""
        meta = {
            'prompt': 'beautiful sunset',
            'negativePrompt': 'ugly, blurry',
            'steps': '30',
            'sampler': 'DPM++ 2M SDE',
            'Schedule': 'Karras',
            'cfgScale': '7.5',
            'seed': '987654321',
            'Size': '512x768',
            'Model hash': 'abcd1234',
            'Model': 'test_model_v1',
            'Denoising strength': '0.7',
            'Clip skip': '2',
            'ADetailer model': 'face_yolov8n.pt',
            'ADetailer confidence': '0.3',
            'Hires upscale': '2',
            'Hires upscaler': '4x-UltraSharp',
            'Version': 'f2.0.1v1.10.1',
        }

        result = self.data_processor.format_metadata_to_auto1111(meta)
        assert 'beautiful sunset' in result
        assert 'Negative prompt: ugly, blurry' in result
        assert 'Steps: 30' in result
        assert 'Sampler: DPM++ 2M SDE' in result
        assert 'CFG scale: 7.5' in result

    @patch(
        'scripts.civitai_manager_libs.gallery.data_processor.GalleryDataProcessor.get_image_page_data'
    )
    def test_load_page_data_with_paging(self, mock_get_page):
        """Test loading page data with paging information."""
        mock_get_page.return_value = [{'id': 1, 'url': 'test1.jpg'}, {'id': 2, 'url': 'test2.jpg'}]

        paging_info = {'totalPageUrls': ['url1', 'url2', 'url3'], 'currentPageUrlIndex': 1}

        result = self.data_processor.load_page_data('test_url', paging_info)
        assert isinstance(result, tuple)
        assert len(result) == 4

    def test_load_page_data_no_paging(self):
        """Test loading page data without paging information."""
        result = self.data_processor.load_page_data('test_url', None)
        assert isinstance(result, tuple)
        assert len(result) == 4

    @patch('scripts.civitai_manager_libs.gallery.data_processor.settings')
    def test_get_user_gallery_nsfw_filtering(self, mock_settings):
        """Test user gallery with NSFW filtering."""
        mock_settings.nsfw_filter_enable = True
        mock_settings.NSFW_LEVELS = ['None', 'Soft', 'Mature', 'X']
        mock_settings.nsfw_level = 'Soft'

        with patch.object(self.data_processor, 'get_image_page_data') as mock_get_page:
            mock_get_page.return_value = [
                {'id': 1, 'url': 'https://example.com/test1.jpg', 'nsfwLevel': 'None'},
                {
                    'id': 2,
                    'url': 'https://example.com/test2.jpg',
                    'nsfwLevel': 'X',  # Should be filtered out
                },
            ]

            with patch(
                'scripts.civitai_manager_libs.settings.get_image_url_to_gallery_file'
            ) as mock_get_file:
                mock_get_file.return_value = '/tmp/test.jpg'
                with patch('os.path.exists', return_value=False):
                    images_url, images_list = self.data_processor.get_user_gallery(
                        'model123', 'test_url', False
                    )

                    # Only the 'None' level image should be included
                    assert len(images_list) == 1
                    assert 1 in images_list


class TestGalleryDownloadManagerEdgeCases:
    """Test edge cases in download manager."""

    def setup_method(self):
        self.download_manager = GalleryDownloadManager()

    @patch('scripts.civitai_manager_libs.gallery.download_manager.get_http_client')
    @patch('os.makedirs')
    def test_download_single_image_create_dirs(self, mock_makedirs, mock_get_client):
        """Test single image download with directory creation."""
        mock_client = MagicMock()
        mock_client.download_file.return_value = True
        mock_get_client.return_value = mock_client

        with tempfile.NamedTemporaryFile() as tmp:
            result = self.download_manager.download_single_image(
                'http://example.com/test.jpg', os.path.join('/tmp/subdir', 'test.jpg')
            )
            # Should attempt to create directories
            mock_makedirs.assert_called()

    @patch('scripts.civitai_manager_libs.gallery.download_manager.get_http_client')
    def test_download_single_image_exception_handling(self, mock_get_client):
        """Test exception handling in single image download."""
        mock_client = MagicMock()
        mock_client.download_file.side_effect = Exception("Network error")
        mock_get_client.return_value = mock_client

        with tempfile.NamedTemporaryFile() as tmp:
            result = self.download_manager.download_single_image(
                'http://example.com/test.jpg', tmp.name
            )
            assert result is False

    @patch('scripts.civitai_manager_libs.gallery.download_manager.settings')
    def test_download_images_parallel_callback(self, mock_settings):
        """Test parallel downloads with progress callback."""
        mock_settings.get_image_url_to_gallery_file.return_value = '/tmp/test.jpg'

        callback_calls = []

        def progress_callback(done, total, msg):
            callback_calls.append((done, total, msg))

        with patch.object(self.download_manager, 'download_single_image', return_value=True):
            self.download_manager.download_images_parallel(['url1', 'url2'], progress_callback)

            # Should have made progress callback calls
            assert len(callback_calls) > 0

    @patch('scripts.civitai_manager_libs.gallery.download_manager.settings')
    def test_download_images_batch_multiple_batches(self, mock_settings):
        """Test batch downloads with multiple batches."""
        mock_settings.get_image_url_to_gallery_file.return_value = '/tmp/test.jpg'

        with patch.object(self.download_manager, 'download_single_image', return_value=True):
            # Test with 5 URLs and batch size 2 (should create 3 batches)
            urls = [f'url{i}' for i in range(5)]
            result = self.download_manager.download_images_batch(urls, batch_size=2)
            assert isinstance(result, int)

    @patch('scripts.civitai_manager_libs.gallery.download_manager.util')
    @patch('scripts.civitai_manager_libs.gallery.download_manager.settings')
    def test_download_user_gallery_with_model_processor(self, mock_settings, mock_util):
        """Test user gallery download with model processor."""
        mock_util.make_download_image_folder.return_value = '/tmp/test_folder'
        mock_settings.get_image_url_to_gallery_file.return_value = '/tmp/test.jpg'

        with patch(
            'scripts.civitai_manager_libs.gallery.download_manager.ModelProcessor'
        ) as mock_mp:
            mock_mp.return_value.get_model_info.return_value = {'name': 'test_model'}

            with patch.object(self.download_manager, 'download_single_image', return_value=True):
                result = self.download_manager.download_user_gallery('model123', ['url1', 'url2'])
                # Should attempt to get model info
                mock_mp.assert_called_once()

    @patch('scripts.civitai_manager_libs.gallery.download_manager.settings')
    def test_load_gallery_images_with_tqdm(self, mock_settings):
        """Test gallery loading with tqdm progress."""
        mock_settings.get_image_url_to_gallery_file.return_value = '/tmp/test.jpg'
        mock_settings.shortcut_gallery_folder = '/tmp/gallery'
        mock_settings.get_no_card_preview_image.return_value = '/tmp/no_preview.jpg'

        # Mock tqdm progress object
        mock_progress = MagicMock()
        mock_progress.tqdm = lambda iterable, desc=None: iterable

        with patch.object(self.download_manager, 'download_single_image', return_value=False):
            result = self.download_manager.load_gallery_images(['url1', 'url2'], mock_progress)
            assert isinstance(result, tuple)
            assert len(result) == 3

    def test_cleanup_incomplete_downloads_empty(self):
        """Test cleanup with no downloads to clean."""
        result = self.download_manager.cleanup_incomplete_downloads()
        assert result == 0

    def test_retry_failed_downloads_no_failures(self):
        """Test retry with no failed downloads."""
        result = self.download_manager.retry_failed_downloads()
        assert result == 0


class TestGalleryEventHandlersEdgeCases:
    """Test edge cases in event handlers."""

    def setup_method(self):
        self.data_processor = GalleryDataProcessor()
        self.download_manager = GalleryDownloadManager()
        self.utilities = GalleryUtilities()
        self.event_handlers = GalleryEventHandlers(
            self.data_processor, self.download_manager, self.utilities
        )

    def test_handle_selected_model_id_change(self):
        """Test model ID change handler."""
        result = self.event_handlers.handle_selected_model_id_change('model123')
        assert isinstance(result, (str, type(None)))

    def test_handle_versions_list_select_with_model_id(self):
        """Test version list selection with model ID."""
        evt = MagicMock()
        evt.index = 0
        evt.value = ['version456']

        result = self.event_handlers.handle_versions_list_select(evt, 'model123')
        assert isinstance(result, str)

    def test_handle_versions_list_select_no_model_id(self):
        """Test version list selection without model ID."""
        evt = MagicMock()
        evt.index = 0
        evt.value = ['version456']

        result = self.event_handlers.handle_versions_list_select(evt)
        assert isinstance(result, str)

    def test_handle_usergal_page_url_change(self):
        """Test user gallery page URL change."""
        paging_info = {'totalPageUrls': ['url1', 'url2']}

        result = self.event_handlers.handle_usergal_page_url_change('new_url', paging_info)
        assert isinstance(result, (str, type(None)))

    @patch('scripts.civitai_manager_libs.gallery.event_handlers.gr.update')
    def test_handle_refresh_gallery_change(self, mock_update):
        """Test gallery refresh handler."""
        mock_update.return_value = MagicMock()

        result = self.event_handlers.handle_refresh_gallery_change(['url1', 'url2'])
        assert result is not None

    def test_handle_pre_loading_change(self):
        """Test pre-loading change handler."""
        paging_info = {'totalPageUrls': ['url1', 'url2']}

        result = self.event_handlers.handle_pre_loading_change('test_url', paging_info)
        # Should not raise an exception
        assert True

    def test_handle_civitai_hidden_change(self):
        """Test civitai hidden change handler."""
        result = self.event_handlers.handle_civitai_hidden_change('hidden_value', 0)
        # Should not raise an exception
        assert True

    @patch('scripts.civitai_manager_libs.gallery.event_handlers.os.path.exists')
    @patch('scripts.civitai_manager_libs.gallery.event_handlers.Image.open')
    def test_handle_gallery_select_image_error(self, mock_open, mock_exists):
        """Test gallery selection with image reading error."""
        mock_exists.return_value = True
        mock_open.side_effect = Exception("Cannot read image")

        evt = MagicMock()
        evt.index = 0

        result = self.event_handlers.handle_gallery_select(evt, ['/tmp/test.jpg'])
        assert isinstance(result, tuple)
        # Should return error message in PNG info
        assert 'Error extracting generation parameters' in result[3]

    def test_extract_civitai_metadata_no_match(self):
        """Test Civitai metadata extraction with no UUID match."""
        # Store some metadata first
        mock_image_data = [
            {
                'url': 'https://example.com/no-uuid-in-this-url.jpg',
                'meta': {'prompt': 'test'},
                'id': 123,
            }
        ]
        self.data_processor.store_page_metadata(mock_image_data)

        result = self.event_handlers._extract_civitai_metadata('/tmp/some_file.jpg')
        assert 'Image metadata not found' in result


class TestGalleryUtilitiesEdgeCases:
    """Test edge cases in utilities."""

    def setup_method(self):
        self.utilities = GalleryUtilities()

    def test_validate_model_id_valid(self):
        """Test model ID validation with valid ID."""
        assert self.utilities.validate_model_id('12345') is True

    def test_validate_model_id_invalid(self):
        """Test model ID validation with invalid ID."""
        assert self.utilities.validate_model_id('abc123') is False
        assert self.utilities.validate_model_id('') is False
        assert self.utilities.validate_model_id(None) is False

    def test_build_default_page_url_no_version(self):
        """Test URL building without version ID."""
        url = self.utilities.build_default_page_url('123', None, False, 50)
        assert 'modelId=123' in url
        assert 'modelVersionId' not in url
        assert 'limit=50' in url

    def test_build_default_page_url_limit_capping(self):
        """Test URL building with limit over maximum."""
        url = self.utilities.build_default_page_url('123', None, False, 300)
        # Should be capped at 200
        assert 'limit=200' in url

    @patch('scripts.civitai_manager_libs.gallery.gallery_utilities.settings')
    def test_build_default_page_url_default_limit(self, mock_settings):
        """Test URL building with default limit calculation."""
        mock_settings.usergallery_images_rows_per_page = 4
        mock_settings.usergallery_images_column = 5

        url = self.utilities.build_default_page_url('123', None, False, 0)
        # Should use default: 4 * 5 = 20
        assert 'limit=20' in url

    def test_extract_url_cursor_with_letters(self):
        """Test cursor extraction with non-numeric cursor."""
        url = 'https://civitai.com/api/v1/images?cursor=abc123'
        cursor = self.utilities.extract_url_cursor(url)
        # Should return 0 when cursor is not numeric
        assert cursor == 0

    @patch('scripts.civitai_manager_libs.gallery.gallery_utilities.util.update_url')
    def test_fix_page_url_cursor_with_update(self, mock_update_url):
        """Test page URL cursor fixing with URL update."""
        mock_update_url.return_value = 'updated_url'

        url = 'https://civitai.com/api/v1/images?cursor=123'
        result = self.utilities.fix_page_url_cursor(url, use=True)

        # Should call util.update_url with cursor + 1
        mock_update_url.assert_called_with(url, "cursor", 124)
        assert result == 'updated_url'

    def test_fix_page_url_cursor_zero_cursor(self):
        """Test page URL cursor fixing with zero cursor."""
        url = 'https://civitai.com/api/v1/images'
        result = self.utilities.fix_page_url_cursor(url, use=True)
        # Should return original URL when cursor is 0
        assert result == url


class TestGalleryIntegrationScenarios:
    """Test complex integration scenarios."""

    @patch(
        'scripts.civitai_manager_libs.gallery.data_processor.GalleryDataProcessor.get_image_page_data'
    )
    @patch('scripts.civitai_manager_libs.gallery.download_manager.get_http_client')
    def test_complete_gallery_workflow(self, mock_get_client, mock_get_page):
        """Test complete gallery workflow from data to download."""
        # Mock API data
        mock_get_page.return_value = [
            {
                'id': 1,
                'url': 'https://example.com/image-aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee/test.jpg',
                'nsfwLevel': 'None',
                'meta': {'prompt': 'beautiful landscape', 'steps': '20', 'sampler': 'DPM++ 2M'},
            }
        ]

        # Mock HTTP client
        mock_client = MagicMock()
        mock_client.download_file.return_value = True
        mock_get_client.return_value = mock_client

        # Create components
        data_processor = GalleryDataProcessor()
        download_manager = GalleryDownloadManager()

        # Test data processing
        with patch(
            'scripts.civitai_manager_libs.settings.get_image_url_to_gallery_file'
        ) as mock_get_file:
            mock_get_file.return_value = '/tmp/test.jpg'
            with patch('os.path.exists', return_value=False):
                images_url, images_list = data_processor.get_user_gallery(
                    'model123', 'test_url', False
                )

                # Verify data was processed and metadata stored
                assert len(images_list) == 1
                stored_meta = data_processor.get_stored_metadata(
                    'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
                )
                assert stored_meta is not None

                # Test metadata formatting
                formatted = data_processor.format_metadata_to_auto1111(stored_meta['meta'])
                assert 'beautiful landscape' in formatted
                assert 'Steps: 20' in formatted

                # Test downloading the images
                with patch(
                    'scripts.civitai_manager_libs.gallery.download_manager.settings'
                ) as mock_settings:
                    mock_settings.get_image_url_to_gallery_file.return_value = '/tmp/downloaded.jpg'
                    download_count = download_manager.download_images_simple(images_url)
                    assert isinstance(download_count, int)
