import pytest
from unittest.mock import patch

import scripts.civitai_manager_libs.setting as setting
import scripts.civitai_manager_libs.recipe_action as recipe_action


@pytest.fixture(autouse=True)
def use_tmp_recipe_file(tmp_path, monkeypatch):
    """Redirect recipe storage to a temporary file for tests."""
    tmp_file = tmp_path / "recipes.json"
    tmp_folder = tmp_path / "sc_recipes"
    monkeypatch.setattr(setting, "shortcut_recipe", str(tmp_file))
    monkeypatch.setattr(setting, "shortcut_recipe_folder", str(tmp_folder))
    yield


def test_delegation_functions_existence():
    """Test that all delegation functions exist in recipe_action module."""
    # Recipe management functions
    assert hasattr(recipe_action, 'make_recipe_from_sc_information')
    assert hasattr(recipe_action, 'write_recipe_collection')
    assert hasattr(recipe_action, 'delete_recipe_collection')
    assert hasattr(recipe_action, 'get_recipe')
    assert hasattr(recipe_action, 'list_recipes')
    assert hasattr(recipe_action, 'duplicate_recipe')
    assert hasattr(recipe_action, 'validate_recipe_data')

    # Browser functions
    assert hasattr(recipe_action, 'on_ui')
    assert hasattr(recipe_action, 'recipe_browser_page')

    # Reference functions
    assert hasattr(recipe_action, 'get_recipe_references')
    assert hasattr(recipe_action, 'add_recipe_reference')
    assert hasattr(recipe_action, 'remove_recipe_reference')
    assert hasattr(recipe_action, 'update_recipe_reference')
    assert hasattr(recipe_action, 'sync_references_with_models')

    # Gallery functions
    assert hasattr(recipe_action, 'create_gallery_ui')
    assert hasattr(recipe_action, 'load_recipe_images')
    assert hasattr(recipe_action, 'add_image_to_recipe')
    assert hasattr(recipe_action, 'remove_image_from_recipe')
    assert hasattr(recipe_action, 'generate_image_thumbnail')
    assert hasattr(recipe_action, 'get_image_metadata')

    # Utility functions
    assert hasattr(recipe_action, 'export_recipe')
    assert hasattr(recipe_action, 'import_recipe')
    assert hasattr(recipe_action, 'validate_recipe_format')
    assert hasattr(recipe_action, 'generate_recipe_id')
    assert hasattr(recipe_action, 'backup_recipe_data')
    assert hasattr(recipe_action, 'restore_recipe_data')

    # UI Event handler functions
    assert hasattr(recipe_action, 'on_recipe_drop_image_upload')
    assert hasattr(recipe_action, 'on_recipe_generate_data_change')
    assert hasattr(recipe_action, 'on_recipe_gallery_select')
    assert hasattr(recipe_action, 'on_refresh_recipe_change')
    assert hasattr(recipe_action, 'on_recipe_new_btn_click')
    assert hasattr(recipe_action, 'on_recipe_update_btn_click')
    assert hasattr(recipe_action, 'on_recipe_delete_btn_click')
    assert hasattr(recipe_action, 'load_model_information')
    assert hasattr(recipe_action, 'on_reference_modelid_change')
    assert hasattr(recipe_action, 'on_reference_versions_select')
    assert hasattr(recipe_action, 'on_delete_reference_model_btn_click')
    assert hasattr(recipe_action, 'on_close_reference_model_information_btn_click')
    assert hasattr(recipe_action, 'on_insert_prompt_btn_click')
    assert hasattr(recipe_action, 'on_recipe_prompt_tabs_select')
    assert hasattr(recipe_action, 'on_reference_gallery_loading')
    assert hasattr(recipe_action, 'on_reference_sc_gallery_select')
    assert hasattr(recipe_action, 'on_reference_gallery_select')
    assert hasattr(recipe_action, 'add_string')
    assert hasattr(recipe_action, 'remove_strings')
    assert hasattr(recipe_action, 'is_string')
    assert hasattr(recipe_action, 'analyze_prompt')
    assert hasattr(recipe_action, 'on_recipe_input_change')
    assert hasattr(recipe_action, 'get_recipe_information')
    assert hasattr(recipe_action, 'on_recipe_create_btn_click')
    assert hasattr(recipe_action, 'generate_prompt')


