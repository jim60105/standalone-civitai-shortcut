"""
Standalone Sampler Provider

Provides sampler information for standalone execution without WebUI dependencies.
"""

from typing import List
from ..interfaces.isampler_provider import ISamplerProvider


class StandaloneSamplerProvider(ISamplerProvider):
    """Sampler provider implementation for standalone mode."""
    
    def __init__(self):
        """Initialize the standalone sampler provider."""
        self._samplers = self._get_default_samplers()
        self._upscale_modes = self._get_default_upscale_modes()
        self._sd_upscalers = self._get_default_sd_upscalers()
    
    def get_samplers(self) -> List[str]:
        """Get list of available samplers."""
        return self._samplers.copy()
    
    def get_samplers_for_img2img(self) -> List[str]:
        """Get list of samplers for img2img (same as regular samplers in standalone)."""
        return self._samplers.copy()
    
    def get_upscale_modes(self) -> List[str]:
        """Get list of available upscale modes."""
        return self._upscale_modes.copy()
    
    def get_sd_upscalers(self) -> List[str]:
        """Get list of available SD upscalers."""
        return self._sd_upscalers.copy()
    
    def get_all_upscalers(self) -> List[str]:
        """Get combined list of all upscaler options."""
        return self._upscale_modes + self._sd_upscalers
    
    def is_sampler_available(self, sampler_name: str) -> bool:
        """Check if specific sampler is available."""
        return sampler_name in self._samplers
    
    def get_default_sampler(self) -> str:
        """Get default sampler name."""
        return self._samplers[0] if self._samplers else "Euler"
    
    def _get_default_samplers(self) -> List[str]:
        """Get comprehensive list of known samplers."""
        return [
            "Euler",
            "Euler a", 
            "LMS",
            "Heun",
            "DPM2",
            "DPM2 a",
            "DPM++ 2S a",
            "DPM++ 2M",
            "DPM++ SDE",
            "DPM fast",
            "DPM adaptive",
            "LMS Karras",
            "DPM2 Karras", 
            "DPM2 a Karras",
            "DPM++ 2S a Karras",
            "DPM++ 2M Karras",
            "DPM++ SDE Karras",
            "DDIM",
            "PLMS",
            "UniPC",
            "DEIS",
            "DPM++ 3M SDE",
            "DPM++ 3M SDE Karras",
            "Restart"
        ]
    
    def _get_default_upscale_modes(self) -> List[str]:
        """Get list of basic upscale modes."""
        return [
            "Linear",
            "Bilinear", 
            "Bicubic",
            "Nearest",
            "Area",
            "Lanczos"
        ]
    
    def _get_default_sd_upscalers(self) -> List[str]:
        """Get list of known SD upscalers."""
        return [
            "None",
            "Lanczos",
            "Nearest", 
            "LDSR",
            "BSRGAN",
            "ESRGAN_4x",
            "R-ESRGAN 4x+",
            "R-ESRGAN 4x+ Anime6B",
            "ScuNET GAN",
            "ScuNET PSNR", 
            "SwinIR 4x",
            "4x-UltraSharp",
            "4x-AnimeSharp",
            "RealESRGAN_x4plus",
            "RealESRGAN_x4plus_anime_6B"
        ]
