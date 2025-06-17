"""
WebUI Sampler Provider

Provides sampler information using AUTOMATIC1111 WebUI modules.
"""

from typing import List
from ..interfaces.isampler_provider import ISamplerProvider


class WebUISamplerProvider(ISamplerProvider):
    """Sampler provider implementation using WebUI modules."""

    def get_samplers(self) -> List[str]:
        """Get list of available samplers from WebUI."""
        try:
            from modules.sd_samplers import samplers

            return [x.name for x in samplers] if samplers else self._get_default_samplers()
        except (ImportError, AttributeError):
            return self._get_default_samplers()

    def get_samplers_for_img2img(self) -> List[str]:
        """Get list of samplers for img2img from WebUI."""
        try:
            from modules.sd_samplers import samplers_for_img2img

            return (
                [x.name for x in samplers_for_img2img]
                if samplers_for_img2img
                else self._get_default_samplers()
            )
        except (ImportError, AttributeError):
            return self._get_default_samplers()

    def get_upscale_modes(self) -> List[str]:
        """Get upscale modes from WebUI."""
        try:
            from modules import shared

            if hasattr(shared, "latent_upscale_modes"):
                return list(shared.latent_upscale_modes)
        except (ImportError, AttributeError):
            pass

        return self._get_default_upscale_modes()

    def get_sd_upscalers(self) -> List[str]:
        """Get SD upscalers from WebUI."""
        try:
            from modules import shared

            if hasattr(shared, "sd_upscalers"):
                return [x.name for x in shared.sd_upscalers]
        except (ImportError, AttributeError):
            pass

        return self._get_default_sd_upscalers()

    def get_all_upscalers(self) -> List[str]:
        """Get combined list of all upscaler options."""
        upscale_modes = self.get_upscale_modes()
        sd_upscalers = self.get_sd_upscalers()
        return upscale_modes + sd_upscalers

    def is_sampler_available(self, sampler_name: str) -> bool:
        """Check if specific sampler is available."""
        available_samplers = self.get_samplers()
        return sampler_name in available_samplers

    def get_default_sampler(self) -> str:
        """Get default sampler name."""
        samplers = self.get_samplers()
        return samplers[0] if samplers else "Euler"

    def _get_default_samplers(self) -> List[str]:
        """Get default sampler list when WebUI is not available."""
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
        ]

    def _get_default_upscale_modes(self) -> List[str]:
        """Get default upscale modes."""
        return ["Linear", "Bilinear", "Bicubic", "Nearest", "Area", "Lanczos"]

    def _get_default_sd_upscalers(self) -> List[str]:
        """Get default SD upscalers."""
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
        ]
