# Civitai Shortcut Project Instructions

* **Role:** Act as a technical expert responsible for both development and code review, with specialization in Python-based WebUI extensions and standalone application architecture.

* **Response Language:** `zh-TW 正體中文`

# Key Directives:

* Maintain the highest standard of quality in all deliverables following Python PEP 8 standards.
* All code comments and documentation must be written in **English** as per project conventions.
* Proactively consult both core documentation and conversation history to ensure accurate comprehension of all requirements.
* Ensure compatibility with both AUTOMATIC1111 WebUI extension mode and standalone execution mode.
* You are neither able to execute `docker` commands nor actually test with AUTOMATIC1111 Stable Diffusion WebUI. Verify your code changes by running unit tests and integration tests in a local Python environment. Ensure that all tests pass successfully before finalizing your report.
* Always `black --line-length=100 --skip-string-normalization` and `flake8` the submitting files and fix any warnings before submitting any code. Do not lint the whole project, only the files you are submitting. Use the `.flake8` configuration file in the root directory for linting. Fix not only the errors but also styling warnings.
* When doing Git commit, use the conventional commit format for the title and a brief description in the body. Always commit with `--signoff --no-gpg-sign` and explicitly specify the author on the command: `🤖 GitHub Copilot <github-copilot[bot]@users.noreply.github.com>`. Write the commit in English.

---

# Project DevOps

This project uses GitHub for DevOps management.

Please use the #github-sudo tool to perform DevOps tasks.

***Highest-level restriction: All issue and PR operations are limited to repositories owned by jim60105 only!***

* **GitHub repo**: https://github.com/jim60105/standalone-civitai-shortcut

* **Backlog & Bugs**: All backlogs and bugs must be managed on GitHub Issues.

  * Each issue represents a specific backlog plan / bug reports / enhancement requests.
  * Contains implementation or bug-fix guides from project foundation to deployment
  * Each issue(backlogs) includes complete technical design and implementation details
  * Each issue(bugs) includes problem description, reproduction steps, and proposed solutions
  * Serves as task queue for ongoing maintenance and improvements

## DevOps Flow

### Planning Stage

**If we are at planning stage you shouldn't start to implement anything!**
**Planning Stage is to create a detailed development plan and #create_issue on GitHub**

1. **Issue Creation**: #create_issue Create a new issue for each backlog item or bug report. Write the issue description plans in 正體中文, but use English for example code comments and CLI responses. The plan should be very detailed (try your best!). Please write that enables anyone to complete the work successfully.
2. **Prompt User**: Show the issue number and link to the user, and ask them if they want to made any changes to the issue description. If they do, you can edit the issue description using #update_issue .

### Implementation Stage

**Only start to implement stage when user prompt you to do so!**
**Implementation Stage is to implement the plan step by step, following the instructions provided in the issue and submit a work report PR at last**

