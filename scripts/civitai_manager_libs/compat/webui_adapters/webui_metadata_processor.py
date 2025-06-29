"""WebUI Metadata Processor.

Provides metadata processing using AUTOMATIC1111 WebUI modules.
"""

import os
import tempfile
from typing import Dict, Tuple, Optional, Any, Union
from PIL import Image

from ..interfaces.imetadata_processor import IMetadataProcessor


class WebUIMetadataProcessor(IMetadataProcessor):
    """Metadata processor implementation using WebUI modules."""

    def extract_png_info(
        self, image_input: Union[str, Image.Image]
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        """Extract metadata from PNG using WebUI modules."""
        # Handle different input types
        temp_path = None

        try:
            # Convert PIL Image to temporary file if needed
            if isinstance(image_input, Image.Image):
                fd, temp_path = tempfile.mkstemp(suffix=".png", prefix="webui_png_info_")
                os.close(fd)
                image_input.save(temp_path, format="PNG")
                image_path = temp_path
            elif isinstance(image_input, str):
                image_path = image_input
            else:
                return None, None, None

            import modules.extras

            # Call WebUI's PNG info extraction
            result = modules.extras.run_pnginfo(image_path)
            if isinstance(result, tuple) and len(result) >= 3:
                return result[0], result[1], result[2]
            else:
                return None, None, None
        except (ImportError, AttributeError, Exception):
            # Fallback to PIL-based extraction
            if isinstance(image_input, str):
                return self._extract_png_info_fallback(image_input)
            else:
                # For PIL Image, create temp file and try fallback
                fd2, temp_path2 = tempfile.mkstemp(suffix=".png", prefix="webui_fallback_")
                os.close(fd2)
                try:
                    image_input.save(temp_path2, format="PNG")
                    return self._extract_png_info_fallback(temp_path2)
                finally:
                    if os.path.exists(temp_path2):
                        os.remove(temp_path2)
        finally:
            # Clean up temp file if created
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def extract_parameters_from_png(self, image_input: Union[str, Image.Image]) -> Optional[str]:
        """Extract generation parameters from PNG."""
        info1, generate_data, info3 = self.extract_png_info(image_input)

        # Try to get parameters from generate_data first
        if generate_data and isinstance(generate_data, dict):
            if "parameters" in generate_data:
                return generate_data["parameters"]

        # Try to get parameters from info1
        if info1:
            return info1

        return None

    def parse_generation_parameters(self, parameters_text: str) -> Dict[str, Any]:
        """Parse generation parameters text into structured data."""
        if not parameters_text:
            return {}

        try:
            # Try to use WebUI's infotext parsing if available
            import modules.infotext_utils

            if hasattr(modules.infotext_utils, "parse_generation_parameters"):
                return modules.infotext_utils.parse_generation_parameters(parameters_text)
        except (ImportError, AttributeError):
            pass

        # Fallback to custom parsing
        return self._parse_parameters_fallback(parameters_text)

    def extract_prompt_from_parameters(self, parameters_text: str) -> Tuple[str, str]:
        """Extract positive and negative prompts from parameters."""
        if not parameters_text:
            return "", ""

        lines = parameters_text.split("\n")
        positive_prompt = ""
        negative_prompt = ""

        # Look for negative prompt marker
        negative_start = -1
        for i, line in enumerate(lines):
            if line.strip().lower().startswith("negative prompt:"):
                negative_start = i
                negative_prompt = line[len("negative prompt:") :].strip()
                break

        # Everything before negative prompt is positive prompt
        if negative_start > 0:
            positive_prompt = "\n".join(lines[:negative_start]).strip()
        elif negative_start == -1:
            # No negative prompt found, everything is positive
            # Look for parameter line (usually starts with Steps:)
            for i, line in enumerate(lines):
                if line.strip().startswith("Steps:"):
                    positive_prompt = "\n".join(lines[:i]).strip()
                    break
            else:
                positive_prompt = parameters_text.strip()

        return positive_prompt, negative_prompt

    def format_parameters_for_display(self, parameters: Dict[str, Any]) -> str:
        """Format parameters dictionary for display."""
        if not parameters:
            return ""

        lines = []

        # Add prompts first
        if "prompt" in parameters:
            lines.append(str(parameters["prompt"]))

        if "negative_prompt" in parameters:
            lines.append(f"Negative prompt: {parameters['negative_prompt']}")

        # Add other parameters
        param_parts = []
        for key, value in parameters.items():
            if key not in ["prompt", "negative_prompt"]:
                param_parts.append(f"{key}: {value}")

        if param_parts:
            lines.append(", ".join(param_parts))

        return "\n".join(lines)

    def _extract_png_info_fallback(
        self, image_path: str
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        """Fallback PNG info extraction using PIL."""
        try:
            from PIL import Image

            if not os.path.exists(image_path):
                return None, None, None

            with Image.open(image_path) as img:
                # Extract text metadata
                metadata = {}
                if hasattr(img, "text"):
                    metadata = img.text

                # Look for parameters in common metadata keys
                parameters_text = None
                for key in ["parameters", "Parameters", "comment", "Comment"]:
                    if key in metadata:
                        parameters_text = metadata[key]
                        break

                if parameters_text:
                    return parameters_text, {"parameters": parameters_text}, None
                else:
                    return None, None, None

        except Exception:
            return None, None, None

    def _parse_parameters_fallback(self, parameters_text: str) -> Dict[str, Any]:
        """Fallback parameter parsing implementation."""
        params: Dict[str, Any] = {}

        if not parameters_text:
            return params

        # Extract prompts
        positive_prompt, negative_prompt = self.extract_prompt_from_parameters(parameters_text)
        if positive_prompt:
            params["prompt"] = positive_prompt
        if negative_prompt:
            params["negative_prompt"] = negative_prompt

        # Look for parameter line (usually the last line)
        lines = parameters_text.split("\n")
        for line in reversed(lines):
            if ":" in line and ("Steps:" in line or "Sampler:" in line):
                # Parse key-value pairs from parameter line
                parts = line.split(", ")
                for part in parts:
                    if ":" in part:
                        key, value = part.split(":", 1)
                        key = key.strip()
                        value = value.strip()

                        # Try to convert to appropriate type
                        if key.lower() in [
                            "steps",
                            "width",
                            "height",
                            "batch_size",
                            "n_iter",
                        ]:
                            try:
                                params[key.lower()] = int(value)
                            except ValueError:
                                params[key.lower()] = value
                        elif key.lower() in ["cfg_scale", "denoising_strength"]:
                            try:
                                params[key.lower()] = float(value)
                            except ValueError:
                                params[key.lower()] = value
                        else:
                            params[key.lower()] = value
                break

        return params
