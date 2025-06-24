#!/usr/bin/env python3
"""
Civitai Shortcut Standalone Mode Main Application

This application provides standalone execution capability for Civitai Shortcut,
without requiring the AUTOMATIC1111 WebUI environment.
"""

import sys
import os
import argparse
import logging
from typing import Optional
import signal

# Ensure we can find project modules
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'scripts'))

os.environ.setdefault('GRADIO_ANALYTICS_ENABLED', 'False')


class CivitaiShortcutApp:
    """Civitai Shortcut standalone application"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the application.

        Args:
            config_path (Optional[str]): Path to custom configuration file
        """
        self.config_path = config_path
        self.app = None
        self.compat_layer = None
        self._setup_logging()
        self._initialize_components()

    def _setup_logging(self):
        """Setup logging system"""
        log_dir = os.path.join(project_root, 'logs')
        os.makedirs(log_dir, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'civitai_shortcut.log')),
                logging.StreamHandler(sys.stdout),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def _initialize_components(self):
        """Initialize core components"""
        try:
            # Import after path setup
            from scripts.civitai_manager_libs.compat.compat_layer import CompatibilityLayer

            # Force standalone mode
            self.compat_layer = CompatibilityLayer(mode='standalone')

            # Initialize configuration
            self._setup_config()

            self.logger.info("Civitai Shortcut initialized in standalone mode")

        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise

    def _setup_config(self):
        """Setup application configuration"""
        try:
            if self.config_path and os.path.exists(self.config_path):
                self.compat_layer.config_manager.load_config(self.config_path)

            # Ensure necessary directories exist
            self.compat_layer.path_manager.ensure_directories()

        except Exception as e:
            self.logger.error(f"Failed to setup configuration: {e}")
            raise

    def create_interface(self):
        """Create Gradio user interface"""
        try:
            import gradio as gr

            # Import UI creation function
            from ui_adapter import create_civitai_shortcut_ui

            # Load custom CSS if exists
            css_path = os.path.join(project_root, "style.css")
            css = None
            if os.path.exists(css_path):
                with open(css_path, 'r', encoding='utf-8') as f:
                    css = f.read()

            with gr.Blocks(
                title="Civitai Shortcut - Standalone",
                css=css,
            ) as app:
                # Create main UI
                create_civitai_shortcut_ui(self.compat_layer)

            self.app = app
            return app

        except Exception as e:
            self.logger.error(f"Failed to create interface: {e}")
            raise

    def launch(
        self,
        host: str = "0.0.0.0",
        port: int = 7860,
        share: bool = False,
        debug: bool = False,
        **kwargs,
    ):
        """
        Launch the application.

        Args:
            host (str): Server host address
            port (int): Server port
            share (bool): Create Gradio share link
            debug (bool): Enable debug mode
            **kwargs: Additional arguments for Gradio launch
        """
        if not self.app:
            self.create_interface()

        self.logger.info(f"Starting Civitai Shortcut on {host}:{port}")

        if share:
            self.logger.info("Share link will be created")

        try:
            # Setup signal handlers for graceful shutdown
            def signal_handler(signum, frame):
                self.logger.info("Received shutdown signal, stopping application...")
                sys.exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            # Configure queue with optimized settings for long-running tasks
            self.app.queue(
                max_size=64,
                status_update_rate="auto",
                api_open=False,
            )

            # Launch the application
            self.app.launch(
                server_name=host,
                server_port=port,
                share=share,
                debug=debug,
                show_error=debug,
                ssl_verify=False,
                quiet=False,
                **kwargs,
            )

        except KeyboardInterrupt:
            self.logger.info("Application stopped by user")
        except Exception as e:
            self.logger.error(f"Error starting application: {e}")
            raise


def create_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Civitai Shortcut - Standalone Mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Start with default settings
  python main.py --port 8080              # Start on port 8080
  python main.py --host 0.0.0.0 --share   # Allow external access and create share link
  python main.py --config my_config.json  # Use custom config file
  python main.py --debug                  # Enable debug mode
        """,
    )

    # Basic options
    parser.add_argument('--host', default='0.0.0.0', help='Server host address (default: 0.0.0.0)')

    parser.add_argument('--port', type=int, default=7860, help='Server port (default: 7860)')

    parser.add_argument('--share', action='store_true', help='Create Gradio public share link')

    # Configuration options
    parser.add_argument('--config', type=str, help='Custom configuration file path')

    parser.add_argument('--models-path', type=str, help='Models storage path')

    parser.add_argument('--output-path', type=str, help='Output files storage path')

    # Debug and development options
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    parser.add_argument(
        '--reload', action='store_true', help='Enable auto-reload (development only)'
    )

    parser.add_argument('--quiet', action='store_true', help='Quiet mode, reduce output')

    # Version information
    parser.add_argument(
        '--version', action='version', version='Civitai Shortcut 2.0.0 (Standalone)'
    )

    return parser


def apply_cli_overrides(app: CivitaiShortcutApp, args: argparse.Namespace):
    """
    Apply command line arguments to application configuration.

    Args:
        app (CivitaiShortcutApp): Application instance
        args (argparse.Namespace): Parsed command line arguments
    """
    config_manager = app.compat_layer.config_manager

    # Path settings
    if args.models_path:
        config_manager.set('paths.models', args.models_path)

    if args.output_path:
        config_manager.set('paths.output', args.output_path)

    # Debug settings
    if args.debug:
        config_manager.set('debug.enabled', True)
        logging.getLogger().setLevel(logging.DEBUG)
        app.logger.info("Debug mode enabled")

    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    # Server settings
    config_manager.set('server.host', args.host)
    config_manager.set('server.port', args.port)
    config_manager.set('server.share', args.share)


def main():
    """Main application entry point"""
    try:
        # Parse command line arguments
        parser = create_argument_parser()
        args = parser.parse_args()

        # Create application instance
        print("Initializing Civitai Shortcut...")
        app = CivitaiShortcutApp(config_path=args.config)

        # Apply command line overrides
        apply_cli_overrides(app, args)

        # Create interface
        print("Creating user interface...")
        app.create_interface()

        # Launch application
        print(f"Launching application on {args.host}:{args.port}...")
        app.launch(host=args.host, port=args.port, share=args.share, debug=args.debug)

    except KeyboardInterrupt:
        print("\nApplication stopped")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        if '--debug' in sys.argv:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
