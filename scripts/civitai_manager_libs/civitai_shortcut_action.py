# Civitai Shortcut Action Module - Dual Mode Compatible
# This module has been modified to support both AUTOMATIC1111 and standalone modes
# through the compatibility layer.

import datetime
import os
import gradio as gr

from .error_handler import with_error_handling
from .exceptions import (
    NetworkError,
    FileOperationError,
    ConfigurationError,
    ValidationError,
)

from . import civitai
from . import gallery as civitai_gallery_action
import scripts.civitai_manager_libs.ishortcut_core as ishortcut
from . import ishortcut_action
from . import model
from . import model_action
from . import sc_browser_page
from . import settings
from .logging_config import get_logger

logger = get_logger(__name__)

_compat_layer = None


def set_compatibility_layer(compat_layer):
    """Set compatibility layer."""
    logger.debug(f"set_compatibility_layer called with: {compat_layer}")
    global _compat_layer
    _compat_layer = compat_layer


@with_error_handling(
    fallback_value=(gr.update(visible=False), gr.update(selected=None), gr.update(visible=False)),
    exception_types=(ValidationError,),
    user_message="Failed to process shortcut input",
)
def on_shortcut_input_change(shortcut_input):
    logger.debug(
        f"[civitai_shortcut_action] on_shortcut_input_change called with "
        f"shortcut_input: {shortcut_input}"
    )
    if not shortcut_input:
        logger.debug(" shortcut_input is empty or None")
        return gr.update(visible=False), gr.update(selected=None), gr.update(visible=False)
    logger.debug(" shortcut_input is valid, returning values")
    return shortcut_input, gr.update(selected="Shortcut"), None


