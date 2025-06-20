# Bugfix Report: Standalone Mode PNG Info Extraction

## Summary
修正 Standalone 模式下，`extract_png_info` 接收 PIL Image 物件時導致型別錯誤（"stat: path should be string, bytes, os.PathLike or integer, not Image"）的問題。

## Problem
- 在 Standalone 模式下，Gradio UI 會將 `gr.Image(type="pil")` 產生的 PIL Image 物件直接傳給 `extract_png_info`，但介面原本僅接受檔案路徑字串
- 導致 `os.path.isfile` 等檔案操作出現 TypeError
- 錯誤發生在兼容層的 metadata processor 中

## Solution
### 1. 更新介面定義
- 修改 `IMetadataProcessor` 介面，讓 `extract_png_info` 和 `extract_parameters_from_png` 接受 `Union[str, Image.Image]` 類型輸入

### 2. 實現智能輸入處理
- **Standalone 模式**：直接處理 PIL Image 物件，無需創建臨時文件，提升性能
- **WebUI 模式**：為 PIL Image 創建臨時文件（因為 WebUI 模組需要文件路徑），並自動清理

### 3. 向後兼容性
- 保持對原有字串路徑參數的完全支持
- 所有現有功能和測試仍正常運作

## Testing
- ✅ 新增 PIL Image 輸入的專門測試案例
- ✅ 所有現有測試通過 (9/9 standalone, 10/10 compat layer)
- ✅ 集成測試通過，包括 PNG info 處理的後備測試
- ✅ 通過 `black` 與 `flake8` 格式檢查

## Impact
### 受益模組
- `civitai_gallery_action.py` - Civitai Gallery 圖片處理
- `ishortcut_action.py` - Shortcut 圖片資訊處理  
- `recipe_action.py` - Recipe 圖片參數提取

### 性能提升
- Standalone 模式下直接處理 PIL Image，避免不必要的文件 I/O
- 減少臨時文件創建和清理的開銷

## Files Modified
- `scripts/civitai_manager_libs/compat/interfaces/imetadata_processor.py`
- `scripts/civitai_manager_libs/compat/standalone_adapters/standalone_metadata_processor.py`
- `scripts/civitai_manager_libs/compat/webui_adapters/webui_metadata_processor.py`
- `tests/test_standalone_metadata_processor.py`

## Reference
- Issue: [Civitai Shortcut] Error processing PNG info through compatibility layer: stat: path should be string, bytes, os.PathLike or integer, not Image
- Test file: `tests/00004.webp` 用於驗證修復效果

---

🤖 修正者：GitHub Copilot <github-copilot[bot]@users.noreply.github.com>
日期：2025-06-20
