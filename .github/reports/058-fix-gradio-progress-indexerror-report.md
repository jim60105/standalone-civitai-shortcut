---
title: "Job Report: Bug Fix #058 - 修復 Gradio Progress 物件 IndexError 異常"
date: "2025-06-23T21:55:14Z"
---

# Bug Fix #058 - 修復 Gradio Progress 物件 IndexError 異常 工作報告

**日期**：2025-06-23T21:55:14Z  
**任務**：修復在模型圖片下載過程中發生的 IndexError 異常  
**類型**：Bug Fix  
**狀態**：已完成

## 一、任務概述

修復在註冊新模型時發生的 `IndexError: list index out of range` 錯誤。該錯誤出現在 `_setup_progress_tracking` 函數中，當檢查 Gradio Progress 物件是否為 falsy 時，會觸發 Progress 物件的 `__len__` 方法，但該方法在 `iterables` 清單為空時會嘗試存取 `self.iterables[-1].length`，導致 IndexError。

根據錯誤日誌分析，問題的具體調用鏈為：
1. 用戶嘗試註冊新模型 (model ID: 752237)
2. 系統開始下載模型圖片
3. 在 `_setup_progress_tracking` 函數中執行 `if not progress:` 檢查
4. Gradio Progress 物件的 `__len__` 方法被調用
5. 由於 `iterables` 清單為空，存取 `iterables[-1]` 時發生 IndexError

## 二、實作內容

### 2.1 修復 Progress 物件檢查邏輯
- 將 `if not progress:` 改為 `if progress is None:`，避免觸發 Gradio Progress 物件的 `__len__` 方法
- 【F:scripts/civitai_manager_libs/ishortcut.py†L881-L881】

```python
# 修改前：
if not progress:

# 修改後：
if progress is None:
```

### 2.2 保持異常處理機制
- 維持原有的 try-catch 結構，確保其他類型的異常也能被正確處理
- 【F:scripts/civitai_manager_libs/ishortcut.py†L887-L892】

## 三、技術細節

### 3.1 根本原因分析
問題的根本原因是 Gradio v3.41.2 中 Progress 物件的 `__len__` 方法實現：
```python
def __len__(self):
    return self.iterables[-1].length  # 當 iterables 為空時會出錯
```

### 3.2 解決方案選擇
選擇使用 `is None` 檢查而非 falsy 檢查的原因：
1. **避免觸發特殊方法**：`is None` 是身份檢查，不會觸發 `__len__`、`__bool__` 等特殊方法
2. **明確的語義**：更清楚地表達我們要檢查的是 None 值，而非任何 falsy 值
3. **性能考量**：身份檢查比 falsy 檢查更快
4. **向前相容性**：與未來版本的 Gradio 相容性更好

### 3.3 影響範圍
此修改僅影響 `_setup_progress_tracking` 函數，不會影響其他使用 progress 物件的地方。

## 四、測試與驗證

### 4.1 程式碼品質檢查
```bash
black --line-length=100 --skip-string-normalization scripts/civitai_manager_libs/ishortcut.py
flake8 scripts/civitai_manager_libs/ishortcut.py
```

### 4.2 功能測試
- 建立了專門的測試腳本驗證修復效果
- 模擬 Gradio Progress 物件的問題行為
- 確認修復後不再出現 IndexError
- 驗證 None 進度物件的正確處理

### 4.3 回歸測試
```bash
pytest -v
```
- 所有 420 個測試案例通過
- 無新增的測試失敗

## 五、影響評估

### 5.1 向後相容性
- **相容性**：100% 向後相容
- **行為變更**：無行為變更，僅修復錯誤
- **API 穩定性**：API 介面保持不變

### 5.2 使用者體驗
- **問題解決**：用戶現在可以正常註冊新模型，不會遇到 IndexError
- **功能恢復**：圖片下載功能完全恢復正常
- **穩定性提升**：減少了異常中斷的情況

## 六、問題與解決方案

### 6.1 遇到的問題
- **問題描述**：Gradio Progress 物件的 `__len__` 方法在 iterables 為空時會拋出 IndexError
- **解決方案**：改用 `is None` 檢查避免觸發 `__len__` 方法

### 6.2 技術債務
- **解決的債務**：修復了一個會導致功能完全失效的關鍵錯誤
- **新增的債務**：無

## 七、後續事項

### 7.1 待完成項目
- [x] 驗證修復效果
- [x] 執行回歸測試
- [x] 程式碼品質檢查

### 7.2 相關任務
- 此問題與之前的 HTTP 客戶端重構相關，但屬於獨立的錯誤處理問題

### 7.3 建議的下一步
- 考慮在其他地方檢查是否有類似的 Gradio Progress 物件使用模式
- 評估是否需要升級到更新版本的 Gradio

## 八、檔案異動清單

| 檔案路徑 | 異動類型 | 描述 |
|---------|----------|------|
| `scripts/civitai_manager_libs/ishortcut.py` | 修改 | 修復 `_setup_progress_tracking` 函數中的 Progress 物件檢查邏輯 |
