import pytest

from scripts.civitai_manager_libs.scan_action import get_scan_client, download_scan_image


def test_get_scan_client_returns_client():
    client = get_scan_client()
    # Should have download_file method
    assert hasattr(client, 'download_file')


def test_download_scan_image_success(monkeypatch, capsys):
    url = 'http://example.com/img.jpg'
    path = '/tmp/test.jpg'

    class DummyClient:
        def download_file(self, u, p):
            assert u == url and p == path
            return True

    monkeypatch.setattr(
        'scripts.civitai_manager_libs.scan_action.get_scan_client', lambda: DummyClient()
    )
    result = download_scan_image(url, path)
    assert result is True
    captured = capsys.readouterr()
    assert 'Downloading scan image' in captured.out
    assert 'Scan image downloaded' in captured.out


def test_download_scan_image_failure(monkeypatch, capsys):
    url = 'http://example.com/img.jpg'
    path = '/tmp/test.jpg'

    class DummyClient:
        def download_file(self, u, p):
            return False

    monkeypatch.setattr(
        'scripts.civitai_manager_libs.scan_action.get_scan_client', lambda: DummyClient()
    )
    result = download_scan_image(url, path)
    assert result is False
    captured = capsys.readouterr()
    assert 'Downloading scan image' in captured.out
    assert 'Failed to download scan image' in captured.out