def test_recipe_management_delegations():
    """Test recipe management function delegations."""
    # Test make_recipe_from_sc_information
    with patch.object(
        recipe_action._recipe_manager, 'create_recipe', return_value="test_id"
    ) as mock_create:
        result = recipe_action.make_recipe_from_sc_information({"name": "test"})
        assert result == "test_id"
        mock_create.assert_called_once_with({"name": "test"})

    # Test write_recipe_collection
    with patch.object(
        recipe_action._recipe_manager, 'update_recipe', return_value=True
    ) as mock_update:
        result = recipe_action.write_recipe_collection("id", {"name": "updated"})
        assert result is True
        mock_update.assert_called_once_with("id", {"name": "updated"})

    # Test delete_recipe_collection
    with patch.object(
        recipe_action._recipe_manager, 'delete_recipe', return_value=True
    ) as mock_delete:
        result = recipe_action.delete_recipe_collection("test_id")
        assert result is True
        mock_delete.assert_called_once_with("test_id")

    # Test get_recipe
    with patch.object(
        recipe_action._recipe_manager, 'get_recipe', return_value={"name": "test"}
    ) as mock_get:
        result = recipe_action.get_recipe("test_id")
        assert result == {"name": "test"}
        mock_get.assert_called_once_with("test_id")

    # Test list_recipes
    with patch.object(
        recipe_action._recipe_manager, 'list_recipes', return_value=["r1", "r2"]
    ) as mock_list:
        result = recipe_action.list_recipes({"search": "test"})
        assert result == ["r1", "r2"]
        mock_list.assert_called_once_with({"search": "test"})

    # Test duplicate_recipe
    with patch.object(
        recipe_action._recipe_manager, 'duplicate_recipe', return_value="dup_id"
    ) as mock_dup:
        result = recipe_action.duplicate_recipe("orig_id", "new_name")
        assert result == "dup_id"
        mock_dup.assert_called_once_with("orig_id", "new_name")

    # Test validate_recipe_data
    with patch.object(
        recipe_action._recipe_manager, 'validate_recipe_data', return_value=True
    ) as mock_validate:
        result = recipe_action.validate_recipe_data({"name": "test"})
        assert result is True
        mock_validate.assert_called_once_with({"name": "test"})


def test_browser_delegations():
    """Test browser function delegations."""
    # Test on_ui
    with patch.object(
        recipe_action._recipe_browser, 'on_ui', return_value="ui_result"
    ) as mock_on_ui:
        result = recipe_action.on_ui("recipe_input", "shortcut_input", "civitai_tabs")
        assert result == "ui_result"
        mock_on_ui.assert_called_once_with("recipe_input", "shortcut_input", "civitai_tabs")

    # Test recipe_browser_page
    with patch.object(
        recipe_action._recipe_browser, 'create_browser_ui', return_value=("gallery", "refresh")
    ) as mock_browser:
        result = recipe_action.recipe_browser_page()
        assert result == ("gallery", "refresh")
        mock_browser.assert_called_once_with()


def test_reference_delegations():
    """Test reference management function delegations."""
    # Test get_recipe_references
    with patch.object(
        recipe_action._recipe_reference_manager, 'get_recipe_references', return_value=["ref1"]
    ) as mock_get_refs:
        result = recipe_action.get_recipe_references("recipe_id")
        assert result == ["ref1"]
        mock_get_refs.assert_called_once_with("recipe_id")

    # Test add_recipe_reference
    with patch.object(
        recipe_action._recipe_reference_manager, 'add_recipe_reference', return_value=True
    ) as mock_add_ref:
        result = recipe_action.add_recipe_reference("recipe_id", {"model_id": "model1"})
        assert result is True
        mock_add_ref.assert_called_once_with("recipe_id", {"model_id": "model1"})

    # Test remove_recipe_reference
    with patch.object(
        recipe_action._recipe_reference_manager, 'remove_recipe_reference', return_value=True
    ) as mock_remove_ref:
        result = recipe_action.remove_recipe_reference("recipe_id", "ref_id")
        assert result is True
        mock_remove_ref.assert_called_once_with("recipe_id", "ref_id")

    # Test update_recipe_reference
    with patch.object(
        recipe_action._recipe_reference_manager, 'update_recipe_reference', return_value=False
    ) as mock_update_ref:
        result = recipe_action.update_recipe_reference("ref_id", {"data": "test"})
        assert result is False
        mock_update_ref.assert_called_once_with("ref_id", {"data": "test"})

    # Test sync_references_with_models
    with patch.object(
        recipe_action._recipe_reference_manager, 'sync_references_with_models', return_value=False
    ) as mock_sync:
        result = recipe_action.sync_references_with_models("recipe_id")
        assert result is False
        mock_sync.assert_called_once_with("recipe_id")


