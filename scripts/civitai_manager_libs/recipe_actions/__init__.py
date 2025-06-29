"""
Recipe Actions Package

This package contains the refactored recipe management modules split from
the original recipe_action.py file following the design plan in issue #39.

Modules according to design plan:
- recipe_management: Recipe management logic (~400 lines)
- recipe_browser: Recipe browsing functionality (~300 lines)
- recipe_reference: Reference related functionality (~300 lines)
- recipe_gallery: Gallery integration functionality (~200 lines)
- recipe_utilities: Recipe utility functions (~200 lines)
"""

# Import all migrated functions for backward compatibility
from .recipe_management import (
    on_recipe_new_btn_click,
    on_recipe_create_btn_click,
    on_recipe_update_btn_click,
    on_recipe_delete_btn_click,
    get_recipe_information,
    on_refresh_recipe_change,
)

from .recipe_browser import (
    on_recipe_input_change,
    on_recipe_drop_image_upload,
    on_recipe_generate_data_change,
    on_recipe_gallery_select,
    on_recipe_prompt_tabs_select,
)

from .recipe_reference import (
    load_model_information,
    on_reference_modelid_change,
    on_reference_versions_select,
    on_delete_reference_model_btn_click,
    on_close_reference_model_information_btn_click,
    on_reference_gallery_loading,
    on_reference_sc_gallery_select,
    on_reference_gallery_select,
)

from .recipe_utilities import (
    add_string,
    remove_strings,
    is_string,
    on_insert_prompt_btn_click,
    analyze_prompt,
    generate_prompt,
)

__all__ = [
    # Recipe management
    'on_recipe_new_btn_click',
    'on_recipe_create_btn_click',
    'on_recipe_update_btn_click',
    'on_recipe_delete_btn_click',
    'get_recipe_information',
    'on_refresh_recipe_change',
    
    # Recipe browser
    'on_recipe_input_change',
    'on_recipe_drop_image_upload',
    'on_recipe_generate_data_change',
    'on_recipe_gallery_select',
    'on_recipe_prompt_tabs_select',
    
    # Recipe reference
    'load_model_information',
    'on_reference_modelid_change',
    'on_reference_versions_select',
    'on_delete_reference_model_btn_click',
    'on_close_reference_model_information_btn_click',
    'on_reference_gallery_loading',
    'on_reference_sc_gallery_select',
    'on_reference_gallery_select',
    
    # Recipe utilities
    'add_string',
    'remove_strings',
    'is_string',
    'on_insert_prompt_btn_click',
    'analyze_prompt',
    'generate_prompt',
]
