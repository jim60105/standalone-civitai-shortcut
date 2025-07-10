"""Model-related utility functions."""

import os

from .. import util
from ..logging_config import get_logger
from .constants import ui_typenames
from .path_manager import model_folders

logger = get_logger(__name__)


def generate_type_basefolder(content_type):
    """Generates the base folder path for a given content type."""
    if content_type in model_folders:
        return model_folders[content_type]
    if content_type:
        unknown_folder = model_folders.get('Unknown')
        if unknown_folder:
            return os.path.join(str(unknown_folder), str(util.replace_dirname(content_type)))
    return model_folders.get('Unknown', '')


def generate_version_foldername(model_name, ver_name, ver_id):
    """Generates a folder name for a specific model version."""
    return f"{model_name}-{ver_name}"


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
