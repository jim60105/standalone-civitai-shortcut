"""Script to run integration tests with proper setup."""

import os
import sys
import pytest
import tempfile
import shutil


def setup_test_environment():
    """Set up test environment."""
    # Create temporary directories
    temp_base = tempfile.mkdtemp(prefix="civitai_integration_test_")

    # Set environment variables for testing
    os.environ["CIVITAI_TEST_MODE"] = "1"
    os.environ["CIVITAI_TEST_TEMP_DIR"] = temp_base

    return temp_base


def cleanup_test_environment(temp_base):
    """Clean up test environment."""
    if os.path.exists(temp_base):
        shutil.rmtree(temp_base)

    # Clean up environment variables
    os.environ.pop("CIVITAI_TEST_MODE", None)
    os.environ.pop("CIVITAI_TEST_TEMP_DIR", None)


def main():
    """Run integration tests."""
    temp_base = setup_test_environment()

    try:
        # Run tests
        test_args = [
            "tests/integration/",
            "-v",
            "--tb=short",
            "--durations=10",
        ]

        result = pytest.main(test_args)
        return result

    finally:
        cleanup_test_environment(temp_base)


if __name__ == "__main__":
    sys.exit(main())
