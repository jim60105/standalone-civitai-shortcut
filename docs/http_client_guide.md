# HTTP Client Guide

This guide provides instructions on how to use the modular HTTP client for Civitai API integration. The HTTP client has been refactored into focused submodules following Single Responsibility Principle (SRP) while maintaining complete backward compatibility.

## Module Structure

The HTTP functionality is now organized into specialized modules:

- **`http/client.py`** - Core HTTP client with authentication and error handling
- **`http/file_downloader.py`** - File download capabilities with resume and progress tracking  
- **`http/image_downloader.py`** - Parallel image downloading with thread safety
- **`http/client_manager.py`** - Global client instance management

## Quick Start

### Basic Usage

```python
# New modular import (recommended)
from civitai_manager_libs.http import get_http_client

# Backward compatible import (still works)
from civitai_manager_libs.http_client import get_http_client

# Get the global client instance (preferred approach)
client = get_http_client()

# Send GET request
data = client.get_json("https://civitai.com/api/v1/models/12345")
if data:
    print(f"Model name: {data['name']}")
```

### Custom Client Configuration

```python
from civitai_manager_libs.http import CivitaiHttpClient

# Create custom client instance
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
# Using the global client (recommended)
from civitai_manager_libs.http import get_http_client

client = get_http_client()

# Basic file download
success = client.download_file(
    url="https://civitai.com/path/to/file",
    filepath="./downloads/model.safetensors"
)

if success:
    print("Download completed!")
else:
    print("Download failed!")

# Download with resume capability
success = client.download_file_with_resume(
    url="https://civitai.com/path/to/large_file",
    filepath="./downloads/large_model.safetensors"
)
```

### Parallel Image Download

```python
from civitai_manager_libs.http import ParallelImageDownloader

# Download multiple images in parallel
downloader = ParallelImageDownloader(max_workers=10)
image_tasks = [
    ("https://civitai.com/image1.jpg", "./downloads/image1.jpg"),
    ("https://civitai.com/image2.jpg", "./downloads/image2.jpg"),
    ("https://civitai.com/image3.jpg", "./downloads/image3.jpg"),
]

def progress_callback(done, total, desc):
    print(f"Progress: {done}/{total} - {desc}")

success_count = downloader.download_images(image_tasks, progress_callback)
print(f"Downloaded {success_count} images successfully")
```

### Progress Tracking

```python
def progress_callback(downloaded: int, total: int, speed: str = ""):
    if total > 0:
        percentage = (downloaded / total) * 100
        print(f"Progress: {percentage:.1f}% ({speed})")
    else:
        print(f"Downloaded: {downloaded} bytes ({speed})")

client = get_http_client()
success = client.download_file_with_resume(
    url="https://civitai.com/path/to/large_file",
    filepath="./downloads/large_model.safetensors",
    progress_callback=progress_callback
)
```

## Module Architecture

### Core HTTP Client (`http/client.py`)

The core HTTP client provides the fundamental API interaction capabilities:

```python
from civitai_manager_libs.http.client import CivitaiHttpClient

client = CivitaiHttpClient(api_key="your_key")

# GET requests with JSON response
data = client.get_json(url, params={"limit": 20})

# POST requests with JSON payload
response = client.post_json(url, json_data={"query": "search"})

# Streaming downloads
response = client.get_stream(url, headers={"Range": "bytes=0-1023"})
```

### File Download Mixin (`http/file_downloader.py`)

File download capabilities are provided through a mixin pattern:

```python
# The FileDownloadMixin is automatically included in the complete client
client = get_http_client()  # Returns CompleteCivitaiHttpClient

# Basic download
client.download_file(url, filepath)

# Download with resume
client.download_file_with_resume(url, filepath, progress_callback, headers)
```

### Image Downloader (`http/image_downloader.py`)

Specialized parallel image downloading:

```python
from civitai_manager_libs.http.image_downloader import ParallelImageDownloader

downloader = ParallelImageDownloader(max_workers=5)
success_count = downloader.download_images(
    image_tasks=[(url1, path1), (url2, path2)],
    progress_callback=callback_func,
    client=custom_client  # Optional, uses global client if not provided
)
```

### Client Manager (`http/client_manager.py`)

Global instance management with automatic configuration updates:

```python
from civitai_manager_libs.http.client_manager import get_http_client

# Get the singleton instance
client = get_http_client()

# Client configuration is automatically updated from settings
# No manual client recreation needed when settings change
```

## Advanced Features

### Modular Import Patterns

The refactored HTTP system supports multiple import patterns for different use cases:

```python
# Global client approach (recommended for most cases)
from civitai_manager_libs.http import get_http_client
client = get_http_client()

# Direct module imports for specific functionality
from civitai_manager_libs.http.client import CivitaiHttpClient
from civitai_manager_libs.http.image_downloader import ParallelImageDownloader
from civitai_manager_libs.http.client_manager import CompleteCivitaiHttpClient

# Backward compatible imports (still supported)
from civitai_manager_libs.http_client import get_http_client, ParallelImageDownloader
```

