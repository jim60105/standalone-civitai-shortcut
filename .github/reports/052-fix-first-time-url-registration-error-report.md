---
title: "Job Report: Bug Fix #052 - 首次 URL 註冊顯示錯誤修復"
date: "2025-06-23T07:57:02Z"
---

# Bug Fix #052 - 首次 URL 註冊顯示錯誤修復 工作報告

**日期**：2025-06-23T07:57:02Z  
**任務**：修復獨立模式下首次於「Register Model」輸入框貼上 Civitai 模型 URL 時顯示 "Error" 的問題，確保後端處理成功時 UI 也能正確反映，並兼容 WebUI/Standalone 雙模式。  
**類型**：Bug Fix  
**狀態**：已完成

## 一、任務概述

本次任務針對 Civitai Shortcut 獨立模式下，首次於「Register Model」輸入框貼上 Civitai 模型 URL 時，UI 顯示 "Error"，但實際後端已成功處理的問題進行修復。經深入分析，發現主因為 Gradio Progress 物件在獨立模式下不相容，以及事件綁定時產生的循環依賴。目標為徹底解決此問題，並確保 WebUI/Standalone 雙模式皆穩定運作。

## 二、實作內容

### 2.1 修正 Progress 物件相容性
- 新增 MockProgress 類別，於獨立模式下取代 gr.Progress，避免不相容錯誤。
- 於 `on_civitai_internet_url_txt_upload` 函式內根據模式自動選用正確 Progress 物件。
- 【F:scripts/civitai_manager_libs/civitai_shortcut_action.py†L410-L470】

```python
class MockProgress:
    def tqdm(self, iterable, desc=""):
        return iterable
```

### 2.2 重構 Gradio 事件綁定，消除循環依賴
- 將 textbox 從主 handler 輸出移除，改用 .then() 於成功時清空 textbox，避免 Gradio 狀態錯亂。
- 標準化回傳值，僅於成功時回傳 model_id 觸發清空。
- 【F:scripts/civitai_manager_libs/civitai_shortcut_action.py†L260-L290】

```python
civitai_internet_url_txt.change(
    fn=on_civitai_internet_url_txt_upload,
    inputs=[civitai_internet_url_txt, register_information_only],
    outputs=[sc_modelid, refresh_sc_browser],
).then(
    fn=lambda success, timestamp: "" if isinstance(success, str) and success else None,
    inputs=[sc_modelid, refresh_sc_browser],
    outputs=[civitai_internet_url_txt],
)
```

### 2.3 除錯與測試腳本
- 撰寫多個 debug 及 end-to-end 測試腳本，驗證修正後各種情境皆正常。
- 清理除錯與測試檔案，保持專案整潔。

## 三、技術細節

### 3.1 架構變更
- 於事件處理流程中引入 MockProgress，並重構 UI 綁定邏輯，提升雙模式相容性。

### 3.2 API 變更
- 無對外 API 變更，僅內部事件處理與 UI 綁定優化。

### 3.3 配置變更
- 無配置檔或環境變數變更。

## 四、測試與驗證

### 4.1 程式碼品質檢查
```bash
black --line-length=100 --skip-string-normalization scripts/civitai_manager_libs/civitai_shortcut_action.py
flake8 scripts/civitai_manager_libs/civitai_shortcut_action.py
pytest -v
```

### 4.2 功能測試
- 啟動獨立模式，於 UI 貼上有效/無效/錯誤格式 URL，確認首次與多次皆無 "Error"，且成功時自動清空輸入框並顯示模型。
- 於 WebUI 模式重複測試，確認無副作用。
- 端對端測試腳本與手動驗證皆通過。

### 4.3 覆蓋率測試（如適用）
```bash
pytest --cov=scripts/civitai_manager_libs/civitai_shortcut_action --cov-report=term --cov-report=html
```

## 五、影響評估

### 5.1 向後相容性
- 完全相容 WebUI 模式，無影響現有功能。
- Standalone 模式首次註冊體驗大幅提升。

### 5.2 使用者體驗
- 首次貼上 URL 即可正確註冊模型，無需重試。
- UI 響應一致，無 "Error" 錯誤彈窗。

## 六、問題與解決方案

### 6.1 遇到的問題
- **問題描述**：首次貼上 URL 時 UI 顯示 "Error"，但後端已成功處理。
- **解決方案**：引入 MockProgress 取代 gr.Progress，並重構事件綁定消除循環依賴。

### 6.2 技術債務
- 無新增技術債務，反而簡化了事件處理流程。

## 七、後續事項

### 7.1 待完成項目
- [ ] 持續觀察 Gradio 版本升級對 Progress 物件的影響
- [ ] 強化 UI 測試自動化

### 7.2 相關任務
- 參考 Backlog 與歷史 bug 修復紀錄

### 7.3 建議的下一步
- 建議針對 UI 互動流程進行更細緻的自動化測試覆蓋

## 八、檔案異動清單

| 檔案路徑 | 異動類型 | 描述 |
|---------|----------|------|
| `scripts/civitai_manager_libs/civitai_shortcut_action.py` | 修改 | 修正 Progress 相容性與事件綁定邏輯 |
| `scripts/civitai_manager_libs/ishortcut_action.py` | 修改 | 除錯與測試期間暫時調整 |
