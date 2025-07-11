import pytest

from scripts.civitai_manager_libs import settings
from scripts.civitai_manager_libs.ishortcut_core.shortcut_thumbnail_manager import (
    ShortcutThumbnailManager,
)


class DummyProgress:
    def __init__(self):
        self.tqdm = lambda x, **kw: x


class DummyImageProcessor:
    def download_thumbnail_image(self, mid, url):
        self.called = (mid, url)


class DummyCollectionManager:
    def __init__(self, data):
        self._data = data

    def load_shortcuts(self):
        return self._data

    def save_shortcuts(self, shortcuts):
        self.saved = shortcuts


@pytest.fixture
def sample_images():
    return [
        {'url': 'u1', 'nsfwLevel': 1},
        {'url': 'u2', 'nsfw': 'medium'},
    ]


def test_select_and_level(monkeypatch, sample_images):
    orig = settings.NSFW_LEVELS
    monkeypatch.setattr(settings, 'NSFW_LEVELS', ['low', 'medium', 'high'])
    manager = ShortcutThumbnailManager(DummyImageProcessor(), DummyCollectionManager({}))
    # select optimal based on nsfwLevel
    sel = manager.select_optimal_image(sample_images)
    assert sel == 'u1'
    # unknown nsfw leads to fallback first
    assert manager.select_optimal_image([]) == ''
    # test calculate level
    assert manager._calculate_nsfw_level({'nsfwLevel': 3}) == 2
    lvl2 = manager._calculate_nsfw_level({'nsfw': 'unknown'})
    assert lvl2 == len(settings.NSFW_LEVELS)
    monkeypatch.setattr(settings, 'NSFW_LEVELS', orig)


def test_update_and_batch(monkeypatch):
    # stub civitai and image processor
    from scripts.civitai_manager_libs import civitai

    monkeypatch.setattr(
        civitai,
        'get_latest_version_info_by_model_id',
        lambda mid: {'images': [{'url': 'xu'}]},
    )
    imgp = DummyImageProcessor()
    coll = DummyCollectionManager({'a': {'id': 'a'}})
    manager = ShortcutThumbnailManager(imgp, coll)
    # update all invokes download
    manager.update_all_thumbnails(DummyProgress())
    assert imgp.called == ('a', 'xu')
    # test batch download
    imgp2 = DummyImageProcessor()
    shortcuts = {'b': {'imageurl': 'ub'}}
    ShortcutThumbnailManager(imgp2, coll).batch_download_thumbnails(shortcuts, DummyProgress())
    assert imgp2.called == ('b', 'ub')
