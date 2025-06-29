"""
IShortcut Core Module Package

This package contains the refactored core business logic modules split from the
original ishortcut.py file for better maintainability and testability.

Modules:
- model_processor: Model processing core logic
- file_processor: File processing logic
- image_processor: Image processing logic
- metadata_processor: Metadata processing logic
- data_validator: Data validation logic
- model_factory: Model factory classes
"""

# Import main classes for convenience
from .model_processor import ModelProcessor
from .file_processor import FileProcessor
from .image_processor import ImageProcessor
from .metadata_processor import MetadataProcessor
from .data_validator import DataValidator
from .model_factory import ModelFactory

__all__ = [
    'ModelProcessor',
    'FileProcessor',
    'ImageProcessor',
    'MetadataProcessor',
    'DataValidator',
    'ModelFactory',
]
