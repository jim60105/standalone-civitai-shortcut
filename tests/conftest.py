"""Pytest configuration and test environment setup."""

import sys
import os

# Ensure the scripts directory is on sys.path for module imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, 'scripts')
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
