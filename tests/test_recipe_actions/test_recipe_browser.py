import pytest

import scripts.civitai_manager_libs.setting as setting
from scripts.civitai_manager_libs.recipe_actions.recipe_browser import RecipeBrowser


@pytest.fixture(autouse=True)
def use_tmp_recipe_file(tmp_path, monkeypatch):
    """Redirect recipe storage to a temporary file for tests."""
    tmp_file = tmp_path / "recipes.json"
    tmp_folder = tmp_path / "sc_recipes"
    monkeypatch.setattr(setting, "shortcut_recipe", str(tmp_file))
    monkeypatch.setattr(setting, "shortcut_recipe_folder", str(tmp_folder))
    yield


def test_recipe_browser_create_ui(monkeypatch):
    # Simulate Gradio UI creation callback
    def dummy_on_ui():
        return ("ui_component", "refresh_trigger")

    monkeypatch.setattr("scripts.civitai_manager_libs.recipe_browser_page.on_ui", dummy_on_ui)
    browser = RecipeBrowser()
    ui, trigger = browser.create_browser_ui()
    assert ui == "ui_component"
    assert trigger == "refresh_trigger"


def test_recipe_browser_refresh_search_and_filter(monkeypatch):
    # Prepare dummy recipe list provider
    calls = {}

    def dummy_get_list(**kwargs):
        calls.update(kwargs)
        return ["r1", "r2"]

    monkeypatch.setattr("scripts.civitai_manager_libs.recipe.get_list", dummy_get_list)
    browser = RecipeBrowser()
    # refresh with search term
    result = browser.refresh_recipe_list(search_term="foo")
    assert result == ["r1", "r2"]
    assert calls.get("search") == "foo"
    # search_recipes uses same provider
    result2 = browser.search_recipes(query="bar")
    assert result2 == ["r1", "r2"]
    assert calls.get("search") == "bar"
    # filter_recipes sets custom criteria
    calls.clear()
    filt = browser.filter_recipes(filter_type="type", filter_value="val")
    assert filt == ["r1", "r2"]
    assert calls.get("type") == "val"


def test_recipe_browser_sort_and_handle_selection(monkeypatch):
    # Dummy list for sorting
    def dummy_list(**_):
        return [
            {"name": "a", "order": 2},
            {"name": "b", "order": 1},
        ]

    monkeypatch.setattr("scripts.civitai_manager_libs.recipe.get_list", dummy_list)
    browser = RecipeBrowser()
    # sort descending
    sorted_desc = browser.sort_recipes(sort_by="order", ascending=False)
    assert sorted_desc[0]["order"] == 2
    # sort ascending
    sorted_asc = browser.sort_recipes(sort_by="order", ascending=True)
    assert sorted_asc[0]["order"] == 1
    # sort with invalid key logs warning and returns original
    # silence logger warning
    monkeypatch.setattr(browser._logger, "warning", lambda *args, **kwargs: None)
    orig = browser.sort_recipes(sort_by="invalid_key")
    assert isinstance(orig, list)

    # handle_recipe_selection returns detailed recipe
    def dummy_get_recipe(rid):
        return {"id": rid}

    monkeypatch.setattr("scripts.civitai_manager_libs.recipe.get_recipe", dummy_get_recipe)
    detail = browser.handle_recipe_selection("xyz")
    assert detail == {"id": "xyz"}
