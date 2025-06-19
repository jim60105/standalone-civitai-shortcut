"""Sampler Provider Interface.

Provides unified access to sampler information across execution modes.
"""

from abc import ABC, abstractmethod
from typing import List


class ISamplerProvider(ABC):
    """Abstract interface for sampler information across different execution modes."""

    @abstractmethod
    def get_samplers(self) -> List[str]:
        """
        Get list of available samplers.

        Returns:
            List[str]: List of sampler names.
        """
        pass

    @abstractmethod
    def get_samplers_for_img2img(self) -> List[str]:
        """
        Get list of samplers available for img2img.

        Returns:
            List[str]: List of sampler names for img2img.
        """
        pass

    @abstractmethod
    def get_upscale_modes(self) -> List[str]:
        """
        Get list of available upscale modes.

        Returns:
            List[str]: List of upscale mode names.
        """
        pass

    @abstractmethod
    def get_sd_upscalers(self) -> List[str]:
        """
        Get list of available SD upscalers.

        Returns:
            List[str]: List of SD upscaler names.
        """
        pass

    @abstractmethod
    def get_all_upscalers(self) -> List[str]:
        """
        Get combined list of all upscaler options.

        Returns:
            List[str]: Combined list of upscale modes and SD upscalers.
        """
        pass

    @abstractmethod
    def is_sampler_available(self, sampler_name: str) -> bool:
        """
        Check if a specific sampler is available.

        Args:
            sampler_name (str): Name of the sampler to check

        Returns:
            bool: True if sampler is available.
        """
        pass

    @abstractmethod
    def get_default_sampler(self) -> str:
        """
        Get the default sampler name.

        Returns:
            str: Default sampler name.
        """
        pass
