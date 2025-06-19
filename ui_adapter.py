"""
UI Adapter for Civitai Shortcut Standalone Mode

This module adapts the existing UI components for standalone execution,
providing compatibility layer injection and proper initialization.
"""

import sys
import gradio as gr

# Core modules for initialization
import datetime

from scripts.civitai_manager_libs import setting, model, util


def create_civitai_shortcut_ui(compat_layer):
    """
    Create adapted Civitai Shortcut UI for standalone mode.

    Args:
        compat_layer: The compatibility layer instance
    """
    # Inject compatibility layer to all action modules
    _inject_compatibility_layer(compat_layer)

    # Initialize components
    _initialize_components(compat_layer)

    # Import action modules after injection
    from scripts.civitai_manager_libs import (
        civitai_shortcut_action,
        recipe_action,
        classification_action,
        setting_action,
        scan_action,
    )

    # Create main UI structure
    with gr.Tabs(elem_id="civitai_shortcut_tabs_container") as civitai_tabs:
        with gr.Row(visible=False):
            recipe_input = gr.Textbox()
            shortcut_input = gr.Textbox()

        with gr.TabItem("🏠 Model Browser", id="Shortcut"):
            with gr.Row():
                # Invoke on_ui for model browser; may return multiple values or None
                _ = civitai_shortcut_action.on_ui(recipe_input, shortcut_input, civitai_tabs)

        with gr.TabItem("📝 Prompt Recipe", id="Recipe"):
            with gr.Row():
                refresh_recipe = recipe_action.on_ui(recipe_input, shortcut_input, civitai_tabs)

        with gr.TabItem("🔧 Assistance", id="Assistance"):
            with gr.Tabs():
                with gr.TabItem("Classification"):
                    with gr.Row():
                        refresh_classification = classification_action.on_ui(shortcut_input)
                with gr.TabItem("Scan and Update Models"):
                    with gr.Row():
                        scan_action.on_scan_ui()

        with gr.TabItem("⚙️ Settings", id="Manage"):
            with gr.Tabs():
                with gr.TabItem("Application Settings"):
                    with gr.Row():
                        refresh_setting = setting_action.on_setting_ui()
                with gr.TabItem("Standalone Configuration"):
                    with gr.Row():
                        _create_standalone_settings_ui(compat_layer)

        # Setup tab selection events
        civitai_tabs.select(
            fn=_on_civitai_tabs_select,
            inputs=None,
            outputs=[
                refresh_recipe,
                refresh_classification,
                refresh_setting,
            ],
        )


def _inject_compatibility_layer(compat_layer):
    """
    Inject compatibility layer into all action modules.

    Args:
        compat_layer: The compatibility layer instance
    """
    modules_to_inject = [
        'scripts.civitai_manager_libs.civitai_shortcut_action',
        'scripts.civitai_manager_libs.recipe_action',
        'scripts.civitai_manager_libs.classification_action',
        'scripts.civitai_manager_libs.setting_action',
        'scripts.civitai_manager_libs.scan_action',
        'scripts.civitai_manager_libs.model_action',
        'scripts.civitai_manager_libs.setting',
        'scripts.civitai_manager_libs.model',
        'scripts.civitai_manager_libs.ishortcut',
        'scripts.civitai_manager_libs.recipe',
        'scripts.civitai_manager_libs.classification',
        'scripts.civitai_manager_libs.util',
    ]

    for module_name in modules_to_inject:
        if module_name in sys.modules:
            module = sys.modules[module_name]
            if hasattr(module, 'set_compatibility_layer'):
                module.set_compatibility_layer(compat_layer)
            # Also set as global variable for modules that expect it
            setattr(module, '_compat_layer', compat_layer)


def _initialize_components(compat_layer):
    """
    Initialize core components for standalone mode.

    Args:
        compat_layer: The compatibility layer instance
    """
    try:
        setting.init()
        model.update_downloaded_model()
        util.printD("Civitai Shortcut initialized in standalone mode")
    except Exception as e:
        print(f"Warning: Failed to initialize some components: {e}")


