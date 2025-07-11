from scripts.civitai_manager_libs.util import should_show_open_folder_buttons
from scripts.civitai_manager_libs import settings

config_manager = settings.config_manager


def test_should_show_open_folder_buttons_in_container(monkeypatch):
    """Test that open folder buttons are hidden in container environment"""
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.util.is_linux_container',
        lambda: {'is_container': True, 'container_type': 'docker'},
    )
    assert should_show_open_folder_buttons() is False


def test_should_show_open_folder_buttons_on_host(monkeypatch):
    """Test that open folder buttons are visible on host environment"""
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.util.is_linux_container', lambda: {'is_container': False}
    )
    assert should_show_open_folder_buttons() is True
