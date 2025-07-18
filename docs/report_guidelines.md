# Civitai Shortcut 專案報告範本使用指南

本目錄包含 Civitai Shortcut 專案的工作報告範本，用於統一開發進度記錄格式。

## 範本檔案

### `REPORT_TEMPLATE.md` - 完整報告範本
適用於重要功能開發、架構變更、複雜 bug 修復等需要詳細記錄的任務。

**使用時機**：
- Backlog 實作
- 重大架構變更
- 複雜功能開發
- 需要詳細技術文件的變更

## 填寫指南

### 必填欄位
- `title`: 任務標題
- `任務`: 任務描述
- `實作內容`: 主要變更內容

### 檔案變更標記格式
使用格式：`【F:檔案路徑†L起始行-L結束行】`

**範例**：
- `【F:src/config.py†L1-L17】` - 檔案特定行範圍
- `【F:requirements.txt†L41-L43】` - 依賴項變更
- `【F:src/commands/mod.py†L1-L2】` - 模組宣告

### 任務類型標籤
- `Backlog` - 計劃性功能開發
- `Bug Fix` - 問題修復
- `Enhancement` - 功能改善
- `Refactor` - 程式碼重構
- `Test` - 測試相關變更

### 程式碼品質檢查
每個報告都應包含標準驗證步驟：
```bash
black --line-length=100 --skip-string-normalization tests
black --line-length=100 --skip-string-normalization scripts/civitai_manager_libs/compat
flake8 tests
flake8 scripts/civitai_manager_libs/compat
pytest -v
```

## 品質標準

### 報告品質要求
1. **完整性**: 記錄所有重要變更
2. **可追蹤性**: 包含檔案變更標記
3. **可驗證性**: 包含測試步驟和結果
4. **一致性**: 遵循範本格式

### 技術要求
1. 所有程式碼通過 `black` 格式化
2. 零 `flake8` 警告
3. 所有測試通過
4. 適當的程式碼覆蓋率（核心模組 >70%）

## 最佳實踐

1. **及時記錄**: 完成任務後立即撰寫報告
2. **詳細標記**: 準確標記檔案變更位置
3. **測試驗證**: 包含完整的測試步驟
4. **後續規劃**: 明確列出下一步行動
5. **影響評估**: 評估變更對系統的影響
6. **關聯項目**: 列出與本次變更相關的 issue
