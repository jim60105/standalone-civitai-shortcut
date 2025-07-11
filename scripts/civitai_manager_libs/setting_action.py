"""
Setting Action Module - Dual Mode Compatible.

This module has been modified to support both AUTOMATIC1111 and standalone modes
through the compatibility layer.
"""

import os
import copy
import gradio as gr
import shutil
from packaging import version

from .logging_config import get_logger

logger = get_logger(__name__)
from . import settings
from . import util
from .compat.compat_layer import CompatibilityLayer  # noqa: F401
from .error_handler import with_error_handling
from .exceptions import (
    FileOperationError,
    ConfigurationError,
)

# Compatibility layer variables
_compat_layer = None


def set_compatibility_layer(compat_layer):
    """Set compatibility layer."""
    global _compat_layer
    _compat_layer = compat_layer


def _check_ui_reload_required(old_env: dict, new_env: dict) -> bool:
    """Return True if changed settings require UI reload to take effect."""
    ui_dependent_keys = [
        ('screen_style', 'shortcut_browser_screen_split_ratio'),
        ('screen_style', 'information_gallery_height'),
        ('screen_style', 'gallery_thumbnail_image_style'),
        ('screen_style', 'shortcut_browser_search_up'),
        ('image_style', 'shortcut_column'),
        ('image_style', 'shortcut_rows_per_page'),
        ('image_style', 'gallery_column'),
        ('image_style', 'classification_shortcut_column'),
        ('image_style', 'classification_shortcut_rows_per_page'),
        ('image_style', 'classification_gallery_column'),
        ('image_style', 'classification_gallery_rows_per_page'),
    ]
    for section, key in ui_dependent_keys:
        if old_env.get(section, {}).get(key) != new_env.get(section, {}).get(key):
            return True
    return False