def test_gallery_delegations():
    """Test gallery function delegations."""
    # Test create_gallery_ui
    with patch.object(
        recipe_action._recipe_gallery, 'create_gallery_ui', return_value="gallery_ui"
    ) as mock_create_gallery:
        result = recipe_action.create_gallery_ui("recipe_id")
        assert result == "gallery_ui"
        mock_create_gallery.assert_called_once_with("recipe_id")

    # Test load_recipe_images
    with patch.object(
        recipe_action._recipe_gallery, 'load_recipe_images', return_value=["img1.jpg"]
    ) as mock_load_images:
        result = recipe_action.load_recipe_images("recipe_id")
        assert result == ["img1.jpg"]
        mock_load_images.assert_called_once_with("recipe_id")

    # Test add_image_to_recipe
    with patch.object(
        recipe_action._recipe_gallery, 'add_image_to_recipe', return_value=True
    ) as mock_add_image:
        result = recipe_action.add_image_to_recipe("recipe_id", "image.jpg")
        assert result is True
        mock_add_image.assert_called_once_with("recipe_id", "image.jpg")

    # Test remove_image_from_recipe
    with patch.object(
        recipe_action._recipe_gallery, 'remove_image_from_recipe', return_value=True
    ) as mock_remove_image:
        result = recipe_action.remove_image_from_recipe("recipe_id", "image_id")
        assert result is True
        mock_remove_image.assert_called_once_with("recipe_id", "image_id")

    # Test generate_image_thumbnail
    with patch.object(
        recipe_action._recipe_gallery, 'generate_image_thumbnail', return_value="/thumb/img.jpg"
    ) as mock_gen_thumb:
        result = recipe_action.generate_image_thumbnail("/path/img.jpg")
        assert result == "/thumb/img.jpg"
        mock_gen_thumb.assert_called_once_with("/path/img.jpg")

    # Test get_image_metadata
    with patch.object(
        recipe_action._recipe_gallery, 'get_image_metadata', return_value={"meta": "data"}
    ) as mock_get_meta:
        result = recipe_action.get_image_metadata("/path/img.jpg")
        assert result == {"meta": "data"}
        mock_get_meta.assert_called_once_with("/path/img.jpg")


def test_utility_delegations():
    """Test utility function delegations."""
    # Test export_recipe
    with patch(
        'scripts.civitai_manager_libs.recipe_action.RecipeUtilities.export_recipe',
        return_value="/export/recipe.json",
    ) as mock_export:
        result = recipe_action.export_recipe("recipe_id", "json")
        assert result == "/export/recipe.json"
        mock_export.assert_called_once_with("recipe_id", "json")

    # Test import_recipe
    with patch(
        'scripts.civitai_manager_libs.recipe_action.RecipeUtilities.import_recipe',
        return_value="imported_id",
    ) as mock_import:
        result = recipe_action.import_recipe("/import/recipe.json")
        assert result == "imported_id"
        mock_import.assert_called_once_with("/import/recipe.json")

    # Test validate_recipe_format
    with patch(
        'scripts.civitai_manager_libs.recipe_action.RecipeUtilities.validate_recipe_format',
        return_value=True,
    ) as mock_validate_format:
        result = recipe_action.validate_recipe_format({"name": "test"})
        assert result is True
        mock_validate_format.assert_called_once_with({"name": "test"})

    # Test generate_recipe_id
    with patch(
        'scripts.civitai_manager_libs.recipe_action.RecipeUtilities.generate_recipe_id',
        return_value="uuid123",
    ) as mock_gen_id:
        result = recipe_action.generate_recipe_id()
        assert result == "uuid123"
        mock_gen_id.assert_called_once_with()

    # Test backup_recipe_data
    with patch(
        'scripts.civitai_manager_libs.recipe_action.RecipeUtilities.backup_recipe_data',
        return_value="/backup/recipe.json",
    ) as mock_backup:
        result = recipe_action.backup_recipe_data("recipe_id")
        assert result == "/backup/recipe.json"
        mock_backup.assert_called_once_with("recipe_id")

    # Test restore_recipe_data
    with patch(
        'scripts.civitai_manager_libs.recipe_action.RecipeUtilities.restore_recipe_data',
        return_value=True,
    ) as mock_restore:
        result = recipe_action.restore_recipe_data("/backup/recipe.json")
        assert result is True
        mock_restore.assert_called_once_with("/backup/recipe.json")


