"""Manages settings categories and their definitions."""

import os
from .constants import SD_DATA_ROOT


class SettingCategories:
    """Defines and manages settings categories."""

    # UI related settings
    UI_SETTINGS = {
        'shortcut_column': 'integer',
        'shortcut_rows_per_page': 'integer',
        'gallery_column': 'integer',
        'usergallery_images_column': 'integer',
        'usergallery_images_rows_per_page': 'integer',
        'prompt_shortcut_column': 'integer',
        'prompt_shortcut_rows_per_page': 'integer',
        'prompt_reference_shortcut_column': 'integer',
        'prompt_reference_shortcut_rows_per_page': 'integer',
        'classification_shortcut_column': 'integer',
        'classification_shortcut_rows_per_page': 'integer',
        'classification_gallery_column': 'integer',
        'classification_gallery_rows_per_page': 'integer',
        'information_gallery_height': 'string',
        'shortcut_browser_screen_split_ratio': 'integer',
        'shortcut_browser_screen_split_ratio_max': 'integer',
        'shortcut_browser_search_up': 'boolean',
        'gallery_thumbnail_image_style': 'string',
    }

    # Download related settings
    DOWNLOAD_SETTINGS = {
        'download_images_folder': 'string',
        'shortcut_max_download_image_per_version': 'integer',
        'download_timeout': 'integer',
        'download_max_retries': 'integer',
        'download_retry_delay': 'integer',
        'download_chunk_size': 'integer',
        'download_max_concurrent': 'integer',
        'download_resume_enabled': 'boolean',
        'download_verify_checksum': 'boolean',
        'image_download_timeout': 'integer',
        'image_download_max_retries': 'integer',
        'image_download_cache_enabled': 'boolean',
        'image_download_cache_max_age': 'integer',
        'gallery_download_batch_size': 'integer',
        'gallery_download_timeout': 'integer',
        'gallery_max_concurrent_downloads': 'integer',
    }

    # API related settings
    API_SETTINGS = {
        'civitai_api_key': 'string',
        'http_timeout': 'integer',
        'http_max_retries': 'integer',
        'http_retry_delay': 'integer',
        'http_pool_connections': 'integer',
        'http_pool_maxsize': 'integer',
        'http_pool_block': 'boolean',
        'http_enable_chunked_download': 'boolean',
        'http_max_parallel_chunks': 'integer',
        'http_chunk_size': 'integer',
        'http_cache_enabled': 'boolean',
        'http_cache_max_size_mb': 'integer',
        'http_cache_default_ttl': 'integer',
    }

    # Scanning related settings
    SCANNING_SETTINGS = {
        'scan_timeout': 'integer',
        'scan_max_retries': 'integer',
        'preview_image_quality': 'integer',
    }

    # Application related settings
    APPLICATION_SETTINGS = {
        'shortcut_update_when_start': 'boolean',
        'usergallery_preloading': 'boolean',
        'NSFW_filtering_enable': 'boolean',
        'NSFW_level_user': 'string',
    }

    # Default values for each category
    _CATEGORY_DEFAULTS = {
        'ui': {
            'shortcut_column': 5,
            'shortcut_rows_per_page': 4,
            'gallery_column': 7,
            'usergallery_images_column': 6,
            'usergallery_images_rows_per_page': 2,
            'prompt_shortcut_column': 5,
            'prompt_shortcut_rows_per_page': 4,
            'prompt_reference_shortcut_column': 8,
            'prompt_reference_shortcut_rows_per_page': 4,
            'classification_shortcut_column': 5,
            'classification_shortcut_rows_per_page': 4,
            'classification_gallery_column': 8,
            'classification_gallery_rows_per_page': 4,
            'information_gallery_height': "auto",
            'shortcut_browser_screen_split_ratio': 3,
            'shortcut_browser_screen_split_ratio_max': 10,
            'shortcut_browser_search_up': False,
            'gallery_thumbnail_image_style': "scale-down",
        },
        'download': {
            'download_images_folder': os.path.join(SD_DATA_ROOT, "output", "download-images"),
            'shortcut_max_download_image_per_version': 0,
            'download_timeout': 600,
            'download_max_retries': 5,
            'download_retry_delay': 10,
            'download_chunk_size': 8192,
            'download_max_concurrent': 3,
            'download_resume_enabled': True,
            'download_verify_checksum': False,
            'image_download_timeout': 30,
            'image_download_max_retries': 3,
            'image_download_cache_enabled': True,
            'image_download_cache_max_age': 3600,
            'gallery_download_batch_size': 5,
            'gallery_download_timeout': 30,
            'gallery_max_concurrent_downloads': 3,
        },
        'api': {
            'civitai_api_key': "",
            'http_timeout': 60,
            'http_max_retries': 3,
            'http_retry_delay': 2,
            'http_pool_connections': 10,
            'http_pool_maxsize': 20,
            'http_pool_block': False,
            'http_enable_chunked_download': True,
            'http_max_parallel_chunks': 4,
            'http_chunk_size': 1024 * 1024,
            'http_cache_enabled': True,
            'http_cache_max_size_mb': 100,
            'http_cache_default_ttl': 3600,
        },
        'scanning': {
            'scan_timeout': 30,
            'scan_max_retries': 2,
            'preview_image_quality': 85,
        },
        'application': {
            'shortcut_update_when_start': True,
            'usergallery_preloading': False,
            'NSFW_filtering_enable': True,
            'NSFW_level_user': "None",
        },
    }

    # Mapping of logical categories to actual config file categories
    _CONFIG_CATEGORY_MAPPING = {
        'ui': 'image_style',  # UI settings are stored in image_style
        'download': 'application_allow',  # Download settings in application_allow
        'api': 'application_allow',  # API settings in application_allow
        'scanning': 'application_allow',  # Scanning settings in application_allow
        'application': 'application_allow',  # Application settings in application_allow
    }

    # Special key mappings for different nested key names
    _SPECIAL_KEY_MAPPINGS = {
        'NSFW_level_user': ('NSFW_filter', 'nsfw_level'),
        'NSFW_filtering_enable': ('NSFW_filter', 'nsfw_filter_enable'),
        'gallery_thumbnail_image_style': ('screen_style', 'gallery_thumbnail_image_style'),
        'shortcut_browser_screen_split_ratio': (
            'screen_style',
            'shortcut_browser_screen_split_ratio',
        ),
        'information_gallery_height': ('screen_style', 'information_gallery_height'),
        'shortcut_browser_search_up': ('screen_style', 'shortcut_browser_search_up'),
    }

    @classmethod
    def get_all_categories(cls) -> dict:
        """Returns all settings categories."""
        return {
            'ui': cls.UI_SETTINGS,
            'download': cls.DOWNLOAD_SETTINGS,
            'api': cls.API_SETTINGS,
            'scanning': cls.SCANNING_SETTINGS,
            'application': cls.APPLICATION_SETTINGS,
        }

    @classmethod
    def get_category_settings(cls, category: str) -> dict:
        """Returns settings for a specific category."""
        return cls.get_all_categories().get(category, {})

    @classmethod
    def get_setting_type(cls, key: str) -> str:
        """Returns the data type of a specific settings key."""
        for category in cls.get_all_categories().values():
            if key in category:
                return category[key]
        return 'string'  # Default to string if not found

    @classmethod
    def get_category_defaults(cls, category: str) -> dict:
        """Returns default values for a specific category."""
        return cls._CATEGORY_DEFAULTS.get(category, {})

    @classmethod
    def get_all_defaults(cls) -> dict:
        """Returns all default settings."""
        all_defaults = {}
        for defaults in cls._CATEGORY_DEFAULTS.values():
            all_defaults.update(defaults)
        return all_defaults

    @classmethod
    def get_default_value(cls, key: str):
        """Returns the default value for a specific settings key."""
        return cls.get_all_defaults().get(key)

    @classmethod
    def get_config_category_mapping(cls) -> dict:
        """Returns the mapping of logical categories to config file categories."""
        return cls._CONFIG_CATEGORY_MAPPING.copy()

    @classmethod
    def get_special_key_mappings(cls) -> dict:
        """Returns special key mappings for nested settings."""
        return cls._SPECIAL_KEY_MAPPINGS.copy()

    @classmethod
    def find_setting_category(cls, key: str) -> str | None:
        """Finds which category a setting key belongs to."""
        for category_name, settings in cls.get_all_categories().items():
            if key in settings:
                return category_name
        return None

    @classmethod
    def get_validation_range(cls, key: str) -> tuple:
        """Returns validation range for numeric settings."""
        # Define validation ranges for different settings
        validation_ranges = {
            'shortcut_column': (1, 12),
            'shortcut_rows_per_page': (1, 10),
            'gallery_column': (1, 12),
            'http_timeout': (10, 300),
            'http_max_retries': (0, 10),
            'preview_image_quality': (1, 100),
        }
        return validation_ranges.get(key, (None, None))
