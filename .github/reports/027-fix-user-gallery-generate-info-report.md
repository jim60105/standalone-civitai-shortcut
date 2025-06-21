---
title: "Job Report: Bug Fix #027 - 修正 Civitai User Gallery 點選圖片無法顯示 Generate Info"
date: "2025-06-21T02:23:28Z"
---

# Bug Fix #027 - 修正 Civitai User Gallery 點選圖片無法顯示 Generate Info 工作報告

**日期**：2025-06-21T02:23:28Z  
**任務**：修正於「Civitai User Gallery」分頁點選圖片時，無法正確顯示該圖片的 Generate Info（生成參數）問題。  
**類型**：Bug Fix  
**狀態**：已完成

## 一、任務概述

本次任務針對 Civitai Shortcut 專案中「Civitai User Gallery」分頁，使用者點選圖片時，Generate Info 欄位無法顯示該圖片的生成參數（如 prompt、seed 等）。經分析發現，事件回傳的圖片資訊為 URL 而非本地檔案路徑，導致 PNG info 提取失敗。

## 二、實作內容

### 2.1 Gallery 選取事件修正
- 修正 `on_gallery_select`，確保傳遞本地圖片檔案路徑給 PNG info 提取邏輯。
- 若選取為 URL，則自動轉換為本地 gallery file path。
- 增加 debug log 以利日後追蹤。
- 【F:scripts/civitai_manager_libs/civitai_gallery_action.py†L410-L430】

```python
    def on_gallery_select(evt: gr.SelectData, civitai_images):
        """Ensure local file path is passed to hidden for PNG info extraction."""
        selected = civitai_images[evt.index]
        util.printD(f"[civitai_gallery_action] on_gallery_select: selected={selected}")
        if isinstance(selected, str) and selected.startswith("http"):
            from . import setting
            local_path = setting.get_image_url_to_gallery_file(selected)
            util.printD(f"[civitai_gallery_action] on_gallery_select: converted URL to local_path={local_path}")
            return evt.index, local_path, gr.update(selected="Image_Information")
        return evt.index, selected, gr.update(selected="Image_Information")
```

### 2.2 測試與驗證
- 執行所有單元測試與整合測試，確保修正不影響其他功能。
- 【F:tests/ 全部】

## 三、技術細節

### 3.1 架構變更
- 無架構層級變更，僅修正 callback 資料流。

### 3.2 API 變更
- 無對外 API 變更。

### 3.3 配置變更
- 無配置檔異動。

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
- 手動於 WebUI/Standalone 模式下，點選 User Gallery 圖片，確認 Generate Info 正常顯示。
- 所有自動化測試（pytest）均通過。

### 4.3 覆蓋率測試（如適用）
```bash
pytest --cov=scripts/civitai_manager_libs/compat --cov-report=term --cov-report=html
```

## 五、影響評估

### 5.1 向後相容性
- 僅修正資料流，對現有功能無破壞性影響。

### 5.2 使用者體驗
- 使用者可於 User Gallery 正常取得圖片生成參數，體驗大幅提升。

## 六、問題與解決方案

### 6.1 遇到的問題
- **問題描述**：圖片選取事件傳遞 URL，導致 PNG info 提取失敗。
- **解決方案**：事件 callback 轉換 URL 為本地檔案路徑，確保 info 提取成功。

### 6.2 技術債務
- 無新增技術債務。

## 七、後續事項

### 7.1 待完成項目
- [ ] 無

### 7.2 相關任務
- #026-fix-user-gallery-generate-info-report

### 7.3 建議的下一步
- 持續監控 gallery 選取事件資料流，確保未來擴充時不再出現類似問題。

## 八、檔案異動清單

| 檔案路徑 | 異動類型 | 描述 |
|---------|----------|------|
| `scripts/civitai_manager_libs/civitai_gallery_action.py` | 修改 | 修正 gallery 選取事件，確保傳遞本地檔案路徑 |
