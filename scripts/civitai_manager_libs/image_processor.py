"""
Image metadata processor for PNG information extraction and embedding.

Supports extraction via AUTOMATIC1111 WebUI extras or PIL for standalone mode.
"""

import json
import re
from typing import Dict, Any, Optional

from PIL import Image
from PIL.ExifTags import TAGS


class ImageMetadataProcessor:
    """Process image metadata for generation parameters extraction and embedding."""

    def __init__(self, mode: str = 'webui'):
        self.mode = mode

    def extract_png_info(self, image_path: str) -> Dict[str, Any]:
        """Extract PNG metadata information based on mode."""
        if self.mode == 'webui':
            return self._extract_with_webui(image_path)
        return self._extract_with_pil(image_path)

    def _extract_with_webui(self, image_path: str) -> Dict[str, Any]:
        """Use WebUI extras.run_pnginfo if available."""
        try:
            from modules import extras  # type: ignore

            result = extras.run_pnginfo(image_path)
            return result or {}
        except ImportError:
            return self._extract_with_pil(image_path)

    def _extract_with_pil(self, image_path: str) -> Dict[str, Any]:
        """Extract metadata and parameters using PIL."""
        try:
            with Image.open(image_path) as img:
                png_text = getattr(img, 'text', {}) or {}
                exif = self._extract_exif(img)
                png_text.update(exif)
                params = self._parse_generation_parameters(png_text)
                return {'parameters': params, 'raw_info': png_text}
        except Exception:
            return {}

    def _extract_exif(self, img: Image.Image) -> Dict[str, Any]:
        """Extract EXIF tags from image if present."""
        try:
            exif_data = img.getexif()
            if not exif_data:
                return {}
            return {TAGS.get(tag_id, str(tag_id)): val for tag_id, val in exif_data.items()}
        except Exception:
            return {}

    def _parse_generation_parameters(self, png_info: Dict[str, Any]) -> Dict[str, Any]:
        """Parse generation parameters embedded in PNG metadata text."""
        param_text = None
        for key in ('parameters', 'Parameters', 'prompt', 'Prompt'):
            if key in png_info:
                param_text = png_info[key]
                break
        if not param_text:
            return {}
        return self._parse_parameter_string(param_text)

    def _parse_parameter_string(self, text: str) -> Dict[str, Any]:
        """Parse JSON or WebUI formatted parameter string."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        params: Dict[str, Any] = {}
        patterns = {
            'prompt': r'^([^\n]+?)(?=\nNegative prompt:|$)',
            'negative_prompt': r'Negative prompt:\s*([^\n]+)',
            'steps': r'Steps:\s*(\d+)',
            'sampler_name': r'Sampler:\s*([^,\n]+)',
            'cfg_scale': r'CFG scale:\s*([\d.]+)',
            'seed': r'Seed:\s*(\d+)',
            'width': r'Size:\s*(\d+)x\d+',
            'height': r'Size:\s*\d+x(\d+)',
            'model_hash': r'Model hash:\s*([a-f0-9]+)',
            'model': r'Model:\s*([^,\n]+)',
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if not match:
                continue
            val = match.group(1).strip()
            if key in ('steps', 'seed', 'width', 'height'):
                try:
                    params[key] = int(val)
                except ValueError:
                    pass
            elif key == 'cfg_scale':
                try:
                    params[key] = float(val)
                except ValueError:
                    pass
            else:
                params[key] = val
        return params

    def embed_parameters_to_png(
        self, image_path: str, parameters: Dict[str, Any], output_path: Optional[str] = None
    ) -> str:
        """Embed generation parameters into PNG metadata and save."""
        dest = output_path or image_path
        try:
            with Image.open(image_path) as img:
                info = getattr(img, 'text', {}).copy()
                info['parameters'] = self._format_parameters(parameters)
                img.save(dest, pnginfo=info)
            return dest
        except Exception:
            return image_path

    def _format_parameters(self, parameters: Dict[str, Any]) -> str:
        """Format parameters dictionary into text block."""
        parts: list[str] = []
        if 'prompt' in parameters:
            parts.append(parameters['prompt'])
        if 'negative_prompt' in parameters:
            parts.append(f"Negative prompt: {parameters['negative_prompt']}")
        other: list[str] = []
        order = ['steps', 'sampler_name', 'cfg_scale', 'seed', 'width', 'height', 'model']
        for key in order:
            if key in parameters:
                val = parameters[key]
                if key == 'sampler_name':
                    other.append(f"Sampler: {val}")
                elif key == 'cfg_scale':
                    other.append(f"CFG scale: {val}")
                elif key in ('width', 'height'):
                    continue  # handled as size
                else:
                    other.append(f"{key.replace('_', ' ').title()}: {val}")
        # handle size
        if 'width' in parameters and 'height' in parameters:
            other.insert(0, f"Size: {parameters['width']}x{parameters['height']}")
        if other:
            parts.append(', '.join(other))
        return '\n'.join(parts)
