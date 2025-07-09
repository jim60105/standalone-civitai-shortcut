"""
Gallery presentation and management for recipe-associated images.
"""

import os

import gradio as gr
from PIL import Image

from .. import setting
from .. import recipe
from ..logging_config import get_logger
from ..compat.compat_layer import CompatibilityLayer
from ..image_processor import ImageMetadataProcessor

logger = get_logger(__name__)


class RecipeGallery:
    """Manages display and CRUD of recipe-associated images."""

    def __init__(self):
        self._logger = logger

    def create_gallery_ui(self, recipe_id: str) -> gr.Gallery:
        """Create a Gradio gallery UI component for a given recipe."""
        images = self.load_recipe_images(recipe_id)
        return gr.Gallery(
            value=images,
            show_label=False,
            columns=setting.prompt_shortcut_column,
            height="auto",
            object_fit=setting.gallery_thumbnail_image_style,
            preview=False,
            allow_preview=False,
        )

    def load_recipe_images(self, recipe_id: str) -> list:
        """Load file paths of images associated with the specified recipe."""
        if not recipe_id:
            return []
        rc = recipe.get_recipe(recipe_id)
        img = rc.get('image') if isinstance(rc, dict) else None
        if img:
            img_path = os.path.join(setting.shortcut_recipe_folder, img)
            if os.path.isfile(img_path):
                return [img_path]
        return []

    def add_image_to_recipe(self, recipe_id: str, image_path: str) -> bool:
        """Associate an image file with a recipe."""
        return recipe.update_recipe_image(recipe_id, image_path)

    def remove_image_from_recipe(self, recipe_id: str, image_id: str) -> bool:
        """Remove associated image from a recipe."""
        # Clearing image association
        return recipe.update_recipe_image(recipe_id, None)

    def generate_image_thumbnail(self, image_path: str) -> str:
        """Generate and return the thumbnail path for an image."""
        try:
            thumb_dir = setting.shortcut_thumbnail_folder
            os.makedirs(thumb_dir, exist_ok=True)
            base = os.path.basename(image_path)
            thumb_path = os.path.join(thumb_dir, base)
            with Image.open(image_path) as img:
                img.thumbnail((setting.thumbnail_width, setting.thumbnail_height))
                img.save(thumb_path)
            return thumb_path
        except Exception as e:
            self._logger.error("generate_image_thumbnail: %s", e)
            return image_path

    def get_image_metadata(self, image_path: str) -> dict:
        """Retrieve embedded metadata or parameters from an image file."""
        compat = CompatibilityLayer.get_compatibility_layer()
        if compat and hasattr(compat, 'metadata_processor'):
            try:
                info = compat.metadata_processor.extract_png_info(image_path)
                return info
            except Exception:
                pass
        # Fallback to PIL metadata extraction
        try:
            processor = ImageMetadataProcessor(mode='standalone')
            return processor.extract_png_info(image_path)
        except Exception as e:
            self._logger.error("get_image_metadata: %s", e)
            return {}
