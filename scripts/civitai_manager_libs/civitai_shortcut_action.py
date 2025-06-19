# Civitai Shortcut Action Module - Dual Mode Compatible
# This module has been modified to support both AUTOMATIC1111 and standalone modes
# through the compatibility layer.

import datetime
import os

import gradio as gr

from . import civitai
from . import civitai_gallery_action
from . import ishortcut
from . import ishortcut_action
from . import model
from . import model_action
from . import sc_browser_page
from . import setting
from . import util

_compat_layer = None
def set_compatibility_layer(compat_layer):
    """Set compatibility layer."""
    util.printD(f"[civitai_shortcut_action] set_compatibility_layer called with: {compat_layer}")
    global _compat_layer
    _compat_layer = compat_layer

def get_compatibility_layer():
    """Get compatibility layer."""
    global _compat_layer
    if _compat_layer is None:
        util.printD(
            "[civitai_shortcut_action] _compat_layer is None, "
            "calling setting.get_compatibility_layer()"
        )
        _compat_layer = setting.get_compatibility_layer()
    util.printD(f"[civitai_shortcut_action] get_compatibility_layer returns: {_compat_layer}")
    return _compat_layer

def on_shortcut_input_change(shortcut_input):
    util.printD(
        f"[civitai_shortcut_action] on_shortcut_input_change called with "
        f"shortcut_input: {shortcut_input}"
    )
    if not shortcut_input:
        util.printD("[civitai_shortcut_action] shortcut_input is empty or None")
        return gr.update(visible=False), gr.update(selected=None), gr.update(visible=False)
    util.printD("[civitai_shortcut_action] shortcut_input is valid, returning values")
    return shortcut_input, gr.update(selected="Shortcut"), None

