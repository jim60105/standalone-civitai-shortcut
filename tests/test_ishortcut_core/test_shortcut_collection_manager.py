import os
import json
import pytest

import scripts.civitai_manager_libs.setting as setting
from scripts.civitai_manager_libs.ishortcut_core.shortcut_collection_manager import (
    ShortcutCollectionManager,
)


class DummyProgress:
    def __init__(self):
        self.tqdm = lambda x, **kwargs: x


@pytest.fixture(autouse=True)
def isolate_settings(tmp_path, monkeypatch):
    # Isolate file paths to temporary directory
    monkeypatch.setattr(setting, 'shortcut', str(tmp_path / 'shortcuts.json'))
    monkeypatch.setattr(
        setting,
        'shortcut_civitai_internet_shortcut_url',
        str(tmp_path / 'shortcut_urls.json'),
    )
    return tmp_path


def test_load_and_save_shortcuts(isolate_settings):
    scm = ShortcutCollectionManager()
    # load when file does not exist
    assert scm.load_shortcuts() == {}
    # save and load data
    data = {'1': {'id': '1', 'name': 'Test'}}
    msg = scm.save_shortcuts(data)
    assert 'Civitai Internet Shortcut saved to:' in msg
    loaded = scm.load_shortcuts()
    assert loaded == data


def test_add_and_get_shortcut(monkeypatch, isolate_settings):
    scm = ShortcutCollectionManager()
    # stub factory to return new entry
    monkeypatch.setattr(
        scm,
        '_model_factory',
        type('F', (), {'create_model_shortcut': lambda self, mid, reg, prog: {mid: {'id': mid}}})(),
    )
    shortcuts = {}
    result = scm.add_shortcut(shortcuts, '123', False, None)
    assert '123' in result and result['123']['id'] == '123'
    # get existing shortcut
    monkeypatch.setattr(scm, 'load_shortcuts', lambda: result)
    assert scm.get_shortcut('123')['id'] == '123'


def test_delete_shortcut_and_backup(monkeypatch, isolate_settings, tmp_path):
    # prepare entry and stub cleanups
    entry = {'id': '9', 'name': 'Name9'}
    shortcuts = {'9': entry.copy()}
    scm = ShortcutCollectionManager()
    monkeypatch.setattr(scm._image_processor, 'delete_thumbnail_image', lambda x: None)
    monkeypatch.setattr(scm._file_processor, 'delete_model_information', lambda x: None)
    # delete and backup URL mapping
    remaining = scm.delete_shortcut(shortcuts.copy(), '9')
    assert '9' not in remaining
    # verify backup file content
    backup_file = os.path.realpath(setting.shortcut_civitai_internet_shortcut_url)
    with open(backup_file, 'r') as f:
        mapping = json.load(f)
    assert any('url=' in k and v == 'Name9' for k, v in mapping.items())


def test_update_and_note(monkeypatch, isolate_settings):
    scm = ShortcutCollectionManager()
    # prepare shortcuts file
    initial = {'5': {'id': '5', 'note': 'old', 'date': '2020-01-01 00:00:00'}}
    scm.save_shortcuts(initial)
    # stub factory create_model_shortcut
    new_data = {'5': {'id': '5'}}
    monkeypatch.setattr(
        scm._model_factory,
        'create_model_shortcut',
        lambda mid, reg, prog: new_data,
    )
    # update keeps note and date
    scm.update_shortcut('5', None)
    updated = scm.load_shortcuts()['5']
    assert updated.get('note') == 'old'
    assert updated.get('date') == '2020-01-01 00:00:00'
    # update note
    scm.update_shortcut_note('5', 'newnote')
    assert scm.get_shortcut_note('5') == 'newnote'


def test_batch_update_and_all(monkeypatch, isolate_settings):
    # stub load and save
    dummy = {'1': {'id': '1'}, '2': {'id': '2'}}
    scm = ShortcutCollectionManager()
    monkeypatch.setattr(scm, 'load_shortcuts', lambda: dummy.copy())
    calls = []
    monkeypatch.setattr(scm, 'update_shortcut', lambda mid, prog: calls.append(mid))
    scm.update_multiple_shortcuts(['1', '2'], DummyProgress())
    assert calls == ['1', '2']
    # update all calls multiple
    calls.clear()
    scm.update_all_shortcuts(DummyProgress())
    assert set(calls) == {'1', '2'}
