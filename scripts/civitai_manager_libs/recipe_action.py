"""Unified entry point for recipe actions."""

from .recipe_actions.recipe_management import RecipeManager
from .recipe_actions.recipe_browser import RecipeBrowser
from .recipe_actions.recipe_reference import RecipeReferenceManager
from .recipe_actions.recipe_gallery import RecipeGallery
from .recipe_actions.recipe_utilities import RecipeUtilities

# Global instances
_recipe_manager = RecipeManager()
_recipe_browser = RecipeBrowser()
_recipe_reference_manager = RecipeReferenceManager()
_recipe_gallery = RecipeGallery()


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