def on_setting_ui():
    with gr.Column():
        with gr.Row():
            with gr.Accordion("Option", open=False):
                with gr.Row():
                    civitai_api_key = gr.Textbox(
                        value=settings.civitai_api_key,
                        label="Civitai Api Key",
                        info=(
                            "To access the models that require you to be logged in. "
                            "Please obtain the key from: https://civitai.com/user/account."
                        ),
                        interactive=True,
                    )
                with gr.Row():
                    shortcut_update_when_start = gr.Checkbox(
                        value=settings.shortcut_update_when_start,
                        label=(
                            "Startup : The program performs 'Update the model information for the "
                            "shortcut' when it starts."
                        ),
                        info=(
                            "At program startup, the registered shortcuts are updated with the "
                            "latest data. This process operates in the background. To update "
                            "manually, you can uncheck that option and use the 'Scans and Model "
                            "Updates -> Update the model information for the shortcut' feature."
                        ),
                        interactive=True,
                    )
                    shortcut_max_download_image_per_version = gr.Slider(
                        minimum=0,
                        maximum=30,
                        value=settings.shortcut_max_download_image_per_version,
                        step=1,
                        info=(
                            "When registering a shortcut of a model, you can specify the maximum "
                            "number of images to download. This is the maximum per version, and "
                            "settings it to 0 means unlimited downloads."
                        ),
                        label='Maximum number of download images per version',
                        interactive=True,
                    )
        with gr.Row():
            with gr.Accordion("Screen Style", open=False):
                with gr.Row():
                    scbrowser_screen_split_ratio = gr.Slider(
                        minimum=0,
                        maximum=settings.shortcut_browser_screen_split_ratio_max,
                        value=settings.shortcut_browser_screen_split_ratio,
                        step=1,
                        info=(
                            "You can specify the size ratio between the shortcut browser and the "
                            "information screen."
                        ),
                        label='Model Browser screen ratio',
                        interactive=True,
                    )
                with gr.Row():
                    info_gallery_height = gr.Dropdown(
                        choices=["auto"],
                        value=settings.information_gallery_height,
                        allow_custom_value=True,
                        interactive=True,
                        info="You can also specify a specific size other than 'auto'",
                        label="Information Gallery Height",
                    )
                    gallery_thumbnail_image_style = gr.Dropdown(
                        choices=["scale-down", "cover", "contain", "fill", "none"],
                        value=settings.gallery_thumbnail_image_style,
                        interactive=True,
                        info="This specifies the shape of the displayed thumbnail.",
                        label="Gallery Thumbnail Image Style",
                    )
                    shortcut_browser_search_up = gr.Dropdown(
                        choices=["Up", "Down"],
                        value="Up" if settings.shortcut_browser_search_up else "Down",
                        interactive=True,
                        label="Set the position of the search bar in the shortcut browser.",
                        info=(
                            "If you select 'Up', the search bar will be placed above the "
                            "thumbnail pane."
                        ),
                    )

        with gr.Row():
            with gr.Tabs():
                with gr.TabItem("Model Browser and Model Information"):
                    with gr.Row():
                        shortcut_column = gr.Slider(
                            minimum=1,
                            maximum=14,
                            value=settings.shortcut_column,
                            step=1,
                            label='Model Browser Thumbnail Counts per Row',
                            interactive=True,
                        )
                        shortcut_rows_per_page = gr.Slider(
                            minimum=0,
                            maximum=14,
                            value=settings.shortcut_rows_per_page,
                            step=1,
                            label=(
                                'Model Browser Thumbnails Rows per Page : settings it to 0 means '
                                'displaying the entire list without a page.'
                            ),
                            interactive=True,
                        )
                    with gr.Row():
                        gallery_column = gr.Slider(
                            minimum=1,
                            maximum=14,
                            value=settings.gallery_column,
                            step=1,
                            label='Model Information Image Counts per Row',
                            interactive=True,
                        )
                with gr.TabItem("Civitai User Gallery"):
                    with gr.Row():
                        usergallery_images_column = gr.Slider(
                            minimum=1,
                            maximum=14,
                            value=settings.usergallery_images_column,
                            step=1,
                            label='Civitai User Gallery Image Counts per Row',
                            interactive=True,
                        )
                        usergallery_images_rows_per_page = gr.Slider(
                            minimum=1,
                            maximum=14,
                            value=settings.usergallery_images_rows_per_page,
                            step=1,
                            label='Civitai User Gallery Image Rows Per Page',
                            interactive=True,
                        )
                    with gr.Row():
                        usergallery_openfolder_btn = gr.Button(
                            value="Open Civitai User Gallery Cache Folder",
                            variant="primary",
                            visible=util.should_show_open_folder_buttons(),
                        )
                        with gr.Accordion("Clean User Gallery Cache", open=False):
                            usergallery_cleangallery_btn = gr.Button(
                                value="Clean Civitai User Gallery Cache", variant="primary"
                            )

        with gr.Row():
            with gr.Tabs():
                with gr.TabItem("Prompt Recipe"):
                    with gr.Row():
                        prompt_shortcut_column = gr.Slider(
                            minimum=1,
                            maximum=14,
                            value=settings.prompt_shortcut_column,
                            step=1,
                            label='Prompt Recipe Browser Thumbnail Counts per Row',
                            interactive=True,
                        )
                        prompt_shortcut_rows_per_page = gr.Slider(
                            minimum=1,
                            maximum=14,
                            value=settings.prompt_shortcut_rows_per_page,
                            step=1,
                            label='Prompt Recipe Browser Thumbnails Rows per Page',
                            interactive=True,
                        )
                    # with gr.TabItem("Shortcut Models for Reference"):
                    with gr.Row():
                        prompt_reference_shortcut_column = gr.Slider(
                            minimum=1,
                            maximum=14,
                            value=settings.prompt_reference_shortcut_column,
                            step=1,
                            label='Reference\'s Models Browser Thumbnail Counts per Row',
                            interactive=True,
                        )
                        prompt_reference_shortcut_rows_per_page = gr.Slider(
                            minimum=1,
                            maximum=14,
                            value=settings.prompt_reference_shortcut_rows_per_page,
                            step=1,
                            label=' Reference\'s Models Browser Thumbnails Rows per Page',
                            interactive=True,
                        )

        with gr.Row():
            with gr.Tabs():
                with gr.TabItem("Classification"):
                    with gr.Row():
                        classification_shortcut_column = gr.Slider(
                            minimum=1,
                            maximum=14,
                            value=settings.classification_shortcut_column,
                            step=1,
                            label='Classification\'s Model Browser Thumbnail Counts per Row',
                            interactive=True,
                        )
                        classification_shortcut_rows_per_page = gr.Slider(
                            minimum=0,
                            maximum=14,
                            value=settings.classification_shortcut_rows_per_page,
                            step=1,
                            label=(
                                'Classification\'s Model Browser Thumbnails Rows per Page : '
                                'settings it to 0 means displaying the entire list without a page.'
                            ),
                            interactive=True,
                        )
                    with gr.Row():
                        classification_gallery_column = gr.Slider(
                            minimum=1,
                            maximum=14,
                            value=settings.classification_gallery_column,
                            step=1,
                            label='Classification Model Counts per Row',
                            interactive=True,
                        )
                        classification_gallery_rows_per_page = gr.Slider(
                            minimum=0,
                            maximum=14,
                            value=settings.classification_gallery_rows_per_page,
                            step=1,
                            label=(
                                'Classification Model Rows per Page : settings it to 0 means '
                                'displaying the entire list without a page.'
                            ),
                            interactive=True,
                        )

        with gr.Row():
            with gr.Accordion("Download Folder for Extensions", open=False):
                with gr.Column():
                    extension_locon_folder = gr.Textbox(
                        value=settings.model_folders['LoCon'], label="LyCORIS", interactive=True
                    )
                    extension_wildcards_folder = gr.Textbox(
                        value=settings.model_folders['Wildcards'],
                        label="Wildcards",
                        interactive=True,
                    )
                    extension_controlnet_folder = gr.Textbox(
                        value=settings.model_folders['Controlnet'],
                        label="Controlnet",
                        interactive=True,
                    )
                    extension_aestheticgradient_folder = gr.Textbox(
                        value=settings.model_folders['AestheticGradient'],
                        label="Aesthetic Gradient",
                        interactive=True,
                    )
                    extension_poses_folder = gr.Textbox(
                        value=settings.model_folders['Poses'], label="Poses", interactive=True
                    )
                    extension_other_folder = gr.Textbox(
                        value=settings.model_folders['Other'], label="Other", interactive=True
                    )
                    download_images_folder = gr.Textbox(
                        value=settings.download_images_folder,
                        label="Download Images Folder",
                        interactive=True,
                    )

        with gr.Row():
            save_btn = gr.Button(value="Save Setting", variant="primary")
            reload_btn = gr.Button(value="Reload UI")
            refresh_setting = gr.Textbox(visible=False)

    refresh_setting.change(
        fn=on_refresh_setting_change,
        inputs=None,
        outputs=[
            civitai_api_key,
            shortcut_update_when_start,
            scbrowser_screen_split_ratio,
            info_gallery_height,
            shortcut_column,
            shortcut_rows_per_page,
            gallery_column,
            classification_shortcut_column,
            classification_shortcut_rows_per_page,
            classification_gallery_column,
            classification_gallery_rows_per_page,
            usergallery_images_column,
            usergallery_images_rows_per_page,
            prompt_shortcut_column,
            prompt_shortcut_rows_per_page,
            prompt_reference_shortcut_column,
            prompt_reference_shortcut_rows_per_page,
            shortcut_max_download_image_per_version,
            gallery_thumbnail_image_style,
            shortcut_browser_search_up,
            extension_locon_folder,
            extension_wildcards_folder,
            extension_controlnet_folder,
            extension_aestheticgradient_folder,
            extension_poses_folder,
            extension_other_folder,
            download_images_folder,
        ],
        show_progress=False,
    )

    # reload the page
    # Check if we have a compatibility layer to determine environment
    try:
        # In WebUI mode, use the JavaScript function
        if _compat_layer and _compat_layer.mode == 'webui':
            # Dynamically select the correct JS argument for Gradio v3/v4 compatibility
            gradio_version = version.parse(gr.__version__)
            # Gradio <=4.0.1 uses '_js', >4.0.1 uses 'js'
            js_arg = '_js' if gradio_version <= version.parse('4.0.1') else 'js'
            reload_btn.click(
                fn=on_reload_btn_click, **{js_arg: 'restart_reload'}, inputs=None, outputs=None
            )
        else:
            # In standalone mode, use Python-only restart (no JavaScript needed)
            reload_btn.click(fn=on_reload_btn_click, inputs=None, outputs=None)
    except Exception as e:
        logger.warning(f"Failed to determine environment for reload button: {e}")
        # Fallback to Python-only reload
        reload_btn.click(fn=on_reload_btn_click, inputs=None, outputs=None)

    if util.should_show_open_folder_buttons():
        usergallery_openfolder_btn.click(
            fn=on_usergallery_openfolder_btn_click, inputs=None, outputs=None
        )

    usergallery_cleangallery_btn.click(
        fn=on_usergallery_cleangallery_btn_click, inputs=None, outputs=None
    )

    save_btn.click(
        fn=on_save_btn_click,
        inputs=[
            civitai_api_key,
            shortcut_update_when_start,
            scbrowser_screen_split_ratio,
            info_gallery_height,
            shortcut_column,
            shortcut_rows_per_page,
            gallery_column,
            classification_shortcut_column,
            classification_shortcut_rows_per_page,
            classification_gallery_column,
            classification_gallery_rows_per_page,
            usergallery_images_column,
            usergallery_images_rows_per_page,
            prompt_shortcut_column,
            prompt_shortcut_rows_per_page,
            prompt_reference_shortcut_column,
            prompt_reference_shortcut_rows_per_page,
            shortcut_max_download_image_per_version,
            gallery_thumbnail_image_style,
            shortcut_browser_search_up,
            extension_locon_folder,
            extension_wildcards_folder,
            extension_controlnet_folder,
            extension_aestheticgradient_folder,
            extension_poses_folder,
            extension_other_folder,
            download_images_folder,
        ],
        outputs=None,
    )

    return refresh_setting


