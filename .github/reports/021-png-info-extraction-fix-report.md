---
title: "Job Report: Bug Fix #021 - PNG 圖片資訊提取功能修復"
date: "2025-06-20T21:36:39Z"
---

# Bug Fix #021 - PNG 圖片資訊提取功能修復 工作報告

**日期**：2025-06-20T21:36:39Z  
**任務**：修復「從圖片生成提示詞」功能無法正確提取 PNG 圖片中嵌入的提示詞資訊，導致顯示空白結果的問題  
**類型**：Bug Fix  
**狀態**：已完成

## 一、任務概述

用戶在使用 Recipe 區域的「Generate Prompt From Image」功能時，拖拽包含提示詞資訊的 PNG 圖片後，系統無法正確提取並顯示圖片中嵌入的提示詞、負面提示詞和生成參數，導致相關欄位顯示為空白。

經過深入分析發現，問題出現在兼容性層的 `extract_png_info` 方法返回值處理上。該方法返回一個包含三個元素的元組 `(geninfo, generation_params, info_text)`，但多個動作文件中的程式碼錯誤地將整個元組當作字串處理，或直接傳遞給期望字串參數的函數，導致後續的提示詞解析失敗。

## 二、實作內容

### 2.1 修復 recipe_action.py 中的資料提取邏輯
- 修復 `on_recipe_generate_data_change` 函數中的返回值處理
- 正確提取元組的第一個元素（geninfo）作為參數字串
- 添加調試日誌以便追蹤提取過程
- 【F:scripts/civitai_manager_libs/recipe_action.py†L842-L886】

```python
def on_recipe_generate_data_change(recipe_img):
    """Process recipe PNG info with compatibility layer support"""
    generate_data = None
    if recipe_img:
        compat = CompatibilityLayer.get_compatibility_layer()

        if compat and hasattr(compat, 'metadata_processor'):
            try:
                # extract_png_info returns (geninfo, generation_params, info_text)
                # We need the first element (geninfo) which contains the parameters string
                result = compat.metadata_processor.extract_png_info(recipe_img)
                if result and result[0]:
                    generate_data = result[0]
                    data_len = len(generate_data) if generate_data else 0
                    util.printD(f"[RECIPE] Extracted via compatibility layer: {data_len} chars")
            except Exception as e:
                util.printD(f"Error processing PNG info through compatibility layer: {e}")
```

### 2.2 修復 ishortcut_action.py 中的類似問題
- 修復 `on_civitai_hidden_change` 函數的返回值處理
- 確保返回的是參數字串而不是整個元組
- 統一錯誤處理和後備機制
- 【F:scripts/civitai_manager_libs/ishortcut_action.py†L866-L901】

### 2.3 修復 civitai_gallery_action.py 中的相同模式
- 修復所有 PNG 資訊提取點的一致性行為
- 確保在不同模式下的返回值格式統一
- 【F:scripts/civitai_manager_libs/civitai_gallery_action.py†L347-L383】

## 三、技術細節

### 3.1 架構變更
- 統一了所有 PNG 資訊提取函數的返回值處理模式
- 改善了兼容性層與動作層之間的資料流處理
- 確保在 WebUI 模式和獨立模式下的一致行為

### 3.2 API 變更
- 無對外 API 變更，僅修復內部函數邏輯
- 保持現有介面的向後兼容性

### 3.3 配置變更
- 無配置檔案變更

## 四、測試與驗證

### 4.1 程式碼品質檢查
```bash
# 格式化檢查
python -m black --line-length=100 --skip-string-normalization scripts/civitai_manager_libs/recipe_action.py scripts/civitai_manager_libs/ishortcut_action.py scripts/civitai_manager_libs/civitai_gallery_action.py

# 建置測試
python -c "import scripts.civitai_manager_libs.recipe_action"

# 相關測試
python -m pytest tests/test_standalone_metadata_processor.py -v
python -m pytest tests/test_webui_metadata_processor.py -v
```

### 4.2 功能測試
建立了綜合測試腳本，驗證修復效果：
1. 創建包含嵌入參數的測試 PNG 圖片
2. 測試提取功能
3. 驗證正確提取正面提示詞、負面提示詞和選項參數
4. 確認修復解決了空白結果問題

測試結果顯示成功提取：
- ✅ 正面提示詞："beautiful landscape, detailed, masterpiece"
- ✅ 負面提示詞："blurry, low quality, bad anatomy"  
- ✅ 選項："Steps:20, Sampler:Euler a, CFG scale:7.5..."

### 4.3 集成測試
```bash
python -m pytest tests/test_integration.py -v
```
所有相關的 metadata processor 測試通過。

## 五、影響評估

### 5.1 向後相容性
- 修復不影響現有功能的正常運行
- 保持所有現有 API 介面不變
- 所有現有測試繼續通過

### 5.2 使用者體驗
- 「從圖片生成提示詞」功能現在正常工作
- 用戶可以正確看到從圖片中提取的提示詞資訊
- 提升了 Recipe 功能的可用性和用戶滿意度

## 六、問題與解決方案

### 6.1 遇到的問題
- **問題描述**：兼容性層的 `extract_png_info` 方法返回元組，但被錯誤當作字串處理
- **解決方案**：正確解構元組，僅提取包含參數字串的第一個元素

### 6.2 技術債務
- 解決了資料流處理不一致的技術債務
- 改善了錯誤處理和調試能力
- 統一了不同動作文件中的處理模式

## 七、後續事項

### 7.1 待完成項目
- [x] 修復主要的 PNG 資訊提取問題
- [x] 添加調試日誌和錯誤處理
- [x] 驗證修復效果

### 7.2 相關任務
- 關聯到用戶回報的「從圖片生成提示詞功能顯示空白」問題

### 7.3 建議的下一步
- 考慮為 PNG 資訊提取功能添加更多的自動化測試
- 監控用戶回饋，確保修復完全解決問題

## 八、檔案異動清單

| 檔案路徑 | 異動類型 | 描述 |
|---------|----------|------|
| `scripts/civitai_manager_libs/recipe_action.py` | 修改 | 修復 on_recipe_generate_data_change 函數的返回值處理邏輯 |
| `scripts/civitai_manager_libs/ishortcut_action.py` | 修改 | 修復 on_civitai_hidden_change 函數的返回值處理邏輯 |
| `scripts/civitai_manager_libs/civitai_gallery_action.py` | 修改 | 修復相同函數的返回值處理邏輯，確保一致性 |
| `.github/reports/021-png-info-extraction-fix-report.md` | 新增 | 工作報告文件 |
