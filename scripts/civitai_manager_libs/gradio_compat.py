"""
Gradio compatibility module for versions 3.41.2 and 4.40.0.

This module provides minimal compatibility shims between Gradio 3.41.2 and 4.40.0.
"""

import gradio as gr

# Handle SelectData import for Gradio 3.41.2 vs 4.40.0
try:
    from gradio import SelectData
except ImportError:
    # For older versions, create a simple data class
    class SelectData:
        def __init__(self, index=None, value=None):
            self.index = index
            self.value = value


# Handle components with safe fallbacks
try:
    State = gr.State
except AttributeError:
    # Fallback for test environments
    class State:
        def __init__(self, value=None):
            self.value = value


try:
    HTML = gr.HTML
except AttributeError:
    # Fallback to Markdown if HTML not available
    HTML = getattr(gr, 'Markdown', lambda **kwargs: None)

try:
    Gallery = gr.Gallery
except AttributeError:
    # Use Column as fallback
    Gallery = getattr(gr, 'Column', lambda **kwargs: None)

try:
    File = gr.File
except AttributeError:
    # Use Textbox as fallback
    File = getattr(gr, 'Textbox', lambda **kwargs: None)

try:
    Dropdown = gr.Dropdown
except AttributeError:
    # Use Textbox as fallback
    Dropdown = getattr(gr, 'Textbox', lambda **kwargs: None)

try:
    Accordion = gr.Accordion
except AttributeError:
    # Use Column as fallback
    Accordion = getattr(gr, 'Column', lambda **kwargs: None)

# Export all compatibility components
__all__ = ['SelectData', 'State', 'HTML', 'Gallery', 'File', 'Dropdown', 'Accordion']
