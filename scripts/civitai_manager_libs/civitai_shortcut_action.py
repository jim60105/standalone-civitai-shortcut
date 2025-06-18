"""
Civitai Shortcut Action Module - Dual Mode Compatible

This module has been modified to support both AUTOMATIC1111 and standalone modes
through the compatibility layer.
"""

import gradio as gr
import datetime
import os

from . import model
from . import civitai
from . import setting
from . import sc_browser_page

from . import util
from . import ishortcut
from . import model_action
from . import ishortcut_action
from . import civitai_gallery_action
from .gradio_compat import SelectData, State, HTML, Gallery, File, Dropdown, Accordion

# Compatibility layer variables
_compat_layer = None

def set_compatibility_layer(compat_layer):
    """Set compatibility layer"""
    global _compat_layer
    _compat_layer = compat_layer

def get_compatibility_layer():
    """Get compatibility layer"""
    global _compat_layer
    if _compat_layer is None:
        _compat_layer = setting.get_compatibility_layer()
    return _compat_layer

def on_shortcut_input_change(shortcut_input):
    if not shortcut_input:
        return gr.update(visible=False), gr.update(selected=None), gr.update(visible=False)
    return shortcut_input, gr.update(selected="Shortcut"), None
        
def on_ui(recipe_input, shortcut_input, civitai_tabs):    
    with gr.Row(visible=False):       
        
        sc_modelid = gr.Textbox()
        update_informations = gr.Textbox()
        current_information_tabs = State(0)
        refresh_NSFW = gr.Textbox()
        
    with gr.Column(scale=setting.shortcut_browser_screen_split_ratio):
        with gr.Tabs() as civitai_shortcut_tabs:
            with gr.TabItem("Register Model"):
                with gr.Row(visible=False):                                 
                    register_information_only = gr.Checkbox(label="Register only model information", value=False)
                with gr.Row():
                    with gr.Column():
                        gr.Markdown(value="Using the model URL from the Civitai site, you register the information of the model. You can click and drag the Civitai Model's URL or drag and drop a saved internet shortcut. Additionally, you can select multiple internet shortcuts and drop them all at once.", visible=True)
                        civitai_internet_url_txt = gr.Textbox(placeholder="Copy & Paste or Drag & Drop Civitai Model Url", show_label=False, interactive=True)
                        civitai_internet_url = File(label="Civitai Internet Shortcut", file_count="multiple", file_types=[".url"])
                        # update_modelfolder_btn = gr.Button(value="Update Downloaded Model Information", variant="primary")
                        # gr.Markdown(value="If you have made direct modifications(e.g. moving or renaming a folder) to the downloaded model during runtime, please execute the \"Update Downloaded Model Information\" function, which rescans the downloaded model and updates its information accordingly. ", visible=True)
                                                    
            with gr.TabItem("Model Browser"):    
                with gr.Row():
                    with gr.Column():
                        sc_gallery, refresh_sc_browser, refresh_sc_gallery = sc_browser_page.on_ui()
                        
            with gr.TabItem("Scan New Version"):
                with gr.Row():
                    with gr.Column():
                        shortcut_new_version_type = Dropdown(label='Filter Model type', multiselect=True, choices=[k for k in setting.ui_typenames], interactive=True)                                     
                        scan_new_version_btn = gr.Button(value="Scan new version model", variant="primary")
                        sc_new_version_gallery = Gallery(label="SC New Version Gallery", elem_id="sc_new_version_gallery", show_label=False, columns=setting.shortcut_column, height="fit", object_fit=setting.gallery_thumbnail_image_style)
                        gr.Markdown(value="The feature is to search for new versions of models on Civitai among the downloaded ones.", visible=True)
            with gr.TabItem("NSFW Filter"):
                with gr.Row():
                    with gr.Column():
                        nsfw_filter_enable = Dropdown(value='On', choices=['On','Off'], label='NSFW Filtering', interactive=True)
                        nsfw_level = Dropdown(value=setting.NSFW_level_user, choices=setting.NSFW_levels, label='NSFW Filtering Level', visible=True, interactive=True)
                        nsfw_save_btn = gr.Button(value="Save NSFW Setting", variant="primary", visible=True)
                        
    with gr.Column(scale=(setting.shortcut_browser_screen_split_ratio_max-setting.shortcut_browser_screen_split_ratio)):
        with gr.Tabs() as civitai_information_tabs:
            with gr.TabItem("Model Information" , id="civitai_info"):
                with gr.Row():
                    shortcut_modelid, refresh_civitai_information = ishortcut_action.on_ui(refresh_sc_browser, recipe_input)

            with gr.TabItem("Civitai User Gallery" , id="gallery_info"):
                with gr.Row():
                    gallery_modelid, refresh_gallery_information = civitai_gallery_action.on_ui(recipe_input)

            with gr.TabItem("Downloaded Model Information" , id="download_info"):
                with gr.Row():
                    downloadinfo_modelid , refresh_download_information = model_action.on_ui()
                    
    # NSFW Filter Setting Refresh    
    refresh_NSFW.change(
        fn=on_refresh_NSFW_change,
        inputs=None,
        outputs=[
            nsfw_filter_enable,
            nsfw_level
        ]
    )

    nsfw_filter_enable.select(
        fn=on_nsfw_filter,
        inputs=[
            nsfw_filter_enable,
            nsfw_level
        ],
        outputs=[
            nsfw_level,
            refresh_civitai_information,
            refresh_gallery_information
        ]
    )
    
    nsfw_level.select(
        fn=on_nsfw_filter,
        inputs=[
            nsfw_filter_enable,
            nsfw_level            
        ],
        outputs=[
            nsfw_level,            
            refresh_civitai_information,
            refresh_gallery_information
        ]        
    )
    
    nsfw_save_btn.click(fn=on_nsfw_save_btn_click)
    
    # shortcut information 에서 넘어올때는 새로운 레시피를 만든다.
    shortcut_input.change(
        fn=on_shortcut_input_change,
        inputs=[
            shortcut_input
        ],
        outputs=[
            sc_modelid,
            civitai_tabs,
            shortcut_input
        ], show_progress=False
    )
    
    scan_new_version_btn.click(on_scan_new_version_btn,shortcut_new_version_type,sc_new_version_gallery)                
    sc_gallery.select(on_sc_gallery_select, None, [sc_modelid], show_progress=False)    
    sc_new_version_gallery.select(on_sc_gallery_select, None, [sc_modelid], show_progress=False)
    # update_modelfolder_btn.click(on_update_modelfolder_btn_click,None,refresh_sc_browser)
    civitai_shortcut_tabs.select(on_civitai_shortcut_tabs_select,None,[refresh_sc_browser,refresh_NSFW],show_progress=False)

    update_informations.change(
        fn=on_sc_modelid_change,
        inputs=[
            sc_modelid, 
            current_information_tabs
        ],
        outputs=[
            shortcut_modelid, 
            gallery_modelid, 
            downloadinfo_modelid
        ]
    )

    sc_modelid.change(
        fn=on_sc_modelid_change,
        inputs=[
            sc_modelid, 
            current_information_tabs
        ],
        outputs=[
            shortcut_modelid, 
            gallery_modelid, 
            downloadinfo_modelid
        ]
    )
        
    civitai_information_tabs.select(
        fn=on_civitai_information_tabs_select,
        inputs=None,        
        outputs=[
            current_information_tabs, 
            update_informations
        ]
    )
    
    civitai_internet_url.upload(
        fn=on_civitai_internet_url_upload,
        inputs=[
            civitai_internet_url,
            register_information_only,
        ],
        outputs=[
            sc_modelid,
            refresh_sc_browser,
            civitai_internet_url
        ]
    )
    
    civitai_internet_url_txt.change(
        fn=on_civitai_internet_url_txt_upload,
        inputs=[
            civitai_internet_url_txt,
            register_information_only,
        ],
        outputs=[
            sc_modelid, 
            refresh_sc_browser,
            civitai_internet_url_txt
        ]        
    )

    return refresh_sc_browser, refresh_civitai_information

