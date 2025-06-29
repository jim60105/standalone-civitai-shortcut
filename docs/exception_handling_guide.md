# Exception Handling Guide

This document provides a comprehensive guide on how to use the unified exception handling framework introduced in PR #43.

## Overview

The unified exception handling framework provides a consistent way to handle errors across the entire Civitai Shortcut application. It includes custom exception types, a unified error handling decorator, and recovery mechanisms.

## Core Components

### 1. Custom Exception Types (`exceptions.py`)

The framework defines a hierarchy of custom exceptions for better error categorization:

```python
from scripts.civitai_manager_libs.exceptions import (
    CivitaiShortcutError,    # Base exception
    NetworkError,            # Network/API related errors
    FileOperationError,      # File I/O errors
    ConfigurationError,      # Configuration issues
    ValidationError,         # Data validation errors
    APIError,               # Civitai API specific errors
)
```

#### Exception Hierarchy

```
CivitaiShortcutError (Base)
├── NetworkError
│   └── APIError
├── FileOperationError
├── ConfigurationError
└── ValidationError
```

#### Exception Properties

All custom exceptions include:
- `message`: Error description
- `context`: Additional context information (dict)
- `cause`: Original exception that caused this error
- `timestamp`: When the error occurred

**APIError** additionally includes:
- `status_code`: HTTP status code for API errors

### 2. Error Handling Decorator (`error_handler.py`)

The `@with_error_handling` decorator provides unified error handling with retry logic and user feedback.

#### Basic Usage

```python
from scripts.civitai_manager_libs.error_handler import with_error_handling
from scripts.civitai_manager_libs.exceptions import NetworkError, FileOperationError

@with_error_handling(
    fallback_value=None,
    exception_types=(NetworkError, FileOperationError),
    retry_count=2,
    retry_delay=1.0,
    user_message="Failed to process request"
)
def my_function():
    # Your function logic here
    pass
```

#### Decorator Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fallback_value` | Any | `None` | Value to return when all retries fail |
| `exception_types` | tuple | `(Exception,)` | Exception types to catch and handle |
| `retry_count` | int | `0` | Number of retries before giving up |
| `retry_delay` | float | `1.0` | Delay between retries in seconds |
| `log_errors` | bool | `True` | Whether to log errors |
| `user_message` | str | `None` | Custom message to show to users |

#### Special Error Handling

The decorator provides special handling for:

1. **Cloudflare 524 Errors**: Shows the full error message instead of just the exception type
2. **General Errors**: Shows the exception class name for user-friendly feedback
3. **UI Integration**: Automatically displays errors using `gr.Error()` in Gradio UI

## Usage Patterns

### 1. Simple Function Protection

For basic error handling without retries:

```python
@with_error_handling(
    fallback_value=False,
    exception_types=(FileOperationError,),
    user_message="Failed to save file"
)
def save_data(data, filepath):
    with open(filepath, 'w') as f:
        json.dump(data, f)
    return True
```

### 2. Network Operations with Retry

For network operations that might fail temporarily:

```python
@with_error_handling(
    fallback_value=None,
    exception_types=(NetworkError, APIError),
    retry_count=3,
    retry_delay=2.0,
    user_message="Failed to fetch data from API"
)
def fetch_model_info(model_id):
    response = requests.get(f"https://api.civitai.com/v1/models/{model_id}")
    return response.json()
```

### 3. UI Event Handlers

For Gradio UI event handlers that need user feedback:

```python
@with_error_handling(
    fallback_value=gr.update(visible=False),
    exception_types=(ValidationError, FileOperationError),
    user_message="Failed to process selection"
)
def on_gallery_select(evt: gr.SelectData, images):
    selected_image = images[evt.index]
    # Process selection
    return gr.update(visible=True)
```

### 4. Complex Operations with Multiple Exception Types

For operations that can fail in multiple ways:

```python
@with_error_handling(
    fallback_value=(None, None, None),
    exception_types=(NetworkError, FileOperationError, ValidationError),
    retry_count=1,
    user_message="Failed to load model information"
)
def load_model_information(model_id):
    # Network call
    model_data = fetch_model_info(model_id)
    
    # File operation
    save_model_cache(model_data)
    
    # Data validation
    validate_model_data(model_data)
    
    return model_data, model_data['name'], model_data['version']
```

## Best Practices

### 1. Choose Appropriate Exception Types

Use specific exception types for better error categorization:

