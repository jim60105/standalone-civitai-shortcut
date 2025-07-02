import sys
import types

import pytest

from scripts.civitai_manager_libs.error_handler import with_error_handling, _map_exception_type
from scripts.civitai_manager_libs.exceptions import (
    APIError,
    FileOperationError,
    ValidationError,
    CivitaiShortcutError,
)


class DummyError(BaseException):
    """Dummy gradio Error replacement to capture messages."""

    last_msg = None

    def __init__(self, msg, *args, **kwargs):
        DummyError.last_msg = msg
        super().__init__(msg)


@pytest.fixture(autouse=True)
def fake_gradio_module(monkeypatch):
    fake = types.SimpleNamespace(Error=DummyError)
    monkeypatch.setitem(sys.modules, 'gradio', fake)
    yield
    # cleanup if necessary


def test_with_error_handling_general_exception_fallback():
    import pytest

    @with_error_handling(fallback_value='fallback', exception_types=(Exception,), log_errors=False)
    def func():
        raise Exception('oops')

    with pytest.raises(DummyError) as excinfo:
        func()
    assert 'Exception' in str(excinfo.value)


def test_with_error_handling_api_error_524_status():
    import pytest

    @with_error_handling(fallback_value='fb', exception_types=(APIError,), log_errors=False)
    def func_api():
        raise APIError('timeout occurred', status_code=524)

    DummyError.last_msg = None
    with pytest.raises(DummyError) as excinfo:
        func_api()
    assert 'timeout occurred' in str(excinfo.value)


def test_map_exception_type_mappings():
    # IOError -> FileOperationError
    assert _map_exception_type(IOError('io')) is FileOperationError
    # OSError -> FileOperationError
    assert _map_exception_type(OSError('os')) is FileOperationError
    # Network-related exceptions (requests.RequestException and URLError inherit OSError,
    # so mapped as FileOperationError)
    import requests
    from urllib.error import URLError

    assert _map_exception_type(requests.RequestException('req')) is FileOperationError
    assert _map_exception_type(URLError('url')) is FileOperationError
    # Validation errors
    import json

    assert _map_exception_type(json.JSONDecodeError('msg', doc='', pos=0)) is ValidationError
    assert _map_exception_type(ValueError('val')) is ValidationError

    # Default mapping
    class Other(Exception):
        pass

    assert _map_exception_type(Other('x')) is CivitaiShortcutError
