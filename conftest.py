import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts")))
# Stub gradio module for tests (avoid requiring actual gradio dependency)
import types

stub_gradio = types.ModuleType('gradio')
stub_gradio.Warning = lambda msg: None
stub_gradio.update = lambda *args, **kwargs: None


def __getattr__(name):
    # Provide dummy classes or callables for any gradio attribute
    return type(name, (), {})


stub_gradio.__getattr__ = __getattr__
sys.modules['gradio'] = stub_gradio
try:
    import PIL
    import PIL.Image
except ImportError:
    # Stub PIL modules if Pillow is not installed
    sys.modules['PIL'] = types.ModuleType('PIL')
    pil_image_module = types.ModuleType('PIL.Image')
    # Provide a dummy Image class for compatibility interfaces
    pil_image_module.Image = type('Image', (), {})
    sys.modules['PIL.Image'] = pil_image_module
    sys.modules['PIL'].Image = pil_image_module
try:
    import requests
except ImportError:
    # Stub requests if not installed
    sys.modules['requests'] = types.ModuleType('requests')

import pytest  # noqa: F401

# Strip application-specific CLI args before pytest parsing
_orig_argv = sys.argv[:]
_prefixes = (
    '--port',
    '--host',
    '--share',
    '--debug',
    '--quiet',
    '--reload',
    '--config',
    '--models-path',
    '--output-path',
    '--version',
)
sys.argv = [_orig_argv[0]] + [
    arg for arg in _orig_argv[1:] if not any(arg.startswith(p) for p in _prefixes)
]


def pytest_configure(config):
    """
    Ensure compatibility package and its submodules are imported so coverage can detect them.
    """
    try:
        import pkgutil

        # Import compatibility modules under scripts.civitai_manager_libs.compat
        try:
            import scripts.civitai_manager_libs.compat as compat_pkg

            for _, name, _ in pkgutil.walk_packages(compat_pkg.__path__, compat_pkg.__name__ + '.'):
                __import__(name)
        except ImportError:
            pass

        # Import compatibility modules under civitai_manager_libs.compat
        try:
            import civitai_manager_libs.compat as compat2

            for _, name, _ in pkgutil.walk_packages(compat2.__path__, compat2.__name__ + '.'):
                __import__(name)
        except ImportError:
            pass
    except Exception:
        pass
