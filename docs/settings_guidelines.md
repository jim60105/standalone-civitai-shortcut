# Settings System Guidelines

This document provides guidelines for developers working with the Civitai Shortcut settings system.

## Architecture Overview

The settings system follows a modular design with clear separation of concerns:

```
SettingCategories (SRP) → ConfigManager (Coordinator) → SettingPersistence (Storage)
       ↑                         ↓
SettingValidator (Validation)
```

## Core Components

### SettingCategories (`setting_categories.py`)
**Single Responsibility**: Defines all settings categories, types, defaults, and mappings.

- **Categories**: UI, Download, API, Scanning, Application
- **Data Types**: string, integer, boolean
- **Default Values**: Centralized in `_CATEGORY_DEFAULTS`
- **Config Mapping**: Maps logical categories to config file structure
- **Validation Ranges**: Defines min/max values for numeric settings
- **Backward Compatibility**: Provides all methods previously available through SettingDefaults

### ConfigManager (`config_manager.py`)
**Single Responsibility**: Coordinates between all settings components.

- Loads/saves settings using SettingPersistence
- Validates settings using SettingValidator
- Provides unified access to settings with fallback to defaults
- Handles nested settings lookup

### SettingPersistence (`setting_persistence.py`)
**Single Responsibility**: Handles file I/O operations for settings.

- JSON serialization/deserialization
- Backup and restore functionality
- Atomic writes with temporary files
- Error handling for file operations

### SettingValidator (`setting_validation.py`)
**Single Responsibility**: Validates setting values.

- Uses SettingCategories for validation rules
- Path validation for directory settings
- Range validation for numeric settings
- Type validation

## Usage Guidelines

### Adding New Settings

1. **Define in SettingCategories**:
```python
# Add to appropriate category
DOWNLOAD_SETTINGS = {
    'new_download_setting': 'integer',  # Define type
}

# Add default value
_CATEGORY_DEFAULTS = {
    'download': {
        'new_download_setting': 10,  # Add default
    }
}

# Add validation range if needed
def get_validation_range(cls, key: str) -> tuple:
    validation_ranges = {
        'new_download_setting': (1, 100),  # min, max
    }
```

2. **Validation is automatic** - handled by SettingValidator
3. **No changes needed** in other files (DRY principle)

### Reading Settings

```python
from scripts.civitai_manager_libs.settings import config_manager

# Get a setting (with automatic fallback to default)
value = config_manager.get_setting('shortcut_column')

# Get with custom default
value = config_manager.get_setting('custom_setting', 'default_value')
```

### Writing Settings

```python
# Set a single setting (includes validation)
success = config_manager.set_setting('shortcut_column', 6)

# Update multiple settings
updates = {'shortcut_column': 6, 'gallery_column': 8}
validated = config_manager.update_settings(updates)
```

### Category-based Operations

```python
from scripts.civitai_manager_libs.settings.setting_categories import SettingCategories

# Get all UI settings
ui_settings = SettingCategories.get_category_settings('ui')

# Get defaults for a category
ui_defaults = SettingCategories.get_category_defaults('ui')

# Get all default values
all_defaults = SettingCategories.get_all_defaults()

# Get a specific default value
default_value = SettingCategories.get_default_value('shortcut_column')

# Find which category a setting belongs to
category = SettingCategories.find_setting_category('shortcut_column')  # Returns 'ui'
```

## Design Principles Applied

### DRY (Don't Repeat Yourself)
- Settings definitions exist only in `SettingCategories`
- Other modules delegate to avoid duplication
- Validation rules auto-generated from categories

### KISS (Keep It Simple, Stupid)
- Each module has a single, clear responsibility
- Simple interfaces for common operations
- Minimal configuration required for basic use

### SRP (Single Responsibility Principle)
- `SettingCategories`: Defines settings structure
- `ConfigManager`: Coordinates operations
- `SettingPersistence`: Handles file I/O
- `SettingValidator`: Validates values

## Configuration File Structure

Settings are stored in nested JSON structure:

```json
{
  "application_allow": {
    "download_timeout": 600,
    "http_timeout": 60
  },
  "image_style": {
    "shortcut_column": 5,
    "gallery_column": 7
  },
  "screen_style": {
    "gallery_thumbnail_image_style": "scale-down"
  },
  "NSFW_filter": {
    "nsfw_filter_enable": true,
    "nsfw_level": "None"
  }
}
```

## Best Practices

### For Developers

1. **Always use SettingCategories** for new settings definitions
2. **Use ConfigManager** for all settings operations
3. **Don't hardcode** validation ranges - use `get_validation_range()`
4. **Follow naming conventions** - use snake_case for setting keys
5. **Test with fallbacks** - ensure code works when settings are missing

### For Settings Structure

1. **Group related settings** in appropriate categories
2. **Choose descriptive names** that indicate purpose
3. **Define sensible defaults** that work out-of-the-box
4. **Use appropriate data types** (string, integer, boolean)
5. **Document validation ranges** for numeric settings

## Error Handling

The settings system includes comprehensive error handling:

- **File operations**: Automatic backup/restore on errors
- **JSON parsing**: Graceful degradation to defaults
- **Validation**: Clear error messages with valid ranges
- **Missing settings**: Automatic fallback to defaults

## Testing

When writing tests for settings:

```python
def test_setting_operations():
    # Use a test config file
    test_config = ConfigManager(config_file='test_settings.json')
    
    # Test with known values
    assert test_config.set_setting('shortcut_column', 5)
    assert test_config.get_setting('shortcut_column') == 5
    
    # Test validation
    assert not test_config.set_setting('shortcut_column', 99)  # Out of range
```

## Migration

When changing settings structure:

1. Update `SettingCategories` definitions
2. Add migration logic in `SettingPersistence.migrate_settings()`
3. Maintain backward compatibility in `get_setting()`
4. Update documentation and tests

This modular design ensures the settings system remains maintainable, testable, and extensible while following solid software engineering principles.
