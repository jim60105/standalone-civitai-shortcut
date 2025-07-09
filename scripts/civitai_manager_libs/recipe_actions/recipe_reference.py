"""
Reference management and relationship handling for recipes.
"""

import os
import re
import datetime
import gradio as gr

import scripts.civitai_manager_libs.ishortcut_core as ishortcut
from ..setting import setting
from ..logging_config import get_logger

logger = get_logger(__name__)
from ..recipe_action import generate_prompt


class RecipeReferenceManager:
    """Handles recipe reference UI interactions and model synchronization."""

    def __init__(self):
        self._logger = logger

    def load_model_information(self, modelid=None, ver_index=None):
        """Load model and version info for reference management UI."""
        if modelid:
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
                    gr.update(value=setting.get_ui_typename(model_type)),
                    gr.update(choices=versions_list, value=version_name),
                    gr.update(choices=flist, value=file_name),
                    gr.update(value=triger, visible=triger_visible),
                    gr.update(visible=weight_visible),
                    gr.update(visible=insert_btn_visible),
                    gr.update(label=title_name, visible=True),
                )
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
            gr.update(value=generate_prompt(recipe_prompt, recipe_negative, recipe_option)),
        )
