from scripts.civitai_manager_libs.scan_action import download_scan_image


import logging


def test_download_scan_image_success(monkeypatch, caplog):
    url = 'http://example.com/img.jpg'
    path = '/tmp/test.jpg'

    class DummyClient:
        def download_file(self, u, p):
            assert u == url and p == path
            return True

    monkeypatch.setattr(
        'scripts.civitai_manager_libs.scan_action.get_http_client', lambda: DummyClient()
    )
    caplog.set_level(logging.DEBUG)
    result = download_scan_image(url, path)
    assert result is True
    log_text = caplog.text
    assert 'Downloading scan image' in log_text
    assert 'Scan image downloaded' in log_text


def test_download_scan_image_failure(monkeypatch, caplog):
    url = 'http://example.com/img.jpg'
    path = '/tmp/test.jpg'

    class DummyClient:
        def download_file(self, u, p):
            return False

    monkeypatch.setattr(
        'scripts.civitai_manager_libs.scan_action.get_http_client', lambda: DummyClient()
    )
    caplog.set_level(logging.DEBUG)
    result = download_scan_image(url, path)
    assert result is False
    log_text = caplog.text
    assert 'Downloading scan image' in log_text
    assert 'Failed to download scan image' in log_text