def on_ui(recipe_input, shortcut_input, civitai_tabs):
    logger.debug(
        f"[civitai_shortcut_action] on_ui called with recipe_input: {recipe_input}, "
        f"shortcut_input: {shortcut_input}, civitai_tabs: {civitai_tabs}"
    )

    with gr.Row(visible=False):
        logger.debug(" Creating hidden Row for internal state components")
        sc_modelid = gr.Textbox()
        update_informations = gr.Textbox()
        current_information_tabs = gr.State(0)
        refresh_NSFW = gr.Textbox()

    with gr.Column(scale=settings.shortcut_browser_screen_split_ratio):
        logger.debug(
            f"[civitai_shortcut_action] Creating main UI column with scale: "
            f"{settings.shortcut_browser_screen_split_ratio}"
        )
        with gr.Tabs() as civitai_shortcut_tabs:
            logger.debug(" Creating civitai_shortcut_tabs")
            with gr.TabItem("Register Model"):
                logger.debug(" Register Model tab initialized")
                with gr.Row(visible=False):
                    register_information_only = gr.Checkbox(
                        label="Register only model information", value=False
                    )
                with gr.Row():
                    with gr.Column():
                        logger.debug(
                            "[civitai_shortcut_action] Register Model tab: Markdown, Textbox, "
                            "File components created"
                        )
                        gr.Markdown(
                            value=(
                                "Using the model URL from the Civitai site, you register the "
                                "information of the model. You can click and drag the Civitai "
                                "Model's URL or drag and drop a saved internet shortcut. "
                                "Additionally, you can select multiple internet shortcuts and "
                                "drop them all at once."
                            ),
                            visible=True,
                        )
                        civitai_internet_url_txt = gr.Textbox(
                            placeholder="Copy & Paste or Drag & Drop Civitai Model Url",
                            show_label=False,
                            interactive=True,
                        )
                        civitai_internet_url = gr.File(
                            label="Civitai Internet Shortcut",
                            file_count="multiple",
                            file_types=[".url"],
                        )

            with gr.TabItem("Model Browser"):
                logger.debug(" Model Browser tab initialized")
                with gr.Row():
                    with gr.Column():
                        logger.debug(
                            "[civitai_shortcut_action] Model Browser: calling "
                            "sc_browser_page.on_ui()"
                        )
                        sc_gallery, refresh_sc_browser, refresh_sc_gallery = sc_browser_page.on_ui()

            with gr.TabItem("Scan New Version"):
                logger.debug(" Scan New Version tab initialized")
                with gr.Row():
                    with gr.Column():
                        logger.debug(
                            "[civitai_shortcut_action] Scan New Version: Dropdown, Button, "
                            "Gallery, Markdown created"
                        )
                        shortcut_new_version_type = gr.Dropdown(
                            label="Filter Model type",
                            multiselect=True,
                            choices=[k for k in settings.UI_TYPENAMES],
                            interactive=True,
                        )
                        scan_new_version_btn = gr.Button(
                            value="Scan new version model", variant="primary"
                        )
                        sc_new_version_gallery = gr.Gallery(
                            label="SC New Version Gallery",
                            elem_id="sc_new_version_gallery",
                            show_label=False,
                            columns=settings.shortcut_column,
                            height="fit",
                            object_fit=settings.gallery_thumbnail_image_style,
                        )
                        gr.Markdown(
                            value=(
                                "The feature is to search for new versions of models on Civitai "
                                "among the downloaded ones."
                            ),
                            visible=True,
                        )
            with gr.TabItem("NSFW Filter"):
                logger.debug(" NSFW Filter tab initialized")
                with gr.Row():
                    with gr.Column():
                        logger.debug(
                            "[civitai_shortcut_action] NSFW Filter: Dropdowns and Button created"
                        )
                        nsfw_filter_enable = gr.Dropdown(
                            value="On",
                            choices=["On", "Off"],
                            label="NSFW Filtering",
                            interactive=True,
                        )
                        nsfw_level = gr.Dropdown(
                            value=settings.nsfw_level,
                            choices=settings.NSFW_LEVELS,
                            label="NSFW Filtering Level",
                            visible=True,
                            interactive=True,
                        )
                        nsfw_save_btn = gr.Button(
                            value="Save NSFW Setting", variant="primary", visible=True
                        )

    with gr.Column(
        scale=(
            settings.shortcut_browser_screen_split_ratio_max
            - settings.shortcut_browser_screen_split_ratio
        )
    ):
        scale_val = (
            settings.shortcut_browser_screen_split_ratio_max
            - settings.shortcut_browser_screen_split_ratio
        )
        logger.debug(
            f"[civitai_shortcut_action] Creating secondary UI column with scale: " f"{scale_val}"
        )
        with gr.Tabs() as civitai_information_tabs:
            logger.debug(" Creating civitai_information_tabs")
            with gr.TabItem("Model Information", id="civitai_info"):
                logger.debug(" Model Information tab initialized")
                with gr.Row():
                    shortcut_modelid, refresh_civitai_information = ishortcut_action.on_ui(
                        refresh_sc_browser, recipe_input
                    )
            with gr.TabItem("Civitai User Gallery", id="gallery_info"):
                logger.debug(" Civitai User Gallery tab initialized")
                with gr.Row():
                    gallery_modelid, refresh_gallery_information = civitai_gallery_action.on_ui(
                        recipe_input
                    )

            with gr.TabItem("Downloaded Model Information", id="download_info"):
                logger.debug(
                    "[civitai_shortcut_action] Downloaded Model Information tab initialized"
                )
                with gr.Row():
                    downloadinfo_modelid, refresh_download_information = model_action.on_ui()

    # NSFW Filter Setting Refresh
    logger.debug(" Binding refresh_NSFW.change event handler")
    refresh_NSFW.change(
        fn=on_refresh_NSFW_change,
        inputs=None,
        outputs=[nsfw_filter_enable, nsfw_level],
    )

    logger.debug(" Binding nsfw_filter_enable.select event handler")
    nsfw_filter_enable.select(
        fn=on_nsfw_filter,
        inputs=[nsfw_filter_enable, nsfw_level],
        outputs=[nsfw_level, refresh_civitai_information, refresh_gallery_information],
    )

    logger.debug(" Binding nsfw_level.select event handler")
    nsfw_level.select(
        fn=on_nsfw_filter,
        inputs=[nsfw_filter_enable, nsfw_level],
        outputs=[nsfw_level, refresh_civitai_information, refresh_gallery_information],
    )

    nsfw_save_btn.click(fn=on_nsfw_save_btn_click)
    logger.debug(" Binding nsfw_save_btn.click event handler")

    logger.debug(" Binding shortcut_input.change event handler")
    shortcut_input.change(
        fn=on_shortcut_input_change,
        inputs=[shortcut_input],
        outputs=[sc_modelid, civitai_tabs, shortcut_input],
        show_progress=False,
    )

    scan_new_version_btn.click(
        on_scan_new_version_btn, shortcut_new_version_type, sc_new_version_gallery
    )
    logger.debug(" Binding scan_new_version_btn.click event handler")
    sc_gallery.select(on_sc_gallery_select, None, [sc_modelid], show_progress=False)
    logger.debug(" Binding sc_gallery.select event handler")
    sc_new_version_gallery.select(on_sc_gallery_select, None, [sc_modelid], show_progress=False)
    logger.debug(" Binding sc_new_version_gallery.select event handler")
    civitai_shortcut_tabs.select(
        on_civitai_shortcut_tabs_select,
        None,
        [refresh_sc_browser, refresh_NSFW],
        show_progress=False,
    )
    logger.debug(" Binding civitai_shortcut_tabs.select event handler")

    logger.debug(" Binding update_informations.change event handler")
    update_informations.change(
        fn=on_sc_modelid_change,
        inputs=[sc_modelid, current_information_tabs],
        outputs=[shortcut_modelid, gallery_modelid, downloadinfo_modelid],
    )

    logger.debug(" Binding sc_modelid.change event handler")
    sc_modelid.change(
        fn=on_sc_modelid_change,
        inputs=[sc_modelid, current_information_tabs],
        outputs=[shortcut_modelid, gallery_modelid, downloadinfo_modelid],
    )

    logger.debug(" Binding civitai_information_tabs.select event handler")
    civitai_information_tabs.select(
        fn=on_civitai_information_tabs_select,
        inputs=None,
        outputs=[current_information_tabs, update_informations],
    )

    logger.debug(" Binding civitai_internet_url.upload event handler")
    civitai_internet_url.upload(
        fn=on_civitai_internet_url_upload,
        inputs=[civitai_internet_url, register_information_only],
        outputs=[sc_modelid, refresh_sc_browser, civitai_internet_url],
        show_progress=True,
    )

    logger.debug(" Binding civitai_internet_url_txt.change event handler")
    civitai_internet_url_txt.change(
        fn=on_civitai_internet_url_txt_upload,
        inputs=[civitai_internet_url_txt, register_information_only],
        outputs=[sc_modelid, refresh_sc_browser, civitai_internet_url_txt],
        show_progress=True,
    )

    return refresh_sc_browser, refresh_civitai_information


