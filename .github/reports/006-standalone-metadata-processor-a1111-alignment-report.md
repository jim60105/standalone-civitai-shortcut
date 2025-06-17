---
title: "Job Report: Refactor #006 - Standalone Metadata Processor A1111 Alignment"
date: "2025-06-17T20:18:44Z"
---

# Refactor #006 - Standalone Metadata Processor A1111 Alignment 工作報告

**日期**：2025-06-17T20:18:44Z
**任務**：依據 AUTOMATIC1111/stable-diffusion-webui 的原始碼，對本專案的 `StandaloneMetadataProcessor` 進行比對與重構，使其行為與 A1111 完全一致，並確保所有相關測試通過。
**類型**：Refactor
**狀態**：已完成

## 一、任務概述

既有的 `StandaloneMetadataProcessor` 在處理圖片資訊（infotext）時，其參數解析邏輯與 AUTOMATIC1111 Stable Diffusion WebUI 的原生實作存在不一致。本次任務的目標是深入分析 A1111 的原始碼，重構我們的實作，以達成 100% 的行為相容性，確保在獨立模式（Standalone Mode）下，對 PNG 資訊區塊的解析與生成結果與 A1111 完全相同。

## 二、實作內容

### 2.1 `StandaloneMetadataProcessor` 重構
- **檔案變更**: `scripts/civitai_manager_libs/compat/standalone_adapters/standalone_metadata_processor.py`
- **核心邏輯分析**: 深入研究 A1111 專案中的 `modules/images.py` 與 `modules/processing.py`，特別是 `parse_generation_parameters` 函數，以掌握其處理 infotext 的核心演算法。
- **參數解析重寫**: 完全重寫 `get_generation_parameters` 方法，以精確複製 A1111 的參數解析流程。這包括對 "Negative prompt"、"Steps" 以及其他鍵值對的處理，並採用了與 A1111 相同的正規表示式。
- **Prompt 提取修正**: 修改 `extract_prompt_from_parameters` 方法，使其能夠正確地從 infotext 中分離出正面提示詞（Prompt）、負面提示詞（Negative Prompt）以及參數字串。
- **介面新增**: 在 `IMetadataProcessor` 介面中新增 `set_debug_mode` 與 `validate_parameters` 方法，並在 `StandaloneMetadataProcessor` 中實作，以符合 A1111 的設計。

### 2.2 測試案例修正與依賴增補
- **檔案變更**: `tests/test_webui_function_simulation.py`
- **測試案例對齊**: 修正 `test_prompt_extraction` 測試案例，使其預期結果與 A1111 的實際行為（例如，負面提示詞不應包含參數行）保持一致。
- **環境依賴安裝**: 為測試環境安裝 `Pillow` 與 `piexif` 兩個必要的 Python 函式庫，以確保能正確處理圖片的元數據。

## 三、技術細節

本次重構的核心在於將 A1111 `parse_generation_parameters` 函數的邏輯，忠實地移植到 `StandaloneMetadataProcessor` 中。關鍵的技術點包括：

1.  **Infotext 結構**: A1111 的 infotext 分為三個主要部分：
    1.  正面提示詞 (Prompt)
    2.  負面提示詞 (Negative Prompt)，以 `Negative prompt:` 開頭
    3.  參數行 (Parameter Line)，包含 `Steps`, `Sampler`, `CFG scale` 等參數。

2.  **解析順序**: 解析器首先分離出正面與負面提示詞，剩餘的部分即為參數行。接著，從參數行中透過正規表示式逐一提取各項參數。

3.  **正則表達式**: 使用與 A1111 原始碼中完全相同的正規表示式 `re.compile(r"\s*([a-zA-Z\s]+):\s*([^,]+)(?:,|$)"` 來解析參數行，確保了鍵值對提取的準確性。

## 四、測試與驗證

### 4.1 程式碼品質檢查
在提交前，已對所有變更的檔案執行 `black` 與 `flake8` 進行格式化與風格檢查，確保符合專案規範。

```bash
# Black 格式化
black --line-length=100 --skip-string-normalization scripts/civitai_manager_libs/compat/standalone_adapters/standalone_metadata_processor.py tests/test_webui_function_simulation.py

# Flake8 檢查
flake8 scripts/civitai_manager_libs/compat/standalone_adapters/standalone_metadata_processor.py tests/test_webui_function_simulation.py
```

### 4.2 功能測試
透過 `pytest` 執行完整的測試套件。在多次修正後，最終所有 54 個測試案例均已成功通過，驗證了重構後的處理器行為符合預期，並與 A1111 的實作完全一致。

```bash
# 執行 Pytest
pytest
============================= test session starts ==============================
...
============================== 54 passed in 0.78s ==============================
```

## 五、影響評估

本次重構顯著提升了獨立模式下的可靠性與相容性。現在，由本工具生成或解析的 infotext 將與 A1111 WebUI 原生的產出完全一致。這消除了潛在的錯誤來源與使用者混淆，並確保了與其他基於 A1111 生態的工具之間的互操作性。

## 六、問題與解決方案

### 6.1 遇到的問題
- **問題描述**: 初步重構後，部分測試（特別是 `test_prompt_extraction`）失敗。根本原因在於對負面提示詞與參數行之間的分隔邏輯理解不夠精確。
- **解決方案**: 透過對 A1111 原始碼進行更深入的逐行分析，釐清了其先分離提示詞、後處理參數行的準確順序。據此修正 `extract_prompt_from_parameters` 的實作後，問題得以解決。

- **問題描述**: 執行測試時，系統回報缺少 `PIL` 與 `piexif` 模組。
- **解決方案**: 透過 `pip install Pillow piexif` 指令為開發環境安裝了必要的依賴，使測試得以順利執行。

## 七、後續事項

本次任務已全部完成，無後續事項。
