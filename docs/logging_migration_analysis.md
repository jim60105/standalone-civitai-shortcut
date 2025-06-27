## Logging Migration Analysis (Stage 1)

This document summarizes the occurrences of `util.printD()` across the codebase as stage 1 analysis for migrating to standard Python logging (Issue #26).

| File                                                                 | Occurrences |
|----------------------------------------------------------------------|-------------|
| AGENTS.md                                                            | 2           |
| scripts/civitai_manager_libs/civitai.py                               | 81          |
| scripts/civitai_manager_libs/civitai_gallery_action.py               | 69          |
| scripts/civitai_manager_libs/civitai_shortcut_action.py              | 119         |
| scripts/civitai_manager_libs/classification.py                       | 4           |
| scripts/civitai_manager_libs/classification_action.py                | 3           |
| scripts/civitai_manager_libs/compat/standalone_adapters/standalone_path_manager.py | 10          |
| scripts/civitai_manager_libs/compat/webui_adapters/webui_path_manager.py      | 12          |
| scripts/civitai_manager_libs/downloader.py                           | 10          |
| scripts/civitai_manager_libs/http_client.py                          | 14          |
| scripts/civitai_manager_libs/ishortcut.py                            | 79          |
| scripts/civitai_manager_libs/ishortcut_action.py                     | 105         |
| scripts/civitai_manager_libs/model.py                                | 1           |
| scripts/civitai_manager_libs/model_action.py                         | 2           |
| scripts/civitai_manager_libs/module_compatibility.py                 | 1           |
| scripts/civitai_manager_libs/prompt.py                               | 16          |
| scripts/civitai_manager_libs/prompt_ui.py                            | 4           |
| scripts/civitai_manager_libs/recipe.py                               | 4           |
| scripts/civitai_manager_libs/recipe_action.py                        | 42          |
| scripts/civitai_manager_libs/recipe_browser_page.py                  | 2           |
| scripts/civitai_manager_libs/scan_action.py                          | 7           |
| scripts/civitai_manager_libs/setting.py                              | 61          |
| scripts/civitai_manager_libs/setting_action.py                       | 3           |
| scripts/civitai_shortcut.py                                          | 1           |
| tests/test_gallery_select_fix.py                                     | 8           |
| tests/test_http_client.py                                            | 1           |
| tests/test_integration.py                                            | 1           |
| tests/test_module_compatibility.py                                   | 3           |
| ui_adapter.py                                                        | 1           |

*Total occurrences: 666*

---

## Next Steps (Stage 2)

Stage 2 will migrate each `util.printD()` call to `logger.debug()` or another appropriate logging level using the standard Python `logging` module. High-priority modules will be processed first, followed by medium and low-priority modules according to the implementation plan outlined in Issue #26.
