"""
UI components abstraction for parameter copy-paste functionality.
Supports both WebUI native and standalone implementations.
"""

import gradio as gr
import json
import re
from typing import Dict, Any, Optional


class ParameterCopyPaste:
    """Parameter copy-paste component handling for dual modes."""

    def __init__(self, mode: str = 'webui'):
        self.mode = mode
        self._parameter_mapping = {
            'prompt': 'prompt',
            'negative_prompt': 'negative_prompt',
            'steps': 'steps',
            'sampler_name': 'sampler_name',
            'cfg_scale': 'cfg_scale',
            'seed': 'seed',
            'width': 'width',
            'height': 'height',
        }

    def register_copypaste_components(self, components: Dict[str, gr.Component]) -> None:
        """Register copy-paste components according to mode."""
        if self.mode == 'webui':
            self._register_webui_copypaste(components)
        else:
            self._register_standalone_copypaste(components)

    def _register_webui_copypaste(self, components: Dict[str, gr.Component]) -> None:
        """Use WebUI native parameter paste registration."""
        try:
            from modules import infotext_utils  # type: ignore

            infotext_utils.register_paste_params_button(
                components.get('paste_button'),
                components.get('prompt'),
                components,
            )
        except ImportError:
            self._register_standalone_copypaste(components)

    def _register_standalone_copypaste(self, components: Dict[str, gr.Component]) -> None:
        """Bind standalone paste handling to the paste button."""
        paste_button = components.get('paste_button')
        if paste_button:
            paste_button.click(
                fn=self._handle_paste,
                inputs=[components.get('input_text', gr.Textbox())],
                outputs=[components[key] for key in self._parameter_mapping],
            )

    def _handle_paste(self, input_text: str) -> tuple:
        """Handle paste action parsing text into parameters."""
        if not input_text:
            return tuple([''] * len(self._parameter_mapping))
        params = self._parse_parameters(input_text)
        return tuple(params.get(k, '') for k in self._parameter_mapping)

    def _parse_parameters(self, text: str) -> Dict[str, Any]:
        """Parse parameter text from JSON or WebUI formatted string."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        params: Dict[str, Any] = {}
        patterns = {
            'prompt': r'(?:^|,\s*)([^,]+?)(?=,\s*\w+:|$)',
            'negative_prompt': r'Negative prompt:\s*([^,\n]+)',
            'steps': r'Steps:\s*(\d+)',
            'sampler_name': r'Sampler:\s*([^,\n]+)',
            'cfg_scale': r'CFG scale:\s*([\d.]+)',
            'seed': r'Seed:\s*(\d+)',
            'width': r'Size:\s*(\d+)x\d+',
            'height': r'Size:\s*\d+x(\d+)',
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
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

    def generate_parameter_string(self, components: Dict[str, gr.Component]) -> str:
        """Generate formatted parameter string for copying."""
        params: Dict[str, Any] = {}
        for ui_key, param_key in self._parameter_mapping.items():
            comp = components.get(ui_key)
            if hasattr(comp, 'value'):
                params[param_key] = comp.value
        parts = []
        for key, val in params.items():
            if val:
                parts.append(f"{key}: {val}")
        return ", ".join(parts)
