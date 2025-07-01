import json

import pytest

import requests

from scripts.civitai_manager_libs.http_client import CivitaiHttpClient, _STATUS_CODE_MESSAGES
from scripts.civitai_manager_libs.exceptions import AuthenticationError


class DummyResponse:
    def __init__(self, status_code=200, data=None, headers=None, raise_json=False):
        self.status_code = status_code
        self._data = data or {}
        self.headers = headers or {}
        self._raise_json = raise_json

    def json(self):
        if self._raise_json:
            raise json.JSONDecodeError("msg", "doc", 0)
        return self._data

    @property
    def text(self):
        return json.dumps(self._data)

    def iter_content(self, chunk_size=1):
        yield from [b"abc", b"123"]


@pytest.fixture(autouse=True)
def disable_gr_error(monkeypatch):
    # Prevent gradio.Error calls from interfering tests; ignore if gr not in http_client
    try:
        monkeypatch.setattr(
            "scripts.civitai_manager_libs.http_client.gr.Error",
            lambda *args, **kwargs: None,
            raising=False,
        )
    except ImportError:
        pass


def test_get_json_success(monkeypatch):
    client = CivitaiHttpClient()
    dummy = DummyResponse(status_code=200, data={"key": "value"})
    monkeypatch.setattr(client.session, "get", lambda *args, **kwargs: dummy)
    result = client.get_json("http://test")
    assert result == {"key": "value"}


@pytest.mark.parametrize("code", [400, 404, 500])
def test_get_json_http_error(monkeypatch, code):
    client = CivitaiHttpClient()
    dummy = DummyResponse(status_code=code)
    monkeypatch.setattr(client.session, "get", lambda *args, **kwargs: dummy)
    assert client.get_json("http://test") is None


def test_get_json_connection_error(monkeypatch):
    client = CivitaiHttpClient(max_retries=1)

    def raise_conn(*args, **kwargs):
        raise requests.exceptions.ConnectionError

    monkeypatch.setattr(client.session, "get", raise_conn)
    assert client.get_json("http://test") is None


def test_get_json_timeout(monkeypatch):
    client = CivitaiHttpClient(max_retries=1)

    def raise_to(*args, **kwargs):
        raise requests.exceptions.Timeout

    monkeypatch.setattr(client.session, "get", raise_to)
    assert client.get_json("http://test") is None


def test_get_json_json_error(monkeypatch):
    client = CivitaiHttpClient()
    dummy = DummyResponse(status_code=200, data=None, raise_json=True)
    monkeypatch.setattr(client.session, "get", lambda *args, **kwargs: dummy)
    assert client.get_json("http://test") is None


def test_post_json_success(monkeypatch):
    client = CivitaiHttpClient()
    dummy = DummyResponse(status_code=200, data={"ok": True})
    monkeypatch.setattr(client.session, "post", lambda *args, **kwargs: dummy)
    result = client.post_json("http://test", json_data={})
    assert result == {"ok": True}


@pytest.mark.parametrize("code", [401, 503])
def test_post_json_http_error(monkeypatch, code):
    client = CivitaiHttpClient()
    dummy = DummyResponse(status_code=code)
    monkeypatch.setattr(client.session, "post", lambda *args, **kwargs: dummy)
    assert client.post_json("http://test", json_data={}) is None


def test_get_stream_success(monkeypatch):
    client = CivitaiHttpClient()
    dummy = DummyResponse(status_code=200)
    monkeypatch.setattr(client.session, "get", lambda *args, **kwargs: dummy)
    resp = client.get_stream("http://test")
    assert resp is dummy


def test_get_stream_http_error(monkeypatch):
    client = CivitaiHttpClient()
    dummy = DummyResponse(status_code=404)
    monkeypatch.setattr(client.session, "get", lambda *args, **kwargs: dummy)
    assert client.get_stream("http://test") is None


def test_download_file_success(monkeypatch, tmp_path):
    client = CivitaiHttpClient()
    # Mock get_stream to return DummyResponse with headers
    dummy = DummyResponse(status_code=200, headers={"content-length": "6"})
    monkeypatch.setattr(client, "get_stream", lambda url: dummy)
    target = tmp_path / "out.bin"
    called = []

    def prog(downloaded, total):
        called.append((downloaded, total))

    success = client.download_file("http://test", str(target), progress_callback=prog)
    assert success
    assert target.read_bytes() == b"abc123"
    assert called[-1] == (6, 6)


def test_download_file_stream_fail(monkeypatch, tmp_path):
    client = CivitaiHttpClient()
    monkeypatch.setattr(client, "get_stream", lambda url: None)
    target = tmp_path / "out.bin"
    assert not client.download_file("http://test", str(target))


