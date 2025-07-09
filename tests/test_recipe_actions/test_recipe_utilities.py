import json
import os
import pytest
from unittest.mock import patch, mock_open

import scripts.civitai_manager_libs.setting as setting
from scripts.civitai_manager_libs.recipe_actions.recipe_utilities import RecipeUtilities
from scripts.civitai_manager_libs.exceptions import ValidationError, FileOperationError


@pytest.fixture(autouse=True)
def use_tmp_recipe_file(tmp_path, monkeypatch):
    """Redirect recipe storage to a temporary file for tests."""
    tmp_file = tmp_path / "recipes.json"
    tmp_folder = tmp_path / "sc_recipes"
    monkeypatch.setattr(setting, "shortcut_recipe", str(tmp_file))
    monkeypatch.setattr(setting, "shortcut_recipe_folder", str(tmp_folder))
    monkeypatch.setattr(setting, "PLACEHOLDER", "Select Classification")
    os.makedirs(tmp_folder, exist_ok=True)
    tmp_file.write_text("{}")
    yield


def test_generate_recipe_id():
    rid = RecipeUtilities.generate_recipe_id()
    assert isinstance(rid, str)
    assert len(rid) == 32


def test_validate_recipe_format():
    assert RecipeUtilities.validate_recipe_format({"name": "a"})
    assert not RecipeUtilities.validate_recipe_format({})
    assert not RecipeUtilities.validate_recipe_format({"name": ""})
    assert not RecipeUtilities.validate_recipe_format({"name": "   "})  # Whitespace only
    assert not RecipeUtilities.validate_recipe_format({"name": 123})  # Non-string name
    assert not RecipeUtilities.validate_recipe_format("not_dict")  # Not a dictionary


