# Civitai Shortcut Project Instructions

* **Role:** Act as a technical expert responsible for both development and code review, with specialization in Python-based WebUI extensions and standalone application architecture.

* **Core References:** `README.md`, `docs/testing_guidelines.md`, `docs/architecture_overview.md`

* **Response Language:** `zh-TW 正體中文`

* **Key Directives:**

  * Maintain the highest standard of quality in all deliverables following Python PEP 8 standards.
  * All code comments and documentation must be written in **English** as per project conventions.
  * Use `snake_case` for function names, `PascalCase` for class names, and `UPPER_CASE` for constants.
  * Proactively consult both core documentation and conversation history to ensure accurate comprehension of all requirements.
  * The use of @deprecated is prohibited. Whenever you want to use @deprecated, simply remove it and directly modify any place where it is used.
  * Instead of concentrating on backward compatibility, greater importance is given to removing unnecessary designs. When a module is no longer utilized, remove it. DRY (Don't Repeat Yourself) and KISS (Keep It Simple, Stupid) principles are paramount.
  * Any unimplemented code must be marked with `//TODO` comment.
  * Unless the requirements document asks you to implement in phases, using TODO is prohibited. TODO means there is still unfinished work. You are required to complete your work.
  * Use `pytest` for running tests and makesure this project is testable.
  * Follow the testing principles and practices outlined in `docs/testing_guidelines.md`.
  * Always use `util.printD()` for structured debug output with module identifiers.
  * Ensure compatibility with both AUTOMATIC1111 WebUI extension mode and standalone execution mode.
  * You are neither able to execute `docker` commands nor actually test with AUTOMATIC1111 Stable Diffusion WebUI. Verify your code changes by running unit tests and integration tests in a local Python environment. Ensure that all tests pass successfully before finalizing your report.
  * Always `black --line-length=100 --skip-string-normalization` and `flake8` the submitting files and fix any warnings before submitting any code. Do not lint the whole project, only the files you are submitting. Use the `.flake8` configuration file in the root directory for linting. Fix not only the errors but also styling warnings.
  * Write a report following `.github/reports/README.md` and `.github/reports/REPORT_TEMPLATE.md`. Commit your report file together with the code changes, using the templates provided in `.github/reports/`.
  * When doing Git commit, use the conventional commit format for the title and a brief description in the body. Always commit with `--signoff --no-gpg-sign` and explicitly specify the author on the command: `🤖 GitHub Copilot <github-copilot[bot]@users.noreply.github.com>`. Write the commit in English.

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
    ├── prompt.py               # Prompt handling logic
    ├── downloader.py           # File download management
    ├── util.py                 # Utility functions
    ├── *_action.py             # UI event handlers
    ├── *_browser_page.py       # Browser page components
    ├── prompt_ui.py            # Prompt UI components
    └── compat/                 # Compatibility layer
        ├── __init__.py
        ├── compat_layer.py     # Main compatibility layer
        ├── environment_detector.py  # Environment detection
        ├── interfaces/         # Abstract interfaces
        │   ├── iconfig_manager.py
        │   ├── imetadata_processor.py
        │   ├── iparameter_processor.py
        │   ├── ipath_manager.py
        │   ├── isampler_provider.py
        │   └── iui_bridge.py
        ├── standalone_adapters/  # Standalone mode adapters
        │   ├── standalone_config_manager.py
        │   ├── standalone_metadata_processor.py
        │   ├── standalone_parameter_processor.py
        │   ├── standalone_path_manager.py
        │   ├── standalone_sampler_provider.py
        │   └── standalone_ui_bridge.py
        └── webui_adapters/     # WebUI mode adapters
            ├── webui_config_manager.py
            ├── webui_metadata_processor.py
            ├── webui_parameter_processor.py
            ├── webui_path_manager.py
            ├── webui_sampler_provider.py
            └── webui_ui_bridge.py

docs/                          # Documentation
├── architecture_overview.md  # System architecture
├── interface_specifications.md  # API specifications
├── testing_guidelines.md     # Testing standards
└── usage_examples.md         # Usage examples

tests/                        # Test suite
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

