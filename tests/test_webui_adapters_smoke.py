import os
import sys

# Ensure scripts folder in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import pytest
import types

from civitai_manager_libs.compat.webui_adapters.webui_config_manager import WebUIConfigManager
from civitai_manager_libs.compat.webui_adapters.webui_path_manager import WebUIPathManager
from civitai_manager_libs.compat.webui_adapters.webui_sampler_provider import WebUISamplerProvider
from civitai_manager_libs.compat.webui_adapters.webui_metadata_processor import (
    WebUIMetadataProcessor,
)
from civitai_manager_libs.compat.webui_adapters.webui_parameter_processor import (
    WebUIParameterProcessor,
)
from civitai_manager_libs.compat.webui_adapters.webui_ui_bridge import WebUIUIBridge


@pytest.fixture(autouse=True)
def patch_webui_modules(monkeypatch, tmp_path):
    # Simulate WebUI modules.scripts and modules.shared(cmd_opts)
    fake_scripts = types.SimpleNamespace(basedir=lambda: str(tmp_path))
    fake_shared = types.SimpleNamespace(
        cmd_opts=types.SimpleNamespace(
            embeddings_dir=str(tmp_path / 'emb'),
            hypernetwork_dir=str(tmp_path / 'hyper'),
            ckpt_dir=str(tmp_path / 'ckpt'),
            lora_dir=str(tmp_path / 'lora'),
        )
    )
    monkeypatch.setitem(sys.modules, 'modules.scripts', fake_scripts)
    monkeypatch.setitem(sys.modules, 'modules.shared', fake_shared)
    # Create paths
    for d in ('emb', 'hyper', 'ckpt', 'lora'):
        os.makedirs(tmp_path / d, exist_ok=True)
    yield


def test_webui_config_manager(tmp_path):
    """Test webui config manager."""
    manager = WebUIConfigManager()
    # Test folder access - just check they're strings
    folders = manager.get_model_folders()
    assert isinstance(folders, dict)
    assert 'TextualInversion' in folders
    assert isinstance(folders['TextualInversion'], str)
    # Test individual dir getters
    emb_dir = manager.get_embeddings_dir()
    assert emb_dir is None or isinstance(emb_dir, str)


def test_webui_path_manager():
    """Test webui path manager."""
    pm = WebUIPathManager()
    script = pm.get_script_path()
    assert isinstance(script, str)
    models = pm.get_models_path()
    assert isinstance(models, str)
    # Test specific model folder path
    lora_path = pm.get_model_folder_path('Lora')
    assert isinstance(lora_path, str)
    folder = pm.get_model_folder_path('Checkpoint')
    assert 'Checkpoint' in folder


def test_webui_sampler_provider():
    """Test webui sampler provider."""
    sp = WebUISamplerProvider()
    samplers = sp.get_samplers()
    assert isinstance(samplers, list)
    if samplers:  # Only test if we have samplers
        assert sp.is_sampler_available(samplers[0]) is True
    upscale_modes = sp.get_upscale_modes()
    assert isinstance(upscale_modes, list)


def test_webui_metadata_and_parameter_processors(tmp_path):
    """Test webui metadata and parameter processors."""
    # Create dummy png for metadata
    png = tmp_path / 'img.png'
    png.write_bytes(b'')
    mp = WebUIMetadataProcessor()
    # Should return None or empty for non-valid PNG
    result = mp.extract_png_info(str(png))
    assert isinstance(result, tuple) and len(result) == 3
    pp = WebUIParameterProcessor()
    params = pp.parse_parameters('Steps: 5, Sampler: Euler')
    assert params.get('steps') == 5
    assert params.get('sampler_name') == 'Euler'


def test_webui_ui_bridge(tmp_path):
    """Test webui ui bridge."""
    ub = WebUIUIBridge()
    assert ub.is_webui_mode() is True
    # create_send_to_buttons may return dict or None
    buttons = ub.create_send_to_buttons(['A'])
    # Should produce a dict with Button or None
    if buttons:
        assert 'A' in buttons
