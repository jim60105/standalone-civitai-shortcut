"""Fallback path configuration for compatibility layer.

This module provides fallback paths when WebUI modules are not available.
"""

import os
from pathlib import Path

# Calculate script path - go up to find the main script directory
current_file = os.path.dirname(os.path.realpath(__file__))
# From: scripts/civitai_manager_libs/compat/paths.py
# Go up: compat -> civitai_manager_libs -> scripts -> project_root
script_path_str = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

# Set up standard paths following AUTOMATIC1111 WebUI conventions
data_path_str = os.path.join(script_path_str, "data")
models_path_str = os.path.join(data_path_str, "models")

# Convert to Path objects for convenience
script_path = Path(script_path_str)
data_path = Path(data_path_str)
models_path = Path(models_path_str)
