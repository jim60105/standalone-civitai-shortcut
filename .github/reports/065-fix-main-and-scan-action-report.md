---
title: "Job Report: Bug Fix #065 - Fix default host, queue settings and replace Box with Group in scan_action"
date: "2025-06-24T06:56:05Z"
---

# Bug Fix #065 - Fix default host, queue settings and replace Box with Group in scan_action 工作報告

**日期**：2025-06-24T06:56:05Z  
**任務**：修正 standalone 模式下的 Gradio 啟動參數與掃描頁面容器 API 變更  
**類型**：Bug Fix  
**狀態**：已完成

## 一、任務概述

執行 standalone 模式時，需:
- 將預設 host 設為 0.0.0.0 以允許外部存取。
- 在 Gradio queue 與 launch 中新增或調整參數，提升穩定性與相容性。
- 因 Gradio 4.x 移除 Box 容器，需將 scan_action 中的 gr.Box 改為 gr.Group。

## 二、實作內容

### 2.1 更新 main.py 中 Gradio 啟動參數
- 將 default host 從 `127.0.0.1` 修改為 `0.0.0.0`【F:main.py†L117-L122】
- 在 `self.app.queue` 中新增 `status_update_rate=3`【F:main.py†L151-L155】
- 在 `self.app.launch` 中新增 `ssl_verify=False, quiet=False` 以符合 Gradio API 並改善日誌顯示【F:main.py†L164-L167】

### 2.2 替換 scan_action 中的 Box 容器
- 將 `scripts/civitai_manager_libs/scan_action.py` 中的 `gr.Box` 改為 `gr.Group`，解決 Box 容器不再支援問題【F:scripts/civitai_manager_libs/scan_action.py†L42】

## 三、技術細節

### 3.1 API 相容性
- Gradio 4.x 更新：
  - `Box` 容器已被移除，改用 `Group`。
  - 增強 queue、launch 參數穩定性。

## 四、測試與驗證

### 4.1 程式碼品質檢查
```bash
black --line-length=100 --skip-string-normalization main.py scripts/civitai_manager_libs/scan_action.py
flake8 main.py scripts/civitai_manager_libs/scan_action.py || true
pytest tests/test_main.py tests/test_ui_adapter.py -q
timeout 5 python3 main.py --debug
```

### 4.2 功能測試
- 執行 `timeout 30 python3 main.py --debug`，確認不再因 API 變動報錯，介面正常啟動。

## 五、影響評估

### 5.1 向後相容性
- 僅調整內部 Gradio 事件呼叫與預設參數，對其他功能無影響。

### 5.2 使用者體驗
- 強化可連外部 access，並修正掃描頁面錯誤，提升使用流暢度。

## 六、後續事項

### 6.1 建議後續檢查
- 檢視其他使用 gr.Box 的模組，以確保無遺漏。

## 八、檔案異動清單

| 檔案路徑                                       | 異動類型 | 描述                                    |
|----------------------------------------------|--------|----------------------------------------|
| `main.py`                                    | 修改     | 更新 default host、queue 與 launch 參數           |
| `scripts/civitai_manager_libs/scan_action.py` | 修改     | 將 `gr.Box` 改為 `gr.Group`                     |