@with_error_handling(
    fallback_value=None,
    exception_types=(FileOperationError, ConfigurationError),
    retry_count=2,
    user_message="Failed to save settings",
)
def on_save_btn_click(
    civitai_api_key,
    shortcut_update_when_start,
    scbrowser_screen_split_ratio,
    info_gallery_height,
    shortcut_column,
    shortcut_rows_per_page,
    gallery_column,
    classification_shortcut_column,
    classification_shortcut_rows_per_page,
    classification_gallery_column,
    classification_gallery_rows_per_page,
    usergallery_images_column,
    usergallery_images_rows_per_page,
    prompt_shortcut_column,
    prompt_shortcut_rows_per_page,
    prompt_reference_shortcut_column,
    prompt_reference_shortcut_rows_per_page,
    shortcut_max_download_image_per_version,
    gallery_thumbnail_image_style,
    shortcut_browser_search_up,
    locon,
    wildcards,
    controlnet,
    aestheticgradient,
    poses,
    other,
    download_images_folder,
):
    logger.debug(
        "[on_save_btn_click] Called with params: "
        "civitai_api_key=%s, shortcut_update_when_start=%s, "
        "scbrowser_screen_split_ratio=%s, ... (truncated)",
        civitai_api_key,
        shortcut_update_when_start,
        scbrowser_screen_split_ratio,
    )
    save_setting(
        civitai_api_key,
        shortcut_update_when_start,
        scbrowser_screen_split_ratio,
        info_gallery_height,
        shortcut_column,
        shortcut_rows_per_page,
        gallery_column,
        classification_shortcut_column,
        classification_shortcut_rows_per_page,
        classification_gallery_column,
        classification_gallery_rows_per_page,
        usergallery_images_column,
        usergallery_images_rows_per_page,
        prompt_shortcut_column,
        prompt_shortcut_rows_per_page,
        prompt_reference_shortcut_column,
        prompt_reference_shortcut_rows_per_page,
        shortcut_max_download_image_per_version,
        gallery_thumbnail_image_style,
        shortcut_browser_search_up,
        locon,
        wildcards,
        controlnet,
        aestheticgradient,
        poses,
        other,
        download_images_folder,
    )


