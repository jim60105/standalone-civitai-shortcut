"""Unified entry point for recipe actions."""

from .recipe_actions.recipe_management import RecipeManager
from .recipe_actions.recipe_browser import RecipeBrowser
from .recipe_actions.recipe_reference import RecipeReferenceManager
from .recipe_actions.recipe_gallery import RecipeGallery
from .recipe_actions.recipe_utilities import RecipeUtilities

from .logging_config import get_logger
from .recipe_browser_page import on_recipe_reference_gallery_select

# Module logger for this component
logger = get_logger(__name__)
from . import setting

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


def generate_prompt(prompt_text: str, negative_prompt: str = None, options: dict = None) -> str:
    """Combine prompt text with negative prompt and options into a single string."""
    result = prompt_text or ""
    if negative_prompt:
        result = f"{result} {negative_prompt}"
    if options:
        # Append options as key=value pairs
        for key, value in options.items():
            result = f"{result} {key}={value}"
    return result


def on_reference_sc_gallery_select(evt, shortcuts):
    """
    Handle reference shortcut gallery select event, adding model ID on valid input.
    Logs debug on invalid input formats.
    """
    val = getattr(evt, 'value', None)
    if not val or not isinstance(val, (dict, list, str)):
        logger.debug(f"Unexpected evt.value format: {val}")
        return shortcuts, None
    return on_recipe_reference_gallery_select(evt, shortcuts)


def on_reference_gallery_select(evt, shortcuts, delete_opt=True):
    """
    Handle reference gallery select toggle event. delete_opt parameter retained for compatibility.
    """
    # Support string, list, or FileData dict input; ignore delete_opt for compatibility
    val = getattr(evt, 'value', None)
    if isinstance(val, list) and len(val) > 1:
        shortcut = val[1]
    elif isinstance(val, dict) and 'caption' in val:
        shortcut = val['caption']
    elif isinstance(val, str):
        shortcut = val
    else:
        return shortcuts, None, None, None
    model_id = setting.get_modelid_from_shortcutname(shortcut)
    return shortcuts, None, None, model_id


def analyze_prompt(metadata: str):
    """
    Parse metadata string into prompt, negative prompt, options string, and return raw metadata.
    """
    raw = metadata
    lines = [line.strip() for line in metadata.strip().splitlines() if line.strip()]
    prompt = None
    negative = None
    options = None
    for line in lines:
        low = line.lower()
        if low.startswith('prompt:'):
            prompt = line[len('prompt:') :].strip()
        elif low.startswith('negative prompt:'):
            negative = line[len('negative prompt:') :].strip()
        elif low.startswith('steps:') or low.startswith('sampler:') or low.startswith('cfg scale:'):
            # Normalize spacing after colon for options
            cleaned = line.replace(': ', ':')
            options = options + cleaned if options else cleaned
    if prompt is None and lines:
        prompt = lines[0]
    if negative is None and len(lines) > 1 and lines[1].lower().startswith('negative prompt:'):
        negative = lines[1].split(':', 1)[1].strip()
    if options is None and len(lines) > 2:
        # Fallback options line, normalize colon spacing
        opts = ', '.join(lines[2:])
        options = opts.replace(': ', ':')
    return prompt, negative, options, raw


def on_recipe_input_change(recipe_input: str, _):
    """
    Handle recipe input change, parsing first line for image filename and metadata for prompts.
    Returns list of updated values matching Gradio component order.
    """
    parts = recipe_input.splitlines()
    first_line = parts[0] if parts else ''
    img = ''
    if ':' in first_line:
        img = first_line.split(':', 1)[1]
    base = [None, img, img, None, None, None, None, None]
    metadata = recipe_input[len(first_line) + 1 :]
    ap, an, ao, ag = analyze_prompt(metadata)
    prompt_update = {'value': ap or ''}
    negative_update = {'value': an or ''}
    option_update = {'value': ao or ''}
    output_update = {'value': ag}
    return base + [prompt_update, negative_update, option_update, output_update]


def get_recipe_information(select_name):
    """
    Retrieve recipe data fields for given recipe name.
    """
    from . import recipe

    data = recipe.get_recipe(select_name)
    if not data:
        return "", "", "", "", "", "", None
    desc = data.get('description', '')
    prompt = data.get('prompt') or data.get('generate', '')
    negative = data.get('negative', '')
    option = data.get('option', '')
    generate = data.get('generate', '')
    classification = data.get('classification', '')
    page = None
    return desc, prompt, negative, option, generate, classification, page


def on_recipe_gallery_select(evt):
    """
    Handle recipe gallery select event, supporting string or list evt.value.
    """
    val = getattr(evt, 'value', None)
    if isinstance(val, list) and len(val) > 1:
        name = val[1]
    elif isinstance(val, str):
        name = val
    else:
        return "", "", "", "", "", "", None, []
    info = get_recipe_information(name)
    from . import recipe

    shortcuts = recipe.get_recipe_shortcuts(name) or []
    return (*info, shortcuts)


def on_recipe_create_btn_click(
    recipe_name, recipe_desc, recipe_prompt, recipe_negative, recipe_option, recipe_classification
):
    """
    Handle create recipe button click, validating recipe name before creation.
    """
    import gradio as gr
    from . import recipe, setting

    if not recipe_name or not recipe_name.strip() or recipe_name == setting.NEWRECIPE:
        gr.Warning("Please enter a recipe name before creating.")
        return ()
    # Delegate creation
    recipe.create_recipe(
        recipe_name,
        recipe_desc,
        recipe_prompt,
        recipe_negative,
        recipe_option,
        recipe_classification,
    )
    return ()
