"""
Model Action Module - Dual Mode Compatible

This module has been modified to support both AUTOMATIC1111 and standalone modes
through the compatibility layer.
"""

import os
import json
import gradio as gr
import datetime

from . import util
from . import model
from . import setting
from .error_handler import with_error_handling
from .exceptions import (
    NetworkError,
    FileOperationError,
    ValidationError,
)
import scripts.civitai_manager_libs.ishortcut_core as ishortcut
from .compat.compat_layer import CompatibilityLayer  # noqa: F401

from .logging_config import get_logger

# Module logger for this component
logger = get_logger(__name__)

# from . import civitai

# Compatibility layer variables
_compat_layer = None


def set_compatibility_layer(compat_layer):
    """Set compatibility layer"""
    global _compat_layer
    _compat_layer = compat_layer


def on_ui():

    with gr.Column(scale=1):
        with gr.Accordion("", open=True) as model_title_name:
            update_modelfolder_btn = gr.Button(
                value="Reload Model Information", variant="primary", visible=True
            )
            with gr.Row():
                download_imagefolder = gr.Button(
                    value="Open Download Image Folder",
                    variant="primary",
                    visible=util.should_show_open_folder_buttons(),
                )
                saved_infofolder = gr.Button(
                    value="Open Saved Information Folder",
                    variant="primary",
                    visible=util.should_show_open_folder_buttons(),
                )

            downloaded_information = gr.DataFrame(
                headers=["Version ID", "Version Name", "Location"],
                datatype=["str", "str", "str"],
                col_count=(3, "fixed"),
                interactive=False,
                type="array",
            )

        with gr.Accordion("", open=True, visible=False) as version_title_name:
            version_location = gr.Textbox(label="Version file location", interactive=False)
            downloaded_files = gr.DataFrame(
                headers=["File Id", "Filename", "Type", "Downloaded"],
                datatype=["str", "str", "str", "str"],
                col_count=(4, "fixed"),
                interactive=False,
                type="array",
            )
            download_openfolder = gr.Button(
                value="Open Folder",
                variant="primary",
                visible=util.should_show_open_folder_buttons(),
            )
            version_info = gr.JSON(label="Version information")

    with gr.Row(visible=False):
        selected_model_id = gr.Textbox()
        refresh_information = gr.Textbox()

    update_modelfolder_btn.click(
        fn=on_update_modelfolder_btn_click, inputs=None, outputs=refresh_information
    )

    downloaded_information.select(
        fn=on_downloaded_information_select,
        inputs=[downloaded_information],
        outputs=[version_title_name, version_location, downloaded_files, version_info],
    )

    selected_model_id.change(
        fn=on_load_model,
        inputs=[
            selected_model_id,
        ],
        outputs=[
            model_title_name,
            downloaded_information,
            version_title_name,
            version_location,
            downloaded_files,
            version_info,
        ],
    )

    refresh_information.change(
        fn=on_load_model,
        inputs=[
            selected_model_id,
        ],
        outputs=[
            model_title_name,
            downloaded_information,
            version_title_name,
            version_location,
            downloaded_files,
            version_info,
        ],
        show_progress=False,
    )

    if util.should_show_open_folder_buttons():
        download_openfolder.click(on_download_openfolder_click, [version_location], None)
        download_imagefolder.click(on_download_imagefolder_click, [selected_model_id], None)
        saved_infofolder.click(on_saved_infofolder_click, [selected_model_id], None)

    return selected_model_id, refresh_information


@with_error_handling(
    fallback_value=datetime.datetime.now(),
    exception_types=(FileOperationError,),
    retry_count=1,
    user_message="Failed to update model folder",
)
def on_update_modelfolder_btn_click():
    model.update_downloaded_model()
    current_time = datetime.datetime.now()
    return current_time


@with_error_handling(
    fallback_value=None,
    exception_types=(FileOperationError, NetworkError),
    user_message="Failed to open image folder",
)
def on_download_imagefolder_click(modelid):
    if modelid:
        # model_info = civitai.get_model_info(modelid)
        model_info = ishortcut.modelprocessor.get_model_info(modelid)
        if model_info:
            model_name = model_info['name']
            image_folder = util.get_download_image_folder(model_name)
            if image_folder:
                util.open_folder(image_folder)


@with_error_handling(
    fallback_value=None,
    exception_types=(FileOperationError,),
    user_message="Failed to open info folder",
)
def on_saved_infofolder_click(modelid):
    if modelid:
        model_path = os.path.join(setting.shortcut_info_folder, modelid)
        if model_path:
            if os.path.exists(model_path):
                util.open_folder(model_path)


def on_download_openfolder_click(vlocation):
    if vlocation:
        path = os.path.dirname(vlocation)
        if path:
            util.open_folder(path)


@with_error_handling(
    fallback_value=(gr.update(label="", visible=False), None, None, None),
    exception_types=(FileOperationError, ValidationError),
    user_message="Failed to load download information",
)
def on_downloaded_information_select(evt: gr.SelectData, df):
    logger.debug(f"on_downloaded_information_select index: {evt.index}")
    vname = None
    vlocation = None
    contents = None
    file_list = None
    base_folder = None

    if df:
        vlocation = df[evt.index[0]][2]
        vname = df[evt.index[0]][1]
        base_folder = os.path.dirname(vlocation)
        if os.path.isfile(vlocation):
            try:
                with open(vlocation, 'r') as f:
                    contents = json.load(f)
                if 'id' not in contents.keys():
                    contents = None
            except Exception:
                pass

        if contents:
            file_list = list()
            if "files" in contents:
                for file in contents['files']:
                    file_list.append(
                        [
                            file['id'],
                            file['name'],
                            file['type'],
                            (
                                "Downloaded"
                                if os.path.isfile(os.path.join(base_folder, file['name']))
                                else ""
                            ),
                        ]
                    )

    if vlocation:
        return (
            gr.update(label=vname, visible=True),
            vlocation,
            file_list if len(file_list) > 0 else None,
            contents,
        )
    else:
        return gr.update(label=vname, visible=False), vlocation, None, contents


@with_error_handling(
    fallback_value=(
        gr.update(label=None, visible=False),
        None,
        gr.update(label=None, visible=False),
        None,
        None,
        None,
    ),
    exception_types=(FileOperationError, NetworkError),
    user_message="Failed to load model",
)
def on_load_model(modelid=None):
    title_name = None
    data_list = list()

    if modelid:
        model.update_downloaded_model()
        title_name, data_list = get_model_information(modelid)

    return (
        gr.update(label=title_name),
        gr.update(value=data_list),
        gr.update(label=None, visible=False),
        None,
        None,
        None,
    )


def get_model_information(modelid: str = None):
    if modelid:
        # model_info = civitai.get_model_info(modelid)
        model_info = ishortcut.modelprocessor.get_model_info(modelid)
        if model_info:
            title_name = f"{model_info['name']}"

            downloaded_versions = model.get_model_downloaded_versions(modelid)
            versions_list = list()
            if downloaded_versions:
                for vid, name in downloaded_versions.items():
                    info_list = model.get_infopaths(str(vid))
                    if info_list:
                        for path in info_list:
                            versions_list.append([vid, name, path])
                            logger.debug(f"{vid} : {name} : {path}")
            return title_name, versions_list if len(versions_list) > 0 else None
    return None, None
