"""
Standalone launcher for Civitai Shortcut application using Gradio.

This script enables running the Civitai Shortcut in standalone mode
without AUTOMATIC1111 WebUI integration.
"""

import gradio as gr
import argparse
import os

from scripts.civitai_shortcut import civitai_shortcut_ui


def create_standalone_app() -> gr.Blocks:
    """Create standalone Gradio Blocks application."""
    # Mark mode for compatibility layer
    os.environ['CIVITAI_SHORTCUT_MODE'] = 'standalone'

    # Load CSS theme
    css_theme = _load_standalone_css()
    
    with gr.Blocks(
        title='Civitai Shortcut - Standalone Version',
        theme=gr.themes.Default(),
        css=css_theme
    ) as app:
        # Create standalone header
        _create_header()
        
        # Main UI
        civitai_shortcut_ui()
        
        # Create footer
        _create_footer()
        
    return app


def _load_standalone_css() -> str:
    """Load CSS theme for standalone mode."""
    css_path = os.path.join(os.path.dirname(__file__), 'style.css')
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return _get_default_css()


def _get_default_css() -> str:
    """Return default CSS for standalone mode."""
    return """
    /* Standalone Mode CSS */
    .gradio-container {
        max-width: none !important;
        margin: 0 auto;
    }
    
    .civitai-header {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 20px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        border-radius: 8px;
    }
    
    .civitai-card {
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        padding: 16px;
        margin: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: box-shadow 0.2s ease;
    }
    
    .civitai-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .civitai-preview {
        max-width: 100%;
        max-height: 200px;
        object-fit: cover;
        border-radius: 6px;
    }
    
    .model-stats {
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
        font-size: 0.9em;
        color: #666;
    }
    
    .progress-container {
        background: #f8f9fa;
        border-radius: 6px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid #dee2e6;
    }
    
    .status-bar {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .footer {
        text-align: center;
        padding: 20px;
        margin-top: 30px;
        border-top: 1px solid #e1e5e9;
        color: #666;
        font-size: 0.9em;
    }
    
    /* Tab styling */
    #civitai_shortcut_tabs_container {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Button styling */
    .gradio-button {
        border-radius: 6px !important;
        border: 1px solid #ddd !important;
        transition: all 0.2s ease !important;
    }
    
    .gradio-button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    """


def _create_header() -> None:
    """Create application header."""
    with gr.Row():
        gr.Markdown("""
        <div class="civitai-header">
            <h1>🎨 Civitai Shortcut</h1>
            <p>AI Model Manager & Downloader - Standalone Edition</p>
            <p style="font-size: 0.9em; opacity: 0.8;">
                Browse, download, and manage AI models from Civitai
            </p>
        </div>
        """)


def _create_footer() -> None:
    """Create application footer."""
    with gr.Row():
        gr.Markdown("""
        <div class="footer">
            <p>
                <strong>Civitai Shortcut</strong> - Version 2.0.0<br>
                Standalone Mode |
                <a href="https://github.com/zixaphir/Stable-Diffusion-Webui-Civitai-Helper" target="_blank">
                    GitHub Repository
                </a>
            </p>
        </div>
        """)


def main() -> None:
    """Main entry for standalone launcher."""
    parser = argparse.ArgumentParser(description='Civitai Shortcut Standalone Launcher')
    parser.add_argument('--host', default='127.0.0.1', help='Server host')
    parser.add_argument('--port', type=int, default=7860, help='Server port')
    parser.add_argument('--share', action='store_true', help='Enable public share link')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    app = create_standalone_app()
    print(f'Starting Civitai Shortcut at http://{args.host}:{args.port}')
    app.launch(
        server_name=args.host,
        server_port=args.port,
        share=args.share,
        debug=args.debug,
        show_error=True,
        quiet=False,
    )


if __name__ == '__main__':
    main()