### Custom Configuration

The HTTP client supports both global and instance-specific configuration:

```python
# Global configuration via settings
# These are automatically applied to the global client instance
import civitai_manager_libs.settings as settings
settings.http_timeout = 60
settings.http_max_retries = 5
settings.http_retry_delay = 10

# Custom client instance
from civitai_manager_libs.http.client import CivitaiHttpClient
custom_client = CivitaiHttpClient(
    api_key="different_key",
    timeout=30,
    max_retries=3,
    retry_delay=2.0
)
```

### Authentication Management

```python
client = get_http_client()

# Update API key dynamically
client.update_api_key("new_api_key")

# The client automatically includes Bearer token authentication
# for requests that require it
```

### Error Handling and Recovery

The modular HTTP client provides sophisticated error handling:

```python
from civitai_manager_libs.exceptions import (
    AuthenticationError, NetworkError, HTTPError, TimeoutError
)

try:
    data = client.get_json("https://civitai.com/api/v1/models/12345")
except AuthenticationError:
    print("Invalid or expired API key")
except NetworkError:
    print("Network connectivity issue")
except HTTPError as e:
    print(f"HTTP error {e.status_code}: {e.message}")
except TimeoutError:
    print("Request timed out")
```

## Backward Compatibility

### Legacy Import Support

All existing imports continue to work without any code changes:

```python
# These imports still work exactly as before
from civitai_manager_libs.http_client import get_http_client, ParallelImageDownloader
from civitai_manager_libs.downloader import DownloadManager, download_file

# The old module names are aliased to the new modular structure
import civitai_manager_libs.http_client as http_client
import civitai_manager_libs.downloader as downloader

client = http_client.get_http_client()
manager = downloader.DownloadManager()
```

### API Compatibility

All existing method signatures and return values remain unchanged:

```python
# All these continue to work exactly as before
client = get_http_client()
data = client.get_json(url)  # Same signature
success = client.download_file(url, path)  # Same signature
response = client.get_stream(url)  # Same signature
```

### Migration Path

While backward compatibility is maintained, new code should prefer the modular imports:

```python
# Old style (deprecated but still works)
from civitai_manager_libs.http_client import get_http_client

# New style (recommended)
from civitai_manager_libs.http import get_http_client

# The functionality is identical, but the new imports are clearer
# about the modular organization
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

### Recommended Usage Patterns

```python
# 1. Use the global client for most operations
from civitai_manager_libs.http import get_http_client
client = get_http_client()

# 2. Use specialized components for specific needs
from civitai_manager_libs.http import ParallelImageDownloader
downloader = ParallelImageDownloader(max_workers=8)

# 3. Prefer modular imports for new code
from civitai_manager_libs.http.client import CivitaiHttpClient
from civitai_manager_libs.download import DownloadManager

# 4. Handle errors appropriately
from civitai_manager_libs.error_handler import with_error_handling

@with_error_handling(
    fallback_value=None,
    exception_types=(NetworkError, HTTPError),
    retry_count=3,
    user_message="Failed to fetch model data"
)
def fetch_model_data(model_id):
    client = get_http_client()
    return client.get_json(f"https://civitai.com/api/v1/models/{model_id}")
```

### Performance Optimization

- **Reuse the global client instance** - No need to create multiple instances
- **Configure appropriate timeouts** - Balance responsiveness with reliability
- **Use parallel downloads** - For multiple images or files
- **Enable resume capability** - For large file downloads
- **Monitor progress** - Provide user feedback for long operations

### Error Handling Strategy

- **Use the error handler decorator** - For automatic retry and user feedback
- **Handle specific exception types** - Different recovery strategies for different errors
- **Provide meaningful fallbacks** - Graceful degradation when operations fail
- **Log errors appropriately** - For debugging and monitoring

## Module Benefits

The refactored HTTP system provides several advantages:

### Single Responsibility Principle
- **`client.py`**: Core HTTP operations and authentication
- **`file_downloader.py`**: File download logic with resume capability
- **`image_downloader.py`**: Parallel image processing
- **`client_manager.py`**: Instance management and configuration

### Improved Testability
- Each module can be tested in isolation
- Easier to mock specific functionality
- Better test coverage and reliability

### Enhanced Maintainability
- Clear separation of concerns
- Focused modules with specific responsibilities
- Easier to debug and modify individual components

### Better Performance
- Optimized parallel processing for images
- Intelligent resume capability for large files
- Connection pooling and resource management

### Future Extensibility
- Easy to add new download strategies
- Pluggable authentication mechanisms
- Support for additional protocols or services

## Troubleshooting

- Ensure your API key is valid and has not exceeded rate limits
- Adjust timeout and retry settings if experiencing frequent timeouts
- Verify filesystem permissions and available disk space when downloading files
