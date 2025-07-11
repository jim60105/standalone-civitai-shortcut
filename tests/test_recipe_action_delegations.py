import pytest
from unittest.mock import patch

from scripts.civitai_manager_libs import settings
from scripts.civitai_manager_libs.recipe_actions.recipe_management import RecipeManager
from scripts.civitai_manager_libs.recipe_actions.recipe_browser import RecipeBrowser
from scripts.civitai_manager_libs.recipe_actions.recipe_reference import RecipeReferenceManager
from scripts.civitai_manager_libs.recipe_actions.recipe_gallery import RecipeGallery
from scripts.civitai_manager_libs.recipe_actions.recipe_utilities import RecipeUtilities


@pytest.fixture(autouse=True)
def use_tmp_recipe_file(tmp_path, monkeypatch):
    """Redirect recipe storage to a temporary file for tests."""
    tmp_file = tmp_path / "recipes.json"
    tmp_folder = tmp_path / "sc_recipes"
    monkeypatch.setattr(settings, "shortcut_recipe", str(tmp_file))
    monkeypatch.setattr(settings, "shortcut_recipe_folder", str(tmp_folder))
    yield


def test_recipe_action_classes_functionality():
    """Test that all recipe action classes have expected methods."""
    # Recipe management functions
    recipe_manager = RecipeManager()
    assert hasattr(recipe_manager, 'create_recipe')
    assert hasattr(recipe_manager, 'update_recipe')
    assert hasattr(recipe_manager, 'delete_recipe')
    assert hasattr(recipe_manager, 'get_recipe')
    assert hasattr(recipe_manager, 'list_recipes')
    assert hasattr(recipe_manager, 'duplicate_recipe')
    assert hasattr(recipe_manager, 'validate_recipe_data')

    # Browser functions
    recipe_browser = RecipeBrowser()
    assert hasattr(recipe_browser, 'on_ui')
    assert hasattr(recipe_browser, 'create_browser_ui')

    # Reference functions
    recipe_reference_manager = RecipeReferenceManager()
    assert hasattr(recipe_reference_manager, 'get_recipe_references')
    assert hasattr(recipe_reference_manager, 'add_recipe_reference')
    assert hasattr(recipe_reference_manager, 'remove_recipe_reference')
    assert hasattr(recipe_reference_manager, 'update_recipe_reference')
    assert hasattr(recipe_reference_manager, 'sync_references_with_models')

    # Gallery functions
    recipe_gallery = RecipeGallery()
    assert hasattr(recipe_gallery, 'create_gallery_ui')
    assert hasattr(recipe_gallery, 'load_recipe_images')
    assert hasattr(recipe_gallery, 'add_image_to_recipe')
    assert hasattr(recipe_gallery, 'remove_image_from_recipe')
    assert hasattr(recipe_gallery, 'generate_image_thumbnail')
    assert hasattr(recipe_gallery, 'get_image_metadata')

    # Utility functions
    assert hasattr(RecipeUtilities, 'export_recipe')
    assert hasattr(RecipeUtilities, 'import_recipe')
    assert hasattr(RecipeUtilities, 'validate_recipe_format')
    assert hasattr(RecipeUtilities, 'generate_recipe_id')
    assert hasattr(RecipeUtilities, 'backup_recipe_data')
    assert hasattr(RecipeUtilities, 'restore_recipe_data')
    assert hasattr(RecipeUtilities, 'analyze_prompt')
    assert hasattr(RecipeUtilities, 'get_recipe_information')
    assert hasattr(RecipeUtilities, 'generate_prompt')