def on_ui(recipe_input, shortcut_input, civitai_tabs):
    util.printD(
        f"[civitai_shortcut_action] on_ui called with recipe_input: {recipe_input}, "
        f"shortcut_input: {shortcut_input}, civitai_tabs: {civitai_tabs}"
    )

    with gr.Row(visible=False):
        util.printD("[civitai_shortcut_action] Creating hidden Row for internal state components")
        sc_modelid = gr.Textbox()
        update_informations = gr.Textbox()
        current_information_tabs = gr.State(0)
        refresh_NSFW = gr.Textbox()

    with gr.Column(scale=setting.shortcut_browser_screen_split_ratio):
        util.printD(
            f"[civitai_shortcut_action] Creating main UI column with scale: "
            f"{setting.shortcut_browser_screen_split_ratio}"
        )
        with gr.Tabs() as civitai_shortcut_tabs:
            util.printD("[civitai_shortcut_action] Creating civitai_shortcut_tabs")
            with gr.TabItem("Register Model"):
                util.printD("[civitai_shortcut_action] Register Model tab initialized")
                with gr.Row(visible=False):
                    register_information_only = gr.Checkbox(
                        label="Register only model information", value=False
                    )
                with gr.Row():
                    with gr.Column():
                        util.printD(
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
                util.printD("[civitai_shortcut_action] Model Browser tab initialized")
                with gr.Row():
                    with gr.Column():
                        util.printD(
                            "[civitai_shortcut_action] Model Browser: calling "
                            "sc_browser_page.on_ui()"
                        )
                        sc_gallery, refresh_sc_browser, refresh_sc_gallery = sc_browser_page.on_ui()

            with gr.TabItem("Scan New Version"):
                util.printD("[civitai_shortcut_action] Scan New Version tab initialized")
                with gr.Row():
                    with gr.Column():
                        util.printD(
                            "[civitai_shortcut_action] Scan New Version: Dropdown, Button, "
                            "Gallery, Markdown created"
                        )
                        shortcut_new_version_type = gr.Dropdown(
                            label="Filter Model type",
                            multiselect=True,
                            choices=[k for k in setting.ui_typenames],
                            interactive=True,
                        )
                        scan_new_version_btn = gr.Button(
                            value="Scan new version model", variant="primary"
                        )
                        sc_new_version_gallery = gr.Gallery(
                            label="SC New Version Gallery",
                            elem_id="sc_new_version_gallery",
                            show_label=False,
                            columns=setting.shortcut_column,
                            height="fit",
                            object_fit=setting.gallery_thumbnail_image_style,
                        )
                        gr.Markdown(
                            value=(
                                "The feature is to search for new versions of models on Civitai "
                                "among the downloaded ones."
                            ),
                            visible=True,
                        )
            with gr.TabItem("NSFW Filter"):
                util.printD("[civitai_shortcut_action] NSFW Filter tab initialized")
                with gr.Row():
                    with gr.Column():
                        util.printD(
                            "[civitai_shortcut_action] NSFW Filter: Dropdowns and Button created"
                        )
                        nsfw_filter_enable = gr.Dropdown(
                            value="On",
                            choices=["On", "Off"],
                            label="NSFW Filtering",
                            interactive=True,
                        )
                        nsfw_level = gr.Dropdown(
                            value=setting.NSFW_level_user,
                            choices=setting.NSFW_levels,
                            label="NSFW Filtering Level",
                            visible=True,
                            interactive=True,
                        )
                        nsfw_save_btn = gr.Button(
                            value="Save NSFW Setting", variant="primary", visible=True
                        )

    with gr.Column(
        scale=(
            setting.shortcut_browser_screen_split_ratio_max
            - setting.shortcut_browser_screen_split_ratio
        )
    ):
        scale_val = (
            setting.shortcut_browser_screen_split_ratio_max
            - setting.shortcut_browser_screen_split_ratio
        )
        util.printD(
            f"[civitai_shortcut_action] Creating secondary UI column with scale: "
            f"{scale_val}"
        )
        with gr.Tabs() as civitai_information_tabs:
            util.printD("[civitai_shortcut_action] Creating civitai_information_tabs")
            with gr.TabItem("Model Information", id="civitai_info"):
                util.printD("[civitai_shortcut_action] Model Information tab initialized")
                with gr.Row():
                    shortcut_modelid, refresh_civitai_information = ishortcut_action.on_ui(
                        refresh_sc_browser, recipe_input
                    )
            with gr.TabItem("Civitai User Gallery", id="gallery_info"):
                util.printD("[civitai_shortcut_action] Civitai User Gallery tab initialized")
                with gr.Row():
                    gallery_modelid, refresh_gallery_information = civitai_gallery_action.on_ui(
                        recipe_input
                    )

            with gr.TabItem("Downloaded Model Information", id="download_info"):
                util.printD(
                    "[civitai_shortcut_action] Downloaded Model Information tab initialized"
                )
                with gr.Row():
                    downloadinfo_modelid, refresh_download_information = model_action.on_ui()

    # NSFW Filter Setting Refresh
    util.printD("[civitai_shortcut_action] Binding refresh_NSFW.change event handler")
    refresh_NSFW.change(
        fn=on_refresh_NSFW_change,
        inputs=None,
        outputs=[nsfw_filter_enable, nsfw_level],
    )

    util.printD("[civitai_shortcut_action] Binding nsfw_filter_enable.select event handler")
    nsfw_filter_enable.select(
        fn=on_nsfw_filter,
        inputs=[nsfw_filter_enable, nsfw_level],
        outputs=[nsfw_level, refresh_civitai_information, refresh_gallery_information],
    )

    util.printD("[civitai_shortcut_action] Binding nsfw_level.select event handler")
    nsfw_level.select(
        fn=on_nsfw_filter,
        inputs=[nsfw_filter_enable, nsfw_level],
        outputs=[nsfw_level, refresh_civitai_information, refresh_gallery_information],
    )

    nsfw_save_btn.click(fn=on_nsfw_save_btn_click)
    util.printD("[civitai_shortcut_action] Binding nsfw_save_btn.click event handler")

    util.printD("[civitai_shortcut_action] Binding shortcut_input.change event handler")
    shortcut_input.change(
        fn=on_shortcut_input_change,
        inputs=[shortcut_input],
        outputs=[sc_modelid, civitai_tabs, shortcut_input],
        show_progress=False,
    )

    scan_new_version_btn.click(
        on_scan_new_version_btn, shortcut_new_version_type, sc_new_version_gallery
    )
    util.printD("[civitai_shortcut_action] Binding scan_new_version_btn.click event handler")
    sc_gallery.select(on_sc_gallery_select, None, [sc_modelid], show_progress=False)
    util.printD("[civitai_shortcut_action] Binding sc_gallery.select event handler")
    sc_new_version_gallery.select(
        on_sc_gallery_select, None, [sc_modelid], show_progress=False
    )
    util.printD("[civitai_shortcut_action] Binding sc_new_version_gallery.select event handler")
    civitai_shortcut_tabs.select(
        on_civitai_shortcut_tabs_select,
        None,
        [refresh_sc_browser, refresh_NSFW],
        show_progress=False,
    )
    util.printD("[civitai_shortcut_action] Binding civitai_shortcut_tabs.select event handler")

    util.printD("[civitai_shortcut_action] Binding update_informations.change event handler")
    update_informations.change(
        fn=on_sc_modelid_change,
        inputs=[sc_modelid, current_information_tabs],
        outputs=[shortcut_modelid, gallery_modelid, downloadinfo_modelid],
    )

    util.printD("[civitai_shortcut_action] Binding sc_modelid.change event handler")
    sc_modelid.change(
        fn=on_sc_modelid_change,
        inputs=[sc_modelid, current_information_tabs],
        outputs=[shortcut_modelid, gallery_modelid, downloadinfo_modelid],
    )

    util.printD("[civitai_shortcut_action] Binding civitai_information_tabs.select event handler")
    civitai_information_tabs.select(
        fn=on_civitai_information_tabs_select,
        inputs=None,
        outputs=[current_information_tabs, update_informations],
    )

    util.printD("[civitai_shortcut_action] Binding civitai_internet_url.upload event handler")
    civitai_internet_url.upload(
        fn=on_civitai_internet_url_upload,
        inputs=[civitai_internet_url, register_information_only],
        outputs=[sc_modelid, refresh_sc_browser, civitai_internet_url],
    )

    util.printD("[civitai_shortcut_action] Binding civitai_internet_url_txt.change event handler")
    civitai_internet_url_txt.change(
        fn=on_civitai_internet_url_txt_upload,
        inputs=[civitai_internet_url_txt, register_information_only],
        outputs=[sc_modelid, refresh_sc_browser, civitai_internet_url_txt],
    )

    return refresh_sc_browser, refresh_civitai_information

def on_refresh_NSFW_change():
    util.printD(
        f"[civitai_shortcut_action] on_refresh_NSFW_change called. "
        f"NSFW_filtering_enable: {setting.NSFW_filtering_enable}, "
        f"NSFW_level_user: {setting.NSFW_level_user}"
    )
    if setting.NSFW_filtering_enable:
        return gr.update(value="On"), gr.update(visible=True, value=setting.NSFW_level_user)
    else:
        return gr.update(value="Off"), gr.update(visible=False, value=setting.NSFW_level_user)

def on_nsfw_filter(enable, level):
    util.printD(
        f"[civitai_shortcut_action] on_nsfw_filter called with enable: {enable}, "
        f"level: {level}"
    )
    current_time = datetime.datetime.now()
    setting.set_NSFW(True if enable == "On" else False, level)
    util.printD(f"[civitai_shortcut_action] NSFW set to: {enable == 'On'}, level: {level}")
    return (
        gr.update(visible=True if enable == "On" else False, value=level),
        current_time,
        current_time,
    )

def on_nsfw_save_btn_click():
    util.printD("[civitai_shortcut_action] on_nsfw_save_btn_click called. Saving NSFW settings.")
    setting.save_NSFW()

def on_civitai_shortcut_tabs_select(evt: gr.SelectData):
    util.printD(
        f"[civitai_shortcut_action] on_civitai_shortcut_tabs_select called with "
        f"evt.index: {evt.index}"
    )
    if evt.index == 1:
        current_time = datetime.datetime.now()
        util.printD("[civitai_shortcut_action] Model Browser tab selected, refreshing browser.")
        return current_time, gr.update(visible=False)
    elif evt.index == 3:
        current_time = datetime.datetime.now()
        util.printD("[civitai_shortcut_action] NSFW Filter tab selected, refreshing NSFW.")
        return gr.update(visible=False), current_time
    util.printD("[civitai_shortcut_action] Other tab selected, no refresh.")
    return gr.update(visible=False), gr.update(visible=False)

def on_civitai_information_tabs_select(evt: gr.SelectData):
    util.printD(
        f"[civitai_shortcut_action] on_civitai_information_tabs_select called with "
        f"evt.index: {evt.index}"
    )
    current_time = datetime.datetime.now()
    return evt.index, current_time

# sc_gallery function definition
def on_sc_gallery_select(evt: gr.SelectData):
    util.printD(
        f"[civitai_shortcut_action] on_sc_gallery_select called with evt.value: {evt.value}"
    )
    sc_model_id = None
    if evt.value:
        shortcut = evt.value
        sc_model_id = setting.get_modelid_from_shortcutname(shortcut)
        util.printD(
            f"[civitai_shortcut_action] Gallery select: shortcut={shortcut}, "
            f"sc_model_id={sc_model_id}"
        )
    return sc_model_id

def on_sc_modelid_change(sc_model_id, current_information_tabs):
    util.printD(
        f"[civitai_shortcut_action] on_sc_modelid_change called with sc_model_id: {sc_model_id}, "
        f"current_information_tabs: {current_information_tabs}"
    )
    if current_information_tabs == setting.civitai_information_tab:
        util.printD("[civitai_shortcut_action] Returning for civitai_information_tab")
        return sc_model_id, gr.update(visible=False), gr.update(visible=False)
    if current_information_tabs == setting.usergal_information_tab:
        util.printD("[civitai_shortcut_action] Returning for usergal_information_tab")
        return gr.update(visible=False), sc_model_id, gr.update(visible=False)
    if current_information_tabs == setting.download_information_tab:
        util.printD("[civitai_shortcut_action] Returning for download_information_tab")
        return gr.update(visible=False), gr.update(visible=False), sc_model_id
    util.printD("[civitai_shortcut_action] Returning default (all invisible)")
    return gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

def on_civitai_internet_url_upload(files, register_information_only, progress=gr.Progress()):
    util.printD(
        f"[civitai_shortcut_action] on_civitai_internet_url_upload called with files: {files}, "
        f"register_information_only: {register_information_only}"
    )
    model_id = None
    if files:
        modelids = ishortcut_action.upload_shortcut_by_files(
            files, register_information_only, progress
        )
        util.printD(f"[civitai_shortcut_action] upload_shortcut_by_files returned: {modelids}")
        if len(modelids) > 0:
            model_id = modelids[0]

    current_time = datetime.datetime.now()
    if not model_id:
        util.printD(
            "[civitai_shortcut_action] No model_id found after upload, returning invisible updates."
        )
        return gr.update(visible=False), gr.update(visible=False), None
    util.printD(f"[civitai_shortcut_action] Model registered: {model_id}")
    return model_id, current_time, None

def on_civitai_internet_url_txt_upload(url, register_information_only, progress=gr.Progress()):
    util.printD(
        f"[civitai_shortcut_action] on_civitai_internet_url_txt_upload called with url: {url}, "
        f"register_information_only: {register_information_only}"
    )
    model_id = None
    if url:
        if len(url.strip()) > 0:
            modelids = ishortcut_action.upload_shortcut_by_urls(
                [url], register_information_only, progress
            )
            util.printD(f"[civitai_shortcut_action] upload_shortcut_by_urls returned: {modelids}")
            if len(modelids) > 0:
                model_id = modelids[0]
        current_time = datetime.datetime.now()
        if not model_id:
            util.printD(
                "[civitai_shortcut_action] No model_id found after txt upload, "
                "returning invisible updates."
            )
            return gr.update(visible=False), gr.update(visible=False), None
        util.printD(f"[civitai_shortcut_action] Model registered from txt: {model_id}")
        return model_id, current_time, None
    util.printD("[civitai_shortcut_action] URL is empty or None, returning fallback updates.")
    return gr.update(visible=False), None, gr.update(visible=True)
def on_update_modelfolder_btn_click():
    util.printD(
        "[civitai_shortcut_action] on_update_modelfolder_btn_click called. "
        "Updating downloaded model."
    )
    model.update_downloaded_model()
    current_time = datetime.datetime.now()
    return current_time

# 새 버전이 있는지 스캔한다
def on_scan_new_version_btn(sc_types, progress=gr.Progress()):
    util.printD(
        f"[civitai_shortcut_action] on_scan_new_version_btn called with sc_types: {sc_types}"
    )
    model.update_downloaded_model()
    result = None
    scan_list = None
    shortlist = get_shortcut_list(sc_types, True)
    util.printD(f"[civitai_shortcut_action] get_shortcut_list returned: {shortlist}")
    if shortlist:
        for short in progress.tqdm(shortlist, desc="Scanning new version model"):
            if not is_latest(str(short['id'])):
                if not scan_list:
                    scan_list = list()
                scan_list.append(short)
                util.printD(f"[civitai_shortcut_action] Found outdated model: {short}")
    if scan_list:
        result = list()
        for v in scan_list:
            if v:
                if ishortcut.is_sc_image(v['id']):
                    result.append(
                        (
                            os.path.join(
                                setting.shortcut_thumbnail_folder,
                                f"{v['id']}{setting.preview_image_ext}",
                            ),
                            setting.set_shortcutname(v['name'], v['id']),
                        )
                    )
                else:
                    result.append(
                        (
                            setting.no_card_preview_image,
                            setting.set_shortcutname(v['name'], v['id']),
                        )
                    )
        util.printD(f"[civitai_shortcut_action] scan_list result: {result}")
    else:
        util.printD("[civitai_shortcut_action] No outdated models found.")
    return gr.update(value=result)

def get_shortcut_list(shortcut_types=None, downloaded_sc=False):
    util.printD(
        f"[civitai_shortcut_action] get_shortcut_list called with shortcut_types: "
        f"{shortcut_types}, downloaded_sc: {downloaded_sc}"
    )
    shortcut_list = ishortcut.get_image_list(shortcut_types, None, None, None)
    util.printD(f"[civitai_shortcut_action] ishortcut.get_image_list returned: {shortcut_list}")
    if not shortcut_list:
        util.printD("[civitai_shortcut_action] shortcut_list is empty, returning None")
        return None
    if downloaded_sc:
        if model.Downloaded_Models:
            downloaded_list = list()
            for short in shortcut_list:
                mid = short['id']
                if str(mid) in model.Downloaded_Models.keys():
                    downloaded_list.append(short)
            shortcut_list = downloaded_list
            util.printD(
                f"[civitai_shortcut_action] Filtered downloaded models: {shortcut_list}"
            )
        else:
            util.printD("[civitai_shortcut_action] No Downloaded_Models found, returning None")
            shortcut_list = None
    return shortcut_list
def is_latest(modelid: str) -> bool:
    util.printD(
        f"[civitai_shortcut_action] is_latest called with modelid: {modelid}"
    )
    if not modelid:
        util.printD(
            "[civitai_shortcut_action] modelid is None or empty, returning False"
        )
        return False
    if str(modelid) in model.Downloaded_Models.keys():
        util.printD(
            f"[civitai_shortcut_action] modelid {modelid} found in Downloaded_Models"
        )
        version_info = civitai.get_latest_version_info_by_model_id(str(modelid))
        util.printD(
            f"[civitai_shortcut_action] get_latest_version_info_by_model_id returned: "
            f"{version_info}"
        )
        if version_info:
            latest_versionid = str(version_info['id']).strip()
            dnver_list = list()
            for vid, _ in model.Downloaded_Models[str(modelid)]:
                dnver_list.append(str(vid).strip())
            util.printD(
                f"[civitai_shortcut_action] Downloaded version list: {dnver_list}, "
                f"latest_versionid: {latest_versionid}"
            )
            if latest_versionid in dnver_list:
                util.printD(
                    "[civitai_shortcut_action] Model is up to date (latest version present)"
                )
                return True
    util.printD(
        "[civitai_shortcut_action] Model is not up to date or not found in Downloaded_Models"
    )
    return False

def setup_ui_copypaste(compat_layer):
    util.printD(
        f"[civitai_shortcut_action] setup_ui_copypaste called with compat_layer: {compat_layer}"
    )
    from .ui_components import ParameterCopyPaste
    return ParameterCopyPaste(mode=compat_layer.mode)


def create_parameter_components(copypaste, gr=gr):
    util.printD(
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
    util.printD(f"[civitai_shortcut_action] Registering copypaste components: {components}")
    copypaste.register_copypaste_components(components)
    return components

# def update_shortcut_information(modelid):
#     if not modelid:
#         return
#     try:
#         if setting.shortcut_auto_update:
#             ishortcut.write_model_information(modelid, False, None)
#     except:
#         return
#     return

# def update_shortcut_thread(modelid):
#     try:
#         thread = threading.Thread(target=update_shortcut_information, args=(modelid,))
#         thread.start()
#     except Exception as e:
#         util.printD(e)
#         pass
