# Backlog 004: 獨立執行入口與主程式建立

## 優先級
**高 (Critical)** - 建立獨立執行的主要入口點，使應用程式具備獨立運行能力

## 估算工作量
**6-8 工作天**

## 目標描述
建立獨立執行模式的主程式入口點，包含命令列介面、Gradio 伺服器啟動、設定載入、以及完整的應用程式生命週期管理。確保使用者可以透過簡單的命令啟動應用程式。

## 接受標準 (Definition of Done)
1. ✅ 建立功能完整的主程式 `main.py`
2. ✅ 實作命令列參數解析和處理
3. ✅ 建立 Gradio 伺服器啟動邏輯
4. ✅ 整合相容性層和所有必要元件
5. ✅ 實作應用程式生命週期管理（啟動、執行、關閉）
6. ✅ 建立使用者友善的啟動腳本
7. ✅ 通過獨立執行測試

## 詳細任務

### 任務 4.1: 主程式架構設計
**預估時間：2 天**

1. **設計主程式結構**
   ```python
   # main.py
   #!/usr/bin/env python3
   """
   Civitai Shortcut 獨立執行主程式
   
   此程式提供 Civitai Shortcut 的獨立執行能力，
   無需依賴 AUTOMATIC1111 WebUI 環境。
   """
   
   import sys
   import os
   import argparse
   import logging
   from typing import Optional
   
   # 確保能夠找到專案模組
   project_root = os.path.dirname(os.path.abspath(__file__))
   sys.path.insert(0, project_root)
   sys.path.insert(0, os.path.join(project_root, 'scripts'))
   
   # 主要應用程式類別
   class CivitaiShortcutApp:
       """Civitai Shortcut 獨立應用程式"""
       
       def __init__(self, config_path: Optional[str] = None):
           self.config_path = config_path
           self.app = None
           self.compat_layer = None
           self._setup_logging()
           self._initialize_components()
       
       def _setup_logging(self):
           """設定記錄系統"""
           logging.basicConfig(
               level=logging.INFO,
               format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
               handlers=[
                   logging.FileHandler('civitai_shortcut.log'),
                   logging.StreamHandler(sys.stdout)
               ]
           )
           self.logger = logging.getLogger(__name__)
       
       def _initialize_components(self):
           """初始化核心元件"""
           from scripts.civitai_manager_libs.compat_layer import CompatibilityLayer
           from scripts.civitai_manager_libs.environment_detector import EnvironmentDetector
           
           # 強制設定為獨立模式
           self.compat_layer = CompatibilityLayer(mode='standalone')
           
           # 初始化設定
           self._setup_config()
           
           self.logger.info("Civitai Shortcut initialized in standalone mode")
       
       def _setup_config(self):
           """設定應用程式設定"""
           if self.config_path:
               self.compat_layer.config_manager.load_config(self.config_path)
           
           # 確保必要目錄存在
           self.compat_layer.path_manager.ensure_directories()
       
       def create_interface(self):
           """建立 Gradio 使用者介面"""
           import gradio as gr
           from scripts.civitai_shortcut import create_civitai_shortcut_ui
           
           with gr.Blocks(
               title="Civitai Shortcut - Standalone",
               theme=gr.themes.Soft(),
               css_paths=[os.path.join(project_root, "style.css")]
           ) as app:
               # 建立主要 UI
               create_civitai_shortcut_ui(self.compat_layer)
           
           self.app = app
           return app
       
       def launch(self, 
                 host: str = "127.0.0.1", 
                 port: int = 7860, 
                 share: bool = False,
                 **kwargs):
           """啟動應用程式"""
           if not self.app:
               self.create_interface()
           
           self.logger.info(f"Starting Civitai Shortcut on {host}:{port}")
           
           try:
               self.app.launch(
                   server_name=host,
                   server_port=port,
                   share=share,
                   **kwargs
               )
           except KeyboardInterrupt:
               self.logger.info("Application stopped by user")
           except Exception as e:
               self.logger.error(f"Error starting application: {e}")
               raise
   ```

### 任務 4.2: 命令列介面實作
**預估時間：2 天**