def test_status_code_messages_defined():
    # Ensure the status code mapping is available
    assert isinstance(_STATUS_CODE_MESSAGES, dict)
    # Common HTTP error codes should be present
    for code in (400, 401, 403, 404, 429, 500, 502, 503, 504, 524):
        assert code in _STATUS_CODE_MESSAGES


# Tests for _validate_download_size method
def test_validate_download_size_file_not_exists():
    """Test validation when file doesn't exist."""
    client = CivitaiHttpClient()
    result = client._validate_download_size("/non/existent/file.bin", 1000)
    assert result is False


def test_validate_download_size_unknown_expected_size(tmp_path):
    """Test validation when expected size is unknown (0 or negative)."""
    client = CivitaiHttpClient()
    test_file = tmp_path / "test.bin"
    test_file.write_bytes(b"hello world")

    # Should return True when expected size is 0 or negative
    assert client._validate_download_size(str(test_file), 0) is True
    assert client._validate_download_size(str(test_file), -1) is True


def test_validate_download_size_exact_match(tmp_path):
    """Test validation when file size matches exactly."""
    client = CivitaiHttpClient()
    test_file = tmp_path / "test.bin"
    content = b"hello world"
    test_file.write_bytes(content)

    result = client._validate_download_size(str(test_file), len(content))
    assert result is True


def test_validate_download_size_within_tolerance(tmp_path, monkeypatch):
    """Test validation when file size is within tolerance."""
    client = CivitaiHttpClient()
    test_file = tmp_path / "test.bin"
    content = b"hello world" * 100  # 1100 bytes
    test_file.write_bytes(content)

    # Mock gr.Warning to avoid UI calls
    monkeypatch.setattr(
        "scripts.civitai_manager_libs.http_client.gr.Warning",
        lambda *args, **kwargs: None,
        raising=False,
    )

    # Test within 10% tolerance (default)
    expected_size = 1050  # About 4.8% difference, should pass
    result = client._validate_download_size(str(test_file), expected_size)
    assert result is True


def test_validate_download_size_exceeds_tolerance(tmp_path, monkeypatch):
    """Test validation when file size exceeds tolerance."""
    client = CivitaiHttpClient()
    test_file = tmp_path / "test.bin"
    content = b"hello world" * 100  # 1100 bytes
    test_file.write_bytes(content)

    # Mock notification service to capture warnings instead of UI calls
    warning_called = []

    class DummyService:
        def show_warning(self, message, duration=3):
            warning_called.append((message, duration))

    monkeypatch.setattr(
        "scripts.civitai_manager_libs.http_client.get_notification_service",
        lambda: DummyService(),
        raising=True,
    )

    # Test beyond 10% tolerance
    expected_size = 500  # More than 50% difference, should fail
    result = client._validate_download_size(str(test_file), expected_size)
    assert result is False
    assert len(warning_called) == 1


def test_validate_download_size_custom_tolerance(tmp_path, monkeypatch):
    """Test validation with custom tolerance."""
    client = CivitaiHttpClient()
    test_file = tmp_path / "test.bin"
    content = b"hello world" * 100  # 1100 bytes
    test_file.write_bytes(content)

    # Mock notification service to avoid UI calls in tests
    class DummyService:
        def show_warning(self, message, duration=3):
            pass

    monkeypatch.setattr(
        "scripts.civitai_manager_libs.http_client.get_notification_service",
        lambda: DummyService(),
        raising=True,
    )

    # Test with custom tolerance of 5%
    expected_size = 1050  # About 4.8% difference
    result = client._validate_download_size(str(test_file), expected_size, tolerance=0.05)
    assert result is True

    # Test with custom tolerance of 2%
    result = client._validate_download_size(str(test_file), expected_size, tolerance=0.02)
    assert result is False


# Tests for redirect handling (307 fix)
def test_handle_authentication_error_307_login_redirect():
    """Test that 307 login redirects are handled as authentication errors."""
    client = CivitaiHttpClient()

    # Create mock response with login redirect
    mock_response = DummyResponse(
        status_code=307,
        headers={
            'Location': 'https://civitai.com/login?returnUrl=%2Fmodel-versions%2F1955810&reason=download-auth'  # noqa: E501
        },
    )
    mock_response.url = 'https://civitai.com/api/download/models/1955810'

    result = client._handle_authentication_error(mock_response, "HTTP 307 login redirect")
    assert result is False


def test_handle_authentication_error_416_range_error():
    """Test that 416 range errors are handled as authentication errors."""
    client = CivitaiHttpClient()

    # Create mock response with 416 error
    mock_response = DummyResponse(status_code=416)
    mock_response.url = 'https://civitai.com/api/download/models/1955810'

    result = client._handle_authentication_error(mock_response, "HTTP 416")
    assert result is False


