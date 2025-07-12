from scripts.civitai_manager_libs.gallery import on_download_images_click
from scripts.civitai_manager_libs import settings

config_manager = settings.config_manager


class TestGalleryOpenFolderVisibility:
    def test_on_download_images_click_hidden_in_container(self, monkeypatch):
        """When in container environment and images are downloaded, button is hidden."""
        monkeypatch.setattr(
            'scripts.civitai_manager_libs.gallery.event_handlers.util.should_show_open_folder_buttons', 
            lambda: False
        )
        # Mock extract_model_info to return valid model info
        monkeypatch.setattr(
            'scripts.civitai_manager_libs.gallery.gallery_utilities.GalleryUtilities.extract_model_info',
            lambda self, url: ('model123', 'version456')
        )
        # Mock download_user_gallery at the instance level
        monkeypatch.setattr(
            'scripts.civitai_manager_libs.gallery.download_manager.GalleryDownloadManager.download_user_gallery',
            lambda self, modelid, images_url: '/tmp/model_folder'
        )
        update = on_download_images_click('dummy_url', 'dummy_images_url')
        # open folder button should be hidden in container environment
        assert isinstance(update, dict)
        assert update.get('visible') is False

    def test_on_download_images_click_visible_on_host(self, monkeypatch):
        """When on host environment and images are downloaded, button is visible."""
        monkeypatch.setattr(
            'scripts.civitai_manager_libs.gallery.event_handlers.util.should_show_open_folder_buttons',
            lambda: True
        )
        # Mock extract_model_info to return valid model info
        monkeypatch.setattr(
            'scripts.civitai_manager_libs.gallery.gallery_utilities.GalleryUtilities.extract_model_info',
            lambda self, url: ('model123', 'version456')
        )
        # Mock download_user_gallery at the instance level
        monkeypatch.setattr(
            'scripts.civitai_manager_libs.gallery.download_manager.GalleryDownloadManager.download_user_gallery',
            lambda self, modelid, images_url: '/tmp/model_folder'
        )
        update = on_download_images_click('dummy_url', 'dummy_images_url')
        # open folder button should be visible on host environment
        assert isinstance(update, dict)
        assert update.get('visible') is True
