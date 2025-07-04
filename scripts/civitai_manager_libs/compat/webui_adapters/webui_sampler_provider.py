"""WebUI Sampler Provider.

Provides sampler information using AUTOMATIC1111 WebUI modules.
Compatible with the actual AUTOMATIC1111 implementation.
"""

from typing import List
from ..interfaces.isampler_provider import ISamplerProvider


class WebUISamplerProvider(ISamplerProvider):
    """
    Sampler provider implementation using WebUI modules.

    Provides sampler and upscaler information compatible with AUTOMATIC1111 WebUI.
    """

    def get_txt2img_samplers(self) -> List[str]:
        """
        Get list of samplers for txt2img from WebUI using visible_samplers().

        Returns:
            List[str]: List of sampler names for txt2img.
        """
        # In AUTOMATIC1111, txt2img uses the same visible samplers as img2img
        return self.get_samplers()

    """
    Sampler provider implementation using WebUI modules.

    Provides sampler and upscaler information compatible with AUTOMATIC1111 WebUI.
    """

    def get_samplers(self) -> List[str]:
        """Get list of available samplers from WebUI using visible_samplers()."""
        try:
            from modules.sd_samplers import visible_samplers

            visible = visible_samplers()
            return [x.name for x in visible] if visible else self._get_default_samplers()
        except (ImportError, AttributeError):
            # Fallback to older method
            try:
                from modules.sd_samplers import samplers

                return [x.name for x in samplers] if samplers else self._get_default_samplers()
            except (ImportError, AttributeError):
                return self._get_default_samplers()

    def get_samplers_for_img2img(self) -> List[str]:
        """Get list of samplers for img2img from WebUI using visible_samplers()."""
        try:
            from modules.sd_samplers import visible_samplers

            # In AUTOMATIC1111, samplers_for_img2img is set to all_samplers
            # so we use visible_samplers() which filters hidden ones
            visible = visible_samplers()
            return [x.name for x in visible] if visible else self._get_default_samplers()
        except (ImportError, AttributeError):
            # Fallback to older method
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