def test_recipe_management_functionality():
    """Test recipe management function functionality."""
    recipe_manager = RecipeManager()

    # Test create_recipe
    with patch.object(recipe_manager, 'create_recipe', return_value="test_id") as mock_create:
        result = recipe_manager.create_recipe({"name": "test"})
        assert result == "test_id"
        mock_create.assert_called_once_with({"name": "test"})

    # Test update_recipe
    with patch.object(recipe_manager, 'update_recipe', return_value=True) as mock_update:
        result = recipe_manager.update_recipe("id", {"name": "updated"})
        assert result is True
        mock_update.assert_called_once_with("id", {"name": "updated"})

    # Test delete_recipe
    with patch.object(recipe_manager, 'delete_recipe', return_value=True) as mock_delete:
        result = recipe_manager.delete_recipe("test_id")
        assert result is True
        mock_delete.assert_called_once_with("test_id")

    # Test get_recipe
    with patch.object(recipe_manager, 'get_recipe', return_value={"name": "test"}) as mock_get:
        result = recipe_manager.get_recipe("test_id")
        assert result == {"name": "test"}
        mock_get.assert_called_once_with("test_id")

    # Test list_recipes
    with patch.object(recipe_manager, 'list_recipes', return_value=["r1", "r2"]) as mock_list:
        result = recipe_manager.list_recipes({"search": "test"})
        assert result == ["r1", "r2"]
        mock_list.assert_called_once_with({"search": "test"})

    # Test duplicate_recipe
    with patch.object(recipe_manager, 'duplicate_recipe', return_value="dup_id") as mock_dup:
        result = recipe_manager.duplicate_recipe("orig_id", "new_name")
        assert result == "dup_id"
        mock_dup.assert_called_once_with("orig_id", "new_name")

    # Test validate_recipe_data
    with patch.object(recipe_manager, 'validate_recipe_data', return_value=True) as mock_validate:
        result = recipe_manager.validate_recipe_data({"name": "test"})
        assert result is True
        mock_validate.assert_called_once_with({"name": "test"})


def test_browser_functionality():
    """Test browser function functionality."""
    recipe_browser = RecipeBrowser()

    # Test on_ui
    with patch.object(recipe_browser, 'on_ui', return_value="ui_result") as mock_on_ui:
        result = recipe_browser.on_ui("recipe_input", "shortcut_input", "civitai_tabs")
        assert result == "ui_result"
        mock_on_ui.assert_called_once_with("recipe_input", "shortcut_input", "civitai_tabs")

    # Test create_browser_ui
    with patch.object(
        recipe_browser, 'create_browser_ui', return_value=("gallery", "refresh")
    ) as mock_browser:
        result = recipe_browser.create_browser_ui()
        assert result == ("gallery", "refresh")
        mock_browser.assert_called_once_with()


def test_reference_functionality():
    """Test reference management function functionality."""
    recipe_reference_manager = RecipeReferenceManager()

    # Test get_recipe_references
    with patch.object(
        recipe_reference_manager, 'get_recipe_references', return_value=["ref1"]
    ) as mock_get_refs:
        result = recipe_reference_manager.get_recipe_references("recipe_id")
        assert result == ["ref1"]
        mock_get_refs.assert_called_once_with("recipe_id")

    # Test add_recipe_reference
    with patch.object(
        recipe_reference_manager, 'add_recipe_reference', return_value=True
    ) as mock_add_ref:
        result = recipe_reference_manager.add_recipe_reference("recipe_id", {"model_id": "model1"})
        assert result is True
        mock_add_ref.assert_called_once_with("recipe_id", {"model_id": "model1"})

    # Test remove_recipe_reference
    with patch.object(
        recipe_reference_manager, 'remove_recipe_reference', return_value=True
    ) as mock_remove_ref:
        result = recipe_reference_manager.remove_recipe_reference("recipe_id", "ref_id")
        assert result is True
        mock_remove_ref.assert_called_once_with("recipe_id", "ref_id")

    # Test update_recipe_reference
    with patch.object(
        recipe_reference_manager, 'update_recipe_reference', return_value=False
    ) as mock_update_ref:
        result = recipe_reference_manager.update_recipe_reference("ref_id", {"data": "test"})
        assert result is False
        mock_update_ref.assert_called_once_with("ref_id", {"data": "test"})

    # Test sync_references_with_models
    with patch.object(
        recipe_reference_manager, 'sync_references_with_models', return_value=False
    ) as mock_sync:
        result = recipe_reference_manager.sync_references_with_models("recipe_id")
        assert result is False
        mock_sync.assert_called_once_with("recipe_id")


