# Backlog 006: UI 元件雙模式適配

## 優先級
**中高 (High)** - 確保使用者介面在兩種模式下都能正常運作

## 估算工作量
**8-12 工作天**

## 目標描述
修改和適配所有 UI 元件，確保它們在 AUTOMATIC1111 WebUI 模式和獨立模式下都能正常運作。這包括處理 AUTOMATIC1111 特定的 UI 整合功能、參數複製貼上機制，以及建立獨立模式下的 UI 功能替代方案。

## 接受標準 (Definition of Done)
1. ✅ 所有 Gradio UI 元件在兩種模式下正常顯示
2. ✅ 參數複製貼上功能在兩種模式下正常運作
3. ✅ PNG 資訊處理功能完全相容
4. ✅ 獨立模式下提供等效的 UI 功能
5. ✅ 所有互動事件正確綁定和觸發
6. ✅ UI 回應性能符合預期
7. ✅ 跨瀏覽器相容性驗證通過
8. ✅ 無障礙功能保持

## 詳細任務

### 任務 6.1: UI 架構分析和設計
**預估時間：2 天**

1. **分析現有 UI 架構**
   ```
   主要 UI 檔案分析：
   - scripts/civitai_shortcut.py (主要 UI 入口)
   - civitai_manager_libs/*_action.py (事件處理)
   - civitai_manager_libs/*_page.py (頁面元件)
   - civitai_manager_libs/prompt_ui.py (提示詞 UI)
   ```

2. **識別 AUTOMATIC1111 特定的 UI 功能**
   ```python
   # 需要處理的特定功能：
   1. infotext_utils - 參數複製貼上
   2. modules.extras.run_pnginfo - PNG 資訊解析
   3. modules.shared - 共享 UI 狀態
   4. script_callbacks.on_ui_tabs - 標籤註冊
   5. WebUI 專用的 CSS 樣式
   ```

3. **設計 UI 相容性策略**
   ```markdown
   # UI 相容性設計原則
   
   ## 雙模式 UI 策略
   1. 保持 Gradio 元件結構不變
   2. 透過條件邏輯處理模式差異
   3. 建立 UI 功能的抽象層
   4. 實作獨立模式的替代功能
   
   ## 具體適配方案
   - 參數複製貼上：WebUI 模式使用原生功能，獨立模式實作自訂版本
   - PNG 處理：兩種模式都使用統一的處理邏輯
   - 樣式：提供獨立的 CSS 檔案
   - 事件處理：透過相容性層統一處理
   ```

### 任務 6.2: 主要 UI 入口適配
**預估時間：3 天**

