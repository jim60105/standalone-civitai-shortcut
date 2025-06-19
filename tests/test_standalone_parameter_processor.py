import os
import sys

# Ensure scripts folder is in path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import pytest
from civitai_manager_libs.compat.standalone_adapters.standalone_parameter_processor import (
    StandaloneParameterProcessor,
)


@pytest.fixture()
def spp():
    return StandaloneParameterProcessor()


def test_parse_format_merge_and_validate(spp):
    text = (
        "prompt text\n"
        "Negative prompt: neg_text\n"
        "Steps: 10, Sampler: TestSampler, CFG scale: 5.5, Seed: 42, Size: 100x200, Clip skip: 2"
    )
    result = spp.parse_parameters(text)
    assert result['prompt'] == 'prompt text'
    assert result['negative_prompt'] == 'neg_text'
    assert result['steps'] == 10
    assert result['sampler_name'] == 'TestSampler'
    assert result['cfg_scale'] == 5.5
    assert result['seed'] == 42
    assert result['size']['width'] == 100 and result['size']['height'] == 200
    assert result['clip_skip'] == 2

    formatted = spp.format_parameters(result)
    assert 'Negative prompt: neg_text' in formatted
    assert 'Steps: 10' in formatted


    merged = spp.merge_parameters({'a': 1}, {'b': 2})
    assert merged == {'a': 1, 'b': 2}


def test_internal_helpers(spp):
    assert spp._is_parameter_line('Steps: 1')
    assert not spp._is_parameter_line('no params here')
    pairs = spp._split_parameter_line('a:1, b:2, c:3')
    assert ('a', '1') in pairs and ('b', '2') in pairs
    assert spp._normalize_parameter_key('CFG scale') == 'cfg_scale'
    # Keys without mapping: spaces replaced and lowercased
    assert spp._normalize_parameter_key('unknown key') == 'unknown_key'
    assert spp._format_parameter_key('cfg_scale') == 'CFG scale'
    assert spp._format_parameter_key('new_key') == 'New Key'
    assert spp._parse_parameter_value('steps', '5') == 5
    assert spp._parse_parameter_value('cfg_scale', '2.5') == 2.5
    assert spp._parse_parameter_value('size', '10x20') == {'width': 10, 'height': 20}
    assert spp._parse_parameter_value('other', 'val') == 'val'
