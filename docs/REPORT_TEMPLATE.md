# [任務類型] [任務標題] 工作報告

**任務**：[簡要描述此次任務的目標與範圍]  
**類型**：[Backlog | Bug Fix | Enhancement | Refactor | Test]  
**狀態**：[進行中 | 已完成 | 部分完成]

## 一、任務概述

[詳細描述任務背景、需求和目標]

## 二、實作內容

### 2.1 [子任務一標題]
- [實作內容描述]
- [檔案變更說明，使用格式：【F:檔案路徑†L起始行-L結束行】]

```python
// 程式碼範例（如需要）
[程式碼片段]
```

### 2.2 [子任務二標題]
- [實作內容描述]
- [檔案變更說明]

## 三、技術細節

### 3.1 架構變更
- [描述架構層面的變更]

### 3.2 API 變更
- [描述對外 API 的變更]

### 3.3 配置變更
- [描述配置檔或環境變數的變更]

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
- [描述手動測試步驟與結果]

### 4.3 覆蓋率測試（如適用）
```bash
pytest --cov=scripts/civitai_manager_libs/compat --cov-report=term --cov-report=html
```

## 五、影響評估

### 5.1 向後相容性
- [描述此變更對現有功能的影響]

### 5.2 使用者體驗
- [描述對使用者體驗的改善]

## 六、問題與解決方案

### 6.1 遇到的問題
- **問題描述**：[描述遇到的問題]
- **解決方案**：[描述如何解決]

### 6.2 技術債務
- [列出此次變更產生或解決的技術債務]

## 七、後續事項

### 7.1 待完成項目
- [ ] [待完成項目一]
- [ ] [待完成項目二]

### 7.2 建議的下一步
- [建議後續應進行的任務]

## 八、檔案異動清單

| 檔案路徑 | 異動類型 | 描述 |
|---------|----------|------|
| `src/example.py` | 新增 | [描述] |
| `src/other.py` | 修改 | [描述] |
| `requirements.txt` | 修改 | [描述] |

### 九、關聯項目

Resolves #[issue_number]

> [!TIP]  
> The word `Resolves` must remain in English and be used as is.
> (Do not include this tip in the final report)
