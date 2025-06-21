# Bug Fix 002: Send To Recipe Prompt Extraction Bug

## 優先級
**高 (High)** - 影響核心功能與主要用戶體驗

## 估算工作量
**2-3 工作天**

## 目標描述
修正「Send To Recipe」功能，確保當用戶從 Model Browser 或 Civitai User Gallery 點擊「Send To Recipe」按鈕時，圖像中的提示詞、負面提示詞與生成參數能自動正確提取並分別填充到 Prompt、Negative prompt 與 Parameter 欄位，提升 Recipe 編輯流程的直覺性與效率。

## 接受標準 (Definition of Done)
1. ✅ 點擊「Send To Recipe」後，Prompt 欄位自動填入圖像元數據中的提示詞
2. ✅ Negative prompt 欄位自動填入負面提示詞
3. ✅ Parameter 欄位自動填入生成參數
4. ✅ Reference Image 正確顯示圖像
5. ✅ 支援 Model Browser、Civitai User Gallery、拖拽圖像三種入口
6. ✅ 通過所有相關單元測試與整合測試
7. ✅ 程式碼通過 black、flake8 檢查
8. ✅ 完成詳細工作報告與文檔更新

## 問題分析

### 現狀問題
當前在「Model Browser」或「Civitai User Gallery」中，點擊「Send To Recipe」按鈕後，雖然圖像能正確顯示於「Prompt Recipe」頁籤的 Reference Image 區域，但圖像中的提示詞、負面提示詞與生成參數未能自動提取並填入對應欄位，導致用戶需手動複製貼上，體驗不佳。

### 根本原因
- 在 Model Browser 和 Civitai User Gallery 中，`on_gallery_select` 已正確實作 PNG info 提取的 fallback 機制（先嘗試從圖像檔案的 PNG info，再從 Civitai API 元數據），並將解析好的生成參數放入 `img_file_info`
- 但在 `on_send_to_recipe_click` 中，只傳遞了圖像檔案路徑，而未傳遞已解析的 `img_file_info`（生成參數字串）
- 在 `on_recipe_generate_data_change` 中再次嘗試從圖像檔案提取 PNG info，但圖像檔案可能並不包含 PNG info（特別是從 Civitai 下載的圖像）
- 正確流程應為：`on_send_to_recipe_click` 直接傳遞已解析的 `img_file_info` 到 Recipe，避免重複解析和 fallback 失敗

## 詳細任務

### 任務 2.1: 現有流程分析與需求確認
**預估時間：0.5 天**
1. 詳細分析 `on_send_to_recipe_click()`、`on_gallery_select()`、`on_recipe_input_change()` 的資料流與事件觸發
2. 確認 `img_file_info` 已包含完整的生成參數（透過 PNG info 和 Civitai API fallback）
3. 製作現有與預期流程圖，明確資料傳遞節點的問題與解決方案

### 任務 2.2: 修正資料傳遞邏輯，直接傳遞已解析的生成參數
**預估時間：1 天**
1. 修改 `on_send_to_recipe_click()` 函數，將 `img_file_info`（已解析的生成參數字串）而非圖像檔案傳遞給 Recipe
2. 修改 Recipe 的資料流，直接使用傳入的生成參數字串而非再次解析圖像
3. 確保拖拽圖像進入 Recipe 頁籤時的行為保持一致（仍需解析圖像 PNG info）
4. 保持向後相容性，確保現有 Recipe 編輯流程不受影響

### 任務 2.3: 程式碼品質與相容性檢查
**預估時間：0.5 天**
1. 使用 black 格式化修改檔案
2. 使用 flake8 依 .flake8 配置檢查程式碼品質
3. 驗證修改不影響其他功能元件與 UI 狀態

### 任務 2.4: 測試設計與驗證
**預估時間：1 天**
1. 單元測試：覆蓋 on_send_to_recipe_click、on_recipe_input_change 的資料流與欄位填充
2. 整合測試：模擬從 Model Browser、Civitai User Gallery、拖拽圖像三種入口的完整流程
3. 手動測試：依據測試場景逐步驗證 UI 行為與資料正確性

### 任務 2.5: 文檔與報告撰寫
**預估時間：0.5 天**
1. 更新 API 與 UI 流程說明
2. 撰寫詳細工作報告，依 .github/reports/REPORT_TEMPLATE.md 格式

## 技術規格

