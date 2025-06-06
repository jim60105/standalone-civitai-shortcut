# Civitai Shortcut 獨立執行開發計劃

## 專案概述

本專案目標是讓 Civitai Shortcut 擴展具備獨立執行的能力，同時保持作為 AUTOMATIC1111/stable-diffusion-webui 擴展的相容性。透過建立包裝層（wrapper）來實現雙模式運行，避免大規模重構。

## 當前狀況分析

### 現有架構分析

1. **主要入口點**
   - `scripts/civitai_shortcut.py` - AUTOMATIC1111 擴展的主要入口
   - 透過 `script_callbacks.on_ui_tabs()` 註冊到 AUTOMATIC1111 的 UI 系統

2. **核心相依性**
   - **AUTOMATIC1111 模組相依**：
     - `modules.scripts` - 擴展基礎功能
     - `modules.script_callbacks` - UI 標籤註冊
     - `modules.shared` - 共享設定
     - `modules.infotext_utils` - 參數處理
     - `modules.extras` - PNG 資訊處理
     - `modules.sd_samplers` - 採樣器資訊

3. **外部套件相依性**
   - `gradio` - Web UI 框架
   - `requests` - HTTP 請求
   - `tqdm` - 進度條
   - Python 標準函式庫（os, json, datetime, threading 等）

4. **核心功能模組**
   - `civitai_manager_libs/` - 主要功能函式庫
   - 包含 22 個子模組，涵蓋模型管理、下載、分類、Recipe 等功能

## 開發策略

### 核心原則
1. **最小侵入性**：避免大規模修改現有程式碼
2. **相容性優先**：確保 AUTOMATIC1111 擴展功能不受影響
3. **模組化設計**：透過抽象層隔離相依性
4. **漸進式開發**：分階段實現獨立執行能力

## 詳細開發計劃

### 第一階段：相依性分析與抽象化設計 (1-2 週)

#### 1.1 建立相依性清單
- **高優先級任務**：
  1. 詳細分析每個 `modules.*` 相依性的使用方式
  2. 建立 AUTOMATIC1111 特定功能的使用清單
  3. 識別可替代或模擬的功能

- **具體步驟**：
  ```
  1. 掃描所有 Python 檔案中的 `from modules import` 語句
  2. 建立功能對應表：
     - modules.scripts.basedir() -> 擴展目錄路徑
     - modules.shared -> 全域設定變數
     - modules.infotext_utils -> 參數解析工具
     - modules.extras.run_pnginfo -> PNG metadata 解析
     - modules.sd_samplers -> 採樣器列表
  3. 評估每個功能的替代方案
  ```

#### 1.2 設計抽象介面
- **建立 `compat_layer.py`**：
  ```python
  # 示例結構
  class CompatibilityLayer:
      def __init__(self, mode='standalone'):
          self.mode = mode  # 'webui' 或 'standalone'
      
      def get_base_path(self):
          if self.mode == 'webui':
              from modules import scripts
              return scripts.basedir()
          else:
              return os.path.dirname(os.path.abspath(__file__))
      
      def get_shared_config(self, key, default=None):
          if self.mode == 'webui':
              from modules import shared
              return getattr(shared, key, default)
          else:
              return self._standalone_config.get(key, default)
  ```

### 第二階段：核心包裝層實作 (2-3 週)

#### 2.1 建立環境偵測機制
- **檔案**：`environment_detector.py`
- **功能**：
  1. 自動偵測執行環境（AUTOMATIC1111 vs 獨立）
  2. 根據環境設定適當的相容性層
  
- **實作邏輯**：
  ```python
  def detect_environment():
      try:
          import modules.scripts
          return 'webui'
      except ImportError:
          return 'standalone'
  ```

#### 2.2 實作 AUTOMATIC1111 功能模擬
- **檔案**：`webui_mock.py`
- **需要模擬的功能**：
  1. **基礎路徑管理**
     ```python
     def mock_basedir():
         return os.path.dirname(os.path.abspath(__file__))
     ```
  
  2. **PNG 資訊處理**
     ```python
     def mock_run_pnginfo(image):
         # 使用 PIL 或其他函式庫解析 PNG metadata
         from PIL import Image
         from PIL.ExifTags import TAGS
         # 實作邏輯...
     ```
  
  3. **參數處理**
     ```python
     def mock_parameters_copypaste():
         # 實作參數複製貼上功能
         pass
     ```