@with_error_handling(
    fallback_value=(gr.update(value="Off"), gr.update(visible=False, value="None")),
    exception_types=(ConfigurationError,),
    user_message="Failed to refresh NSFW settings",
)
def on_refresh_NSFW_change():
    logger.debug(
        f"[civitai_shortcut_action] on_refresh_NSFW_change called. "
        f"nsfw_filter_enable: {settings.nsfw_filter_enable}, "
        f"nsfw_level: {settings.nsfw_level}"
    )
    if settings.nsfw_filter_enable:
        return gr.update(value="On"), gr.update(visible=True, value=settings.nsfw_level)
    else:
        return gr.update(value="Off"), gr.update(visible=False, value=settings.nsfw_level)


@with_error_handling(
    fallback_value=(gr.update(visible=False), datetime.datetime.now(), datetime.datetime.now()),
    exception_types=(ConfigurationError,),
    user_message="Failed to apply NSFW filter",
)
def on_nsfw_filter(enable, level):
    logger.debug(
        f"[civitai_shortcut_action] on_nsfw_filter called with enable: {enable}, " f"level: {level}"
    )
    current_time = datetime.datetime.now()
    settings.set_NSFW(True if enable == "On" else False, level)
    logger.debug(f" NSFW set to: {enable == 'On'}, level: {level}")
    return (
        gr.update(visible=True if enable == "On" else False, value=level),
        current_time,
        current_time,
    )


