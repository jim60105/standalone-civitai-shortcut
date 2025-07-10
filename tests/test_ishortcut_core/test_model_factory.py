from unittest.mock import patch

import pytest

from scripts.civitai_manager_libs.ishortcut_core.model_factory import ModelFactory


class MockGradioProgressWithIndexError:
    """Mock Gradio Progress object that mimics the problematic behavior."""

    def __init__(self):
        self.iterables = []  # Empty list to cause IndexError
        self.call_log = []  # Track progress calls

    def __call__(self, progress, desc=""):
        """Mock progress callback."""
        self.call_log.append((progress, desc))
        return f"Progress: {progress:.1%} - {desc}"

    def __len__(self):
        """This method causes IndexError when called during truthiness evaluation."""
        # This mimics the exact error from Gradio's Progress object
        return self.iterables[-1].length  # IndexError: list index out of range

    def __bool__(self):
        """Override bool to cause the IndexError like Gradio does."""
        # In Gradio, the __bool__ method calls __len__ which causes the error
        return len(self) > 0

    def tqdm(self, iterable=None, **kwargs):
        """Mock tqdm method."""
        return iterable if iterable else []


class MockNormalProgress:
    """Mock normal progress object that works correctly."""

    def __init__(self):
        self.call_log = []

    def __call__(self, progress, desc=""):
        self.call_log.append((progress, desc))
        return f"Progress: {progress:.1%} - {desc}"


@pytest.fixture(autouse=True)
def tmp_dirs(monkeypatch, tmp_path):
    # Redirect thumbnail folder for ImageProcessor operations
    monkeypatch.setattr(
        "scripts.civitai_manager_libs.settings.shortcut_thumbnail_folder", str(tmp_path)
    )
    # Redirect info folder
    monkeypatch.setattr("scripts.civitai_manager_libs.settings.shortcut_info_folder", str(tmp_path))
    # Set image extension
    monkeypatch.setattr("scripts.civitai_manager_libs.settings.preview_image_ext", ".jpg")
    yield


@patch("scripts.civitai_manager_libs.civitai.get_model_info")
def test_create_model_shortcut_api_call_fix(mock_get_model_info, tmp_path):
    """Test that create_model_shortcut calls correct API function and handles response."""
    # Arrange
    model_id = "190092"
    expected_model_info = {
        "id": 190092,
        "name": "Test Model",
        "type": "Checkpoint",
        "description": "A test model for unit testing",
        "creator": {"username": "testuser"},
        "tags": ["test", "example"],
        "nsfw": False,
        "modelVersions": [
            {
                "id": 12345,
                "name": "v1.0",
                "baseModel": "SD1.5",
                "files": [
                    {
                        "name": "model.safetensors",
                        "downloadUrl": "http://test.com/model.safetensors",
                    }
                ],
                "images": [{"url": "http://test.com/preview.jpg"}],
            }
        ],
    }

    mock_get_model_info.return_value = expected_model_info

    # Mock all the required components
    mf = ModelFactory()

    # Create the model directory structure that the factory expects
    model_dir = tmp_path / model_id
    model_dir.mkdir(parents=True, exist_ok=True)

    # Mock the file processor to avoid actual file operations
    with (
        patch.object(mf.file_processor, "create_model_directory", return_value=str(model_dir)),
        patch.object(mf.file_processor, "save_model_information", return_value=True),
        patch.object(mf.image_processor, "extract_version_images", return_value=[]),
        patch.object(mf.image_processor, "download_model_images", return_value=True),
        patch.object(mf.image_processor, "is_sc_image", return_value=True),
        patch.object(mf.image_processor, "get_preview_image_by_model_info", return_value=None),
        patch.object(mf.image_processor, "get_preview_image_url", return_value=None),
    ):

        # Create required info file
        info_file = model_dir / f"{model_id}.json"
        info_file.write_text("{}")

        # Act
        result = mf.create_model_shortcut(model_id, download_images=False, validate_data=True)

    # Assert
    assert result is not None
    assert result["id"] == 190092  # ID should be integer
    assert result["name"] == "Test Model"
    assert result["type"] == "Checkpoint"

    # Verify that the correct API function was called
    mock_get_model_info.assert_called_once_with(model_id)


def test_count_model_images_and_shortcut_object(tmp_path):
    mf = ModelFactory()
    model_info = {
        "id": 1,  # Integer ID
        "modelVersions": [{"id": "v1", "images": ["i1", "i2"]}, {"id": "v2", "images": []}],
    }
    assert mf._count_model_images(model_info) == 2
    # Prepare arguments for _create_shortcut_object
    metadata = {
        "id": 1,  # Integer ID
        "name": "n",
        "type": "t",
        "description": "d",
        "stats": {},
        "tags": [],
        "is_nsfw": False,
        "version_count": 2,
        "processed_at": "now",
        "creator": {},
    }
    model_dir = tmp_path / "1"
    model_dir.mkdir()

    info_file = model_dir / "1.json"
    info_file.write_text("{}")
    shortcut = mf._create_shortcut_object(model_info, metadata, str(model_dir))
    # Test basic functionality
    assert shortcut["id"] == 1  # ID should be integer
    assert isinstance(shortcut["name"], str)
    assert isinstance(shortcut["type"], str)
    assert isinstance(shortcut["tags"], list)
    assert isinstance(shortcut["nsfw"], bool)
    assert "url" in shortcut
    assert "date" in shortcut