def on_refresh_NSFW_change():
    if setting.NSFW_filtering_enable:
        return gr.update(value="On") , gr.update(visible=True, value=setting.NSFW_level_user)
    else:
        return gr.update(value="Off") , gr.update(visible=False, value=setting.NSFW_level_user)

def on_nsfw_filter(enable, level):
    current_time = datetime.datetime.now()  
    setting.set_NSFW(True if enable == "On" else False , level)
    
    return gr.update(visible=True if enable == "On" else False, value=level), current_time, current_time

def on_nsfw_save_btn_click():
    setting.save_NSFW()

def on_civitai_shortcut_tabs_select(evt: SelectData):
    if evt.index == 1:      
        current_time = datetime.datetime.now()  
        return current_time,gr.update(visible=False)
    elif evt.index == 3:      
        current_time = datetime.datetime.now()  
        return gr.update(visible=False), current_time    
    return gr.update(visible=False),gr.update(visible=False)

def on_civitai_information_tabs_select(evt: SelectData):
    current_time = datetime.datetime.now()  
    return evt.index, current_time

##### sc_gallery 함수 정의 #####
def on_sc_gallery_select(evt : SelectData):

    if evt.value:
        shortcut = evt.value 
        sc_model_id = setting.get_modelid_from_shortcutname(shortcut) #shortcut[0:shortcut.find(':')]      
        
        # 최신버전이 있으면 업데이트한다. 백그라운드에서 수행되므로 다음에 번에 반영된다.
        # update_shortcut_thread(sc_model_id)
    return sc_model_id