def test_global_instances():
    """Test that global instances are created correctly."""
    assert recipe_action._recipe_manager is not None
    assert recipe_action._recipe_browser is not None
    assert recipe_action._recipe_reference_manager is not None
    assert recipe_action._recipe_gallery is not None

    # Check types
    from scripts.civitai_manager_libs.recipe_actions.recipe_management import RecipeManager
    from scripts.civitai_manager_libs.recipe_actions.recipe_browser import RecipeBrowser
    from scripts.civitai_manager_libs.recipe_actions.recipe_reference import RecipeReferenceManager
    from scripts.civitai_manager_libs.recipe_actions.recipe_gallery import RecipeGallery

    assert isinstance(recipe_action._recipe_manager, RecipeManager)
    assert isinstance(recipe_action._recipe_browser, RecipeBrowser)
    assert isinstance(recipe_action._recipe_reference_manager, RecipeReferenceManager)
    assert isinstance(recipe_action._recipe_gallery, RecipeGallery)


def test_multiple_delegations_with_kwargs():
    """Test delegations with various argument patterns."""
    # Test with positional and keyword arguments
    with patch.object(
        recipe_action._recipe_manager, 'create_recipe', return_value="test"
    ) as mock_create:
        result = recipe_action.make_recipe_from_sc_information(
            {"name": "test"}, description="desc", classification="cat"
        )
        assert result == "test"
        mock_create.assert_called_once_with(
            {"name": "test"}, description="desc", classification="cat"
        )

    # Test with only keyword arguments
    with patch.object(
        recipe_action._recipe_manager, 'list_recipes', return_value=["recipe1"]
    ) as mock_list:
        result = recipe_action.list_recipes(search="test", classification="category")
        assert result == ["recipe1"]
        mock_list.assert_called_once_with(search="test", classification="category")


def test_error_propagation():
    """Test that errors from underlying modules are properly propagated."""
    # Test exception propagation from recipe manager
    with patch.object(
        recipe_action._recipe_manager, 'create_recipe', side_effect=ValueError("Invalid data")
    ):
        with pytest.raises(ValueError, match="Invalid data"):
            recipe_action.make_recipe_from_sc_information({"invalid": "data"})

    # Test exception propagation from utility functions
    with patch(
        'scripts.civitai_manager_libs.recipe_action.RecipeUtilities.export_recipe',
        side_effect=FileNotFoundError("File not found"),
    ):
        with pytest.raises(FileNotFoundError, match="File not found"):
            recipe_action.export_recipe("nonexistent_recipe", "json")


def test_logger_initialization():
    """Test that module logger is properly initialized."""
    assert recipe_action.logger is not None
    assert hasattr(recipe_action.logger, 'info')
    assert hasattr(recipe_action.logger, 'error')
    assert hasattr(recipe_action.logger, 'debug')
    assert hasattr(recipe_action.logger, 'warning')


