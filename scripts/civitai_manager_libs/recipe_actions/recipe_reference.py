"""
Reference management and relationship handling for recipes.
"""

import os
import re
import datetime
import gradio as gr

try:
    import scripts.civitai_manager_libs.ishortcut_core as ishortcut
except ImportError:
    ishortcut = None

from .. import settings
from ..logging_config import get_logger

logger = get_logger(__name__)


class RecipeReferenceManager:
    """Handles recipe reference UI interactions and model synchronization."""

    def __init__(self):
        self._logger = logger

    def get_recipe_references(self, recipe_id: str) -> list:
        """Get list of references for a recipe."""
        from .. import recipe

        recipe_data = recipe.get_recipe(recipe_id)
        if recipe_data and isinstance(recipe_data, dict):
            return recipe_data.get('shortcuts', [])
        return []

    def add_recipe_reference(self, recipe_id: str, ref_data: dict) -> bool:
        """Add a reference to a recipe."""
        try:
            from .. import recipe

            recipe_data = recipe.get_recipe(recipe_id)
            if not recipe_data:
                return False

            shortcuts = recipe_data.get('shortcuts', [])
            model_id = ref_data.get('model_id')
            if model_id and model_id not in shortcuts:
                shortcuts.append(model_id)
                recipe_data['shortcuts'] = shortcuts
                # Update recipe
                recipe.update_recipe(
                    recipe_id,
                    recipe_data.get('name'),
                    recipe_data.get('description'),
                    recipe_data.get('prompt'),
                    recipe_data.get('classification'),
                )
                return True
            return False
        except Exception as e:
            self._logger.error("Failed to add recipe reference: %s", e)
            return False

    def remove_recipe_reference(self, recipe_id: str, ref_id: str) -> bool:
        """Remove a reference from a recipe."""
        try:
            from .. import recipe

            recipe_data = recipe.get_recipe(recipe_id)
            if not recipe_data:
                return False

            shortcuts = recipe_data.get('shortcuts', [])
            if ref_id in shortcuts:
                shortcuts.remove(ref_id)
                recipe_data['shortcuts'] = shortcuts
                # Update recipe
                recipe.update_recipe(
                    recipe_id,
                    recipe_data.get('name'),
                    recipe_data.get('description'),
                    recipe_data.get('prompt'),
                    recipe_data.get('classification'),
                )
                return True
            return False
        except Exception as e:
            self._logger.error("Failed to remove recipe reference: %s", e)
            return False

    def update_recipe_reference(self, ref_id: str, ref_data: dict) -> bool:
        """Update a recipe reference."""
        # This method might need more context about how references are stored
        self._logger.warning("update_recipe_reference not fully implemented")
        return False

    def sync_references_with_models(self, recipe_id: str) -> bool:
        """Sync recipe references with available models."""
        # This method might need more context about model availability
        self._logger.warning("sync_references_with_models not fully implemented")
        return False

    def load_model_information(self, modelid=None, ver_index=None):
        """Load model and version info for reference management UI."""
        if modelid and ishortcut and hasattr(ishortcut, 'modelprocessor'):
            try:
                (
                    model_info,
                    version_info,
                    versionid,
                    version_name,
                    model_type,
                    model_basemodels,
                    versions_list,
                    dhtml,
                    triger,
                    files,
                ) = ishortcut.modelprocessor.get_model_information(modelid, None, ver_index)
                if model_info:
                    insert_btn_visible = False
                    weight_visible = False
                    triger_visible = False
                    if model_type in ('LORA', 'LoCon', 'Hypernetwork'):
                        insert_btn_visible = True
                        weight_visible = True
                        triger_visible = True
                    elif model_type == 'TextualInversion':
                        insert_btn_visible = True

                    flist = [f['name'] for f in files]
                    file_name = flist[0] if flist else ''
                    title_name = f"# {model_info['name']} : {version_name}"
                    return (
                        gr.update(value=model_type),
                        gr.update(value=settings.get_ui_typename(model_type)),
                        gr.update(choices=versions_list, value=version_name),
                        gr.update(choices=flist, value=file_name),
                        gr.update(value=triger, visible=triger_visible),
                        gr.update(visible=weight_visible),
                        gr.update(visible=insert_btn_visible),
                        gr.update(label=title_name, visible=True),
                    )
            except AttributeError:
                self._logger.error("ishortcut.modelprocessor not available")
            except Exception as e:
                self._logger.error("Failed to load model information: %s", e)
        return (
            None,
            None,
            None,
            None,
            gr.update(value=None, visible=True),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(label="#", visible=False),
        )

    def on_reference_modelid_change(self, modelid=None):
        """Gradio: handle model ID change in reference UI."""
        return self.load_model_information(modelid, None)

    def on_reference_versions_select(self, evt: gr.SelectData, modelid: str):
        """Gradio: handle version selection change in reference UI."""
        return self.load_model_information(modelid, evt.index)

    def on_delete_reference_model_btn_click(self, sc_model_id: str, shortcuts):
        """Gradio: delete a model shortcut from reference list."""
        if sc_model_id:
            now = datetime.datetime.now()
            if not shortcuts:
                shortcuts = []
            if sc_model_id in shortcuts:
                shortcuts.remove(sc_model_id)
                return shortcuts, now, None, None
        return (
            shortcuts,
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
        )

    def on_close_reference_model_information_btn_click(self, shortcuts):
        """Gradio: close reference model information panel."""
        now = datetime.datetime.now()
        return shortcuts, now, None, None

    def add_string(self, text, mtype, filename, weight, triger=None):
        """Add model reference syntax string to prompt text."""
        pattern = f"<{mtype}:{filename}:{weight}>"
        if triger:
            pattern += ' ' + triger
        return text.strip() + ' ' + pattern

    def remove_strings(self, text, mtype, filename, triger=None):
        """Remove model reference syntax strings from prompt text."""
        pattern = f"<{mtype}:{re.escape(filename)}:.*?>"
        if triger:
            pattern += ' ' + triger
        return re.sub(pattern, '', text)

    def is_string(self, text, mtype, filename, triger=None):
        """Check if model reference syntax exists in prompt text."""
        pattern = f"<{mtype}:{re.escape(filename)}:.*?>"
        if triger:
            pattern += ' ' + triger
        return re.search(pattern, text)

    def on_insert_prompt_btn_click(
        self, model_type, recipe_prompt, recipe_negative, recipe_option, filename, weight, triger
    ):
        """Gradio: handle insert/remove prompt button click for references."""
        # Import generate_prompt from utilities to avoid circular import
        from .recipe_utilities import RecipeUtilities

        if model_type in ('LORA', 'LoCon'):
            mtype = 'lora'
        elif model_type == 'Hypernetwork':
            mtype = 'hypernet'
        elif model_type == 'TextualInversion':
            mtype = 'ti'
        else:
            mtype = None

        if filename:
            filename, _ = os.path.splitext(filename)

        if mtype in ('lora', 'hypernet'):
            if self.is_string(recipe_prompt, mtype, filename, triger):
                recipe_prompt = self.remove_strings(recipe_prompt, mtype, filename, triger)
            else:
                recipe_prompt = self.remove_strings(recipe_prompt, mtype, filename)
                recipe_prompt = self.add_string(recipe_prompt, mtype, filename, weight, triger)
        elif mtype == 'ti':
            if filename in recipe_prompt:
                recipe_prompt = recipe_prompt.replace(filename, '')
            else:
                recipe_prompt = recipe_prompt.replace(filename, '')
                recipe_prompt = recipe_prompt + ' ' + filename

        return (
            gr.update(value=recipe_prompt),
            gr.update(
                value=RecipeUtilities.generate_prompt(recipe_prompt, recipe_negative, recipe_option)
            ),
        )

    def on_reference_gallery_loading(self, shortcuts):
        """Gradio: load gallery images for reference shortcuts."""
        if not ishortcut or not hasattr(ishortcut, 'shortcutcollectionmanager'):
            return None

        try:
            shortcut_manager = getattr(ishortcut, 'shortcutcollectionmanager', None)
            if not shortcut_manager or not hasattr(shortcut_manager, 'load_shortcuts'):
                return None
            ISC = shortcut_manager.load_shortcuts()
        except (AttributeError, TypeError):
            return None

        if not ISC:
            return None

        result_list = None

        if shortcuts:
            result_list = list()
            for mid in shortcuts:
                if str(mid) in ISC.keys():
                    v = ISC[str(mid)]
                    try:
                        image_processor = getattr(ishortcut, 'imageprocessor', None)
                        has_image = (
                            image_processor
                            and hasattr(image_processor, 'is_sc_image')
                            and image_processor.is_sc_image(v['id'])
                        )
                    except (AttributeError, TypeError):
                        has_image = False

                    if has_image:
                        if 'nsfw' in v.keys() and bool(v['nsfw']) and settings.nsfw_filter_enable:
                            result_list.append(
                                (
                                    settings.get_nsfw_disable_image,
                                    settings.set_shortcutname(v['name'], v['id']),
                                )
                            )
                        else:
                            result_list.append(
                                (
                                    os.path.join(
                                        settings.shortcut_thumbnail_folder,
                                        f"{v['id']}{settings.PREVIEW_IMAGE_EXT}",
                                    ),
                                    settings.set_shortcutname(v['name'], v['id']),
                                )
                            )
                    else:
                        result_list.append(
                            (
                                settings.no_card_preview_image,
                                settings.set_shortcutname(v['name'], v['id']),
                            )
                        )
                else:
                    result_list.append(
                        (settings.no_card_preview_image, settings.set_shortcutname("delete", mid))
                    )

        return gr.update(value=result_list)

    def on_reference_sc_gallery_select(self, evt: gr.SelectData, shortcuts):
        """Gradio: handle selection from shortcut gallery for references with error handling."""
        import datetime
        from ..error_handler import with_error_handling
        from ..exceptions import ValidationError

        @with_error_handling(
            fallback_value=([], datetime.datetime.now()),
            exception_types=(ValidationError,),
            user_message="Failed to process reference selection",
        )
        def _handle_selection():
            nonlocal shortcuts
            current_time = datetime.datetime.now()

            if evt.value:
                # evt.value can be Gradio v4+ FileData dict,
                # v3.41+ list [image_url, shortcut_name], or legacy string
                if isinstance(evt.value, dict) and 'caption' in evt.value:
                    shortcut = evt.value['caption']
                elif isinstance(evt.value, list) and len(evt.value) > 1:
                    shortcut = evt.value[1]
                elif isinstance(evt.value, str):
                    shortcut = evt.value
                else:
                    self._logger.debug("Unexpected evt.value format: %s", evt.value)
                    return shortcuts, current_time

                sc_model_id = settings.get_modelid_from_shortcutname(shortcut)

                if not shortcuts:
                    shortcuts = list()

                if sc_model_id not in shortcuts:
                    shortcuts.append(sc_model_id)

                return shortcuts, current_time
            return shortcuts, gr.update(visible=False)

        return _handle_selection()

    def on_reference_gallery_select(self, evt: gr.SelectData, shortcuts, delete_opt=True):
        """Gradio: handle gallery selection for reference management."""
        if evt.value:
            # evt.value can be Gradio v4+ FileData dict,
            # v3.41+ list [image_url, shortcut_name], or legacy string
            if isinstance(evt.value, dict) and 'caption' in evt.value:
                shortcut = evt.value['caption']
            elif isinstance(evt.value, list) and len(evt.value) > 1:
                shortcut = evt.value[1]
            elif isinstance(evt.value, str):
                shortcut = evt.value
            else:
                self._logger.debug("Unexpected evt.value format: %s", evt.value)
                return shortcuts, gr.update(visible=False), gr.update(visible=True), None

            sc_model_id = settings.get_modelid_from_shortcutname(shortcut)
            current_time = datetime.datetime.now()

            if not shortcuts:
                shortcuts = list()

            if delete_opt and sc_model_id in shortcuts:
                shortcuts.remove(sc_model_id)
                return shortcuts, current_time, None, None

            return shortcuts, gr.update(visible=False), gr.update(visible=True), sc_model_id

        return shortcuts, gr.update(visible=False), gr.update(visible=True), None


# Global instance for delegation
_recipe_reference_manager = RecipeReferenceManager()