def test_handle_redirect_response_valid_redirect():
    """Test that valid (non-login) redirects are allowed."""
    client = CivitaiHttpClient()

    # Create mock response with valid redirect
    mock_response = DummyResponse(
        status_code=307, headers={'Location': 'https://cdn.civitai.com/files/model123.safetensors'}
    )
    mock_response.url = 'https://civitai.com/api/download/models/1955810'

    result = client._handle_redirect_response(mock_response)
    assert result is True


def test_authentication_error_login_case_insensitive():
    """Test that login detection in 307 redirects is case insensitive."""
    client = CivitaiHttpClient()

    # Test various cases of "login" in URL - should all be handled by _is_stream_response_valid
    test_cases = [
        'https://civitai.com/LOGIN?test=1',
        'https://civitai.com/Login?test=1',
        'https://civitai.com/auth/login',
        'https://test.com/user/LOGIN/page',
    ]

    for location in test_cases:
        mock_response = DummyResponse(status_code=307, headers={'Location': location})
        mock_response.url = 'https://civitai.com/api/download/models/test'

        result = client._is_stream_response_valid(mock_response)
        assert result is False, f"Should detect login redirect for {location}"


def test_is_stream_response_valid_login_redirect():
    """Test stream response validation with login redirect (now authentication error)."""
    client = CivitaiHttpClient()

    mock_response = DummyResponse(
        status_code=307, headers={'Location': 'https://civitai.com/login?test=1'}
    )
    mock_response.url = 'https://test.com'

    result = client._is_stream_response_valid(mock_response)
    assert result is False


def test_is_stream_response_valid_range_error():
    """Test stream response validation with range error (now authentication error)."""
    client = CivitaiHttpClient()

    mock_response = DummyResponse(status_code=416)
    mock_response.url = 'https://test.com'

    result = client._is_stream_response_valid(mock_response)
    assert result is False


def test_is_stream_response_valid_ok_response():
    """Test stream response validation with OK response."""
    client = CivitaiHttpClient()

    mock_response = DummyResponse(status_code=200)

    result = client._is_stream_response_valid(mock_response)
    assert result is True


def test_is_stream_response_valid_general_error():
    """Test stream response validation with general HTTP error."""
    client = CivitaiHttpClient()

    mock_response = DummyResponse(status_code=404)

    result = client._is_stream_response_valid(mock_response)
    assert result is False