1. **修改 civitai_shortcut.py 主入口**
   ```python
   # scripts/civitai_shortcut.py 修改範例
   
   import gradio as gr
   from typing import Optional, Tuple, Any
   
   # 相容性層匯入
   try:
       from modules import scripts, script_callbacks, shared
       from modules.ui_components import ToolButton
       WEBUI_MODE = True
   except ImportError:
       WEBUI_MODE = False
       from .civitai_manager_libs.compat_layer import CompatibilityLayer
       from .civitai_manager_libs.ui_components import ToolButton  # 自訂實作
   
   # 全域相容性層
   _compat_layer = None
   
   def get_compatibility_layer():
       """取得相容性層實例"""
       global _compat_layer
       if _compat_layer is None:
           if WEBUI_MODE:
               from .civitai_manager_libs.compat_layer import WebUICompatibilityLayer
               _compat_layer = WebUICompatibilityLayer()
           else:
               from .civitai_manager_libs.compat_layer import StandaloneCompatibilityLayer
               _compat_layer = StandaloneCompatibilityLayer()
       return _compat_layer
   
   def civitai_shortcut_ui():
       """建立 Civitai Shortcut UI"""
       compat = get_compatibility_layer()
       
       # 設定相容性層到所有子模組
       _setup_compatibility_layer_for_modules(compat)
       
       # 建立主要 UI
       with gr.Blocks(css=_get_ui_css()) as civitai_shortcut_interface:
           with gr.Tabs(elem_id="civitai_shortcut_tabs"):
               # 現有的標籤頁邏輯
               _create_shortcut_tab(compat)
               _create_model_tab(compat)
               _create_recipe_tab(compat)
               _create_gallery_tab(compat)
               _create_classification_tab(compat)
               _create_setting_tab(compat)
       
       return civitai_shortcut_interface
   
   def _setup_compatibility_layer_for_modules(compat):
       """設定相容性層到所有相關模組"""
       from .civitai_manager_libs import (
           civitai_shortcut_action, model_action, recipe_action,
           classification_action, setting_action, scan_action
       )
       
       # 設定相容性層到各個 action 模組
       for module in [civitai_shortcut_action, model_action, recipe_action,
                      classification_action, setting_action, scan_action]:
           if hasattr(module, 'set_compatibility_layer'):
               module.set_compatibility_layer(compat)
   
   def _get_ui_css() -> str:
       """取得 UI CSS 樣式"""
       compat = get_compatibility_layer()
       if compat.mode == 'webui':
           # WebUI 模式使用最小 CSS
           return """
           /* WebUI 模式特定樣式 */
           .civitai-shortcut-container {
               padding: 10px;
           }
           """
       else:
           # 獨立模式使用完整 CSS
           return _get_standalone_css()
   
   def _get_standalone_css() -> str:
       """取得獨立模式的完整 CSS"""
       import os
       css_file = os.path.join(os.path.dirname(__file__), "..", "style.css")
       try:
           with open(css_file, 'r', encoding='utf-8') as f:
               return f.read()
       except FileNotFoundError:
           return _get_default_css()
   
   def _get_default_css() -> str:
       """預設 CSS 樣式"""
       return """
       /* 獨立模式預設樣式 */
       .civitai-shortcut-container {
           max-width: 1200px;
           margin: 0 auto;
           padding: 20px;
       }
       
       .civitai-card {
           border: 1px solid #ddd;
           border-radius: 8px;
           padding: 15px;
           margin: 10px;
           box-shadow: 0 2px 4px rgba(0,0,0,0.1);
       }
       
       .civitai-preview {
           max-width: 200px;
           max-height: 200px;
           object-fit: cover;
           border-radius: 4px;
       }
       """
   
   # WebUI 模式的標籤註冊
   if WEBUI_MODE:
       def on_ui_tabs():
           return [(civitai_shortcut_ui(), "Civitai Shortcut", "civitai_shortcut")]
       
       script_callbacks.on_ui_tabs(on_ui_tabs)
   ```

2. **建立獨立模式啟動器**
   ```python
   # standalone_launcher.py
   
   import gradio as gr
   import argparse
   import os
   import sys
   
   def create_standalone_app():
       """建立獨立模式應用程式"""
       from scripts.civitai_shortcut import civitai_shortcut_ui
       
       # 設定獨立模式
       os.environ['CIVITAI_SHORTCUT_MODE'] = 'standalone'
       
       # 建立應用程式
       with gr.Blocks(
           title="Civitai Shortcut - 獨立版本",
           theme=gr.themes.Default(),
           css=_get_app_css()
       ) as app:
           gr.Markdown("# Civitai Shortcut")
           gr.Markdown("獨立執行版本 - 模型管理與下載工具")
           
           # 嵌入主要 UI
           civitai_shortcut_ui()
       
       return app
   
   def _get_app_css():
       """取得應用程式 CSS"""
       return """
       body {
           font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       }
       
       .gradio-container {
           max-width: none !important;
       }
       
       #civitai_shortcut_tabs {
           border: 1px solid #e0e0e0;
           border-radius: 8px;
           overflow: hidden;
       }
       """
   
   def main():
       """主要啟動函式"""
       parser = argparse.ArgumentParser(description='Civitai Shortcut 獨立版本')
       parser.add_argument('--host', default='127.0.0.1', help='伺服器主機')
       parser.add_argument('--port', type=int, default=7860, help='伺服器埠號')
       parser.add_argument('--share', action='store_true', help='建立公開分享連結')
       parser.add_argument('--debug', action='store_true', help='啟用除錯模式')
       
       args = parser.parse_args()
       
       # 建立應用程式
       app = create_standalone_app()
       
       # 啟動伺服器
       print(f"正在啟動 Civitai Shortcut 在 http://{args.host}:{args.port}")
       app.launch(
           server_name=args.host,
           server_port=args.port,
           share=args.share,
           debug=args.debug,
           show_error=True,
           quiet=False
       )
   
   if __name__ == "__main__":
       main()
   ```

### 任務 6.3: 參數複製貼上功能適配
**預估時間：2 天**