@with_error_handling(
    fallback_value=None,
    exception_types=(FileOperationError, ConfigurationError),
    retry_count=1,
    user_message="Failed to save NSFW settings",
)
def on_nsfw_save_btn_click():
    logger.debug(" on_nsfw_save_btn_click called. Saving NSFW settings.")
    settings.save_NSFW()


def on_civitai_shortcut_tabs_select(evt: gr.SelectData):
    logger.debug(
        f"[civitai_shortcut_action] on_civitai_shortcut_tabs_select called with "
        f"evt.index: {evt.index}"
    )
    if evt.index == 1:
        current_time = datetime.datetime.now()
        logger.debug(" Model Browser tab selected, refreshing browser.")
        return current_time, gr.update(visible=False)
    elif evt.index == 3:
        current_time = datetime.datetime.now()
        logger.debug(" NSFW Filter tab selected, refreshing NSFW.")
        return gr.update(visible=False), current_time
    logger.debug(" Other tab selected, no refresh.")
    return gr.update(visible=False), gr.update(visible=False)


def on_civitai_information_tabs_select(evt: gr.SelectData):
    logger.debug(
        f"[civitai_shortcut_action] on_civitai_information_tabs_select called with "
        f"evt.index: {evt.index}"
    )
    current_time = datetime.datetime.now()
    return evt.index, current_time


# sc_gallery function definition
@with_error_handling(
    fallback_value=None,
    exception_types=(ValidationError,),
    user_message="Failed to process gallery selection",
)
def on_sc_gallery_select(evt: gr.SelectData):
    logger.debug(
        f"[civitai_shortcut_action] on_sc_gallery_select called with evt.value: {evt.value}"
    )
    sc_model_id = None
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
            logger.debug(f" Unexpected evt.value format: {evt.value}")
            return None

        sc_model_id = settings.get_modelid_from_shortcutname(shortcut)
        logger.debug(
            f"[civitai_shortcut_action] Gallery select: shortcut={shortcut}, "
            f"sc_model_id={sc_model_id}"
        )
    return sc_model_id


def on_sc_modelid_change(sc_model_id, current_information_tabs):
    logger.debug(
        f"[civitai_shortcut_action] on_sc_modelid_change called with sc_model_id: {sc_model_id}, "
        f"current_information_tabs: {current_information_tabs}"
    )
    if current_information_tabs == settings.civitai_information_tab:
        logger.debug(" Returning for civitai_information_tab")
        return sc_model_id, gr.update(visible=False), gr.update(visible=False)
    if current_information_tabs == settings.usergal_information_tab:
        logger.debug(" Returning for usergal_information_tab")
        return gr.update(visible=False), sc_model_id, gr.update(visible=False)
    if current_information_tabs == settings.download_information_tab:
        logger.debug(" Returning for download_information_tab")
        return gr.update(visible=False), gr.update(visible=False), sc_model_id
    logger.debug(" Returning default (all invisible)")
    return gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)


