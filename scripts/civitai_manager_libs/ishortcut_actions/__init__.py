"""
IShortcut Actions Package

This package contains the refactored UI event handling modules split from
the original ishortcut_action.py file following the design plan in issue #39.

Modules according to design plan:
- model_info_actions: Model information related operations (~300 lines)
- download_actions: Download related operations (~400 lines)
- file_management_actions: File management operations (~300 lines)
- gallery_actions: Gallery related operations (~300 lines)
- recipe_integration: Recipe integration functionality (~200 lines)
- utility_actions: Utility functions (~200 lines)
"""

# Import all migrated functions for backward compatibility
from .model_info_actions import (
    on_load_saved_model,
    on_update_information_btn_click,
    on_model_classification_update_btn_click,
    on_versions_list_select,
    load_saved_model,
    on_personal_note_save_click,
)

from .download_actions import (
    on_download_model_click,
    on_download_images_click,
    on_file_gallery_loading,
)

from .file_management_actions import (
    on_change_filename_submit,
    on_downloadable_files_select,
    on_cs_foldername_select,
    on_open_folder_click,
    on_open_image_folder_click,
    on_change_thumbnail_image_click,
    on_change_preview_image_click,
)

from .gallery_actions import (
    on_gallery_select,
    on_civitai_hidden_change,
)

from .recipe_integration import (
    on_send_to_recipe_click,
)

from .utility_actions import (
    upload_shortcut_by_files,
    upload_shortcut_by_urls,
    scan_downloadedmodel_to_shortcut,
    on_shortcut_del_btn_click,
    _create_send_to_buttons,
    _bind_send_to_buttons,
    set_compatibility_layer,
)

__all__ = [
    # Model info actions
    'on_load_saved_model',
    'on_update_information_btn_click',
    'on_model_classification_update_btn_click',
    'on_versions_list_select',
    'load_saved_model',
    'on_personal_note_save_click',
    
    # Download actions
    'on_download_model_click',
    'on_download_images_click',
    'on_file_gallery_loading',
    
    # File management actions
    'on_change_filename_submit',
    'on_downloadable_files_select',
    'on_cs_foldername_select',
    'on_open_folder_click',
    'on_open_image_folder_click',
    'on_change_thumbnail_image_click',
    'on_change_preview_image_click',
    
    # Gallery actions
    'on_gallery_select',
    'on_civitai_hidden_change',
    
    # Recipe integration
    'on_send_to_recipe_click',
    
    # Utility actions
    'upload_shortcut_by_files',
    'upload_shortcut_by_urls',
    'scan_downloadedmodel_to_shortcut',
    'on_shortcut_del_btn_click',
    '_create_send_to_buttons',
    '_bind_send_to_buttons',
    'set_compatibility_layer',
]
