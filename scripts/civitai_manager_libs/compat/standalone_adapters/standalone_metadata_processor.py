"""
Standalone Metadata Processor

Provides metadata processing for standalone execution using PIL.
"""

import os
import re
from typing import Dict, Tuple, Optional, Any

from ..interfaces.imetadata_processor import IMetadataProcessor


class StandaloneMetadataProcessor(IMetadataProcessor):
    """Metadata processor implementation for standalone mode using PIL."""
    
    def extract_png_info(self, image_path: str) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        """Extract metadata from PNG using PIL."""
        try:
            from PIL import Image
            
            if not os.path.exists(image_path):
                return None, None, None
            
            with Image.open(image_path) as img:
                # Extract text metadata
                metadata = {}
                if hasattr(img, 'text'):
                    metadata = img.text
                
                # Look for parameters in common metadata keys
                parameters_text = None
                for key in ['parameters', 'Parameters', 'comment', 'Comment', 'Description']:
                    if key in metadata:
                        parameters_text = metadata[key]
                        break
                
                if parameters_text:
                    # Parse the parameters text
                    generate_data = self.parse_generation_parameters(parameters_text)
                    return parameters_text, generate_data, None
                else:
                    return None, None, None
                    
        except ImportError:
            # PIL not available, return None
            return None, None, None
        except Exception:
            # Any other error
            return None, None, None
    
    def extract_parameters_from_png(self, image_path: str) -> Optional[str]:
        """Extract generation parameters from PNG."""
        info1, generate_data, info3 = self.extract_png_info(image_path)
        return info1
    
    def parse_generation_parameters(self, parameters_text: str) -> Dict[str, Any]:
        """Parse generation parameters text into structured data."""
        if not parameters_text:
            return {}
        
        params = {}
        
        # Extract prompts
        positive_prompt, negative_prompt = self.extract_prompt_from_parameters(parameters_text)
        if positive_prompt:
            params['prompt'] = positive_prompt
        if negative_prompt:
            params['negative_prompt'] = negative_prompt
        
        # Find and parse parameter line
        lines = parameters_text.split('\n')
        for line in lines:
            if self._is_parameter_line(line):
                # Parse key-value pairs from parameter line
                pairs = self._split_parameter_line(line)
                for key, value in pairs:
                    normalized_key = self._normalize_parameter_key(key)
                    parsed_value = self._parse_parameter_value(normalized_key, value)
                    if parsed_value is not None:
                        params[normalized_key] = parsed_value
                break
        
        return params
    
    def extract_prompt_from_parameters(self, parameters_text: str) -> Tuple[str, str]:
        """Extract positive and negative prompts from parameters."""
        if not parameters_text:
            return "", ""
        
        lines = parameters_text.split('\n')
        positive_prompt = ""
        negative_prompt = ""
        
        # Find negative prompt
        negative_found = False
        positive_lines = []
        
        for line in lines:
            if line.strip().lower().startswith('negative prompt:'):
                negative_found = True
                negative_prompt = line[len('negative prompt:'):].strip()
            elif not negative_found and not self._is_parameter_line(line):
                positive_lines.append(line)
            elif negative_found and not self._is_parameter_line(line):
                # Multi-line negative prompt
                negative_prompt += " " + line.strip()
        
        positive_prompt = '\n'.join(positive_lines).strip()
        
        return positive_prompt, negative_prompt
    
    def format_parameters_for_display(self, parameters: Dict[str, Any]) -> str:
        """Format parameters dictionary for display."""
        if not parameters:
            return ""
        
        lines = []
        
        # Add positive prompt
        if 'prompt' in parameters and parameters['prompt']:
            lines.append(str(parameters['prompt']))
        
        # Add negative prompt
        if 'negative_prompt' in parameters and parameters['negative_prompt']:
            lines.append(f"Negative prompt: {parameters['negative_prompt']}")
        
        # Add other parameters
        param_parts = []
        for key, value in parameters.items():
            if key not in ['prompt', 'negative_prompt'] and value is not None:
                # Format key name
                formatted_key = self._format_parameter_key(key)
                param_parts.append(f"{formatted_key}: {value}")
        
        if param_parts:
            lines.append(", ".join(param_parts))
        
        return '\n'.join(lines)
    
    def _is_parameter_line(self, line: str) -> bool:
        """Check if line contains generation parameters."""
        line_lower = line.lower().strip()
        return ('steps:' in line_lower or 
                'sampler:' in line_lower or 
                'cfg scale:' in line_lower or
                'seed:' in line_lower or
                'size:' in line_lower or
                'model:' in line_lower)
    
    def _split_parameter_line(self, line: str) -> list[tuple[str, str]]:
        """Split parameter line into key-value pairs."""
        pairs = []
        # Split by comma, but be careful about commas in quoted values
        parts = re.split(r',(?=\s*[A-Za-z_][A-Za-z0-9_\s]*:)', line)
        
        for part in parts:
            part = part.strip()
            if ':' in part:
                key, value = part.split(':', 1)
                pairs.append((key.strip(), value.strip()))
        
        return pairs
    
    def _normalize_parameter_key(self, key: str) -> str:
        """Normalize parameter key to standard format."""
        key_mapping = {
            'steps': 'steps',
            'sampler': 'sampler_name',
            'cfg scale': 'cfg_scale',
            'seed': 'seed',
            'size': 'size',
            'model hash': 'model_hash',
            'model': 'model',
            'denoising strength': 'denoising_strength',
            'clip skip': 'clip_skip',
            'ensd': 'eta_noise_seed_delta',
        }
        
        key_lower = key.lower().strip()
        return key_mapping.get(key_lower, key_lower.replace(' ', '_'))
    
    def _parse_parameter_value(self, key: str, value: str) -> Any:
        """Parse parameter value to appropriate type."""
        value = value.strip()
        
        # Integer parameters
        if key in ['steps', 'width', 'height', 'batch_size', 'n_iter', 'seed', 'clip_skip']:
            try:
                return int(value)
            except ValueError:
                return None
        
        # Float parameters
        elif key in ['cfg_scale', 'denoising_strength', 'eta_noise_seed_delta']:
            try:
                return float(value)
            except ValueError:
                return None
        
        # Size parameter (e.g., "512x768")
        elif key == 'size' and 'x' in value:
            try:
                width, height = value.split('x')
                return {'width': int(width.strip()), 'height': int(height.strip())}
            except ValueError:
                return value
        
        # String parameters
        else:
            return value
    
    def _format_parameter_key(self, key: str) -> str:
        """Format parameter key for display."""
        key_formatting = {
            'cfg_scale': 'CFG scale',
            'sampler_name': 'Sampler',
            'denoising_strength': 'Denoising strength',
            'clip_skip': 'Clip skip',
            'eta_noise_seed_delta': 'ENSD',
            'model_hash': 'Model hash',
        }
        
        return key_formatting.get(key, key.replace('_', ' ').title())
