# Bug Fix 001: Prompt Recipe 名稱驗證與用戶提示功能增強

## 優先級
**中等 (Medium)** - 用戶體驗改善，影響日常操作流暢度

## 估算工作量
**2-3 工作天**

## 目標描述
改善 Prompt Recipe 功能的用戶體驗，當用戶在未輸入配方名稱的情況下點擊 "Create" 按鈕時，系統應該顯示明確的提示訊息而非靜默跳過操作。通過實作 `gr.Warning()` 提示通知，讓用戶清楚瞭解為什麼創建操作沒有執行，並提供明確的操作指引。

## 接受標準 (Definition of Done)
1. ✅ 當 Recipe 名稱為空時顯示 `gr.Warning()` 提示訊息
2. ✅ 當 Recipe 名稱僅包含空白字符時顯示提示訊息  
3. ✅ 當 Recipe 名稱為預設值 `[New Prompt Recipe]` 時顯示提示訊息
4. ✅ 提示訊息使用英文且內容明確易懂
5. ✅ 保持現有功能的向後相容性
6. ✅ 通過程式碼品質檢查（black、flake8）
7. ✅ 添加對應的單元測試
8. ✅ 更新相關文檔和提交報告

## 問題分析

### 現狀問題
當前在 `/workspaces/civitai-shortcut/scripts/civitai_manager_libs/recipe_action.py` 中的 `on_recipe_create_btn_click()` 函數（第977行開始）存在以下問題：

1. **無聲失敗**：當名稱驗證失敗時，函數直接返回預設值而不提供任何用戶反饋
2. **用戶困惑**：用戶無法瞭解為什麼點擊 "Create" 按鈕後沒有任何反應
3. **體驗不佳**：缺乏明確的操作指引，影響使用流暢度

### 根本原因
```python
# 第979行：當驗證失敗時直接返回，沒有用戶提示
if recipe_name and len(recipe_name.strip()) > 0 and recipe_name != setting.NEWRECIPE:
    # 正常創建邏輯...
else:
    # 直接返回預設值，沒有任何提示
    return (...)
```

## 詳細任務

### 任務 1.1: 深入程式碼分析與需求確認
**預估時間：0.5 天**

1. **詳細分析現有邏輯**
   ```bash
   # 分析相關檔案的功能實作
   grep -n "recipe_create_btn_click" /workspaces/civitai-shortcut/scripts/civitai_manager_libs/recipe_action.py
   grep -n "NEWRECIPE" /workspaces/civitai-shortcut/scripts/civitai_manager_libs/setting.py
   ```

2. **確認 gr.Warning 使用方式**
   - 研究專案中 Gradio 元件的使用模式
   - 確認 `gr.Warning()` 的正確調用方式
   - 分析是否需要特殊的返回值處理

3. **檢查相關函數**
   - `on_recipe_update_btn_click()` - 了解更新按鈕的驗證邏輯
   - `setting.NEWRECIPE` 常數定義
   - UI 元件的綁定關係

4. **預期輸出**：完整的技術分析報告，包含：
   - 現有功能流程圖
   - 問題點詳細說明
   - 解決方案設計草圖

### 任務 1.2: 實作名稱驗證與提示功能
**預估時間：1 天**

1. **修改 `on_recipe_create_btn_click()` 函數**
   
   **檔案位置**：`/workspaces/civitai-shortcut/scripts/civitai_manager_libs/recipe_action.py`
   
   **修改範圍**：第977-1030行
   
   **實作內容**：
   ```python
   def on_recipe_create_btn_click(
       recipe_name,
       recipe_desc,
       recipe_prompt,
       recipe_negative,
       recipe_option,
       recipe_classification,
       recipe_image=None,
       recipe_shortcuts=None,
   ):
       current_time = datetime.datetime.now()
       s_classification = setting.PLACEHOLDER
       
       # 新增：名稱驗證邏輯
       if not recipe_name or not recipe_name.strip() or recipe_name == setting.NEWRECIPE:
           gr.Warning("Please enter a recipe name before creating.")
           return (
               gr.update(value=""),
               gr.update(
                   choices=[setting.PLACEHOLDER] + recipe.get_classifications(), 
                   value=s_classification
               ),
               gr.update(label=setting.NEWRECIPE),
               gr.update(visible=True),
               gr.update(visible=False),
               gr.update(visible=False),
           )
       
       # 原有的創建邏輯保持不變...
   ```

2. **驗證條件設計**
   - 空字串：`not recipe_name`
   - 純空白字符：`not recipe_name.strip()`
   - 預設值：`recipe_name == setting.NEWRECIPE`

3. **提示訊息設計**
   - 訊息內容：`"Please enter a recipe name before creating."`
   - 語言：英文（符合專案規範）
   - 長度：簡潔明確，適合 toast 顯示

4. **返回值處理**
   - 保持與現有失敗情況相同的返回值結構
   - 確保 UI 狀態一致性
   - 不影響其他功能元件

### 任務 1.3: 程式碼品質確保
**預估時間：0.5 天**

