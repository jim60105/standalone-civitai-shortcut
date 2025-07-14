import threading

import pytest

from scripts.civitai_manager_libs.http.client_manager import (
    get_http_client,
    _create_new_http_client,
    _update_client_configuration,
    CompleteCivitaiHttpClient,
)
from scripts.civitai_manager_libs import settings
from scripts.civitai_manager_libs.settings import config_manager


def test_create_new_http_client_defaults(monkeypatch):
    # set settings
    monkeypatch.setattr(settings, 'civitai_api_key', 'key0')
    monkeypatch.setattr(settings, 'http_timeout', 10)
    monkeypatch.setattr(settings, 'http_max_retries', 2)
    monkeypatch.setattr(settings, 'http_retry_delay', 0.5)
    client = _create_new_http_client()
    assert isinstance(client, CompleteCivitaiHttpClient)
    assert client.api_key == 'key0'
    assert client.timeout == 10
    assert client.max_retries == 2
    assert client.retry_delay == 0.5


def test_get_http_client_singleton_and_update(monkeypatch):
    # reset global
    # Call first time
    client1 = get_http_client()
    client1.api_key = 'old'
    # change settings for update
    monkeypatch.setattr(settings, 'civitai_api_key', 'newkey')
    monkeypatch.setattr(config_manager, 'get_setting', lambda k: 'newkey')
    # calling get_http_client again should update existing
    client2 = get_http_client()
    assert client1 is client2
    assert client1.api_key == 'newkey'


def test_update_client_configuration(monkeypatch):
    client = _create_new_http_client()
    # set new values in settings and config_manager
    monkeypatch.setattr(settings, 'civitai_api_key', 'k2')
    monkeypatch.setattr(settings, 'http_timeout', 20)
    monkeypatch.setattr(settings, 'http_max_retries', 5)
    monkeypatch.setattr(settings, 'http_retry_delay', 1.0)
    monkeypatch.setattr(config_manager, 'get_setting', lambda k: 'k2')
    # call update
    _update_client_configuration(client)
    assert client.api_key == 'k2'
    assert client.timeout == 20
    assert client.max_retries == 5
    assert client.retry_delay == 1.0
