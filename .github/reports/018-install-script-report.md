---
title: "Job Report: Chore #018 - Add install.py to install requirements"
date: "2025-06-19T20:13:13Z"
---

# [Chore] #018 - Add install.py to install requirements 工作報告

**日期**：2025-06-19T20:13:13Z  
**任務**：新增 `install.py`，使用 `launch` 工具自動安裝 `requirements.txt` 中列出的相依套件。

## 一、實作內容

### 1.1 新增自動安裝腳本
- 新增 `install.py`，解析 `requirements.txt`，並對每個需求判斷是否已安裝，若未安裝則透過 `launch.run_pip` 進行安裝。
- 檔案變更：【F:install.py†L1-L43】

## 二、驗證

```bash
# 代碼格式檢查
black --line-length=100 --skip-string-normalization install.py
flake8 install.py
```

結果：通過

---
**檔案異動**：
- install.py