1. **建立命令列參數解析器**
   ```python
   def create_argument_parser() -> argparse.ArgumentParser:
       """建立命令列參數解析器"""
       parser = argparse.ArgumentParser(
           description="Civitai Shortcut - Standalone Mode",
           formatter_class=argparse.RawDescriptionHelpFormatter,
           epilog="""
   範例:
     python main.py                          # 使用預設設定啟動
     python main.py --port 8080              # 在 port 8080 啟動
     python main.py --host 0.0.0.0 --share   # 允許外部存取並建立公開連結
     python main.py --config my_config.json  # 使用自訂設定檔
     python main.py --debug                  # 開啟除錯模式
           """
       )
       
       # 基本選項
       parser.add_argument(
           '--host', 
           default='127.0.0.1',
           help='伺服器主機位址 (預設: 127.0.0.1)'
       )
       
       parser.add_argument(
           '--port', 
           type=int, 
           default=7860,
           help='伺服器連接埠 (預設: 7860)'
       )
       
       parser.add_argument(
           '--share', 
           action='store_true',
           help='建立 Gradio 公開分享連結'
       )
       
       # 設定選項
       parser.add_argument(
           '--config', 
           type=str,
           help='自訂設定檔路徑'
       )
       
       parser.add_argument(
           '--models-path',
           type=str,
           help='模型檔案儲存路徑'
       )
       
       parser.add_argument(
           '--output-path',
           type=str,
           help='輸出檔案儲存路徑'
       )
       
       # 除錯和開發選項
       parser.add_argument(
           '--debug',
           action='store_true',
           help='開啟除錯模式'
       )
       
       parser.add_argument(
           '--reload',
           action='store_true',
           help='開啟自動重載 (開發用)'
       )
       
       parser.add_argument(
           '--quiet',
           action='store_true',
           help='靜默模式，減少輸出'
       )
       
       # 版本資訊
       parser.add_argument(
           '--version',
           action='version',
           version='Civitai Shortcut 2.0.0 (Standalone)'
       )
       
       return parser
   ```

2. **實作設定覆寫邏輯**
   ```python
   def apply_cli_overrides(app: CivitaiShortcutApp, args: argparse.Namespace):
       """將命令列參數套用到應用程式設定"""
       config_manager = app.compat_layer.config_manager
       
       # 路徑設定
       if args.models_path:
           config_manager.set('paths.models', args.models_path)
       
       if args.output_path:
           config_manager.set('paths.output', args.output_path)
       
       # 除錯設定
       if args.debug:
           config_manager.set('debug.enabled', True)
           logging.getLogger().setLevel(logging.DEBUG)
       
       if args.quiet:
           logging.getLogger().setLevel(logging.WARNING)
       
       # 伺服器設定
       config_manager.set('server.host', args.host)
       config_manager.set('server.port', args.port)
       config_manager.set('server.share', args.share)
   ```

### 任務 4.3: UI 整合和適配
**預估時間：2 天**

1. **修改現有 UI 建立邏輯**
   ```python
   # ui_adapter.py
   def create_civitai_shortcut_ui(compat_layer):
       """建立適配獨立模式的 Civitai Shortcut UI"""
       import gradio as gr
       
       # 匯入現有的 UI 元件
       from scripts.civitai_manager_libs import (
           civitai_shortcut_action,
           model_action,
           recipe_action,
           classification_action
       )
       
       # 注入相容性層到所有 action 模組
       _inject_compatibility_layer(compat_layer)
       
       with gr.Tab("🏠 Shortcut", elem_id="civitai_shortcut"):
           # 原有的 shortcut UI
           civitai_shortcut_action.on_ui(compat_layer)
       
       with gr.Tab("📁 Model Browser", elem_id="civitai_model_browser"):
           # 模型瀏覽器 UI
           model_action.on_ui(compat_layer)
       
       with gr.Tab("📝 Recipe Manager", elem_id="civitai_recipe_manager"):
           # Recipe 管理 UI
           recipe_action.on_ui(compat_layer)
       
       with gr.Tab("🏷️ Classification", elem_id="civitai_classification"):
           # 分類管理 UI
           classification_action.on_ui(compat_layer)
       
       with gr.Tab("⚙️ Settings", elem_id="civitai_settings"):
           # 設定 UI
           _create_settings_ui(compat_layer)
   
   def _inject_compatibility_layer(compat_layer):
       """將相容性層注入到各個 action 模組"""
       modules_to_inject = [
           'scripts.civitai_manager_libs.civitai_shortcut_action',
           'scripts.civitai_manager_libs.model_action',
           'scripts.civitai_manager_libs.recipe_action',
           'scripts.civitai_manager_libs.classification_action',
           'scripts.civitai_manager_libs.setting_action'
       ]
       
       for module_name in modules_to_inject:
           if module_name in sys.modules:
               module = sys.modules[module_name]
               if hasattr(module, 'set_compatibility_layer'):
                   module.set_compatibility_layer(compat_layer)
   ```