def test_export_and_import_recipe(tmp_path):
    utils = RecipeUtilities()
    test_id = "petest"
    data = {test_id: {"description": "d", "generate": "g", "classification": None}}
    import_file = tmp_path / "import.json"
    import_file.write_text(json.dumps(data))
    # Import recipe
    out_id = utils.import_recipe(str(import_file))
    assert out_id == test_id
    # Export recipe
    export_path = utils.export_recipe(test_id, "json")
    assert os.path.isfile(export_path)
    with open(export_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert test_id in loaded


def test_export_recipe_not_found():
    utils = RecipeUtilities()

    with patch(
        'scripts.civitai_manager_libs.recipe_actions.recipe_utilities._raw_get', return_value=None
    ):
        with pytest.raises(ValidationError, match="Recipe not found: nonexistent"):
            utils.export_recipe("nonexistent", "json")


def test_export_recipe_unsupported_format():
    utils = RecipeUtilities()

    with patch(
        'scripts.civitai_manager_libs.recipe_actions.recipe_utilities._raw_get',
        return_value={"data": "test"},
    ):
        with pytest.raises(ValidationError, match="Unsupported export format: xml"):
            utils.export_recipe("test", "xml")


def test_export_recipe_file_error():
    utils = RecipeUtilities()

    with (
        patch(
            'scripts.civitai_manager_libs.recipe_actions.recipe_utilities._raw_get',
            return_value={"data": "test"},
        ),
        patch('builtins.open', side_effect=IOError("Permission denied")),
    ):
        with pytest.raises(FileOperationError):
            utils.export_recipe("test", "json")


def test_import_recipe_file_not_found():
    utils = RecipeUtilities()

    with pytest.raises(ValidationError, match="Import file not found"):
        utils.import_recipe("/nonexistent/file.json")


def test_import_recipe_read_error():
    utils = RecipeUtilities()

    with (
        patch('os.path.isfile', return_value=True),
        patch('builtins.open', side_effect=IOError("Read error")),
    ):
        with pytest.raises(FileOperationError):
            utils.import_recipe("/some/file.json")


def test_import_recipe_invalid_data_format():
    utils = RecipeUtilities()

    # Invalid JSON structure
    mock_data = {"recipe1": {"data": "test"}, "recipe2": {"data": "test2"}}  # Multiple recipes

    with (
        patch('os.path.isfile', return_value=True),
        patch('builtins.open', mock_open(read_data=json.dumps(mock_data))),
    ):
        with pytest.raises(ValidationError, match="Invalid recipe data format for import"):
            utils.import_recipe("/some/file.json")


def test_import_recipe_create_failure():
    utils = RecipeUtilities()

    valid_data = {
        "test_recipe": {"description": "desc", "generate": "gen", "classification": "cat"}
    }

    with (
        patch('os.path.isfile', return_value=True),
        patch('builtins.open', mock_open(read_data=json.dumps(valid_data))),
        patch(
            'scripts.civitai_manager_libs.recipe_actions.recipe_utilities._raw_create',
            return_value=False,
        ),
    ):
        with pytest.raises(FileOperationError):
            utils.import_recipe("/some/file.json")


def test_backup_and_restore_recipe(tmp_path, monkeypatch):
    utils = RecipeUtilities()
    # override settings for file paths
    monkeypatch.setattr(setting, "shortcut_recipe_folder", str(tmp_path))
    monkeypatch.setattr(setting, "shortcut_recipe", str(tmp_path / "recipes.json"))
    test_id = "bptest"
    # simulate original recipe file
    origin_file = tmp_path / f"{test_id}.json"
    origin_file.write_text("{}")
    # Backup
    backup_path = utils.backup_recipe_data(test_id)
    assert os.path.isfile(backup_path)
    # Remove and restore
    origin_file.unlink()
    assert utils.restore_recipe_data(backup_path)
    assert origin_file.exists()


def test_backup_recipe_data_error():
    utils = RecipeUtilities()

    with patch('shutil.copy2', side_effect=IOError("Permission denied")):
        with pytest.raises(FileOperationError):
            utils.backup_recipe_data("test_recipe")


def test_restore_recipe_data_file_not_found():
    utils = RecipeUtilities()

    with pytest.raises(ValidationError, match="Backup file not found"):
        utils.restore_recipe_data("/nonexistent/backup.json")


def test_restore_recipe_data_error():
    utils = RecipeUtilities()

    with (
        patch('os.path.isfile', return_value=True),
        patch('shutil.copy2', side_effect=IOError("Permission denied")),
    ):
        with pytest.raises(FileOperationError):
            utils.restore_recipe_data("/some/backup_testid_20230101120000.json")


def test_generate_prompt():
    # Test with all components
    result = RecipeUtilities.generate_prompt("test prompt", "test negative", "param1:value1")
    expected = "test prompt\nNegative prompt:test negative\nparam1:value1"
    assert result == expected

    # Test with only prompt
    result = RecipeUtilities.generate_prompt("test prompt", "", "")
    assert result == "test prompt\n"

    # Test with only negative prompt
    result = RecipeUtilities.generate_prompt("", "test negative", "")
    assert result == "Negative prompt:test negative\n"

    # Test with only options
    result = RecipeUtilities.generate_prompt("", "", "param1:value1")
    assert result == "param1:value1"

    # Test with no components
    result = RecipeUtilities.generate_prompt("", "", "")
    assert result is None

    # Test with whitespace
    result = RecipeUtilities.generate_prompt("   ", "   ", "   ")
    assert result is None


@patch('scripts.civitai_manager_libs.prompt.parse_data')
def test_analyze_prompt(mock_parse_data):
    # Test with valid generate data
    mock_parse_data.return_value = {
        'prompt': 'test prompt',
        'negativePrompt': 'test negative',
        'options': {'param1': 'value1', 'param2': 'value2'},
    }

    result = RecipeUtilities.analyze_prompt("some_generate_data")

    expected_prompt = 'test prompt'
    expected_negative = 'test negative'
    expected_options = 'param1:value1, param2:value2'
    expected_string = 'test prompt\nNegative prompt:test negative\nparam1:value1, param2:value2'

    assert result == (expected_prompt, expected_negative, expected_options, expected_string)


@patch('scripts.civitai_manager_libs.prompt.parse_data')
def test_analyze_prompt_parse_exception(mock_parse_data):
    # Test when parse_data raises exception
    mock_parse_data.side_effect = Exception("Parse error")

    result = RecipeUtilities.analyze_prompt("invalid_data")

    # Should return all None values
    assert result == (None, None, None, None)


@patch('scripts.civitai_manager_libs.prompt.parse_data')
def test_analyze_prompt_empty_data(mock_parse_data):
    # Test with empty generate data
    result = RecipeUtilities.analyze_prompt("")

    # parse_data should not be called for empty data
    mock_parse_data.assert_not_called()
    assert result == (None, None, None, None)


@patch('scripts.civitai_manager_libs.prompt.parse_data')
def test_analyze_prompt_no_generate(mock_parse_data):
    # Test when parse_data returns None
    mock_parse_data.return_value = None

    result = RecipeUtilities.analyze_prompt("some_data")

    assert result == (None, None, None, None)


@patch('scripts.civitai_manager_libs.recipe.get_recipe')
def test_get_recipe_information(mock_get_recipe):
    # Test with complete recipe data
    mock_recipe_data = {
        'generate': {
            'prompt': 'test prompt',
            'negativePrompt': 'test negative',
            'options': {'param1': 'value1', 'param2': 'value2'},
        },
        'description': 'test description',
        'classification': 'test category',
        'image': 'test_image.jpg',
    }
    mock_get_recipe.return_value = mock_recipe_data

    with patch('os.path.join', return_value='/path/to/test_image.jpg'):
        result = RecipeUtilities.get_recipe_information("test_recipe")

    description, prompt, negative, options, gen_string, classification, imagefile = result

    assert description == 'test description'
    assert prompt == 'test prompt'
    assert negative == 'test negative'
    assert options == 'param1:value1, param2:value2'
    assert classification == 'test category'
    assert imagefile == '/path/to/test_image.jpg'
    assert gen_string is not None


@patch('scripts.civitai_manager_libs.recipe.get_recipe')
def test_get_recipe_information_empty_classification(mock_get_recipe):
    # Test with empty classification
    mock_recipe_data = {
        'generate': {'prompt': 'test prompt', 'negativePrompt': 'test negative'},
        'description': 'test description',
        'classification': '',  # Empty classification
    }
    mock_get_recipe.return_value = mock_recipe_data

    result = RecipeUtilities.get_recipe_information("test_recipe")
    classification = result[5]

    assert classification == setting.PLACEHOLDER


@patch('scripts.civitai_manager_libs.recipe.get_recipe')
def test_get_recipe_information_no_recipe(mock_get_recipe):
    # Test with non-existent recipe
    mock_get_recipe.return_value = None

    result = RecipeUtilities.get_recipe_information("nonexistent")

    # Should return all None/empty values
    description, prompt, negative, options, gen_string, classification, imagefile = result

    assert description is None
    assert prompt is None
    assert negative is None
    assert options is None
    assert gen_string is None
    assert classification is None
    assert imagefile is None


@patch('scripts.civitai_manager_libs.recipe.get_recipe')
def test_get_recipe_information_no_image(mock_get_recipe):
    # Test with recipe that has no image
    mock_recipe_data = {
        'generate': {'prompt': 'test prompt'},
        'description': 'test description',
        'classification': 'test category',
        # No 'image' key
    }
    mock_get_recipe.return_value = mock_recipe_data

    result = RecipeUtilities.get_recipe_information("test_recipe")
    imagefile = result[6]

    assert imagefile is None
