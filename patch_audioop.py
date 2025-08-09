#!/usr/bin/env python3
"""
Patch script to provide a minimal audioop module for environments missing it.
This is a workaround for Python 3.13+ where audioop was removed.
"""
import sys

# Create a minimal audioop module with stubbed functions
class MockAudioop:
    """Mock audioop module to prevent import errors."""
    
    @staticmethod
    def mul(*args, **kwargs):
        """Mock mul function."""
        return b''
    
    @staticmethod
    def add(*args, **kwargs):
        """Mock add function."""
        return b''
    
    @staticmethod
    def bias(*args, **kwargs):
        """Mock bias function."""
        return b''
    
    @staticmethod
    def reverse(*args, **kwargs):
        """Mock reverse function."""
        return b''
    
    @staticmethod
    def lin2lin(*args, **kwargs):
        """Mock lin2lin function."""
        return b''
    
    @staticmethod
    def ratecv(*args, **kwargs):
        """Mock ratecv function."""
        return (b'', (-1, ((0, 0),)))
    
    @staticmethod
    def tomono(*args, **kwargs):
        """Mock tomono function."""
        return b''
    
    @staticmethod
    def tostereo(*args, **kwargs):
        """Mock tostereo function."""
        return b''
    
    @staticmethod
    def minmax(*args, **kwargs):
        """Mock minmax function."""
        return (0, 0)
    
    @staticmethod
    def max(*args, **kwargs):
        """Mock max function."""
        return 0
    
    @staticmethod
    def maxpp(*args, **kwargs):
        """Mock maxpp function."""
        return 0
    
    @staticmethod
    def avg(*args, **kwargs):
        """Mock avg function."""
        return 0
    
    @staticmethod
    def avgpp(*args, **kwargs):
        """Mock avgpp function."""
        return 0
    
    @staticmethod
    def rms(*args, **kwargs):
        """Mock rms function."""
        return 0
    
    @staticmethod
    def findfit(*args, **kwargs):
        """Mock findfit function."""
        return (0, 0)
    
    @staticmethod
    def findmax(*args, **kwargs):
        """Mock findmax function."""
        return 0
    
    @staticmethod
    def cross(*args, **kwargs):
        """Mock cross function."""
        return 0
    
    @staticmethod
    def ulaw2lin(*args, **kwargs):
        """Mock ulaw2lin function."""
        return b''
    
    @staticmethod
    def lin2ulaw(*args, **kwargs):
        """Mock lin2ulaw function."""
        return b''
    
    @staticmethod
    def alaw2lin(*args, **kwargs):
        """Mock alaw2lin function."""
        return b''
    
    @staticmethod
    def lin2alaw(*args, **kwargs):
        """Mock lin2alaw function."""
        return b''
    
    @staticmethod
    def lin2adpcm(*args, **kwargs):
        """Mock lin2adpcm function."""
        return (b'', None)
    
    @staticmethod
    def adpcm2lin(*args, **kwargs):
        """Mock adpcm2lin function."""
        return (b'', None)


class MockStrictVersion:
    """Mock StrictVersion class for distutils compatibility."""
    
    def __init__(self, version_string):
        """Initialize with version string."""
        self.version = version_string
        self._parse_version(version_string)
    
    def _parse_version(self, version_string):
        """Parse version string into components."""
        # Simple version parsing
        parts = version_string.split('.')
        self.version_tuple = tuple(int(p) if p.isdigit() else p for p in parts)
    
    def __str__(self):
        return self.version
    
    def __repr__(self):
        return f"StrictVersion('{self.version}')"
    
    def __eq__(self, other):
        if isinstance(other, MockStrictVersion):
            return self.version_tuple == other.version_tuple
        return False
    
    def __lt__(self, other):
        if isinstance(other, MockStrictVersion):
            return self.version_tuple < other.version_tuple
        return False
    
    def __le__(self, other):
        return self == other or self < other
    
    def __gt__(self, other):
        if isinstance(other, MockStrictVersion):
            return self.version_tuple > other.version_tuple
        return False
    
    def __ge__(self, other):
        return self == other or self > other


class MockDistutilsVersion:
    """Mock distutils.version module."""
    StrictVersion = MockStrictVersion


class MockDistutils:
    """Mock distutils module."""
    version = MockDistutilsVersion()


def patch_audioop():
    """Patch the audioop module if it's missing."""
    try:
        import audioop
        print("audioop module found, no patching needed")
        return
    except ImportError:
        pass
    
    try:
        import pyaudioop as audioop
        print("pyaudioop module found, no patching needed")
        return
    except ImportError:
        pass
    
    # Neither audioop nor pyaudioop found, install our mock
    print("Installing mock audioop module...")
    mock_audioop = MockAudioop()
    sys.modules['audioop'] = mock_audioop
    sys.modules['pyaudioop'] = mock_audioop
    print("Mock audioop module installed successfully")


def patch_distutils():
    """Patch the distutils module if it's missing."""
    try:
        import distutils
        print("distutils module found, no patching needed")
        return
    except ImportError:
        pass
    
    # distutils not found, install our mock
    print("Installing mock distutils module...")
    mock_distutils = MockDistutils()
    sys.modules['distutils'] = mock_distutils
    sys.modules['distutils.version'] = mock_distutils.version
    print("Mock distutils module installed successfully")


def patch_all():
    """Apply all compatibility patches."""
    patch_audioop()
    patch_distutils()


if __name__ == "__main__":
    patch_all()
