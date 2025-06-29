import re
from datetime import datetime

import pytest

from scripts.civitai_manager_libs.ishortcut_core.metadata_processor import MetadataProcessor
from scripts.civitai_manager_libs.exceptions import DataValidationError


def test_validate_model_info():
    mp = MetadataProcessor()
    # These should return False due to error handling, not raise exceptions
    assert mp.validate_model_info({}) is False
    valid = {'id': 1, 'name': 'n', 'type': 't'}
    assert mp.validate_model_info(valid) is True


def test_validate_model_versions():
    mp = MetadataProcessor()
    # No versions key
    assert mp.validate_model_versions({}) is True
    # Not a list - should return False due to error handling
    assert mp.validate_model_versions({'modelVersions': 'bad'}) is False
    # Empty list
    assert mp.validate_model_versions({'modelVersions': []}) is True
    # Incomplete version - should return False due to error handling
    assert mp.validate_model_versions({'modelVersions': [{'name': 'x'}]}) is False
    # Valid version
    valid_ver = {'id': 2, 'name': 'v', 'downloadUrl': 'u'}
    assert mp.validate_model_versions({'modelVersions': [valid_ver]}) is True
    assert mp.validate_model_versions({'modelVersions': [valid_ver]})


def test_is_nsfw_content_and_tags():
    mp = MetadataProcessor()
    assert mp.is_nsfw_content({'nsfw': True})
    assert mp.is_nsfw_content({'modelVersions': [{'images': [{'nsfw': 'X'}]}]})
    assert mp.is_nsfw_content({'tags': ['nsfw', {'name': 'adult'}]})
    assert not mp.is_nsfw_content({'tags': ['safe']})


def test_clean_and_extract_description_and_parse_timestamp_and_stats_and_tags():
    mp = MetadataProcessor()
    # Clean HTML tags
    assert mp._clean_html_tags('<p>hi</p>') == 'hi'
    # Extract description truncation
    import scripts.civitai_manager_libs.ishortcut_core.metadata_processor as mod
    setattr(mod.setting, 'max_description_length', 5)
    desc = mp.extract_model_description({'description': 'abcdef'})
    assert desc.endswith('...')
    # Parse timestamp formats
    ts1 = '2021-01-01T00:00:00Z'
    assert mp._parse_timestamp(ts1) == datetime.strptime(ts1, '%Y-%m-%dT%H:%M:%SZ').isoformat()
    dt = datetime(2020, 1, 1)
    assert mp._parse_timestamp(dt) == dt.isoformat()
    # Extract stats
    stats = mp.extract_model_stats({
        'downloadCount': 3,
        'thumbsUpCount': 1,
        'commentCount': 2,
        'stats': {'rating': 4.5},
        'createdAt': '2021-01-01T00:00:00Z',
        'updatedAt': '2021-01-02T00:00:00Z',
    })
    assert stats['download_count'] == 3 and stats['rating'] == 4.5
    # Extract tags normalization
    tags = mp.extract_model_tags({'tags': ['A', 'a', {'name': 'B'}]})
    assert sorted(tags) == ['a', 'b']


def test_process_and_validate_processed_metadata():
    mp = MetadataProcessor()
    base = {'id': 1, 'name': 'n', 'type': 't', 'description': '', 'modelVersions': []}
    metadata = mp.process_model_metadata(base)
    assert metadata['id'] == 1
    assert mp.validate_processed_metadata(metadata)
    bad = metadata.copy()
    bad.pop('id')
    assert not mp.validate_processed_metadata(bad)
