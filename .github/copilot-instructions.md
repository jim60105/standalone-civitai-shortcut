# Civitai Shortcut - GitHub Copilot Instructions

## Project Overview

This repository contains a custom script extension purpose-built for the [AUTOMATIC1111 Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui). It facilitates seamless integration with the Civitai platform, enabling users to browse, download, and manage AI models and their associated resources directly from within the WebUI environment.

### Key Features

* **Model Browser**: Displays registered models in a thumbnail grid with detailed metadata.
* **Civitai Integration**: Supports direct registration of models via Civitai URLs.
* **Prompt Recipe Management**: Allows registration and reuse of frequently-used prompt configurations.
* **Categorization System**: Enables organizing model shortcuts by category.
* **Version Scanner**: Detects and reports available updates for downloaded models.
* **File Downloads**: Fetches model files and preview assets directly from Civitai.

## Coding Conventions and Style

### Python Code Standards

* All code comments must be written in **English**.
* Documentation and user interface text are authored in **English**.
* Function names follow the `snake_case` convention.
* Class names follow `PascalCase`.
* Constants use `UPPER_CASE`.

### File Organization

```
scripts/
├── civitai_shortcut.py          # Primary entry point
└── civitai_manager_libs/        # Core utility modules
    ├── __init__.py
    ├── civitai.py              # Civitai API integration logic
    ├── setting.py              # Configuration management
    ├── model.py                # Model data handling
    ├── ishortcut.py            # Shortcut logic
    ├── classification.py       # Category structure
    ├── recipe.py               # Prompt recipe management
    ├── util.py                 # Utility functions
    └── *_action.py             # UI event handlers
```

### Gradio UI Guidelines

* The UI is constructed using Gradio v3.41.2 or higher.
* Components are named descriptively; abbreviations are discouraged.
* Interface layout is organized using `gr.Tabs()` and `gr.TabItem()`.
* Event bindings use `.click()`, `.change()`, `.select()`, etc.
* `gr.State()` is used for cross-component state management.

### Data Handling Patterns

* JSON files are used for configuration and persistence.
* Complex relationships are managed using Python dictionaries.
* Model metadata is fetched via the Civitai API and locally cached.
* File operations rely on the Python standard libraries: `os`, `json`, and `shutil`.

## Special Considerations

### Integration with AUTOMATIC1111 WebUI

* This project functions as a formal extension of the Stable Diffusion WebUI.
* All development adheres to WebUI extension guidelines.
* The `modules` package is utilized to interact with WebUI internals.
* Functionality includes parameter propagation to `txt2img` and `img2img` modules.

### Civitai API Usage

* Implements full integration with the Civitai RESTful API.
* Supports fetching model, version, and preview asset data.
* Includes mechanisms for handling rate limits and API failure modes.
* Offers offline fallback capabilities.

### Internationalization

* Interfaces support both English and Korean languages.
* Configuration files and user data use English key identifiers.
* All error messages and debugging output are presented in English.

### Performance Optimization

* Pagination mechanisms are employed to reduce memory overhead.
* Long-running tasks are delegated to background threads.
* Caching is used to minimize redundant API calls.
* Thumbnail generation and caching are optimized for responsiveness.

## Development Principles

1. **Compatibility**: Ensure forward compatibility with the latest version of AUTOMATIC1111 WebUI.
2. **Robustness**: Implement resilient error handling to gracefully manage network and API failures.
3. **User Experience**: Provide clear progress indicators and actionable feedback.
4. **Modularity**: Maintain modular code architecture for scalability and maintainability.
5. **Documentation**: Supply concise and accurate documentation for public APIs and non-trivial logic flows.

## Debugging and Logging

* Use `util.printD()` for structured debug output.
* All debug messages should be prefixed with module identifiers.
* Network failures must yield detailed error diagnostics.
* File I/O exceptions should include full path context in logs.

---

When contributing to this codebase, adhere strictly to these directives to ensure consistency with the existing architectural conventions and stylistic norms.

