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

    with gr.Blocks(
        title='Civitai Shortcut - Standalone Version',
        theme=gr.themes.Default(),
    ) as app:
        gr.Markdown('# Civitai Shortcut')
        gr.Markdown('Standalone version - Model management and downloader')
        civitai_shortcut_ui()
    return app


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