def on_sc_modelid_change(sc_model_id, current_information_tabs):
   
    if current_information_tabs == setting.civitai_information_tab:
        return sc_model_id, gr.update(visible=False), gr.update(visible=False)
    
    if current_information_tabs == setting.usergal_information_tab:
        return gr.update(visible=False), sc_model_id, gr.update(visible=False)
    
    if current_information_tabs == setting.download_information_tab:
        return gr.update(visible=False), gr.update(visible=False), sc_model_id
    
    return gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

def on_civitai_internet_url_upload(files, register_information_only, progress=gr.Progress()):       
    model_id = None    
    if files:
        modelids = ishortcut_action.upload_shortcut_by_files(files, register_information_only, progress)
        if len(modelids) > 0:
            model_id = modelids[0]

    current_time = datetime.datetime.now()
    
    if not model_id:
        return gr.update(visible=False), gr.update(visible=False), None
    return model_id, current_time, None

def on_civitai_internet_url_txt_upload(url, register_information_only, progress=gr.Progress()):       
    model_id = None    
    if url:
        if len(url.strip()) > 0:
            modelids = ishortcut_action.upload_shortcut_by_urls([url], register_information_only, progress)
            if len(modelids) > 0:
                model_id = modelids[0]        
    
        current_time = datetime.datetime.now()
    
        if not model_id:
            return gr.update(visible=False), gr.update(visible=False), None
        return model_id, current_time, None

    return gr.update(visible=False), None, gr.update(visible=True)

def on_update_modelfolder_btn_click():
    model.update_downloaded_model()
    current_time = datetime.datetime.now()
    return current_time

# 새 버전이 있는지 스캔한다
def on_scan_new_version_btn(sc_types, progress=gr.Progress()):
    model.update_downloaded_model()

    result = None
    scan_list = None
    shortlist =  get_shortcut_list(sc_types,True)
    
    if shortlist:        
        for short in progress.tqdm(shortlist, desc="Scanning new version model"):            
            if not is_latest(str(short['id'])):
                if not scan_list:
                    scan_list = list()
                scan_list.append(short)
                
    # util.printD(scan_list)
    if scan_list:
        result = list()        
        for v in scan_list:
            if v:
                if ishortcut.is_sc_image(v['id']):
                    result.append((os.path.join(setting.shortcut_thumbnail_folder,f"{v['id']}{setting.preview_image_ext}"),setting.set_shortcutname(v['name'],v['id'])))
                else:
                    result.append((setting.no_card_preview_image,setting.set_shortcutname(v['name'],v['id'])))
                        
    return gr.update(value=result)

def get_shortcut_list(shortcut_types=None, downloaded_sc=False):
    
    shortcut_list =  ishortcut.get_image_list(shortcut_types, None, None, None)
   
    if not shortcut_list:
        return None
    
    if downloaded_sc:
        if model.Downloaded_Models:                
            downloaded_list = list()            
            for short in shortcut_list:
                mid = short['id']
                if str(mid) in model.Downloaded_Models.keys():
                    downloaded_list.append(short)
            shortcut_list = downloaded_list
        else:
            shortcut_list = None
                                    
    return shortcut_list

def is_latest(modelid:str)->bool:
    if not modelid:
        return False
   
    if str(modelid) in model.Downloaded_Models.keys():
        # civitai 에서 최신 모델 정보를 가져온다.
        version_info = civitai.get_latest_version_info_by_model_id(str(modelid))
        if version_info:
            latest_versionid = str(version_info['id']).strip()                
            # util.printD(latest_versionid)
            # 현재 가지고 있는 버전들을 가져온다.                
            dnver_list = list()                
            for vid, version_paths in model.Downloaded_Models[str(modelid)]:
                dnver_list.append(str(vid).strip())
                
                # util.printD(dnver_list)
            if latest_versionid in dnver_list:     
                # util.printD("True")                   
                return True
    return False


def setup_ui_copypaste(compat_layer):
    """Setup UI parameter copy-paste feature."""
    from .ui_components import ParameterCopyPaste
    return ParameterCopyPaste(mode=compat_layer.mode)


def create_parameter_components(copypaste, gr=gr):
    """Create UI components for parameter copy-paste and bind events."""
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
        'paste_button': paste_button,
        'copy_button': copy_button,
        'prompt': prompt,
        'negative_prompt': negative_prompt,
        'steps': steps,
        'cfg_scale': cfg_scale,
    }
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