#### 2.3 建立設定管理系統
- **檔案**：`config_manager.py`
- **功能**：
  1. 獨立模式的設定檔管理
  2. 與 AUTOMATIC1111 設定的相容性
  3. 預設值與驗證

### 第三階段：獨立執行入口建立 (1-2 週)

#### 3.1 建立主要啟動腳本
- **檔案**：`main.py`
- **結構**：
  ```python
  #!/usr/bin/env python3
  import argparse
  import sys
  import os
  
  # 添加當前目錄到 Python 路徑
  sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
  
  from environment_detector import detect_environment
  from compat_layer import CompatibilityLayer
  
  def main():
      # 環境偵測
      env = detect_environment()
      
      # 初始化相容性層
      compat = CompatibilityLayer(mode=env)
      
      if env == 'standalone':
          # 獨立模式啟動
          launch_standalone()
      else:
          # AUTOMATIC1111 模式（現有邏輯）
          launch_webui_extension()
  
  def launch_standalone():
      import gradio as gr
      from scripts.civitai_manager_libs import setting
      
      # 初始化設定
      setting.init()
      
      # 建立 Gradio 介面
      with gr.Blocks(title="Civitai Shortcut") as app:
          # 建立 UI
          from scripts.civitai_shortcut import civitai_shortcut_ui
          civitai_shortcut_ui()
      
      # 啟動伺服器
      app.launch()
  
  if __name__ == "__main__":
      main()
  ```

#### 3.2 建立啟動設定檔
- **檔案**：`config.json`
- **內容**：
  ```json
  {
    "server": {
      "host": "127.0.0.1",
      "port": 7860,
      "share": false
    },
    "paths": {
      "models": "./models",
      "outputs": "./outputs"
    },
    "civitai": {
      "api_key": ""
    }
  }
  ```

### 第四階段：相依性隔離與替換 (2-3 週)

#### 4.1 模組修改策略
1. **最小化修改原則**：僅在必要時修改現有程式碼
2. **條件導入**：使用 try-except 處理可選相依性
3. **功能降級**：某些 AUTOMATIC1111 特定功能在獨立模式下可能不可用

#### 4.2 關鍵檔案修改
- **`scripts/civitai_manager_libs/setting.py`**：
  ```python
  # 在檔案開頭添加
  try:
      from modules import scripts, script_callbacks, shared
      WEBUI_MODE = True
  except ImportError:
      WEBUI_MODE = False
      # 導入替代實作
      from ..webui_mock import mock_basedir as basedir
      from ..config_manager import StandaloneConfig as shared
  
  # 修改路徑設定
  if WEBUI_MODE:
      extension_base = scripts.basedir()
  else:
      extension_base = basedir()
  ```

- **`scripts/civitai_manager_libs/util.py`**：
  ```python
  try:
      from modules import scripts, script_callbacks, shared
      WEBUI_MODE = True
  except ImportError:
      WEBUI_MODE = False
      from ..webui_mock import shared
  ```

#### 4.3 Gradio UI 適配
- 確保 UI 元件在獨立模式下正常運作
- 處理 AUTOMATIC1111 特定的 UI 整合部分

### 第五階段：套件管理與分發 (1 週)

#### 5.1 建立套件設定檔
- **檔案**：`requirements.txt`
  ```
  gradio>=3.41.2
  requests>=2.25.0
  tqdm>=4.60.0
  Pillow>=8.0.0
  ```

- **檔案**：`setup.py` 或 `pyproject.toml`
  ```python
  from setuptools import setup, find_packages
  
  setup(
      name="civitai-shortcut",
      version="2.0.0",
      packages=find_packages(),
      install_requires=[
          "gradio>=3.41.2",
          "requests>=2.25.0",
          "tqdm>=4.60.0",
          "Pillow>=8.0.0",
      ],
      entry_points={
          "console_scripts": [
              "civitai-shortcut=main:main",
          ],
      },
  )
  ```

