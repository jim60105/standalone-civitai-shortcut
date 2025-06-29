"""
Defaults Module

Contains all default values, constants, and configuration presets
used throughout the application.
"""

# Project Information
EXTENSIONS_NAME = "Civitai Shortcut"
EXTENSIONS_VERSION = "v1.6.7"

# Directory Constants
SC_DATA_ROOT = "data_sc"
SD_DATA_ROOT = "data"

# HTTP Client Settings
DEFAULT_HTTP_TIMEOUT = 60  # seconds
DEFAULT_HTTP_MAX_RETRIES = 3
DEFAULT_HTTP_RETRY_DELAY = 2  # seconds
DEFAULT_HEADERS = {
    'user-agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 '
        'Safari/537.36 Edg/112.0.1722.68'
    ),
    "Authorization": "",
}

# Download Settings
DEFAULT_DOWNLOAD_TIMEOUT = 600  # 10 minutes for large files
DEFAULT_DOWNLOAD_MAX_RETRIES = 5
DEFAULT_DOWNLOAD_RETRY_DELAY = 10  # seconds
DEFAULT_DOWNLOAD_CHUNK_SIZE = 8192  # bytes
DEFAULT_DOWNLOAD_MAX_CONCURRENT = 3
DEFAULT_DOWNLOAD_RESUME_ENABLED = True
DEFAULT_DOWNLOAD_VERIFY_CHECKSUM = False

# HTTP Pool Settings
DEFAULT_HTTP_POOL_CONNECTIONS = 10
DEFAULT_HTTP_POOL_MAXSIZE = 20
DEFAULT_HTTP_POOL_BLOCK = False
DEFAULT_HTTP_ENABLE_CHUNKED_DOWNLOAD = True
DEFAULT_HTTP_MAX_PARALLEL_CHUNKS = 4
DEFAULT_HTTP_CHUNK_SIZE = 1024 * 1024  # 1MB

# Cache Settings
DEFAULT_HTTP_CACHE_ENABLED = True
DEFAULT_HTTP_CACHE_MAX_SIZE_MB = 100
DEFAULT_HTTP_CACHE_DEFAULT_TTL = 3600  # 1 hour

# UI Constants
PLACEHOLDER = "[No Select]"
NORESULT = "[No Result]"
NEWRECIPE = "[New Prompt Recipe]"
NEWCLASSIFICATION = "[New Classification]"
CREATE_MODEL_FOLDER = "Create a model folder to download the model"

# File Extensions
MODEL_EXTENSIONS = (".bin", ".pt", ".safetensors", ".ckpt")
INFO_EXT = ".info"
INFO_SUFFIX = ".civitai"
TRIGGER_EXT = ".txt"
TRIGGER_SUFFIX = ".triger"  # Note: keeping original spelling
PREVIEW_IMAGE_EXT = ".png"
PREVIEW_IMAGE_SUFFIX = ".preview"

# Base Models Configuration
MODEL_BASEMODELS = {
    'SD 1.4': 'sd14',
    'SD 1.5': 'sd15',
    'SD 2.0': 'sd20',
    'SD 2.0 768': 'sd20',
    'SD 2.1': 'sd21',
    'SD 2.1 768': 'sd21',
    'SDXL 0.9': 'sdxl09',
    'SDXL 1.0': 'sdxl10',
    'SDXL Turbo': 'sdxlt',
    'SD 3': 'sd3',
    'Other': 'other',
}

# Model Folders Configuration
MODEL_FOLDERS = {
    'Checkpoint': 'checkpoints',
    'TextualInversion': 'embeddings',
    'Hypernetwork': 'hypernetworks',
    'AestheticGradient': 'aesthetic_gradients',
    'LORA': 'lora',
    'LoCon': 'lora',
    'DoRA': 'lora',
    'Controlnet': 'controlnet',
    'Poses': 'poses',
    'Wildcards': 'wildcards',
    'Workflows': 'workflows',
    'Other': 'other',
}

# UI Type Names
UI_TYPENAMES = {
    'Checkpoint': 'Stable Diffusion',
    'TextualInversion': 'Textual Inversion',
    'Hypernetwork': 'Hypernetwork',
    'AestheticGradient': 'Aesthetic Gradient',
    'LORA': 'LoRA',
    'LoCon': 'LyCORIS',
    'DoRA': 'DoRA',
    'Controlnet': 'Controlnet',
    'Poses': 'Poses',
}

# Tab Indices
CIVITAI_INFORMATION_TAB = 0
USERGAL_INFORMATION_TAB = 1
DOWNLOAD_INFORMATION_TAB = 2

# UI Settings
DEFAULT_INFORMATION_GALLERY_HEIGHT = "auto"  # auto, fit
DEFAULT_GALLERY_COLUMN = 4
DEFAULT_GALLERY_THUMBNAIL_IMAGE_STYLE = "contain"
DEFAULT_SHORTCUT_BROWSER_SCREEN_SPLIT_RATIO = 3
DEFAULT_SHORTCUT_BROWSER_SCREEN_SPLIT_RATIO_MAX = 10