1. **程式碼格式化**
   ```bash
   # 使用 black 格式化修改的檔案
   black --line-length=100 --skip-string-normalization scripts/civitai_manager_libs/recipe_action.py
   
   # 使用 flake8 檢查程式碼品質
   flake8 scripts/civitai_manager_libs/recipe_action.py --config=.flake8
   ```

2. **相容性檢查**
   - 確保修改不影響現有的 Create 成功流程
   - 確保修改不影響 Update 功能
   - 驗證與 `setting.NEWRECIPE` 的邏輯一致性

3. **匯入檢查**
   - 確認 `gr` 模組已正確匯入
   - 檢查是否需要新增任何相依性

### 任務 1.4: 測試實作與驗證
**預估時間：1 天**

1. **單元測試設計**
   
   **檔案位置**：`/workspaces/civitai-shortcut/tests/test_recipe_validation.py`
   
   **測試案例**：
   ```python
   import pytest
   from unittest.mock import patch, MagicMock
   import gradio as gr
   from scripts.civitai_manager_libs import recipe_action, setting
   
   class TestRecipeNameValidation:
       
       @patch('gradio.Warning')
       def test_empty_recipe_name_shows_warning(self, mock_warning):
           """測試空名稱時顯示警告"""
           result = recipe_action.on_recipe_create_btn_click(
               recipe_name="",
               recipe_desc="Test description",
               recipe_prompt="Test prompt",
               recipe_negative="",
               recipe_option="",
               recipe_classification=setting.PLACEHOLDER
           )
           mock_warning.assert_called_once_with("Please enter a recipe name before creating.")
           # 驗證返回值結構
           
       @patch('gradio.Warning')
       def test_whitespace_only_name_shows_warning(self, mock_warning):
           """測試純空白字符名稱時顯示警告"""
           result = recipe_action.on_recipe_create_btn_click(
               recipe_name="   \t\n   ",
               recipe_desc="Test description",
               recipe_prompt="Test prompt",
               recipe_negative="",
               recipe_option="",
               recipe_classification=setting.PLACEHOLDER
           )
           mock_warning.assert_called_once_with("Please enter a recipe name before creating.")
           
       @patch('gradio.Warning')
       def test_default_name_shows_warning(self, mock_warning):
           """測試預設名稱時顯示警告"""
           result = recipe_action.on_recipe_create_btn_click(
               recipe_name=setting.NEWRECIPE,
               recipe_desc="Test description",
               recipe_prompt="Test prompt",
               recipe_negative="",
               recipe_option="",
               recipe_classification=setting.PLACEHOLDER
           )
           mock_warning.assert_called_once_with("Please enter a recipe name before creating.")
           
       @patch('scripts.civitai_manager_libs.recipe.create_recipe', return_value=True)
       def test_valid_name_creates_recipe(self, mock_create):
           """測試有效名稱時正常創建"""
           result = recipe_action.on_recipe_create_btn_click(
               recipe_name="Valid Recipe Name",
               recipe_desc="Test description",
               recipe_prompt="Test prompt",
               recipe_negative="",
               recipe_option="",
               recipe_classification=setting.PLACEHOLDER
           )
           mock_create.assert_called_once()
           # 驗證成功創建的返回值
   ```

2. **整合測試**
   ```python
   def test_ui_integration():
       """測試 UI 整合，確保警告不影響其他元件"""
       # 模擬完整的 UI 互動流程
       pass
       
   def test_backwards_compatibility():
       """測試向後相容性"""
       # 確保現有功能不受影響
       pass
   ```

3. **手動測試案例**
   
   **測試環境準備**：
   ```bash
   # 啟動 Standalone 模式進行測試
   python main.py
   ```
   
   **測試步驟**：
   
   | 測試案例 | 操作步驟 | 預期結果 |
   |---------|---------|---------|
   | 空名稱測試 | 1. 進入 Prompt Recipe 頁面<br/>2. 填寫描述和提示詞<br/>3. 保持名稱欄位為空<br/>4. 點擊 Create 按鈕 | 顯示警告："Please enter a recipe name before creating." |
   | 空白字符測試 | 1. 在名稱欄位輸入只有空格的內容<br/>2. 點擊 Create 按鈕 | 顯示相同警告訊息 |
   | 預設值測試 | 1. 確保名稱顯示為 [New Prompt Recipe]<br/>2. 點擊 Create 按鈕 | 顯示相同警告訊息 |
   | 正常創建測試 | 1. 輸入有效的配方名稱<br/>2. 點擊 Create 按鈭 | 正常創建配方，不顯示警告 |

4. **跨模式測試**
   - **WebUI 模式測試**：在 AUTOMATIC1111 環境中測試
   - **Standalone 模式測試**：使用 `python main.py` 測試

### 任務 1.5: 文檔更新與報告撰寫
**預估時間：0.5 天**

