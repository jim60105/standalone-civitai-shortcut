from scripts.civitai_manager_libs.exceptions import FileOperationError, NetworkError
from scripts.civitai_manager_libs.recovery import ErrorRecoveryManager


def test_handle_file_operation_error_read(tmp_path, monkeypatch):
    # Prepare file and backup
    filepath = tmp_path / 'test.txt'
    backup_path = tmp_path / 'test.txt.backup'
    filepath.write_text('original')
    backup_path.write_text('backup')

    # Should recover by copying backup over original
    result = ErrorRecoveryManager.handle_file_operation_error(
        FileOperationError('fail'), 'read', str(filepath)
    )
    assert result is True
    assert filepath.read_text() == 'backup'


def test_handle_file_operation_error_write_delete():
    # write and delete operations currently no recovery
    err = FileOperationError('fail')
    assert ErrorRecoveryManager.handle_file_operation_error(err, 'write', 'path') is False
    assert ErrorRecoveryManager.handle_file_operation_error(err, 'delete', 'path') is False
    # unknown operation
    assert ErrorRecoveryManager.handle_file_operation_error(err, 'other', 'path') is False


def test_handle_network_error_no_cache(monkeypatch):
    # Default _get_cached_api_response returns None
    result = ErrorRecoveryManager.handle_network_error(
        NetworkError('netfail'), 'https://api.civitai.com/data', method='POST'
    )
    assert result is None


def test_handle_network_error_with_cache(monkeypatch):
    # Inject cached response
    fake = {'data': 123}
    monkeypatch.setattr(
        ErrorRecoveryManager, '_get_cached_api_response', staticmethod(lambda url: fake)
    )
    result = ErrorRecoveryManager.handle_network_error(
        NetworkError('netfail'), 'https://api.civitai.com/data', method='GET'
    )
    assert result == fake


def test_private_methods_attempts(tmp_path, monkeypatch):
    # _attempt_file_read_recovery returns False when no files exist
    nonexist = tmp_path / 'nofile.txt'
    assert ErrorRecoveryManager._attempt_file_read_recovery(str(nonexist)) is False
    # _attempt_file_write_recovery and delete always False
    assert ErrorRecoveryManager._attempt_file_write_recovery('unused') is False
    assert ErrorRecoveryManager._attempt_file_delete_recovery('unused') is False
    # _get_cached_api_response default
    assert ErrorRecoveryManager._get_cached_api_response('x') is None
