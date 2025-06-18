"""
Stub implementation of gradio for standalone testing and CLI usage.

This module provides minimal definitions to allow UI adapter and main
to import gradio without requiring the actual gradio package.
"""


class Blocks:
    """Context manager stub for Gradio Blocks."""

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def launch(self, *args, **kwargs):
        pass


class themes:
    """Stub for Gradio theme definitions."""

    class Soft:
        pass

    class Default:
        pass


def update(*args, **kwargs):
    """Stub for Gradio update function."""
    return None


def Tabs(*args, **kwargs):
    """Stub for Gradio Tabs component."""
    return Blocks()


def TabItem(*args, **kwargs):
    """Stub for Gradio TabItem component."""
    return Blocks()


def Row(*args, **kwargs):
    """Stub for Gradio Row component."""
    return Blocks()


def Column(*args, **kwargs):
    """Stub for Gradio Column component."""
    return Blocks()


def Markdown(*args, **kwargs):
    """Stub for Gradio Markdown component."""
    return None


def Textbox(*args, **kwargs):
    """Stub for Gradio Textbox component."""
    return None


def Number(*args, **kwargs):
    """Stub for Gradio Number component."""
    return None


def Checkbox(*args, **kwargs):
    """Stub for Gradio Checkbox component."""
    return None


def Slider(*args, **kwargs):
    """Stub for Gradio Slider component."""
    return None


def Button(*args, **kwargs):
    """Stub for Gradio Button component."""
    return None


def Progress(*args, **kwargs):
    """Stub for Gradio Progress component."""
    return None