1. **分析現有參數複製貼上功能**
   ```python
   # 現有功能分析 (在 civitai_shortcut_action.py 中)
   
   # AUTOMATIC1111 原生功能：
   from modules import infotext_utils
   
   def setup_parameters_copypaste(component_dict):
       # 使用 WebUI 的參數複製貼上系統
       infotext_utils.register_paste_params_button(
           component_dict["paste"],
           component_dict["prompt"],
           component_dict
       )
   ```

2. **實作獨立模式的參數複製貼上**
   ```python
   # civitai_manager_libs/ui_components.py (新檔案)
   
   import gradio as gr
   import json
   import re
   from typing import Dict, Any, Optional
   
   class ParameterCopyPaste:
       """參數複製貼上功能實作"""
       
       def __init__(self, mode='webui'):
           self.mode = mode
           self._parameter_mapping = {
               'prompt': 'prompt',
               'negative_prompt': 'negative_prompt',
               'steps': 'steps',
               'sampler_name': 'sampler_name',
               'cfg_scale': 'cfg_scale',
               'seed': 'seed',
               'width': 'width',
               'height': 'height'
           }
       
       def register_copypaste_components(self, components: Dict[str, gr.Component]):
           """註冊複製貼上元件"""
           if self.mode == 'webui':
               self._register_webui_copypaste(components)
           else:
               self._register_standalone_copypaste(components)
       
       def _register_webui_copypaste(self, components: Dict[str, gr.Component]):
           """註冊 WebUI 模式的複製貼上"""
           try:
               from modules import infotext_utils
               
               # 使用 WebUI 原生功能
               infotext_utils.register_paste_params_button(
                   components.get('paste_button'),
                   components.get('prompt'),
                   components
               )
           except ImportError:
               # fallback 到自訂實作
               self._register_standalone_copypaste(components)
       
       def _register_standalone_copypaste(self, components: Dict[str, gr.Component]):
           """註冊獨立模式的複製貼上"""
           paste_button = components.get('paste_button')
           if paste_button:
               # 綁定貼上事件
               paste_button.click(
                   fn=self._handle_paste,
                   inputs=[components.get('input_text', gr.Text())],
                   outputs=[components[key] for key in self._parameter_mapping.keys() 
                           if key in components]
               )
       
       def _handle_paste(self, input_text: str) -> tuple:
           """處理貼上操作"""
           if not input_text:
               return tuple([''] * len(self._parameter_mapping))
           
           # 解析參數
           params = self._parse_parameters(input_text)
           
           # 建立輸出元組
           outputs = []
           for key in self._parameter_mapping.keys():
               outputs.append(params.get(key, ''))
           
           return tuple(outputs)
       
       def _parse_parameters(self, text: str) -> Dict[str, Any]:
           """解析參數文字"""
           params = {}
           
           # 嘗試解析 JSON 格式
           try:
               return json.loads(text)
           except json.JSONDecodeError:
               pass
           
           # 解析 WebUI 格式的參數
           # 例如: "prompt: beautiful girl, steps: 20, cfg: 7"
           patterns = {
               'prompt': r'(?:^|,\s*)([^,]+?)(?=,\s*\w+:|$)',
               'negative_prompt': r'Negative prompt:\s*([^,\n]+)',
               'steps': r'Steps:\s*(\d+)',
               'sampler_name': r'Sampler:\s*([^,\n]+)',
               'cfg_scale': r'CFG scale:\s*([\d.]+)',
               'seed': r'Seed:\s*(\d+)',
               'width': r'Size:\s*(\d+)x\d+',
               'height': r'Size:\s*\d+x(\d+)'
           }
           
           for key, pattern in patterns.items():
               match = re.search(pattern, text, re.IGNORECASE)
               if match:
                   value = match.group(1).strip()
                   # 型別轉換
                   if key in ['steps', 'seed', 'width', 'height']:
                       try:
                           params[key] = int(value)
                       except ValueError:
                           continue
                   elif key in ['cfg_scale']:
                       try:
                           params[key] = float(value)
                       except ValueError:
                           continue
                   else:
                       params[key] = value
           
           return params
       
       def generate_parameter_string(self, components: Dict[str, gr.Component]) -> str:
           """產生參數字串供複製"""
           params = {}
           
           # 從元件取得值
           for ui_key, param_key in self._parameter_mapping.items():
               component = components.get(ui_key)
               if component and hasattr(component, 'value'):
                   params[param_key] = component.value
           
           # 產生格式化字串
           param_parts = []
           for key, value in params.items():
               if value:
                   param_parts.append(f"{key}: {value}")
           
           return ", ".join(param_parts)
   ```