def save_setting(
    civitai_api_key,
    shortcut_update_when_start,
    scbrowser_screen_split_ratio,
    info_gallery_height,
    shortcut_column,
    shortcut_rows_per_page,
    gallery_column,
    classification_shortcut_column,
    classification_shortcut_rows_per_page,
    classification_gallery_column,
    classification_gallery_rows_per_page,
    usergallery_images_column,
    usergallery_images_rows_per_page,
    prompt_shortcut_column,
    prompt_shortcut_rows_per_page,
    prompt_reference_shortcut_column,
    prompt_reference_shortcut_rows_per_page,
    shortcut_max_download_image_per_version,
    gallery_thumbnail_image_style,
    shortcut_browser_search_up,
    locon,
    wildcards,
    controlnet,
    aestheticgradient,
    poses,
    other,
    download_images_folder,
):
    logger.debug(
        "[save_setting] Called with params: "
        "civitai_api_key=%s, shortcut_update_when_start=%s, "
        "scbrowser_screen_split_ratio=%s, ... (truncated)",
        civitai_api_key,
        shortcut_update_when_start,
        scbrowser_screen_split_ratio,
    )
    environment = settings.load()
    if not environment:
        environment = dict()
    old_env = copy.deepcopy(environment)

    application_allow = dict()
    application_allow['civitai_api_key'] = civitai_api_key
    application_allow['shortcut_update_when_start'] = shortcut_update_when_start
    application_allow['shortcut_max_download_image_per_version'] = (
        shortcut_max_download_image_per_version
    )
    environment['application_allow'] = application_allow

    screen_style = dict()
    screen_style['shortcut_browser_screen_split_ratio'] = scbrowser_screen_split_ratio
    screen_style['information_gallery_height'] = info_gallery_height
    screen_style['gallery_thumbnail_image_style'] = gallery_thumbnail_image_style
    screen_style['shortcut_browser_search_up'] = (
        True if shortcut_browser_search_up == "Up" else False
    )
    environment['screen_style'] = screen_style

    image_style = dict()
    image_style['shortcut_column'] = shortcut_column
    image_style['shortcut_rows_per_page'] = shortcut_rows_per_page

    image_style['gallery_column'] = gallery_column

    image_style['classification_shortcut_column'] = classification_shortcut_column
    image_style['classification_shortcut_rows_per_page'] = classification_shortcut_rows_per_page
    image_style['classification_gallery_column'] = classification_gallery_column
    image_style['classification_gallery_rows_per_page'] = classification_gallery_rows_per_page

    image_style['usergallery_images_column'] = usergallery_images_column
    image_style['usergallery_images_rows_per_page'] = usergallery_images_rows_per_page

    image_style['prompt_shortcut_column'] = prompt_shortcut_column
    image_style['prompt_shortcut_rows_per_page'] = prompt_shortcut_rows_per_page
    image_style['prompt_reference_shortcut_column'] = prompt_reference_shortcut_column
    image_style['prompt_reference_shortcut_rows_per_page'] = prompt_reference_shortcut_rows_per_page

    environment['image_style'] = image_style

    model_folders = dict()
    if locon:
        model_folders['LoCon'] = locon
    if wildcards:
        model_folders['Wildcards'] = wildcards
    if controlnet:
        model_folders['Controlnet'] = controlnet
    if aestheticgradient:
        model_folders['AestheticGradient'] = aestheticgradient
    if poses:
        model_folders['Poses'] = poses
    if other:
        model_folders['Other'] = other

    environment['model_folders'] = model_folders

    download_folders = dict()
    if download_images_folder:
        download_folders['download_images'] = download_images_folder

    environment['download_folders'] = download_folders

    temporary = dict()

    environment['temporary'] = temporary

    logger.debug("[save_setting] environment to be saved: %s", environment)
    settings.save_setting(environment)
    from .settings.path_manager import load_model_folder_data
    from .settings import config_manager

    load_model_folder_data(config_manager)

    # notify user based on whether layout reload is needed
    ui_reload_needed = _check_ui_reload_required(old_env, environment)

    try:
        if ui_reload_needed:
            gr.Info(
                "⚙️ Settings saved! Some layout changes require UI reload to take effect. "
                "Please click the 'Reload UI' button below.",
                duration=8,
            )
        else:
            gr.Info(
                "✅ Settings saved and applied successfully!",
                duration=3,
            )
    except Exception as e:
        logger.error(f"Failed to show settings save notification: {e}")

    # log for debugging purposes
    if ui_reload_needed:
        logger.info("Settings saved. UI reload recommended for layout changes.")
    else:
        logger.info("Settings saved and applied successfully.")


