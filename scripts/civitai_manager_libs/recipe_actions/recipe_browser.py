"""
UI and interaction logic for browsing recipes.
"""

from .. import recipe
from ..logging_config import get_logger
import importlib

logger = get_logger(__name__)


class RecipeBrowser:
    """Provides recipe browsing UI construction and list handling."""

    def __init__(self):
        self._logger = logger

    def create_browser_ui(self) -> tuple:
        """Construct and return the browser gallery and refresh trigger."""
        # Dynamically import on_ui to respect monkeypatch overrides
        module = importlib.import_module('scripts.civitai_manager_libs.recipe_browser_page')
        return module.on_ui()

    def refresh_recipe_list(self, search_term: str = "") -> list:
        """Refresh list of recipes matching the search term."""
        return recipe.get_list(search=search_term)

    def filter_recipes(self, filter_type: str, filter_value: str) -> list:
        """Filter recipes by classification or shortcuts."""
        criteria = {filter_type: filter_value}
        return recipe.get_list(**criteria)

    def sort_recipes(self, sort_by: str, ascending: bool = True) -> list:
        """Sort recipes by specified field."""
        recipelist = recipe.get_list()
        try:
            return sorted(recipelist, key=lambda x: x.get(sort_by), reverse=not ascending)
        except Exception:
            self._logger.warning("sort_recipes: unable to sort by %s", sort_by)
            return recipelist

    def handle_recipe_selection(self, recipe_id: str) -> dict:
        """Retrieve detailed recipe information for selection event."""
        return recipe.get_recipe(recipe_id)

    def search_recipes(self, query: str) -> list:
        """Search recipes by name, description, or classification."""
        return recipe.get_list(search=query)
