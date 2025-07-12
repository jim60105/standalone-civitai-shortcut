

import pytest
from unittest.mock import MagicMock, patch
import gradio as gr
from PIL import Image
from scripts.civitai_manager_libs.gallery.event_handlers import GalleryEventHandlers

@pytest.fixture
def event_handlers():
    """Fixture for GalleryEventHandlers."""
    data_processor = MagicMock()
    download_manager = MagicMock()
    utilities = MagicMock()
    return GalleryEventHandlers(data_processor, download_manager, utilities)

def test_handle_recipe_integration(event_handlers: GalleryEventHandlers):
    """Test recipe integration handler."""
    # Arrange
    model_id = "123"
    img_file_info = "some_info"
    img_index = 0
    civitai_images = ["image1.jpg"]

    with patch('scripts.civitai_manager_libs.gallery.event_handlers.settings.set_imagefn_and_shortcutid_for_recipe_image') as mock_set_image:
        mock_set_image.return_value = "recipe_image.jpg"

        # Act
        result = event_handlers.handle_recipe_integration(model_id, img_file_info, img_index, civitai_images)

        # Assert
        assert result == "recipe_image.jpg\nsome_info"

def test_handle_open_image_folder(event_handlers: GalleryEventHandlers):
    """Test open image folder handler."""
    # Arrange
    model_id = "123"
    model_info = {'name': 'TestModel'}
    image_folder = "/path/to/folder"

    with patch('scripts.civitai_manager_libs.ishortcut_core.model_processor.ModelProcessor') as mock_model_processor, \
         patch('scripts.civitai_manager_libs.gallery.event_handlers.util.get_download_image_folder', return_value=image_folder) as mock_get_folder, \
         patch('scripts.civitai_manager_libs.gallery.event_handlers.util.open_folder') as mock_open_folder:
        
        mock_model_processor.return_value.get_model_info.return_value = model_info

        # Act
        event_handlers.handle_open_image_folder(model_id)

        # Assert
        mock_get_folder.assert_called_once_with('TestModel')
        mock_open_folder.assert_called_once_with(image_folder)

def test_handle_download_click(event_handlers: GalleryEventHandlers):
    """Test download button click handler."""
    # Arrange
    page_url = "http://civitai.com/models/123"
    images_url = ["http://example.com/image.jpg"]
    event_handlers.utilities.extract_model_info.return_value = ("123", "456")
    event_handlers.download_manager.download_user_gallery.return_value = "/path/to/folder"

    with patch('scripts.civitai_manager_libs.gallery.event_handlers.util.should_show_open_folder_buttons', return_value=True):
        # Act
        result = event_handlers.handle_download_click(page_url, images_url)

        # Assert
        assert result == gr.update(visible=True)

def test_handle_page_slider_release(event_handlers: GalleryEventHandlers):
    """Test page slider release handler."""
    # Arrange
    paging_info = {"totalPageUrls": ["url1", "url2"]}

    # Act
    result = event_handlers.handle_page_slider_release("some_url", 2, paging_info)

    # Assert
    assert result == "url2"

def test_handle_first_btn_click(event_handlers: GalleryEventHandlers):
    """Test first page button click handler."""
    # Arrange
    paging_info = {"totalPageUrls": ["url1", "url2"]}

    # Act
    result = event_handlers.handle_first_btn_click("some_url", paging_info)

    # Assert
    assert result == "url1"

def test_handle_end_btn_click(event_handlers: GalleryEventHandlers):
    """Test end page button click handler."""
    # Arrange
    paging_info = {"totalPageUrls": ["url1", "url2"]}

    # Act
    result = event_handlers.handle_end_btn_click("some_url", paging_info)

    # Assert
    assert result == "url2"

def test_handle_next_btn_click(event_handlers: GalleryEventHandlers):
    """Test next page button click handler."""
    # Arrange
    paging_info = {"totalPageUrls": ["url1", "url2"]}
    event_handlers.data_processor.calculate_current_page.return_value = 1

    # Act
    result = event_handlers.handle_next_btn_click("url1", paging_info)

    # Assert
    assert result == "url2"

def test_handle_prev_btn_click(event_handlers: GalleryEventHandlers):
    """Test previous page button click handler."""
    # Arrange
    paging_info = {"totalPageUrls": ["url1", "url2"]}
    event_handlers.data_processor.calculate_current_page.return_value = 2

    # Act
    result = event_handlers.handle_prev_btn_click("url2", paging_info)

    # Assert
    assert result == "url1"

def test_handle_gallery_select(event_handlers: GalleryEventHandlers):
    """Test gallery select handler."""
    # Arrange
    evt = MagicMock(spec=gr.SelectData)
    evt.index = 0
    civitai_images = ["http://example.com/image.jpg"]
    event_handlers.data_processor.get_all_stored_metadata.return_value = {}
    event_handlers.data_processor.get_stored_metadata.return_value = None

    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', MagicMock()):
        # Act
        index, path, update, info = event_handlers.handle_gallery_select(evt, civitai_images)

        # Assert
        assert index == 0
        assert path is not None
        assert update == gr.update(selected="Image_Information")

