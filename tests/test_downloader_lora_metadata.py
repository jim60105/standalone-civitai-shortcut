import pytest
from civitai_manager_libs.download.utilities import _is_lora_model


@pytest.mark.parametrize("model_type", ["lora", "LoCon", "LYCORIS", "LORA"])
def test_is_lora_model_true_variants(model_type):
    vi = {"model": {"type": model_type}}
    assert _is_lora_model(vi) is True


@pytest.mark.parametrize("model_type", ["checkpoint", "text", "", None])
def test_is_lora_model_false_variants(model_type):
    if model_type is None:
        vi = {"model": {}}
    else:
        vi = {"model": {"type": model_type}}
    assert _is_lora_model(vi) is False


def test_is_lora_model_no_model_key():
    assert _is_lora_model({}) is False
