import pytest
from unittest.mock import Mock, patch

import scripts.civitai_manager_libs.setting as setting
from scripts.civitai_manager_libs.recipe_actions.recipe_gallery import RecipeGallery


@pytest.fixture(autouse=True)
def use_tmp_recipe_file(tmp_path, monkeypatch):
    """Redirect recipe storage to a temporary file for tests."""
    tmp_file = tmp_path / "recipes.json"
    tmp_folder = tmp_path / "sc_recipes"
    monkeypatch.setattr(setting, "shortcut_recipe", str(tmp_file))
    monkeypatch.setattr(setting, "shortcut_recipe_folder", str(tmp_folder))
    monkeypatch.setattr(setting, "prompt_shortcut_column", 4)
    monkeypatch.setattr(setting, "gallery_thumbnail_image_style", "contain")
    monkeypatch.setattr(setting, "preview_image_ext", ".jpg")
    yield


def test_recipe_gallery_init():
    """Test RecipeGallery initialization."""
    gallery = RecipeGallery()
    assert gallery._logger is not None


@patch('scripts.civitai_manager_libs.recipe_actions.recipe_gallery.gr')
def test_create_gallery_ui(mock_gr):
    """Test creating gallery UI component."""
    gallery = RecipeGallery()

    # Mock the gallery component
    mock_gallery_component = Mock()
    mock_gr.Gallery.return_value = mock_gallery_component

    with patch.object(gallery, 'load_recipe_images', return_value=['image1.jpg', 'image2.jpg']):
        result = gallery.create_gallery_ui("test_recipe")

        assert result == mock_gallery_component
        mock_gr.Gallery.assert_called_once_with(
            value=['image1.jpg', 'image2.jpg'],
            show_label=False,
            columns=4,
            height="auto",
            object_fit="contain",
            preview=False,
            allow_preview=False,
        )


def test_load_recipe_images():
    """Test loading recipe images."""
    gallery = RecipeGallery()

    # Test with recipe that has an image
    mock_recipe = {'image': 'test_image.jpg'}

    with (
        patch('scripts.civitai_manager_libs.recipe.get_recipe', return_value=mock_recipe),
        patch('os.path.join', return_value='/path/to/test_image.jpg'),
        patch('os.path.isfile', return_value=True),
    ):

        result = gallery.load_recipe_images("test_recipe")
        assert result == ['/path/to/test_image.jpg']

    # Test with recipe that has no image
    mock_recipe_no_image = {'name': 'test'}

    with patch('scripts.civitai_manager_libs.recipe.get_recipe', return_value=mock_recipe_no_image):
        result = gallery.load_recipe_images("test_recipe")
        assert result == []

    # Test with non-existent recipe
    with patch('scripts.civitai_manager_libs.recipe.get_recipe', return_value=None):
        result = gallery.load_recipe_images("nonexistent")
        assert result == []

    # Test with empty recipe_id
    result = gallery.load_recipe_images("")
    assert result == []

    # Test with recipe that has image but file doesn't exist
    mock_recipe_missing_file = {'image': 'missing_image.jpg'}

    with (
        patch(
            'scripts.civitai_manager_libs.recipe.get_recipe', return_value=mock_recipe_missing_file
        ),
        patch('os.path.join', return_value='/path/to/missing_image.jpg'),
        patch('os.path.isfile', return_value=False),
    ):

        result = gallery.load_recipe_images("test_recipe")
        assert result == []

    # Test with non-dict recipe data
    with patch('scripts.civitai_manager_libs.recipe.get_recipe', return_value="invalid"):
        result = gallery.load_recipe_images("test_recipe")
        assert result == []


def test_add_image_to_recipe():
    """Test adding image to recipe."""
    gallery = RecipeGallery()

    # Test successful addition
    with patch('scripts.civitai_manager_libs.recipe.update_recipe_image', return_value=True):
        result = gallery.add_image_to_recipe("test_recipe", "image.jpg")
        assert result is True

    # Test failed addition
    with patch('scripts.civitai_manager_libs.recipe.update_recipe_image', return_value=False):
        result = gallery.add_image_to_recipe("test_recipe", "image.jpg")
        assert result is False

    # Test with None return (treat as False)
    with patch('scripts.civitai_manager_libs.recipe.update_recipe_image', return_value=None):
        result = gallery.add_image_to_recipe("test_recipe", "image.jpg")
        assert result is False


