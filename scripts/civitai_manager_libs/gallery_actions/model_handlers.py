"""
Gallery Model Handlers - Model information and version management.

This module handles model-related events and information retrieval.
"""

import gradio as gr
from typing import Optional, Tuple, List, Dict, Any

from ..logging_config import get_logger
from .. import setting, ishortcut, util
from ..error_handler import with_error_handling

logger = get_logger(__name__)


def extract_model_info(page_url: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract model ID and version ID from page URL."""
    # This function needs to be imported from original module
    # Placeholder implementation
    return None, None


def get_default_page_url(modelid: str, versionid: Optional[str], is_user: bool) -> str:
    """Get default page URL for model."""
    # This function needs to be imported from original module
    # Placeholder implementation
    return ""


def get_paging_information_working(
    modelid: str, versionid: Optional[str], is_user: bool
) -> Optional[Dict]:
    """Get paging information for model gallery."""
    # This function needs to be imported from original module
    # Placeholder implementation
    return None


@with_error_handling()
def on_selected_model_id_change(modelid: str) -> Tuple[Any, ...]:
    """Handle model ID selection change."""
    page_url = None
    versions_list = None
    title_name = None
    version_name = None
    paging_information = None
    is_image_folder = False

    if modelid:
        page_url = get_default_page_url(modelid, None, False)
        model_name, versions_list, version_name, paging_information = get_model_information(
            page_url
        )

        title_name = f"# {model_name}"
        if paging_information:
            total_page = paging_information["totalPages"]
        else:
            total_page = 0

        image_folder = util.get_download_image_folder(model_name)
        if image_folder:
            is_image_folder = True

    return (
        gr.update(label=title_name),
        page_url,
        gr.update(
            choices=[setting.PLACEHOLDER] + versions_list if versions_list else None,
            value=version_name if version_name else setting.PLACEHOLDER,
        ),
        gr.update(
            minimum=1, maximum=total_page, value=1, step=1, label=f"Total {total_page} Pages"
        ),
        paging_information,
        gr.update(visible=is_image_folder),
    )


@with_error_handling()
def on_versions_list_select(evt: gr.SelectData, modelid: Optional[str] = None) -> Tuple[Any, ...]:
    """Handle version list selection."""
    page_url = None
    versions_list = None
    title_name = None
    version_name = None
    paging_information = None

    if modelid:
        if evt.index > 0:
            ver_index = evt.index - 1
            model_info = ishortcut.get_model_info(modelid)
            version_info = dict()
            if model_info:
                if "modelVersions" in model_info.keys():
                    if len(model_info["modelVersions"]) > 0:
                        version_info = model_info["modelVersions"][ver_index]
                        if version_info["id"]:
                            versionid = version_info["id"]
                            page_url = get_default_page_url(modelid, versionid, False)
        else:
            page_url = get_default_page_url(modelid, None, False)

        model_name, versions_list, version_name, paging_information = get_model_information(
            page_url
        )
        title_name = f"# {model_name}"
        if paging_information:
            total_page = paging_information["totalPages"]
        else:
            total_page = 0

    return (
        gr.update(label=title_name),
        page_url,
        gr.update(
            choices=[setting.PLACEHOLDER] + versions_list if versions_list else None,
            value=version_name if version_name else setting.PLACEHOLDER,
        ),
        gr.update(
            minimum=1, maximum=total_page, value=1, step=1, label=f"Total {total_page} Pages"
        ),
        paging_information,
    )


@with_error_handling()
def get_model_information(
    page_url: Optional[str] = None,
) -> Tuple[Optional[str], Optional[List], Optional[str], Optional[Dict]]:
    """Get model information from page URL."""
    model_info = None
    version_name = None
    modelid = None
    versionid = None

    if page_url:
        modelid, versionid = extract_model_info(page_url)

    if modelid:
        model_info = ishortcut.get_model_info(modelid)

    if model_info:
        model_name = model_info['name']

        versions_list = list()
        if 'modelVersions' in model_info:
            for ver in model_info['modelVersions']:
                versions_list.append(ver['name'])
                if versionid:
                    if versionid == str(ver['id']):
                        version_name = ver['name']

        paging_information = get_paging_information_working(modelid, versionid, False)

        return model_name, versions_list, version_name, paging_information
    return None, None, None, None
