import datetime
import gradio as gr
import threading

# Try to import WebUI modules, fallback if not available
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
from scripts.civitai_manager_libs.logging_config import get_logger

# Module logger
logger = get_logger(__name__)
from scripts.civitai_manager_libs import ishortcut_core as ishortcut
from scripts.civitai_manager_libs import recipe_action
from scripts.civitai_manager_libs.module_compatibility import initialize_compatibility_layer


# Initialize compatibility layer for all modules
def initialize_civitai_shortcut():
    """Initialize Civitai Shortcut with compatibility layer."""
    try:
        from scripts.civitai_manager_libs.compat.compat_layer import CompatibilityLayer
        from scripts.civitai_manager_libs.compat.environment_detector import EnvironmentDetector

        # Detect environment and create compatibility layer
        env = EnvironmentDetector.detect_environment()
        compat_layer = CompatibilityLayer(mode=env)

        # Initialize all modules with compatibility layer
        initialize_compatibility_layer(compat_layer)

        logger.info(f"Civitai Shortcut initialized in {env} mode")

        return compat_layer

    except Exception as e:
        logger.warning(f"Failed to initialize compatibility layer: {e}")
        logger.info("Running in fallback mode")
        return None


# Initialize on import
_compatibility_layer = initialize_civitai_shortcut()


def on_civitai_tabs_select(evt: gr.SelectData):
    current_time = datetime.datetime.now()
    if evt.index == 0:
        return (
            current_time,
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
        )
    elif evt.index == 1:
        return (
            gr.update(visible=False),
            current_time,
            gr.update(visible=False),
            gr.update(visible=False),
        )
    elif evt.index == 2:
        return (
            gr.update(visible=False),
            gr.update(visible=False),
            current_time,
            gr.update(visible=False),
        )
    elif evt.index == 3:
        return (
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            current_time,
        )

    return (
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
    )


# def readmarkdown():
#     path = os.path.join(setting.extension_base,"README.md")
#     markdown_text = None
#     try:
#         with open(path, 'r',encoding='UTF-8') as f:
#             markdown_text = f.read()
#     except Exception as e:
#         logger.error(f"{e}")
#         return
#     return markdown_text


def civitai_shortcut_ui():
    """Create the main Civitai Shortcut UI with dual-mode support."""
    # Setup UI components for dual-mode
    from scripts.civitai_manager_libs.compat.compat_layer import CompatibilityLayer

    compat_layer = _compatibility_layer or CompatibilityLayer.get_compatibility_layer()

    # Initialize enhanced UI components for standalone mode
    if compat_layer and compat_layer.mode == 'standalone':
        from scripts.civitai_manager_libs.standalone_ui import StandaloneUIComponents

        standalone_ui = StandaloneUIComponents()

        # Add header for standalone mode
        standalone_ui.create_header()

    with gr.Tabs(elem_id="civitai_shortcut_tabs_container") as civitai_tabs:
        with gr.Row(visible=False):
            recipe_input = gr.Textbox()
            shortcut_input = gr.Textbox()

        with gr.TabItem("Model Browser", id="Shortcut"):
            with gr.Row():
                refresh_civitai_sc_browser, refresh_civitai_information = (
                    civitai_shortcut_action.on_ui(recipe_input, shortcut_input, civitai_tabs)
                )

        with gr.TabItem("Prompt Recipe", id="Recipe"):
            with gr.Row():
                refresh_recipe = recipe_action.on_ui(recipe_input, shortcut_input, civitai_tabs)

        with gr.TabItem("Assistance", id="Assistance"):
            with gr.Tabs():
                with gr.TabItem("Classification"):
                    with gr.Row():
                        refresh_classification = classification_action.on_ui(shortcut_input)
                with gr.TabItem("Scan and Update Models"):
                    with gr.Row():
                        scan_action.on_scan_ui()

        with gr.TabItem("Manage", id="Manage"):
            with gr.Tabs():
                with gr.TabItem("Setting"):
                    with gr.Row():
                        refresh_setting = setting_action.on_setting_ui()

    # Setup parameter copy-paste functionality if available
    if compat_layer:
        try:
            civitai_shortcut_action.setup_ui_copypaste(compat_layer)
            # This would be integrated into specific UI components as needed
        except Exception as e:
            logger.error(f"Failed to setup copy-paste functionality: {e}")

    # civitai tab start
    civitai_tabs.select(
        fn=on_civitai_tabs_select,
        inputs=None,
        outputs=[
            refresh_civitai_sc_browser,
            refresh_recipe,
            refresh_classification,
            refresh_setting,
        ],
    )


def update_all_shortcut_informations():
    preISC = ishortcut.shortcutcollectionmanager.load_shortcuts()
    if not preISC:
        return

    modelid_list = [k for k in preISC]
    logger.debug("shortcut update start")
    for modelid in modelid_list:
        ishortcut.fileprocessor.write_model_information(modelid, False, None)
    logger.debug("shortcut update end")


def update_all_shortcut_informations_thread():
    try:
        thread = threading.Thread(target=update_all_shortcut_informations)
        thread.start()
    except Exception as e:
        logger.error(f"{e}")
        pass


def init_civitai_shortcut():
    setting.init()
    model.update_downloaded_model()

    logger.info(setting.Extensions_Version)

    if setting.shortcut_update_when_start:
        update_all_shortcut_informations_thread()


def on_ui_tabs():
    # init
    init_civitai_shortcut()

    with gr.Blocks() as civitai_shortcut:
        civitai_shortcut_ui()

    return ((civitai_shortcut, "Civitai Shortcut", "civitai_shortcut"),)


# Only register with WebUI if available
if WEBUI_MODE and script_callbacks:
    script_callbacks.on_ui_tabs(on_ui_tabs)