@with_error_handling(
    fallback_value=None,
    exception_types=(FileOperationError,),
    user_message="Failed to open gallery folder",
)
def on_usergallery_openfolder_btn_click():
    if os.path.exists(settings.shortcut_gallery_folder):
        util.open_folder(settings.shortcut_gallery_folder)


@with_error_handling(
    fallback_value=None,
    exception_types=(FileOperationError,),
    retry_count=1,
    user_message="Failed to clean gallery folder",
)
def on_usergallery_cleangallery_btn_click():
    if os.path.exists(settings.shortcut_gallery_folder):
        shutil.rmtree(settings.shortcut_gallery_folder)


@with_error_handling(
    fallback_value=None, exception_types=(Exception,), user_message="Failed to reload application"
)
def on_reload_btn_click():
    request_restart()


def request_restart():
    """Request application restart."""
    try:
        # Check if we have a compatibility layer to determine environment
        if _compat_layer and _compat_layer.mode == 'webui':
            # WebUI mode: use shared.state for restart
            try:
                from modules import shared  # noqa: F401

                shared.state.interrupt()
                shared.state.need_restart = True
                logger.info("WebUI restart requested")
            except ImportError as e:
                logger.warning(f"Failed to import WebUI modules: {e}")
                raise
        else:
            # Standalone mode: perform process restart
            import sys
            import os

            try:
                import psutil

                p = psutil.Process(os.getpid())
                for handler in p.open_files() + p.connections():
                    os.close(handler.fd)
            except Exception as e:
                logger.error(f"Failed to cleanup process resources: {e}")

            logger.info("Performing process restart for standalone mode")
            python = sys.executable
            os.execl(python, python, *sys.argv)
    except ImportError:
        # Fallback for standalone mode when modules are not available
        import sys
        import os

        try:
            import psutil

            p = psutil.Process(os.getpid())
            for handler in p.open_files() + p.connections():
                os.close(handler.fd)
        except Exception as e:
            logger.error(f"Failed to cleanup process resources: {e}")

        logger.info("Performing fallback process restart")
        python = sys.executable
        os.execl(python, python, *sys.argv)
    except Exception as e:
        logger.error(f"Failed to request restart: {e}")
        # Last resort: perform process restart
        import sys
        import os

        try:
            import psutil

            p = psutil.Process(os.getpid())
            for handler in p.open_files() + p.connections():
                os.close(handler.fd)
        except Exception as cleanup_e:
            logger.error(f"Failed to cleanup process resources: {cleanup_e}")

        logger.warning("Performing process restart as last resort")
        python = sys.executable
        os.execl(python, python, *sys.argv)


