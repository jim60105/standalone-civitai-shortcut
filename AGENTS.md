# Civitai Shortcut Project Instructions

* **Project:** Civitai Shortcut - An intelligent extension for AUTOMATIC1111 Stable Diffusion WebUI that facilitates seamless integration with the Civitai platform for model browsing, downloading, and management.

* **Role:** Act as a technical expert responsible for development, with specialization in Python-based WebUI extensions and standalone application architecture.

* **Core References:** `README.md`, `.github/copilot-instructions.md`, `scripts/civitai_shortcut.py`

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
  * Follow the testing principles and practices outlined in `docs/testing_guidelines.md`.
  * Always use `util.printD()` for structured debug output with module identifiers.
  * Ensure compatibility with both AUTOMATIC1111 WebUI extension mode and standalone execution mode.
  * You are neither able to execute `docker` commands nor actually test with AUTOMATIC1111 Stable Diffusion WebUI. Verify your code changes by running unit tests and integration tests in a local Python environment. Ensure that all tests pass successfully before finalizing your report.
  * Always `black` and `flake8` the submitting files and fix any warnings before submitting any code. Do not lint the whole project, only the files you are submitting. Use the `.flake8` configuration file in the root directory for linting.
  * Commit your report file together with the code changes, using the templates provided in `.github/reports/`.
  * Git commit after completing your work, using the conventional commit format for the title and a brief description in the body. Always commit with `--signoff` and `--no-gpg-sign`. Write the commit in English.

---

# Detailed Guidelines for Product Backlogs

Each product backlog entry encapsulates the complete technical design and implementation blueprint for transitioning from WebUI-dependent extension to dual-mode (WebUI + Standalone) application:

1. **[Dependency Analysis and Mapping](.github/plans/civitai-shortcut-independent-execution-development-plan/backlogs/001-dependency-analysis-and-mapping.md)**

   * Complete analysis of AUTOMATIC1111 WebUI dependencies and creation of functionality mapping table

2. **[Abstract Interface Design](.github/plans/civitai-shortcut-independent-execution-development-plan/backlogs/002-abstract-interface-design.md)**

   * Design and implementation of compatibility layer architecture for dual-mode execution

3. **[WebUI Function Simulation](.github/plans/civitai-shortcut-independent-execution-development-plan/backlogs/003-webui-function-simulation.md)**

   * Implementation of WebUI-equivalent functionality for standalone mode operation

4. **[Standalone Entry Point](.github/plans/civitai-shortcut-independent-execution-development-plan/backlogs/004-standalone-entry-point.md)**

   * Development of independent application entry point and command-line interface

5. **[Module Dependency Modification](.github/plans/civitai-shortcut-independent-execution-development-plan/backlogs/005-module-dependency-modification.md)**

   * Refactoring existing modules to utilize the new compatibility layer architecture

6. **[UI Components Dual-Mode Adaptation](.github/plans/civitai-shortcut-independent-execution-development-plan/backlogs/006-ui-components-dual-mode-adaptation.md)**

   * Adaptation of all Gradio UI components for both WebUI integration and standalone execution

7. **[Testing and Quality Assurance](.github/plans/civitai-shortcut-independent-execution-development-plan/backlogs/007-testing-and-quality-assurance.md)**

   * Comprehensive testing framework for both execution modes and quality validation

8. **[Deployment and Distribution Preparation](.github/plans/civitai-shortcut-independent-execution-development-plan/backlogs/008-deployment-and-distribution-preparation.md)**

   * Docker containerization, CI/CD pipeline setup, and distribution package preparation

9. **[Documentation and User Guide](.github/plans/civitai-shortcut-independent-execution-development-plan/backlogs/009-documentation-and-user-guide.md)**

   * Docker deployment documentation and comprehensive user guides for both execution modes

# Work Report Protocol

Development progress for this project is systematically tracked within the `.github/reports` directory. Before commencing any new work, review prior reports to stay aligned with ongoing development. Treat all past reports as immutable references—do not edit or revise them under any circumstance. Upon the completion of each task, you are required to generate a new comprehensive work report. Refer to the naming conventions of existing files to determine an appropriate filename.

Your report must include a detailed account of the work performed, encompassing all relevant code modifications and corresponding test outcomes.

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