### 實作方案說明
**新實作方案：直接傳遞已解析的生成參數**
1. Model Browser 和 Civitai User Gallery 的 `on_gallery_select` 已完整實作 fallback 機制
2. `img_file_info` 包含完整格式化的生成參數字串（如："Prompt: xxx\nNegative prompt: xxx\nSteps: 20, Sampler: Euler"）
3. `on_send_to_recipe_click` 直接傳遞 `img_file_info` 到 Recipe，避免重複解析
4. Recipe 接收到已解析的參數字串，直接進行欄位分析與填充

**相較於原有錯誤方案的優勢：**
- 避免重複實作 Civitai API fallback 邏輯
- 降低圖像無 PNG info 時的失敗率
- 保持現有 Gallery 的解析邏輯不變
- 減少程式碼複雜度與維護成本

### 檔案修改清單
| 檔案路徑 | 修改類型 | 修改內容 |
|---------|---------|---------|
| `scripts/civitai_manager_libs/ishortcut_action.py` | 修改 | 修改 on_send_to_recipe_click() 直接傳遞 img_file_info |
| `scripts/civitai_manager_libs/civitai_gallery_action.py` | 修改 | 修改 on_send_to_recipe_click() 直接傳遞 img_file_info |
| `scripts/civitai_manager_libs/recipe_action.py` | 修改 | 修改 on_recipe_input_change() 處理已解析的生成參數 |
| `tests/test_send_to_recipe_fix.py` | 新增/修改 | 添加/更新單元測試與整合測試 |
| `.github/reports/037-send-to-recipe-prompt-extraction-bug-report.md` | 新增 | 工作報告文檔 |

### 相依性分析
- **直接相依**：gradio、setting、recipe、ishortcut_action
- **間接相依**：無新增相依性

### 風險評估
| 風險類型 | 風險等級 | 風險描述 | 緩解措施 |
|---------|---------|---------|---------|
| 功能回歸 | 低 | 直接傳遞已解析資料，不改變現有解析邏輯 | 完整回歸測試，特別關注拖拽圖像場景 |
| 資料格式相容性 | 低 | img_file_info 格式已標準化 | 新增格式驗證與錯誤處理 |
| 用戶習慣 | 極低 | 提升自動填充體驗，無需改變操作流程 | 無需特別措施 |

## 驗收測試

### 自動化測試

```bash
pytest tests/test_send_to_recipe_fix.py -v
black --check --line-length=100 --skip-string-normalization scripts/civitai_manager_libs/ishortcut_action.py
black --check --line-length=100 --skip-string-normalization scripts/civitai_manager_libs/civitai_gallery_action.py  
black --check --line-length=100 --skip-string-normalization scripts/civitai_manager_libs/recipe_action.py
flake8 scripts/civitai_manager_libs/ishortcut_action.py --config=.flake8
flake8 scripts/civitai_manager_libs/civitai_gallery_action.py --config=.flake8
flake8 scripts/civitai_manager_libs/recipe_action.py --config=.flake8
```

### 手動驗收標準
1. [ ] 點擊「Send To Recipe」後，Prompt、Negative prompt、Parameter 欄位自動正確填充
2. [ ] Reference Image 正確顯示圖像
3. [ ] 支援三種入口（Model Browser、Civitai User Gallery、拖拽圖像）
4. [ ] UI 狀態與欄位同步正確
5. [ ] WebUI 與 Standalone 模式皆正常運作

## 成功標準
- [x] 三個欄位自動正確填充，無需手動複製貼上
- [x] 通過所有自動化與手動測試
- [x] 程式碼品質與專案規範完全符合
- [x] 完成詳細報告與文檔

## 後續改善建議
### 短期改善
1. 統一 Send To Recipe 的資料傳遞介面，確保所有入口使用相同格式
2. 增強錯誤處理，當生成參數為空時提供清楚的用戶提示
### 長期規劃
1. 重構圖像元數據提取邏輯，避免多處重複實作 fallback 機制
2. 建立統一的元數據處理介面，支援更多圖像格式與生成器

## 注意事項
### 開發注意事項
1. 嚴格遵循專案編碼規範與測試準則
2. 測試所有入口與模式，確保一致性
3. 不可破壞現有 Recipe 編輯與瀏覽流程
### 部署注意事項
1. 修改應可熱載入，無需重啟應用
2. 文檔與更新說明需同步
3. 部署後密切監控用戶回饋

本計劃針對 Send To Recipe Prompt Extraction Bug 提供完整修正路徑。**修正策略**：直接傳遞 Model Browser 和 Civitai Gallery 中已解析的生成參數（`img_file_info`），而非讓 Recipe 重新解析圖像檔案，避免重複實作 fallback 機制和圖像無 PNG info 時的失敗。涵蓋詳細任務分解、技術規格、驗收標準與後續優化建議，確保開發人員可高品質完成修正並提升用戶體驗。
