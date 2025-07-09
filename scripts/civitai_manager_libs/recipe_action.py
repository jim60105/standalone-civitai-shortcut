"""Unified entry point for recipe actions."""

from .recipe_actions.recipe_management import RecipeManager
from .recipe_actions.recipe_browser import RecipeBrowser
from .recipe_actions.recipe_reference import RecipeReferenceManager
from .recipe_actions.recipe_gallery import RecipeGallery
from .recipe_actions.recipe_utilities import RecipeUtilities

from .logging_config import get_logger

# Module logger for this component
logger = get_logger(__name__)

# Global instances
_recipe_manager = RecipeManager()
_recipe_browser = RecipeBrowser()
_recipe_reference_manager = RecipeReferenceManager()
_recipe_gallery = RecipeGallery()


def on_ui(recipe_input, shortcut_input, civitai_tabs):
    """Delegate to RecipeBrowser.on_ui."""
    return _recipe_browser.on_ui(recipe_input, shortcut_input, civitai_tabs)


def make_recipe_from_sc_information(*args, **kwargs):
    """Delegate to RecipeManager.create_recipe."""
    return _recipe_manager.create_recipe(*args, **kwargs)


def write_recipe_collection(*args, **kwargs):
    """Delegate to RecipeManager.update_recipe."""
    return _recipe_manager.update_recipe(*args, **kwargs)


def delete_recipe_collection(*args, **kwargs):
    """Delegate to RecipeManager.delete_recipe."""
    return _recipe_manager.delete_recipe(*args, **kwargs)


def get_recipe(*args, **kwargs):
    """Delegate to RecipeManager.get_recipe."""
    return _recipe_manager.get_recipe(*args, **kwargs)


def list_recipes(*args, **kwargs):
    """Delegate to RecipeManager.list_recipes."""
    return _recipe_manager.list_recipes(*args, **kwargs)


def duplicate_recipe(*args, **kwargs):
    """Delegate to RecipeManager.duplicate_recipe."""
    return _recipe_manager.duplicate_recipe(*args, **kwargs)


def validate_recipe_data(*args, **kwargs):
    """Delegate to RecipeManager.validate_recipe_data."""
    return _recipe_manager.validate_recipe_data(*args, **kwargs)


def recipe_browser_page(*args, **kwargs):
    """Delegate to RecipeBrowser.create_browser_ui."""
    return _recipe_browser.create_browser_ui(*args, **kwargs)


def get_recipe_references(*args, **kwargs):
    """Delegate to RecipeReferenceManager.get_recipe_references."""
    return _recipe_reference_manager.get_recipe_references(*args, **kwargs)


def add_recipe_reference(*args, **kwargs):
    """Delegate to RecipeReferenceManager.add_recipe_reference."""
    return _recipe_reference_manager.add_recipe_reference(*args, **kwargs)


def remove_recipe_reference(*args, **kwargs):
    """Delegate to RecipeReferenceManager.remove_recipe_reference."""
    return _recipe_reference_manager.remove_recipe_reference(*args, **kwargs)


def update_recipe_reference(*args, **kwargs):
    """Delegate to RecipeReferenceManager.update_recipe_reference."""
    return _recipe_reference_manager.update_recipe_reference(*args, **kwargs)


def sync_references_with_models(*args, **kwargs):
    """Delegate to RecipeReferenceManager.sync_references_with_models."""
    return _recipe_reference_manager.sync_references_with_models(*args, **kwargs)


def create_gallery_ui(*args, **kwargs):
    """Delegate to RecipeGallery.create_gallery_ui."""
    return _recipe_gallery.create_gallery_ui(*args, **kwargs)


def load_recipe_images(*args, **kwargs):
    """Delegate to RecipeGallery.load_recipe_images."""
    return _recipe_gallery.load_recipe_images(*args, **kwargs)


def add_image_to_recipe(*args, **kwargs):
    """Delegate to RecipeGallery.add_image_to_recipe."""
    return _recipe_gallery.add_image_to_recipe(*args, **kwargs)


def remove_image_from_recipe(*args, **kwargs):
    """Delegate to RecipeGallery.remove_image_from_recipe."""
    return _recipe_gallery.remove_image_from_recipe(*args, **kwargs)


def generate_image_thumbnail(*args, **kwargs):
    """Delegate to RecipeGallery.generate_image_thumbnail."""
    return _recipe_gallery.generate_image_thumbnail(*args, **kwargs)


def get_image_metadata(*args, **kwargs):
    """Delegate to RecipeGallery.get_image_metadata."""
    return _recipe_gallery.get_image_metadata(*args, **kwargs)


def export_recipe(*args, **kwargs):
    """Delegate to RecipeUtilities.export_recipe."""
    return RecipeUtilities.export_recipe(*args, **kwargs)


def import_recipe(*args, **kwargs):
    """Delegate to RecipeUtilities.import_recipe."""
    return RecipeUtilities.import_recipe(*args, **kwargs)


def validate_recipe_format(*args, **kwargs):
    """Delegate to RecipeUtilities.validate_recipe_format."""
    return RecipeUtilities.validate_recipe_format(*args, **kwargs)


def generate_recipe_id(*args, **kwargs):
    """Delegate to RecipeUtilities.generate_recipe_id."""
    return RecipeUtilities.generate_recipe_id(*args, **kwargs)


def backup_recipe_data(*args, **kwargs):
    """Delegate to RecipeUtilities.backup_recipe_data."""
    return RecipeUtilities.backup_recipe_data(*args, **kwargs)


