import pytest

from scripts.civitai_manager_libs import civitai


class DummyClient:
    def __init__(self, data=None):
        self.data = data

    def get_json(self, url, params=None):
        return self.data


@pytest.fixture(autouse=True)
def disable_printD(monkeypatch):
    monkeypatch.setattr(civitai.util, "printD", lambda *args, **kwargs: None)


def test_request_models_success(monkeypatch):
    dummy_data = {'items': [1], 'metadata': {'page': 1}}
    monkeypatch.setattr(civitai, 'get_http_client', lambda: DummyClient(data=dummy_data))
    result = civitai.request_models('url')
    assert result == dummy_data


def test_request_models_no_url():
    result = civitai.request_models(None)
    assert result == {'items': [], 'metadata': {}}


def test_request_models_fail(monkeypatch):
    monkeypatch.setattr(civitai, 'get_http_client', lambda: DummyClient(data=None))
    result = civitai.request_models('url')
    assert result == {'items': [], 'metadata': {}}


@pytest.mark.parametrize(
    "func, arg",
    [
        (civitai.get_model_info, '1'),
        (civitai.get_version_info_by_hash, 'hash'),
        (civitai.get_version_info_by_version_id, '2'),
    ],
)
def test_info_functions_invalid_arg(func, arg):
    assert func('') is None


def test_get_model_info_success(monkeypatch):
    data = {'id': 1}
    monkeypatch.setattr(civitai, 'get_http_client', lambda: DummyClient(data=data))
    result = civitai.get_model_info('1')
    assert result == data


def test_get_model_info_fail(monkeypatch):
    monkeypatch.setattr(civitai, 'get_http_client', lambda: DummyClient(data=None))
    assert civitai.get_model_info('1') is None


def test_get_version_info_by_hash_success(monkeypatch):
    data = {'id': 10}
    monkeypatch.setattr(civitai, 'get_http_client', lambda: DummyClient(data=data))
    result = civitai.get_version_info_by_hash('h')
    assert result == data


def test_get_version_info_by_hash_fail(monkeypatch):
    monkeypatch.setattr(civitai, 'get_http_client', lambda: DummyClient(data=None))
    assert civitai.get_version_info_by_hash('h') is None


def test_get_version_info_by_version_id_success(monkeypatch):
    data = {'id': 20}
    monkeypatch.setattr(civitai, 'get_http_client', lambda: DummyClient(data=data))
    result = civitai.get_version_info_by_version_id('2')
    assert result == data


def test_get_version_info_by_version_id_fail(monkeypatch):
    monkeypatch.setattr(civitai, 'get_http_client', lambda: DummyClient(data=None))
    assert civitai.get_version_info_by_version_id('2') is None


def test_get_http_client_initialization(monkeypatch):
    # Reset client and configure settings
    civitai._http_client = None
    monkeypatch.setattr(civitai.setting, 'civitai_api_key', 'key1')
    monkeypatch.setattr(civitai.setting, 'http_timeout', 10)
    monkeypatch.setattr(civitai.setting, 'http_max_retries', 2)
    client = civitai.get_http_client()
    assert client.api_key == 'key1'
    assert client.timeout == 10
    assert client.max_retries == 2


def test_get_http_client_api_key_update(monkeypatch):
    # Existing client updates api_key when setting changes
    civitai._http_client = None
    monkeypatch.setattr(civitai.setting, 'civitai_api_key', 'initial')
    client = civitai.get_http_client()
    # Change setting and retrieve again
    monkeypatch.setattr(civitai.setting, 'civitai_api_key', 'updated')
    client2 = civitai.get_http_client()
    assert client2 is client
    assert client.api_key == 'updated'