```python
# Good: Specific exception types
@with_error_handling(exception_types=(NetworkError, APIError))

# Avoid: Too generic
@with_error_handling(exception_types=(Exception,))
```

### 2. Provide Meaningful Fallback Values

Ensure fallback values maintain the expected return type:

```python
# Good: Maintains expected tuple structure
@with_error_handling(fallback_value=(None, None, None))
def get_model_info():
    return model_id, model_name, version_name

# Good: Maintains expected Gradio update
@with_error_handling(fallback_value=gr.update(visible=False))
def update_ui():
    return gr.update(visible=True, value="Success")
```

### 3. Use Appropriate Retry Strategies

- **Network operations**: 2-3 retries with increasing delay
- **File operations**: 1-2 retries with short delay
- **UI operations**: Usually no retries (0)

```python
# Network: Multiple retries
@with_error_handling(retry_count=3, retry_delay=2.0)

# File I/O: Few retries
@with_error_handling(retry_count=1, retry_delay=0.5)

# UI: No retries
@with_error_handling(retry_count=0)
```

### 4. Provide User-Friendly Messages

Write clear, actionable error messages:

```python
# Good: Clear and actionable
@with_error_handling(user_message="Failed to download image. Please check your internet connection.")

# Avoid: Too technical
@with_error_handling(user_message="HTTPConnectionPool(host='example.com', port=80): Max retries exceeded")
```

## Integration with Existing Code

### Gradio UI Components

The decorator automatically integrates with Gradio's error display system:

```python
import gradio as gr

@with_error_handling(user_message="Custom error message")
def button_click_handler():
    # Error will be shown in Gradio UI automatically
    raise ValueError("Something went wrong")
```

### Logging Integration

Errors are automatically logged with context information:

```python
# Automatic logging includes:
# - Function name
# - Module name
# - Error message
# - Exception details
```

### Recovery Integration

The decorator can be combined with recovery mechanisms:

```python
@with_error_handling(
    fallback_value=None,
    exception_types=(FileOperationError,),
    retry_count=1
)
def read_config_file(filepath):
    # If this fails, the decorator will:
    # 1. Log the error
    # 2. Retry if configured
    # 3. Return fallback value if all fails
    with open(filepath, 'r') as f:
        return json.load(f)
```

## Migration from Legacy Error Handling

### Before (Legacy)

```python
def old_function():
    try:
        result = some_operation()
        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        return None
```

### After (Unified Framework)

```python
@with_error_handling(
    fallback_value=None,
    exception_types=(NetworkError, FileOperationError),
    user_message="Operation failed"
)
def new_function():
    result = some_operation()
    return result
```

## Testing Error Handling

### Unit Testing

Test both success and failure scenarios:

```python
def test_function_success():
    result = my_decorated_function(valid_input)
    assert result is not None

def test_function_with_network_error(monkeypatch):
    # Mock to raise NetworkError
    monkeypatch.setattr('module.network_call', lambda: exec('raise NetworkError()'))
    
    result = my_decorated_function(valid_input)
    assert result is None  # fallback_value
```

### Error Injection

Use the test utilities to inject specific errors:

```python
from scripts.civitai_manager_libs.exceptions import APIError

def test_api_error_handling():
    with pytest.raises(APIError):
        # Test direct exception handling
        pass
```

## Performance Considerations

### Minimal Overhead

The decorator is designed with minimal performance impact:
- Exception handling only activates on errors
- Logging is conditional based on `log_errors` parameter
- Import statements are inside exception blocks to avoid import overhead

### Retry Strategy

Use retry strategies judiciously:
- Avoid excessive retry counts for operations that are unlikely to succeed on retry
- Use exponential backoff for network operations
- Consider the total timeout when setting retry parameters

## Troubleshooting

### Common Issues

1. **Decorator not working**: Ensure you're importing from the correct module
2. **Fallback value type mismatch**: Ensure fallback value matches expected return type
3. **Excessive retries**: Reduce retry count for operations that shouldn't be retried

### Debug Mode

Enable detailed logging to diagnose issues:

```python
@with_error_handling(log_errors=True)  # Default is True
```

### Error Context

Access error context for debugging:

```python
try:
    raise CivitaiShortcutError("Test error", context={"user_id": 123})
except CivitaiShortcutError as e:
    print(f"Error: {e}")
    print(f"Context: {e.context}")
    print(f"Timestamp: {e.timestamp}")
```
