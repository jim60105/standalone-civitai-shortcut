#!/usr/bin/env python3
"""
Python 3.13+ Compatibility Patches

Provides compatibility shims for modules removed in Python 3.13+:
- audioop/pyaudioop (removed in Python 3.13)
- distutils.version.StrictVersion (removed in Python 3.13)

This module follows SRP by focusing solely on Python version compatibility.
"""
import sys
import types
from typing import Any, Tuple


class MockAudioop:
    """Mock audioop module to prevent import errors in Python 3.13+."""
    
    @staticmethod
    def mul(*args: Any, **kwargs: Any) -> bytes:
        """Mock mul function."""
        return b''
    
    @staticmethod
    def add(*args: Any, **kwargs: Any) -> bytes:
        """Mock add function."""
        return b''
    
    @staticmethod
    def bias(*args: Any, **kwargs: Any) -> bytes:
        """Mock bias function."""
        return b''
    
    @staticmethod
    def reverse(*args: Any, **kwargs: Any) -> bytes:
        """Mock reverse function."""
        return b''
    
    @staticmethod
    def lin2lin(*args: Any, **kwargs: Any) -> bytes:
        """Mock lin2lin function."""
        return b''
    
    @staticmethod
    def ratecv(*args: Any, **kwargs: Any) -> Tuple[bytes, Tuple[int, Tuple[Tuple[int, int]]]]:
        """Mock ratecv function."""
        return (b'', (-1, ((0, 0),)))
    
    @staticmethod
    def tomono(*args: Any, **kwargs: Any) -> bytes:
        """Mock tomono function."""
        return b''
    
    @staticmethod
    def tostereo(*args: Any, **kwargs: Any) -> bytes:
        """Mock tostereo function."""
        return b''
    
    @staticmethod
    def minmax(*args: Any, **kwargs: Any) -> Tuple[int, int]:
        """Mock minmax function."""
        return (0, 0)
    
    @staticmethod
    def max(*args: Any, **kwargs: Any) -> int:
        """Mock max function."""
        return 0
    
    @staticmethod
    def maxpp(*args: Any, **kwargs: Any) -> int:
        """Mock maxpp function."""
        return 0
    
    @staticmethod
    def avg(*args: Any, **kwargs: Any) -> int:
        """Mock avg function."""
        return 0
    
    @staticmethod
    def avgpp(*args: Any, **kwargs: Any) -> int:
        """Mock avgpp function."""
        return 0
    
    @staticmethod
    def rms(*args: Any, **kwargs: Any) -> int:
        """Mock rms function."""
        return 0
    
    @staticmethod
    def findfit(*args: Any, **kwargs: Any) -> Tuple[int, int]:
        """Mock findfit function."""
        return (0, 0)
    
    @staticmethod
    def findmax(*args: Any, **kwargs: Any) -> int:
        """Mock findmax function."""
        return 0
    
    @staticmethod
    def cross(*args: Any, **kwargs: Any) -> int:
        """Mock cross function."""
        return 0
    
    @staticmethod
    def ulaw2lin(*args: Any, **kwargs: Any) -> bytes:
        """Mock ulaw2lin function."""
        return b''
    
    @staticmethod
    def lin2ulaw(*args: Any, **kwargs: Any) -> bytes:
        """Mock lin2ulaw function."""
        return b''
    
    @staticmethod
    def alaw2lin(*args: Any, **kwargs: Any) -> bytes:
        """Mock alaw2lin function."""
        return b''
    
    @staticmethod
    def lin2alaw(*args: Any, **kwargs: Any) -> bytes:
        """Mock lin2alaw function."""
        return b''
    
    @staticmethod
    def lin2adpcm(*args: Any, **kwargs: Any) -> Tuple[bytes, Any]:
        """Mock lin2adpcm function."""
        return (b'', None)
    
    @staticmethod
    def adpcm2lin(*args: Any, **kwargs: Any) -> Tuple[bytes, Any]:
        """Mock adpcm2lin function."""
        return (b'', None)


