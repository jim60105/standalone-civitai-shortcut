import os

import pytest

import scripts.civitai_manager_libs.ishortcut_core.model_factory as mf_mod
from scripts.civitai_manager_libs.ishortcut_core.model_factory import ModelFactory


@pytest.fixture(autouse=True)
def tmp_dirs(monkeypatch, tmp_path):
    # Redirect thumbnail folder for ModelFactory operations
    monkeypatch.setattr(mf_mod.setting, 'shortcut_thumbnail_folder', str(tmp_path))
    yield


def test_count_model_images_and_shortcut_object(tmp_path):
    mf = ModelFactory()
    model_info = {'id': '1', 'modelVersions': [
        {'id': 'v1', 'images': ['i1', 'i2']}, {'id': 'v2', 'images': []}
    ]}
    assert mf._count_model_images(model_info) == 2
    # Prepare arguments for _create_shortcut_object
    metadata = {
        'id': '1', 'name': 'n', 'type': 't', 'description': 'd',
        'stats': {}, 'tags': [], 'is_nsfw': False,
        'version_count': 2, 'processed_at': 'now', 'creator': {}
    }
    model_dir = tmp_path / '1'
    model_dir.mkdir()
    info_file = model_dir / '1.json'
    info_file.write_text('{}')
    shortcut = mf._create_shortcut_object(model_info, metadata, str(model_dir))
    assert shortcut['id'] == '1'
    assert os.path.exists(shortcut['info_file'])
    assert isinstance(shortcut['image_count'], int)
    # Invalid inputs should return None
    assert mf._create_shortcut_object({}, metadata, str(tmp_path / 'x')) is None
