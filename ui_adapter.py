"""
UI Adapter for Civitai Shortcut Standalone Mode.

This module adapts the existing UI components for standalone execution,
providing compatibility layer injection and proper initialization.
"""

import gradio as gr

# Core modules for initialization
import datetime

from scripts.civitai_manager_libs import (
    util,
    civitai_shortcut_action,
    recipe_action,
    classification_action,
    setting_action,
    scan_action,
    module_compatibility,
)


def create_civitai_shortcut_ui(compat_layer):
    """
    Create adapted Civitai Shortcut UI for standalone mode.

    Args:
        compat_layer: The compatibility layer instance
    """
    # Initialize compatibility layer for all modules
    module_compatibility.initialize_compatibility_layer(compat_layer)

    # Create main UI structure
    with gr.Tabs(elem_id="civitai_shortcut_tabs_container") as civitai_tabs:
        with gr.Row(visible=False):
            recipe_input = gr.Textbox()
            shortcut_input = gr.Textbox()

        with gr.TabItem("🏠 Model Browser", id="Shortcut"):
            with gr.Row():
                refresh_civitai_sc_browser, refresh_civitai_information = (
                    civitai_shortcut_action.on_ui(recipe_input, shortcut_input, civitai_tabs)
                )

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

        # Setup tab selection events
        civitai_tabs.select(
            fn=_on_civitai_tabs_select,
            inputs=None,
            outputs=[
                refresh_civitai_sc_browser,
                refresh_recipe,
                refresh_classification,
                refresh_setting,
            ],
        )

def _on_civitai_tabs_select(evt: gr.SelectData):
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

    if evt is None:
        util.printD(
            "[ui_adapter] _on_civitai_tabs_select: evt is None, skipping tab selection logic."
        )
        update = getattr(gr, 'update', lambda **kwargs: None)
        return (
            update(visible=False),
            update(visible=False),
            update(visible=False),
            update(visible=False),
        )

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