def restore_recipe_data(*args, **kwargs):
    """Delegate to RecipeUtilities.restore_recipe_data."""
    return RecipeUtilities.restore_recipe_data(*args, **kwargs)


def on_recipe_drop_image_upload(*args, **kwargs):
    """Delegate to RecipeGallery.on_recipe_drop_image_upload."""
    return _recipe_gallery.on_recipe_drop_image_upload(*args, **kwargs)


def on_recipe_generate_data_change(*args, **kwargs):
    """Delegate to RecipeGallery.on_recipe_generate_data_change."""
    return _recipe_gallery.on_recipe_generate_data_change(*args, **kwargs)


def on_recipe_gallery_select(*args, **kwargs):
    """Delegate to RecipeGallery.on_recipe_gallery_select."""
    return _recipe_gallery.on_recipe_gallery_select(*args, **kwargs)


def on_refresh_recipe_change(*args, **kwargs):
    """Delegate to RecipeBrowser.on_refresh_recipe_change."""
    return _recipe_browser.on_refresh_recipe_change(*args, **kwargs)


def on_recipe_new_btn_click(*args, **kwargs):
    """Delegate to RecipeManager.on_recipe_new_btn_click."""
    return _recipe_manager.on_recipe_new_btn_click(*args, **kwargs)


def on_recipe_update_btn_click(*args, **kwargs):
    """Delegate to RecipeManager.on_recipe_update_btn_click."""
    return _recipe_manager.on_recipe_update_btn_click(*args, **kwargs)


def on_recipe_delete_btn_click(*args, **kwargs):
    """Delegate to RecipeManager.on_recipe_delete_btn_click."""
    return _recipe_manager.on_recipe_delete_btn_click(*args, **kwargs)


def load_model_information(*args, **kwargs):
    """Delegate to RecipeReferenceManager.load_model_information."""
    return _recipe_reference_manager.load_model_information(*args, **kwargs)


def on_reference_modelid_change(*args, **kwargs):
    """Delegate to RecipeReferenceManager.on_reference_modelid_change."""
    return _recipe_reference_manager.on_reference_modelid_change(*args, **kwargs)


def on_reference_versions_select(*args, **kwargs):
    """Delegate to RecipeReferenceManager.on_reference_versions_select."""
    return _recipe_reference_manager.on_reference_versions_select(*args, **kwargs)


def on_delete_reference_model_btn_click(*args, **kwargs):
    """Delegate to RecipeReferenceManager.on_delete_reference_model_btn_click."""
    return _recipe_reference_manager.on_delete_reference_model_btn_click(*args, **kwargs)


def on_close_reference_model_information_btn_click(*args, **kwargs):
    """Delegate to RecipeReferenceManager.on_close_reference_model_information_btn_click."""
    return _recipe_reference_manager.on_close_reference_model_information_btn_click(*args, **kwargs)


def on_insert_prompt_btn_click(*args, **kwargs):
    """Delegate to RecipeReferenceManager.on_insert_prompt_btn_click."""
    return _recipe_reference_manager.on_insert_prompt_btn_click(*args, **kwargs)


def on_recipe_prompt_tabs_select(*args, **kwargs):
    """Delegate to RecipeBrowser.on_recipe_prompt_tabs_select."""
    return _recipe_browser.on_recipe_prompt_tabs_select(*args, **kwargs)


def on_reference_gallery_loading(*args, **kwargs):
    """Delegate to RecipeReferenceManager.on_reference_gallery_loading."""
    return _recipe_reference_manager.on_reference_gallery_loading(*args, **kwargs)


def on_reference_sc_gallery_select(*args, **kwargs):
    """Delegate to RecipeReferenceManager.on_reference_sc_gallery_select."""
    return _recipe_reference_manager.on_reference_sc_gallery_select(*args, **kwargs)


def on_reference_gallery_select(*args, **kwargs):
    """Delegate to RecipeReferenceManager.on_reference_gallery_select."""
    return _recipe_reference_manager.on_reference_gallery_select(*args, **kwargs)


def add_string(*args, **kwargs):
    """Delegate to RecipeReferenceManager.add_string."""
    return _recipe_reference_manager.add_string(*args, **kwargs)


def remove_strings(*args, **kwargs):
    """Delegate to RecipeReferenceManager.remove_strings."""
    return _recipe_reference_manager.remove_strings(*args, **kwargs)


def is_string(*args, **kwargs):
    """Delegate to RecipeReferenceManager.is_string."""
    return _recipe_reference_manager.is_string(*args, **kwargs)


def analyze_prompt(*args, **kwargs):
    """Delegate to RecipeUtilities.analyze_prompt."""
    return RecipeUtilities.analyze_prompt(*args, **kwargs)


def on_recipe_input_change(*args, **kwargs):
    """Delegate to RecipeBrowser.on_recipe_input_change."""
    return _recipe_browser.on_recipe_input_change(*args, **kwargs)


def get_recipe_information(*args, **kwargs):
    """Delegate to RecipeUtilities.get_recipe_information."""
    return RecipeUtilities.get_recipe_information(*args, **kwargs)


def on_recipe_create_btn_click(*args, **kwargs):
    """Delegate to RecipeManager.on_recipe_create_btn_click."""
    return _recipe_manager.on_recipe_create_btn_click(*args, **kwargs)


def generate_prompt(*args, **kwargs):
    """Delegate to RecipeUtilities.generate_prompt."""
    return RecipeUtilities.generate_prompt(*args, **kwargs)
