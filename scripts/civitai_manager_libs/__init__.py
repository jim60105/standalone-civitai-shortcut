"""
Package marker for civitai_manager_libs modules.
"""

from .settings import config_manager

# Import the new modular structure 
from . import http
from . import download

# Backward compatibility imports - expose old module names
# This ensures existing imports like 'from civitai_manager_libs import downloader' still work
import sys
sys.modules[__name__ + '.downloader'] = download
sys.modules[__name__ + '.http_client'] = http

# Also make them available as direct attributes for imports like 'civitai_manager_libs.downloader'
downloader = download
http_client = http