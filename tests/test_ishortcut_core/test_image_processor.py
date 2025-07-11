import pytest
from PIL import Image

import scripts.civitai_manager_libs.ishortcut_core.image_processor as ip_mod
from scripts.civitai_manager_libs.ishortcut_core.image_processor import ImageProcessor
from scripts.civitai_manager_libs.settings import config_manager


@pytest.fixture(autouse=True)
def tmp_thumbnail_folder(monkeypatch, tmp_path):
    # Redirect thumbnail folder to temporary path
    monkeypatch.setattr(
        config_manager,
        "set_setting",
        lambda key, value: config_manager.settings.update({key: value}),
    )
    config_manager.set_setting('shortcut_thumbnail_folder', str(tmp_path))
    config_manager.set_setting('preview_image_ext', '.jpg')
    yield


def test_create_thumbnail_invalid_params(tmp_path):
    from scripts.civitai_manager_libs import settings

    settings.preview_image_ext = '.jpg'
    processor = ImageProcessor(thumbnail_folder=str(tmp_path))
    assert not processor.create_thumbnail('', '')
    assert not processor.create_thumbnail('id', 'nonexistent.jpg')


def test_create_thumbnail_success(tmp_path, monkeypatch):
    from scripts.civitai_manager_libs import settings

    settings.preview_image_ext = '.jpg'
    processor = ImageProcessor(thumbnail_folder=str(tmp_path))
    # Create a sample image
    img_path = tmp_path / 'sample.jpg'
    img = Image.new('RGB', (800, 600), color='blue')
    img.save(str(img_path))
    # Generate thumbnail
    result = processor.create_thumbnail('myid', str(img_path))
    # The thumbnail should be created in the mocked thumbnail folder
    thumb_file = tmp_path / 'myid.jpg'  # This should work with the fixture
    assert result is True
    assert thumb_file.exists()


def test_is_sc_image_and_delete(tmp_path, monkeypatch):
    from scripts.civitai_manager_libs import settings

    settings.preview_image_ext = '.jpg'
    processor = ImageProcessor(thumbnail_folder=str(tmp_path))
    # Empty model_id
    assert not processor.is_sc_image('')
    # Create dummy thumbnail file in the mocked thumbnail folder (tmp_path)
    modelid = 'x'
    thumb_path = tmp_path / f"{modelid}.jpg"
    thumb_path.write_text('data')
    assert processor.is_sc_image(modelid)
    assert processor.delete_thumbnail_image(modelid)
    assert not thumb_path.exists()


def test_get_preview_image_url_and_path_and_extract(tmp_path):
    from scripts.civitai_manager_libs import settings

    settings.preview_image_ext = '.jpg'
    processor = ImageProcessor(thumbnail_folder=str(tmp_path))
    # Preview URL from modelVersions
    model_info = {'id': 1, 'modelVersions': [{'id': 1, 'images': [{'url': 'http://img'}]}]}
    url = processor.get_preview_image_url(model_info)
    assert url == 'http://img'
    # Path generation
    path = processor.get_preview_image_path({'id': 2})
    assert path.endswith('model_2_preview.jpg')
    # Extract version images
    images = [{'url': 'http://test', 'width': 100}]
    version_list = processor._process_version_images(images, 'vid')
    assert version_list == [['vid', 'http://test']]
    model_info2 = {'modelVersions': [{'id': 'vid', 'images': images}, {'id': None}, {}]}
    extracted = processor.extract_version_images(model_info2, 'mid')
    assert isinstance(extracted, list)
