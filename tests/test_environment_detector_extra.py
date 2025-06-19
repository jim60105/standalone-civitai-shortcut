"""
Additional tests for EnvironmentDetector to cover marker detection,
cache management, and environment info reporting.
"""
import os
import sys
import types
import importlib

import pytest

from scripts.civitai_manager_libs.compat.environment_detector import EnvironmentDetector


@pytest.fixture(autouse=True)
def reset_env_detector():
    # Ensure cache and any fake modules are reset before each test
    for key in ('modules', 'modules.scripts', 'modules.shared'):
        sys.modules.pop(key, None)
    EnvironmentDetector.reset_cache()
    yield
    EnvironmentDetector.reset_cache()
    for key in ('modules', 'modules.scripts', 'modules.shared'):
        sys.modules.pop(key, None)


def test_force_and_reset_cache():
    # Force to webui and verify cache
    EnvironmentDetector.force_environment('webui')
    assert EnvironmentDetector.detect_environment() == 'webui'
    # Reset should clear the cache
    EnvironmentDetector.reset_cache()
    assert EnvironmentDetector._cached_environment is None


def test_is_mode_helpers():
    EnvironmentDetector.force_environment('webui')
    assert EnvironmentDetector.is_webui_mode() is True
    assert EnvironmentDetector.is_standalone_mode() is False
    EnvironmentDetector.reset_cache()
    EnvironmentDetector.force_environment('standalone')
    assert EnvironmentDetector.is_standalone_mode() is True


def test_get_environment_info_standalone(tmp_path, monkeypatch):
    # In standalone mode, info should not include webui keys
    monkeypatch.chdir(tmp_path)
    info = EnvironmentDetector.get_environment_info()
    assert info['environment'] == 'standalone'
    assert 'python_version' in info
    assert 'working_directory' in info
    assert 'python_path' in info
    assert 'webui_base_dir' not in info
    assert 'webui_cmd_opts' not in info


@pytest.mark.parametrize('marker', ['webui.py', 'launch.py'])
def test_detect_marker_files(marker, tmp_path, monkeypatch):
    # Create marker file in current directory
    file_path = tmp_path / marker
    file_path.write_text('# marker')
    monkeypatch.chdir(tmp_path)
    assert EnvironmentDetector.detect_environment() == 'webui'


def test_detect_marker_extensions_dir(tmp_path, monkeypatch):
    # Create extensions directory marker
    (tmp_path / 'extensions').mkdir()
    monkeypatch.chdir(tmp_path)
    assert EnvironmentDetector.detect_environment() == 'webui'


def test_detect_marker_env_var(tmp_path, monkeypatch):
    # Use environment variable marker
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('WEBUI_MODE', '1')
    assert EnvironmentDetector.detect_environment() == 'webui'

def test_detect_with_modules_scripts(tmp_path, monkeypatch):
    # Simulate AUTOMATIC1111 WebUI environment via modules.scripts.basedir
    fake_scripts = type(sys)('modules.scripts')
    fake_shared = type(sys)('modules.shared')
    # basedir returns existing directory
    fake_scripts.basedir = lambda: str(tmp_path)
    # shared.cmd_opts exists
    fake_shared.cmd_opts = 'dummy_opts'
    # Inject fake modules package and submodules
    fake_pkg = types.ModuleType('modules')
    fake_pkg.__path__ = ['']
    monkeypatch.setitem(sys.modules, 'modules', fake_pkg)
    monkeypatch.setitem(sys.modules, 'modules.scripts', fake_scripts)
    monkeypatch.setitem(sys.modules, 'modules.shared', fake_shared)
    # Ensure working dir exists
    monkeypatch.chdir(tmp_path)
    # Force environment to webui for info reporting test
    EnvironmentDetector.force_environment('webui')
    info = EnvironmentDetector.get_environment_info()
    assert info['environment'] == 'webui'
    # Should report webui-specific info, even if default values used
    assert 'webui_base_dir' in info
    assert 'webui_cmd_opts' in info

def test_detect_modules_scripts_attribute_error(monkeypatch):
    # Simulate modules.scripts present but basedir fails
    fake_scripts = type(sys)('modules.scripts')
    fake_shared = type(sys)('modules.shared')
    fake_scripts.basedir = lambda: (_ for _ in ()).throw(AttributeError())
    fake_shared.cmd_opts = None
    fake_pkg = types.ModuleType('modules')
    fake_pkg.__path__ = ['']
    monkeypatch.setitem(sys.modules, 'modules', fake_pkg)
    monkeypatch.setitem(sys.modules, 'modules.scripts', fake_scripts)
    monkeypatch.setitem(sys.modules, 'modules.shared', fake_shared)
    # No markers or env var
    monkeypatch.delenv('WEBUI_MODE', raising=False)
    # Should fall through to standalone
    assert EnvironmentDetector.detect_environment() == 'standalone'