@patch('scripts.civitai_manager_libs.civitai.get_model_info')
def test_create_model_shortcut_with_problematic_gradio_progress(mock_get_model_info, tmp_path):
    """
    Test that create_model_shortcut works correctly with a Gradio Progress object
    that has a problematic __len__ method causing IndexError.

    This test ensures we don't regress on the fix for:
    IndexError: list index out of range when evaluating 'if progress:'
    """
    # Arrange
    model_id = "179824"
    expected_model_info = {
        "id": 179824,
        "name": "Test Model with Progress",
        "type": "LORA",
        "description": "Test model for progress object testing",
        "creator": {"username": "testuser"},
        "tags": ["test", "progress"],
        "nsfw": False,
        "modelVersions": [
            {
                "id": 1953893,
                "name": "v1.0",
                "baseModel": "SD1.5",
                "files": [
                    {
                        "name": "model.safetensors",
                        "downloadUrl": "http://test.com/model.safetensors",
                    }
                ],
                "images": [{"url": "http://test.com/preview.jpg"}],
            }
        ],
    }

    mock_get_model_info.return_value = expected_model_info

    # Create a problematic progress object that mimics Gradio's behavior
    problematic_progress = MockGradioProgressWithIndexError()

    # Verify the progress object would cause IndexError with old 'if progress:' check
    with pytest.raises(IndexError, match="list index out of range"):
        bool(problematic_progress)  # This would fail with old implementation

    # Create ModelFactory and mock dependencies
    mf = ModelFactory()
    model_dir = tmp_path / str(model_id)
    model_dir.mkdir(parents=True, exist_ok=True)

    # Mock all the required components to avoid actual file/network operations
    with (
        patch.object(mf.file_processor, 'create_model_directory', return_value=str(model_dir)),
        patch.object(mf.file_processor, 'save_model_information', return_value=True),
        patch.object(mf.image_processor, 'extract_version_images', return_value=[]),
        patch.object(mf.image_processor, 'download_model_images', return_value=True),
        patch.object(mf.image_processor, 'get_preview_image_by_model_info', return_value=None),
        patch.object(mf.image_processor, 'get_preview_image_url', return_value=None),
        patch.object(mf.image_processor, 'download_thumbnail_image', return_value=True),
    ):
        # Act - This should NOT raise IndexError with the fix
        result = mf.create_model_shortcut(
            model_id, progress=problematic_progress, download_images=True, validate_data=True
        )

    # Assert
    assert (
        result is not None
    ), "ModelFactory should successfully create shortcut despite problematic progress object"
    assert result['id'] == 179824
    assert result['name'] == "Test Model with Progress"
    assert result['type'] == "LORA"

    # Verify that progress callbacks were actually called
    assert len(problematic_progress.call_log) > 0, "Progress callbacks should have been called"

    # Verify expected progress steps were called
    progress_descriptions = [desc for _, desc in problematic_progress.call_log]
    expected_steps = [
        "Fetching model information...",
        "Processing metadata...",
        "Creating directories...",
        "Saving model information...",
        "Downloading images...",
        "Generating thumbnail...",
        "Creating shortcut...",
        "Complete!",
    ]

    for expected_step in expected_steps:
        assert (
            expected_step in progress_descriptions
        ), f"Expected progress step '{expected_step}' was not called"

    # Verify API was called correctly
    mock_get_model_info.assert_called_once_with(str(model_id))


@patch('scripts.civitai_manager_libs.civitai.get_model_info')
def test_create_model_shortcut_with_none_progress(mock_get_model_info, tmp_path):
    """Test that create_model_shortcut works correctly when progress=None."""
    # Arrange
    model_id = "123456"
    expected_model_info = {
        "id": 123456,
        "name": "Test Model No Progress",
        "type": "Checkpoint",
        "description": "Test model with no progress",
        "creator": {"username": "testuser"},
        "tags": ["test"],
        "nsfw": False,
        "modelVersions": [
            {
                "id": 1,
                "name": "v1.0",
                "baseModel": "SD1.5",
                "files": [
                    {
                        "name": "model.safetensors",
                        "downloadUrl": "http://test.com/model.safetensors",
                    }
                ],
                "images": [{"url": "http://test.com/preview.jpg"}],
            }
        ],
    }

    mock_get_model_info.return_value = expected_model_info

    # Create ModelFactory
    mf = ModelFactory()
    model_dir = tmp_path / str(model_id)
    model_dir.mkdir(parents=True, exist_ok=True)

    # Mock dependencies
    with (
        patch.object(mf.file_processor, 'create_model_directory', return_value=str(model_dir)),
        patch.object(mf.file_processor, 'save_model_information', return_value=True),
        patch.object(mf.image_processor, 'extract_version_images', return_value=[]),
        patch.object(mf.image_processor, 'download_model_images', return_value=True),
        patch.object(mf.image_processor, 'get_preview_image_by_model_info', return_value=None),
        patch.object(mf.image_processor, 'get_preview_image_url', return_value=None),
        patch.object(mf.image_processor, 'download_thumbnail_image', return_value=True),
    ):
        # Act - Test with progress=None
        result = mf.create_model_shortcut(
            model_id, progress=None, download_images=False, validate_data=True
        )

    # Assert
    assert result is not None
    assert result['id'] == 123456
    assert result['name'] == "Test Model No Progress"