# API Settings
DEFAULT_CIVITAI_API_KEY = ""

# Download Filter Settings
DEFAULT_DOWNLOAD_FILTER_DICT = {
    'Model': True,
    'Pruned Model': True,
    'Training Data': False,
    'Config': True,
    'VAE': True,
    'Negative': False,
    'Archive': False,
    'Other': False,
}

# Search Parameters
DEFAULT_SEARCH_LIMIT = 20
DEFAULT_SEARCH_SORT = "Highest Rated"
DEFAULT_SEARCH_PERIOD = "AllTime"
DEFAULT_SEARCH_NSFW = "None"

# Classification Settings
DEFAULT_CLASSIFICATION_KEY = "classification"

# Recipe Settings
DEFAULT_RECIPE_MAX_HISTORY = 100

# Browser Settings
DEFAULT_BROWSER_UPDATE_BUTTON_MIN_WIDTH = "100px"
DEFAULT_BROWSER_REFRESH_BUTTON_MIN_WIDTH = "100px"

# Logging Settings
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
DEFAULT_LOG_BACKUP_COUNT = 5

# Performance Settings
DEFAULT_BATCH_SIZE = 10
DEFAULT_MAX_WORKERS = 4
DEFAULT_MEMORY_LIMIT_MB = 512

# Validation Settings
DEFAULT_VALIDATE_DOWNLOADS = True
DEFAULT_VALIDATE_CHECKSUMS = False
DEFAULT_VALIDATE_FILE_INTEGRITY = True

# Backup Settings
DEFAULT_BACKUP_ENABLED = True
DEFAULT_BACKUP_MAX_COUNT = 5
DEFAULT_BACKUP_INTERVAL_HOURS = 24

# Network Settings
DEFAULT_CONNECTION_TIMEOUT = 30
DEFAULT_READ_TIMEOUT = 300
DEFAULT_MAX_REDIRECTS = 5
DEFAULT_VERIFY_SSL = True


