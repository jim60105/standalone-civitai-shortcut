"""WebUI Parameter Processor.

Provides parameter processing using AUTOMATIC1111 WebUI modules.
"""

import re
from typing import Dict, Any
from ..interfaces.iparameter_processor import IParameterProcessor


class WebUIParameterProcessor(IParameterProcessor):
    """Parameter processor implementation using WebUI modules."""

    def parse_parameters(self, text: str) -> Dict[str, Any]:
        """Parse parameters using WebUI utilities if available."""
        if not text:
            return {}

        try:
            # Try to use WebUI's infotext parsing
            import modules.infotext_utils

            if hasattr(modules.infotext_utils, "parse_generation_parameters"):
                return modules.infotext_utils.parse_generation_parameters(text)
        except (ImportError, AttributeError):
            pass

        # Fallback to custom parsing
        return self._parse_parameters_fallback(text)

    def format_parameters(self, params: Dict[str, Any]) -> str:
        """Format parameters dictionary into text string."""
        if not params:
            return ""

        lines = []

        # Add positive prompt
        if "prompt" in params and params["prompt"]:
            lines.append(str(params["prompt"]))

        # Add negative prompt
        if "negative_prompt" in params and params["negative_prompt"]:
            lines.append(f"Negative prompt: {params['negative_prompt']}")

        # Add other parameters
        param_parts = []
        for key, value in params.items():
            if key not in ["prompt", "negative_prompt"] and value is not None:
                formatted_key = self._format_parameter_key(key)
                param_parts.append(f"{formatted_key}: {value}")

        if param_parts:
            # Ensure 'Steps' is listed first for WebUI standard
            steps_parts = [p for p in param_parts if p.startswith("Steps:")]
            other_parts = [p for p in param_parts if not p.startswith("Steps:")]
            ordered_parts = steps_parts + other_parts
            lines.append(", ".join(ordered_parts))

        return "\n".join(lines)

    def standardize_parameters_for_webui(self, text: str) -> str:
        """Convert our parameter format to WebUI standard format."""
        if not text:
            return ""

        # Remove Civitai header lines (e.g., "Generated using example parameters from Civitai:")
        lines = text.split("\n")
        if lines and lines[0].lower().startswith("generated using"):
            lines = lines[1:]
        # Strip leading "Prompt:" prefix if present
        if lines and lines[0].lower().startswith("prompt:"):
            lines[0] = lines[0].split(":", 1)[1].strip()
        sanitized_text = "\n".join(lines)
        # Parse using fallback logic to correctly handle Civitai formats
        params = self._parse_parameters_fallback(sanitized_text)

        return self.format_parameters(params)

    def extract_prompt_and_negative(self, text: str) -> tuple[str, str]:
        """Extract positive and negative prompts from parameters text."""
        if not text:
            return "", ""

        lines = text.split("\n")
        positive_prompt = ""
        negative_prompt = ""

        # Find negative prompt
        negative_found = False
        positive_lines = []

        for line in lines:
            if line.strip().lower().startswith("negative prompt:"):
                negative_found = True
                negative_prompt = line[len("negative prompt:") :].strip()
            elif not negative_found and not self._is_parameter_line(line):
                positive_lines.append(line)
            elif negative_found and not self._is_parameter_line(line):
                # Multi-line negative prompt
                negative_prompt += " " + line.strip()

        positive_prompt = "\n".join(positive_lines).strip()

        return positive_prompt, negative_prompt

    def merge_parameters(
        self, base_params: Dict[str, Any], override_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge parameters with override taking precedence."""
        merged = base_params.copy()
        merged.update(override_params)
        return merged

    def _parse_parameters_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback parameter parsing implementation."""
        params = {}

        # Extract prompts
        positive_prompt, negative_prompt = self.extract_prompt_and_negative(text)
        if positive_prompt:
            params["prompt"] = positive_prompt
        if negative_prompt:
            params["negative_prompt"] = negative_prompt

        # Find parameter line (usually contains "Steps:")
        lines = text.split("\n")
        for line in lines:
            if self._is_parameter_line(line):
                # Parse key-value pairs
                pairs = self._split_parameter_line(line)
                for key, value in pairs:
                    normalized_key = self._normalize_parameter_key(key)
                    parsed_value = self._parse_parameter_value(normalized_key, value)
                    if parsed_value is not None:
                        params[normalized_key] = parsed_value
                break

        return params

    def _is_parameter_line(self, line: str) -> bool:
        """Check if line contains generation parameters."""
        line_lower = line.lower().strip()
        return (
            "steps:" in line_lower
            or "sampler:" in line_lower
            or "cfg scale:" in line_lower
            or "seed:" in line_lower
        )

    def _split_parameter_line(self, line: str) -> list[tuple[str, str]]:
        """Split parameter line into key-value pairs."""
        pairs = []
        # Split by comma, but be careful about commas in quoted values
        parts = re.split(r",(?=\s*[A-Za-z_][A-Za-z0-9_\s]*:)", line)

        for part in parts:
            part = part.strip()
            if ":" in part:
                key, value = part.split(":", 1)
                pairs.append((key.strip(), value.strip()))

        return pairs

    def _normalize_parameter_key(self, key: str) -> str:
        """Normalize parameter key to standard format."""
        key_mapping = {
            "steps": "steps",
            "sampler": "sampler_name",
            "cfg scale": "cfg_scale",
            "seed": "seed",
            "size": "size",
            "model hash": "model_hash",
            "model": "model",
            "denoising strength": "denoising_strength",
            "clip skip": "clip_skip",
            "ensd": "eta_noise_seed_delta",
        }

        key_lower = key.lower().strip()
        return key_mapping.get(key_lower, key_lower.replace(" ", "_"))

    def _parse_parameter_value(self, key: str, value: str) -> Any:
        """Parse parameter value to appropriate type."""
        value = value.strip()

        # Integer parameters
        if key in [
            "steps",
            "width",
            "height",
            "batch_size",
            "n_iter",
            "seed",
            "clip_skip",
        ]:
            try:
                return int(value)
            except ValueError:
                return None

        # Float parameters
        elif key in ["cfg_scale", "denoising_strength", "eta_noise_seed_delta"]:
            try:
                val = float(value)
                # Convert whole number floats to int for consistency
                if val.is_integer():
                    return int(val)
                return val
            except ValueError:
                return None

        # Size parameter (e.g., "512x768")
        elif key == "size" and "x" in value:
            try:
                width, height = value.split("x")
                return {"width": int(width.strip()), "height": int(height.strip())}
            except ValueError:
                return value

        # String parameters
        else:
            return value

    def _format_parameter_key(self, key: str) -> str:
        """Format parameter key for display."""
        key_formatting = {
            "cfg_scale": "CFG scale",
            "sampler_name": "Sampler",
            "denoising_strength": "Denoising strength",
            "clip_skip": "Clip skip",
            "eta_noise_seed_delta": "ENSD",
            "model_hash": "Model hash",
        }

        return key_formatting.get(key, key.replace("_", " ").title())
