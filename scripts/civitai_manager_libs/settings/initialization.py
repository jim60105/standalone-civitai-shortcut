"""Initialization utilities for the application."""

import os

from ..logging_config import get_logger
from ..ui.notification_service import GradioNotificationService, set_notification_service
from .constants import SC_DATA_ROOT
from .path_manager import init_paths, migrate_existing_files, load_model_folder_data

logger = get_logger(__name__)

# Compatibility layer variables
_compat_layer = None


def set_compatibility_layer(compat_layer):
    """Set compatibility layer (called by main program)."""
    global _compat_layer
    logger.info("Setting compatibility layer.")
    _compat_layer = compat_layer
    from .path_manager import initialize_extension_base

    initialize_extension_base()


def init():
    """Initialize application with notification service setup."""
    # Import the global config_manager instance from the settings module
    from .. import settings

    config_manager_instance = settings.config_manager

    set_notification_service(GradioNotificationService())
    from .path_manager import get_extension_base

    logger.info(f"Initializing with extension_base={get_extension_base()}")

    # Ensure data root exists before migration
    ext_base = get_extension_base()
    data_root = os.path.join(ext_base, SC_DATA_ROOT) if ext_base else SC_DATA_ROOT
    try:
        os.makedirs(data_root, exist_ok=True)
    except Exception as e:
        logger.warning(f"Failed to create data_root for migration: {e}")

    migrate_existing_files()
    init_paths(config_manager_instance)
    config_manager_instance.load_settings()
    load_model_folder_data(config_manager_instance)


def set_NSFW(enable, level="None"):
    """Sets NSFW filtering options."""
    from . import config_manager

    config_manager.set_setting('nsfw_filter_enable', enable)
    config_manager.set_setting('nsfw_level', level)


def save_NSFW():
    """Save NSFW settings to the configuration file."""
    from . import config_manager

    return config_manager.save_settings()