def _create_standalone_settings_ui(compat_layer):
    """
    Create standalone mode specific settings UI.

    Args:
        compat_layer: The compatibility layer instance
    """
    with gr.Column():
        gr.Markdown("## 🖥️ Server Configuration")

        host_input = gr.Textbox(
            label="Host Address",
            value=compat_layer.config_manager.get('server.host', '127.0.0.1'),
            placeholder="127.0.0.1",
        )

        port_input = gr.Number(
            label="Port",
            value=compat_layer.config_manager.get('server.port', 7860),
            precision=0,
            minimum=1,
            maximum=65535,
        )

        share_enabled = gr.Checkbox(
            label="Enable Share Link", value=compat_layer.config_manager.get('server.share', False)
        )

        gr.Markdown("## 🌐 Civitai Configuration")

        api_key_input = gr.Textbox(
            label="API Key",
            type="password",
            value=compat_layer.config_manager.get('civitai.api_key', ''),
            placeholder="Optional: Enter your Civitai API key",
        )

        download_path_input = gr.Textbox(
            label="Download Path",
            value=compat_layer.config_manager.get('civitai.download_path', './models'),
            placeholder="./models",
        )

        gr.Markdown("## 💾 Cache Configuration")

        cache_enabled = gr.Checkbox(
            label="Enable Cache",
            value=compat_layer.config_manager.get('civitai.cache_enabled', True),
        )

        cache_size = gr.Slider(
            label="Cache Size (MB)",
            minimum=100,
            maximum=2000,
            value=compat_layer.config_manager.get('civitai.cache_size_mb', 500),
            step=50,
        )

        gr.Markdown("## 🐛 Debug Configuration")

        debug_enabled = gr.Checkbox(
            label="Enable Debug Mode", value=compat_layer.config_manager.get('debug.enabled', False)
        )

        with gr.Row():
            save_button = gr.Button("💾 Save Configuration", variant="primary")
            reset_button = gr.Button("🔄 Reset to Defaults", variant="secondary")

        status_output = gr.Textbox(label="Status", interactive=False, visible=False)

        def save_settings(
            host,
            port,
            share,
            api_key,
            download_path,
            cache_enabled_val,
            cache_size_val,
            debug_enabled_val,
        ):
            """Save standalone settings"""
            try:
                settings_map = {
                    'server.host': host,
                    'server.port': int(port),
                    'server.share': share,
                    'civitai.api_key': api_key,
                    'civitai.download_path': download_path,
                    'civitai.cache_enabled': cache_enabled_val,
                    'civitai.cache_size_mb': int(cache_size_val),
                    'debug.enabled': debug_enabled_val,
                }

                for key, value in settings_map.items():
                    compat_layer.config_manager.set(key, value)

                compat_layer.config_manager.save()
                return gr.update(value="✅ Configuration saved successfully!", visible=True)

            except Exception as e:
                return gr.update(value=f"❌ Error saving configuration: {e}", visible=True)

        def reset_settings():
            """Reset settings to defaults"""
            try:
                compat_layer.config_manager.reset_to_defaults()
                return (
                    gr.update(value='127.0.0.1'),  # host
                    gr.update(value=7860),  # port
                    gr.update(value=False),  # share
                    gr.update(value=''),  # api_key
                    gr.update(value='./models'),  # download_path
                    gr.update(value=True),  # cache_enabled
                    gr.update(value=500),  # cache_size
                    gr.update(value=False),  # debug_enabled
                    gr.update(value="🔄 Settings reset to defaults", visible=True),
                )
            except Exception as e:
                return (
                    gr.update(),  # host
                    gr.update(),  # port
                    gr.update(),  # share
                    gr.update(),  # api_key
                    gr.update(),  # download_path
                    gr.update(),  # cache_enabled
                    gr.update(),  # cache_size
                    gr.update(),  # debug_enabled
                    gr.update(value=f"❌ Error resetting settings: {e}", visible=True),
                )

        save_button.click(
            save_settings,
            inputs=[
                host_input,
                port_input,
                share_enabled,
                api_key_input,
                download_path_input,
                cache_enabled,
                cache_size,
                debug_enabled,
            ],
            outputs=[status_output],
        )

        reset_button.click(
            reset_settings,
            inputs=[],
            outputs=[
                host_input,
                port_input,
                share_enabled,
                api_key_input,
                download_path_input,
                cache_enabled,
                cache_size,
                debug_enabled,
                status_output,
            ],
        )


def _on_civitai_tabs_select(evt):
    """
    Handle tab selection events.

    Args:
        evt (gr.SelectData): Selection event data

    Returns:
        tuple: Updated visibility states for refresh components
    """
    current_time = datetime.datetime.now()
    # Use gr.update if available, otherwise fallback to no-op
    update = getattr(gr, 'update', lambda **kwargs: None)

    if evt.index == 0:
        return (
            current_time,
            update(visible=False),
            update(visible=False),
            update(visible=False),
        )
    elif evt.index == 1:
        return (
            update(visible=False),
            current_time,
            update(visible=False),
            update(visible=False),
        )
    elif evt.index == 2:
        return (
            update(visible=False),
            update(visible=False),
            current_time,
            update(visible=False),
        )
    elif evt.index == 3:
        return (
            update(visible=False),
            update(visible=False),
            update(visible=False),
            current_time,
        )

    return (
        update(visible=False),
        update(visible=False),
        update(visible=False),
        update(visible=False),
    )