3. **整合到現有 action 模組**
   ```python
   # 在 civitai_shortcut_action.py 中整合
   
   from .ui_components import ParameterCopyPaste
   
   def setup_ui_copypaste(compat_layer):
       """設定 UI 複製貼上功能"""
       copypaste = ParameterCopyPaste(mode=compat_layer.mode)
       return copypaste
   
   def create_parameter_components(copypaste: ParameterCopyPaste):
       """建立參數相關元件"""
       with gr.Row():
           paste_button = gr.Button("貼上參數", elem_id="paste_params")
           copy_button = gr.Button("複製參數", elem_id="copy_params")
       
       with gr.Column():
           prompt = gr.Textbox(label="提示詞", lines=3)
           negative_prompt = gr.Textbox(label="負面提示詞", lines=2)
           
           with gr.Row():
               steps = gr.Slider(minimum=1, maximum=150, value=20, label="步數")
               cfg_scale = gr.Slider(minimum=1, maximum=30, value=7, label="CFG")
       
       # 註冊複製貼上功能
       components = {
           'paste_button': paste_button,
           'copy_button': copy_button,
           'prompt': prompt,
           'negative_prompt': negative_prompt,
           'steps': steps,
           'cfg_scale': cfg_scale
       }
       
       copypaste.register_copypaste_components(components)
       
       return components
   ```

### 任務 6.4: PNG 資訊處理功能適配
**預估時間：2 天**

