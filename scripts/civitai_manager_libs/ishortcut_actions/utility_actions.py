"""
Utility Actions Module

This module contains utility functions and misc actions
migrated from ishortcut_action.py according to the design plan.
"""

import datetime

from ..error_handler import with_error_handling
from ..exceptions import NetworkError, FileOperationError, ValidationError
from ..conditional_imports import import_manager
from ..logging_config import get_logger
from ..compat.compat_layer import CompatibilityLayer

logger = get_logger(__name__)

from .. import util
from .. import model
from .. import ishortcut
from .. import setting

# Compatibility layer variables
_compat_layer = None


def set_compatibility_layer(compat_layer):
    """Set compatibility layer"""
    global _compat_layer
    _compat_layer = compat_layer


@with_error_handling(
    fallback_value=datetime.datetime.now(),
    exception_types=(FileOperationError,),
    user_message="Failed to delete shortcut",
)
def on_shortcut_del_btn_click(model_id):
    """Handle shortcut deletion button click"""
    if model_id:
        ishortcut.delete_shortcut_model(model_id)
    current_time = datetime.datetime.now()
    return current_time


@with_error_handling(
    fallback_value=None,
    exception_types=(NetworkError, FileOperationError, ValidationError),
    retry_count=2,
    retry_delay=2.0,
    user_message="Failed to upload shortcuts by files",
)
def upload_shortcut_by_files(files, register_information_only, progress):
    """Upload shortcuts from file list"""
    modelids = list()
    if files:
        shortcuts = []
        add_ISC = dict()

        for file in files:
            shortcuts = util.load_InternetShortcut(file.name)
            if shortcuts:
                for shortcut in shortcuts:
                    model_id = util.get_model_id_from_url(shortcut)
                    if model_id:
                        modelids.append(model_id)

        for model_id in progress.tqdm(modelids, desc=f"Civitai Shortcut"):
            if model_id:
                add_ISC = ishortcut.add(add_ISC, model_id, register_information_only, progress)

        ISC = ishortcut.load()
        if ISC:
            ISC.update(add_ISC)
        else:
            ISC = add_ISC
        ishortcut.save(ISC)

    return modelids