@patch('scripts.civitai_manager_libs.civitai.get_model_info')
def test_create_model_shortcut_with_normal_progress(mock_get_model_info, tmp_path):
    """Test that create_model_shortcut works correctly with a normal progress object."""
    # Arrange
    model_id = "789012"
    expected_model_info = {
        "id": 789012,
        "name": "Test Model Normal Progress",
        "type": "LORA",
        "description": "Test model with normal progress",
        "creator": {"username": "testuser"},
        "tags": ["test"],
        "nsfw": False,
        "modelVersions": [
            {
                "id": 2,
                "name": "v1.0",
                "baseModel": "SD1.5",
                "files": [
                    {
                        "name": "model.safetensors",
                        "downloadUrl": "http://test.com/model.safetensors",
                    }
                ],
                "images": [{"url": "http://test.com/preview.jpg"}],
            }
        ],
    }

    mock_get_model_info.return_value = expected_model_info

    # Create a normal progress object
    normal_progress = MockNormalProgress()

    # Create ModelFactory
    mf = ModelFactory()
    model_dir = tmp_path / str(model_id)
    model_dir.mkdir(parents=True, exist_ok=True)

    # Mock dependencies
    with (
        patch.object(mf.file_processor, 'create_model_directory', return_value=str(model_dir)),
        patch.object(mf.file_processor, 'save_model_information', return_value=True),
        patch.object(mf.image_processor, 'extract_version_images', return_value=[]),
        patch.object(mf.image_processor, 'download_model_images', return_value=True),
        patch.object(mf.image_processor, 'get_preview_image_by_model_info', return_value=None),
        patch.object(mf.image_processor, 'get_preview_image_url', return_value=None),
        patch.object(mf.image_processor, 'download_thumbnail_image', return_value=True),
    ):
        # Act
        result = mf.create_model_shortcut(
            model_id, progress=normal_progress, download_images=True, validate_data=True
        )

    # Assert
    assert result is not None
    assert result['id'] == 789012
    assert result['name'] == "Test Model Normal Progress"

    # Verify that progress callbacks were called
    assert len(normal_progress.call_log) > 0

    # Verify all expected progress steps
    progress_descriptions = [desc for _, desc in normal_progress.call_log]
    expected_steps = [
        "Fetching model information...",
        "Processing metadata...",
        "Creating directories...",
        "Saving model information...",
        "Downloading images...",
        "Generating thumbnail...",
        "Creating shortcut...",
        "Complete!",
    ]

    for expected_step in expected_steps:
        assert expected_step in progress_descriptions


def test_progress_object_edge_cases():
    """Test various edge cases with progress objects to ensure robustness."""

    # Test 1: Progress object that returns None when called
    class NoneReturningProgress:
        def __call__(self, progress, desc=''):
            return None

    progress1 = NoneReturningProgress()

    # Test 2: Progress object with custom attributes
    class CustomProgress:
        def __init__(self):
            self.custom_attr = "test"
            self.call_count = 0

        def __call__(self, progress, desc=''):
            self.call_count += 1
            return f"Custom: {progress}"

    progress2 = CustomProgress()

    # Test 3: Progress object that raises other exceptions
    class ExceptionProgress:
        def __call__(self, progress, desc=''):
            if progress > 0.5:
                raise ValueError("Simulated progress error")
            return "OK"

    progress3 = ExceptionProgress()

    # Verify that 'progress is not None' check works for all these cases
    assert (progress1 is not None) is True
    assert (progress2 is not None) is True
    assert (progress3 is not None) is True

    # Verify they can be called
    assert progress1(0.5, "test") is None
    assert progress2(0.5, "test") == "Custom: 0.5"
    assert progress2.call_count == 1

    # Verify exception handling would work in real usage
    try:
        progress3(0.3, "test")
        result_ok = True
    except ValueError:
        result_ok = False
    assert result_ok is True

    try:
        progress3(0.8, "test")
        result_error = False
    except ValueError:
        result_error = True
    assert result_error is True
