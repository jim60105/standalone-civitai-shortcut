"""Test for refactored gallery event handling."""

from scripts.civitai_manager_libs.gallery.event_normalizer import EventNormalizer
from scripts.civitai_manager_libs.gallery import on_gallery_select


class TestGalleryEventRefactor:
    """Test cases for refactored gallery event handling."""

    def test_event_normalizer_gradio_v3_scenario(self):
        """Test EventNormalizer with Gradio v3 scenario."""
        images_list = ['image1.jpg', 'image2.jpg']
        evt, civitai_images = EventNormalizer.normalize_gallery_event(images_list, None)

        assert hasattr(evt, 'index')
        assert evt.index == 0
        assert civitai_images == images_list

    def test_refactored_on_gallery_select_basic(self):
        """Test refactored on_gallery_select basic functionality."""
        images_list = ['test_image.jpg']

        # Test Gradio v3 scenario
        result = on_gallery_select(images_list, None)
        assert isinstance(result, tuple)
        assert len(result) == 4
