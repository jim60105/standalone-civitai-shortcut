"""This module provides a centralized configuration management system for the application."""

import os
import shutil

from . import util
from .compat.compat_layer import CompatibilityLayer
from .conditional_imports import import_manager
from .logging_config import get_logger
from .settings import ConfigManager
from .ui.notification_service import GradioNotificationService, set_notification_service

logger = get_logger(__name__)

# Global configuration manager
config_manager = ConfigManager()

# Compatibility layer variables
_compat_layer = None

# Project-generated files root directory
SC_DATA_ROOT = "data_sc"
# Stable Diffusion files root directory
SD_DATA_ROOT = "data"

root_path = os.getcwd()
extension_base = ""

# File paths for various application data
shortcut = os.path.join(SC_DATA_ROOT, "CivitaiShortCut.json")
shortcut_setting = os.path.join(SC_DATA_ROOT, "CivitaiShortCutSetting.json")
shortcut_classification = os.path.join(SC_DATA_ROOT, "CivitaiShortCutClassification.json")
shortcut_civitai_internet_shortcut_url = os.path.join(SC_DATA_ROOT, "CivitaiShortCutBackupUrl.json")
shortcut_recipe = os.path.join(SC_DATA_ROOT, "CivitaiShortCutRecipeCollection.json")

shortcut_thumbnail_folder = os.path.join(SC_DATA_ROOT, "sc_thumb_images")
shortcut_recipe_folder = os.path.join(SC_DATA_ROOT, "sc_recipes")
shortcut_info_folder = os.path.join(SC_DATA_ROOT, "sc_infos")
shortcut_gallery_folder = os.path.join(SC_DATA_ROOT, "sc_gallery")


def set_compatibility_layer(compat_layer):
    """Set compatibility layer (called by main program)."""
    global _compat_layer
    logger.info("Setting compatibility layer.")
    _compat_layer = compat_layer
    _initialize_extension_base()


def _initialize_extension_base():
    """Initialize extension base path."""
    global extension_base
    logger.debug("Initializing extension base path.")
    compat = CompatibilityLayer.get_compatibility_layer()
    if compat and hasattr(compat, 'path_manager'):
        extension_base = str(compat.path_manager.get_extension_path())
        logger.debug(f"Set extension_base from compat.path_manager: {extension_base}")
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        extension_base = os.path.dirname(os.path.dirname(current_dir))
        logger.debug(f"Fallback extension_base: {extension_base}")


# Initialize extension_base on module load
try:
    _initialize_extension_base()
except Exception:
    pass

# Constants
PLACEHOLDER = "[No Select]"
NORESULT = "[No Result]"
NEWRECIPE = "[New Prompt Recipe]"
NEWCLASSIFICATION = "[New Classification]"
CREATE_MODEL_FOLDER = "Create a model folder to download the model"

model_exts = (".bin", ".pt", ".safetensors", ".ckpt")

