"""
Test interface implementations to ensure they work correctly.

These tests verify that the abstract interfaces can be implemented
and that their methods can be called without causing immediate errors.
"""

import pytest
from typing import Dict, Any, List, Tuple, Optional
from scripts.civitai_manager_libs.compat.interfaces.iconfig_manager import IConfigManager
from scripts.civitai_manager_libs.compat.interfaces.imetadata_processor import IMetadataProcessor
from scripts.civitai_manager_libs.compat.interfaces.iparameter_processor import IParameterProcessor
from scripts.civitai_manager_libs.compat.interfaces.ipath_manager import IPathManager
from scripts.civitai_manager_libs.compat.interfaces.isampler_provider import ISamplerProvider
from scripts.civitai_manager_libs.compat.interfaces.iui_bridge import IUIBridge
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


class DummyConfigManager(IConfigManager):
    """Dummy implementation for testing interface compliance."""

    def get_config(self, key: str, default: Any = None) -> Any:
        return None

    def set_config(self, key: str, value: Any) -> None:
        pass

    def save_config(self) -> bool:
        return True

    def load_config(self) -> bool:
        return True

    def get_all_configs(self) -> Dict[str, Any]:
        return {}

    def has_config(self, key: str) -> bool:
        return False

    def get_model_folders(self) -> Dict[str, str]:
        return {}

    def get_embeddings_dir(self) -> Optional[str]:
        return None

    def get_hypernetwork_dir(self) -> Optional[str]:
        return None

    def get_ckpt_dir(self) -> Optional[str]:
        return None

    def get_lora_dir(self) -> Optional[str]:
        return None


