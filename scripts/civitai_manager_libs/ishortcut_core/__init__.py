"""
ishortcut_core: Modularized core functionality for ishortcut module.

This package provides a clean separation of concerns for the ishortcut functionality:
- model_processor: Model information handling and API interactions
- file_processor: File operations and directory management
- image_processor: Image downloading and thumbnail generation
- metadata_processor: Data validation and metadata handling
- data_validator: Input validation and data consistency checks
- model_factory: Model creation and shortcut generation

Each module focuses on a single responsibility to improve maintainability
and testability of the codebase.
"""

# Public API exports - Will be enabled as modules are created
from .model_processor import ModelProcessor
from .file_processor import FileProcessor

# Import the ImageProcessor class
from .image_processor import ImageProcessor

# Import the MetadataProcessor class
from .metadata_processor import MetadataProcessor

# Import the DataValidator class
from .data_validator import DataValidator

# Import the ModelFactory class
from .model_factory import ModelFactory
from .shortcut_collection_manager import ShortcutCollectionManager
from .shortcut_search_filter import ShortcutSearchFilter
from .preview_image_manager import PreviewImageManager

# Create global instances for backward compatibility
_collection_manager = None
_model_processor = None
_search_filter = None
_image_processor = None


def _initialize_globals():
    """Initialize global instances for backward compatibility."""
    global _collection_manager, _model_processor, _search_filter, _image_processor

    if _collection_manager is None:
        _collection_manager = ShortcutCollectionManager()

    if _model_processor is None:
        _model_processor = ModelProcessor()

    if _search_filter is None:
        _search_filter = ShortcutSearchFilter(_collection_manager, _model_processor)

    if _image_processor is None:
        _image_processor = ImageProcessor()


# Initialize globals on import
_initialize_globals()

# Global instances for backward compatibility
shortcutsearchfilter = _search_filter
imageprocessor = _image_processor
modelprocessor = _model_processor
shortcutcollectionmanager = _collection_manager

__version__ = "1.0.0"
__all__ = [
    # Core classes that are directly imported
    "ModelProcessor",
    "FileProcessor",
    "ImageProcessor",
    "MetadataProcessor",
    "DataValidator",
    "ModelFactory",
    "ShortcutCollectionManager",
    "ShortcutSearchFilter",
    "PreviewImageManager",
    # Global instances for backward compatibility
    "shortcutsearchfilter",
    "imageprocessor",
    "modelprocessor",
    "shortcutcollectionmanager",
]
