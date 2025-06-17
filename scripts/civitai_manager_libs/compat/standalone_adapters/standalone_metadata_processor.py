"""
Standalone Metadata Processor

Provides metadata processing for standalone execution using PIL.
Enhanced to fully replicate AUTOMATIC1111 WebUI PNG info processing.
"""

import os
import re
import json
import base64
import io
from typing import Dict, Tuple, Optional, Any, List
from ..interfaces.imetadata_processor import IMetadataProcessor

try:
    import piexif
    import piexif.helper
    PIEXIF_AVAILABLE = True
except ImportError:
    PIEXIF_AVAILABLE = False

try:
    from PIL import Image, PngImagePlugin
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class StandaloneMetadataProcessor(IMetadataProcessor):
    """
    Enhanced metadata processor implementation for standalone mode using PIL.
    
    Provides comprehensive PNG metadata processing that fully replicates
    AUTOMATIC1111 WebUI functionality.
    """
    
    def __init__(self):
        """Initialize the metadata processor."""
        self._debug_mode = False
        self._logger_name = "StandaloneMetadataProcessor"
    
    def extract_png_info(self, image_path: str) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract metadata from PNG using PIL, replicating modules.extras.run_pnginfo().
        
        This implementation matches AUTOMATIC1111's read_info_from_image exactly.
        
        Returns:
            Tuple containing:
            - info1: Empty string (as per WebUI)
            - geninfo: Generation parameters as string
            - info3: HTML formatted info for display
        """
        if not PIL_AVAILABLE:
            self._log_debug("PIL not available")
            return "", "", ""
        
        try:
            if not os.path.exists(image_path):
                self._log_debug(f"Image file not found: {image_path}")
                return "", "", ""
            
            with Image.open(image_path) as image:
                geninfo, items = self._read_info_from_image(image)
                
                # Format items for display (matching WebUI's run_pnginfo format)
                info_html = self._format_info_for_display(geninfo, items)
                
                return "", geninfo or "", info_html
                
        except Exception as e:
            self._log_debug(f"Error extracting PNG info from {image_path}: {e}")
            return "", "", ""
    
    def _read_info_from_image(self, image: "Image.Image") -> Tuple[Optional[str], Dict[str, Any]]:
        """
        Read info from image, replicating AUTOMATIC1111's read_info_from_image exactly.
        
        Returns:
            Tuple containing:
            - geninfo: Generation parameters as string
            - items: Dictionary of all metadata items
        """
        # Get image info copy
        items = (image.info or {}).copy()
        
        # Pop parameters from items
        geninfo = items.pop('parameters', None)
        
        # Check EXIF data if available
        if "exif" in items and PIEXIF_AVAILABLE:
            exif_data = items["exif"]
            try:
                exif = piexif.load(exif_data)
            except OSError:
                # memory / exif was not valid so piexif tried to read from a file
                exif = None
            
            exif_comment = (exif or {}).get("Exif", {}).get(piexif.ExifIFD.UserComment, b'')
            try:
                exif_comment = piexif.helper.UserComment.load(exif_comment)
            except ValueError:
                exif_comment = exif_comment.decode('utf8', errors="ignore")
            
            if exif_comment:
                geninfo = exif_comment
        
        # Check comment field for GIF
        elif "comment" in items:
            if isinstance(items["comment"], bytes):
                geninfo = items["comment"].decode('utf8', errors="ignore")
            else:
                geninfo = items["comment"]
        
        # Remove ignored info keys (matching WebUI's IGNORED_INFO_KEYS)
        ignored_keys = {
            'jfif', 'jfif_version', 'jfif_unit', 'jfif_density', 'dpi', 'exif',
            'loop', 'background', 'timestamp', 'duration', 'progressive', 'progression',
            'icc_profile', 'chromaticity', 'photoshop',
        }
        
        for field in ignored_keys:
            items.pop(field, None)
        
        # Handle NovelAI format (matching WebUI exactly)
        if items.get("Software", None) == "NovelAI":
            try:
                json_info = json.loads(items["Comment"])
                # Map NovelAI sampler to WebUI sampler
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
                    "ddim": "DDIM"
                }
                sampler = sampler_mapping.get(json_info.get("sampler", ""), "Euler a")
                
                geninfo = f"""{items["Description"]}