@with_error_handling(
    fallback_value=(gr.update(visible=False), gr.update(visible=False), None),
    exception_types=(NetworkError, FileOperationError, ValidationError),
    retry_count=2,
    retry_delay=2.0,
    user_message="Failed to upload shortcut files",
)
def on_civitai_internet_url_upload(files, register_information_only, progress=gr.Progress()):
    logger.debug(
        f"[civitai_shortcut_action] on_civitai_internet_url_upload called with files: {files}, "
        f"register_information_only: {register_information_only}"
    )
    model_id = None
    if files:
        modelids = ishortcut_action.upload_shortcut_by_files(
            files, register_information_only, progress
        )
        logger.debug(f" upload_shortcut_by_files returned: {modelids}")
        if len(modelids) > 0:
            model_id = modelids[0]

    current_time = datetime.datetime.now()
    if not model_id:
        logger.debug(
            "[civitai_shortcut_action] No model_id found after upload, returning invisible updates."
        )
        return gr.update(visible=False), gr.update(visible=False), None
    logger.debug(f" Model registered: {model_id}")
    return model_id, current_time, None


@with_error_handling(
    fallback_value=(gr.update(visible=False), None, gr.update(visible=True)),
    exception_types=(NetworkError, ValidationError, FileOperationError),
    retry_count=2,
    retry_delay=2.0,
    user_message="Failed to process URL",
)
def on_civitai_internet_url_txt_upload(
    url, register_information_only, progress=gr.Progress(track_tqdm=True)
):
    logger.debug(" ========== URL UPLOAD HANDLER START ==========")
    logger.debug(
        f"[civitai_shortcut_action] on_civitai_internet_url_txt_upload called with url: {url}, "
        f"register_information_only: {register_information_only}, progress: {progress}"
    )
    logger.debug(f" URL type: {type(url)}, URL repr: {repr(url)}")
    logger.debug(
        f"[civitai_shortcut_action] register_information_only type: "
        f"{type(register_information_only)}"
    )
    logger.debug(f" progress type: {type(progress)}")

    try:
        logger.debug(f"[civitai_shortcut_action] Using provided progress object: {type(progress)}")

        model_id = None
        logger.debug(f" Initialized model_id = {model_id}")

        if url:
            logger.debug(" URL is not None/empty, checking length...")
            logger.debug(
                f"[civitai_shortcut_action] URL stripped: '{url.strip()}', "
                f"length: {len(url.strip())}"
            )

            if len(url.strip()) > 0:
                logger.debug(
                    "[civitai_shortcut_action] URL has content, calling upload_shortcut_by_urls..."
                )
                logger.debug(
                    f"[civitai_shortcut_action] Parameters: urls=[{url}], "
                    f"register_info_only={register_information_only}, progress={progress}"
                )

                # Attempt to upload shortcut by URL with specific error handling
                # for inaccessible models
                from .exceptions import ModelNotAccessibleError
                from .ui.notification_service import get_notification_service

                try:
                    modelids = ishortcut_action.upload_shortcut_by_urls(
                        [url], register_information_only, progress
                    )

                    logger.debug(
                        f"[civitai_shortcut_action] upload_shortcut_by_urls SUCCESS, "
                        f"returned: {modelids}"
                    )
                    modelids_len = len(modelids) if modelids else 'None'
                    logger.debug(
                        f"[civitai_shortcut_action] modelids type: {type(modelids)}, "
                        f"length: {modelids_len}"
                    )

                    if modelids and len(modelids) > 0:
                        model_id = modelids[0]
                        logger.debug(f" Extracted model_id: {model_id}")
                    else:
                        logger.debug(" modelids is empty!")

                except ModelNotAccessibleError as e:
                    notification_service = get_notification_service()
                    if notification_service:
                        notification_service.show_error(str(e))
                    return gr.update(visible=False), None, gr.update(visible=True)
                except Exception as e:
                    logger.debug(
                        f"[civitai_shortcut_action] EXCEPTION in upload_shortcut_by_urls: {e}"
                    )
                    logger.debug(f" Exception type: {type(e)}")
                    import traceback

                    tb_str = traceback.format_exc()
                    logger.debug(f" Exception traceback: {tb_str}")
                    # Re-raise to see what happens
                    raise e
            else:
                logger.debug(" URL is empty after strip")

            current_time = datetime.datetime.now()
            logger.debug(f" Generated current_time: {current_time}")

            if not model_id:
                logger.debug(
                    "[civitai_shortcut_action] No model_id found after txt upload, "
                    "returning invisible updates."
                )
                result = (gr.update(visible=False), gr.update(visible=False), None)
                logger.debug(f" Returning (no model): {result}")
                logger.debug(
                    "[civitai_shortcut_action] ========== URL UPLOAD HANDLER END (NO MODEL) "
                    "=========="
                )
                return result

            logger.debug(f" Model registered from txt: {model_id}")
            result = (model_id, current_time, None)  # Clear textbox on success
            logger.debug(f" Returning (success): {result}")
            logger.debug(
                "[civitai_shortcut_action] ========== URL UPLOAD HANDLER END (SUCCESS) "
                "=========="
            )
            return result
        else:
            logger.debug(
                "[civitai_shortcut_action] URL is empty or None, returning fallback updates."
            )
            result = (
                gr.update(visible=False),
                None,
                gr.update(visible=True),
            )  # Keep textbox visible
            logger.debug(f" Returning (empty URL): {result}")
            logger.debug(
                "[civitai_shortcut_action] ========== URL UPLOAD HANDLER END (EMPTY URL) "
                "=========="
            )
            return result

    except Exception as e:
        logger.debug(
            f"[civitai_shortcut_action] OUTER EXCEPTION in on_civitai_internet_url_txt_upload: "
            f"{e}"
        )
        logger.debug(f" Outer exception type: {type(e)}")
        import traceback

        tb_str = traceback.format_exc()
        logger.debug(f" Outer exception traceback: {tb_str}")

        # Return safe fallback values
        result = (gr.update(visible=False), None, gr.update(visible=True))
        logger.debug(f" Returning (exception): {result}")
        logger.debug(
            "[civitai_shortcut_action] ========== URL UPLOAD HANDLER END (EXCEPTION) " "=========="
        )
        return result


