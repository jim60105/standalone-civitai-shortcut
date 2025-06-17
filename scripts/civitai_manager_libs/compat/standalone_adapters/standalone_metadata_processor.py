"""
Standalone Metadata Processor

Provides metadata processing for standalone execution using PIL.
Enhanced to fully replicate AUTOMATIC1111 WebUI PNG info processing.
"""

import os
import json
import hashlib
from typing import Dict, Tuple, Optional, Any
from PIL import Image
from ..interfaces.imetadata_processor import IMetadataProcessor

try:
    import piexif
    import piexif.helper

    PIEXIF_AVAILABLE = True
except ImportError:
    PIEXIF_AVAILABLE = False


class StandaloneMetadataProcessor(IMetadataProcessor):
    """
    Enhanced metadata processor implementation for standalone mode using PIL.
    Fully replicates AUTOMATIC1111 WebUI functionality.
    """

    PARAM_FIELD_DELIM = ", "
    PARAM_LINE_DELIM = "\n"

    def __init__(self):
        """Initialize the metadata processor."""
        self._debug_mode = False
        self._logger_name = "StandaloneMetadataProcessor"
        self._supported_formats = {".png", ".jpg", ".jpeg", ".webp", ".gif"}

    def set_debug_mode(self, enabled: bool):
        """Enable or disable debug mode."""
        self._debug_mode = enabled

    @property
    def supported_formats(self) -> set:
        """Get supported image formats."""
        return self._supported_formats

    def _calculate_image_hash(self, image_path: str) -> str:
        """Calculate SHA256 hash of image file."""
        sha256_hash = hashlib.sha256()
        with open(image_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def extract_png_info(
        self, image_path: str
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract metadata from image files, replicating A1111's implementation.

        Args:
            image_path: Path to image file

        Returns:
            Tuple containing:
            - Generation parameters text
            - Raw metadata dictionary
            - Formatted display info
        """
        if not os.path.isfile(image_path):
            return None, None, None

        try:
            image = Image.open(image_path)
        except Exception:
            return None, None, None

        geninfo, items = self._extract_metadata(image)

        if items and items.get("Software", "").startswith("NovelAI"):
            try:
                geninfo = self._process_novelai_metadata(items, image)
            except Exception:
                self._log_debug("Error parsing NovelAI metadata")

        info_text = self._format_info_for_display(geninfo, items)
        generation_params = self.parse_generation_parameters(geninfo) if geninfo else {}

        return geninfo, generation_params, info_text

    def _extract_metadata(self, image: Image.Image) -> Tuple[Optional[str], Dict[str, Any]]:
        """Extract metadata from image file."""
        items = {}
        geninfo = None

        if not hasattr(image, 'info'):
            return geninfo, items

        # Copy relevant info fields
        for key, value in image.info.items():
            if value is not None:
                items[key] = value

        if 'parameters' in items:
            geninfo = items['parameters']

        # Try reading from PNG chunks
        if image.format == 'PNG':
            if 'tEXt' in items and isinstance(items['tEXt'], dict):
                for key, value in items['tEXt'].items():
                    items[key] = value
                    if key == 'parameters':
                        geninfo = value

        # Read from EXIF
        if PIEXIF_AVAILABLE:
            try:
                exif = piexif.load(image.info.get('exif', b''))
                exif_comment = (exif or {}).get("Exif", {}).get(piexif.ExifIFD.UserComment, b"")
                try:
                    exif_comment = piexif.helper.UserComment.load(exif_comment)
                except ValueError:
                    exif_comment = exif_comment.decode("utf8", errors="ignore")
                if exif_comment:
                    geninfo = exif_comment
            except Exception:
                pass

        # Clean up metadata
        ignored_keys = {
            "jfif",
            "jfif_version",
            "jfif_unit",
            "jfif_density",
            "dpi",
            "exif",
            "loop",
            "background",
            "timestamp",
            "duration",
            "progressive",
            "progression",
            "icc_profile",
            "chromaticity",
            "photoshop",
        }
        for key in ignored_keys:
            items.pop(key, None)

        return geninfo, items

    def _process_novelai_metadata(self, items: Dict[str, Any], image: Image.Image) -> str:
        """Process NovelAI specific metadata."""
        json_info = json.loads(items["Comment"])

        sampler_mapping = {
            "k_euler_ancestral": "Euler a",
            "k_euler": "Euler",
            "k_lms": "LMS",
            "k_heun": "Heun",
            "k_dpm_2": "DPM2",
            "k_dpm_2_ancestral": "DPM2 a",
            "k_dpmpp_2s_ancestral": "DPM++ 2S a",
            "k_dpmpp_2m": "DPM++ 2M",
            "k_dpmpp_sde": "DPM++ SDE",
            "ddim": "DDIM",
        }

        sampler = sampler_mapping.get(json_info.get("sampler", ""), "Euler a")

        return (
            f"{items['Description']}\n"
            f"Negative prompt: {json_info['uc']}\n"
            f"Steps: {json_info['steps']}, "
            f"Sampler: {sampler}, "
            f"CFG scale: {json_info['scale']}, "
            f"Seed: {json_info['seed']}, "
            f"Size: {image.width}x{image.height}, "
            f"Clip skip: 2, "
            f"ENSD: 31337"
        )

    def extract_parameters_from_png(self, image_path: str) -> Optional[str]:
        """Get parameters string from image metadata."""
        geninfo, _, _ = self.extract_png_info(image_path)
        return geninfo

    def parse_generation_parameters(self, parameters_text: str) -> Dict[str, Any]:
        """Parse generation parameters into structured data, matching A1111's implementation."""
        if not parameters_text:
            return {}

        import re

        # A1111's regex pattern for parsing parameters
        re_param_code = r'\s*(\w[\w \-/]+):\s*("(?:\\.|[^\\"])+"|[^,]*)(?:,|$)'
        re_param = re.compile(re_param_code)
        re_imagesize = re.compile(r"^(\d+)x(\d+)$")

        res = {}
        prompt = ""
        negative_prompt = ""
        done_with_prompt = False

        *lines, lastline = parameters_text.strip().split("\n")
        if len(re_param.findall(lastline)) < 3:
            lines.append(lastline)
            lastline = ''

        # Parse prompt and negative prompt
        for line in lines:
            line = line.strip()
            if line.startswith("Negative prompt:"):
                done_with_prompt = True
                line = line[16:].strip()
            if done_with_prompt:
                negative_prompt += ("" if negative_prompt == "" else "\n") + line
            else:
                prompt += ("" if prompt == "" else "\n") + line

        # Parse parameters from last line
        for k, v in re_param.findall(lastline):
            try:
                if v and v[0] == '"' and v[-1] == '"':
                    v = v[1:-1]  # Simple unquote

                # Handle size parameter specially (A1111 format)
                m = re_imagesize.match(v)
                if m is not None:
                    res[f"{k}-1"] = m.group(1)
                    res[f"{k}-2"] = m.group(2)
                else:
                    res[k] = v
            except Exception:
                print(f"Error parsing \"{k}: {v}\"")

        res["Prompt"] = prompt
        res["Negative prompt"] = negative_prompt

        # Set default values to match A1111
        if "Clip skip" not in res:
            res["Clip skip"] = "1"

        return res

    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize parameters."""
        validated = parameters.copy()

        # Validate steps
        if 'steps' in validated:
            steps = int(validated['steps'])
            validated['steps'] = max(1, min(150, steps))

        # Validate CFG scale
        if 'cfg_scale' in validated:
            cfg = float(validated['cfg_scale'])
            validated['cfg_scale'] = max(1.0, min(30.0, cfg))

        # Validate seed
        if 'seed' in validated:
            seed = int(validated['seed'])
            validated['seed'] = max(-1, min(2**32 - 1, seed))

        return validated

    def extract_prompt_from_parameters(self, parameters_text: str) -> Tuple[str, str]:
        """Get positive and negative prompts."""
        params = self.parse_generation_parameters(parameters_text)
        return params.get("Prompt", ""), params.get("Negative prompt", "")

    def format_parameters_for_display(self, parameters: Dict[str, Any]) -> str:
        """Format parameters for display."""
        if not parameters:
            return ""

        lines = []

        # Add prompt and negative prompt first
        if "Prompt" in parameters:
            lines.append(parameters["Prompt"])
        if "Negative prompt" in parameters:
            lines.append(f"Negative prompt: {parameters['Negative prompt']}")

        # Add remaining parameters, excluding processed ones
        param_list = []
        ordered_keys = [
            "Steps",
            "Sampler",
            "CFG scale",
            "Seed",
            "Size",
            "Model",
            "Model hash",
            "Denoising strength",
            "Clip skip",
            "ENSD",
            "Version",
        ]

        # First add ordered keys
        for key in ordered_keys:
            if key in parameters:
                param_list.append(f"{key}: {parameters[key]}")

        # Then add any remaining parameters
        for key, value in parameters.items():
            if key not in ["Prompt", "Negative prompt"] + ordered_keys:
                param_list.append(f"{key}: {value}")

        if param_list:
            lines.append(self.PARAM_FIELD_DELIM.join(param_list))

        return self.PARAM_LINE_DELIM.join(lines)

    def _log_debug(self, message: str) -> None:
        """Internal debug logging."""
        if self._debug_mode:
            print(f"[{self._logger_name}] {message}")

    def _format_info_for_display(self, geninfo: Optional[str], items: Dict[str, Any]) -> str:
        """Format metadata for display."""
        display_items = {**{"parameters": geninfo}, **items}

        info_parts = []
        for key, text in display_items.items():
            if text is not None:
                key_escaped = str(key).replace("<", "&lt;").replace(">", "&gt;")
                text_escaped = str(text).replace("<", "&lt;").replace(">", "&gt;")

                info_parts.append(
                    f"""
<div>
<p><b>{key_escaped}</b></p>
<p>{text_escaped}</p>
</div>""".strip()
                )

        if not info_parts:
            return "<div><p>No metadata found in image.</p></div>"

        return "\n".join(info_parts)