def test_handle_selected_model_id_change(event_handlers: GalleryEventHandlers):
    """Test selected model id change handler."""
    # Arrange
    model_id = "123"
    event_handlers.utilities.build_default_page_url.return_value = "some_url"
    event_handlers.data_processor.get_model_information.return_value = ("Test Model", ["v1"], "v1", {"totalPages": 1})

    with patch('scripts.civitai_manager_libs.gallery.event_handlers.util.get_download_image_folder', return_value="/path/to/folder"):
        # Act
        label, url, versions, slider, paging, visible = event_handlers.handle_selected_model_id_change(model_id)

        # Assert
        assert label == gr.update(label="# Test Model")
        assert url == "some_url"
        assert versions['value'] == "v1"

def test_handle_versions_list_select(event_handlers: GalleryEventHandlers):
    """Test versions list select handler."""
    # Arrange
    evt = MagicMock(spec=gr.SelectData)
    evt.index = 1
    model_id = "123"
    model_info = {'modelVersions': [{'id': '456'}]}
    event_handlers.utilities.build_default_page_url.return_value = "some_url"
    event_handlers.data_processor.get_model_information.return_value = ("Test Model", ["v1"], "v1", {"totalPages": 1})

    with patch('scripts.civitai_manager_libs.ishortcut_core.model_processor.ModelProcessor') as mock_model_processor:
        mock_model_processor.return_value.get_model_info.return_value = model_info
        # Act
        label, url, versions, slider, paging = event_handlers.handle_versions_list_select(evt, model_id)

        # Assert
        assert url == "some_url"

def test_handle_usergal_page_url_change(event_handlers: GalleryEventHandlers):
    """Test user gallery page url change handler."""
    # Arrange
    event_handlers.data_processor.load_page_data.return_value = ("a", "b", "c")

    # Act
    result = event_handlers.handle_usergal_page_url_change("some_url", {})

    # Assert
    assert result == ("a", "b", "c")

def test_handle_refresh_gallery_change(event_handlers: GalleryEventHandlers):
    """Test refresh gallery change handler."""
    # Arrange
    event_handlers.download_manager.load_gallery_images.return_value = ("a", "b", "c")

    # Act
    result = event_handlers.handle_refresh_gallery_change([])

    # Assert
    assert result == ("a", "b", "c")

def test_handle_pre_loading_change(event_handlers: GalleryEventHandlers):
    """Test pre-loading change handler."""
    # Act
    event_handlers.handle_pre_loading_change("some_url", {})

    # Assert
    event_handlers.download_manager.preload_next_page.assert_called_once_with("some_url", {})

def test_handle_civitai_hidden_change_standalone_filepath(event_handlers: GalleryEventHandlers):
    """Test civitai hidden change handler in standalone mode with a filepath."""
    # Arrange
    with patch('scripts.civitai_manager_libs.gallery.event_handlers.CompatibilityLayer.get_compatibility_layer') as mock_compat, \
         patch('os.path.isfile', return_value=True):
        mock_compat.return_value.is_standalone_mode.return_value = True
        mock_compat.return_value.metadata_processor.extract_png_info.return_value = ["info1"]
        # Act
        result = event_handlers.handle_civitai_hidden_change("path/to/image.png", 0)
        # Assert
        assert result == "info1"

def test_handle_civitai_hidden_change_standalone_pil(event_handlers: GalleryEventHandlers):
    """Test civitai hidden change handler in standalone mode with a PIL Image."""
    # Arrange
    with patch('scripts.civitai_manager_libs.gallery.event_handlers.CompatibilityLayer.get_compatibility_layer') as mock_compat, \
         patch('tempfile.mkstemp', return_value=(0, 'temp_path')), \
         patch('os.close'), \
         patch('os.remove'):
        mock_compat.return_value.is_standalone_mode.return_value = True
        mock_compat.return_value.metadata_processor.extract_png_info.return_value = ["info1"]
        image = Image.new('RGB', (100, 100), color = 'red')
        # Act
        result = event_handlers.handle_civitai_hidden_change(image, 0)
        # Assert
        assert result == "info1"

def test_handle_civitai_hidden_change_webui(event_handlers: GalleryEventHandlers):
    """Test civitai hidden change handler in webui mode."""
    # Arrange
    with patch('scripts.civitai_manager_libs.gallery.event_handlers.import_manager.get_webui_module') as mock_get_module:
        mock_get_module.return_value.run_pnginfo.return_value = ("info1", "info2", "info3")
        # Act
        result = event_handlers.handle_civitai_hidden_change(None, 0)
        # Assert
        assert result == "info1"

def test_extract_civitai_metadata(event_handlers: GalleryEventHandlers):
    """Test _extract_civitai_metadata."""
    # Arrange
    event_handlers.data_processor.get_stored_metadata.return_value = {'meta': {'prompt': 'test prompt'}}
    event_handlers.data_processor.format_metadata_to_auto1111.return_value = "formatted_prompt"
    # Act
    result = event_handlers._extract_civitai_metadata("some_path/12345678-1234-1234-1234-1234567890ab.png")
    # Assert
    assert result == "formatted_prompt"