def on_update_modelfolder_btn_click():
    logger.debug(
        "[civitai_shortcut_action] on_update_modelfolder_btn_click called. "
        "Updating downloaded model."
    )
    model.update_downloaded_model()
    current_time = datetime.datetime.now()
    return current_time


# 새 버전이 있는지 스캔한다
@with_error_handling(
    fallback_value=gr.update(value=None),
    exception_types=(NetworkError, FileOperationError),
    retry_count=1,
    user_message="Failed to scan for new versions",
)
def on_scan_new_version_btn(sc_types, progress=gr.Progress()):
    logger.debug(
        f"[civitai_shortcut_action] on_scan_new_version_btn called with sc_types: {sc_types}"
    )
    model.update_downloaded_model()
    result = None
    scan_list = None
    shortlist = get_shortcut_list(sc_types, True)
    logger.debug(f" get_shortcut_list returned: {shortlist}")
    if shortlist:
        for short in progress.tqdm(shortlist, desc="Scanning new version model"):
            if not is_latest(str(short['id'])):
                if not scan_list:
                    scan_list = list()
                scan_list.append(short)
                logger.debug(f" Found outdated model: {short}")
    if scan_list:
        result = list()
        for v in scan_list:
            if v:
                if ishortcut.imageprocessor.is_sc_image(v['id']):
                    result.append(
                        (
                            os.path.join(
                                settings.shortcut_thumbnail_folder,
                                f"{v['id']}{settings.PREVIEW_IMAGE_EXT}",
                            ),
                            settings.set_shortcutname(v['name'], v['id']),
                        )
                    )
                else:
                    result.append(
                        (
                            settings.no_card_preview_image,
                            settings.set_shortcutname(v['name'], v['id']),
                        )
                    )
        logger.debug(f" scan_list result: {result}")
    else:
        logger.debug(" No outdated models found.")
    return gr.update(value=result)