#### 5.2 建立安裝腳本
- **檔案**：`install.sh` (Linux/macOS)
  ```bash
  #!/bin/bash
  python -m pip install -r requirements.txt
  echo "安裝完成！執行 'python main.py' 啟動應用程式"
  ```

- **檔案**：`install.bat` (Windows)
  ```batch
  @echo off
  python -m pip install -r requirements.txt
  echo 安裝完成！執行 'python main.py' 啟動應用程式
  pause
  ```

### 第六階段：測試與文件 (1-2 週)

#### 6.1 測試計劃
1. **AUTOMATIC1111 相容性測試**
   - 確保擴展在 AUTOMATIC1111 中正常運作
   - 測試所有現有功能
   
2. **獨立模式測試**
   - 測試獨立啟動
   - 測試核心功能（模型瀏覽、下載、分類等）
   - 測試 Civitai API 整合

3. **跨平台測試**
   - Windows、Linux、macOS 測試
   - 不同 Python 版本測試

#### 6.2 文件建立
- **更新 README.md**：
  ```markdown
  # 安裝方式
  
  ## 方式一：AUTOMATIC1111 擴展（現有方式）
  ...
  
  ## 方式二：獨立執行
  1. 複製儲存庫
  2. 安裝相依性：pip install -r requirements.txt
  3. 執行：python main.py
  ```

- **建立 STANDALONE_GUIDE.md**：
  - 獨立模式特定的設定說明
  - 功能差異說明
  - 故障排除指南

## 風險評估與應對策略

### 主要風險
1. **AUTOMATIC1111 相依性過度耦合**
   - **應對**：逐步解耦，建立抽象層
   - **備案**：部分功能在獨立模式下降級或停用

2. **UI 整合複雜性**
   - **應對**：保持 Gradio UI 結構不變
   - **備案**：建立簡化版獨立 UI

3. **功能完整性**
   - **應對**：優先確保核心功能可用
   - **備案**：建立功能差異文件

### 相容性策略
1. **向後相容**：確保現有 AUTOMATIC1111 使用者不受影響
2. **功能對等**：盡可能在獨立模式中提供相同功能
3. **漸進升級**：允許使用者逐步遷移到獨立模式

## 成功指標

1. **功能性指標**
   - AUTOMATIC1111 擴展功能 100% 保持
   - 獨立模式核心功能 90% 可用
   - 跨平台相容性 95%

2. **維護性指標**
   - 程式碼重複度低於 10%
   - 新增程式碼行數少於現有程式碼 30%

## 時程規劃

| 階段 | 時間 | 主要交付物 | 負責人員 |
|------|------|------------|----------|
| 第一階段 | 週 1-2 | 相依性分析報告、抽象介面設計 | 新進人員 + 導師 |
| 第二階段 | 週 3-5 | 包裝層實作、環境偵測機制 | 新進人員 |
| 第三階段 | 週 6-7 | 獨立執行入口、基本設定 | 新進人員 |
| 第四階段 | 週 8-10 | 相依性隔離、功能測試 | 新進人員 + 測試 |
| 第五階段 | 週 11 | 套件管理、分發準備 | 新進人員 |
| 第六階段 | 週 12-13 | 測試、文件、發布 | 全團隊 |

## 新進人員指導重點

### 第一週學習要點
1. **專案結構理解**
   - 閱讀現有程式碼，特別是主要入口點
   - 理解 AUTOMATIC1111 擴展機制
   - 熟悉 Gradio UI 框架

2. **關鍵概念掌握**
   - Civitai API 使用方式
   - 模型下載與管理機制
   - UI 元件互動邏輯

### 技術指導原則
1. **先理解再修改**：充分理解現有實作再進行變更
2. **小步快跑**：每次修改都要進行測試驗證
3. **文件先行**：重要決策都要記錄在文件中
4. **持續溝通**：遇到問題及時尋求協助

## 結論

此開發計劃採用漸進式、最小侵入性的方法，透過建立抽象層和包裝機制，實現 Civitai Shortcut 的雙模式運行能力。計劃強調相容性保持、風險控制和可維護性，適合新進人員在導師指導下執行。

