import os
import sys

# Ensure scripts folder is in path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


import pytest
from civitai_manager_libs.compat.standalone_adapters.standalone_ui_bridge import (
    StandaloneUIBridge,
)


@pytest.fixture()
def bridge():
    return StandaloneUIBridge()


def test_basic_ui_bridge_methods(bridge):
    assert bridge.is_webui_mode() is False
    assert bridge.interrupt_generation() is None
    assert bridge.request_restart() is None
    assert bridge.get_ui_config('x', 'd') == 'd'


def test_save_parameters_for_export(tmp_path, bridge, monkeypatch):
    monkeypatch.chdir(tmp_path)
    text = 'sample parameters'
    bridge._save_parameters_for_export(text)
    txt_file = tmp_path / 'exported_parameters.txt'
    json_file = tmp_path / 'exported_parameters.json'
    assert txt_file.exists()
    assert json_file.exists()


def test_create_send_to_buttons_without_gradio(monkeypatch, bridge):
    # Simulate gradio import failure
    monkeypatch.setitem(sys.modules, 'gradio', None)
    buttons = bridge.create_send_to_buttons(['A', 'B'])
    assert buttons is None
