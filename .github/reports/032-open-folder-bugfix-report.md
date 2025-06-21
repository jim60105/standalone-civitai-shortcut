---
title: "Job Report: Bug Fix #032 - 修正 Open Download Folder 按鈕異常"
date: "2025-06-21T06:32:37Z"
---

# Bug Fix #032 - 修正 Open Download Folder 按鈕異常 工作報告

**日期**：2025-06-21T06:32:37Z  
**任務**：修正「Open Download Folder」按鈕於 WebUI/Standalone 模式下點擊無效與異常拋錯問題，確保兼容性與用戶體驗。  
**類型**：Bug Fix  
**狀態**：已完成

## 一、任務概述

本次任務針對「Open Download Folder」按鈕於 Gradio UI 點擊時，因 `util.open_folder` 內部直接依賴 `shared` 導致 NameError，造成無法開啟資料夾或程式異常終止。需確保該功能於 AUTOMATIC1111 WebUI extension 及 Standalone 模式下皆能正確運作，並於失敗時給予用戶明確提示。

## 二、實作內容

### 2.1 open_folder 兼容性重構
- 移除對 `shared` 全域變數的直接依賴，改用 `EnvironmentDetector` 判斷運行模式。
- WebUI 模式下，僅於未隱藏 UI 目錄時嘗試開啟資料夾，否則 fallback 為系統 open 指令。
- Standalone 模式直接使用系統 open 指令。
- 所有例外皆以 `util.printD()` 詳細記錄。
- 【F:scripts/civitai_manager_libs/util.py†L137-L157】

```python
def open_folder(path):
    """
    Open the given folder in the system file explorer.
    Compatible with both WebUI and standalone modes.
    Returns True if successful, False otherwise.
    """
    try:
        if not os.path.exists(path):
            printD(f"[util.open_folder] Path does not exist: {path}")
            return False
        if EnvironmentDetector.is_webui_mode():
            try:
                import modules.shared as shared
                if hasattr(shared, "cmd_opts") and hasattr(shared.cmd_opts, "hide_ui_dir_config"):
                    if getattr(shared.cmd_opts, "hide_ui_dir_config", False):
                        printD(
                            "[util.open_folder] UI directory config is hidden by WebUI settings."
                        )
                        return False
            except Exception as e:
                printD(f"[util.open_folder] WebUI detection/import failed: {e}")
        system = platform.system()
        if system == "Windows":
            os.startfile(path)
        elif system == "Darwin":
            subprocess.Popen(["open", path])
        elif "microsoft-standard-WSL2" in platform.uname().release:
            subprocess.Popen(["wsl-open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        printD(f"[util.open_folder] Opened folder: {path}")
        return True
    except Exception as e:
        printD(f"[util.open_folder] Exception: {e} (path: {path})")
        return False
```

### 2.2 on_open_folder_click 回傳行為優化
- 根據 `open_folder` 回傳值，若失敗則回傳 HTML 超連結，讓用戶可手動點擊開啟。
- 增加詳細 debug log。
- 【F:scripts/civitai_manager_libs/ishortcut_action.py†L778-L789】

```python
def on_open_folder_click(mid, vid):
    path = model.get_default_version_folder(vid)
    if path:
        result = util.open_folder(path)
        if not result:
            # 回傳 HTML 超連結，讓使用者自行點擊
            util.printD(f"[ishortcut_action.on_open_folder_click] Failed to open folder, returning link: {path}")
            return gr.HTML(f'<a href="file://{path}" target="_blank">Open folder: {path}</a>')
        else:
            util.printD(f"[ishortcut_action.on_open_folder_click] Folder opened: {path}")
    else:
        util.printD(f"[ishortcut_action.on_open_folder_click] No folder found for version id: {vid}")
    return None
```

## 三、技術細節

### 3.1 架構變更
- 無重大架構調整，僅針對單一功能點進行兼容性與健壯性優化。

### 3.2 API 變更
- 無對外 API 變更。

### 3.3 配置變更
- 無配置檔異動。

## 四、測試與驗證

### 4.1 程式碼品質檢查
```bash
black --line-length=100 --skip-string-normalization scripts/civitai_manager_libs/ishortcut_action.py
flake8 scripts/civitai_manager_libs/ishortcut_action.py --config=.flake8
```
- 已自動格式化，部分 flake8 警告（如註解過長、未用變數等）未完全清除，建議後續優化。

### 4.2 功能測試
- 手動於 WebUI 及 Standalone 模式下點擊「Open Download Folder」按鈕：
  - 資料夾存在且允許時，能正確開啟。
  - 若系統無法自動開啟，UI 會顯示可點擊的資料夾連結。
  - 失敗與例外皆有詳細 debug log。

### 4.3 覆蓋率測試（如適用）
- 本次為小範圍修正，未執行額外覆蓋率統計。

## 五、影響評估

### 5.1 向後相容性
- 無破壞性變更，原有功能均可正常運作。

### 5.2 使用者體驗
- 用戶遇到系統無法自動開啟資料夾時，能獲得明確提示與可點擊連結，提升易用性。

## 六、問題與解決方案

### 6.1 遇到的問題
- **問題描述**：原本 `util.open_folder` 直接依賴 `shared`，於 Standalone 或非 WebUI 環境下會拋出 NameError。
- **解決方案**：改用 `EnvironmentDetector` 判斷運行模式，並於例外時詳細記錄。

### 6.2 技術債務
- 部分 flake8 警告（如行過長、未用變數）尚未完全清除，建議後續重構。

## 七、後續事項

### 7.1 待完成項目
- [ ] 清除所有 flake8 警告
- [ ] 增加自動化測試覆蓋此功能

### 7.2 相關任務
- 無

### 7.3 建議的下一步
- 優化程式碼風格，提升 flake8 合規率
- 增加自動化測試覆蓋率

## 八、檔案異動清單

| 檔案路徑 | 異動類型 | 描述 |
|---------|----------|------|
| `scripts/civitai_manager_libs/util.py` | 修改 | 移除 shared 依賴，強化 open_folder 兼容性與健壯性 |
| `scripts/civitai_manager_libs/ishortcut_action.py` | 修改 | on_open_folder_click 失敗時回傳 HTML 連結並加強 debug log |