1. **建立統一的 PNG 處理介面**
   ```python
   # civitai_manager_libs/image_processor.py (新檔案)
   
   import os
   from PIL import Image
   from PIL.ExifTags import TAGS
   import json
   import re
   from typing import Dict, Optional, Any
   
   class ImageMetadataProcessor:
       """圖片 metadata 處理器"""
       
       def __init__(self, mode='webui'):
           self.mode = mode
       
       def extract_png_info(self, image_path: str) -> Dict[str, Any]:
           """提取 PNG 資訊"""
           if self.mode == 'webui':
               return self._extract_with_webui(image_path)
           else:
               return self._extract_with_pil(image_path)
       
       def _extract_with_webui(self, image_path: str) -> Dict[str, Any]:
           """使用 WebUI 方法提取資訊"""
           try:
               from modules import extras
               result = extras.run_pnginfo(image_path)
               return result if result else {}
           except ImportError:
               # fallback 到 PIL
               return self._extract_with_pil(image_path)
       
       def _extract_with_pil(self, image_path: str) -> Dict[str, Any]:
           """使用 PIL 提取資訊"""
           try:
               with Image.open(image_path) as img:
                   # 提取 PNG 文字資訊
                   png_info = {}
                   
                   # 處理 PNG tEXt chunks
                   if hasattr(img, 'text'):
                       png_info.update(img.text)
                   
                   # 處理 EXIF 資料
                   exif_info = self._extract_exif(img)
                   if exif_info:
                       png_info.update(exif_info)
                   
                   # 解析生成參數
                   parameters = self._parse_generation_parameters(png_info)
                   
                   return {
                       'parameters': parameters,
                       'raw_info': png_info
                   }
                   
           except Exception as e:
               print(f"Error extracting PNG info: {e}")
               return {}
       
       def _extract_exif(self, img: Image.Image) -> Dict[str, Any]:
           """提取 EXIF 資訊"""
           try:
               exif_dict = img._getexif()
               if exif_dict:
                   exif_info = {}
                   for tag_id, value in exif_dict.items():
                       tag = TAGS.get(tag_id, tag_id)
                       exif_info[tag] = value
                   return exif_info
           except Exception:
               pass
           return {}
       
       def _parse_generation_parameters(self, png_info: Dict[str, Any]) -> Dict[str, Any]:
           """解析生成參數"""
           parameters = {}
           
           # 查找常見的參數鍵
           param_keys = ['parameters', 'Parameters', 'prompt', 'Prompt']
           param_text = None
           
           for key in param_keys:
               if key in png_info:
                   param_text = png_info[key]
                   break
           
           if param_text:
               parameters = self._parse_parameter_string(param_text)
           
           return parameters
       
       def _parse_parameter_string(self, param_text: str) -> Dict[str, Any]:
           """解析參數字串"""
           params = {}
           
           try:
               # 嘗試 JSON 解析
               return json.loads(param_text)
           except json.JSONDecodeError:
               pass
           
           # 解析 WebUI 格式
           patterns = {
               'prompt': r'^([^\\n]+?)(?=\\nNegative prompt:|$)',
               'negative_prompt': r'Negative prompt:\\s*([^\\n]+)',
               'steps': r'Steps:\\s*(\\d+)',
               'sampler_name': r'Sampler:\\s*([^,\\n]+)',
               'cfg_scale': r'CFG scale:\\s*([\\d.]+)',
               'seed': r'Seed:\\s*(\\d+)',
               'width': r'Size:\\s*(\\d+)x\\d+',
               'height': r'Size:\\s*\\d+x(\\d+)',
               'model_hash': r'Model hash:\\s*([a-f0-9]+)',
               'model': r'Model:\\s*([^,\\n]+)'
           }
           
           for key, pattern in patterns.items():
               match = re.search(pattern, param_text, re.MULTILINE | re.IGNORECASE)
               if match:
                   value = match.group(1).strip()
                   
                   # 型別轉換
                   if key in ['steps', 'seed', 'width', 'height']:
                       try:
                           params[key] = int(value)
                       except ValueError:
                           continue
                   elif key in ['cfg_scale']:
                       try:
                           params[key] = float(value)
                       except ValueError:
                           continue
                   else:
                       params[key] = value
           
           return params
       
       def embed_parameters_to_png(self, image_path: str, parameters: Dict[str, Any], 
                                  output_path: Optional[str] = None) -> str:
           """將參數嵌入到 PNG 檔案"""
           if output_path is None:
               output_path = image_path
           
           try:
               with Image.open(image_path) as img:
                   # 準備 metadata
                   png_info = img.text.copy() if hasattr(img, 'text') else {}
                   
                   # 添加參數
                   param_string = self._format_parameters(parameters)
                   png_info['parameters'] = param_string
                   
                   # 儲存圖片
                   img.save(output_path, pnginfo=png_info)
                   
               return output_path
               
           except Exception as e:
               print(f"Error embedding parameters: {e}")
               return image_path
       
       def _format_parameters(self, parameters: Dict[str, Any]) -> str:
           """格式化參數為字串"""
           parts = []
           
           # 主要提示詞
           if 'prompt' in parameters:
               parts.append(parameters['prompt'])
           
           # 負面提示詞
           if 'negative_prompt' in parameters:
               parts.append(f"Negative prompt: {parameters['negative_prompt']}")
           
           # 其他參數
           other_params = []
           param_order = ['steps', 'sampler_name', 'cfg_scale', 'seed', 'width', 'height', 'model']
           
           for key in param_order:
               if key in parameters:
                   value = parameters[key]
                   if key == 'sampler_name':
                       other_params.append(f"Sampler: {value}")
                   elif key == 'cfg_scale':
                       other_params.append(f"CFG scale: {value}")
                   elif key in ['width', 'height']:
                       if 'size_added' not in locals():
                           size_added = True
                           w = parameters.get('width', '')
                           h = parameters.get('height', '')
                           if w and h:
                               other_params.append(f"Size: {w}x{h}")
                   else:
                       formatted_key = key.replace('_', ' ').title()
                       other_params.append(f"{formatted_key}: {value}")
           
           if other_params:
               parts.append(", ".join(other_params))
           
           return "\\n".join(parts)
   ```

2. **整合到現有功能**
   ```python
   # 在相關 action 模組中整合 ImageMetadataProcessor
   
   from .image_processor import ImageMetadataProcessor
   
   def setup_image_processing(compat_layer):
       """設定圖片處理功能"""
       return ImageMetadataProcessor(mode=compat_layer.mode)
   
   def handle_image_info_extraction(image_processor, image_path):
       """處理圖片資訊提取"""
       if not image_path:
           return {}
       
       return image_processor.extract_png_info(image_path)
   ```

### 任務 6.5: 事件處理和互動邏輯適配
**預估時間：2 天**

