"""
Core CRUD operations and business logic for recipes.
"""

from ..logging_config import get_logger
from ..exceptions import ValidationError, FileOperationError
from ..recipe import (
    create_recipe as _raw_create,
    update_recipe as _raw_update,
    delete_recipe as _raw_delete,
    get_recipe as _raw_get,
    get_list as _raw_list,
)
from .recipe_utilities import RecipeUtilities

logger = get_logger(__name__)


class RecipeManager:
    """Handles CRUD operations and core logic for recipes."""

    def __init__(self):
        """Initialize the RecipeManager with utility helpers."""
        self._utils = RecipeUtilities()

    def create_recipe(self, recipe_data: dict) -> str:
        """Create a new recipe and return its identifier."""
        if not isinstance(recipe_data, dict):
            logger.error("create_recipe: recipe_data must be a dict, got %s", type(recipe_data))
            raise ValidationError("Recipe data must be a dictionary")
        if not self.validate_recipe_data(recipe_data):
            logger.error("create_recipe: invalid recipe data: %s", recipe_data)
            raise ValidationError("Invalid recipe data")
        name = recipe_data.get("name")
        desc = recipe_data.get("description", "")
        prompt = recipe_data.get("prompt")
        classification = recipe_data.get("classification")
        success = _raw_create(name, desc, prompt, classification)
        if not success:
            logger.error("create_recipe: failed to create recipe %s", name)
            raise FileOperationError(f"Failed to create recipe: {name}")
        return name

    def update_recipe(self, recipe_id: str, recipe_data: dict) -> bool:
        """Update a recipe's content and return True if successful."""
        if not recipe_id or not isinstance(recipe_data, dict):
            logger.error("update_recipe: invalid arguments: %s, %s", recipe_id, recipe_data)
            raise ValidationError("Invalid arguments for update_recipe")
        if not self.validate_recipe_data(recipe_data):
            logger.error("update_recipe: invalid recipe data: %s", recipe_data)
            raise ValidationError("Invalid recipe data")
        name = recipe_data.get("name")
        desc = recipe_data.get("description", "")
        prompt = recipe_data.get("prompt")
        classification = recipe_data.get("classification")
        success = _raw_update(recipe_id, name, desc, prompt, classification)
        if not success:
            logger.error("update_recipe: failed to update recipe %s", recipe_id)
            return False
        return True

    def delete_recipe(self, recipe_id: str) -> bool:
        """Delete a recipe and return True if deletion succeeded."""
        if not recipe_id:
            logger.error("delete_recipe: recipe_id is required")
            raise ValidationError("Recipe ID is required for deletion")
        _raw_delete(recipe_id)
        exists = _raw_get(recipe_id) is not None
        if exists:
            logger.error("delete_recipe: failed to delete recipe %s", recipe_id)
            return False
        return True

    def get_recipe(self, recipe_id: str) -> dict:
        """Retrieve detailed information about a recipe by its identifier."""
        if not recipe_id:
            logger.error("get_recipe: recipe_id is required")
            raise ValidationError("Recipe ID is required to retrieve recipe")
        return _raw_get(recipe_id)

    def list_recipes(self, filter_criteria: dict = None) -> list:
        """List recipes with optional filtering criteria."""
        if filter_criteria and not isinstance(filter_criteria, dict):
            logger.warning(
                "list_recipes: filter_criteria must be a dict, ignoring invalid filter: %s",
                filter_criteria,
            )
            filter_criteria = None
        search = classification = shortcuts = None
        if filter_criteria:
            search = filter_criteria.get("search")
            classification = filter_criteria.get("classification")
            shortcuts = filter_criteria.get("shortcuts")
        return _raw_list(search=search, classification=classification, shortcuts=shortcuts)

    def duplicate_recipe(self, recipe_id: str, new_name: str) -> str:
        """Duplicate an existing recipe under a new name and return the new identifier."""
        original = _raw_get(recipe_id)
        if not original:
            logger.error("duplicate_recipe: original recipe %s not found", recipe_id)
            raise ValidationError(f"Original recipe not found: {recipe_id}")
        new_desc = original.get("description")
        new_prompt = original.get("generate")
        new_classification = original.get("classification")
        success = _raw_create(new_name, new_desc, new_prompt, new_classification)
        if not success:
            logger.error(
                "duplicate_recipe: failed to duplicate recipe %s to %s", recipe_id, new_name
            )
            raise FileOperationError(f"Failed to duplicate recipe: {recipe_id}")
        return new_name

    def validate_recipe_data(self, recipe_data: dict) -> bool:
        """Validate the structure of recipe data using utility function."""
        try:
            return self._utils.validate_recipe_format(recipe_data)
        except Exception as e:
            logger.error("validate_recipe_data: validation error: %s", e)
            return False
