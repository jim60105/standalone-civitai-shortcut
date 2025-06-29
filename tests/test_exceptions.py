import time


from scripts.civitai_manager_libs.exceptions import (
    CivitaiShortcutError,
    NetworkError,
    FileOperationError,
    ConfigurationError,
    ValidationError,
    APIError,
)


def test_civitai_shortcut_error_properties():
    cause_exc = ValueError("cause detail")
    err = CivitaiShortcutError("error occurred", context={"key": 123}, cause=cause_exc)
    assert str(err) == "error occurred"
    assert err.context == {"key": 123}
    assert err.cause is cause_exc
    assert isinstance(err.timestamp, float)


def test_exception_subclasses_inheritance():
    # Ensure custom exceptions inherit from base
    for exc_cls in (NetworkError, FileOperationError, ConfigurationError, ValidationError):
        instance = exc_cls("msg")
        assert isinstance(instance, CivitaiShortcutError)


def test_api_error_status_code_and_inheritance():
    api_err = APIError("not found", status_code=404, context={"url": "/test"})
    assert isinstance(api_err, NetworkError)
    assert isinstance(api_err, CivitaiShortcutError)
    assert api_err.status_code == 404
    # Context should be set from kwargs
    assert api_err.context.get("url") == "/test"


def test_timestamp_monotonicity():
    # Timestamps should increase over time
    first = CivitaiShortcutError("first").timestamp
    time.sleep(0.001)
    second = CivitaiShortcutError("second").timestamp
    assert second > first