1. **代碼註解更新**
   ```python
   def on_recipe_create_btn_click(
       recipe_name,
       # ... 其他參數
   ):
       """
       Handle recipe creation button click with name validation.
       
       Shows warning message if recipe name is empty, whitespace-only, 
       or set to default value.
       
       Args:
           recipe_name (str): The name of the recipe to create
           # ... 其他參數說明
           
       Returns:
           tuple: UI update values for recipe creation state
           
       Raises:
           gr.Warning: When recipe name validation fails
       """
   ```

2. **工作報告撰寫**
   
   **檔案位置**：`.github/reports/024-prompt-recipe-name-validation-enhancement-report.md`
   
   **報告結構**：
   ```markdown
   # Bug Fix #024 - Prompt Recipe 名稱驗證與用戶提示功能增強 工作報告
   
   ## 一、任務概述
   ## 二、問題分析
   ## 三、實作內容
   ## 四、測試驗證
   ## 五、影響評估
   ## 六、代碼品質
   ## 七、使用說明
   ## 八、檔案異動清單
   ## 九、後續建議
   ```

3. **API 文檔更新**（如果需要）
   - 更新函數說明
   - 更新用戶指南中的相關章節

## 技術規格

### 檔案修改清單
| 檔案路徑 | 修改類型 | 修改內容 |
|---------|---------|---------|
| `scripts/civitai_manager_libs/recipe_action.py` | 修改 | 在 `on_recipe_create_btn_click()` 函數中添加名稱驗證邏輯 |
| `tests/test_recipe_validation.py` | 新增 | 添加名稱驗證功能的單元測試 |
| `.github/reports/024-prompt-recipe-name-validation-enhancement-report.md` | 新增 | 工作報告文檔 |

### 相依性分析
- **直接相依**：
  - `gradio` 模組（已存在）
  - `setting` 模組（已存在）
  - `recipe` 模組（已存在）
  
- **間接相依**：無新增相依性

### 風險評估
| 風險類型 | 風險等級 | 風險描述 | 緩解措施 |
|---------|---------|---------|---------|
| 功能回歸 | 低 | 修改可能影響現有創建流程 | 完整的回歸測試 |
| UI 相容性 | 低 | 警告訊息可能影響 UI 佈局 | 在兩種模式下進行測試 |
| 用戶習慣 | 極低 | 用戶需要適應新的提示訊息 | 提供清楚的提示內容 |

## 驗收測試

### 自動化測試
```bash
# 執行相關單元測試
pytest tests/test_recipe_validation.py -v

# 執行回歸測試
pytest tests/test_recipe_action.py -v

# 程式碼品質檢查
black --check --line-length=100 --skip-string-normalization scripts/civitai_manager_libs/recipe_action.py
flake8 scripts/civitai_manager_libs/recipe_action.py --config=.flake8
```

### 手動驗收標準
1. **基本功能驗證**
   - [ ] 空名稱時顯示警告訊息
   - [ ] 純空白字符時顯示警告訊息
   - [ ] 預設名稱時顯示警告訊息
   - [ ] 有效名稱時正常創建配方

2. **用戶體驗驗證**
   - [ ] 警告訊息內容清晰易懂
   - [ ] 警告訊息顯示時機正確
   - [ ] UI 狀態保持一致

3. **相容性驗證**
   - [ ] WebUI 模式正常運作
   - [ ] Standalone 模式正常運作
   - [ ] 其他功能不受影響

## 成功標準

### 功能標準
- [x] 實作名稱驗證邏輯，涵蓋三種無效情況
- [x] 使用 `gr.Warning()` 顯示適當的提示訊息
- [x] 保持現有功能的完整性和向後相容性

### 品質標準
- [x] 通過所有自動化測試
- [x] 程式碼符合專案的編碼規範
- [x] 完成完整的文檔和報告

### 用戶體驗標準
- [x] 提供明確且有用的錯誤提示
- [x] 不影響正常的操作流程
- [x] 增強整體使用者體驗

## 後續改善建議

### 短期改善
1. **國際化支援**：考慮為提示訊息添加多語言支援
2. **輸入提示**：在名稱欄位添加 placeholder 提示文字
3. **即時驗證**：考慮在用戶輸入時進行即時驗證反饋

### 長期規劃
1. **統一驗證機制**：為其他類似功能建立統一的驗證和提示機制
2. **用戶體驗優化**：收集用戶反饋，持續改善提示訊息和互動體驗
3. **自動化測試擴展**：為更多用戶互動場景添加自動化測試

## 注意事項

### 開發注意事項
1. **測試環境**：確保在兩種模式（WebUI 和 Standalone）下都進行充分測試
2. **向後相容**：絕對不能破壞現有的成功創建流程
3. **程式碼品質**：嚴格遵循專案的編碼規範和品質要求

### 部署注意事項
1. **無需重啟**：修改應該可以透過重新載入生效，無需重啟應用
2. **用戶培訓**：考慮在更新說明中提及新的提示功能
3. **監控反饋**：部署後密切關注用戶反饋，確保改善達到預期效果

此開發計劃提供了實作 Prompt Recipe 名稱驗證與用戶提示功能的完整指導，通過詳細的任務分解、技術規格說明和驗收標準，確保任何開發人員都能成功完成這項工作，並達到高品質的交付標準。
