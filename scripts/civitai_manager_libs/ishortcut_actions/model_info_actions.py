"""
Model Information Actions Module

This module contains model information related UI event handlers
migrated from ishortcut_action.py according to the design plan.
"""

import os
import datetime
import gradio as gr
from typing import Optional, Any, List, Dict, Tuple

from ..error_handler import with_error_handling
from ..exceptions import NetworkError, FileOperationError, ValidationError
from ..conditional_imports import import_manager
from ..logging_config import get_logger

logger = get_logger(__name__)

from .. import util
from .. import model
from .. import civitai
from .. import ishortcut
from .. import setting
from .. import classification


@with_error_handling(
    fallback_value=None,
    exception_types=(NetworkError, FileOperationError),
    retry_count=2,
    retry_delay=2.0,
    user_message="Failed to update model information",
)
def on_update_information_btn_click(modelid, progress=None):
    """Update model information button click handler"""
    if progress is None:
        # Import gradio for Progress if not provided
        try:
            import gradio as gr
            progress = gr.Progress()
        except ImportError:
            progress = None
    
    if modelid:
        ishortcut.update_shortcut_models([modelid], progress)

        current_time = datetime.datetime.now()
        return (
            gr.update(value=modelid),
            gr.update(value=current_time),
            gr.update(value=None),
            gr.update(value=current_time),
        )
    return (
        gr.update(value=modelid),
        gr.update(visible=True),
        gr.update(value=None),
        gr.update(visible=True),
    )


@with_error_handling(
    fallback_value=datetime.datetime.now(),
    exception_types=(ValidationError,),
    user_message="Failed to update model classification",
)
def on_model_classification_update_btn_click(model_classification, modelid):
    """Update model classification button click handler"""
    if modelid:
        classification.clean_classification_shortcut(str(modelid))

    if model_classification and modelid:
        for name in model_classification:
            classification.add_classification_shortcut(name, str(modelid))
    current_time = datetime.datetime.now()
    return current_time


def on_load_saved_model(modelid=None, ver_index=None):
    """Load saved model wrapper function"""
    return load_saved_model(modelid, ver_index)


def on_versions_list_select(evt, modelid: str):
    """Version list selection handler"""
    try:
        # evt should have .index attribute
        return load_saved_model(modelid, evt.index)
    except (AttributeError, IndexError):
        logger.error(f"Invalid event data in on_versions_list_select: {evt}")
        return load_saved_model(modelid, None)