def test_ui_event_handler_delegations():
    """Test UI event handler function delegations."""
    # Test gallery UI event handlers
    with patch.object(
        recipe_action._recipe_gallery, 'on_recipe_drop_image_upload', return_value="upload_result"
    ) as mock_upload:
        result = recipe_action.on_recipe_drop_image_upload("image_data", "recipe_id")
        assert result == "upload_result"
        mock_upload.assert_called_once_with("image_data", "recipe_id")

    with patch.object(
        recipe_action._recipe_gallery,
        'on_recipe_generate_data_change',
        return_value="data_change_result",
    ) as mock_data_change:
        result = recipe_action.on_recipe_generate_data_change("new_data")
        assert result == "data_change_result"
        mock_data_change.assert_called_once_with("new_data")

    with patch.object(
        recipe_action._recipe_gallery,
        'on_recipe_gallery_select',
        return_value="gallery_select_result",
    ) as mock_gallery_select:
        result = recipe_action.on_recipe_gallery_select("selected_image")
        assert result == "gallery_select_result"
        mock_gallery_select.assert_called_once_with("selected_image")

    # Test browser UI event handlers
    with patch.object(
        recipe_action._recipe_browser, 'on_refresh_recipe_change', return_value="refresh_result"
    ) as mock_refresh:
        result = recipe_action.on_refresh_recipe_change("refresh_data")
        assert result == "refresh_result"
        mock_refresh.assert_called_once_with("refresh_data")

    with patch.object(
        recipe_action._recipe_browser,
        'on_recipe_prompt_tabs_select',
        return_value="tab_select_result",
    ) as mock_tab_select:
        result = recipe_action.on_recipe_prompt_tabs_select("tab_index")
        assert result == "tab_select_result"
        mock_tab_select.assert_called_once_with("tab_index")

    with patch.object(
        recipe_action._recipe_browser, 'on_recipe_input_change', return_value="input_change_result"
    ) as mock_input_change:
        result = recipe_action.on_recipe_input_change("input_value")
        assert result == "input_change_result"
        mock_input_change.assert_called_once_with("input_value")

    # Test recipe management UI event handlers
    with patch.object(
        recipe_action._recipe_manager, 'on_recipe_new_btn_click', return_value="new_btn_result"
    ) as mock_new_btn:
        result = recipe_action.on_recipe_new_btn_click()
        assert result == "new_btn_result"
        mock_new_btn.assert_called_once_with()

    with patch.object(
        recipe_action._recipe_manager,
        'on_recipe_update_btn_click',
        return_value="update_btn_result",
    ) as mock_update_btn:
        result = recipe_action.on_recipe_update_btn_click("recipe_id", "data")
        assert result == "update_btn_result"
        mock_update_btn.assert_called_once_with("recipe_id", "data")

    with patch.object(
        recipe_action._recipe_manager,
        'on_recipe_delete_btn_click',
        return_value="delete_btn_result",
    ) as mock_delete_btn:
        result = recipe_action.on_recipe_delete_btn_click("recipe_id")
        assert result == "delete_btn_result"
        mock_delete_btn.assert_called_once_with("recipe_id")

    with patch.object(
        recipe_action._recipe_manager,
        'on_recipe_create_btn_click',
        return_value="create_btn_result",
    ) as mock_create_btn:
        result = recipe_action.on_recipe_create_btn_click("recipe_data")
        assert result == "create_btn_result"
        mock_create_btn.assert_called_once_with("recipe_data")


