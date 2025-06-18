import os
import datetime
import gradio as gr
import threading

# Conditional imports for WebUI mode
try:
    from modules import script_callbacks
    WEBUI_MODE = True
except ImportError:
    WEBUI_MODE = False
    script_callbacks = None

from scripts.civitai_manager_libs import model
from scripts.civitai_manager_libs import setting
from scripts.civitai_manager_libs import classification_action
from scripts.civitai_manager_libs import civitai_shortcut_action
from scripts.civitai_manager_libs import setting_action
from scripts.civitai_manager_libs import scan_action
from scripts.civitai_manager_libs import util
from scripts.civitai_manager_libs import ishortcut
from scripts.civitai_manager_libs import recipe_action
from scripts.civitai_manager_libs.module_compatibility import initialize_compatibility_layer
from scripts.civitai_manager_libs.gradio_compat import SelectData

# Global compatibility layer
_compat_layer = None


def get_compatibility_layer():
    """Get the compatibility layer instance"""
    global _compat_layer
    if _compat_layer is None:
        from scripts.civitai_manager_libs.compat.compat_layer import CompatibilityLayer
        
        # Detect environment and create compatibility layer
        if WEBUI_MODE:
            env = "webui"
        else:
            env = "standalone"
            
        _compat_layer = CompatibilityLayer(mode=env)
        
        # Initialize all modules with compatibility layer
        initialize_compatibility_layer(_compat_layer)
        
        util.printD(f"Civitai Shortcut initialized in {env} mode")
        
    return _compat_layer


# Initialize compatibility layer for all modules
def initialize_civitai_shortcut():
    """Initialize Civitai Shortcut with compatibility layer"""
    try:
        get_compatibility_layer()
    except Exception as e:
        # Simple print to avoid circular dependency
        print(f"Warning: Failed to initialize compatibility layer: {e}")
        print("Running in fallback mode")


# Initialize on import
initialize_civitai_shortcut()

def on_civitai_tabs_select(evt: SelectData):
    current_time = datetime.datetime.now() 
    if evt.index == 0:
        return current_time, gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
    elif evt.index == 1:            
        return gr.update(visible=False), current_time, gr.update(visible=False), gr.update(visible=False)    
    elif evt.index == 2:
        return gr.update(visible=False), gr.update(visible=False), current_time, gr.update(visible=False)
    elif evt.index == 3:       
        return gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), current_time
        
    return gr.update(visible=False), gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)

# def readmarkdown():
#     path = os.path.join(setting.extension_base,"README.md")
#     markdown_text = None
#     try:    
#         with open(path, 'r',encoding='UTF-8') as f:
#             markdown_text = f.read()                
#     except Exception as e:    
#         util.printD(e)        
#         return
#     return markdown_text
                   
def civitai_shortcut_ui():
    with gr.Tabs(elem_id="civitai_shortcut_tabs_container") as civitai_tabs:
        with gr.Row(visible=False):
            recipe_input = gr.Textbox()
            shortcut_input = gr.Textbox()
            
        with gr.TabItem("Model Browser" , id="Shortcut"):
            with gr.Row():
                refresh_civitai_sc_browser, refresh_civitai_information = civitai_shortcut_action.on_ui(recipe_input, shortcut_input, civitai_tabs)

        with gr.TabItem("Prompt Recipe" , id="Recipe"):
            with gr.Row():
                refresh_recipe = recipe_action.on_ui(recipe_input, shortcut_input, civitai_tabs)

        with gr.TabItem("Assistance" , id="Assistance"):
            with gr.Tabs() as civitai_assistance_tabs:
                with gr.TabItem("Classification"):
                    with gr.Row():
                        refresh_classification = classification_action.on_ui(shortcut_input)
                with gr.TabItem("Scan and Update Models"):
                    with gr.Row():
                        scan_action.on_scan_ui()

        with gr.TabItem("Manage" , id="Manage"):
            with gr.Tabs() as civitai_manage_tabs:
                with gr.TabItem("Setting"):
                    with gr.Row():
                        refresh_setting = setting_action.on_setting_ui()
                # with gr.TabItem("ReadMe"):
                #     with gr.Row():
                #         gr.Markdown(value=readmarkdown())

    # civitai tab start
    civitai_tabs.select(
        fn=on_civitai_tabs_select,
        inputs=None,        
        outputs=[refresh_civitai_sc_browser, refresh_recipe , refresh_classification, refresh_setting]
    )
         
def update_all_shortcut_informations():
    preISC = ishortcut.load()                           
    if not preISC:
        return
   
    modelid_list = [k for k in preISC]
    util.printD("shortcut update start")
    for modelid in modelid_list:
        ishortcut.write_model_information(modelid, False, None)     
    util.printD("shortcut update end")

def update_all_shortcut_informations_thread():
    try:
        thread = threading.Thread(target=update_all_shortcut_informations)
        thread.start()                
    except Exception as e:
        util.printD(e)
        pass
    
def init_civitai_shortcut():
    setting.init()
    model.update_downloaded_model()

    util.printD(setting.Extensions_Version)

    if setting.shortcut_update_when_start:        
        update_all_shortcut_informations_thread()

def on_ui_tabs():
    # init
    init_civitai_shortcut()

    with gr.Blocks() as civitai_shortcut:
        civitai_shortcut_ui()
        
    return (civitai_shortcut, "Civitai Shortcut", "civitai_shortcut"),


# Only register with WebUI if in WebUI mode
if WEBUI_MODE and script_callbacks:
    script_callbacks.on_ui_tabs(on_ui_tabs)