1. **建立統一的事件處理系統**
   ```python
   # civitai_manager_libs/event_handler.py (新檔案)
   
   import gradio as gr
   from typing import Callable, Dict, List, Any, Optional
   import threading
   import time
   
   class EventHandler:
       """統一的事件處理系統"""
       
       def __init__(self, mode='webui'):
           self.mode = mode
           self._event_queue = []
           self._processing = False
           self._callbacks = {}
       
       def register_callback(self, event_name: str, callback: Callable):
           """註冊事件回呼"""
           if event_name not in self._callbacks:
               self._callbacks[event_name] = []
           self._callbacks[event_name].append(callback)
       
       def trigger_event(self, event_name: str, *args, **kwargs):
           """觸發事件"""
           if event_name in self._callbacks:
               for callback in self._callbacks[event_name]:
                   try:
                       callback(*args, **kwargs)
                   except Exception as e:
                       print(f"Error in callback for {event_name}: {e}")
       
       def setup_component_events(self, components: Dict[str, gr.Component], 
                                 actions: Dict[str, Callable]):
           """設定元件事件"""
           for component_name, component in components.items():
               if component_name in actions:
                   action = actions[component_name]
                   
                   # 根據元件類型設定適當的事件
                   if isinstance(component, gr.Button):
                       component.click(fn=action)
                   elif isinstance(component, gr.Dropdown):
                       component.change(fn=action)
                   elif isinstance(component, gr.Slider):
                       component.change(fn=action)
                   elif isinstance(component, gr.Textbox):
                       # 對於文字框，可能需要同時處理 change 和 submit
                       component.change(fn=action)
                       if hasattr(component, 'submit'):
                           component.submit(fn=action)
       
       def create_progress_handler(self, progress_component: gr.Progress):
           """建立進度處理器"""
           def update_progress(current: int, total: int, message: str = ""):
               if self.mode == 'webui':
                   # WebUI 模式的進度更新
                   progress_component.update(current / total, desc=message)
               else:
                   # 獨立模式的進度更新
                   percentage = (current / total) * 100
                   print(f"Progress: {percentage:.1f}% - {message}")
           
           return update_progress
       
       def handle_async_operation(self, operation: Callable, 
                                success_callback: Optional[Callable] = None,
                                error_callback: Optional[Callable] = None):
           """處理非同步操作"""
           def wrapper():
               try:
                   result = operation()
                   if success_callback:
                       success_callback(result)
               except Exception as e:
                   if error_callback:
                       error_callback(e)
                   else:
                       print(f"Async operation error: {e}")
           
           thread = threading.Thread(target=wrapper)
           thread.daemon = True
           thread.start()
           return thread
   ```

2. **更新現有 action 模組的事件處理**
   ```python
   # 在各個 action 模組中使用 EventHandler
   
   from .event_handler import EventHandler
   
   class CivitaiShortcutAction:
       """Civitai Shortcut 動作處理器"""
       
       def __init__(self, compat_layer):
           self.compat_layer = compat_layer
           self.event_handler = EventHandler(mode=compat_layer.mode)
           self._setup_event_callbacks()
       
       def _setup_event_callbacks(self):
           """設定事件回呼"""
           self.event_handler.register_callback('model_selected', self._on_model_selected)
           self.event_handler.register_callback('download_started', self._on_download_started)
           self.event_handler.register_callback('download_completed', self._on_download_completed)
       
       def _on_model_selected(self, model_info):
           """模型選擇事件處理"""
           print(f"Model selected: {model_info.get('name', 'Unknown')}")
       
       def _on_download_started(self, download_info):
           """下載開始事件處理"""
           print(f"Download started: {download_info.get('filename', 'Unknown')}")
       
       def _on_download_completed(self, download_info):
           """下載完成事件處理"""
           print(f"Download completed: {download_info.get('filename', 'Unknown')}")
       
       def create_ui_components(self):
           """建立 UI 元件"""
           components = {}
           actions = {}
           
           # 建立元件
           with gr.Row():
               components['refresh_button'] = gr.Button("重新整理", variant="secondary")
               components['download_button'] = gr.Button("下載", variant="primary")
           
           # 定義動作
           actions['refresh_button'] = self._handle_refresh
           actions['download_button'] = self._handle_download
           
           # 設定事件
           self.event_handler.setup_component_events(components, actions)
           
           return components
       
       def _handle_refresh(self):
           """處理重新整理"""
           self.event_handler.trigger_event('refresh_requested')
           # 執行重新整理邏輯
           return self._refresh_content()
       
       def _handle_download(self):
           """處理下載"""
           self.event_handler.trigger_event('download_started', {'filename': 'example.safetensors'})
           # 執行下載邏輯
           result = self._start_download()
           self.event_handler.trigger_event('download_completed', {'filename': 'example.safetensors'})
           return result
   ```

