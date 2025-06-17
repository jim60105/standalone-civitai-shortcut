"""
Standalone Sampler Provider

Provides comprehensive sampler information for standalone execution without WebUI dependencies.
Enhanced with full sampler compatibility and configuration management.
"""

import json
import os
from typing import List, Dict, Optional, Any
from ..interfaces.isampler_provider import ISamplerProvider


class StandaloneSamplerProvider(ISamplerProvider):
    """
    Enhanced sampler provider implementation for standalone mode.
    
    Provides comprehensive sampler information including:
    - Complete sampler list with aliases
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
        """Get list of available samplers."""
        return [sampler['name'] for sampler in self._samplers_data['samplers']]
    
    def get_samplers_for_img2img(self) -> List[str]:
        """
        Get list of samplers for img2img.
        
        Some samplers may not be suitable for img2img, so we filter them.
        """
        img2img_compatible = []
        for sampler in self._samplers_data['samplers']:
            if sampler.get('img2img_compatible', True):  # Default to True
                img2img_compatible.append(sampler['name'])
        
        return img2img_compatible
    
    def get_upscale_modes(self) -> List[str]:
        """Get list of available upscale modes."""
        return self._samplers_data['upscale_modes'].copy()
    
    def get_sd_upscalers(self) -> List[str]:
        """Get list of available SD upscalers."""
        return self._samplers_data['sd_upscalers'].copy()
    
    def get_all_upscalers(self) -> List[str]:
        """Get combined list of all upscaler options."""
        return self._samplers_data['upscale_modes'] + self._samplers_data['sd_upscalers']
    
    def is_sampler_available(self, sampler_name: str) -> bool:
        """Check if specific sampler is available."""
        sampler_names = [s['name'] for s in self._samplers_data['samplers']]
        sampler_aliases = []
        for sampler in self._samplers_data['samplers']:
            sampler_aliases.extend(sampler.get('aliases', []))
        
        return sampler_name in sampler_names or sampler_name in sampler_aliases
    
    def get_default_sampler(self) -> str:
        """Get default sampler name."""
        for sampler in self._samplers_data['samplers']:
            if sampler.get('default', False):
                return sampler['name']
        
        # Fallback to first sampler
        return self._samplers_data['samplers'][0]['name'] if self._samplers_data['samplers'] else "Euler"
    
    def get_sampler_info(self, sampler_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific sampler.
        
        Args:
            sampler_name: Name or alias of the sampler
            
        Returns:
            Dictionary with sampler information or None if not found
        """
        for sampler in self._samplers_data['samplers']:
            if (sampler['name'] == sampler_name or 
                sampler_name in sampler.get('aliases', [])):
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
        return sampler_info.get('aliases', []) if sampler_info else []
    
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
        sampler_info = self.get_sampler_info(sampler_name)
        return sampler_info['name'] if sampler_info else sampler_name
    
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
        for sampler in self._samplers_data['samplers']:
            if category.lower() in sampler.get('categories', []):
                filtered_samplers.append(sampler['name'])
        
        return filtered_samplers
    
    def _load_samplers_config(self) -> Dict[str, Any]:
        """Load sampler configuration from file or use defaults."""
        if self._config_path and os.path.exists(self._config_path):
            try:
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self._log_debug(f"Error loading sampler config: {e}")
        
        return self._get_default_samplers_config()
    
    def _get_default_samplers_config(self) -> Dict[str, Any]:
        """Get comprehensive default sampler configuration."""
        return {
            "samplers": [
                {
                    "name": "Euler",
                    "aliases": ["euler"],
                    "categories": ["basic"],
                    "img2img_compatible": True,
                    "default": True,
                    "description": "Basic Euler method sampler"
                },
                {
                    "name": "Euler a",
                    "aliases": ["euler_a", "euler_ancestral"],
                    "categories": ["ancestral", "basic"],
                    "img2img_compatible": True,
                    "description": "Euler ancestral sampler"
                },
                {
                    "name": "LMS",
                    "aliases": ["lms"],
                    "categories": ["basic"],
                    "img2img_compatible": True,
                    "description": "Linear multistep sampler"
                },
                {
                    "name": "Heun",
                    "aliases": ["heun"],
                    "categories": ["basic"],
                    "img2img_compatible": True,
                    "description": "Heun's method sampler"
                },
                {
                    "name": "DPM2",
                    "aliases": ["dpm2"],
                    "categories": ["dpm"],
                    "img2img_compatible": True,
                    "description": "DPM solver, 2nd order"
                },
                {
                    "name": "DPM2 a",
                    "aliases": ["dpm2_a", "dpm2_ancestral"],
                    "categories": ["dpm", "ancestral"],
                    "img2img_compatible": True,
                    "description": "DPM solver, 2nd order, ancestral"
                },
                {
                    "name": "DPM++ 2S a",
                    "aliases": ["dpm_plus_plus_2s_a", "dpmpp_2s_a"],
                    "categories": ["dpm", "ancestral"],
                    "img2img_compatible": True,
                    "description": "DPM++ solver, 2S, ancestral"
                },
                {
                    "name": "DPM++ 2M",
                    "aliases": ["dpm_plus_plus_2m", "dpmpp_2m"],
                    "categories": ["dpm"],
                    "img2img_compatible": True,
                    "description": "DPM++ solver, 2M"
                },
                {
                    "name": "DPM++ SDE",
                    "aliases": ["dpm_plus_plus_sde", "dpmpp_sde"],
                    "categories": ["dpm", "sde"],
                    "img2img_compatible": True,
                    "description": "DPM++ solver, SDE"
                },
                {
                    "name": "DPM fast",
                    "aliases": ["dpm_fast"],
                    "categories": ["dpm", "fast"],
                    "img2img_compatible": True,
                    "description": "DPM solver, fast variant"
                },
                {
                    "name": "DPM adaptive",
                    "aliases": ["dpm_adaptive"],
                    "categories": ["dpm", "adaptive"],
                    "img2img_compatible": True,
                    "description": "DPM solver, adaptive"
                },
                {
                    "name": "LMS Karras",
                    "aliases": ["lms_karras"],
                    "categories": ["karras", "basic"],
                    "img2img_compatible": True,
                    "description": "LMS with Karras noise schedule"
                },
                {
                    "name": "DPM2 Karras",
                    "aliases": ["dpm2_karras"],
                    "categories": ["dpm", "karras"],
                    "img2img_compatible": True,
                    "description": "DPM2 with Karras noise schedule"
                },
                {
                    "name": "DPM2 a Karras",
                    "aliases": ["dpm2_a_karras"],
                    "categories": ["dpm", "karras", "ancestral"],
                    "img2img_compatible": True,
                    "description": "DPM2 ancestral with Karras noise schedule"
                },
                {
                    "name": "DPM++ 2S a Karras",
                    "aliases": ["dpm_plus_plus_2s_a_karras", "dpmpp_2s_a_karras"],
                    "categories": ["dpm", "karras", "ancestral"],
                    "img2img_compatible": True,
                    "description": "DPM++ 2S ancestral with Karras noise schedule"
                },
                {
                    "name": "DPM++ 2M Karras",
                    "aliases": ["dpm_plus_plus_2m_karras", "dpmpp_2m_karras"],
                    "categories": ["dpm", "karras"],
                    "img2img_compatible": True,
                    "description": "DPM++ 2M with Karras noise schedule"
                },
                {
                    "name": "DPM++ SDE Karras",
                    "aliases": ["dpm_plus_plus_sde_karras", "dpmpp_sde_karras"],
                    "categories": ["dpm", "karras", "sde"],
                    "img2img_compatible": True,
                    "description": "DPM++ SDE with Karras noise schedule"
                },
                {
                    "name": "DDIM",
                    "aliases": ["ddim"],
                    "categories": ["basic"],
                    "img2img_compatible": True,
                    "description": "Denoising Diffusion Implicit Models"
                },
                {
                    "name": "PLMS",
                    "aliases": ["plms"],
                    "categories": ["basic"],
                    "img2img_compatible": True,
                    "description": "Pseudo Linear Multi-Step"
                },
                {
                    "name": "UniPC",
                    "aliases": ["unipc"],
                    "categories": ["advanced"],
                    "img2img_compatible": True,
                    "description": "Unified Predictor-Corrector"
                },
                {
                    "name": "DEIS",
                    "aliases": ["deis"],
                    "categories": ["advanced"],
                    "img2img_compatible": True,
                    "description": "Diffusion Exponential Integrator Sampler"
                },
                {
                    "name": "DPM++ 3M SDE",
                    "aliases": ["dpm_plus_plus_3m_sde", "dpmpp_3m_sde"],
                    "categories": ["dpm", "sde", "advanced"],
                    "img2img_compatible": True,
                    "description": "DPM++ solver, 3M, SDE"
                },
                {
                    "name": "DPM++ 3M SDE Karras",
                    "aliases": ["dpm_plus_plus_3m_sde_karras", "dpmpp_3m_sde_karras"],
                    "categories": ["dpm", "sde", "karras", "advanced"],
                    "img2img_compatible": True,
                    "description": "DPM++ 3M SDE with Karras noise schedule"
                },
                {
                    "name": "Restart",
                    "aliases": ["restart"],
                    "categories": ["advanced"],
                    "img2img_compatible": True,
                    "description": "Restart sampler"
                }
            ],
            "upscale_modes": [
                "Linear",
                "Bilinear",
                "Bicubic", 
                "Nearest",
                "Area",
                "Lanczos"
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
                "RealESRGAN_x4plus_anime_6B"
            ]
        }
    
    def _log_debug(self, message: str):
        """Log debug message if debug mode is enabled."""
        if self._debug_mode:
            print(f"StandaloneSamplerProvider: {message}")
    
    def set_debug_mode(self, enabled: bool):
        """Enable or disable debug mode."""
        self._debug_mode = enabled
