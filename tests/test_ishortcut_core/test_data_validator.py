import os
import json

import pytest

from scripts.civitai_manager_libs.ishortcut_core.data_validator import DataValidator
from scripts.civitai_manager_libs.exceptions import DataValidationError


def test_validate_model_id():
    dv = DataValidator()
    # These should return False due to error handling, not raise exceptions
    assert dv.validate_model_id(None) is False
    assert dv.validate_model_id('') is False
    assert dv.validate_model_id('abc') is False
    assert dv.validate_model_id('1') is True


def test_validate_url():
    dv = DataValidator()
    # These should return False due to error handling, not raise exceptions
    assert dv.validate_url('') is False
    assert dv.validate_url('ftp://example.com') is False
    assert dv.validate_url('http://example.com') is True


def test_validate_file_path(tmp_path):
    dv = DataValidator()
    # These should return False due to error handling, not raise exceptions
    assert dv.validate_file_path('') is False
    assert dv.validate_file_path('a<>') is False
    # Relative path is allowed
    assert dv.validate_file_path('test.txt') is True
    # must_exist assertion
    filepath = tmp_path / 'f.txt'
    assert dv.validate_file_path(str(filepath), must_exist=True) is False


def test_validate_image_and_model_file(tmp_path):
    dv = DataValidator()
    img = tmp_path / 'file.bmp'
    img.write_text('x')
    # These should return False due to error handling, not raise exceptions
    assert dv.validate_image_file(str(img)) is False
    j = tmp_path / 'file.jpg'
    j.write_text('x')
    assert dv.validate_image_file(str(j)) is True
    m = tmp_path / 'file.txt'
    m.write_text('x')
    assert dv.validate_model_file(str(m)) is False
    ms = tmp_path / 'file.ckpt'
    ms.write_text('x')
    assert dv.validate_model_file(str(ms)) is True


def test_validate_model_type_and_download_params(tmp_path):
    dv = DataValidator()
    # These should return False due to error handling, not raise exceptions
    assert dv.validate_model_type('') is False
    assert dv.validate_model_type('Checkpoint') is True
    # Download params
    assert dv.validate_download_params({}) is False
    assert dv.validate_download_params({'url': 'http://example.com', 'output_path': ''}) is False
    params = {
        'url': 'http://example.com',
        'output_path': str(tmp_path / 'out.txt'),
        'max_retries': 2,
        'timeout': 5,
    }
    assert dv.validate_download_params(params) is True


def test_validate_configuration_and_json_and_consistency(tmp_path):
    dv = DataValidator()
    # These should return False due to error handling, not raise exceptions
    assert dv.validate_configuration([]) is False
    cfg = {
        'shortcut_folder': str(tmp_path),
        'shortcut_thumbnail_folder': str(tmp_path),
        'shortcut_info_folder': str(tmp_path),
        'shortcut_recipe_folder': str(tmp_path),
        'shortcut_max_download_image_per_version': 1,
        'max_description_length': 100,
        'request_timeout': 10,
        'enable_nsfw_filter': True,
        'auto_download_images': False,
        'create_thumbnails': True,
    }
    assert dv.validate_configuration(cfg)
    # JSON data validation
    assert dv.validate_json_data(None) is False
    assert dv.validate_json_data({'a': 1}) is True
    schema = {'type': 'dict', 'required_keys': ['a']}
    assert dv.validate_json_data({'a': 1}, schema) is True
    # Data consistency
    model_info = {'id': 1, 'modelVersions': []}
    file_info = {'model_id': '2', 'versions': []}
    assert not dv.check_data_consistency(model_info, file_info)
    model_info2 = {'id': 2, 'modelVersions': [1]}
    file_info2 = {'model_id': '2', 'versions': [1]}
    assert dv.check_data_consistency(model_info2, file_info2)
