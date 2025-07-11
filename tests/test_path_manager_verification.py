# flake8: noqa
"""
Test suite for the Path Manager compatibility layer using pytest.
"""

import os
import sys
import pytest

# Add the scripts directory to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from civitai_manager_libs.compat.compat_layer import CompatibilityLayer  # noqa: E402


@pytest.fixture(autouse=True)
def reset_compat():
    """Reset the global compatibility layer before and after each test."""
    CompatibilityLayer.reset_compatibility_layer()
    yield
    CompatibilityLayer.reset_compatibility_layer()


@pytest.fixture
def standalone_compat():
    """Provide a standalone compatibility layer instance."""
    return CompatibilityLayer.get_compatibility_layer("standalone")


def test_path_patterns_and_directory_creation(standalone_compat, tmp_path):
    """Test model folder paths, config path, and directory creation."""
    pm = standalone_compat.path_manager

    # Verify basic paths
    script_path = pm.get_script_path()
    assert isinstance(script_path, str) and script_path

    data_path = pm.get_user_data_path()
    assert isinstance(data_path, str) and data_path

    models_path = pm.get_models_path()
    assert isinstance(models_path, str) and models_path

    # Test model folder paths for standard types
    model_types = [
        "Stable-diffusion",
        "Lora",
        "VAE",
        "embeddings",
        "hypernetworks",
        "ControlNet",
    ]
    for model_type in model_types:
        model_dir = pm.get_model_folder_path(model_type)
        assert model_dir.startswith(
            models_path
        ), f"Model path {model_dir} should be under {models_path}"
        assert os.path.isdir(model_dir)

    # Test config path ends with CivitaiShortCutSetting.json
    config_path = pm.get_config_path()
    assert os.path.basename(config_path) == "CivitaiShortCutSetting.json"

    # Test directory creation on arbitrary temp path
    test_dir = tmp_path / "test_dir"
    created = pm.ensure_directory_exists(str(test_dir))
    assert created and test_dir.is_dir()


def test_path_consistency(standalone_compat):
    """Test that repeated calls to path getters return consistent results."""
    pm = standalone_compat.path_manager

    assert pm.get_script_path() == pm.get_script_path()
    assert pm.get_user_data_path() == pm.get_user_data_path()
    assert pm.get_models_path() == pm.get_models_path()


@pytest.mark.parametrize(
    "model_type",
    [
        "Stable-diffusion",
        "Lora",
        "VAE",
        "embeddings",
        "hypernetworks",
        "ControlNet",
    ],
)
def test_webui_naming_conventions(standalone_compat, model_type):
    """Test that model folder names match expected WebUI conventions."""
    pm = standalone_compat.path_manager
    full_path = pm.get_model_folder_path(model_type)
    assert os.path.basename(full_path) == model_type