# def on_update_btn_click():
#     git = os.environ.get('GIT', "git")

#     subdir = os.path.dirname(os.path.abspath(__file__))

#     # perform git pull in the extension folder
#     output = subprocess.check_output([git, '-C', subdir, 'pull', '--autostash'])
#     print(output.decode('utf-8'))


def on_refresh_setting_change():
    return (
        settings.civitai_api_key,
        settings.shortcut_update_when_start,
        settings.shortcut_browser_screen_split_ratio,
        settings.information_gallery_height,
        settings.shortcut_column,
        settings.shortcut_rows_per_page,
        settings.gallery_column,
        settings.classification_shortcut_column,
        settings.classification_shortcut_rows_per_page,
        settings.classification_gallery_column,
        settings.classification_gallery_rows_per_page,
        settings.usergallery_images_column,
        settings.usergallery_images_rows_per_page,
        settings.prompt_shortcut_column,
        settings.prompt_shortcut_rows_per_page,
        settings.prompt_reference_shortcut_column,
        settings.prompt_reference_shortcut_rows_per_page,
        settings.shortcut_max_download_image_per_version,
        settings.gallery_thumbnail_image_style,
        "Up" if settings.shortcut_browser_search_up else "Down",
        settings.model_folders['LoCon'],
        settings.model_folders['Wildcards'],
        settings.model_folders['Controlnet'],
        settings.model_folders['AestheticGradient'],
        settings.model_folders['Poses'],
        settings.model_folders['Other'],
        settings.download_images_folder,
    )