def test_remove_image_from_recipe():
    """Test removing image from recipe."""
    gallery = RecipeGallery()

    # Test successful removal
    with patch('scripts.civitai_manager_libs.recipe.update_recipe_image', return_value=True):
        result = gallery.remove_image_from_recipe("test_recipe", "image_id")
        assert result is True

    # Test failed removal
    with patch('scripts.civitai_manager_libs.recipe.update_recipe_image', return_value=False):
        result = gallery.remove_image_from_recipe("test_recipe", "image_id")
        assert result is False

    # Test with None return (treat as False)
    with patch('scripts.civitai_manager_libs.recipe.update_recipe_image', return_value=None):
        result = gallery.remove_image_from_recipe("test_recipe", "image_id")
        assert result is False


@patch('scripts.civitai_manager_libs.recipe_actions.recipe_gallery.Image')
@patch('scripts.civitai_manager_libs.recipe_actions.recipe_gallery.os')
def test_generate_image_thumbnail(mock_os, mock_pil_image):
    """Test generating image thumbnail."""
    gallery = RecipeGallery()

    # Setup mocks
    mock_os.makedirs.return_value = None
    mock_os.path.basename.return_value = "test_image.jpg"
    mock_os.path.join.return_value = "/thumbnails/test_image.jpg"

    # Mock PIL Image
    mock_image = Mock()
    mock_pil_image.open.return_value.__enter__ = Mock(return_value=mock_image)
    mock_pil_image.open.return_value.__exit__ = Mock(return_value=None)
    mock_image.thumbnail = Mock()
    mock_image.save = Mock()

    # Test successful thumbnail generation
    result = gallery.generate_image_thumbnail("/path/to/test_image.jpg")
    assert result == "/thumbnails/test_image.jpg"
    mock_image.thumbnail.assert_called_once()
    mock_image.save.assert_called_once()


@patch('scripts.civitai_manager_libs.recipe_actions.recipe_gallery.Image')
def test_generate_image_thumbnail_error(mock_pil_image):
    """Test thumbnail generation with error."""
    gallery = RecipeGallery()

    # Mock PIL Image to raise exception
    mock_pil_image.open.side_effect = Exception("Cannot open image")

    with patch.object(gallery._logger, 'error') as mock_error:
        result = gallery.generate_image_thumbnail("/path/to/invalid_image.jpg")
        assert result == "/path/to/invalid_image.jpg"  # Should return original path
        mock_error.assert_called_once()


@patch('scripts.civitai_manager_libs.recipe_actions.recipe_gallery.CompatibilityLayer')
def test_get_image_metadata_with_compat_layer(mock_compat_layer):
    """Test getting image metadata using compatibility layer."""
    gallery = RecipeGallery()

    # Mock compatibility layer
    mock_compat = Mock()
    mock_metadata_processor = Mock()
    mock_metadata_processor.extract_png_info.return_value = ("info", {"param1": "value1"})
    mock_compat.metadata_processor = mock_metadata_processor
    mock_compat_layer.get_compatibility_layer.return_value = mock_compat

    result = gallery.get_image_metadata("/path/to/image.png")
    assert result == {"param1": "value1"}


@patch('scripts.civitai_manager_libs.recipe_actions.recipe_gallery.CompatibilityLayer')
@patch('scripts.civitai_manager_libs.recipe_actions.recipe_gallery.ImageMetadataProcessor')
def test_get_image_metadata_fallback(mock_processor_class, mock_compat_layer):
    """Test image metadata extraction fallback."""
    gallery = RecipeGallery()

    # Mock compatibility layer to return None
    mock_compat_layer.get_compatibility_layer.return_value = None

    # Mock fallback processor
    mock_processor = Mock()
    mock_processor.extract_png_info.return_value = {"fallback": "data"}
    mock_processor_class.return_value = mock_processor

    result = gallery.get_image_metadata("/path/to/image.png")
    assert result == {"fallback": "data"}
    mock_processor_class.assert_called_with(mode='standalone')


@patch('scripts.civitai_manager_libs.recipe_actions.recipe_gallery.CompatibilityLayer')
@patch('scripts.civitai_manager_libs.recipe_actions.recipe_gallery.ImageMetadataProcessor')
def test_get_image_metadata_error(mock_processor_class, mock_compat_layer):
    """Test image metadata extraction with error."""
    gallery = RecipeGallery()

    # Mock compatibility layer to return None
    mock_compat_layer.get_compatibility_layer.return_value = None

    # Mock processor to raise exception
    mock_processor_class.side_effect = Exception("Metadata error")

    with patch.object(gallery._logger, 'error') as mock_error:
        result = gallery.get_image_metadata("/path/to/image.png")
        assert result == {}
        mock_error.assert_called_once()


