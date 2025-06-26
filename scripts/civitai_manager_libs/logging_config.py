import logging
import os
from typing import Optional
from .compat.environment_detector import EnvironmentDetector

try:
    from tqdm import tqdm

    class TqdmLoggingHandler(logging.Handler):
        def __init__(self, fallback_handler: logging.Handler):
            super().__init__()
            self.fallback_handler = fallback_handler

        def emit(self, record):
            try:
                if tqdm._instances:
                    tqdm.write(self.format(record))
                else:
                    self.fallback_handler.emit(record)
            except Exception:
                self.fallback_handler.emit(record)

except ImportError:
    TqdmLoggingHandler = None


def setup_logging_for_standalone(loglevel: Optional[str] = None, log_file: Optional[str] = None):
    """
    Setup logging for standalone mode, compatible with SD WebUI format.
    Only call this in standalone mode.
    Always enables rich logging in standalone mode.
    """
    if logging.root.handlers:
        return

    if loglevel is None:
        loglevel = os.environ.get("SD_WEBUI_LOG_LEVEL")

    if not loglevel:
        loglevel = "INFO"

    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s [%(name)s] %(message)s',
        '%Y-%m-%d %H:%M:%S',
    )

    try:
        from rich.logging import RichHandler

        handler = RichHandler()
    except ImportError:
        handler = logging.StreamHandler()

    if TqdmLoggingHandler:
        handler = TqdmLoggingHandler(handler)

    handler.setFormatter(formatter)

    handlers = [handler]
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        if TqdmLoggingHandler:
            file_handler = TqdmLoggingHandler(file_handler)
        handlers.append(file_handler)

    log_level = getattr(logging, loglevel.upper(), None) or logging.INFO
    logging.root.setLevel(log_level)
    for h in handlers:
        logging.root.addHandler(h)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance. Works in both WebUI and standalone modes.
    """
    env_detector = EnvironmentDetector()
    # Use is_standalone_mode to check standalone execution environment
    if env_detector.is_standalone_mode():
        setup_logging_for_standalone()
    return logging.getLogger(name)