### 任務 6.6: 獨立模式 UI 最佳化
**預估時間：1 天**

1. **建立獨立模式專用的 UI 元件**
   ```python
   # civitai_manager_libs/standalone_ui.py (新檔案)
   
   import gradio as gr
   import os
   from typing import Dict, List, Optional
   
   class StandaloneUIComponents:
       """獨立模式專用 UI 元件"""
       
       def __init__(self):
           self.css_theme = self._load_theme()
       
       def _load_theme(self) -> str:
           """載入主題 CSS"""
           css_path = os.path.join(os.path.dirname(__file__), "..", "..", "style.css")
           try:
               with open(css_path, 'r', encoding='utf-8') as f:
                   return f.read()
           except FileNotFoundError:
               return self._get_default_theme()
       
       def _get_default_theme(self) -> str:
           """預設主題"""
           return """
           /* Civitai Shortcut 獨立版本主題 */
           .gradio-container {
               font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
           }
           
           .civitai-header {
               background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
               color: white;
               padding: 20px;
               border-radius: 10px;
               margin-bottom: 20px;
               text-align: center;
           }
           
           .civitai-card {
               border: 1px solid #e1e5e9;
               border-radius: 8px;
               padding: 16px;
               margin: 8px;
               background: white;
               box-shadow: 0 2px 4px rgba(0,0,0,0.1);
               transition: box-shadow 0.2s ease;
           }
           
           .civitai-card:hover {
               box-shadow: 0 4px 8px rgba(0,0,0,0.15);
           }
           
           .civitai-preview {
               max-width: 100%;
               max-height: 200px;
               object-fit: cover;
               border-radius: 6px;
           }
           
           .progress-container {
               background: #f8f9fa;
               border-radius: 6px;
               padding: 10px;
               margin: 10px 0;
           }
           """
       
       def create_header(self) -> gr.HTML:
           """建立頁面標題"""
           header_html = """
           <div class="civitai-header">
               <h1>🎨 Civitai Shortcut</h1>
               <p>AI 模型管理與下載工具 - 獨立版本</p>
           </div>
           """
           return gr.HTML(header_html)
       
       def create_status_bar(self) -> Dict[str, gr.Component]:
           """建立狀態列"""
           with gr.Row(elem_classes="status-bar"):
               status_text = gr.Markdown("準備就緒", elem_classes="status-text")
               version_info = gr.Markdown("版本: 2.0.0", elem_classes="version-info")
           
           return {
               'status_text': status_text,
               'version_info': version_info
           }
       
       def create_navigation_tabs(self) -> gr.Tabs:
           """建立導航標籤"""
           return gr.Tabs(elem_classes="main-tabs")
       
       def create_model_card(self, model_info: Dict) -> gr.HTML:
           """建立模型卡片"""
           card_html = f"""
           <div class="civitai-card">
               <img src="{model_info.get('preview_url', '')}" class="civitai-preview" alt="預覽圖">
               <h3>{model_info.get('name', '未知模型')}</h3>
               <p>{model_info.get('description', '無描述')}</p>
               <div class="model-stats">
                   <span>下載次數: {model_info.get('download_count', 0)}</span>
                   <span>評分: {model_info.get('rating', 'N/A')}</span>
               </div>
           </div>
           """
           return gr.HTML(card_html)
       
       def create_download_progress(self) -> Dict[str, gr.Component]:
           """建立下載進度元件"""
           with gr.Column(elem_classes="progress-container", visible=False) as container:
               progress_text = gr.Markdown("準備下載...")
               progress_bar = gr.Progress()
               cancel_button = gr.Button("取消下載", variant="stop")
           
           return {
               'container': container,
               'progress_text': progress_text,
               'progress_bar': progress_bar,
               'cancel_button': cancel_button
           }
   ```

