"""
Parameter Parser for Standalone Mode

Provides comprehensive parameter parsing and formatting capabilities
that replicate AUTOMATIC1111 WebUI parameter handling.
"""

import re
from typing import Dict, List, Optional, Any, Tuple


class ParameterParser:
    """
    Enhanced parameter parser for Stable Diffusion generation parameters.
    
    Handles parsing of complex parameter strings with support for:
    - Basic generation parameters (steps, sampler, CFG scale, etc.)
    - LoRA and embedding parameters
    - ControlNet parameters
    - Custom extensions parameters
    - Multi-line prompts and parameters
    """
    
    def __init__(self):
        """Initialize the parameter parser."""
        self._setup_patterns()
        self._debug_mode = False
    
    def _setup_patterns(self):
        """Set up regular expression patterns for parameter extraction."""
        self.basic_patterns = {
            'steps': r'Steps:\s*(\d+)',
            'sampler': r'Sampler:\s*([^,\n]+?)(?=,|\n|$)',
            'cfg_scale': r'CFG scale:\s*([\d.]+)',
            'seed': r'Seed:\s*(-?\d+)',
            'size': r'Size:\s*(\d+x\d+)', 
            'model_hash': r'Model hash:\s*([a-fA-F0-9]+)',
            'model': r'Model:\s*([^,\n]+?)(?=,|\n|$)',
            'denoising_strength': r'Denoising strength:\s*([\d.]+)',
            'clip_skip': r'Clip skip:\s*(\d+)',
            'ensd': r'ENSD:\s*([\d.]+)',
            'eta': r'Eta:\s*([\d.]+)',
        }
        
        self.advanced_patterns = {
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
            'ddim_discretize': r'DDIM discretize:\s*([^,\n]+)',
            'ddim_eta': r'DDIM eta:\s*([\d.]+)',
        }
        
        # Special patterns for extensions
        self.extension_patterns = {
            'lora': r'<lora:([^:>]+):([^>]+)>',
            'lycoris': r'<lyco:([^:>]+):([^>]+)>',
            'hypernet': r'<hypernet:([^:>]+):([^>]+)>',
            'embedding': r'<([^<>:]+)>',
            'wildcard': r'__([^_]+)__',
        }
    
    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse parameter text into structured data.
        
        Args:
            text: Raw parameter text string
            
        Returns:
            Dictionary containing parsed parameters
        """
        if not text:
            return {}
        
        params = {}
        
        try:
            # Extract prompts first
            positive_prompt, negative_prompt = self._extract_prompts(text)
            if positive_prompt:
                params['prompt'] = positive_prompt
            if negative_prompt:
                params['negative_prompt'] = negative_prompt
            
            # Extract basic parameters
            basic_params = self._extract_basic_parameters(text)
            params.update(basic_params)
            
            # Extract advanced parameters
            advanced_params = self._extract_advanced_parameters(text)
            params.update(advanced_params)
            
            # Extract extension parameters
            extension_params = self._extract_extension_parameters(text)
            params.update(extension_params)
            
            self._log_debug(f"Parsed {len(params)} parameters from text")
            
        except Exception as e:
            self._log_debug(f"Error parsing parameters: {e}")
        
        return params
    
    def _extract_prompts(self, text: str) -> Tuple[str, str]:
        """Extract positive and negative prompts from text."""
        lines = text.split('\n')
        positive_lines = []
        negative_lines = []
        current_section = 'positive'
        
        for line in lines:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            # Check for negative prompt marker
            if line_lower.startswith('negative prompt:'):
                current_section = 'negative'
                negative_content = line[line.lower().find('negative prompt:') + len('negative prompt:'):].strip()
                if negative_content:
                    negative_lines.append(negative_content)
                continue
            
            # Check if we've hit technical parameters
            if self._is_parameter_line(line):
                break
            
            # Add line to appropriate section
            if current_section == 'positive' and line_stripped:
                positive_lines.append(line_stripped)
            elif current_section == 'negative' and line_stripped:
                negative_lines.append(line_stripped)
        
        positive_prompt = ' '.join(positive_lines).strip()
        negative_prompt = ' '.join(negative_lines).strip()
        
        return self._clean_prompt(positive_prompt), self._clean_prompt(negative_prompt)
    
    def _extract_basic_parameters(self, text: str) -> Dict[str, Any]:
        """Extract basic generation parameters."""
        params = {}
        
        for key, pattern in self.basic_patterns.items():
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                params[key] = self._convert_value(key, value)
        
        return params
    
    def _extract_advanced_parameters(self, text: str) -> Dict[str, Any]:
        """Extract advanced generation parameters."""
        params = {}
        
        for key, pattern in self.advanced_patterns.items():
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                params[key] = self._convert_value(key, value)
        
        return params
    
    def _extract_extension_parameters(self, text: str) -> Dict[str, Any]:
        """Extract extension-specific parameters."""
        params = {}
        
        # Extract LoRA parameters
        lora_matches = re.findall(self.extension_patterns['lora'], text, re.IGNORECASE)
        if lora_matches:
            params['lora'] = [
                {'name': name.strip(), 'strength': self._safe_float(strength.strip())}
                for name, strength in lora_matches
            ]
        
        # Extract LyCORIS parameters
        lycoris_matches = re.findall(self.extension_patterns['lycoris'], text, re.IGNORECASE)
        if lycoris_matches:
            params['lycoris'] = [
                {'name': name.strip(), 'strength': self._safe_float(strength.strip())}
                for name, strength in lycoris_matches
            ]
        
        # Extract hypernet parameters from tags
        hypernet_matches = re.findall(self.extension_patterns['hypernet'], text, re.IGNORECASE)
        if hypernet_matches:
            params['hypernet_tags'] = [
                {'name': name.strip(), 'strength': self._safe_float(strength.strip())}
                for name, strength in hypernet_matches
            ]
        
        # Extract embeddings (excluding LoRA and other special tags)
        embedding_matches = re.findall(self.extension_patterns['embedding'], text)
        if embedding_matches:
            # Filter out matches that are actually LoRA or other special tags
            embeddings = []
            for emb in embedding_matches:
                if not any(lora[0] in emb for lora in lora_matches + lycoris_matches + hypernet_matches):
                    embeddings.append(emb.strip())
            if embeddings:
                params['embeddings'] = embeddings
        
        # Extract wildcards
        wildcard_matches = re.findall(self.extension_patterns['wildcard'], text)
        if wildcard_matches:
            params['wildcards'] = [w.strip() for w in wildcard_matches]
        
        return params
    
    def _convert_value(self, key: str, value: str) -> Any:
        """Convert parameter value to appropriate type."""
        value = value.strip()
        
        # Integer parameters
        if key in ['steps', 'batch_size', 'batch_count', 'clip_skip', 
                   'seed_resize_from_h', 'seed_resize_from_w']:
            return self._safe_int(value)
        
        # Special handling for seed (can be -1)
        elif key in ['seed', 'variation_seed']:
            return self._safe_int(value, allow_negative=True)
        
        # Float parameters
        elif key in ['cfg_scale', 'denoising_strength', 'ensd', 'eta', 'ddim_eta',
                     'hypernet_strength', 'variation_seed_strength']:
            return self._safe_float(value)
        
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
        
        # Boolean parameters
        elif key in ['face_restoration'] and value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        # String parameters - clean up quotes
        else:
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            return value
    
    def _safe_int(self, value: str, allow_negative: bool = False) -> Optional[int]:
        """Safely convert string to integer."""
        try:
            result = int(value)
            if not allow_negative and result < 0:
                return None
            return result
        except ValueError:
            return None
    
    def _safe_float(self, value: str) -> Optional[float]:
        """Safely convert string to float."""
        try:
            return float(value)
        except ValueError:
            return None
    
    def _is_parameter_line(self, line: str) -> bool:
        """Check if line contains generation parameters."""
        if not line:
            return False
            
        line_lower = line.lower().strip()
        indicators = [
            'steps:', 'sampler:', 'cfg scale:', 'seed:', 'size:', 
            'model:', 'model hash:', 'denoising strength:', 'clip skip:',
            'ensd:', 'eta:', 'batch size:', 'batch count:'
        ]
        
        return any(indicator in line_lower for indicator in indicators)
    
    def _clean_prompt(self, prompt: str) -> str:
        """Clean up prompt text."""
        if not prompt:
            return ""
        
        # Remove extra whitespace
        prompt = re.sub(r'\s+', ' ', prompt).strip()
        
        # Remove trailing commas that might be artifacts
        prompt = re.sub(r',$', '', prompt).strip()
        
        return prompt
    
    def _log_debug(self, message: str):
        """Log debug message if debug mode is enabled."""
        if self._debug_mode:
            print(f"ParameterParser: {message}")
    
    def set_debug_mode(self, enabled: bool):
        """Enable or disable debug mode."""
        self._debug_mode = enabled


class ParameterFormatter:
    """
    Parameter formatter for converting structured data back to text format.
    
    Produces output that matches AUTOMATIC1111 WebUI parameter format.
    """
    
    def __init__(self):
        """Initialize the parameter formatter."""
        self._debug_mode = False
    
    def format(self, params: Dict[str, Any]) -> str:
        """
        Format parameters dictionary as text.
        
        Args:
            params: Dictionary containing parameters
            
        Returns:
            Formatted parameter string
        """
        if not params:
            return ""
        
        lines = []
        
        # Add positive prompt
        if 'prompt' in params and params['prompt']:
            lines.append(str(params['prompt']))
        
        # Add negative prompt
        if 'negative_prompt' in params and params['negative_prompt']:
            lines.append(f"Negative prompt: {params['negative_prompt']}")
        
        # Format technical parameters
        tech_params = self._format_technical_parameters(params)
        if tech_params:
            lines.append(tech_params)
        
        return '\n'.join(lines)
    
    def _format_technical_parameters(self, params: Dict[str, Any]) -> str:
        """Format technical parameters as comma-separated string."""
        param_parts = []
        
        # Define parameter order for consistent output
        param_order = [
            'steps', 'sampler', 'cfg_scale', 'seed', 'size',
            'model_hash', 'model', 'denoising_strength', 'clip_skip',
            'ensd', 'eta', 'batch_size', 'batch_count',
            'face_restoration', 'hypernet', 'hypernet_strength',
            'variation_seed', 'variation_seed_strength'
        ]
        
        # Add ordered parameters
        for key in param_order:
            if key in params and params[key] is not None:
                formatted_key = self._format_key(key)
                formatted_value = self._format_value(key, params[key])
                if formatted_value:
                    param_parts.append(f"{formatted_key}: {formatted_value}")
        
        # Add remaining parameters
        for key, value in params.items():
            if (key not in ['prompt', 'negative_prompt'] + param_order and
                value is not None and 
                key not in ['lora', 'lycoris', 'embeddings', 'wildcards']):  # Skip extension params
                formatted_key = self._format_key(key)
                formatted_value = self._format_value(key, value)
                if formatted_value:
                    param_parts.append(f"{formatted_key}: {formatted_value}")
        
        return ", ".join(param_parts)
    
    def _format_key(self, key: str) -> str:
        """Format parameter key for display."""
        key_mapping = {
            'cfg_scale': 'CFG scale',
            'sampler': 'Sampler',
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
        
        return key_mapping.get(key, key.replace('_', ' ').title())
    
    def _format_value(self, key: str, value: Any) -> str:
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
        
        # Handle lists
        elif isinstance(value, list):
            return ', '.join(str(item) for item in value)
        
        # Handle dictionaries
        elif isinstance(value, dict):
            return ', '.join([f"{k}: {v}" for k, v in value.items()])
        
        # Default string conversion
        else:
            return str(value)
    
    def set_debug_mode(self, enabled: bool):
        """Enable or disable debug mode."""
        self._debug_mode = enabled
