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
  * Always use `util.printD()` for structured debug output with module identifiers.
  * Ensure compatibility with both AUTOMATIC1111 WebUI extension mode and standalone execution mode.
  * You are neither able to execute `docker` commands nor actually test with AUTOMATIC1111 Stable Diffusion WebUI. Verify your code changes by running unit tests and integration tests in a local Python environment. Ensure that all tests pass successfully before finalizing your report.
  * Git commit after completing your work, using conventional commit format for the title and a brief description in the body. Always sign off the commit with `--signoff` and do not use GPG signing.

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

Development progress for this project is systematically tracked within the `.github/codex` directory. Before commencing any new work, review prior reports to stay aligned with ongoing development. Treat all past reports as immutable references—do not edit or revise them under any circumstance. Upon the completion of each task, you are required to generate a new comprehensive work report. Refer to the naming conventions of existing files to determine an appropriate filename.

Your report must include a detailed account of the work performed, encompassing all relevant code modifications and corresponding test outcomes.
