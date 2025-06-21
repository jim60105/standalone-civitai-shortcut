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
- 在 `scripts/civitai_manager_libs/recipe_action.py` 的 `on_recipe_input_change()` 函數中，recipe_generate_data 被設為 current_time（時間戳），而非圖像對象，導致後續 on_recipe_generate_data_change() 無法正確提取圖像元數據。
- 正確流程應為：recipe_input.change() → on_recipe_input_change() 設定 recipe_generate_data = recipe_image → recipe_generate_data.change() → on_recipe_generate_data_change() 提取元數據。

## 詳細任務

### 任務 2.1: 現有流程分析與需求確認
**預估時間：0.5 天**
1. 詳細分析 `on_send_to_recipe_click()`、`on_recipe_input_change()`、`on_recipe_generate_data_change()` 的資料流與事件觸發
2. 確認 UI 元件間的狀態傳遞與依賴關係
3. 製作現有與預期流程圖，明確資料傳遞節點

### 任務 2.2: 修正資料傳遞與元數據提取邏輯
**預估時間：1 天**
1. 修改 `on_recipe_input_change()`，將 recipe_generate_data 設為 recipe_image（圖像對象）
2. 確認 `on_recipe_generate_data_change()` 能正確接收圖像對象並提取提示詞、負面提示詞、生成參數
3. 保持拖拽圖像進入 Recipe 頁籤時的行為一致

### 任務 2.3: 程式碼品質與相容性檢查
**預估時間：0.5 天**
1. 使用 black 格式化修改檔案
2. 使用 flake8 依 .flake8 配置檢查程式碼品質
3. 驗證修改不影響其他功能元件與 UI 狀態

### 任務 2.4: 測試設計與驗證
**預估時間：1 天**
1. 單元測試：覆蓋 on_recipe_input_change、on_recipe_generate_data_change 的資料流與欄位填充
2. 整合測試：模擬從 Model Browser、Civitai User Gallery、拖拽圖像三種入口的完整流程
3. 手動測試：依據測試場景逐步驗證 UI 行為與資料正確性

### 任務 2.5: 文檔與報告撰寫
**預估時間：0.5 天**
1. 更新 API 與 UI 流程說明
2. 撰寫詳細工作報告，依 .github/reports/REPORT_TEMPLATE.md 格式

## 技術規格

### 檔案修改清單
| 檔案路徑 | 修改類型 | 修改內容 |
|---------|---------|---------|
| `scripts/civitai_manager_libs/recipe_action.py` | 修改 | 修正 on_recipe_input_change() 的資料傳遞與元數據提取 |
| `tests/test_send_to_recipe_fix.py` | 新增/修改 | 添加/更新單元測試與整合測試 |
| `.github/reports/025-send-to-recipe-prompt-extraction-bug-report.md` | 新增 | 工作報告文檔 |

### 相依性分析
- **直接相依**：gradio、setting、recipe、ishortcut_action
- **間接相依**：無新增相依性

### 風險評估
| 風險類型 | 風險等級 | 風險描述 | 緩解措施 |
|---------|---------|---------|---------|
| 功能回歸 | 中 | 修改資料流可能影響其他 UI 行為 | 完整回歸測試與手動驗證 |
| UI 相容性 | 低 | 不同入口的資料格式差異 | 多場景測試與例外處理 |
| 用戶習慣 | 極低 | 用戶需適應自動填充行為 | 清楚提示與文檔說明 |

## 驗收測試

### 自動化測試
```bash
pytest tests/test_send_to_recipe_fix.py -v
black --check --line-length=100 --skip-string-normalization scripts/civitai_manager_libs/recipe_action.pylake8 scripts/civitai_manager_libs/recipe_action.py --config=.flake8
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
1. 增強元數據解析容錯能力，支援更多圖像格式
2. 提供用戶自定義欄位映射選項
### 長期規劃
1. 統一圖像元數據提取邏輯，提升維護性
2. 擴展自動提取支援更多生成器與格式

## 注意事項
### 開發注意事項
1. 嚴格遵循專案編碼規範與測試準則
2. 測試所有入口與模式，確保一致性
3. 不可破壞現有 Recipe 編輯與瀏覽流程
### 部署注意事項
1. 修改應可熱載入，無需重啟應用
2. 文檔與更新說明需同步
3. 部署後密切監控用戶回饋

本計劃針對 Send To Recipe Prompt Extraction Bug 提供完整修正路徑，涵蓋詳細任務分解、技術規格、驗收標準與後續優化建議，確保開發人員可高品質完成修正並提升用戶體驗。
