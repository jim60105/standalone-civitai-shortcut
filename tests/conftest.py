"""Pytest configuration and test environment setup."""

import sys
import os

# Ensure the scripts directory is on sys.path for module imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

# Notification service setup for tests (Phase 5.1)
import pytest
from scripts.civitai_manager_libs.ui.notification_service import (
    set_notification_service,
    SilentNotificationService,
    ConsoleNotificationService,
)

@pytest.fixture(autouse=True)
def setup_test_notification_service(request):
    """Set silent notification service for test environment, except for error handler unit tests."""
    # Skip for tests directly validating error_handler behavior
    if request.fspath.basename == "test_error_handler.py":
        yield
        return
    from scripts.civitai_manager_libs.ui.notification_service import get_notification_service
    original_service = get_notification_service()

    set_notification_service(SilentNotificationService())
    yield
    set_notification_service(original_service)

@pytest.fixture
def console_notification():
    """Provide console notification service for tests that inspect notifications."""
    from scripts.civitai_manager_libs.ui.notification_service import get_notification_service
    original_service = get_notification_service()
    console_service = ConsoleNotificationService()
    set_notification_service(console_service)

    yield console_service
    set_notification_service(original_service)
