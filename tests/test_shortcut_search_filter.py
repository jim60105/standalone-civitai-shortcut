import pytest
from scripts.civitai_manager_libs.settings import config_manager

from scripts.civitai_manager_libs.ishortcut_core.shortcut_search_filter import (
    ShortcutSearchFilter,
)


class DummyManager:
    def __init__(self, data):
        self._data = data

    def load_shortcuts(self):
        return self._data


class DummyModelProcessor:
    def is_baseModel(self, modelid, baseModels):
        # Return True if modelid is in requested baseModels list
        return modelid in baseModels if baseModels else False


@pytest.fixture
def sample_data():
    return {
        '1': {
            'id': '1',
            'name': 'Alpha',
            'type': 'typeA',
            'tags': ['tag1', 'tag2'],
            'note': 'first note',
        },
        '2': {'id': '2', 'name': 'Beta', 'type': 'typeB', 'tags': [], 'note': ''},
        '3': {'id': '3', 'name': 'Gamma', 'type': 'typeA', 'tags': ['tag2'], 'note': 'second'},
    }


@pytest.fixture
def search_filter(sample_data):
    manager = DummyManager(sample_data)
    model_proc = DummyModelProcessor()
    return ShortcutSearchFilter(manager, model_proc)


def test_get_shortcuts_list(search_filter):
    names = search_filter.get_shortcuts_list()
    assert 'Alpha:1' in names and 'Beta:2' in names and 'Gamma:3' in names


def test_type_filter(search_filter, monkeypatch):
    from scripts.civitai_manager_libs import settings

    # 直接 patch settings.ui_typenames
    settings.ui_typenames = {'X': 'typeA'}
    names = search_filter.get_shortcuts_list(['X'])
    assert names == ['Alpha:1', 'Gamma:3']


def test_keyword_filter(search_filter):
    result = search_filter.get_filtered_shortcuts(search='alpha')
    assert len(result) == 1 and result[0]['id'] == '1'


def test_tag_filter(search_filter):
    result = search_filter.get_filtered_shortcuts(search='#tag2')
    assert {r['id'] for r in result} == {'1', '3'}


def test_note_filter(search_filter):
    result = search_filter.get_filtered_shortcuts(search='@second')
    assert len(result) == 1 and result[0]['id'] == '3'


def test_base_model_filter(search_filter):
    # No match when base_models does not include '3'
    empty = search_filter.get_filtered_shortcuts(base_models=['other'])
    assert empty == []
    # Match only '3'
    result = search_filter.get_filtered_shortcuts(base_models=['3'])
    assert len(result) == 1 and result[0]['id'] == '3'


def test_classification_filter(search_filter, monkeypatch):
    import scripts.civitai_manager_libs.classification as clsmod

    CISC = {'cat': {'shortcuts': ['1', '2']}}
    monkeypatch.setattr(clsmod, 'load', lambda: CISC)
    monkeypatch.setattr(
        clsmod,
        'get_shortcut_list',
        lambda CISC, name: CISC.get(name, {}).get('shortcuts'),
    )
    result = search_filter.get_filtered_shortcuts(classifications=['cat'])
    assert {r['id'] for r in result} == {'1', '2'}


def test_sorting(search_filter, sample_data):
    sorted_by_name = search_filter.sort_shortcuts_by_value(sample_data, 'name')
    assert list(sorted_by_name.keys()) == ['1', '2', '3']
    sorted_by_id = search_filter.sort_shortcuts_by_model_id(sample_data, reverse=True)
    assert list(sorted_by_id.keys()) == ['3', '2', '1']


def test_extract_all_tags(search_filter):
    tags = search_filter.extract_all_tags()
    assert set(tags) == {'tag1', 'tag2'}
