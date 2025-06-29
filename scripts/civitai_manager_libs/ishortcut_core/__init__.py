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

__version__ = "1.0.0"
__all__ = [
    "ModelProcessor",
    "FileProcessor",
    "ImageProcessor",
    "MetadataProcessor",
    "DataValidator",
    "ModelFactory",
]