class Defaults:
    """
    Centralized access to all default values and constants.
    """

    # Project Info
    EXTENSIONS_NAME = EXTENSIONS_NAME
    EXTENSIONS_VERSION = EXTENSIONS_VERSION

    # Directories
    SC_DATA_ROOT = SC_DATA_ROOT
    SD_DATA_ROOT = SD_DATA_ROOT

    # HTTP
    HTTP_TIMEOUT = DEFAULT_HTTP_TIMEOUT
    HTTP_MAX_RETRIES = DEFAULT_HTTP_MAX_RETRIES
    HTTP_RETRY_DELAY = DEFAULT_HTTP_RETRY_DELAY
    HEADERS = DEFAULT_HEADERS.copy()

    # Downloads
    DOWNLOAD_TIMEOUT = DEFAULT_DOWNLOAD_TIMEOUT
    DOWNLOAD_MAX_RETRIES = DEFAULT_DOWNLOAD_MAX_RETRIES
    DOWNLOAD_RETRY_DELAY = DEFAULT_DOWNLOAD_RETRY_DELAY
    DOWNLOAD_CHUNK_SIZE = DEFAULT_DOWNLOAD_CHUNK_SIZE
    DOWNLOAD_MAX_CONCURRENT = DEFAULT_DOWNLOAD_MAX_CONCURRENT
    DOWNLOAD_RESUME_ENABLED = DEFAULT_DOWNLOAD_RESUME_ENABLED

    # UI Constants
    PLACEHOLDER = PLACEHOLDER
    NORESULT = NORESULT
    NEWRECIPE = NEWRECIPE
    NEWCLASSIFICATION = NEWCLASSIFICATION

    # Extensions
    MODEL_EXTENSIONS = MODEL_EXTENSIONS
    INFO_EXT = INFO_EXT
    TRIGGER_EXT = TRIGGER_EXT
    PREVIEW_IMAGE_EXT = PREVIEW_IMAGE_EXT

    # Configurations
    MODEL_BASEMODELS = MODEL_BASEMODELS.copy()
    MODEL_FOLDERS = MODEL_FOLDERS.copy()
    UI_TYPENAMES = UI_TYPENAMES.copy()

    # Tab indices
    CIVITAI_INFORMATION_TAB = CIVITAI_INFORMATION_TAB
    USERGAL_INFORMATION_TAB = USERGAL_INFORMATION_TAB
    DOWNLOAD_INFORMATION_TAB = DOWNLOAD_INFORMATION_TAB

    @classmethod
    def get_default_config(cls) -> dict:
        """
        Get complete default configuration dictionary.

        Returns:
            Dictionary containing all default settings
        """
        return {
            # Project
            'extensions_name': cls.EXTENSIONS_NAME,
            'extensions_version': cls.EXTENSIONS_VERSION,
            # Paths
            'sc_data_root': cls.SC_DATA_ROOT,
            'sd_data_root': cls.SD_DATA_ROOT,
            # HTTP
            'http_timeout': cls.HTTP_TIMEOUT,
            'http_max_retries': cls.HTTP_MAX_RETRIES,
            'http_retry_delay': cls.HTTP_RETRY_DELAY,
            'http_pool_connections': DEFAULT_HTTP_POOL_CONNECTIONS,
            'http_pool_maxsize': DEFAULT_HTTP_POOL_MAXSIZE,
            # Downloads
            'download_timeout': cls.DOWNLOAD_TIMEOUT,
            'download_max_retries': cls.DOWNLOAD_MAX_RETRIES,
            'download_retry_delay': cls.DOWNLOAD_RETRY_DELAY,
            'download_chunk_size': cls.DOWNLOAD_CHUNK_SIZE,
            'download_max_concurrent': cls.DOWNLOAD_MAX_CONCURRENT,
            'download_resume_enabled': cls.DOWNLOAD_RESUME_ENABLED,
            # Cache
            'http_cache_enabled': DEFAULT_HTTP_CACHE_ENABLED,
            'http_cache_max_size_mb': DEFAULT_HTTP_CACHE_MAX_SIZE_MB,
            'http_cache_default_ttl': DEFAULT_HTTP_CACHE_DEFAULT_TTL,
            # UI
            'information_gallery_height': DEFAULT_INFORMATION_GALLERY_HEIGHT,
            'gallery_column': DEFAULT_GALLERY_COLUMN,
            'gallery_thumbnail_image_style': DEFAULT_GALLERY_THUMBNAIL_IMAGE_STYLE,
            # API
            'civitai_api_key': DEFAULT_CIVITAI_API_KEY,
            # Search
            'search_limit': DEFAULT_SEARCH_LIMIT,
            'search_sort': DEFAULT_SEARCH_SORT,
            'search_period': DEFAULT_SEARCH_PERIOD,
            'search_nsfw': DEFAULT_SEARCH_NSFW,
            # Filters
            'download_filter_dict': DEFAULT_DOWNLOAD_FILTER_DICT.copy(),
            # Performance
            'batch_size': DEFAULT_BATCH_SIZE,
            'max_workers': DEFAULT_MAX_WORKERS,
            'memory_limit_mb': DEFAULT_MEMORY_LIMIT_MB,
            # Validation
            'validate_downloads': DEFAULT_VALIDATE_DOWNLOADS,
            'validate_checksums': DEFAULT_VALIDATE_CHECKSUMS,
            'validate_file_integrity': DEFAULT_VALIDATE_FILE_INTEGRITY,
            # Backup
            'backup_enabled': DEFAULT_BACKUP_ENABLED,
            'backup_max_count': DEFAULT_BACKUP_MAX_COUNT,
            'backup_interval_hours': DEFAULT_BACKUP_INTERVAL_HOURS,
            # Logging
            'log_level': DEFAULT_LOG_LEVEL,
            'log_max_size': DEFAULT_LOG_MAX_SIZE,
            'log_backup_count': DEFAULT_LOG_BACKUP_COUNT,
        }

    @classmethod
    def get_required_directories(cls) -> list:
        """
        Get list of required directory names.

        Returns:
            List of directory names that should be created
        """
        return [
            cls.SC_DATA_ROOT,
            f"{cls.SC_DATA_ROOT}/sc_infos",
            f"{cls.SC_DATA_ROOT}/sc_gallery",
            f"{cls.SC_DATA_ROOT}/sc_recipes",
            f"{cls.SC_DATA_ROOT}/sc_thumb_images",
        ]

    @classmethod
    def get_supported_model_types(cls) -> list:
        """
        Get list of supported model types.

        Returns:
            List of supported model type names
        """
        return list(cls.UI_TYPENAMES.keys())

    @classmethod
    def get_supported_base_models(cls) -> list:
        """
        Get list of supported base models.

        Returns:
            List of supported base model names
        """
        return list(cls.MODEL_BASEMODELS.keys())

    @classmethod
    def get_model_folder_mapping(cls) -> dict:
        """
        Get model type to folder mapping.

        Returns:
            Dictionary mapping model types to folder names
        """
        return cls.MODEL_FOLDERS.copy()

    @classmethod
    def validate_model_type(cls, model_type: str) -> bool:
        """
        Validate if model type is supported.

        Args:
            model_type: Model type to validate

        Returns:
            True if model type is supported
        """
        return model_type in cls.UI_TYPENAMES

    @classmethod
    def validate_base_model(cls, base_model: str) -> bool:
        """
        Validate if base model is supported.

        Args:
            base_model: Base model to validate

        Returns:
            True if base model is supported
        """
        return base_model in cls.MODEL_BASEMODELS
