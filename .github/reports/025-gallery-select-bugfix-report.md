---
title: "Job Report: Bug Fix #026 - 修正 Gradio Gallery SelectData 事件處理異常"
date: "2025-06-20T23:42:39Z"
---

# Bug Fix #026 - 修正 Gradio Gallery SelectData 事件處理異常 工作報告

**日期**：2025-06-20T23:42:39Z  
**任務**：修正因 Gradio Gallery SelectData 事件 value 型態不一致導致的 AttributeError，確保所有圖庫選擇事件皆能正確處理字串與 list 輸入。  
**類型**：Bug Fix  
**狀態**：已完成

## 一、任務概述

本次任務針對 CIVITAI Shortcut 專案中，Gradio Gallery 組件的 SelectData 事件 value 可能為 list 或 str，導致 `get_modelid_from_shortcutname` 及多個事件處理函數出現 `AttributeError: 'list' object has no attribute 'rfind'` 的問題進行修正。目標為：
- 使所有圖庫選擇事件能正確處理 value 為 list 或 str 的情境
- 增強錯誤處理與除錯資訊
- 補齊單元測試覆蓋所有分支

## 二、實作內容

### 2.1 增強 get_modelid_from_shortcutname 型態處理
- 支援 value 為 list 或 str，並加強型態檢查與說明
- 【F:scripts/civitai_manager_libs/setting.py†L623-L650】

```python
def get_modelid_from_shortcutname(sc_name):
    """Extract model ID from shortcut name.
    Args:
        sc_name: Shortcut name in format "name:id", or list containing shortcut name
    Returns:
        str: Model ID if found, None otherwise
    """
    if not sc_name:
        return None
    if isinstance(sc_name, list):
        if len(sc_name) > 1:
            sc_name = sc_name[1]
        elif len(sc_name) == 1:
            sc_name = sc_name[0]
        else:
            return None
    if not isinstance(sc_name, str):
        return None
    colon_pos = sc_name.rfind(':')
    if colon_pos != -1:
        return sc_name[colon_pos + 1:]
    return None
```

### 2.2 修正所有受影響的圖庫選擇事件處理
- 統一處理 value 為 list 或 str，並加強異常輸出
- 【F:scripts/civitai_manager_libs/recipe_action.py†L1190-L1220】
- 【F:scripts/civitai_manager_libs/classification_action.py†L550-L590】
- 【F:scripts/civitai_manager_libs/recipe_browser_page.py†L424-L485】

## 三、技術細節

### 3.1 架構變更
- 無重大架構調整，僅針對型態處理與事件分支加強

### 3.2 API 變更
- 無對外 API 變更，僅內部事件處理與工具函數增強

### 3.3 配置變更
- 無

## 四、測試與驗證

### 4.1 程式碼品質檢查
```bash
black --line-length=100 --skip-string-normalization tests
black --line-length=100 --skip-string-normalization scripts/civitai_manager_libs/compat
flake8 tests
flake8 scripts/civitai_manager_libs/compat
pytest -v
```

### 4.2 功能測試
- 手動於 WebUI 及 Standalone 模式下，點擊圖庫各類選擇，確認無異常
- 單元測試覆蓋所有分支，包含 list/str/None/異常型態

### 4.3 覆蓋率測試（如適用）
```bash
pytest --cov=scripts/civitai_manager_libs/compat --cov-report=term --cov-report=html
```

## 五、影響評估

### 5.1 向後相容性
- 完全相容，原有功能不受影響，僅增強型態健壯性

### 5.2 使用者體驗
- 修正圖庫選擇異常，提升穩定性與錯誤提示

## 六、問題與解決方案

### 6.1 遇到的問題
- **問題描述**：Gradio Gallery SelectData 事件 value 型態不一致，導致處理失敗
- **解決方案**：統一型態判斷與分支處理，並補齊單元測試

### 6.2 技術債務
- 無新增技術債務

## 七、後續事項

### 7.1 待完成項目
- [ ] 持續追蹤其他 Gradio 事件型態處理一致性
- [ ] 增加更多整合測試

### 7.2 相關任務
- #022, #023, #024

### 7.3 建議的下一步
- 建議審查所有 Gradio 事件處理型態，並補齊自動化測試

## 八、檔案異動清單

| 檔案路徑 | 異動類型 | 描述 |
|---------|----------|------|
| `scripts/civitai_manager_libs/setting.py` | 修改 | 增強型態處理與說明 |
| `scripts/civitai_manager_libs/recipe_action.py` | 修改 | 修正圖庫選擇事件型態處理 |
| `scripts/civitai_manager_libs/classification_action.py` | 修改 | 修正圖庫選擇事件型態處理 |
| `scripts/civitai_manager_libs/recipe_browser_page.py` | 修改 | 修正圖庫選擇事件型態處理 |
| `tests/test_gallery_select_fix.py` | 新增 | 單元測試覆蓋所有分支 |
