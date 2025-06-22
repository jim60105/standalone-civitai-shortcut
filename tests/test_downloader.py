import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.getcwd())

import pytest

from scripts.civitai_manager_libs.downloader import (
    add_number_to_duplicate_files,
    get_download_client,
)


def test_add_number_to_duplicate_files_basic():
    files = ["1:file.txt", "2:file.txt", "3:other.txt"]
    mapping = add_number_to_duplicate_files(files)
    # Same base name should get a counter suffix
    assert mapping["1"] == "file.txt"
    assert mapping["2"].startswith("file (1)")
    # Unique names unchanged
    assert mapping["3"] == "other.txt"


def test_get_download_client_singleton():
    client1 = get_download_client()
    client2 = get_download_client()
    assert client1 is client2


@pytest.mark.parametrize(
    "files, expected",
    [
        ([], {}),
        (["a.txt"], {}),  # no colon entries
        (["1:img.png", "1:img.png", "2:img.png"], {"1": "img.png", "2": "img (1).png"}),
    ],
)
def test_add_number_parametrized(files, expected):
    result = add_number_to_duplicate_files(files)
    assert result == expected