2. **建立獨立模式專用設定 UI**
   ```python
   def _create_settings_ui(compat_layer):
       """建立設定介面"""
       import gradio as gr
       
       with gr.Row():
           with gr.Column():
               gr.Markdown("## 伺服器設定")
               
               host_input = gr.Textbox(
                   label="主機位址",
                   value=compat_layer.config_manager.get('server.host', '127.0.0.1')
               )
               
               port_input = gr.Number(
                   label="連接埠",
                   value=compat_layer.config_manager.get('server.port', 7860),
                   precision=0
               )
               
               gr.Markdown("## Civitai 設定")
               
               api_key_input = gr.Textbox(
                   label="API 金鑰",
                   type="password",
                   value=compat_layer.config_manager.get('civitai.api_key', '')
               )
               
               download_path_input = gr.Textbox(
                   label="下載路徑",
                   value=compat_layer.config_manager.get('civitai.download_path', './models')
               )
           
           with gr.Column():
               gr.Markdown("## 快取設定")
               
               cache_enabled = gr.Checkbox(
                   label="啟用快取",
                   value=compat_layer.config_manager.get('civitai.cache_enabled', True)
               )
               
               cache_size = gr.Slider(
                   label="快取大小 (MB)",
                   minimum=100,
                   maximum=2000,
                   value=compat_layer.config_manager.get('civitai.cache_size_mb', 500)
               )
       
       save_button = gr.Button("儲存設定", variant="primary")
       
       def save_settings(*args):
           # 儲存設定的邏輯
           settings_map = {
               'server.host': args[0],
               'server.port': args[1],
               'civitai.api_key': args[2],
               'civitai.download_path': args[3],
               'civitai.cache_enabled': args[4],
               'civitai.cache_size_mb': args[5]
           }
           
           for key, value in settings_map.items():
               compat_layer.config_manager.set(key, value)
           
           compat_layer.config_manager.save()
           return "設定已儲存！"
       
       save_button.click(
           save_settings,
           inputs=[host_input, port_input, api_key_input, 
                   download_path_input, cache_enabled, cache_size],
           outputs=[gr.Textbox(label="狀態")]
       )
   ```

### 任務 4.4: 啟動腳本建立
**預估時間：1 天**

1. **建立跨平台啟動腳本**

   **Linux/macOS 啟動腳本 (`start.sh`)**
   ```bash
   #!/bin/bash
   
   # Civitai Shortcut 啟動腳本
   
   set -e
   
   # 顏色定義
   RED='\033[0;31m'
   GREEN='\033[0;32m'
   YELLOW='\033[1;33m'
   BLUE='\033[0;34m'
   NC='\033[0m' # No Color
   
   echo -e "${BLUE}Civitai Shortcut - Standalone Mode${NC}"
   echo "=================================="
   
   # 檢查 Python 環境
   if ! command -v python3 &> /dev/null; then
       echo -e "${RED}錯誤: 找不到 Python 3${NC}"
       echo "請安裝 Python 3.8 或更新版本"
       exit 1
   fi
   
   # 檢查相依套件
   echo -e "${YELLOW}檢查相依套件...${NC}"
   if ! python3 -c "import gradio" &> /dev/null; then
       echo -e "${YELLOW}安裝相依套件...${NC}"
       python3 -m pip install -r requirements.txt
   fi
   
   # 啟動應用程式
   echo -e "${GREEN}啟動 Civitai Shortcut...${NC}"
   python3 main.py "$@"
   ```

   **Windows 啟動腳本 (`start.bat`)**
   ```batch
   @echo off
   chcp 65001 > nul
   
   echo Civitai Shortcut - Standalone Mode
   echo ==================================
   
   REM 檢查 Python 環境
   python --version >nul 2>&1
   if errorlevel 1 (
       echo 錯誤: 找不到 Python
       echo 請安裝 Python 3.8 或更新版本
       pause
       exit /b 1
   )
   
   REM 檢查相依套件
   echo 檢查相依套件...
   python -c "import gradio" >nul 2>&1
   if errorlevel 1 (
       echo 安裝相依套件...
       python -m pip install -r requirements.txt
   )
   
   REM 啟動應用程式
   echo 啟動 Civitai Shortcut...
   python main.py %*
   
   pause
   ```

