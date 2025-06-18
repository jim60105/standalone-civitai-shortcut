"""
Gradio compatibility module for version differences.

This module provides compatibility shims for different Gradio versions.
"""

import gradio as gr

# Handle SelectData import for different Gradio versions
try:
    # Gradio 5.x
    from gradio.events import SelectData
except ImportError:
    try:
        # Gradio 4.x
        from gradio import SelectData
    except ImportError:
        # Fallback for older versions
        SelectData = None

# Handle State component for different Gradio versions
try:
    # Try to import State from gradio
    from gradio import State
except ImportError:
    # Gradio 5.x doesn't have State, create a dummy implementation
    class State:
        def __init__(self, value=None):
            self.value = value
        
        def __call__(self, *args, **kwargs):
            return self

# Handle HTML component for different Gradio versions
try:
    # Try to import HTML from gradio
    from gradio import HTML
except ImportError:
    # Gradio 5.x might not have HTML, use Markdown as fallback
    class HTML:
        def __init__(self, value="", **kwargs):
            # Convert to Markdown with HTML support
            self._markdown = gr.Markdown(value, **kwargs)
        
        def __getattr__(self, name):
            return getattr(self._markdown, name)

# Handle Gallery component differences
try:
    Gallery = gr.Gallery
except AttributeError:
    # Fallback implementation if Gallery is missing
    class Gallery:
        def __init__(self, **kwargs):
            # Use a simple container as fallback
            self._component = gr.Column(**kwargs)
        
        def __getattr__(self, name):
            return getattr(self._component, name)

# Handle File component differences
try:
    File = gr.File
except AttributeError:
    # Fallback implementation if File is missing
    class File:
        def __init__(self, label=None, **kwargs):
            # Filter out File-specific kwargs that Textbox doesn't understand
            textbox_kwargs = {}
            if label:
                textbox_kwargs['label'] = label
            # Use Textbox as fallback for file input
            self._component = gr.Textbox(placeholder="File path", **textbox_kwargs)
        
        def __getattr__(self, name):
            return getattr(self._component, name)

# Handle Dropdown component differences
try:
    Dropdown = gr.Dropdown
except AttributeError:
    # Fallback implementation if Dropdown is missing
    class Dropdown:
        def __init__(self, **kwargs):
            # Use Textbox as fallback
            self._component = gr.Textbox(**kwargs)
        
        def __getattr__(self, name):
            return getattr(self._component, name)

# Handle Accordion component differences
try:
    Accordion = gr.Accordion
except AttributeError:
    # Fallback implementation if Accordion is missing
    class Accordion:
        def __init__(self, label="", open=True, **kwargs):
            # Use Column as fallback
            self._component = gr.Column(**kwargs)
        
        def __getattr__(self, name):
            return getattr(self._component, name)
        
        def __enter__(self):
            return self._component.__enter__()
        
        def __exit__(self, *args):
            return self._component.__exit__(*args)

# Export all compatibility components
__all__ = [
    'SelectData',
    'State', 
    'HTML',
    'Gallery',
    'File',
    'Dropdown',
    'Accordion'
]