def test_reference_ui_event_handlers():
    """Test reference management UI event handler delegations."""
    with patch.object(
        recipe_action._recipe_reference_manager, 'load_model_information', return_value="model_info"
    ) as mock_load_model:
        result = recipe_action.load_model_information("model_id")
        assert result == "model_info"
        mock_load_model.assert_called_once_with("model_id")

    with patch.object(
        recipe_action._recipe_reference_manager,
        'on_reference_modelid_change',
        return_value="modelid_change_result",
    ) as mock_modelid_change:
        result = recipe_action.on_reference_modelid_change("new_model_id")
        assert result == "modelid_change_result"
        mock_modelid_change.assert_called_once_with("new_model_id")

    with patch.object(
        recipe_action._recipe_reference_manager,
        'on_reference_versions_select',
        return_value="version_select_result",
    ) as mock_version_select:
        result = recipe_action.on_reference_versions_select("version_id")
        assert result == "version_select_result"
        mock_version_select.assert_called_once_with("version_id")

    with patch.object(
        recipe_action._recipe_reference_manager,
        'on_delete_reference_model_btn_click',
        return_value="delete_ref_result",
    ) as mock_delete_ref:
        result = recipe_action.on_delete_reference_model_btn_click("ref_id")
        assert result == "delete_ref_result"
        mock_delete_ref.assert_called_once_with("ref_id")

    ref_mgr = recipe_action._recipe_reference_manager
    with patch.object(
        ref_mgr, 'on_close_reference_model_information_btn_click', return_value="close_info_result"
    ) as mock_close_info:
        result = recipe_action.on_close_reference_model_information_btn_click()
        assert result == "close_info_result"
        mock_close_info.assert_called_once_with()

    with patch.object(
        recipe_action._recipe_reference_manager,
        'on_insert_prompt_btn_click',
        return_value="insert_prompt_result",
    ) as mock_insert_prompt:
        result = recipe_action.on_insert_prompt_btn_click("prompt_text")
        assert result == "insert_prompt_result"
        mock_insert_prompt.assert_called_once_with("prompt_text")

    with patch.object(
        recipe_action._recipe_reference_manager,
        'on_reference_gallery_loading',
        return_value="gallery_loading_result",
    ) as mock_gallery_loading:
        result = recipe_action.on_reference_gallery_loading("gallery_data")
        assert result == "gallery_loading_result"
        mock_gallery_loading.assert_called_once_with("gallery_data")

    with patch.object(
        recipe_action._recipe_reference_manager,
        'on_reference_sc_gallery_select',
        return_value="sc_gallery_select_result",
    ) as mock_sc_gallery_select:
        result = recipe_action.on_reference_sc_gallery_select("sc_gallery_item")
        assert result == "sc_gallery_select_result"
        mock_sc_gallery_select.assert_called_once_with("sc_gallery_item")

    with patch.object(
        recipe_action._recipe_reference_manager,
        'on_reference_gallery_select',
        return_value="ref_gallery_select_result",
    ) as mock_ref_gallery_select:
        result = recipe_action.on_reference_gallery_select("ref_gallery_item")
        assert result == "ref_gallery_select_result"
        mock_ref_gallery_select.assert_called_once_with("ref_gallery_item")


def test_string_utility_delegations():
    """Test string utility function delegations."""
    with patch.object(
        recipe_action._recipe_reference_manager, 'add_string', return_value="add_string_result"
    ) as mock_add_string:
        result = recipe_action.add_string("text", "category")
        assert result == "add_string_result"
        mock_add_string.assert_called_once_with("text", "category")

    with patch.object(
        recipe_action._recipe_reference_manager,
        'remove_strings',
        return_value="remove_strings_result",
    ) as mock_remove_strings:
        result = recipe_action.remove_strings(["text1", "text2"])
        assert result == "remove_strings_result"
        mock_remove_strings.assert_called_once_with(["text1", "text2"])

    with patch.object(
        recipe_action._recipe_reference_manager, 'is_string', return_value=True
    ) as mock_is_string:
        result = recipe_action.is_string("text", "category")
        assert result is True
        mock_is_string.assert_called_once_with("text", "category")


def test_additional_utility_delegations():
    """Test additional utility function delegations."""
    with patch(
        'scripts.civitai_manager_libs.recipe_action.RecipeUtilities.analyze_prompt',
        return_value="analysis_result",
    ) as mock_analyze:
        result = recipe_action.analyze_prompt("prompt_text")
        assert result == "analysis_result"
        mock_analyze.assert_called_once_with("prompt_text")

    with patch(
        'scripts.civitai_manager_libs.recipe_action.RecipeUtilities.get_recipe_information',
        return_value="recipe_info",
    ) as mock_get_info:
        result = recipe_action.get_recipe_information("recipe_id")
        assert result == "recipe_info"
        mock_get_info.assert_called_once_with("recipe_id")

    with patch(
        'scripts.civitai_manager_libs.recipe_action.RecipeUtilities.generate_prompt',
        return_value="generated_prompt",
    ) as mock_generate:
        result = recipe_action.generate_prompt("recipe_data")
        assert result == "generated_prompt"
        mock_generate.assert_called_once_with("recipe_data")
