import os
import datetime
from types import SimpleNamespace

import pytest

from scripts.civitai_manager_libs import gallery as civitai_gallery_action
from scripts.civitai_manager_libs import settings
from scripts.civitai_manager_libs.settings import config_manager

# Alias for compatibility
cga = civitai_gallery_action


class DummyClient:
    def __init__(self, fail_urls=None):
        self.fail_urls = set(fail_urls or [])

    def download_file(self, url, path, progress_callback=None):
        if url in self.fail_urls:
            return False
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(b"data")
        return True


@pytest.fixture(autouse=True)
def disable_print(monkeypatch):
    monkeypatch.setattr(civitai_gallery_action.util, "printD", lambda *args, **kwargs: None)


def test_download_single_image_success(tmp_path, monkeypatch):
    url = "http://example.com/img.png"
    dest = tmp_path / "img.png"
    monkeypatch.setattr('scripts.civitai_manager_libs.gallery.download_manager.get_http_client', lambda: DummyClient())
    result = civitai_gallery_action._download_single_image(url, str(dest))
    assert result is True
    assert dest.exists()


def test_download_single_image_failure(tmp_path, monkeypatch):
    url = "http://example.com/img.png"
    dest = tmp_path / "img.png"
    monkeypatch.setattr('scripts.civitai_manager_libs.gallery.download_manager.get_http_client', lambda: DummyClient(fail_urls=[url]))
    result = civitai_gallery_action._download_single_image(url, str(dest))
    assert result is False
    assert not dest.exists()


def test_download_images(tmp_path, monkeypatch):
    urls = ["a", "b", "c"]
    # map urls to files under tmp_path
    monkeypatch.setattr(
        settings, "get_image_url_to_gallery_file", lambda u: str(tmp_path / f"{u}.png")
    )
    # fail url 'b'
    monkeypatch.setattr('scripts.civitai_manager_libs.gallery.download_manager.get_http_client', lambda: DummyClient(fail_urls=["b"]))
    # disable UI error
    monkeypatch.setattr('scripts.civitai_manager_libs.gallery.download_manager.gr.Error', lambda *args, **kwargs: None)
    civitai_gallery_action.download_images(urls)
    assert (tmp_path / "a.png").exists()
    assert not (tmp_path / "b.png").exists()
    assert (tmp_path / "c.png").exists()


def test_gallery_loading(tmp_path, monkeypatch):
    urls = ["u1", "u2"]
    # configure gallery folder
    monkeypatch.setattr(settings, "shortcut_gallery_folder", str(tmp_path))
    monkeypatch.setattr(settings, "get_no_card_preview_image", lambda: "no.png")
    monkeypatch.setattr(
        settings, "get_image_url_to_gallery_file", lambda u: str(tmp_path / f"{u}.png")
    )
    monkeypatch.setattr(civitai_gallery_action.util, "is_url_or_filepath", lambda u: "url")
    monkeypatch.setattr(civitai_gallery_action, "_download_single_image", lambda u, p: False)
    progress = SimpleNamespace(tqdm=lambda iterable, desc=None: iterable)
    dn_list, img_list, now = civitai_gallery_action.gallery_loading(urls, progress)
    assert dn_list == ["no.png", "no.png"]
    assert img_list == ["no.png", "no.png"]
    assert isinstance(now, datetime.datetime)


def test_download_user_gallery_images(tmp_path, monkeypatch):
    model_id = "123"
    urls = ["u1.png", "u2.png"]
    # stub model info and folder creation
    from scripts.civitai_manager_libs.ishortcut_core.model_processor import ModelProcessor

    monkeypatch.setattr(ModelProcessor, "get_model_info", lambda self, mid: {"name": "modelname"})
    monkeypatch.setattr(civitai_gallery_action.util, "make_download_image_folder", lambda name: str(tmp_path / name))
    monkeypatch.setattr(
        config_manager,
        "get_setting",
        lambda key: "no.png" if key == 'no_card_preview_image' else None,
    )
    monkeypatch.setattr(civitai_gallery_action.util, "is_url_or_filepath", lambda u: "url")
    monkeypatch.setattr(civitai_gallery_action, "_download_single_image", lambda u, p: True)
    result = civitai_gallery_action.download_user_gallery_images(model_id, urls)
    assert result == str(tmp_path / "modelname")
    user_folder = tmp_path / "modelname" / "user_gallery_images"
    assert user_folder.exists()


def test_gallery_download_manager(tmp_path, monkeypatch):
    # stub client with one failing URL
    client = DummyClient(fail_urls=["fail"])
    monkeypatch.setattr('scripts.civitai_manager_libs.gallery.download_manager.get_http_client', lambda: client)
    manager = civitai_gallery_action.GalleryDownloadManager()
    # success case
    success_dest = tmp_path / "ok.png"
    assert manager.download_single_image("ok", str(success_dest))
    assert success_dest.exists()
    # failure case
    fail_dest = tmp_path / "fail.png"
    assert not manager.download_single_image("fail", str(fail_dest))
    assert not fail_dest.exists()
    # test download statistics
    stats = manager.get_download_statistics()
    assert isinstance(stats, dict)


def test_download_images_with_progress(tmp_path, monkeypatch):
    urls = ["x", "y"]
    monkeypatch.setattr(
        settings, "get_image_url_to_gallery_file", lambda u: str(tmp_path / f"{u}.png")
    )
    monkeypatch.setattr('scripts.civitai_manager_libs.gallery.download_manager.get_http_client', lambda: DummyClient())
    calls = []

    def progress_cb(done, total, msg):
        calls.append((done, total, msg))

    civitai_gallery_action.download_images_with_progress(urls, progress_callback=progress_cb)
    assert (tmp_path / "x.png").exists()
    assert (tmp_path / "y.png").exists()
    # At least the final progress update should indicate completion
    assert calls, f"Expected at least one progress update, got {calls}"
    assert calls[-1] == (
        2,
        2,
        "Downloaded 2/2 images",
    ), f"Expected final progress update (Downloaded 2/2 images), got {calls[-1]}"


def test_download_images_batch(tmp_path, monkeypatch):
    urls = [str(i) for i in range(7)]
    monkeypatch.setattr(
        settings, "get_image_url_to_gallery_file", lambda u: str(tmp_path / f"{u}.png")
    )
    monkeypatch.setattr('scripts.civitai_manager_libs.gallery.download_manager.get_http_client', lambda: DummyClient())
    monkeypatch.setattr(civitai_gallery_action.util, "printD", lambda *args, **kwargs: None)
    civitai_gallery_action.download_images_batch(urls, batch_size=3)
    for u in urls:
        assert (tmp_path / f"{u}.png").exists()
