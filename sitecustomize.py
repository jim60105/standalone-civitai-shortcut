"""
sitecustomize: Auto-apply Python 3.13+ compatibility patches.

Python automatically imports 'sitecustomize' on startup if available.
This module ensures compatibility patches are applied early for all Python processes.

Why this is needed even though main.py and conftest.py have manual calls:

1. Gradio depends on pydub, which imports audioop at module level
2. Any direct import of gradio (e.g., `import gradio`) fails without patches
3. sitecustomize provides a global safety net for all Python processes
4. Third-party tools, IDEs, or scripts might import dependencies directly

This ensures compatibility regardless of entry point.
"""

def _apply_compatibility_patches():
    """Apply compatibility patches if needed."""
    try:
        # Try to import and use the dedicated compatibility module
        import sys
        import os
        
        # Add scripts directory to path if needed
        current_dir = os.path.dirname(os.path.abspath(__file__))
        scripts_dir = os.path.join(current_dir, 'scripts')
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        
        from scripts.civitai_manager_libs.compat.python313_patches import ensure_compatibility
        ensure_compatibility()
        
    except Exception:
        # Fallback: basic audioop/distutils stubs for essential compatibility
        import sys
        import types
        
        # Minimal audioop stub - ensure both 'audioop' and 'pyaudioop' are available
        if 'audioop' not in sys.modules and 'pyaudioop' not in sys.modules:
            audioop_stub = types.ModuleType('audioop')
            for name in ['mul', 'add', 'bias', 'reverse', 'lin2lin', 'tomono', 'tostereo']:
                setattr(audioop_stub, name, lambda *a, **k: b'')
            setattr(audioop_stub, 'ratecv', lambda *a, **k: (b'', (None, None)))
            setattr(audioop_stub, 'minmax', lambda *a, **k: (0, 0))
            for name in ['max', 'maxpp', 'avg', 'avgpp', 'rms', 'cross']:
                setattr(audioop_stub, name, lambda *a, **k: 0)
            sys.modules['audioop'] = audioop_stub
            sys.modules['pyaudioop'] = audioop_stub
        
        # Minimal distutils.version stub
        if 'distutils.version' not in sys.modules:
            class StrictVersion:
                def __init__(self, v): self.version = v
                def __lt__(self, o): return False
                def __le__(self, o): return False
                def __eq__(self, o): return False
                def __ge__(self, o): return False
                def __gt__(self, o): return False
            
            dv = types.ModuleType('distutils.version')
            dv.StrictVersion = StrictVersion
            d = types.ModuleType('distutils')
            d.version = dv
            sys.modules['distutils'] = d
            sys.modules['distutils.version'] = dv


# Apply patches immediately when this module is imported
_apply_compatibility_patches()
