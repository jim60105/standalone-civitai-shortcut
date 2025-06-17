"""
Fallback path configuration for compatibility layer.

This module provides fallback paths when WebUI modules are not available.
"""

import os
from pathlib import Path

# Calculate script path - go up to find the main script directory
current_file = os.path.dirname(os.path.realpath(__file__))
# From: scripts/civitai_manager_libs/compat/paths.py
# Go up: compat -> civitai_manager_libs -> scripts -> project_root
script_path = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

# Set up standard paths following AUTOMATIC1111 WebUI conventions
data_path = os.path.join(script_path, "data")
models_path = os.path.join(data_path, "models")

# Convert to Path objects for convenience
script_path = Path(script_path)
data_path = Path(data_path)
models_path = Path(models_path)
