import pytest
from unittest.mock import Mock, patch

from scripts.civitai_manager_libs.error_handler import with_error_handling
from scripts.civitai_manager_libs.ui.notification_service import (
    set_notification_service,
    SilentNotificationService,
    ConsoleNotificationService,
)
from scripts.civitai_manager_libs.exceptions import APIError, NetworkError


class TestErrorHandlerUIDecoupling:
    def test_decorator_without_notification_service(self):
        """Test the decorator works properly when no notification service is set."""
        set_notification_service(None)

        @with_error_handling(fallback_value="fallback")
        def failing_function():
            raise ValueError("Test error")

        result = failing_function()
        assert result == "fallback"

    def test_decorator_with_silent_service(self):
        """Test silent notification service usage."""
        silent_service = SilentNotificationService()
        set_notification_service(silent_service)

        @with_error_handling(fallback_value="fallback")
        def failing_function():
            raise ValueError("Test error")

        result = failing_function()
        assert result == "fallback"

    def test_decorator_with_console_service(self):
        """Test console notification service usage."""
        console_service = ConsoleNotificationService()
        set_notification_service(console_service)

        with patch.object(console_service, 'show_error') as mock_show_error:

            @with_error_handling(fallback_value="fallback")
            def failing_function():
                raise ValueError("Test error")

            result = failing_function()
            assert result == "fallback"
            mock_show_error.assert_called_once_with("ValueError")

    def test_cloudflare_524_special_handling_preserved(self):
        """Ensure Cloudflare 524 error special handling is preserved."""
        mock_service = Mock()
        set_notification_service(mock_service)

        @with_error_handling(fallback_value="fallback")
        def failing_function():
            error = APIError("Cloudflare timeout")
            error.status_code = 524
            raise error

        result = failing_function()
        assert result == "fallback"
        mock_service.show_error.assert_called_once_with("Cloudflare timeout")

    def test_existing_usage_patterns_still_work(self):
        """Ensure existing usage patterns still function correctly."""

        @with_error_handling(
            fallback_value=None,
            exception_types=(NetworkError,),
            retry_count=2,
            retry_delay=1.0,
            user_message="Network operation failed",
        )
        def network_operation():
            raise NetworkError("Connection failed")

        result = network_operation()
        assert result is None
