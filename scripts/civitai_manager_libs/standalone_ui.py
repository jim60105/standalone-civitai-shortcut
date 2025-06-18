"""
Standalone mode UI components for enhanced layout and styling.
Provides header, status bar, navigation tabs, model card and progress widgets.
"""

import os
import gradio as gr
from typing import Dict, Any


class StandaloneUIComponents:
    """UI components wrapper for standalone mode styling and layout."""

    def __init__(self) -> None:
        self.css_theme = self._load_theme()

    def _load_theme(self) -> str:
        """Load main CSS theme from style.css if available."""
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        css_path = os.path.join(root, 'style.css')
        try:
            with open(css_path, encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return self._get_default_theme()

    def _get_default_theme(self) -> str:
        """Return default inline CSS theme."""
        return """
        .civitai-header { background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px; color: white; text-align: center; }
        .civitai-card { border:1px solid #e1e5e9; border-radius:8px; padding:16px; margin:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1); }
        .civitai-preview { max-width:100%; max-height:200px; object-fit:cover; border-radius:6px; }
        .progress-container { background:#f8f9fa; border-radius:6px; padding:10px; margin:10px 0; }
        """

    def create_header(self) -> gr.HTML:
        """Create top header HTML block."""
        html = (
            '<div class="civitai-header">'
            '<h1>🎨 Civitai Shortcut</h1>'
            '<p>AI Model Manager & Downloader - Standalone</p>'
            '</div>'
        )
        return gr.HTML(html)

    def create_status_bar(self) -> Dict[str, gr.Component]:
        """Create a status bar displaying state and version info."""
        with gr.Row(elem_classes='status-bar'):
            status_text = gr.Markdown('Ready', elem_classes='status-text')
            version_info = gr.Markdown('Version: 2.0.0', elem_classes='version-info')
        return {'status_text': status_text, 'version_info': version_info}

    def create_navigation_tabs(self) -> gr.Tabs:
        """Return navigation tabs container."""
        return gr.Tabs(elem_classes='main-tabs')

    def create_model_card(self, model_info: Dict[str, Any]) -> gr.HTML:
        """Build a model info card HTML."""
        html = (
            '<div class="civitai-card">'
            f'<img src="{model_info.get("preview_url","")}" class="civitai-preview"/>'
            f'<h3>{model_info.get("name","Unknown")}</h3>'
            f'<p>{model_info.get("description","No description")}</p>'
            '<div class="model-stats">'
            f'<span>Downloads: {model_info.get("download_count",0)}</span>'
            f'<span>Rating: {model_info.get("rating","N/A")}</span>'
            '</div>'
            '</div>'
        )
        return gr.HTML(html)

    def create_download_progress(self) -> Dict[str, gr.Component]:
        """Create download progress UI widgets."""
        with gr.Column(elem_classes='progress-container', visible=False) as container:
            progress_text = gr.Markdown('Preparing download...')
            progress_bar = gr.Progress()
            cancel_button = gr.Button('Cancel Download', variant='stop')
        return {
            'container': container,
            'progress_text': progress_text,
            'progress_bar': progress_bar,
            'cancel_button': cancel_button,
        }