class MockStrictVersion:
    """Mock StrictVersion class for distutils compatibility."""
    
    def __init__(self, version_string: str) -> None:
        """Initialize with version string."""
        self.version = version_string
        self._parse_version(version_string)
    
    def _parse_version(self, version_string: str) -> None:
        """Parse version string into components."""
        parts = version_string.split('.')
        self.version_tuple = tuple(int(p) if p.isdigit() else p for p in parts)
    
    def __str__(self) -> str:
        return self.version
    
    def __repr__(self) -> str:
        return f"StrictVersion('{self.version}')"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, MockStrictVersion):
            return self.version_tuple == other.version_tuple
        return False
    
    def __lt__(self, other: 'MockStrictVersion') -> bool:
        if isinstance(other, MockStrictVersion):
            return self.version_tuple < other.version_tuple
        return NotImplemented
    
    def __le__(self, other: 'MockStrictVersion') -> bool:
        return self == other or self < other
    
    def __gt__(self, other: 'MockStrictVersion') -> bool:
        if isinstance(other, MockStrictVersion):
            return self.version_tuple > other.version_tuple
        return NotImplemented
    
    def __ge__(self, other: 'MockStrictVersion') -> bool:
        return self == other or self > other


def is_python_313_or_later() -> bool:
    """Check if running on Python 3.13 or later."""
    return sys.version_info >= (3, 13)


def patch_audioop_modules() -> bool:
    """
    Patch audioop and pyaudioop modules if missing.
    
    Returns:
        True if patching was applied, False if modules already exist
    """
    needs_patch = False
    
    # Check if audioop is available
    try:
        import audioop  # noqa: F401
    except ImportError:
        needs_patch = True
        mock_audioop = MockAudioop()
        sys.modules['audioop'] = mock_audioop
    
    # Check if pyaudioop is available
    try:
        import pyaudioop  # noqa: F401
    except ImportError:
        needs_patch = True
        mock_pyaudioop = MockAudioop()
        sys.modules['pyaudioop'] = mock_pyaudioop
    
    return needs_patch


def patch_distutils_modules() -> bool:
    """
    Patch distutils.version.StrictVersion if missing.
    
    Returns:
        True if patching was applied, False if module already exists
    """
    try:
        from distutils.version import StrictVersion  # noqa: F401
        return False
    except ImportError:
        # Create distutils.version module with StrictVersion
        dv_module = types.ModuleType("distutils.version")
        dv_module.StrictVersion = MockStrictVersion  # type: ignore[attr-defined]
        
        # Create distutils module
        d_module = types.ModuleType("distutils")
        d_module.version = dv_module  # type: ignore[attr-defined]
        
        # Install in sys.modules
        sys.modules['distutils'] = d_module
        sys.modules['distutils.version'] = dv_module
        
        return True


def apply_python313_patches(verbose: bool = False) -> dict[str, bool]:
    """
    Apply all Python 3.13+ compatibility patches.
    
    Args:
        verbose: If True, print patch status messages
        
    Returns:
        Dictionary with patch status for each module
    """
    results = {}
    
    # Patch audioop modules
    audioop_patched = patch_audioop_modules()
    results['audioop'] = audioop_patched
    if verbose and audioop_patched:
        print("Applied audioop compatibility patches")
    
    # Patch distutils modules  
    distutils_patched = patch_distutils_modules()
    results['distutils'] = distutils_patched
    if verbose and distutils_patched:
        print("Applied distutils compatibility patches")
    
    return results


def ensure_compatibility() -> None:
    """
    Ensure Python 3.13+ compatibility by applying necessary patches.
    
    This is the main entry point for compatibility patching.
    Call this early in application startup or test initialization.
    """
    if is_python_313_or_later():
        apply_python313_patches(verbose=True)


if __name__ == "__main__":
    # Allow running as standalone script for testing
    results = apply_python313_patches(verbose=True)
    print(f"Patch results: {results}")
