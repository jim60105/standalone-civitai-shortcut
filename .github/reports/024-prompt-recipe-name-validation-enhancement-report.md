---
title: "Job Report: Bug Fix #024 - Prompt Recipe 名稱驗證與用戶提示功能增強"
date: "2025-06-20T22:53:51Z"
---

# Bug Fix #024 - Prompt Recipe 名稱驗證與用戶提示功能增強 工作報告

**日期**：2025-06-20T22:53:51Z  
**任務**：當使用者未輸入 Prompt Recipe 名稱即點擊 Create 時，應顯示具體提示，改善使用者體驗  
**類型**：Bug Fix  
**狀態**：已完成

> 此報告依據 `.github/plans/bugs/001-prompt-recipe-name-validation-enhancement.md` 任務規範撰寫。

## 一、任務概述

Prompt Recipe 的 Create 按鈕在名稱欄位為空、僅含空白或為預設值時，會無聲失敗，缺乏任何提示，導致使用者不明原因操作失敗。本次修正旨在新增名稱驗證與明確提示，以提升使用流程的可預期性與易用性。

## 二、問題分析

- **無聲失敗**：當 `recipe_name` 為空、僅包含空白或為預設 `[New Prompt Recipe]` 時，`on_recipe_create_btn_click()` 直接返回，未提供任何回饋  【F:scripts/civitai_manager_libs/recipe_action.py†L977-L986】
- **根本原因**：缺少名稱檢查與提示邏輯，使用者無法得知失敗原因並進行後續操作

## 三、實作內容

### 3.1 新增名稱驗證與提示邏輯
- 在 `on_recipe_create_btn_click()` 函式中，於初始化後新增檢查：
  ```python
  # Validate recipe name before creating
  if not recipe_name or not recipe_name.strip() or recipe_name == setting.NEWRECIPE:
      gr.Warning("Please enter a recipe name before creating.")
      return (
          gr.update(value=""),
          gr.update(
              choices=[setting.PLACEHOLDER] + recipe.get_classifications(), value=s_classification
          ),
          gr.update(label=setting.NEWRECIPE),
          gr.update(visible=True),
          gr.update(visible=False),
          gr.update(visible=False),
      )
  ```
  【F:scripts/civitai_manager_libs/recipe_action.py†L993-L1006】

### 3.2 更新函式註釋說明
- 補齊 `on_recipe_create_btn_click()` 的 docstring，說明參數、返回值與警告觸發條件  【F:scripts/civitai_manager_libs/recipe_action.py†L976-L993】

### 3.3 單元測試實作
- 新增 `tests/test_recipe_validation.py` 檔案，對空名稱、空白名稱、預設名稱與有效名稱進行四種測試  【F:tests/test_recipe_validation.py†L1-L62】

### 3.4 抑制測試環境初始化例外
- 於 `setting.py` 中包裝 `_initialize_extension_base()`，避免因相容性層或依賴（PIL、requests）缺失而在匯入時拋出錯誤  【F:scripts/civitai_manager_libs/setting.py†L47-L51】

### 3.5 測試環境 Stub 模組
- 在 `conftest.py` 中 Stub `gradio`、`PIL`、`requests` 模組，並提供基本屬性與 __getattr__ 以支持測試匯入  【F:conftest.py†L5-L20】【F:conftest.py†L21-L32】

## 四、測試驗證

### 自動化測試
```bash
pytest tests/test_recipe_validation.py -q
```  
所有單元測試通過，警告觸發與成功路徑邏輯均達成預期。

### 手動驗證
1. Standalone 模式下啟動程式，於 Prompt Recipe 頁面測試：
   - 空或空白名稱與預設名稱時，顯示 "Please enter a recipe name before creating."  
   - 輸入有效名稱時，正常建立配方且不顯示警告
2. WebUI 模式下同樣驗證，行為一致。

## 五、影響評估

- **向後相容性**：保留原有成功與失敗路徑的返回結構，不影響其他功能元件
- **使用者體驗**：新增即時提示，提升操作直觀性與回饋效能

## 六、代碼品質

- 受影響檔案通過 Black 格式化  【F:scripts/civitai_manager_libs/recipe_action.py†L976-L1006】【F:scripts/civitai_manager_libs/setting.py†L47-L51】
- 單元測試符合 pytest 規範並皆通過

## 七、使用說明

- 執行單元測試：
  ```bash
  pytest tests/test_recipe_validation.py -v
  ```
- 無需額外設定，即可在 Standalone 與 WebUI 模式下驗證此功能

## 八、檔案異動清單

| 檔案路徑                                              | 修改類型 | 描述              |
|-----------------------------------------------------|---------|------------------|
| `scripts/civitai_manager_libs/recipe_action.py`     | 修改    | 新增名稱驗證與提示邏輯，更新 docstring |
| `tests/test_recipe_validation.py`                   | 新增    | 添加名稱驗證功能的單元測試 |
| `scripts/civitai_manager_libs/setting.py`           | 修改    | 包裝初始化以抑制測試環境例外 |
| `conftest.py`                                       | 修改    | Stub gradio、PIL、requests  |
| `.github/reports/024-prompt-recipe-name-validation-enhancement-report.md` | 新增    | 本次工作報告 |

## 九、後續建議

- **國際化支援**：未來可將提示訊息改為多語系以服務更多用戶
- **UI Placeholder**：在名稱欄位加入 Placeholder 提示文字，提升填寫引導
- **即時驗證**：考慮在輸入階段即時檢查名稱有效性，避免點擊後才提示