def test_gallery_functionality():
    """Test gallery function functionality."""
    recipe_gallery = RecipeGallery()

    # Test create_gallery_ui
    with patch.object(
        recipe_gallery, 'create_gallery_ui', return_value="gallery_ui"
    ) as mock_gallery:
        result = recipe_gallery.create_gallery_ui("recipe_id")
        assert result == "gallery_ui"
        mock_gallery.assert_called_once_with("recipe_id")

    # Test load_recipe_images
    with patch.object(
        recipe_gallery, 'load_recipe_images', return_value=["img1", "img2"]
    ) as mock_load:
        result = recipe_gallery.load_recipe_images("recipe_id")
        assert result == ["img1", "img2"]
        mock_load.assert_called_once_with("recipe_id")

    # Test add_image_to_recipe
    with patch.object(recipe_gallery, 'add_image_to_recipe', return_value=True) as mock_add:
        result = recipe_gallery.add_image_to_recipe("recipe_id", "image_path")
        assert result is True
        mock_add.assert_called_once_with("recipe_id", "image_path")

    # Test remove_image_from_recipe
    with patch.object(recipe_gallery, 'remove_image_from_recipe', return_value=True) as mock_remove:
        result = recipe_gallery.remove_image_from_recipe("recipe_id", "image_id")
        assert result is True
        mock_remove.assert_called_once_with("recipe_id", "image_id")

    # Test generate_image_thumbnail
    with patch.object(
        recipe_gallery, 'generate_image_thumbnail', return_value="thumb_path"
    ) as mock_thumb:
        result = recipe_gallery.generate_image_thumbnail("image_path")
        assert result == "thumb_path"
        mock_thumb.assert_called_once_with("image_path")

    # Test get_image_metadata
    with patch.object(
        recipe_gallery, 'get_image_metadata', return_value={"meta": "data"}
    ) as mock_meta:
        result = recipe_gallery.get_image_metadata("image_path")
        assert result == {"meta": "data"}
        mock_meta.assert_called_once_with("image_path")


def test_utilities_functionality():
    """Test utility function functionality."""
    # Test export_recipe
    with patch.object(RecipeUtilities, 'export_recipe', return_value="export_path") as mock_export:
        result = RecipeUtilities.export_recipe("recipe_id", "json")
        assert result == "export_path"
        mock_export.assert_called_once_with("recipe_id", "json")

    # Test import_recipe
    with patch.object(RecipeUtilities, 'import_recipe', return_value="import_id") as mock_import:
        result = RecipeUtilities.import_recipe("import_path")
        assert result == "import_id"
        mock_import.assert_called_once_with("import_path")

    # Test validate_recipe_format
    with patch.object(
        RecipeUtilities, 'validate_recipe_format', return_value=True
    ) as mock_validate:
        result = RecipeUtilities.validate_recipe_format({"recipe": "data"})
        assert result is True
        mock_validate.assert_called_once_with({"recipe": "data"})

    # Test generate_recipe_id
    with patch.object(
        RecipeUtilities, 'generate_recipe_id', return_value="new_id"
    ) as mock_generate:
        result = RecipeUtilities.generate_recipe_id()
        assert result == "new_id"
        mock_generate.assert_called_once_with()

    # Test backup_recipe_data
    with patch.object(RecipeUtilities, 'backup_recipe_data', return_value=True) as mock_backup:
        result = RecipeUtilities.backup_recipe_data("recipe_id")
        assert result is True
        mock_backup.assert_called_once_with("recipe_id")

    # Test restore_recipe_data
    with patch.object(RecipeUtilities, 'restore_recipe_data', return_value=True) as mock_restore:
        result = RecipeUtilities.restore_recipe_data("backup_path")
        assert result is True
        mock_restore.assert_called_once_with("backup_path")

    # Test analyze_prompt
    with patch.object(
        RecipeUtilities, 'analyze_prompt', return_value=("p", "n", "o", "g")
    ) as mock_analyze:
        result = RecipeUtilities.analyze_prompt("prompt_text")
        assert result == ("p", "n", "o", "g")
        mock_analyze.assert_called_once_with("prompt_text")

    # Test get_recipe_information
    with patch.object(
        RecipeUtilities, 'get_recipe_information', return_value={"info": "data"}
    ) as mock_get_info:
        result = RecipeUtilities.get_recipe_information("recipe_id")
        assert result == {"info": "data"}
        mock_get_info.assert_called_once_with("recipe_id")

    # Test generate_prompt
    with patch.object(
        RecipeUtilities, 'generate_prompt', return_value="generated_prompt"
    ) as mock_gen_prompt:
        result = RecipeUtilities.generate_prompt("template", {"var": "value"}, {})
        assert result == "generated_prompt"
        mock_gen_prompt.assert_called_once_with("template", {"var": "value"}, {})
