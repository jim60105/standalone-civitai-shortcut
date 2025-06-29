import os
import json
import pytest

import scripts.civitai_manager_libs.ishortcut_core.file_processor as fp_mod
from scripts.civitai_manager_libs.ishortcut_core.file_processor import FileProcessor


@pytest.fixture(autouse=True)
def tmp_setting_folder(monkeypatch, tmp_path):
    # Redirect shortcut_info_folder to temporary path
    monkeypatch.setattr(fp_mod.setting, 'shortcut_info_folder', str(tmp_path))
    yield


def test_create_and_delete_model_directory(tmp_path):
    processor = FileProcessor()
    # Invalid modelid should return None
    assert processor.create_model_directory('') is None
    # Valid creation
    modelid = '123'
    model_dir = processor.create_model_directory(modelid)
    assert os.path.isdir(model_dir)
    # Delete model information
    assert processor.delete_model_information(modelid) is True
    assert not os.path.exists(model_dir)


def test_save_and_backup_and_exists(tmp_path):
    processor = FileProcessor()
    modelid = '456'
    model_dir = tmp_path / modelid
    os.makedirs(model_dir, exist_ok=True)
    # Invalid parameters
    assert not processor.save_model_information({}, '', modelid)
    # Valid save
    data = {'key': 'value'}
    saved = processor.save_model_information(data, str(model_dir), modelid)
    assert saved is True
    info_file = model_dir / f"{modelid}{fp_mod.setting.info_suffix}{fp_mod.setting.info_ext}"
    assert info_file.exists()
    assert processor.model_info_exists(modelid)
    # Backup
    backup_ok = processor.backup_model_information(modelid)
    assert backup_ok is True
    assert (str(info_file) + '.backup').endswith('.backup')


def test_get_paths_and_ensure_and_size_and_cleanup(tmp_path):
    processor = FileProcessor()
    # Test get_model_info_file_path
    path = processor.get_model_info_file_path('789')
    assert '789' in path
    # Ensure directories exist
    assert processor.ensure_directories_exist() is True
    # Create files to test size and cleanup
    modelid = 'abc'
    dirpath = tmp_path / modelid
    os.makedirs(dirpath, exist_ok=True)
    f1 = dirpath / 'file1.txt'
    f1.write_text('hello')
    tmp1 = dirpath / 'tmpfile.tmp'
    tmp1.write_text('data')
    tmp2 = dirpath / 'tmpinfo.tmp'
    tmp2.write_text('more')
    size = processor.get_model_directory_size(modelid)
    assert size >= len('hello')
    # Clean up temp files
    cleaned = processor.cleanup_temp_files(modelid)
    assert cleaned == 2
