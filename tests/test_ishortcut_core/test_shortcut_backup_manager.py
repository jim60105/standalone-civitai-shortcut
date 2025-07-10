import os
import json
import datetime
import pytest

from scripts.civitai_manager_libs import settings
from scripts.civitai_manager_libs.ishortcut_core.shortcut_backup_manager import (
    ShortcutBackupManager,
)


@pytest.fixture(autouse=True)
def isolate_backup_dir(tmp_path, monkeypatch):
    # isolate settings to temporary backup directory
    bk = tmp_path / 'backups'
    monkeypatch.setattr(settings, 'shortcut_info_folder', str(bk))
    monkeypatch.setattr(
        settings,
        'shortcut_civitai_internet_shortcut_url',
        str(tmp_path / 'urlmap.json'),
    )
    return tmp_path


def test_backup_shortcut_and_restore(isolate_backup_dir):
    mgr = ShortcutBackupManager()
    # invalid data
    assert not mgr.backup_shortcut({})
    # valid backup
    data = {'id': '7', 'name': 'n'}
    assert mgr.backup_shortcut(data)
    files = os.listdir(settings.shortcut_info_folder)
    assert any(f.startswith('7_') and f.endswith('.json') for f in files)
    # restore latest
    restored = mgr.restore_from_backup('7')
    assert restored.get('id') == '7'


def test_backup_url_mapping_and_list(isolate_backup_dir):
    mgr = ShortcutBackupManager()
    # invalid input
    assert not mgr.backup_url_mapping('', '')
    # valid mapping
    assert mgr.backup_url_mapping('n', 'u')
    # mapping file should contain entry
    mapping = json.load(open(settings.shortcut_civitai_internet_shortcut_url))
    assert mapping.get('url=u') == 'n'
    # list backups returns empty list for no .json files
    assert mgr.get_backup_list() == []


def test_get_backup_list_and_cleanup(isolate_backup_dir, tmp_path):
    mgr = ShortcutBackupManager()
    # prepare backup files
    bdir = settings.shortcut_info_folder
    os.makedirs(bdir, exist_ok=True)
    now = datetime.datetime.now()
    old = now - datetime.timedelta(days=10)
    new_file = os.path.join(bdir, '8_20200101010101.json')
    old_file = os.path.join(bdir, '9_20200101010101.json')
    open(new_file, 'w').close()
    open(old_file, 'w').close()
    # set old file mtime
    os.utime(old_file, (old.timestamp(), old.timestamp()))
    # list returns both
    lst = mgr.get_backup_list()
    assert any(item['model_id'] == '8' for item in lst)
    # cleanup older than 5 days
    removed = mgr.cleanup_old_backups(days_old=5)
    assert removed == 1
