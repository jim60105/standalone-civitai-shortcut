"""Metadata Processor Interface.

Provides unified access to image metadata processing across execution modes.
"""

from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional, Any, Union, Type

try:
    from PIL import Image

    ImageType: Type[Image.Image] = Image.Image
except ImportError:
    # Fallback type for systems without PIL
    ImageType = Any  # type: ignore[misc,assignment]


class IMetadataProcessor(ABC):
    """Abstract interface for metadata processing across different execution modes."""

    @abstractmethod
    def extract_png_info(
        self, image_input: Union[str, 'Image.Image']
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract metadata information from PNG files.

        This method replicates the behavior of modules.extras.run_pnginfo()
        which returns a tuple of (info1, generate_data, info3).

        Args:
            image_input (Union[str, Image.Image]): Path to the PNG image file or PIL Image object

        Returns:
            Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
                - info1: Basic info text
                - generate_data: Generation parameters as dictionary
                - info3: Additional info text.
        """
        pass

    @abstractmethod
    def extract_parameters_from_png(self, image_input: Union[str, 'Image.Image']) -> Optional[str]:
        """
        Extract generation parameters string from PNG metadata.

        Args:
            image_input (Union[str, Image.Image]): Path to the PNG image file or PIL Image object

        Returns:
            Optional[str]: Parameters string or None if not found.
        """
        pass

    @abstractmethod
    def parse_generation_parameters(self, parameters_text: str) -> Dict[str, Any]:
        """
        Parse generation parameters text into structured data.

        Args:
            parameters_text (str): Raw parameters text

        Returns:
            Dict[str, Any]: Parsed parameters as key-value pairs.
        """
        pass

    @abstractmethod
    def extract_prompt_from_parameters(self, parameters_text: str) -> Tuple[str, str]:
        """
        Extract positive and negative prompts from parameters text.

        Args:
            parameters_text (str): Raw parameters text

        Returns:
            Tuple[str, str]: (positive_prompt, negative_prompt)
        """
        pass

    @abstractmethod
    def format_parameters_for_display(self, parameters: Dict[str, Any]) -> str:
        """
        Format parameters dictionary for display purposes.

        Args:
            parameters (Dict[str, Any]): Parameters dictionary

        Returns:
            str: Formatted parameters string.
        """
        pass