1. **Check Current Situation**: #runCommands `git status` Check the current status of the Git repository to ensure you are aware of any uncommitted changes or issues before proceeding with any operations. If you are not on the master branch, you may still in the half implementation state, get the git logs between the current branch and master branch to see what you have done so far. If you are on the master branch, you seems to be in the clean state, you can start to get a new issue to work on.
2. **Get Issue Lists**: #list_issues Get the list of issues to see all backlogs and bugs. Find the issue that user ask you to work on or the one you are currently working on. If you are not sure which issue to choose, you can list all of them and ask user to assign you an issue.
3. **Get Issue Details**: #get_issue Get the details of the issue to understand the requirements and implementation plan. Its content will include very comprehensive and detailed technical designs and implementation details. Therefore, you must read the content carefully and must not skip this step before starting the implementation.
4. **Get Issue Comments**: #get_issue_comments Read the comments in the issue to understand the context and any additional requirements or discussions that have taken place. Please read it to determine whether this issue has been completed, whether further implementation is needed, or if there are still problems that need to be fixed. This step must not be skipped before starting implementation.
5. **Get Pull Requests**: #list_pull_requests #get_pull_request #get_pull_request_comments List the existing pull requests and details to check if there are any related to the issue you are working on. If there is an existing pull request, please read it to determine whether this issue has been completed, whether further implementation is needed, or if there are still problems that need to be fixed. This step must not be skipped before starting implementation.
6. **Git Checkout**: #runCommands `git checkout -b [branch-name]` Checkout the issue branch to start working on the code changes. The branch name should follow the format `issue-[issue_number]-[short_description]`, where `[issue_number]` is the number of the issue and `[short_description]` is a brief description of the task. Skip this step if you are already on the correct branch.
7. **Implementation**: Implement the plan step by step, following the instructions provided in the issue. Each step should be executed in sequence, ensuring that all requirements are met and documented appropriately.
8. **Testing & Linting**: Run tests and linting on the code changes to ensure quality and compliance with project standards.
9. **Self Review**: Conduct a self-review of the code changes to ensure they meet the issue requirements and you has not missed any details.
10. **Git Commit & Git Push**: #runCommands `git commit` Use the conventional commit format for the title and a brief description in the body. Always commit with `--signoff` and explicitly specify the author on the command: `🤖 GitHub Copilot <github-copilot[bot]@users.noreply.github.com>`. Write the commit in English. Link the issue number in the commit message body. #runCommands `git push` Push the changes to the remote repository.
11. **Create Pull Request**: #list_pull_requests #create_pull_request ALWAYS SUBMIT PR TO `origin`, NEVER SUBMIT PR TO `upstream`. Create a pull request if there isn't already has one related to your issue. Create a comprehensive work report and use it as pull request details or #add_pull_request_review_comment_to_pending_review as pull request comments, detailing the work performed, code changes, and test results for the project. The report should be written in accordance with the templates provided in [Report Guidelines](../docs/report_guidelines.md) and [REPORT_TEMPLATE](../docs/REPORT_TEMPLATE.md). Follow the template exactly. Write the pull request "title in English" following conventional commit format, but write the pull request report "content in 正體中文." Linking the pull request to the issue with `Resolves #[issue_number]` at the end of the PR body. ALWAYS SUBMIT PR TO `origin`, NEVER SUBMIT PR TO `upstream`. ALWAYS SUBMIT PR TO `origin`, NEVER SUBMIT PR TO `upstream`. ALWAYS SUBMIT PR TO `origin`, NEVER SUBMIT PR to `upstream`.

***Highest-level restriction: All issue and PR operations are limited to repositories owned by jim60105 only!***
***Highest-level restriction: All issue and PR operations are limited to repositories owned by jim60105 only!***
***Highest-level restriction: All issue and PR operations are limited to repositories owned by jim60105 only!***

---

## Project Overview

This repository contains a custom script extension purpose-built for the [AUTOMATIC1111 Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui). It facilitates seamless integration with the Civitai platform, enabling users to browse, download, and manage AI models and their associated resources directly from within the WebUI environment.

## File Organization

