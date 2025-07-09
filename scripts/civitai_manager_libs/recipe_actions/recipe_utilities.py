"""
Utility functions and common logic for recipe operations.
"""

import os
import json
import uuid
import shutil
import datetime

from .. import setting
from ..logging_config import get_logger
from ..exceptions import ValidationError, FileOperationError
from ..recipe import get_recipe as _raw_get, create_recipe as _raw_create

logger = get_logger(__name__)


class RecipeUtilities:
    """Provides helper methods for recipe import/export, validation, and backup."""

    def __init__(self):
        """Initialize the utilities helper."""
        super().__init__()

    @staticmethod
    def export_recipe(recipe_id: str, format: str) -> str:
        """Export a recipe to the specified format (currently only 'json').
        Returns export file path."""
        recipe = _raw_get(recipe_id)
        if not recipe:
            logger.error("export_recipe: recipe %s not found", recipe_id)
            raise ValidationError(f"Recipe not found: {recipe_id}")
        fmt = format.lower()
        if fmt != "json":
            logger.error("export_recipe: unsupported format %s", format)
            raise ValidationError(f"Unsupported export format: {format}")
        export_dir = os.path.dirname(setting.shortcut_recipe)
        os.makedirs(export_dir, exist_ok=True)
        export_path = os.path.join(export_dir, f"{recipe_id}.json")
        try:
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump({recipe_id: recipe}, f, indent=4)
            logger.info("export_recipe: exported %s to %s", recipe_id, export_path)
            return export_path
        except Exception as e:
            logger.error("export_recipe: error exporting recipe %s: %s", recipe_id, e)
            raise FileOperationError(f"Failed to export recipe: {e}")

    @staticmethod
    def import_recipe(file_path: str) -> str:
        """Import a recipe from a JSON file path. Returns the created recipe ID."""
        if not os.path.isfile(file_path):
            logger.error("import_recipe: file not found %s", file_path)
            raise ValidationError(f"Import file not found: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error("import_recipe: error reading file %s: %s", file_path, e)
            raise FileOperationError(f"Failed to read import file: {e}")
        if not isinstance(data, dict) or len(data) != 1:
            logger.error("import_recipe: invalid data format in %s", file_path)
            raise ValidationError("Invalid recipe data format for import")
        recipe_id, recipe_data = next(iter(data.items()))
        desc = recipe_data.get("description", "")
        prompt = recipe_data.get("generate")
        classification = recipe_data.get("classification")
        success = _raw_create(recipe_id, desc, prompt, classification)
        if not success:
            logger.error("import_recipe: failed to import %s", recipe_id)
            raise FileOperationError(f"Failed to import recipe: {recipe_id}")
        logger.info("import_recipe: imported recipe %s from %s", recipe_id, file_path)
        return recipe_id

    @staticmethod
    def validate_recipe_format(recipe_data: dict) -> bool:
        """Validate the structure of recipe data. Requires 'name' non-empty string."""
        if not isinstance(recipe_data, dict):
            return False
        name = recipe_data.get("name")
        if not name or not isinstance(name, str) or not name.strip():
            return False
        return True

    @staticmethod
    def generate_recipe_id() -> str:
        """Generate a unique identifier for a recipe using UUID4."""
        return uuid.uuid4().hex

    @staticmethod
    def backup_recipe_data(recipe_id: str) -> str:
        """Backup the recipe JSON file to a timestamped backup file and return its path."""
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        backup_dir = os.path.join(setting.shortcut_recipe_folder, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, f"{recipe_id}_{timestamp}.json")
        try:
            # Backup the individual recipe JSON file (e.g., recipe_id.json) from recipe folder
            export_path = os.path.join(setting.shortcut_recipe_folder, f"{recipe_id}.json")
            shutil.copy2(export_path, backup_path)
            logger.info("backup_recipe_data: backed up %s to %s", recipe_id, backup_path)
            return backup_path
        except Exception as e:
            logger.error("backup_recipe_data: error backing up %s: %s", recipe_id, e)
            raise FileOperationError(f"Failed to backup recipe data: {e}")

    @staticmethod
    def restore_recipe_data(backup_path: str) -> bool:
        """Restore recipe JSON file from a backup path."""
        if not os.path.isfile(backup_path):
            logger.error("restore_recipe_data: backup file not found %s", backup_path)
            raise ValidationError(f"Backup file not found: {backup_path}")
        # Restore the backup to the original recipe JSON file (recipe_id.json)
        backup_name = os.path.basename(backup_path)
        recipe_id = backup_name.split('_')[0]
        dest = os.path.join(setting.shortcut_recipe_folder, f"{recipe_id}.json")
        try:
            shutil.copy2(backup_path, dest)
            logger.info("restore_recipe_data: restored backup %s to %s", backup_path, dest)
            return True
        except Exception as e:
            logger.error("restore_recipe_data: error restoring %s: %s", backup_path, e)
            raise FileOperationError(f"Failed to restore recipe data: {e}")

    @staticmethod
    def generate_prompt(prompt, negativePrompt, Options):
        """Generate a formatted prompt string from components.

        Args:
            prompt (str): The main prompt text
            negativePrompt (str): The negative prompt text
            Options (str): The options/parameters string

        Returns:
            str: Formatted prompt string or None if all inputs are empty
        """
        meta_string = None
        if prompt and len(prompt.strip()) > 0:
            meta_string = f"""{prompt.strip()}""" + "\n"

        if negativePrompt and len(negativePrompt.strip()) > 0:
            if meta_string:
                meta_string = meta_string + f"""Negative prompt:{negativePrompt.strip()}""" + "\n"
            else:
                meta_string = f"""Negative prompt:{negativePrompt.strip()}""" + "\n"

        if Options and len(Options.strip()) > 0:
            if meta_string:
                meta_string = meta_string + Options.strip()
            else:
                meta_string = Options.strip()

        return meta_string

    @staticmethod
    def analyze_prompt(generate_data):
        """
        Parse generate data into prompt, negative prompt, options string, formatted string.
        This maintains compatibility with the original analyze_prompt function behavior.
        """
        from ..logging_config import get_logger
        from .. import prompt

        logger = get_logger(__name__)
        logger.debug(f"analyze_prompt called with: {repr(generate_data)}")

        positivePrompt = None
        negativePrompt = None
        options = None
        gen_string = None

        if generate_data:
            generate = None
            try:
                logger.debug(" Calling prompt.parse_data")
                generate = prompt.parse_data(generate_data)
                logger.debug(f" prompt.parse_data returned: {generate}")
            except Exception as e:
                logger.debug(f" Exception in prompt.parse_data: {e}")

            if generate:
                if "options" in generate:
                    options = [f"{k}:{v}" for k, v in generate['options'].items()]
                    if options:
                        options = ", ".join(options)
                    logger.debug(f" Processed options: {repr(options)}")

                if 'prompt' in generate:
                    positivePrompt = generate['prompt']
                    logger.debug(f" Extracted positive prompt: {repr(positivePrompt)}")

                if 'negativePrompt' in generate:
                    negativePrompt = generate['negativePrompt']
                    logger.debug(f" Extracted negative prompt: {repr(negativePrompt)}")
            else:
                logger.debug(" generate is None after parse_data")

            gen_string = RecipeUtilities.generate_prompt(positivePrompt, negativePrompt, options)
            logger.debug(f" Generated string: {repr(gen_string)}")
        else:
            logger.debug(" generate_data is empty")

        result = (positivePrompt, negativePrompt, options, gen_string)
        logger.debug(f" analyze_prompt returning: {result}")
        return result

    @staticmethod
    def get_recipe_information(select_name: str):
        """Retrieve recipe data fields for given recipe name with complete processing."""
        import os
        from .. import recipe, setting

        generate = None
        options = None
        classification = None
        gen_string = None
        Prompt = None
        negativePrompt = None
        description = None
        imagefile = None

        if select_name:
            rc = recipe.get_recipe(select_name)

            if rc and "generate" in rc:
                generate = rc['generate']
                if "options" in generate:
                    options = [f"{k}:{v}" for k, v in generate['options'].items()]
                    if options:
                        options = ", ".join(options)

                if "prompt" in generate:
                    Prompt = generate['prompt']

                if "negativePrompt" in generate:
                    negativePrompt = generate['negativePrompt']

                gen_string = RecipeUtilities.generate_prompt(Prompt, negativePrompt, options)

            if rc and "image" in rc:
                if rc['image']:
                    imagefile = os.path.join(setting.shortcut_recipe_folder, rc['image'])

            if rc and "description" in rc:
                description = rc['description']

            if rc and "classification" in rc:
                classification = rc['classification']
                if not classification or len(classification.strip()) == 0:
                    classification = setting.PLACEHOLDER

        return description, Prompt, negativePrompt, options, gen_string, classification, imagefile
