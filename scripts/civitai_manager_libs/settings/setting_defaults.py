"""Default settings for the application."""

import os

# Project-generated files root directory
SC_DATA_ROOT = "data_sc"
# Stable Diffusion files root directory
SD_DATA_ROOT = "data"

# Default headers for HTTP requests
DEFAULT_HEADERS = {
    'user-agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 '
        'Safari/537.36 Edg/112.0.1722.68'
    ),
    "Authorization": "",
}

# Default values for UI elements
PLACEHOLDER = "[No Select]"
NORESULT = "[No Result]"
NEWRECIPE = "[New Prompt Recipe]"
NEWCLASSIFICATION = "[New Classification]"
CREATE_MODEL_FOLDER = "Create a model folder to download the model"

# Default model extensions
MODEL_EXTENSIONS = (".bin", ".pt", ".safetensors", ".ckpt")

# Default base models for different SD versions
DEFAULT_BASE_MODELS = {
    "SD 1.4": "SD1",
    "SD 1.5": "SD1",
    "SD 2.0": "SD2",
    "SD 2.0 768": "SD2",
    "SD 2.1": "SD2",
    "SD 2.1 768": "SD2",
    "SD 2.1 Unclip": "SD2",
    "SDXL 0.9": "SDXL",
    "SDXL 1.0": "SDXL",
    "SDXL 1.0 LCM": "SDXL",
    "SDXL Distilled": "SDXL",
    "SDXL Turbo": "SDXL",
    "SDXL Lightning": "SDXL",
    "Pony": "Pony",
    "SVD": "SVD",
    "SVD XT": "SVD",
    "Stable Cascade": "SC",
    "Playground V2": "PGV2",
    "PixArt A": "PixArtA",
    "Other": "Unknown",
}

# Default model folders
DEFAULT_MODEL_FOLDERS = {
    'Checkpoint': os.path.join("models", "Stable-diffusion"),
    'LORA': os.path.join("models", "Lora"),
    'LoCon': os.path.join("models", "LyCORIS"),
    'TextualInversion': os.path.join("embeddings"),
    'Hypernetwork': os.path.join("models", "hypernetworks"),
    'AestheticGradient': os.path.join(
        "extensions", "stable-diffusion-webui-aesthetic-gradients", "aesthetic_embeddings"
    ),
    'Controlnet': os.path.join("models", "ControlNet"),
    'Poses': os.path.join("models", "Poses"),
    'Wildcards': os.path.join("extensions", "sd-dynamic-prompts", "wildcards"),
    'Other': os.path.join("models", "Other"),
    'VAE': os.path.join("models", "VAE"),
    'ANLORA': os.path.join("extensions", "sd-webui-additional-networks", "models", "lora"),
    'Unknown': os.path.join("models", "Unknown"),
}

# Default UI type names
DEFAULT_UI_TYPENAMES = {
    "Checkpoint": 'Checkpoint',
    "LoRA": 'LORA',
    "LyCORIS": 'LoCon',
    "Textual Inversion": 'TextualInversion',
    "Hypernetwork": 'Hypernetwork',
    "Aesthetic Gradient": 'AestheticGradient',
    "Controlnet": 'Controlnet',
    "Poses": 'Poses',
    "Wildcards": 'Wildcards',
    "Other": 'Other',
}

# Default tab indices
DEFAULT_CIVITAI_INFORMATION_TAB = 0
DEFAULT_USERGAL_INFORMATION_TAB = 1
DEFAULT_DOWNLOAD_INFORMATION_TAB = 2

# Default file extensions for Civitai Helper compatibility
INFO_EXT = ".info"
INFO_SUFFIX = ".civitai"
TRIGER_EXT = ".txt"
TRIGER_SUFFIX = ".triger"
PREVIEW_IMAGE_EXT = ".png"
PREVIEW_IMAGE_SUFFIX = ".preview"


class SettingDefaults:
    """Manages default settings for the application."""

    # UI DEFAULTS
    UI_DEFAULTS = {
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
    }

    # DOWNLOAD DEFAULTS
    DOWNLOAD_DEFAULTS = {
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
    }

    # API DEFAULTS
    API_DEFAULTS = {
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
    }

    # SCANNING DEFAULTS
    SCANNING_DEFAULTS = {
        'scan_timeout': 30,
        'scan_max_retries': 2,
        'preview_image_quality': 85,
    }

    # APPLICATION DEFAULTS
    APPLICATION_DEFAULTS = {
        'shortcut_update_when_start': True,
        'usergallery_preloading': False,
        'NSFW_filtering_enable': True,
        'NSFW_level_user': "None",
    }

    @classmethod
    def get_all_defaults(cls) -> dict:
        """Returns all default settings."""
        return {
            **cls.UI_DEFAULTS,
            **cls.DOWNLOAD_DEFAULTS,
            **cls.API_DEFAULTS,
            **cls.SCANNING_DEFAULTS,
            **cls.APPLICATION_DEFAULTS,
        }

    @classmethod
    def get_category_defaults(cls, category: str) -> dict:
        """Returns default settings for a specific category."""
        if category == 'ui':
            return cls.UI_DEFAULTS
        if category == 'download':
            return cls.DOWNLOAD_DEFAULTS
        if category == 'api':
            return cls.API_DEFAULTS
        if category == 'scanning':
            return cls.SCANNING_DEFAULTS
        if category == 'application':
            return cls.APPLICATION_DEFAULTS
        return {}

    @classmethod
    def get_default_value(cls, key: str) -> any:
        """Returns the default value for a specific setting key."""
        return cls.get_all_defaults().get(key)
