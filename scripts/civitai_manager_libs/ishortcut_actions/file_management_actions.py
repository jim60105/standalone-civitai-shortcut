"""
File Management Actions Module

This module contains file management related UI event handlers
migrated from ishortcut_action.py according to the design plan.
"""

import os
import shutil
import gradio as gr
import datetime

from ..error_handler import with_error_handling
from ..exceptions import NetworkError, FileOperationError, ValidationError
from ..conditional_imports import import_manager
from ..logging_config import get_logger

logger = get_logger(__name__)

from .. import util
from .. import model
from .. import ishortcut
from .. import setting


@with_error_handling(
    fallback_value=(
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
    ),
    exception_types=(ValidationError,),
    user_message="Failed to submit filename change",
)
def on_change_filename_submit(select_fileid, select_filename, df, filenames):
    """Handle filename change submission"""
    if not select_fileid or not select_filename or len(select_filename.strip()) <= 0:
        return (
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
        )

    select_filename = util.replace_filename(select_filename.strip())
    filelist = []

    if df:
        for df_row in df:
            if str(select_fileid) == str(df_row[1]):
                df_row[2] = select_filename

            vid = df_row[1]
            vname = df_row[2]
            dn_name = f"{vid}:{vname}"
            filelist.append(dn_name)

    if filenames and select_fileid and select_filename:
        for i, filename in enumerate(filenames):
            if filename.startswith(f"{select_fileid}:"):
                filenames[i] = f"{select_fileid}:{select_filename}"

    return (
        gr.update(visible=True),
        df,
        gr.update(choices=filelist, value=filenames),
        gr.update(visible=False),
    )


@with_error_handling(
    fallback_value=None,
    exception_types=(ValidationError,),
    user_message="Failed to process downloadable files selection",
)
def on_downloadable_files_select(evt, df, filenames):
    """Handle downloadable files selection"""
    # evt.index[0] = row, evt.index[1] = column
    vid = None
    vname = None
    dn_name = None

    row = evt.index[0]
    col = evt.index[1]

    if col == 0:
        # File selection
        if df:
            vid = df[row][1]
            vname = df[row][2]
            dn_name = f"{vid}:{vname}"

        if vid:
            if filenames:
                if dn_name in filenames:
                    filenames.remove(dn_name)
                    df[row][0] = '⬜️'
                else:
                    filenames.append(dn_name)
                    df[row][0] = '✅'
            else:
                filenames = [dn_name]
                df[row][0] = '✅'

        return (
            df,
            gr.update(value=filenames),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=False),
        )

    elif col == 2:
        # Filename change
        if df:
            vid = df[row][1]
            vname = df[row][2]

        return (
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(value=vid),
            gr.update(value=vname),
            gr.update(visible=True),
        )

    return (
        df,
        gr.update(value=filenames),
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=False),
    )


def on_cs_foldername_select(evt, is_vsfolder):
    """Handle classification folder name selection"""
    if evt.value == setting.CREATE_MODEL_FOLDER:
        return (
            gr.update(visible=True),
            gr.update(visible=is_vsfolder),
            gr.update(visible=True),
            gr.update(visible=True),
        )
    return (
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
    )


@with_error_handling(
    fallback_value=None,
    exception_types=(FileOperationError,),
    user_message="Failed to open folder",
)
def on_open_folder_click(mid, vid):
    """Handle open folder button click"""
    path = model.get_default_version_folder(vid)
    if path:
        result = util.open_folder(path)
        if not result:
            # Return HTML hyperlink so user can click manually if folder cannot be opened
            logger.debug(
                f"[file_management_actions.on_open_folder_click] Failed to open folder, "
                f"returning link: {path}"
            )
            try:
                import gradio as gr
                return gr.HTML(f'<a href="file://{path}" target="_blank">Open folder: {path}</a>')
            except ImportError:
                logger.debug("Could not create HTML link, gradio not available")
                return None
        else:
            logger.debug(f"[file_management_actions.on_open_folder_click] Folder opened: {path}")
    else:
        logger.debug(
            f"[file_management_actions.on_open_folder_click] No folder found for version id: {vid}"
        )
    return None


@with_error_handling(
    fallback_value=None,
    exception_types=(FileOperationError,),
    user_message="Failed to open image folder",
)
def on_open_image_folder_click(modelid):
    """Handle open image folder button click"""
    if modelid:
        model_info = ishortcut.get_model_info(modelid)
        if model_info:
            model_name = model_info['name']
            image_folder = util.get_download_image_folder(model_name)
            if image_folder:
                util.open_folder(image_folder)


@with_error_handling(
    fallback_value=gr.update(visible=False),
    exception_types=(FileOperationError,),
    user_message="Failed to change thumbnail image",
)
def on_change_thumbnail_image_click(mid, img_idx: int, civitai_images):
    """Handle change thumbnail image button click"""
    if civitai_images and mid:
        if len(civitai_images) > int(img_idx):
            selected_image_filepath = civitai_images[int(img_idx)]

            if not os.path.isfile(selected_image_filepath):
                return gr.update(visible=False)

            ishortcut.create_thumbnail(mid, selected_image_filepath)

            current_time = datetime.datetime.now()
            return current_time

    return gr.update(visible=False)


@with_error_handling(
    fallback_value=None,
    exception_types=(FileOperationError,),
    user_message="Failed to change preview image",
)
def on_change_preview_image_click(mid, vid, img_idx: int, civitai_images):
    """Handle change preview image button click"""
    if civitai_images and vid and mid:
        if len(civitai_images) > int(img_idx):
            selected_image_filepath = civitai_images[int(img_idx)]

            if not os.path.isfile(selected_image_filepath):
                return

            # Get info path for the version
            infopath = model.get_default_version_infopath(vid)

            if not infopath:
                logger.debug(
                    "The selected version of the model has not been downloaded. "
                    "The model must be downloaded first."
                )
                return

            path, infofile = os.path.split(infopath)

            if not path or not os.path.isdir(path):
                logger.debug(
                    "The selected version of the model has not been downloaded. "
                    "The model must be downloaded first."
                )
                return

            if not f"{setting.info_suffix}{setting.info_ext}" in infofile:
                logger.debug(
                    "The selected version of the model has not been downloaded. "
                    "The model must be downloaded first."
                )
                return

            savefile_base = infofile[: infofile.rfind(f"{setting.info_suffix}{setting.info_ext}")]

            if not savefile_base:
                logger.debug(
                    "The selected version of the model has not been downloaded. "
                    "The model must be downloaded first."
                )
                return

            preview_img_filepath = os.path.join(
                path,
                f"{util.replace_filename(savefile_base)}"
                f"{setting.preview_image_suffix}{setting.preview_image_ext}",
            )

            shutil.copy(selected_image_filepath, preview_img_filepath)
