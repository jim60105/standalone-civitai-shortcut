import pytest

from scripts.civitai_manager_libs.ishortcut_core.model_processor import ModelProcessor


def test_get_model_information_no_modelid():
    processor = ModelProcessor()
    result = processor.get_model_information(None)
    # Expect fallback tuple of None values
    assert isinstance(result, tuple)
    assert all(v is None for v in result)


def test__get_version_info_from_model_empty():
    processor = ModelProcessor()
    # No 'modelVersions' key or empty list should return None
    assert processor._get_version_info_from_model({}) is None
    assert processor._get_version_info_from_model({'modelVersions': []}) is None


def test__get_version_info_from_model_by_criteria():
    processor = ModelProcessor()
    versions = [{'id': 'a'}, {'id': 'b'}, {'id': 'c'}]
    model_info = {'modelVersions': versions}
    # Search by versionid
    assert processor._get_version_info_from_model(model_info, versionid='b') == versions[1]
    # Search by index
    assert processor._get_version_info_from_model(model_info, ver_index=2) == versions[2]


@pytest.fixture(autouse=True)
def patch_civitai_url(monkeypatch):
    # Patch Url_Page to avoid external dependency
    import scripts.civitai_manager_libs.ishortcut_core.model_processor as mp_mod

    monkeypatch.setattr(mp_mod.civitai, 'Url_Page', lambda: 'http://example.com/')
    yield


def test_get_version_description_none():
    processor = ModelProcessor()
    html, trigger, files = processor.get_version_description(None, None)
    assert html == ''
    assert trigger is None
    assert files == []


def test_get_version_description_populated():
    processor = ModelProcessor()
    version_info = {'id': 1, 'modelId': 5, 'name': 'ver', 'baseModel': 'base'}
    model_info = {'type': 'Checkpoint', 'name': 'model', 'creator': {'username': 'user'}}
    html, trigger, files = processor.get_version_description(version_info, model_info)
    # Should include type and model link
    assert '<b>Type' in html
    assert 'http://example.com/' in html
    assert isinstance(files, list)