model_basemodels = {
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

model_folders = {
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

ui_typenames = {
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

info_ext = ".info"
info_suffix = ".civitai"
triger_ext = ".txt"
triger_suffix = ".triger"
preview_image_ext = ".png"
preview_image_suffix = ".preview"

NSFW_levels = ("None", "Soft", "Mature", "X", "XX")

no_card_preview_image = os.path.join(extension_base, "img", "card-no-preview.png")
nsfw_disable_image = os.path.join(extension_base, "img", "nsfw-no-preview.png")


def init():
    """Initialize application with notification service setup."""
    set_notification_service(GradioNotificationService())
    logger.info(f"Initializing with extension_base={extension_base}")
    try:
        os.makedirs(SC_DATA_ROOT, exist_ok=True)
    except Exception as e:
        logger.warning(f"Failed to create SC_DATA_ROOT for migration: {e}")
    migrate_existing_files()
    init_paths()
    config_manager.load_settings()
    load_data()


def init_paths():
    """Initialize and create necessary directories."""
    download_images_folder = config_manager.get_setting('download_images_folder')
    dirs = [
        SC_DATA_ROOT,
        SD_DATA_ROOT,
        os.path.join(SD_DATA_ROOT, "models"),
        os.path.join(SD_DATA_ROOT, "output"),
        download_images_folder,
        shortcut_thumbnail_folder,
        shortcut_recipe_folder,
        shortcut_info_folder,
        shortcut_gallery_folder,
    ]
    for d in dirs:
        try:
            os.makedirs(d, exist_ok=True)
        except Exception as e:
            logger.warning(f"Failed to create directory {d}: {e}")


def migrate_existing_files():
    """Migrate existing files and folders in root to new data_sc structure."""
    mapping = {
        "CivitaiShortCut.json": shortcut,
        "CivitaiShortCutSetting.json": shortcut_setting,
        "CivitaiShortCutClassification.json": shortcut_classification,
        "CivitaiShortCutRecipeCollection.json": shortcut_recipe,
        "CivitaiShortCutBackupUrl.json": shortcut_civitai_internet_shortcut_url,
        "sc_gallery": shortcut_gallery_folder,
        "sc_thumb_images": shortcut_thumbnail_folder,
        "sc_infos": shortcut_info_folder,
        "sc_recipes": shortcut_recipe_folder,
    }
    for old, new in mapping.items():
        if os.path.exists(old) and not os.path.exists(new):
            try:
                shutil.move(old, new)
                logger.info(f"Moved {old} to {new}")
            except Exception as e:
                logger.warning(f"Failed to move {old} to {new}: {e}")

    for entry in os.listdir('.'):
        if entry.startswith('sc_'):
            old = entry
            new = os.path.join(SC_DATA_ROOT, entry)
            if os.path.exists(old) and not os.path.exists(new):
                try:
                    shutil.move(old, new)
                    logger.info(f"Moved {old} to {new}")
                except Exception as e:
                    logger.warning(f"Failed to move {old} to {new}: {e}")


def load_data():
    """Load configuration data and environment settings."""
    logger.info("Loading configuration data and environment settings.")

    compat = CompatibilityLayer.get_compatibility_layer()
    if compat and hasattr(compat, 'path_manager'):
        logger.debug("Using compat.path_manager for model folders.")
        for model_type, path_key in {
            'TextualInversion': 'embeddings',
            'Hypernetwork': 'hypernetworks',
            'Checkpoint': 'Stable-diffusion',
            'LORA': 'Lora',
        }.items():
            model_path = compat.path_manager.get_model_path(path_key)
            if model_path:
                model_folders[model_type] = model_path
                logger.debug(f"Set {model_type} folder: {model_path}")
    else:
        logger.debug("Fallback to import_manager for model folders.")
        shared = import_manager.get_webui_module('shared')
        if shared and hasattr(shared, 'cmd_opts'):
            cmd_opts = shared.cmd_opts
            for model_type, attr in {
                'TextualInversion': 'embeddings_dir',
                'Hypernetwork': 'hypernetwork_dir',
                'Checkpoint': 'ckpt_dir',
                'LORA': 'lora_dir',
            }.items():
                if hasattr(cmd_opts, attr) and getattr(cmd_opts, attr):
                    model_folders[model_type] = getattr(cmd_opts, attr)
                    logger.debug(f"Set {model_type} folder (fallback): {getattr(cmd_opts, attr)}")

    environment = config_manager.load_settings()
    if not environment:
        return

    logger.info(f"Loaded environment: {environment}")

    user_folders = environment.get('model_folders', {})
    for folder_key in ['LoCon', 'Wildcards', 'Controlnet', 'AestheticGradient', 'Poses', 'Other']:
        if folder_key in user_folders:
            model_folders[folder_key] = user_folders[folder_key]
            logger.debug(f"Set {folder_key} folder: {user_folders[folder_key]}")


def get_setting(key: str, default=None):
    """Proxy for ConfigManager.get_setting."""
    return config_manager.get_setting(key, default)


def set_setting(key: str, value):
    """Proxy for ConfigManager.set_setting."""
    return config_manager.set_setting(key, value)


def save_setting(setting_dict: dict):
    """Proxy for ConfigManager.save_settings."""
    return config_manager.save_settings(setting_dict)


def load():
    """Proxy for ConfigManager.load_settings."""
    return config_manager.load_settings()


def set_NSFW(enable, level="None"):
    """Sets NSFW filtering options."""
    config_manager.set_setting('NSFW_filtering_enable', enable)
    config_manager.set_setting('NSFW_level_user', level)


def save_NSFW():
    """Proxy to save NSFW settings to the configuration file."""
    return config_manager.save_settings()


def generate_type_basefolder(content_type):
    """Generates the base folder path for a given content type."""
    if content_type in model_folders:
        return model_folders[content_type]
    if content_type:
        return os.path.join(model_folders['Unknown'], util.replace_dirname(content_type))
    return model_folders['Unknown']


def generate_version_foldername(model_name, ver_name, ver_id):
    """Generates a folder name for a specific model version."""
    return f"{model_name}-{ver_name}"


def get_model_folders():
    """Returns a list of all model folder paths."""
    return list(model_folders.values())


def get_ui_typename(model_type):
    """Gets the UI type name for a given model type."""
    for k, v in ui_typenames.items():
        if v == model_type:
            return k
    return model_type


def get_imagefn_and_shortcutid_from_recipe_image(recipe_image):
    """Extracts image filename and shortcut ID from a recipe image string."""
    if recipe_image and ":" in recipe_image:
        return recipe_image.split(":", 1)
    return None, None


def set_imagefn_and_shortcutid_for_recipe_image(shortcutid, image_fn):
    """Constructs a recipe image string from a shortcut ID and image filename."""
    if image_fn and shortcutid:
        return f"{shortcutid}:{image_fn}"
    return None


def get_modelid_from_shortcutname(sc_name):
    """Extracts the model ID from a shortcut name."""
    if not sc_name:
        return None

    if isinstance(sc_name, dict) and 'caption' in sc_name:
        sc_name = sc_name['caption']

    if isinstance(sc_name, list):
        sc_name = sc_name[1] if len(sc_name) > 1 else sc_name[0] if sc_name else None

    if isinstance(sc_name, str) and ":" in sc_name:
        return sc_name.rsplit(':', 1)[-1]

    return None


def set_shortcutname(modelname, modelid):
    """Constructs a shortcut name from a model name and ID."""
    if modelname and modelid:
        return f"{modelname}:{modelid}"
    return None


def get_image_url_to_shortcut_file(modelid, versionid, image_url):
    """Generates the local file path for a shortcut image from a URL."""
    if image_url:
        version_image_prefix = f"{versionid}-"
        model_path = os.path.join(shortcut_info_folder, str(modelid))
        image_id, _ = os.path.splitext(os.path.basename(image_url))
        return os.path.join(model_path, f"{version_image_prefix}{image_id}{preview_image_ext}")
    return None


def get_image_url_to_gallery_file(image_url):
    """Generates the local file path for a gallery image from a URL."""
    if image_url:
        image_id, _ = os.path.splitext(os.path.basename(image_url))
        return os.path.join(shortcut_gallery_folder, f"{image_id}{preview_image_ext}")
    return None
