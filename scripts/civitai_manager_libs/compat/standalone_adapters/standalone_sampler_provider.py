"""
Standalone Sampler Provider

Provides comprehensive sampler information for standalone execution without WebUI dependencies.
Enhanced with full sampler compatibility matching AUTOMATIC1111 WebUI implementation.
"""

import json
import os
from typing import List, Dict, Optional, Any
from ..interfaces.isampler_provider import ISamplerProvider


class StandaloneSamplerProvider(ISamplerProvider):
    """
    Enhanced sampler provider implementation for standalone mode.

    Provides comprehensive sampler information including:
    - Complete sampler list matching AUTOMATIC1111 WebUI
    - Upscaler information
    - Configuration management
    - Validation and compatibility checking
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the standalone sampler provider.

        Args:
            config_path: Optional path to custom sampler configuration
        """
        self._config_path = config_path
        self._samplers_data = self._load_samplers_config()
        self._debug_mode = False

    def get_samplers(self) -> List[str]:
        """Get list of available samplers including scheduler combinations."""
        base_samplers = [sampler["name"] for sampler in self._samplers_data["samplers"]]

        # Add common scheduler combinations to match AUTOMATIC1111 behavior
        scheduler_combinations = []

        for sampler_data in self._samplers_data["samplers"]:
            sampler_name = sampler_data["name"]
            # Add common combinations like "DPM++ 2M Karras"
            if "dpm" in sampler_name.lower() and "karras" in sampler_data.get("categories", []):
                if "Karras" not in sampler_name:
                    scheduler_combinations.append(f"{sampler_name} Karras")

        return base_samplers + scheduler_combinations

    def get_samplers_for_img2img(self) -> List[str]:
        """
        Get list of samplers for img2img.

        Some samplers may not be suitable for img2img, so we filter them.
        """
        img2img_compatible = []
        for sampler in self._samplers_data["samplers"]:
            if sampler.get("img2img_compatible", True):  # Default to True
                img2img_compatible.append(sampler["name"])

        # Add scheduler combinations for img2img compatible samplers
        scheduler_combinations = []
        for sampler_data in self._samplers_data["samplers"]:
            if not sampler_data.get("img2img_compatible", True):
                continue
            sampler_name = sampler_data["name"]
            # Add common combinations like "DPM++ 2M Karras"
            if "dpm" in sampler_name.lower() and "karras" in sampler_data.get("categories", []):
                if "Karras" not in sampler_name:
                    scheduler_combinations.append(f"{sampler_name} Karras")

        return img2img_compatible + scheduler_combinations

    def get_upscale_modes(self) -> List[str]:
        """Get list of available upscale modes."""
        return self._samplers_data["upscale_modes"].copy()

    def get_sd_upscalers(self) -> List[str]:
        """Get list of available SD upscalers."""
        return self._samplers_data["sd_upscalers"].copy()

    def get_all_upscalers(self) -> List[str]:
        """Get combined list of all upscaler options."""
        return self._samplers_data["upscale_modes"] + self._samplers_data["sd_upscalers"]

    def is_sampler_available(self, sampler_name: str) -> bool:
        """Check if specific sampler is available."""
        # Check base sampler names (case-insensitive)
        sampler_names = [s["name"].lower() for s in self._samplers_data["samplers"]]
        sampler_aliases = []
        for sampler in self._samplers_data["samplers"]:
            aliases = sampler.get("aliases", [])
            sampler_aliases.extend([alias.lower() for alias in aliases])

        # Check against base names and aliases
        if sampler_name.lower() in sampler_names or sampler_name.lower() in sampler_aliases:
            return True

        # Check against scheduler combinations
        all_samplers = self.get_samplers()
        return sampler_name in all_samplers

    def get_default_sampler(self) -> str:
        """Get default sampler name."""
        for sampler in self._samplers_data["samplers"]:
            if sampler.get("default", False):
                return sampler["name"]

        # Fallback to first sampler
        return (
            self._samplers_data["samplers"][0]["name"]
            if self._samplers_data["samplers"]
            else "Euler"
        )

    def get_sampler_info(self, sampler_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific sampler.

        Args:
            sampler_name: Name or alias of the sampler

        Returns:
            Dictionary with sampler information or None if not found
        """
        for sampler in self._samplers_data["samplers"]:
            # Check name (case-insensitive)
            if sampler["name"].lower() == sampler_name.lower():
                return sampler.copy()
            # Check aliases (case-insensitive)
            aliases = sampler.get("aliases", [])
            if any(alias.lower() == sampler_name.lower() for alias in aliases):
                return sampler.copy()

        return None

    def get_sampler_aliases(self, sampler_name: str) -> List[str]:
        """
        Get aliases for a specific sampler.

        Args:
            sampler_name: Name of the sampler

        Returns:
            List of aliases for the sampler
        """
        sampler_info = self.get_sampler_info(sampler_name)
        return sampler_info.get("aliases", []) if sampler_info else []

    def validate_sampler(self, sampler_name: str) -> bool:
        """
        Validate if sampler name is correct and available.

        Args:
            sampler_name: Name of the sampler to validate

        Returns:
            True if sampler is valid and available
        """
        return self.is_sampler_available(sampler_name)

    def normalize_sampler_name(self, sampler_name: str) -> str:
        """
        Normalize sampler name to standard form.

        Args:
            sampler_name: Input sampler name (may be an alias)

        Returns:
            Normalized sampler name
        """
        # Handle scheduler combinations first
        if " " in sampler_name:
            parts = sampler_name.split()
            if len(parts) >= 2:
                base_name = " ".join(parts[:-1])
                sampler_info = self.get_sampler_info(base_name)
                if sampler_info:
                    return sampler_name  # Return the full combined name

        # Handle base samplers and aliases
        sampler_info = self.get_sampler_info(sampler_name)
        return sampler_info["name"] if sampler_info else sampler_name

    def get_samplers_by_category(self, category: str = None) -> List[str]:
        """
        Get samplers filtered by category.

        Args:
            category: Category to filter by (e.g., 'ancestral', 'karras', 'dpm')

        Returns:
            List of sampler names in the specified category
        """
        if not category:
            return self.get_samplers()

        filtered_samplers = []
        for sampler in self._samplers_data["samplers"]:
            if category.lower() in sampler.get("categories", []):
                filtered_samplers.append(sampler["name"])

        return filtered_samplers

    def _load_samplers_config(self) -> Dict[str, Any]:
        """Load sampler configuration from file or use defaults."""
        if self._config_path and os.path.exists(self._config_path):
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self._log_debug(f"Error loading sampler config: {e}")

        return self._get_default_samplers_config()

    def _get_default_samplers_config(self) -> Dict[str, Any]:
        """Get comprehensive default sampler configuration matching AUTOMATIC1111."""
        return {
            "samplers": [
                # K-Diffusion samplers (from sd_samplers_kdiffusion.py)
                {
                    "name": "DPM++ 2M",
                    "aliases": ["k_dpmpp_2m", "dpmpp_2m_karras"],
                    "categories": ["dpm", "karras"],
                    "img2img_compatible": True,
                    "description": "DPM++ solver, 2M with Karras scheduler",
                },
                {
                    "name": "DPM++ SDE",
                    "aliases": ["k_dpmpp_sde"],
                    "categories": ["dpm", "karras", "sde", "brownian_noise"],
                    "img2img_compatible": True,
                    "description": "DPM++ solver, SDE with Karras scheduler",
                },
                {
                    "name": "DPM++ 2M SDE",
                    "aliases": ["k_dpmpp_2m_sde"],
                    "categories": ["dpm", "exponential", "brownian_noise"],
                    "img2img_compatible": True,
                    "description": "DPM++ solver, 2M SDE with exponential scheduler",
                },
                {
                    "name": "DPM++ 2M SDE Heun",
                    "aliases": ["k_dpmpp_2m_sde_heun"],
                    "categories": ["dpm", "exponential", "brownian_noise", "heun"],
                    "img2img_compatible": True,
                    "description": "DPM++ solver, 2M SDE Heun with exponential scheduler",
                },
                {
                    "name": "DPM++ 2S a",
                    "aliases": ["k_dpmpp_2s_a"],
                    "categories": ["dpm", "karras", "ancestral"],
                    "img2img_compatible": True,
                    "description": "DPM++ solver, 2S ancestral with Karras scheduler",
                },
                {
                    "name": "DPM++ 3M SDE",
                    "aliases": ["k_dpmpp_3m_sde"],
                    "categories": [
                        "dpm",
                        "exponential",
                        "brownian_noise",
                        "discard_next_to_last_sigma",
                    ],
                    "img2img_compatible": True,
                    "description": "DPM++ solver, 3M SDE with exponential scheduler",
                },
                {
                    "name": "Euler a",
                    "aliases": ["k_euler_a", "k_euler_ancestral"],
                    "categories": ["ancestral", "basic"],
                    "img2img_compatible": True,
                    "description": "Euler ancestral sampler",
                },
                {
                    "name": "Euler",
                    "aliases": ["k_euler"],
                    "categories": ["basic"],
                    "img2img_compatible": True,
                    "default": True,
                    "description": "Basic Euler method sampler",
                },
                {
                    "name": "LMS",
                    "aliases": ["k_lms"],
                    "categories": ["basic"],
                    "img2img_compatible": True,
                    "description": "Linear multistep sampler",
                },
                {
                    "name": "Heun",
                    "aliases": ["k_heun"],
                    "categories": ["basic", "second_order"],
                    "img2img_compatible": True,
                    "description": "Heun's method sampler",
                },
                {
                    "name": "DPM2",
                    "aliases": ["k_dpm_2"],
                    "categories": ["dpm", "karras", "discard_next_to_last_sigma", "second_order"],
                    "img2img_compatible": True,
                    "description": "DPM solver, 2nd order",
                },
                {
                    "name": "DPM2 a",
                    "aliases": ["k_dpm_2_a"],
                    "categories": [
                        "dpm",
                        "karras",
                        "discard_next_to_last_sigma",
                        "ancestral",
                        "second_order",
                    ],
                    "img2img_compatible": True,
                    "description": "DPM solver, 2nd order, ancestral",
                },
                {
                    "name": "DPM fast",
                    "aliases": ["k_dpm_fast"],
                    "categories": ["dpm", "fast", "ancestral"],
                    "img2img_compatible": True,
                    "description": "DPM solver, fast variant",
                },
                {
                    "name": "DPM adaptive",
                    "aliases": ["k_dpm_ad"],
                    "categories": ["dpm", "adaptive", "ancestral"],
                    "img2img_compatible": True,
                    "description": "DPM solver, adaptive",
                },
                {
                    "name": "Restart",
                    "aliases": ["restart"],
                    "categories": ["karras", "second_order", "advanced"],
                    "img2img_compatible": True,
                    "description": "Restart sampler for improving generative processes",
                },
                # Timesteps samplers (from sd_samplers_timesteps.py)
                {
                    "name": "DDIM",
                    "aliases": ["ddim"],
                    "categories": ["timesteps"],
                    "img2img_compatible": True,
                    "description": "Denoising Diffusion Implicit Models",
                },
                {
                    "name": "DDIM CFG++",
                    "aliases": ["ddim_cfgpp"],
                    "categories": ["timesteps", "cfg_plus_plus"],
                    "img2img_compatible": True,
                    "description": "DDIM with CFG++ enhancement",
                },
                {
                    "name": "PLMS",
                    "aliases": ["plms"],
                    "categories": ["timesteps"],
                    "img2img_compatible": True,
                    "description": "Pseudo Linear Multi-Step",
                },
                {
                    "name": "UniPC",
                    "aliases": ["unipc"],
                    "categories": ["timesteps", "advanced"],
                    "img2img_compatible": True,
                    "description": "Unified Predictor-Corrector",
                },
                # LCM samplers (from sd_samplers_lcm.py)
                {
                    "name": "LCM",
                    "aliases": ["k_lcm"],
                    "categories": ["lcm", "fast"],
                    "img2img_compatible": True,
                    "description": "Latent Consistency Model sampler",
                },
            ],
            "upscale_modes": [
                "Linear",
                "Bilinear",
                "Bicubic",
                "Nearest",
                "Area",
                "Lanczos",
            ],
            "sd_upscalers": [
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
                "RealESRGAN_x4plus_anime_6B",
            ],
        }

    def _log_debug(self, message: str):
        """Log debug message if debug mode is enabled."""
        if self._debug_mode:
            print(f"StandaloneSamplerProvider: {message}")

    def set_debug_mode(self, enabled: bool):
        """Enable or disable debug mode."""
        self._debug_mode = enabled
