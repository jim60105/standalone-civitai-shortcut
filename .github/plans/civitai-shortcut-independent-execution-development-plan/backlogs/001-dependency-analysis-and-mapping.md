# Backlog 001: 相依性分析與對應表建立

## 優先級
**高 (Critical)** - 此項目是後續開發的基礎，必須優先完成

## 估算工作量
**5-8 工作天**

## 目標描述
建立完整的 AUTOMATIC1111 相依性分析報告，並建立功能對應表，為後續的抽象化設計提供詳細的技術規格。

## 接受標準 (Definition of Done)
1. ✅ 完成所有 `modules.*` 相依性的使用方式分析
2. ✅ 建立功能對應表文件，包含每個相依功能的替代方案
3. ✅ 識別出高風險相依性（難以替代的功能）
4. ✅ 建立相依性分類（核心/可選/可替代）
5. ✅ 提供每個相依性的測試方法

## 詳細任務

### 任務 1.1: 程式碼掃描與相依性提取
**預估時間：2 天**

1. **掃描所有 Python 檔案**
   ```bash
   # 在專案根目錄執行以下命令來找出所有的 modules 匯入
   find scripts/ -name "*.py" -exec grep -H "from modules" {} \;
   find scripts/ -name "*.py" -exec grep -H "import modules" {} \;
   ```

2. **建立相依性清單**
   建立一個 Excel/CSV 檔案或 Markdown 表格，包含：
   - 檔案路徑
   - 匯入的模組名稱
   - 使用的功能/方法
   - 使用頻率（在程式碼中出現的次數）
   - 使用情境描述

3. **預期輸出檔案**: `dependency_analysis.md`

### 任務 1.2: 功能使用方式深度分析  
**預估時間：3 天**

對每個發現的相依性進行詳細分析：

1. **modules.scripts 分析**
   - `scripts.basedir()` - 取得擴展基礎目錄路徑
   - 使用情境：檔案路徑建構、資源載入
   - 替代方案：`os.path.dirname(os.path.abspath(__file__))`

2. **modules.shared 分析**  
   - 共享設定變數存取
   - 使用情境：全域設定讀取/寫入
   - 替代方案：獨立的設定管理系統

3. **modules.infotext_utils 分析**
   - 參數解析與處理工具
   - 使用情境：prompt 參數解析
   - 替代方案：自訂解析函式

4. **modules.extras 分析**
   - `run_pnginfo()` - PNG metadata 解析
   - 使用情境：圖片資訊提取
   - 替代方案：使用 PIL/Pillow 函式庫

5. **modules.sd_samplers 分析**
   - 採樣器列表取得
   - 使用情境：UI 選項顯示
   - 替代方案：靜態列表或設定檔

### 任務 1.3: 風險評估與分類
**預估時間：1 天**

將每個相依性分類：

1. **核心相依性** (Critical Dependencies)
   - 應用程式無法運行沒有的功能
   - 需要完整替代實作

2. **重要相依性** (Important Dependencies)  
   - 影響主要功能但可以降級處理
   - 需要部分替代或 fallback 機制

3. **可選相依性** (Optional Dependencies)
   - 僅影響次要功能
   - 可以在獨立模式下停用

### 任務 1.4: 替代方案研究
**預估時間：2 天**

為每個相依性研究可行的替代方案：

1. **評估現有 Python 套件**
   - 研究是否有現成的函式庫可以替代
   - 評估效能與相容性

2. **自訂實作方案**
   - 評估自行實作的複雜度
   - 估算開發時間

3. **功能降級方案**
   - 識別哪些功能可以簡化
   - 設計降級後的使用者體驗

## 交付物

### 主要文件

> 所有文件都放在 `.github/plans/civitai-shortcut-independent-execution-development-plan` 目錄下，使用 Markdown 格式編寫。

1. **`dependency_analysis.md`** - 完整的相依性分析報告
2. **`function_mapping.md`** - 功能對應表
3. **`risk_assessment.md`** - 風險評估報告
4. **`alternative_solutions.md`** - 替代方案研究報告

### 文件結構範例

```markdown
# dependency_analysis.md

## 相依性總覽
| 模組 | 使用頻率 | 風險級別 | 替代難度 |
|------|----------|----------|----------|
| modules.scripts | 15次 | 低 | 簡單 |
| modules.shared | 8次 | 中 | 中等 |
| ... | ... | ... | ... |

## 詳細分析
### modules.scripts
- **使用方式**: basedir() 函式取得基礎路徑
- **程式碼位置**: scripts/civitai_manager_libs/setting.py:25
- **替代方案**: os.path.dirname(os.path.abspath(__file__))
- **實作複雜度**: 低
- **測試方法**: 確認路徑正確性
```

## 技術要求

### 品質檢查清單
- [ ] 所有 `from modules import` 語句都已記錄
- [ ] 每個相依性都有清楚的使用情境描述  
- [ ] 風險評估基於實際技術限制
- [ ] 替代方案具有可行性
- [ ] 文件格式一致且易於閱讀

## 後續連接
完成此項目後，繼續執行：
- **Backlog 002**: 抽象介面設計
- **Backlog 003**: 環境偵測機制建立
