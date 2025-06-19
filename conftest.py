import sys
import pytest

# Strip application-specific CLI args before pytest parsing
_orig_argv = sys.argv[:]
_prefixes = (
    '--port', '--host', '--share', '--debug', '--quiet',
    '--reload', '--config', '--models-path', '--output-path',
    '--version',
)
sys.argv = [
    _orig_argv[0]
]+ [arg for arg in _orig_argv[1:] if not any(arg.startswith(p) for p in _prefixes)]



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
