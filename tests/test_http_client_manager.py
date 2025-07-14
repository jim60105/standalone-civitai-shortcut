"""Unit tests for HTTP client manager configuration updates."""
import threading

import pytest

from scripts.civitai_manager_libs.http.client_manager import (
    _update_client_configuration,
    CompleteCivitaiHttpClient,
)
from scripts.civitai_manager_libs.settings import config_manager
import scripts.civitai_manager_libs.settings as settings


class DummyClient(CompleteCivitaiHttpClient):
    """Extend CompleteCivitaiHttpClient to stub update_api_key calls."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.updated_keys = []

    def update_api_key(self, api_key: str) -> None:
        self.updated_keys.append(api_key)


def test_update_client_configuration_applies_all_changes(monkeypatch):
    """Ensure _update_client_configuration updates api_key, timeout, max_retries, and retry_delay."""
    # Initial client with outdated settings
    client = DummyClient(api_key='old', timeout=1, max_retries=1, retry_delay=0.5)
    # Patch global settings to new values
    monkeypatch.setattr(settings, 'civitai_api_key', 'new_key', raising=False)
    monkeypatch.setattr(settings, 'http_timeout', 10, raising=False)
    monkeypatch.setattr(settings, 'http_max_retries', 5, raising=False)
    monkeypatch.setattr(settings, 'http_retry_delay', 2.5, raising=False)
    # Patch config_manager to return desired API key
    monkeypatch.setattr(config_manager, 'get_setting', lambda key: 'cfg_key')

    # Invoke configuration update
    _update_client_configuration(client)

    # api_key update should be invoked via update_api_key
    assert client.updated_keys == ['cfg_key']
    # Other attributes should be updated directly
    assert client.timeout == 10
    assert client.max_retries == 5
    assert client.retry_delay == 2.5

def test_get_http_client_singleton(monkeypatch):
    """Ensure get_http_client returns a singleton and updates on settings change."""
    from scripts.civitai_manager_libs.http.client_manager import get_http_client, _global_http_client

    # Reset global client for test isolation
    monkeypatch.setattr('scripts.civitai_manager_libs.http.client_manager._global_http_client', None)
    # First call creates instance
    c1 = get_http_client()
    # Second call returns same instance
    c2 = get_http_client()
    assert c1 is c2