Negative prompt: {json_info["uc"]}
Steps: {json_info["steps"]}, Sampler: {sampler}, CFG scale: {json_info["scale"]}, Seed: {json_info["seed"]}, Size: {image.width}x{image.height}, Clip skip: 2, ENSD: 31337"""
            except Exception:
                self._log_debug("Error parsing NovelAI image generation parameters")
        
        return geninfo, items
    
    def _format_info_for_display(self, geninfo: Optional[str], items: Dict[str, Any]) -> str:
        """
        Format info for display, matching WebUI's run_pnginfo format exactly.
        """
        # Combine parameters and items for display
        display_items = {**{'parameters': geninfo}, **items}
        
        info_parts = []
        for key, text in display_items.items():
            if text is not None:
                # HTML escape the text (simplified version)
                key_escaped = str(key).replace('<', '&lt;').replace('>', '&gt;')
                text_escaped = str(text).replace('<', '&lt;').replace('>', '&gt;')
                
                info_parts.append(f"""
<div>
<p><b>{key_escaped}</b></p>
<p>{text_escaped}</p>
</div>
""".strip())
        
        if len(info_parts) == 0:
            message = "Nothing found in the image."
            return f"<div><p>{message}</p></div>"
        
        return "\n".join(info_parts)
    
    def _extract_parameters_text(self, metadata: Dict[str, str]) -> Optional[str]:
        """Extract parameters text from PNG metadata."""
        # Try multiple keys where parameters might be stored
        parameter_keys = [
            'parameters',
            'Parameters', 
            'comment',
            'Comment',
            'Description',
            'description',
            'Software',
            'UserComment'
        ]
        
        for key in parameter_keys:
            if key in metadata and metadata[key]:
                text = metadata[key].strip()
                # Check if this looks like generation parameters
                if self._is_valid_parameters_text(text):
                    return text
        
        return None
    
    def _is_valid_parameters_text(self, text: str) -> bool:
        """Check if text contains valid generation parameters."""
        if not text:
            return False
        
        # Look for common parameter indicators
        indicators = [
            'Steps:', 'Sampler:', 'CFG scale:', 'Seed:', 'Size:',
            'Model hash:', 'Model:', 'Denoising strength:'
        ]
        
        text_lower = text.lower()
        return any(indicator.lower() in text_lower for indicator in indicators)
    
    def _extract_additional_info(self, metadata: Dict[str, str], parameters_text: str) -> Optional[str]:
        """Extract additional information from metadata."""
        info_parts = []
        
        # Add file format info
        if 'Software' in metadata and metadata['Software'] != parameters_text:
            info_parts.append(f"Software: {metadata['Software']}")
        
        # Add creation date if available
        if 'Creation Time' in metadata:
            info_parts.append(f"Created: {metadata['Creation Time']}")
        elif 'DateTime' in metadata:
            info_parts.append(f"Created: {metadata['DateTime']}")
        
        # Add other relevant metadata
        for key in ['Author', 'Copyright', 'Source']:
            if key in metadata and metadata[key]:
                info_parts.append(f"{key}: {metadata[key]}")
        
        return '\n'.join(info_parts) if info_parts else None
    
    def _log_debug(self, message: str):
        """Log debug message if debug mode is enabled."""
        if self._debug_mode:
            print(f"{self._logger_name}: {message}")
    
    def extract_parameters_from_png(self, image_path: str) -> Optional[str]:
        """Extract generation parameters from PNG."""
        info1, generate_data, info3 = self.extract_png_info(image_path)
        return generate_data if generate_data else info1
    
    def parse_generation_parameters(self, x: str, skip_fields: List[str] = None) -> Dict[str, Any]:
        """
        Parse generation parameters text into structured data.
        
        This implementation exactly matches AUTOMATIC1111's infotext_utils.parse_generation_parameters.
        """
        if not x:
            return {}
        
        # Match WebUI's skip_fields default
        if skip_fields is None:
            skip_fields = []  # WebUI uses shared.opts.infotext_skip_pasting
        
        res = {}
        
        # Regular expressions from WebUI
        re_param_code = r'\s*(\w[\w \-/]+):\s*("(?:\\.|[^\\"])+"|[^,]*)(?:,|$)'
        re_param = re.compile(re_param_code)
        re_imagesize = re.compile(r"^(\d+)x(\d+)$")
        
        prompt = ""
        negative_prompt = ""
        
        done_with_prompt = False
        
        *lines, lastline = x.strip().split("\n")
        if len(re_param.findall(lastline)) < 3:
            lines.append(lastline)
            lastline = ''
        
        for line in lines:
            line = line.strip()
            if line.startswith("Negative prompt:"):
                done_with_prompt = True
                line = line[16:].strip()
            if done_with_prompt:
                negative_prompt += ("" if negative_prompt == "" else "\n") + line
            else:
                prompt += ("" if prompt == "" else "\n") + line
        
        for k, v in re_param.findall(lastline):
            try:
                if v[0] == '"' and v[-1] == '"':
                    v = self._unquote(v)
                
                m = re_imagesize.match(v)
                if m is not None:
                    res[f"{k}-1"] = m.group(1)
                    res[f"{k}-2"] = m.group(2)
                else:
                    res[k] = v
            except Exception:
                self._log_debug(f"Error parsing \"{k}: {v}\"")
        
        # Set defaults exactly as WebUI does
        res["Prompt"] = prompt
        res["Negative prompt"] = negative_prompt
        
        # Missing CLIP skip means it was set to 1 (the default)
        if "Clip skip" not in res:
            res["Clip skip"] = "1"
        
        # Process hypernet parameter
        hypernet = res.get("Hypernet", None)
        if hypernet is not None:
            res["Prompt"] += f"""<hypernet:{hypernet}:{res.get("Hypernet strength", "1.0")}>"""
        
        if "Hires resize-1" not in res:
            res["Hires resize-1"] = 0
            res["Hires resize-2"] = 0
        
        if "Hires sampler" not in res:
            res["Hires sampler"] = "Use same sampler"
        
        if "Hires schedule type" not in res:
            res["Hires schedule type"] = "Use same scheduler"
        
        if "Hires checkpoint" not in res:
            res["Hires checkpoint"] = "Use same checkpoint"
        
        if "Hires prompt" not in res:
            res["Hires prompt"] = ""
        
        if "Hires negative prompt" not in res:
            res["Hires negative prompt"] = ""
        
        if "Mask mode" not in res:
            res["Mask mode"] = "Inpaint masked"
        
        if "Masked content" not in res:
            res["Masked content"] = 'original'
        
        if "Inpaint area" not in res:
            res["Inpaint area"] = "Whole picture"
        
        if "Masked area padding" not in res:
            res["Masked area padding"] = 32
        
        # Missing RNG means the default was set, which is GPU RNG
        if "RNG" not in res:
            res["RNG"] = "GPU"
        
        if "Schedule type" not in res:
            res["Schedule type"] = "Automatic"
        
        if "Schedule max sigma" not in res:
            res["Schedule max sigma"] = 0
        
        if "Schedule min sigma" not in res:
            res["Schedule min sigma"] = 0
        
        if "Schedule rho" not in res:
            res["Schedule rho"] = 0
        
        if "VAE Encoder" not in res:
            res["VAE Encoder"] = "Full"
        
        if "VAE Decoder" not in res:
            res["VAE Decoder"] = "Full"
        
        if "FP8 weight" not in res:
            res["FP8 weight"] = "Disable"
        
        if "Cache FP16 weight for LoRA" not in res and res["FP8 weight"] != "Disable":
            res["Cache FP16 weight for LoRA"] = False
        
        if "Emphasis" not in res:
            res["Emphasis"] = "Original"
        
        if "Refiner switch by sampling steps" not in res:
            res["Refiner switch by sampling steps"] = False
        
        # Remove skip_fields
        for key in skip_fields:
            res.pop(key, None)
        
        return res
    
    def _unquote(self, text: str) -> str:
        """Unquote text, matching WebUI's unquote function."""
        if len(text) == 0 or text[0] != '"' or text[-1] != '"':
            return text
        
        try:
            return json.loads(text)
        except Exception:
            return text
    
    def _extract_technical_parameters(self, text: str) -> Dict[str, Any]:
        """Extract technical parameters from text."""
        params = {}
        
        # Enhanced parameter patterns with better regex
        patterns = {
            'steps': r'Steps:\s*(\d+)',
            'sampler_name': r'Sampler:\s*([^,\n]+?)(?=,|\n|$)',
            'cfg_scale': r'CFG scale:\s*([\d.]+)',
            'seed': r'Seed:\s*(-?\d+)',
            'size': r'Size:\s*(\d+x\d+)',
            'model_hash': r'Model hash:\s*([a-fA-F0-9]+)',
            'model': r'Model:\s*([^,\n]+?)(?=,|\n|$)',
            'denoising_strength': r'Denoising strength:\s*([\d.]+)',
            'clip_skip': r'Clip skip:\s*(\d+)',
            'ensd': r'ENSD:\s*([\d.]+)',
            'eta': r'Eta:\s*([\d.]+)',
            'ddim_discretize': r'DDIM discretize:\s*([^,\n]+)',
            'ddim_eta': r'DDIM eta:\s*([\d.]+)',
            'batch_size': r'Batch size:\s*(\d+)',
            'batch_count': r'Batch count:\s*(\d+)',
            'face_restoration': r'Face restoration:\s*([^,\n]+)',
            'parser': r'Parser:\s*([^,\n]+)',
            'hypernet': r'Hypernet:\s*([^,\n]+)',
            'hypernet_strength': r'Hypernet strength:\s*([\d.]+)',
            'variation_seed': r'Variation seed:\s*(-?\d+)',
            'variation_seed_strength': r'Variation seed strength:\s*([\d.]+)',
            'seed_resize_from_h': r'Seed resize from h:\s*(\d+)',
            'seed_resize_from_w': r'Seed resize from w:\s*(\d+)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                params[key] = self._convert_parameter_value(key, value)
        
        return params
    
    def _extract_advanced_parameters(self, text: str) -> Dict[str, Any]:
        """Extract advanced parameters including extensions and custom fields."""
        params = {}
        
        # Look for ControlNet parameters
        controlnet_match = re.search(r'ControlNet:\s*"([^"]*)"', text)
        if controlnet_match:
            params['controlnet'] = controlnet_match.group(1)
        
        # Look for LoRA parameters
        lora_pattern = r'<lora:([^:>]+):([^>]+)>'
        lora_matches = re.findall(lora_pattern, text)
        if lora_matches:
            params['lora'] = []
            for name, strength in lora_matches:
                try:
                    strength_value = float(strength.strip())
                except ValueError:
                    strength_value = strength.strip()
                params['lora'].append({'name': name.strip(), 'strength': strength_value})
        
        # Look for embeddings/textual inversions
        embedding_pattern = r'<([^<>:]+)>'
        embedding_matches = re.findall(embedding_pattern, text)
        if embedding_matches:
            # Filter out LoRA matches
            embeddings = [emb for emb in embedding_matches if not any(lora[0] in emb for lora in lora_matches)]
            if embeddings:
                params['embeddings'] = embeddings
        
        # Look for wildcards
        wildcard_pattern = r'__([^_]+)__'
        wildcard_matches = re.findall(wildcard_pattern, text)
        if wildcard_matches:
            params['wildcards'] = wildcard_matches
        
        # Look for additional network parameters
        addnet_pattern = r'AddNet\s+([^:]+):\s*([^,\n]+)'
        addnet_matches = re.findall(addnet_pattern, text)
        if addnet_matches:
            params['additional_networks'] = dict(addnet_matches)
        
        return params
    
    def _convert_parameter_value(self, key: str, value: str) -> Any:
        """Convert parameter value to appropriate type with enhanced handling."""
        value = value.strip()
        
        # Integer parameters
        if key in ['steps', 'batch_size', 'batch_count', 'clip_skip', 
                   'seed_resize_from_h', 'seed_resize_from_w']:
            try:
                return int(value)
            except ValueError:
                return value
        
        # Special handling for seed (can be -1)
        elif key in ['seed', 'variation_seed']:
            try:
                return int(value)
            except ValueError:
                return value
        
        # Float parameters
        elif key in ['cfg_scale', 'denoising_strength', 'ensd', 'eta', 'ddim_eta',
                     'hypernet_strength', 'variation_seed_strength']:
            try:
                return float(value)
            except ValueError:
                return value
        
        # Size parameter (e.g., "512x768")
        elif key == 'size' and 'x' in value:
            try:
                width, height = value.split('x', 1)
                return {
                    'width': int(width.strip()), 
                    'height': int(height.strip()),
                    'size_string': value
                }
            except ValueError:
                return value
        
        # Boolean parameters (represented as strings)
        elif key in ['face_restoration'] and value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        # String parameters - clean up
        else:
            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            
            return value
    
    def extract_prompt_from_parameters(self, parameters_text: str) -> Tuple[str, str]:
        """
        Extract positive and negative prompts from parameters.
        
        Enhanced to handle complex multi-line prompts and edge cases.
        """
        if not parameters_text:
            return "", ""
        
        lines = parameters_text.split('\n')
        positive_prompt_lines = []
        negative_prompt_lines = []
        current_section = 'positive'
        
        for line in lines:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            # Check for negative prompt marker
            if line_lower.startswith('negative prompt:'):
                current_section = 'negative'
                # Extract negative prompt from this line
                negative_content = line[line.lower().find('negative prompt:') + len('negative prompt:'):].strip()
                if negative_content:
                    negative_prompt_lines.append(negative_content)
                continue
            
            # Check if we've hit technical parameters
            if self._is_parameter_line(line):
                break
            
            # Add line to appropriate section
            if current_section == 'positive' and line_stripped:
                positive_prompt_lines.append(line_stripped)
            elif current_section == 'negative' and line_stripped:
                negative_prompt_lines.append(line_stripped)
        
        # Join and clean up prompts
        positive_prompt = ' '.join(positive_prompt_lines).strip()
        negative_prompt = ' '.join(negative_prompt_lines).strip()
        
        # Clean up common artifacts
        positive_prompt = self._clean_prompt(positive_prompt)
        negative_prompt = self._clean_prompt(negative_prompt)
        
        return positive_prompt, negative_prompt
    
    def _clean_prompt(self, prompt: str) -> str:
        """Clean up prompt text by removing artifacts."""
        if not prompt:
            return ""
        
        # Remove extra whitespace
        prompt = re.sub(r'\s+', ' ', prompt).strip()
        
        # Remove trailing commas and periods that might be artifacts
        prompt = re.sub(r'[,\.]$', '', prompt).strip()
        
        return prompt
    
    def format_parameters_for_display(self, parameters: Dict[str, Any]) -> str:
        """
        Format parameters dictionary for display.
        
        Enhanced to produce output that matches AUTOMATIC1111 WebUI format.
        """
        if not parameters:
            return ""
        
        lines = []
        
        # Add positive prompt
        if 'prompt' in parameters and parameters['prompt']:
            lines.append(str(parameters['prompt']))
        
        # Add negative prompt
        if 'negative_prompt' in parameters and parameters['negative_prompt']:
            lines.append(f"Negative prompt: {parameters['negative_prompt']}")
        
        # Group technical parameters
        tech_params = []
        param_order = [
            'steps', 'sampler_name', 'cfg_scale', 'seed', 'size', 
            'model_hash', 'model', 'denoising_strength', 'clip_skip',
            'ensd', 'eta', 'batch_size', 'batch_count'
        ]
        
        # Add ordered parameters
        for key in param_order:
            if key in parameters and parameters[key] is not None:
                formatted_key = self._format_parameter_key_for_display(key)
                formatted_value = self._format_parameter_value_for_display(key, parameters[key])
                if formatted_value:
                    tech_params.append(f"{formatted_key}: {formatted_value}")
        
        # Add remaining parameters not in the ordered list
        for key, value in parameters.items():
            if (key not in ['prompt', 'negative_prompt'] + param_order and 
                value is not None):
                formatted_key = self._format_parameter_key_for_display(key)
                formatted_value = self._format_parameter_value_for_display(key, value)
                if formatted_value:
                    tech_params.append(f"{formatted_key}: {formatted_value}")
        
        if tech_params:
            lines.append(", ".join(tech_params))
        
        return '\n'.join(lines)
    
    def _format_parameter_key_for_display(self, key: str) -> str:
        """Format parameter key for display."""
        key_formatting = {
            'cfg_scale': 'CFG scale',
            'sampler_name': 'Sampler',
            'denoising_strength': 'Denoising strength',
            'clip_skip': 'Clip skip',
            'ensd': 'ENSD',
            'eta': 'Eta',
            'model_hash': 'Model hash',
            'model': 'Model',
            'batch_size': 'Batch size',
            'batch_count': 'Batch count',
            'face_restoration': 'Face restoration',
            'hypernet': 'Hypernet',
            'hypernet_strength': 'Hypernet strength',
            'variation_seed': 'Variation seed',
            'variation_seed_strength': 'Variation seed strength',
            'seed_resize_from_h': 'Seed resize from h',
            'seed_resize_from_w': 'Seed resize from w',
        }
        
        return key_formatting.get(key, key.replace('_', ' ').title())
    
    def _format_parameter_value_for_display(self, key: str, value: Any) -> str:
        """Format parameter value for display."""
        if value is None:
            return ""
        
        # Handle size dictionary
        if key == 'size' and isinstance(value, dict):
            if 'size_string' in value:
                return value['size_string']
            elif 'width' in value and 'height' in value:
                return f"{value['width']}x{value['height']}"
        
        # Handle boolean values
        elif isinstance(value, bool):
            return str(value)
        
        # Handle lists (for LoRA, embeddings, etc.)
        elif isinstance(value, list):
            if key == 'lora':
                return ', '.join([f"<lora:{item['name']}:{item['strength']}>" for item in value if isinstance(item, dict)])
            elif key == 'embeddings':
                return ', '.join([f"<{item}>" for item in value])
            else:
                return ', '.join(str(item) for item in value)
        
        # Handle dictionaries
        elif isinstance(value, dict):
            return ', '.join([f"{k}: {v}" for k, v in value.items()])
        
        # Default string conversion
        else:
            return str(value)
    
    def _is_parameter_line(self, line: str) -> bool:
        """
        Check if line contains generation parameters.
        
        Enhanced detection for parameter lines.
        """
        if not line:
            return False
            
        line_lower = line.lower().strip()
        
        # Common parameter indicators
        indicators = [
            'steps:', 'sampler:', 'cfg scale:', 'seed:', 'size:', 
            'model:', 'model hash:', 'denoising strength:', 'clip skip:',
            'ensd:', 'eta:', 'batch size:', 'batch count:',
            'face restoration:', 'hypernet:', 'variation seed:'
        ]
        
        return any(indicator in line_lower for indicator in indicators)
    
    def set_debug_mode(self, enabled: bool):
        """Enable or disable debug mode."""
        self._debug_mode = enabled
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean parameters dictionary.
        
        Ensures parameter values are within reasonable ranges and formats.
        """
        if not parameters:
            return {}
        
        validated = {}
        
        for key, value in parameters.items():
            try:
                validated_value = self._validate_parameter_value(key, value)
                if validated_value is not None:
                    validated[key] = validated_value
            except Exception as e:
                self._log_debug(f"Error validating parameter {key}={value}: {e}")
                # Keep original value if validation fails
                validated[key] = value
        
        return validated
    
    def _validate_parameter_value(self, key: str, value: Any) -> Any:
        """Validate individual parameter value."""
        if value is None:
            return None
        
        # Steps validation
        if key == 'steps':
            if isinstance(value, int) and 1 <= value <= 500:
                return value
            elif isinstance(value, str) and value.isdigit():
                steps = int(value)
                return steps if 1 <= steps <= 500 else None
        
        # CFG scale validation
        elif key == 'cfg_scale':
            if isinstance(value, (int, float)) and 0.1 <= value <= 30:
                return float(value)
            elif isinstance(value, str):
                try:
                    cfg = float(value)
                    return cfg if 0.1 <= cfg <= 30 else None
                except ValueError:
                    return None
        
        # Seed validation
        elif key in ['seed', 'variation_seed']:
            if isinstance(value, int):
                return value
            elif isinstance(value, str) and (value.isdigit() or value.lstrip('-').isdigit()):
                return int(value)
        
        # Denoising strength validation
        elif key == 'denoising_strength':
            if isinstance(value, (int, float)) and 0.0 <= value <= 1.0:
                return float(value)
            elif isinstance(value, str):
                try:
                    strength = float(value)
                    return strength if 0.0 <= strength <= 1.0 else None
                except ValueError:
                    return None
        
        # Size validation
        elif key == 'size':
            if isinstance(value, dict) and 'width' in value and 'height' in value:
                width, height = value['width'], value['height']
                if (isinstance(width, int) and isinstance(height, int) and
                    64 <= width <= 4096 and 64 <= height <= 4096):
                    return value
        
        # Default: return original value
        return value