### 任務 4.5: 主程式入口點實作
**預估時間：1 天**

1. **完成主程式邏輯**
   ```python
   def main():
       """主程式入口點"""
       try:
           # 解析命令列參數
           parser = create_argument_parser()
           args = parser.parse_args()
           
           # 建立應用程式實例
           app = CivitaiShortcutApp(config_path=args.config)
           
           # 套用命令列覆寫
           apply_cli_overrides(app, args)
           
           # 建立介面
           app.create_interface()
           
           # 啟動應用程式
           app.launch(
               host=args.host,
               port=args.port,
               share=args.share,
               debug=args.debug,
               quiet=args.quiet
           )
           
       except KeyboardInterrupt:
           print("\n應用程式已停止")
           sys.exit(0)
       except Exception as e:
           print(f"錯誤: {e}")
           if args.debug:
               import traceback
               traceback.print_exc()
           sys.exit(1)
   
   if __name__ == "__main__":
       main()
   ```

## 交付物

### 主要檔案
1. **`main.py`** - 主程式入口點
2. **`ui_adapter.py`** - UI 適配器
3. **`start.sh`** - Linux/macOS 啟動腳本
4. **`start.bat`** - Windows 啟動腳本

### 設定檔案
1. **`requirements.txt`** - Python 相依套件清單
2. **`config/default_config.json`** - 預設設定檔
3. **`README_STANDALONE.md`** - 獨立模式使用說明

### 測試檔案
1. **`tests/test_main.py`** - 主程式測試
2. **`tests/test_cli.py`** - 命令列介面測試
3. **`tests/test_ui_adapter.py`** - UI 適配器測試

## 品質要求

### 錯誤處理
1. **優雅關閉**: 支援 Ctrl+C 優雅關閉
2. **錯誤訊息**: 提供清楚的錯誤訊息和解決建議
3. **記錄**: 完整的錯誤記錄和除錯資訊

### 使用者體驗
1. **直觀操作**: 啟動腳本使用簡單
2. **進度回饋**: 啟動過程有適當的進度提示
3. **設定保存**: 使用者設定能夠持久化保存

## 測試策略

### 功能測試
1. **基本啟動**: 驗證應用程式能夠正常啟動
2. **參數處理**: 測試各種命令列參數組合
3. **設定載入**: 測試自訂設定檔載入
4. **UI 功能**: 驗證所有 UI 功能正常

### 環境測試
1. **跨平台**: Windows、Linux、macOS 測試
2. **Python 版本**: 3.8, 3.9, 3.10, 3.11 測試
3. **相依套件**: 測試最小相依套件安裝

### 壓力測試
1. **長時間運行**: 24 小時穩定性測試
2. **多使用者**: 多人同時存取測試
3. **大檔案處理**: 處理大型模型檔案

## 常見問題與解答

**Q: 如何在指定的連接埠啟動應用程式？**
A: 使用 `python main.py --port 8080` 命令。

**Q: 如何開啟除錯模式？**
A: 使用 `python main.py --debug` 命令。

**Q: 設定檔儲存在哪裡？**
A: 預設在 `config/config.json`，可以用 `--config` 參數指定自訂路徑。

**Q: 如何允許外部存取？**
A: 使用 `python main.py --host 0.0.0.0` 命令。

## 後續連接
完成此項目後，繼續執行：
- **Backlog 005**: 現有模組相依性修改
- **Backlog 006**: UI 元件雙模式適配