@with_error_handling(
    fallback_value=tuple([gr.update()] * 26),
    exception_types=(NetworkError, FileOperationError, ValidationError),
    user_message="Failed to load model information",
)
def load_saved_model(modelid=None, ver_index=None):
    """Load saved model information and populate UI components"""
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
        ) = ishortcut.get_model_information(modelid, None, ver_index)
        
        if model_info:
            downloaded_info = None
            is_downloaded = False
            is_visible_openfolder = False
            is_visible_changepreview = False
            is_visible_open_download_imagefolder = False
            flist = list()
            downloadable = list()
            current_time = datetime.datetime.now()

            # Update downloaded model information
            model.update_downloaded_model()

            image_folder = util.get_download_image_folder(model_info['name'])
            if image_folder:
                is_visible_open_download_imagefolder = True

            # Get classification list
            classification_list = classification.get_classification_names_by_modelid(modelid)
            ms_foldername = model_info['name']
            cs_foldername = setting.CREATE_MODEL_FOLDER
            is_vsfolder = False

            try:
                # Find current downloaded folder and determine its format
                # If there's an issue, just use defaults
                if versionid:
                    version_path = model.get_default_version_folder(str(versionid))

                    # For models with download history, get folder path info from downloaded version
                    model_path = model.get_default_model_folder(modelid)
                    use_default_folder = False
                    if not version_path and model_path:
                        version_path = model_path
                        use_default_folder = True

                    if version_path:
                        download_classification = None
                        version_parent_path = os.path.dirname(version_path)
                        model_base_folder = os.path.abspath(
                            setting.generate_type_basefolder(model_type)
                        )
                        download_foldername = os.path.basename(version_path)
                        download_parent_foldername = os.path.basename(version_parent_path)

                        if model_base_folder in version_path:
                            if version_path == model_base_folder:
                                # Current download folder is type base folder
                                pass
                            elif model_base_folder == version_parent_path:
                                # Current downloaded folder is model name folder or classification folder
                                for v in classification_list:
                                    if download_foldername == util.replace_dirname(v.strip()):
                                        download_classification = v
                                        break

                                if download_classification:
                                    cs_foldername = download_classification
                                else:
                                    ms_foldername = download_foldername
                            else:
                                # Current downloaded folder is individual version folder
                                ms_foldername = download_parent_foldername

                                # For individual folders, allow creating separate folders
                                # Individual folders should have different names
                                if not use_default_folder:
                                    vs_foldername = download_foldername

                                is_vsfolder = True
            except Exception:
                ms_foldername = model_info['name']
                cs_foldername = setting.CREATE_MODEL_FOLDER
                is_vsfolder = False

            # Suggest names based on creator and tags
            suggested_names = [ms_foldername]

            if "creator" in model_info.keys():
                creator = model_info['creator']['username']
                suggested_names.append(creator)

            if "tags" in model_info.keys():
                # Just in case
                tags = [tag for tag in model_info['tags']]
                suggested_names.extend(tags)

            downloaded_versions = model.get_model_downloaded_versions(modelid)
            if downloaded_versions:
                downloaded_info = "\n".join(downloaded_versions.values())

                if str(versionid) in downloaded_versions:
                    is_visible_openfolder = True
                    is_visible_changepreview = True

            if downloaded_info:
                is_downloaded = True

            for file in files:
                flist.append(f"{file['id']}:{file['name']}")

                primary = False
                if "primary" in file:
                    primary = file['primary']

                downloadable.append(
                    [
                        '✅',
                        file['id'],
                        file['name'],
                        file['type'],
                        round(file['sizeKB']),
                        primary,
                        file['downloadUrl'],
                    ]
                )

            note = ishortcut.get_shortcut_model_note(modelid)
            title_name = f"# {model_info['name']} : {version_name}"
            vs_foldername = setting.generate_version_foldername(
                model_info['name'], version_name, versionid
            )
            model_url = civitai.Url_Page() + str(modelid)

            images_url = ishortcut.get_version_description_gallery(modelid, version_info)

            return (
                gr.update(value=versionid),
                gr.update(value=model_url),
                gr.update(visible=is_downloaded),
                gr.update(value=downloaded_info),
                gr.update(value=setting.get_ui_typename(model_type)),
                gr.update(value=model_basemodels),
                gr.update(choices=versions_list, value=version_name),
                gr.update(value=dhtml),
                gr.update(value=triger),
                gr.update(choices=flist if flist else [], value=flist if flist else []),
                downloadable if len(downloadable) > 0 else None,
                gr.update(label=title_name),
                current_time,
                images_url,
                gr.update(value=None),
                gr.update(visible=is_visible_openfolder),
                gr.update(visible=is_visible_changepreview),
                gr.update(visible=is_visible_open_download_imagefolder),
                gr.update(
                    choices=classification.get_list(), value=classification_list, interactive=True
                ),
                gr.update(
                    value=is_vsfolder,
                    visible=True if cs_foldername == setting.CREATE_MODEL_FOLDER else False,
                ),
                gr.update(value=vs_foldername, visible=is_vsfolder),
                gr.update(
                    choices=[setting.CREATE_MODEL_FOLDER] + classification.get_list(),
                    value=cs_foldername,
                ),
                gr.update(
                    value=ms_foldername,
                    visible=True if cs_foldername == setting.CREATE_MODEL_FOLDER else False,
                ),
                gr.update(visible=False),
                gr.update(
                    choices=suggested_names,
                    value=ms_foldername,
                    visible=True if cs_foldername == setting.CREATE_MODEL_FOLDER else False,
                ),
                gr.update(value=note),
            )

    # Clear model information if no model info available
    return (
        gr.update(value=None),
        gr.update(value=None),
        gr.update(visible=False),
        gr.update(value=None),
        gr.update(value=None),
        gr.update(value=None),
        gr.update(choices=[setting.NORESULT], value=setting.NORESULT),
        gr.update(value=None),
        gr.update(value=None),
        gr.update(value=None),
        None,
        gr.update(label="#"),
        None,
        None,
        gr.update(value=None),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(choices=classification.get_list(), value=[], interactive=True),
        gr.update(value=False, visible=True),
        gr.update(value="", visible=False),
        gr.update(
            choices=[setting.CREATE_MODEL_FOLDER] + classification.get_list(),
            value=setting.CREATE_MODEL_FOLDER,
        ),
        gr.update(value=None),
        gr.update(visible=False),
        gr.update(choices=None, value=None),
        gr.update(value=None),
    )


@with_error_handling(
    fallback_value=None,
    exception_types=(NetworkError, ValidationError),
    retry_count=1,
    user_message="Failed to save personal note",
)
def on_personal_note_save_click(modelid, note):
    """
    Handle personal note save click event.
    
    Args:
        modelid (str): Model ID
        note (str): Personal note text
    """
    ishortcut.update_shortcut_model_note(modelid, note)
