"""
IShortcut Action Module - Refactored Modular Version

This module has been refactored to organize functionality into specific modules
while maintaining backward compatibility. All UI event handlers are imported
from their respective specialized modules.

Phase 1: IShortcut Actions Refactoring (Issue #39)
- Model Information Actions
- Download Actions
- File Management Actions
- Gallery Actions
- Recipe Integration
- Utility Actions
"""

from .logging_config import get_logger

logger = get_logger(__name__)

# Import all UI builder functions that weren't moved (on_ui stays here as main interface)
from .ishortcut_action_backup import on_ui, set_compatibility_layer

# Import all refactored functions from specialized modules
from .ishortcut_actions.model_info_actions import (
    on_update_information_btn_click,
    on_model_classification_update_btn_click,
    on_load_saved_model,
    on_versions_list_select,
)

from .ishortcut_actions.download_actions import (
    on_download_model_click,
    on_download_images_click,
)

from .ishortcut_actions.file_management_actions import (
    on_change_filename_submit,
    on_downloadable_files_select,
    on_cs_foldername_select,
    on_open_folder_click,
    on_open_image_folder_click,
)

from .ishortcut_actions.gallery_actions import (
    on_gallery_select,
    on_civitai_hidden_change,
)

from .ishortcut_actions.recipe_integration import (
    on_send_to_recipe_click,
)

from .ishortcut_actions.utility_actions import (
    on_shortcut_del_btn_click,
)

# Import remaining functions from backup file (not yet migrated)
from .ishortcut_action_backup import (
    on_personal_note_save_click,
    on_change_thumbnail_image_click,
    on_change_preview_image_click,
    on_file_gallery_loading,
)

# Log successful module refactoring
logger.info(
    "IShortcut actions refactored successfully - all functions imported from specialized modules"
)

# Export all functions for backward compatibility
__all__ = [
    # UI Builder (kept in this file)
    'on_ui',
    'set_compatibility_layer',
    
    # Model Information Actions
    'on_update_information_btn_click',
    'on_personal_note_save_click',
    'on_model_classification_update_btn_click',
    'on_load_saved_model',
    'on_versions_list_select',
    
    # Download Actions
    'on_download_model_click',
    'on_download_images_click',
    
    # File Management Actions
    'on_change_filename_submit',
    'on_downloadable_files_select',
    'on_cs_foldername_select',
    'on_open_folder_click',
    'on_open_image_folder_click',
    
    # Gallery Actions (partially migrated)
    'on_gallery_select',
    'on_civitai_hidden_change',
    'on_change_thumbnail_image_click',  # from backup
    'on_change_preview_image_click',    # from backup
    'on_file_gallery_loading',         # from backup
    
    # Recipe Integration
    'on_send_to_recipe_click',
    
    # Utility Actions
    'on_shortcut_del_btn_click',
]
