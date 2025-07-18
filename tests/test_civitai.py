import pytest

from scripts.civitai_manager_libs import civitai
from scripts.civitai_manager_libs.settings import config_manager
from scripts.civitai_manager_libs.http.client_manager import _global_http_client


class DummyClient:
    def __init__(self, data=None):
        self.data = data

    def get_json(self, url, params=None):
        return self.data


@pytest.fixture(autouse=True)
def disable_debug_logging(monkeypatch):
    # Since printD has been migrated to logging, we can mock the logger instead
    # or simply disable it if needed for testing
    pass


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
    from scripts.civitai_manager_libs.exceptions import ModelNotFoundError
    import pytest

    with pytest.raises(ModelNotFoundError):
        civitai.get_model_info('1')


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
    global _global_http_client
    _global_http_client = None
    
    # Mock settings that respect categorized structure
    mock_settings = {
        'application_allow': {
            'civitai_api_key': 'key1',
            'http_timeout': 10,
            'http_max_retries': 2
        }
    }
    
    def mock_get_setting(key, default=None):
        # Look for the setting in the proper categorized structure
        for category_name, category_data in mock_settings.items():
            if isinstance(category_data, dict) and key in category_data:
                return category_data[key]
        return default
    
    def mock_set_setting(key, value):
        # Set the setting in the proper categorized structure
        if key in ['civitai_api_key', 'http_timeout', 'http_max_retries']:
            if 'application_allow' not in mock_settings:
                mock_settings['application_allow'] = {}
            mock_settings['application_allow'][key] = value
    
    monkeypatch.setattr(config_manager, "set_setting", mock_set_setting)
    monkeypatch.setattr(config_manager, "get_setting", mock_get_setting)
    
    config_manager.set_setting('civitai_api_key', 'key1')
    config_manager.set_setting('http_timeout', 10)
    config_manager.set_setting('http_max_retries', 2)
    client = civitai.get_http_client()
    assert client.api_key == 'key1'
    assert client.timeout == 10
    assert client.max_retries == 2


def test_get_http_client_api_key_update(monkeypatch):
    # Existing client updates api_key when settings changes
    global _global_http_client
    _global_http_client = None
    
    # Mock settings that respect categorized structure
    mock_settings = {
        'application_allow': {}
    }
    
    def mock_get_setting(key, default=None):
        # Look for the setting in the proper categorized structure
        for category_name, category_data in mock_settings.items():
            if isinstance(category_data, dict) and key in category_data:
                return category_data[key]
        return default
    
    def mock_set_setting(key, value):
        # Set the setting in the proper categorized structure
        if key in ['civitai_api_key', 'http_timeout', 'http_max_retries']:
            if 'application_allow' not in mock_settings:
                mock_settings['application_allow'] = {}
            mock_settings['application_allow'][key] = value
    
    monkeypatch.setattr(config_manager, "set_setting", mock_set_setting)
    monkeypatch.setattr(config_manager, "get_setting", mock_get_setting)
    
    config_manager.set_setting('civitai_api_key', 'initial')
    client = civitai.get_http_client()
    # Change settings and retrieve again
    config_manager.set_setting('civitai_api_key', 'updated')
    client2 = civitai.get_http_client()
    assert client2 is client
    assert client.api_key == 'updated'
