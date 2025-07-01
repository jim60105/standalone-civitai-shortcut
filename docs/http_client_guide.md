# HTTP Client Guide

This guide provides instructions on how to use the centralized HTTP client for Civitai API integration.

## Quick Start

### Basic Usage

```python
from civitai_manager_libs.http_client import CivitaiHttpClient

# Create client instance
client = CivitaiHttpClient(
    api_key="your_api_key",
    timeout=30,
    max_retries=3
)

# Send GET request
data = client.get_json("https://civitai.com/api/v1/models/12345")
if data:
    print(f"Model name: {data['name']}")
```

### File Download

```python
# Download file
success = client.download_file(
    url="https://civitai.com/path/to/file",
    filepath="./downloads/model.safetensors"
)

if success:
    print("Download completed!")
else:
    print("Download failed!")
```

### Progress Tracking

```python
def progress_callback(downloaded: int, total: int, speed: float):
    percentage = (downloaded / total * 100) if total > 0 else 0
    print(f"Progress: {percentage:.1f}% at {speed:.1f} KB/s")

client.download_file(
    url="https://civitai.com/path/to/large_file",
    filepath="./downloads/large_model.safetensors",
    progress_callback=progress_callback
)
```

## Advanced Features

### Custom Configuration

Adjust default settings in `setting.py`:

```python
# Timeout in seconds
http_timeout = 60
# Maximum retry attempts
http_max_retries = 5
# Delay between retries in seconds
http_retry_delay = 10
```

### Error Handling

```python
try:
    data = client.get_json("https://civitai.com/api/v1/models/invalid_id")
except Exception:
    # Client already handles and logs errors with user-friendly messages
    print("Failed to retrieve model data.")
```

## UI Decoupling and Error Handling

To improve separation of concerns and support multiple environments, the HTTP client no longer performs direct UI notifications. Instead, all HTTP errors are raised as custom exceptions and handled by the application layer via the `@with_error_handling` decorator and notification service.

### HTTP Client Exception Mapping

The client translates HTTP failures into structured exceptions:

```python
# scripts/civitai_manager_libs/http_client.py
try:
    response = self.session.get(url, timeout=self.timeout)
    response.raise_for_status()
except requests.RequestException as e:
    raise NetworkError(f"Request failed: {e}")
```

### Handling Errors with @with_error_handling

Use the unified error handling decorator to catch exceptions and display user-friendly messages without coupling to Gradio:

```python
from scripts.civitai_manager_libs.http_client import CivitaiHttpClient
from scripts.civitai_manager_libs.error_handler import with_error_handling
from scripts.civitai_manager_libs.exceptions import NetworkError, APIError

client = CivitaiHttpClient(api_key="...", timeout=30)

@with_error_handling(
    fallback_value=None,
    exception_types=(NetworkError, APIError),
    retry_count=3,
    user_message="Failed to fetch model data",
)
def get_model_data(model_id: int):
    return client.get_json(f"https://civitai.com/api/v1/models/{model_id}")
```

## Best Practices

- Reuse the same client instance for multiple requests
- Configure appropriate timeouts for different workloads
- Handle `None` return values instead of uncaught exceptions
- Use streaming or chunked downloads for large files

## Troubleshooting

- Ensure your API key is valid and has not exceeded rate limits
- Adjust timeout and retry settings if experiencing frequent timeouts
- Verify filesystem permissions and available disk space when downloading files