2. **整合到主要 UI**
   ```python
   # 在 civitai_shortcut.py 中整合獨立 UI 元件
   
   def create_standalone_enhanced_ui():
       """建立增強的獨立模式 UI"""
       from .civitai_manager_libs.standalone_ui import StandaloneUIComponents
       
       ui_components = StandaloneUIComponents()
       
       with gr.Blocks(css=ui_components.css_theme) as interface:
           # 頁面標題
           ui_components.create_header()
           
           # 狀態列
           status_components = ui_components.create_status_bar()
           
           # 主要內容
           with ui_components.create_navigation_tabs():
               with gr.TabItem("模型瀏覽"):
                   create_model_browser_tab()
               
               with gr.TabItem("下載管理"):
                   create_download_manager_tab()
               
               with gr.TabItem("設定"):
                   create_settings_tab()
           
           # 下載進度
           progress_components = ui_components.create_download_progress()
       
       return interface
   ```

## 交付物

### 修改的核心檔案
1. **`scripts/civitai_shortcut.py`** - 主要 UI 入口雙模式適配
2. **所有 `*_action.py` 檔案** - 事件處理和互動邏輯適配
3. **所有 `*_page.py` 檔案** - 頁面元件雙模式適配

### 新增的 UI 支援檔案
1. **`civitai_manager_libs/ui_components.py`** - UI 元件工具和參數複製貼上
2. **`civitai_manager_libs/image_processor.py`** - 圖片 metadata 處理
3. **`civitai_manager_libs/event_handler.py`** - 事件處理系統
4. **`civitai_manager_libs/standalone_ui.py`** - 獨立模式專用 UI 元件
5. **`standalone_launcher.py`** - 獨立模式啟動器

### 資源檔案
1. **`style.css`** - 獨立模式專用樣式表（更新）
2. **`assets/icons/`** - UI 圖示資源
3. **`assets/themes/`** - 主題檔案

### 測試檔案
1. **`tests/test_ui_compatibility.py`** - UI 相容性測試
2. **`tests/test_parameter_copypaste.py`** - 參數複製貼上測試
3. **`tests/test_image_processing.py`** - 圖片處理測試
4. **`tests/test_event_handling.py`** - 事件處理測試

### 文件
1. **`UI_COMPATIBILITY_GUIDE.md`** - UI 相容性指南
2. **`STANDALONE_UI_GUIDE.md`** - 獨立模式 UI 使用指南
3. **`CUSTOM_THEMES_GUIDE.md`** - 自訂主題指南

## 品質保證要求

### UI 品質標準
1. **視覺一致性**: 兩種模式下的 UI 視覺體驗保持一致
2. **回應性能**: UI 互動回應時間 < 500ms
3. **相容性**: 支援主流瀏覽器 (Chrome, Firefox, Safari, Edge)
4. **無障礙性**: 符合 WCAG 2.1 AA 標準
5. **行動裝置**: 基本的行動裝置相容性

### 功能品質標準
1. **功能完整性**: 所有 UI 功能在兩種模式下都可用
2. **錯誤處理**: 優雅的錯誤處理和使用者提示
3. **效能**: 大量資料載入時保持流暢性
4. **記憶體**: UI 相關記憶體使用控制在合理範圍

## 風險控制和應對策略

### 主要風險
1. **Gradio 版本相容性**
   - **應對**: 鎖定 Gradio 版本，建立相容性測試
   - **備案**: 準備多版本相容性層

2. **WebUI UI 整合複雜性**
   - **應對**: 最小化對 WebUI UI 系統的依賴
   - **備案**: 建立完全獨立的 UI 版本

3. **跨瀏覽器相容性問題**
   - **應對**: 全面的瀏覽器測試
   - **備案**: 提供推薦瀏覽器清單

### 效能最佳化策略
1. **延遲載入**: 大型元件和資料使用延遲載入
2. **快取機制**: UI 狀態和資料的適當快取
3. **資源最佳化**: 圖片和 CSS 資源壓縮

## 測試策略

### 測試階段
1. **元件測試**: 個別 UI 元件功能測試
2. **整合測試**: UI 元件間互動測試
3. **模式切換測試**: 雙模式下的功能對等性測試
4. **使用者體驗測試**: 實際使用情境測試

### 測試環境
1. **WebUI 環境**: 測試與 AUTOMATIC1111 的整合
2. **獨立環境**: 測試獨立模式功能
3. **多瀏覽器環境**: 跨瀏覽器相容性測試
4. **多解析度環境**: 不同螢幕解析度測試

## 後續連接
完成此項目後，繼續執行：
- **Backlog 007**: 測試和品質保證
- **Backlog 008**: 文件撰寫和使用者指南
- **Backlog 009**: 部署和分發準備