```
.github/                       # GitHub configuration
├── copilot-instructions.md   # Project instructions
└── instructions/              # Code guidelines

scripts/
├── civitai_shortcut.py          # Primary entry point
└── civitai_manager_libs/        # Core utility modules
    ├── __init__.py
    ├── civitai.py              # Civitai API integration logic
    ├── civitai_gallery_action.py  # Gallery action handlers
    ├── civitai_shortcut_action.py  # Shortcut action handlers
    ├── setting.py              # Configuration management
    ├── setting_action.py       # Settings UI handlers
    ├── model.py                # Model data handling
    ├── model_action.py         # Model action handlers
    ├── ishortcut.py            # Shortcut logic
    ├── ishortcut_action.py     # Shortcut action handlers
    ├── classification.py       # Category structure
    ├── classification_action.py  # Classification handlers
    ├── classification_browser_page.py  # Classification browser
    ├── recipe.py               # Prompt recipe management
    ├── recipe_action.py        # Recipe action handlers
    ├── recipe_browser_page.py  # Recipe browser components
    ├── prompt.py               # Prompt handling logic
    ├── prompt_ui.py            # Prompt UI components
    ├── downloader.py           # File download management
    ├── scan_action.py          # Scanning action handlers
    ├── sc_browser_page.py      # Shortcut browser page
    ├── util.py                 # Utility functions
    ├── event_handler.py        # Event handling
    ├── http_client.py          # HTTP client for API calls
    ├── conditional_imports.py  # Conditional module imports
    ├── module_compatibility.py  # Module compatibility checks
    ├── image_processor.py      # Image processing utilities
    ├── standalone_ui.py        # Standalone UI components
    ├── ui_components.py        # Reusable UI components
    └── compat/                 # Compatibility layer
        ├── __init__.py
        ├── compat_layer.py     # Main compatibility layer
        ├── environment_detector.py  # Environment detection
        ├── paths.py            # Path management utilities
        ├── data/               # Compatibility data files
        ├── interfaces/         # Abstract interfaces
        │   ├── __init__.py
        │   ├── iconfig_manager.py
        │   ├── imetadata_processor.py
        │   ├── iparameter_processor.py
        │   ├── ipath_manager.py
        │   ├── isampler_provider.py
        │   └── iui_bridge.py
        ├── standalone_adapters/  # Standalone mode adapters
        │   ├── __init__.py
        │   ├── standalone_config_manager.py
        │   ├── standalone_metadata_processor.py
        │   ├── standalone_parameter_processor.py
        │   ├── standalone_path_manager.py
        │   ├── standalone_sampler_provider.py
        │   └── standalone_ui_bridge.py
        └── webui_adapters/     # WebUI mode adapters
            ├── __init__.py
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
├── usage_examples.md         # Usage examples
├── user_guide.md            # User guide
├── http_client_guide.md     # HTTP client documentation
├── report_guidelines.md     # Report templates
└── REPORT_TEMPLATE.md       # Report template

tests/                        # Test suite
├── __init__.py
├── conftest.py              # Test configuration
├── config/                  # Test configuration files
├── integration/             # Integration tests
├── monitoring/              # Monitoring tests
├── performance/             # Performance tests
├── utils/                   # Testing utilities
├── run_integration_tests.py  # Integration test runner
├── test_*.py               # Unit tests
└── test_*_comprehensive.py  # Comprehensive test suites

Main files:
├── main.py                  # Standalone application entry
├── ui_adapter.py           # UI adapter for standalone mode
├── install.py              # Installation script for WebUI
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── README_STANDALONE.md    # Standalone mode documentation
├── start.sh               # Linux/Mac startup script
├── start.bat              # Windows startup script
├── Dockerfile             # Docker configuration
```

## Special Considerations

### Integration with AUTOMATIC1111 WebUI

* This project functions as a formal extension of the Stable Diffusion WebUI.
* All development adheres to WebUI extension guidelines.
* The `modules` package is utilized to interact with WebUI internals.
* Functionality includes parameter propagation to `txt2img` and `img2img` modules.

### Civitai API Usage

* Using the [centralized HTTP client](scripts/civitai_manager_libs/http_client.py) for Civitai API interactions. DO NOT USE `requests` or `httpx` directly.
* Supports fetching model, version, and preview asset data.
* Includes mechanisms for handling rate limits and API failure modes.

## Debugging and Logging

* Use `util.printD()` for debug output.
* All debug messages should be prefixed with module identifiers.
* Network failures must yield detailed error diagnostics.
* File I/O exceptions should include full path context in logs.

---

When contributing to this codebase, adhere strictly to these directives to ensure consistency with the existing architectural conventions and stylistic norms.
