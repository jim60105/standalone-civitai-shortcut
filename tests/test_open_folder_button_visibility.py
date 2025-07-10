from scripts.civitai_manager_libs.civitai_gallery_action import on_download_images_click
from scripts.civitai_manager_libs import setting

config_manager = setting.config_manager


class TestGalleryOpenFolderVisibility:
    def test_on_download_images_click_hidden_in_container(self, monkeypatch):
        """When in container environment and images are downloaded, button is hidden."""
        monkeypatch.setattr(
            'scripts.civitai_manager_libs.util.is_linux_container', lambda: {'is_container': True}
        )
        # Simulate successful download by returning a non-empty path
        monkeypatch.setattr(
            'scripts.civitai_manager_libs.civitai_gallery_action.download_user_gallery_images',
            lambda modelid, images_url: '/tmp',
        )
        update = on_download_images_click('dummy_url', 'dummy_images_url')
        # open folder button should be hidden in container environment
        assert isinstance(update, dict)
        assert update.get('visible') is False

    def test_on_download_images_click_visible_on_host(self, monkeypatch):
        """When on host environment and images are downloaded, button is visible."""
        monkeypatch.setattr(
            'scripts.civitai_manager_libs.util.is_linux_container', lambda: {'is_container': False}
        )
        monkeypatch.setattr(
            'scripts.civitai_manager_libs.civitai_gallery_action.download_user_gallery_images',
            lambda modelid, images_url: '/tmp',
        )
        update = on_download_images_click('dummy_url', 'dummy_images_url')
        # open folder button should be visible on host environment
        assert isinstance(update, dict)
        assert update.get('visible') is True