def get_shortcut_list(shortcut_types=None, downloaded_sc=False):
    logger.debug(
        f"[civitai_shortcut_action] get_shortcut_list called with shortcut_types: "
        f"{shortcut_types}, downloaded_sc: {downloaded_sc}"
    )
    shortcut_list = ishortcut.shortcutsearchfilter.get_filtered_shortcuts(
        shortcut_types, None, None, None
    )
    logger.debug(f" ishortcut.get_image_list returned: {shortcut_list}")
    if not shortcut_list:
        logger.debug(" shortcut_list is empty, returning None")
        return None
    if downloaded_sc:
        if model.Downloaded_Models:
            downloaded_list = list()
            for short in shortcut_list:
                mid = short['id']
                if str(mid) in model.Downloaded_Models.keys():
                    downloaded_list.append(short)
            shortcut_list = downloaded_list
            logger.debug(f" Filtered downloaded models: {shortcut_list}")
        else:
            logger.debug(" No Downloaded_Models found, returning None")
            shortcut_list = None
    return shortcut_list


def is_latest(modelid: str) -> bool:
    logger.debug(f" is_latest called with modelid: {modelid}")
    if not modelid:
        logger.debug(" modelid is None or empty, returning False")
        return False
    if str(modelid) in model.Downloaded_Models.keys():
        logger.debug(f" modelid {modelid} found in Downloaded_Models")
        version_info = civitai.get_latest_version_info_by_model_id(str(modelid))
        logger.debug(
            f"[civitai_shortcut_action] get_latest_version_info_by_model_id returned: "
            f"{version_info}"
        )
        if version_info:
            latest_versionid = str(version_info['id']).strip()
            dnver_list = list()
            for vid, _ in model.Downloaded_Models[str(modelid)]:
                dnver_list.append(str(vid).strip())
            logger.debug(
                f"[civitai_shortcut_action] Downloaded version list: {dnver_list}, "
                f"latest_versionid: {latest_versionid}"
            )
            if latest_versionid in dnver_list:
                logger.debug(
                    "[civitai_shortcut_action] Model is up to date (latest version present)"
                )
                return True
    logger.debug(
        "[civitai_shortcut_action] Model is not up to date or not found in Downloaded_Models"
    )
    return False


def setup_ui_copypaste(compat_layer):
    logger.debug(
        f"[civitai_shortcut_action] setup_ui_copypaste called with compat_layer: {compat_layer}"
    )
    from .ui_components import ParameterCopyPaste

    return ParameterCopyPaste(mode=compat_layer.mode)


def create_parameter_components(copypaste, gr=gr):
    logger.debug(
        f"[civitai_shortcut_action] create_parameter_components called with copypaste: {copypaste}"
    )
    with gr.Row():
        paste_button = gr.Button("Paste Params", elem_id="paste_params")
        copy_button = gr.Button("Copy Params", elem_id="copy_params")

    with gr.Column():
        prompt = gr.Textbox(label="Prompt", lines=3)
        negative_prompt = gr.Textbox(label="Negative Prompt", lines=2)
        with gr.Row():
            steps = gr.Slider(minimum=1, maximum=150, value=20, label="Steps")
            cfg_scale = gr.Slider(minimum=1, maximum=30, value=7, label="CFG Scale")

    components = {
        "paste_button": paste_button,
        "copy_button": copy_button,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": steps,
        "cfg_scale": cfg_scale,
    }
    logger.debug(f" Registering copypaste components: {components}")
    copypaste.register_copypaste_components(components)
    return components


# def update_shortcut_information(modelid):
#     if not modelid:
#         return
#     try:
#         if settings.shortcut_auto_update:
#             fileprocessor.write_model_information(modelid, False, None)
#     except:
#         return
#     return

# def update_shortcut_thread(modelid):
#     try:
#         thread = threading.Thread(target=update_shortcut_information, args=(modelid,))
#         thread.start()
#     except Exception as e:
#         logger.error(str(e))
#         pass
