import os
import json

import pytest

from scripts.civitai_manager_libs.ishortcut_core.data_validator import DataValidator
from scripts.civitai_manager_libs.exceptions import DataValidationError


def test_validate_model_id():
    dv = DataValidator()
    with pytest.raises(DataValidationError):
        dv.validate_model_id(None)
    with pytest.raises(DataValidationError):
        dv.validate_model_id('')
    with pytest.raises(DataValidationError):
        dv.validate_model_id('abc')
    assert dv.validate_model_id('1')


def test_validate_url():
    dv = DataValidator()
    with pytest.raises(DataValidationError):
        dv.validate_url('')
    with pytest.raises(DataValidationError):
        dv.validate_url('ftp://example.com')
    assert dv.validate_url('http://example.com')


def test_validate_file_path(tmp_path):
    dv = DataValidator()
    with pytest.raises(DataValidationError):
        dv.validate_file_path('')
    with pytest.raises(DataValidationError):
        dv.validate_file_path('a<>')
    # Relative path is allowed
    assert dv.validate_file_path('test.txt')
    # must_exist assertion
    filepath = tmp_path / 'f.txt'
    with pytest.raises(DataValidationError):
        dv.validate_file_path(str(filepath), must_exist=True)


def test_validate_image_and_model_file(tmp_path):
    dv = DataValidator()
    img = tmp_path / 'file.bmp'
    img.write_text('x')
    with pytest.raises(DataValidationError):
        dv.validate_image_file(str(img))
    j = tmp_path / 'file.jpg'
    j.write_text('x')
    assert dv.validate_image_file(str(j))
    m = tmp_path / 'file.txt'
    m.write_text('x')
    with pytest.raises(DataValidationError):
        dv.validate_model_file(str(m))
    ms = tmp_path / 'file.ckpt'
    ms.write_text('x')
    assert dv.validate_model_file(str(ms))


def test_validate_model_type_and_download_params(tmp_path):
    dv = DataValidator()
    with pytest.raises(DataValidationError):
        dv.validate_model_type('')
    assert dv.validate_model_type('Checkpoint')
    # Download params
    with pytest.raises(DataValidationError):
        dv.validate_download_params({})
    with pytest.raises(DataValidationError):
        dv.validate_download_params({'url': 'http://example.com', 'output_path': ''})
    params = {
        'url': 'http://example.com',
        'output_path': str(tmp_path / 'out.txt'),
        'max_retries': 2,
        'timeout': 5,
    }
    assert dv.validate_download_params(params)


def test_validate_configuration_and_json_and_consistency(tmp_path):
    dv = DataValidator()
    with pytest.raises(DataValidationError):
        dv.validate_configuration([])
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
    assert not dv.validate_json_data(None)
    assert dv.validate_json_data({'a': 1})
    schema = {'type': 'dict', 'required_keys': ['a']}
    assert dv.validate_json_data({'a': 1}, schema)
    # Data consistency
    assert not dv.check_data_consistency({'id': 1, 'modelVersions': []}, {'model_id': '2', 'versions': []})
    assert dv.check_data_consistency({'id': 2, 'modelVersions': [1]}, {'model_id': '2', 'versions': [1]})