def test_get_stream_redirect_handling(monkeypatch):
    """Test that get_stream properly handles redirects."""
    client = CivitaiHttpClient()

    # Mock session.get to return redirect response first, then success
    call_count = [0]

    def mock_get(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            # First call returns redirect
            resp = DummyResponse(
                status_code=307,
                headers={'Location': 'https://cdn.civitai.com/files/model.safetensors'},
            )
            resp.url = 'https://civitai.com/api/download/models/123'
            return resp
        else:
            # Second call returns success
            return DummyResponse(status_code=200)

    monkeypatch.setattr(client.session, "get", mock_get)

    result = client.get_stream("http://test")
    assert result is not None
    assert result.status_code == 200
    assert call_count[0] == 2  # Should have made 2 calls (original + redirect)


def test_get_stream_login_redirect_blocked(monkeypatch):
    """Test that get_stream blocks login redirects."""
    client = CivitaiHttpClient()

    # Mock session.get to return login redirect
    def mock_get(*args, **kwargs):
        resp = DummyResponse(
            status_code=307, headers={'Location': 'https://civitai.com/login?returnUrl=test'}
        )
        resp.url = 'https://civitai.com/api/download/models/123'
        return resp

    monkeypatch.setattr(client.session, "get", mock_get)
    result = client.get_stream("http://test")
    assert result is None  # Should be blocked


def test_error_handling_priority_416_before_307():
    """Test that 416 errors are handled before 307 redirects when both could apply."""
    client = CivitaiHttpClient()

    # Test 416 error is handled first
    mock_response_416 = DummyResponse(status_code=416)
    mock_response_416.url = 'https://test.com'

    result = client._is_stream_response_valid(mock_response_416)
    assert result is False


def test_error_handling_no_api_key_scenarios():
    """Test error messages when no API key is configured."""
    client = CivitaiHttpClient(api_key=None)  # Explicitly no API key

    # Test 307 login redirect without API key
    mock_307 = DummyResponse(
        status_code=307, headers={'Location': 'https://civitai.com/login?returnUrl=test'}
    )
    mock_307.url = 'https://test.com'

    result = client._handle_authentication_error(mock_307, "HTTP 307 login redirect")
    assert result is False

    # Test 416 error without API key
    mock_416 = DummyResponse(status_code=416)
    mock_416.url = 'https://test.com'

    result = client._handle_authentication_error(mock_416, "HTTP 416")
    assert result is False


def test_error_handling_with_api_key_scenarios():
    """Test error messages when API key is configured."""
    client = CivitaiHttpClient(api_key="test_key")

    # Test 307 login redirect with API key (implies key is invalid)
    mock_307 = DummyResponse(
        status_code=307, headers={'Location': 'https://civitai.com/login?returnUrl=test'}
    )
    mock_307.url = 'https://test.com'

    result = client._handle_authentication_error(mock_307, "HTTP 307 login redirect")
    assert result is False

    # Test 416 error with API key (implies insufficient permissions)
    mock_416 = DummyResponse(status_code=416)
    mock_416.url = 'https://test.com'

    result = client._handle_authentication_error(mock_416, "HTTP 416")
    assert result is False


def test_get_stream_allows_416_to_be_handled(monkeypatch):
    """Test that 416 errors are properly handled and not masked by redirect logic."""
    client = CivitaiHttpClient()

    # Mock session.get to return 416 error directly
    def mock_get(*args, **kwargs):
        resp = DummyResponse(status_code=416)
        resp.url = 'https://civitai.com/api/download/models/123'
        return resp

    monkeypatch.setattr(client.session, "get", mock_get)

    result = client.get_stream("http://test")
    assert result is None  # Should be blocked due to 416 error


def test_get_stream_flow_with_different_status_codes(monkeypatch):
    """Test the complete flow with different HTTP status codes."""
    client = CivitaiHttpClient()

    # Test 200 OK
    def mock_get_200(*args, **kwargs):
        return DummyResponse(status_code=200)

    monkeypatch.setattr(client.session, "get", mock_get_200)
    result = client.get_stream("http://test")
    assert result is not None
    assert result.status_code == 200

    # Test 416 error
    def mock_get_416(*args, **kwargs):
        resp = DummyResponse(status_code=416)
        resp.url = 'https://test.com'
        return resp

    monkeypatch.setattr(client.session, "get", mock_get_416)
    result = client.get_stream("http://test")
    assert result is None

    # Test 404 error
    def mock_get_404(*args, **kwargs):
        return DummyResponse(status_code=404)

    monkeypatch.setattr(client.session, "get", mock_get_404)
    result = client.get_stream("http://test")
    assert result is None


def test_authentication_error_exception_from_background_thread():
    """Test that authentication errors throw exceptions when called from background threads."""
    import threading

    client = CivitaiHttpClient()
    results = {"exception": None, "error": None}

    def background_task():
        try:
            # Create mock response with 416 error
            mock_response = DummyResponse(status_code=416)
            mock_response.url = 'https://civitai.com/api/download/models/test'

            # This should throw AuthenticationError in background thread
            client._handle_authentication_error(mock_response, "HTTP 416")
            results["error"] = "Expected AuthenticationError but none was thrown"
        except AuthenticationError as e:
            results["exception"] = e
        except Exception as e:
            results["error"] = f"Unexpected exception: {e}"

    # Run in background thread
    thread = threading.Thread(target=background_task)
    thread.start()
    thread.join()

    # Verify that AuthenticationError was thrown
    assert results["error"] is None, f"Test error: {results['error']}"
    assert results["exception"] is not None, "Expected AuthenticationError was not thrown"
    assert isinstance(results["exception"], AuthenticationError)
    assert results["exception"].status_code == 416
    assert "authentication" in str(results["exception"]).lower()


def test_unified_authentication_error_handling():
    """Test that 307 login redirects and 416 errors are handled consistently."""
    client_no_key = CivitaiHttpClient(api_key=None)
    client_with_key = CivitaiHttpClient(api_key="test_key")

    # Both 307 login redirect and 416 should behave the same
    mock_307 = DummyResponse(
        status_code=307, headers={'Location': 'https://civitai.com/login?test=1'}
    )
    mock_307.url = 'https://test.com'

    mock_416 = DummyResponse(status_code=416)
    mock_416.url = 'https://test.com'

    # Test without API key - both should return False
    result_307_no_key = client_no_key._is_stream_response_valid(mock_307)
    result_416_no_key = client_no_key._is_stream_response_valid(mock_416)
    assert result_307_no_key is False
    assert result_416_no_key is False

    # Test with API key - both should return False
    result_307_with_key = client_with_key._is_stream_response_valid(mock_307)
    result_416_with_key = client_with_key._is_stream_response_valid(mock_416)
    assert result_307_with_key is False
    assert result_416_with_key is False
