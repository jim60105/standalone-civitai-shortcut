"""
IShortcut Actions Package

This package contains the refactored UI event handling modules split from
the original ishortcut_action.py file for better organization and maintainability.

Modules:
- event_handlers: Core event handling logic
- ui_controllers: UI state management and control
- gallery_handlers: Gallery-specific event handling
- download_handlers: Download-related event management
- search_handlers: Search and filter operations
- model_handlers: Model-specific actions and operations
"""

# Import main classes for convenience
from .event_handlers import EventHandlers
from .ui_controllers import UIControllers
from .gallery_handlers import GalleryHandlers
from .download_handlers import DownloadHandlers
from .search_handlers import SearchHandlers
from .model_handlers import ModelHandlers

__all__ = [
    'EventHandlers',
    'UIControllers',
    'GalleryHandlers',
    'DownloadHandlers',
    'SearchHandlers',
    'ModelHandlers',
]