@with_error_handling(
    fallback_value=None,
    exception_types=(NetworkError, FileOperationError, ValidationError),
    retry_count=2,
    retry_delay=2.0,
    user_message="Failed to upload shortcuts by URLs",
)
def upload_shortcut_by_urls(urls, register_information_only, progress):
    """Upload shortcuts from URL list"""
    logger.debug("[utility_actions] ========== UPLOAD_SHORTCUT_BY_URLS START ==========")
    logger.debug(f"[utility_actions] Function called with urls: {urls}")
    logger.debug(
        f"[utility_actions] urls type: {type(urls)}, length: {len(urls) if urls else 'None'}"
    )
    logger.debug(f"[utility_actions] register_information_only: {register_information_only}")
    logger.debug(f"[utility_actions] progress: {progress}")
    logger.debug(f"[utility_actions] progress type: {type(progress)}")

    if hasattr(progress, 'tqdm'):
        logger.debug(f"[utility_actions] progress.tqdm: {progress.tqdm}")
    else:
        logger.debug("[utility_actions] progress does NOT have tqdm method!")

    try:
        # Send initial progress signal to establish connection and keep alive
        try:
            progress(0, desc="Starting model registration...", total=len(urls))
        except Exception:
            pass

        modelids = list()
        logger.debug(f"[utility_actions] Initialized empty modelids list: {modelids}")

        if urls:
            logger.debug(f"[utility_actions] URLs provided, processing...")
            add_ISC = dict()
            logger.debug(f"[utility_actions] Initialized empty add_ISC dict: {add_ISC}")

            logger.debug(f"[utility_actions] About to process urls: {urls}")

            try:
                logger.debug("[utility_actions] Processing URLs with progress keep-alive")

                for i, url in enumerate(urls):
                    # Update progress to keep connection alive
                    try:
                        progress((i + 1) / len(urls), desc=f"Processing URL {i+1}/{len(urls)}")
                    except Exception:
                        pass

                    logger.debug(f"[utility_actions] Processing URL {i+1}: {url}")
                    url_stripped = url.strip()
                    logger.debug(f"[utility_actions] Stripped URL: {url_stripped}")

                    if url_stripped:
                        model_id = util.get_model_id_from_url(url_stripped)
                        logger.debug(f"[utility_actions] Extracted model_id: {model_id}")

                        if model_id:
                            modelids.append(model_id)
                            logger.debug(f"[utility_actions] Added model_id to list: {model_id}")
                        else:
                            logger.debug(f"[utility_actions] Could not extract model_id from: {url_stripped}")
                    else:
                        logger.debug(f"[utility_actions] Empty URL after stripping: {url}")

                logger.debug(f"[utility_actions] Final modelids list: {modelids}")

                for i, model_id in enumerate(modelids):
                    try:
                        progress((i + 1) / len(modelids), desc=f"Registering model {i+1}/{len(modelids)}")
                    except Exception:
                        pass

                    logger.debug(f"[utility_actions] Processing model_id {i+1}: {model_id}")
                    if model_id:
                        add_ISC = ishortcut.add(add_ISC, model_id, register_information_only, progress)
                        logger.debug(f"[utility_actions] Added to ISC: {model_id}")

                ISC = ishortcut.load()
                if ISC:
                    ISC.update(add_ISC)
                else:
                    ISC = add_ISC
                ishortcut.save(ISC)
                logger.debug("[utility_actions] Saved ISC data")

            except Exception as e:
                logger.debug(f"[utility_actions] INNER EXCEPTION in upload_shortcut_by_urls: {e}")
                logger.debug(f"[utility_actions] Inner exception type: {type(e)}")

        else:
            logger.debug("[utility_actions] No URLs provided")

        logger.debug(f"[utility_actions] Returning modelids: {modelids}")
        logger.debug(
            "[utility_actions] ========== UPLOAD_SHORTCUT_BY_URLS END (SUCCESS) =========="
        )
        return modelids

    except Exception as e:
        logger.debug(f"[utility_actions] OUTER EXCEPTION in upload_shortcut_by_urls: {e}")
        logger.debug(f"[utility_actions] Outer exception type: {type(e)}")
        logger.debug(
            "[utility_actions] ========== UPLOAD_SHORTCUT_BY_URLS END (EXCEPTION) =========="
        )
        return None


def scan_downloadedmodel_to_shortcut(progress):
    """Scan downloaded models and add to shortcuts"""
    if model.Downloaded_Models:
        modelid_list = [k for k in model.Downloaded_Models]
        ishortcut.update_shortcut_models(modelid_list, progress)


def _create_send_to_buttons():
    """Create send to buttons with compatibility layer support"""
    compat = CompatibilityLayer.get_compatibility_layer()

    # Try to use WebUI's parameter copy-paste functionality
    if compat and compat.is_webui_mode():
        infotext_utils = import_manager.get_webui_module('infotext_utils')
        if infotext_utils and hasattr(infotext_utils, 'create_buttons'):
            try:
                return infotext_utils.create_buttons(["txt2img", "img2img", "inpaint", "extras"])
            except Exception as e:
                logger.debug(f"Failed to create WebUI send buttons: {e}")

    # Fallback: Create basic buttons for standalone mode
    try:
        import gradio as gr
        return {
            "txt2img": gr.Button(value="Send to txt2img", visible=False),
            "img2img": gr.Button(value="Send to img2img", visible=False),
            "inpaint": gr.Button(value="Send to inpaint", visible=False),
            "extras": gr.Button(value="Send to extras", visible=False),
        }
    except ImportError:
        logger.debug("Gradio not available for button creation")
        return {}


def _bind_send_to_buttons(send_to_buttons, hidden, img_file_info):
    """Bind send to buttons with compatibility layer support"""
    compat = CompatibilityLayer.get_compatibility_layer()

    # Try to use WebUI's parameter binding
    if compat and compat.is_webui_mode():
        infotext_utils = import_manager.get_webui_module('infotext_utils')
        if infotext_utils and hasattr(infotext_utils, 'bind_buttons'):
            try:
                return infotext_utils.bind_buttons(
                    send_to_buttons, 
                    hidden, 
                    img_file_info
                )
            except Exception as e:
                logger.debug(f"Failed to bind WebUI send buttons: {e}")

    # Fallback: Basic button handling for standalone mode
    # In standalone mode, these buttons won't do anything meaningful
    logger.debug("Send to buttons not functional in standalone mode")
