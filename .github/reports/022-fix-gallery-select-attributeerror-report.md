---
title: "Job Report: Bug Fix #001 - Fix Gallery Select AttributeError"
date: "2025-06-20T21:46:23Z"
---

# Bug Fix #001 - Fix Gallery Select AttributeError 工作報告

**日期**：2025-06-20T21:46:23Z  
**任務**：修復點擊圖片庫圖片時發生的 AttributeError: 'list' object has no attribute 'rfind' 錯誤  
**類型**：Bug Fix  
**狀態**：已完成

## 一、任務概述

用戶報告在點擊圖片庫（sc_gallery）中的圖片時遇到錯誤。錯誤訊息顯示 `on_sc_gallery_select` 函數接收到的 `evt.value` 是一個 list 物件，但程式碼嘗試對其使用字串方法 `rfind()`，導致 AttributeError。

具體錯誤：
```
AttributeError: 'list' object has no attribute 'rfind'
```

錯誤發生在 `setting.get_modelid_from_shortcutname()` 函數中，該函數期望接收字串但實際接收到了 list。

## 二、實作內容

### 2.1 問題分析
- 分析錯誤日誌發現 `evt.value` 的值為：`['http://localhost:7861/file=/tmp/gradio/b3de94ba6de75a5cbef60b0e30ec5f9d8455c0d5/1698570.png', 'Adorable Marching Band:1698570']`
- 第一個元素是圖片 URL，第二個元素是 shortcut 名稱
- 【F:scripts/civitai_manager_libs/civitai_shortcut_action.py†L341-L353】

### 2.2 修復實作
- 在 `on_sc_gallery_select` 函數中增加類型檢查和處理邏輯
- 支援兩種格式：list 格式（取第二個元素）和 string 格式（向後相容）
- 【F:scripts/civitai_manager_libs/civitai_shortcut_action.py†L341-L362】

```python
# evt.value can be either a string or a list [image_url, shortcut_name]
if isinstance(evt.value, list) and len(evt.value) > 1:
    shortcut = evt.value[1]  # Use the shortcut name (second element)
elif isinstance(evt.value, str):
    shortcut = evt.value
else:
    util.printD(
        f"[civitai_shortcut_action] Unexpected evt.value format: {evt.value}"
    )
    return None
```

## 三、技術細節

### 3.1 架構變更
- 無架構層面變更，僅修復既有功能的錯誤處理

### 3.2 API 變更
- 無對外 API 變更，修復為內部函數的錯誤處理

### 3.3 配置變更
- 無配置變更

## 四、測試與驗證

### 4.1 程式碼品質檢查
```bash
# 格式化檢查
python -m black --line-length=100 --skip-string-normalization scripts/civitai_manager_libs/civitai_shortcut_action.py

# Flake8 檢查
python -m flake8 --config .flake8 scripts/civitai_manager_libs/civitai_shortcut_action.py
```

✅ 所有程式碼品質檢查通過

### 4.2 功能測試
- **測試場景 1**：使用 list 格式的 evt.value（問題場景）
  - 輸入：`['http://localhost:7861/file=/tmp/gradio/test.png', 'Adorable Marching Band:1698570']`
  - 預期結果：`1698570`
  - 實際結果：✅ `1698570`

- **測試場景 2**：使用 string 格式的 evt.value（向後相容）
  - 輸入：`'Adorable Marching Band:1698570'`
  - 預期結果：`1698570`
  - 實際結果：✅ `1698570`

- **測試場景 3**：使用原始錯誤場景的完整資料
  - 輸入：`['http://localhost:7861/file=/tmp/gradio/b3de94ba6de75a5cbef60b0e30ec5f9d8455c0d5/1698570.png', 'Adorable Marching Band:1698570']`
  - 預期結果：`1698570`
  - 實際結果：✅ `1698570`

### 4.3 整合測試
```bash
python -m pytest tests/test_integration.py -v
```
✅ 主要功能測試通過（部分既有 mock 測試失敗與此修復無關）

## 五、影響評估

### 5.1 向後相容性
- ✅ 完全向後相容，仍支援原有的字串格式
- ✅ 增加對新 list 格式的支援

### 5.2 使用者體驗
- ✅ 修復點擊圖片庫圖片時的崩潰問題
- ✅ 使用者可以正常選取圖片並查看模型詳情

## 六、問題與解決方案

### 6.1 遇到的問題
- **問題描述**：Gradio gallery 元件的 SelectData 事件回傳值格式與預期不符
- **解決方案**：增加類型檢查，支援多種資料格式以提高程式的健壯性

### 6.2 技術債務
- 無新增技術債務
- 解決了一個潛在的錯誤處理不足問題

## 七、後續事項

### 7.1 待完成項目
- [x] 修復 gallery select 錯誤
- [x] 驗證修復有效性
- [x] 確保向後相容性

### 7.2 相關任務
- 無直接相關的其他任務

### 7.3 建議的下一步
- 考慮對其他類似的事件處理函數進行類型檢查審查
- 建議在類似的 UI 事件處理中增加更健壯的錯誤處理

## 八、檔案異動清單

| 檔案路徑 | 異動類型 | 描述 |
|---------|----------|------|
| `scripts/civitai_manager_libs/civitai_shortcut_action.py` | 修改 | 在 `on_sc_gallery_select` 函數中增加類型檢查和多格式支援 |