@patch('scripts.civitai_manager_libs.recipe_actions.recipe_gallery.CompatibilityLayer')
def test_get_image_metadata_compat_layer_exception(mock_compat_layer):
    """Test image metadata extraction when compatibility layer raises exception."""
    gallery = RecipeGallery()

    # Mock compatibility layer
    mock_compat = Mock()
    mock_metadata_processor = Mock()
    mock_metadata_processor.extract_png_info.side_effect = Exception("Compat error")
    mock_compat.metadata_processor = mock_metadata_processor
    mock_compat_layer.get_compatibility_layer.return_value = mock_compat

    with patch(
        'scripts.civitai_manager_libs.recipe_actions.recipe_gallery.ImageMetadataProcessor'
    ) as mock_fallback:
        mock_fallback_processor = Mock()
        mock_fallback_processor.extract_png_info.return_value = {"fallback": "used"}
        mock_fallback.return_value = mock_fallback_processor

        result = gallery.get_image_metadata("/path/to/image.png")
        assert result == {"fallback": "used"}


def test_get_image_metadata_compat_layer_returns_tuple():
    """Test metadata extraction when compat layer returns tuple."""
    gallery = RecipeGallery()

    with patch(
        'scripts.civitai_manager_libs.recipe_actions.recipe_gallery.CompatibilityLayer'
    ) as mock_compat_layer:
        mock_compat = Mock()
        mock_metadata_processor = Mock()
        # Return tuple with metadata in second position
        mock_metadata_processor.extract_png_info.return_value = ("info_string", {"meta": "data"})
        mock_compat.metadata_processor = mock_metadata_processor
        mock_compat_layer.get_compatibility_layer.return_value = mock_compat

        result = gallery.get_image_metadata("/path/to/image.png")
        assert result == {"meta": "data"}


def test_get_image_metadata_compat_layer_returns_dict():
    """Test metadata extraction when compat layer returns dict directly."""
    gallery = RecipeGallery()

    with patch(
        'scripts.civitai_manager_libs.recipe_actions.recipe_gallery.CompatibilityLayer'
    ) as mock_compat_layer:
        mock_compat = Mock()
        mock_metadata_processor = Mock()
        # Return dict directly
        mock_metadata_processor.extract_png_info.return_value = {"direct": "dict"}
        mock_compat.metadata_processor = mock_metadata_processor
        mock_compat_layer.get_compatibility_layer.return_value = mock_compat

        result = gallery.get_image_metadata("/path/to/image.png")
        assert result == {"direct": "dict"}


@patch('scripts.civitai_manager_libs.recipe_actions.recipe_gallery.gr')
def test_on_recipe_drop_image_upload(mock_gr):
    """Test recipe drop image upload handler."""
    gallery = RecipeGallery()

    # Test method exists and is callable
    assert hasattr(gallery, 'on_recipe_drop_image_upload')

    # Note: This method involves complex UI interactions and file handling
    # Full testing would require extensive mocking of the file upload process


def test_load_recipe_images_with_empty_image():
    """Test loading recipe images when image field is empty."""
    gallery = RecipeGallery()

    mock_recipe = {'image': ''}  # Empty image

    with patch('scripts.civitai_manager_libs.recipe.get_recipe', return_value=mock_recipe):
        result = gallery.load_recipe_images("test_recipe")
        assert result == []


def test_load_recipe_images_with_none_image():
    """Test loading recipe images when image field is None."""
    gallery = RecipeGallery()

    mock_recipe = {'image': None}  # None image

    with patch('scripts.civitai_manager_libs.recipe.get_recipe', return_value=mock_recipe):
        result = gallery.load_recipe_images("test_recipe")
        assert result == []


@patch('scripts.civitai_manager_libs.recipe_actions.recipe_gallery.getattr')
def test_generate_image_thumbnail_missing_settings(mock_getattr):
    """Test thumbnail generation with missing settings."""
    gallery = RecipeGallery()

    # Mock getattr to return default values for missing settings
    mock_getattr.side_effect = lambda obj, attr, default: default

    with (
        patch('scripts.civitai_manager_libs.recipe_actions.recipe_gallery.Image') as mock_pil_image,
        patch('scripts.civitai_manager_libs.recipe_actions.recipe_gallery.os') as mock_os,
    ):

        mock_os.makedirs.return_value = None
        mock_os.path.basename.return_value = "test.jpg"
        mock_os.path.join.return_value = "/thumbnails/test.jpg"

        mock_image = Mock()
        mock_pil_image.open.return_value.__enter__ = Mock(return_value=mock_image)
        mock_pil_image.open.return_value.__exit__ = Mock(return_value=None)

        result = gallery.generate_image_thumbnail("/path/to/test.jpg")
        assert result == "/thumbnails/test.jpg"

        # Verify thumbnail was called with default dimensions (256x256)
        mock_image.thumbnail.assert_called_once_with((256, 256))