class DummyMetadataProcessor(IMetadataProcessor):
    """Dummy implementation for testing interface compliance."""

    def extract_png_info(
        self, image_path: str
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        return (None, None, None)

    def extract_parameters_from_png(self, image_path: str) -> Optional[str]:
        return None

    def extract_prompt_from_parameters(self, text: str) -> Tuple[str, str]:
        return "", ""

    def format_parameters_for_display(self, params: Dict[str, Any]) -> str:
        return ""

    def parse_generation_parameters(self, text: str) -> Dict[str, Any]:
        return {}


class DummyParameterProcessor(IParameterProcessor):
    """Dummy implementation for testing interface compliance."""

    def parse_parameters(self, text: str) -> Dict[str, Any]:
        return {}

    def format_parameters(self, params: Dict[str, Any]) -> str:
        return ""

    def extract_prompt_and_negative(self, text: str) -> Tuple[str, str]:
        return "", ""

    def merge_parameters(
        self, base_params: Dict[str, Any], override_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {**base_params, **override_params}


class DummyPathManager(IPathManager):
    """Dummy implementation for testing interface compliance."""

    def get_script_path(self) -> str:
        return "/dummy/script"

    def get_user_data_path(self) -> str:
        return "/dummy/data"

    def get_models_path(self) -> str:
        return "/dummy/models"

    def get_model_folder_path(self, model_type: str) -> str:
        return f"/dummy/models/{model_type}"

    def get_config_path(self) -> str:
        return "/dummy/config.json"

    def ensure_directory_exists(self, path: str) -> bool:
        return True

    def validate_path(self, path: str) -> bool:
        return True

    def add_model_folder(self, model_type: str, path: str, save_config: bool = True) -> bool:
        return True

    def get_all_model_paths(self) -> Dict[str, str]:
        return {}


class DummySamplerProvider(ISamplerProvider):
    """Dummy implementation for testing interface compliance."""

    def get_samplers(self) -> List[str]:
        return ["Euler", "Heun"]

    def get_samplers_for_img2img(self) -> List[str]:
        return ["Euler", "Heun"]

    def get_upscale_modes(self) -> List[str]:
        return ["None", "Lanczos"]

    def get_sd_upscalers(self) -> List[str]:
        return ["ESRGAN_4x"]

    def get_all_upscalers(self) -> List[str]:
        return ["None", "Lanczos", "ESRGAN_4x"]

    def is_sampler_available(self, sampler_name: str) -> bool:
        return sampler_name in ["Euler", "Heun"]

    def get_default_sampler(self) -> str:
        return "Euler"


class DummyUIBridge(IUIBridge):
    """Dummy implementation for testing interface compliance."""

    def register_ui_tabs(self, callback) -> None:
        pass

    def create_send_to_buttons(self, targets: List[str]) -> Any:
        return None

    def bind_send_to_buttons(self, buttons, image_component, text_component) -> None:
        pass

    def launch_standalone(self, ui_callback, **kwargs) -> Any:
        return None

    def is_webui_mode(self) -> bool:
        return False

    def interrupt_generation(self) -> None:
        pass

    def request_restart(self) -> None:
        pass

    def get_ui_config(self, key: str, default: Any = None) -> Any:
        return default


def test_iconfig_manager_methods_execute_pass():
    """Test that IConfigManager interface methods can be called."""
    dm = DummyConfigManager()
    assert dm.get_config('x') is None
    dm.set_config('x', 1)
    assert dm.save_config() is True
    assert dm.load_config() is True
    assert isinstance(dm.get_all_configs(), dict)
    assert dm.has_config('x') is False
    assert isinstance(dm.get_model_folders(), dict)
    assert dm.get_embeddings_dir() is None
    assert dm.get_hypernetwork_dir() is None
    assert dm.get_ckpt_dir() is None
    assert dm.get_lora_dir() is None


def test_imetadata_processor_methods_execute_pass(tmp_path):
    """Test that IMetadataProcessor interface methods can be called."""
    dp = DummyMetadataProcessor()
    result = dp.extract_png_info(str(tmp_path / 'file.png'))
    assert isinstance(result, tuple) and len(result) == 3
    assert dp.extract_parameters_from_png(str(tmp_path / 'file.png')) is None
    pos, neg = dp.extract_prompt_from_parameters('')
    assert isinstance(pos, str) and isinstance(neg, str)
    assert isinstance(dp.format_parameters_for_display({}), str)
    assert isinstance(dp.parse_generation_parameters(''), dict)


def test_iparameter_processor_methods_execute_pass():
    """Test that IParameterProcessor interface methods can be called."""
    dp = DummyParameterProcessor()
    assert isinstance(dp.parse_parameters(''), dict)
    assert isinstance(dp.format_parameters({}), str)
    pos, neg = dp.extract_prompt_and_negative('')
    assert isinstance(pos, str) and isinstance(neg, str)
    assert isinstance(dp.merge_parameters({}, {}), dict)


def test_ipath_manager_methods_execute_pass(tmp_path):
    """Test that IPathManager interface methods can be called."""
    pm = DummyPathManager()
    assert isinstance(pm.get_script_path(), str)
    assert isinstance(pm.get_user_data_path(), str)
    assert isinstance(pm.get_models_path(), str)
    assert isinstance(pm.get_model_folder_path('Lora'), str)
    assert isinstance(pm.get_config_path(), str)
    assert pm.ensure_directory_exists(str(tmp_path)) is True
    assert pm.validate_path(str(tmp_path)) is True
    assert pm.add_model_folder('Test', str(tmp_path)) is True
    assert isinstance(pm.get_all_model_paths(), dict)


def test_isampler_provider_methods_execute_pass():
    """Test that ISamplerProvider interface methods can be called."""
    sp = DummySamplerProvider()
    assert isinstance(sp.get_samplers(), list)
    assert isinstance(sp.get_samplers_for_img2img(), list)
    assert isinstance(sp.get_upscale_modes(), list)
    assert isinstance(sp.get_sd_upscalers(), list)
    assert isinstance(sp.get_all_upscalers(), list)
    assert isinstance(sp.is_sampler_available('Euler'), bool)
    assert isinstance(sp.get_default_sampler(), str)


def test_iui_bridge_methods_execute_pass():
    """Test that IUIBridge interface methods can be called."""
    ub = DummyUIBridge()
    ub.register_ui_tabs(lambda: None)
    result = ub.create_send_to_buttons([])
    assert result is None
    ub.bind_send_to_buttons(None, None, None)
    result = ub.launch_standalone(lambda: None)
    assert result is None
    assert ub.is_webui_mode() is False


def test_iconfig_manager_not_implemented():
    with pytest.raises(TypeError):
        IConfigManager()


def test_imetadata_processor_not_implemented():
    with pytest.raises(TypeError):
        IMetadataProcessor()


def test_iparameter_processor_not_implemented():
    with pytest.raises(TypeError):
        IParameterProcessor()


def test_ipath_manager_not_implemented():
    with pytest.raises(TypeError):
        IPathManager()


def test_isampler_provider_not_implemented():
    with pytest.raises(TypeError):
        ISamplerProvider()


def test_iui_bridge_not_implemented():
    with pytest.raises(TypeError):
        IUIBridge()
