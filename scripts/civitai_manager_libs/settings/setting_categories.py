"""Manages setting categories and their definitions."""


class SettingCategories:
    """Defines and manages setting categories."""

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

    @classmethod
    def get_all_categories(cls) -> dict:
        """Returns all setting categories."""
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
        """Returns the data type of a specific setting key."""
        for category in cls.get_all_categories().values():
            if key in category:
                return category[key]
        return 'string'  # Default to string if not found
