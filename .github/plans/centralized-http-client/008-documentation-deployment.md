# Backlog Item 008: 文件更新與部署指南

## 工作描述

更新所有相關文件，撰寫使用者指南和維護文件，確保中央化 HTTP 客戶端的完整文件化，並提供部署和維護指南。

## 背景分析

經過前面 7 個工作項目的實作，我們已經完成了中央化 HTTP 客戶端的所有功能開發。現在需要：

1. **更新技術文件**：反映新的架構變更
2. **撰寫使用者指南**：幫助使用者了解新功能
3. **建立維護文件**：協助開發者維護和擴展
4. **提供部署指南**：確保正確的部署流程
5. **建立故障排除手冊**：協助解決常見問題

## 具體需求

### 1. 更新架構文件

#### 1.1 更新 `docs/architecture_overview.md`

**新增 HTTP 客戶端架構章節**：

```markdown
## HTTP 客戶端架構

### 概述

本專案使用中央化的 HTTP 客戶端來處理所有與 Civitai API 的通訊。此設計提供：

- 統一的錯誤處理機制
- 智慧重試和超時控制
- 效能監控和統計
- 連線池最佳化
- 快取機制

### 核心組件

#### CivitaiHttpClient
```python
class CivitaiHttpClient:
    """中央化的 HTTP 客戶端，處理所有 Civitai API 請求。"""
```

**功能特性**：
- Bearer token 認證
- 自動重試機制（指數退避）
- 超時控制（可設定）
- 串流下載支援
- 錯誤處理和使用者提示

#### OptimizedHTTPClient
```python
class OptimizedHTTPClient(CivitaiHttpClient):
    """最佳化版本的 HTTP 客戶端，包含連線池和監控。"""
```

**效能最佳化**：
- 連線池管理
- 並行下載支援
- 記憶體使用監控
- 智慧快取系統

### 模組整合

#### API 請求模組 (civitai.py)
- 所有 Civitai API 請求統一使用 HTTP 客戶端
- 提供模型資訊、版本資訊等 API 存取
- 統一的錯誤處理和使用者提示

#### 檔案下載模組 (downloader.py)
- 大檔案下載最佳化
- 斷點續傳支援
- 進度追蹤整合
- 並行下載支援

#### 圖片處理模組 (civitai_gallery_action.py, ishortcut.py)
- 圖片下載統一化
- 快取機制
- 批次下載最佳化

### 錯誤處理策略

#### HTTP 錯誤分類
1. **4xx 客戶端錯誤**：API 金鑰、請求格式等問題
2. **5xx 伺服器錯誤**：Civitai 伺服器問題
3. **網路錯誤**：連線、超時等問題
4. **應用錯誤**：檔案系統、權限等問題

#### 錯誤處理流程
```
HTTP 請求 → 錯誤檢測 → 重試判斷 → 使用者提示 → 優雅降級
```

### 監控和統計

#### 統計資料收集
- 請求總數和成功率
- 響應時間統計
- 下載速度統計
- 錯誤類型統計
- 頻寬使用統計

#### 監控介面
- 即時狀態顯示
- 效能報告生成
- 錯誤統計檢視
- 統計資料清除功能
```

#### 1.2 建立 `docs/http_client_guide.md`

**建立完整的 HTTP 客戶端使用指南**：

```markdown
# HTTP 客戶端使用指南

## 快速開始

### 基本使用

```python
from civitai_manager_libs.http_client import CivitaiHttpClient

# 建立客戶端實例
client = CivitaiHttpClient(
    api_key="your_api_key",
    timeout=30,
    max_retries=3
)

# 發送 GET 請求
data = client.get_json("https://civitai.com/api/v1/models/12345")
if data:
    print(f"Model name: {data['name']}")
```

### 檔案下載

```python
# 下載檔案
success = client.download_file(
    url="https://civitai.com/path/to/file",
    filepath="./downloads/model.safetensors"
)

if success:
    print("Download completed!")
else:
    print("Download failed!")
```

### 進度追蹤

```python
def progress_callback(downloaded, total, speed):
    percentage = (downloaded / total * 100) if total > 0 else 0
    print(f"Progress: {percentage:.1f}% {speed}")

client.download_file_with_resume(
    url="https://civitai.com/path/to/large_file",
    filepath="./downloads/large_model.safetensors",
    progress_callback=progress_callback
)
```

## 進階功能

### 自訂設定

```python
# 在 setting.py 中調整設定
http_timeout = 60  # 60 秒超時
http_max_retries = 5  # 最多重試 5 次
http_retry_delay = 10  # 重試間隔 10 秒
```

### 錯誤處理

```python
try:
    data = client.get_json("https://civitai.com/api/v1/models/invalid_id")
except Exception as e:
    # HTTP 客戶端內部已處理錯誤並顯示使用者友善訊息
    # 這裡只需要處理應用程式邏輯
    print("Failed to get model data")
```

### 效能監控

```python
# 取得效能統計
from civitai_manager_libs.monitoring import get_http_monitor

monitor = get_http_monitor()
report = monitor.get_performance_report()

print(f"Total requests: {report['total_requests']}")
print(f"Error rate: {report['error_rate_percent']:.2f}%")
print(f"Average response time: {report['avg_response_time_ms']:.1f}ms")
```

## 最佳實踐

### 1. 重複使用客戶端實例

```python
# 好的做法：重複使用客戶端實例
client = CivitaiHttpClient()

for model_id in model_ids:
    data = client.get_json(f"https://civitai.com/api/v1/models/{model_id}")
    process_model_data(data)
```

### 2. 適當的超時設定

```python
# 根據用途設定不同的超時時間
api_client = CivitaiHttpClient(timeout=30)      # API 請求
download_client = CivitaiHttpClient(timeout=300) # 檔案下載
```

### 3. 錯誤處理

```python
# 檢查回傳值而不是依賴例外
data = client.get_json(url)
if data is None:
    # 處理失敗情況
    use_cached_data()
else:
    # 處理成功情況
    process_data(data)
```

### 4. 記憶體管理

```python
# 對於大檔案下載，使用串流模式
response = client.get_stream_response(large_file_url)
if response:
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    response.close()
```

## 故障排除

### 常見問題

#### 1. 請求超時
**症狀**：請求經常超時
**解決方案**：
- 增加超時時間設定
- 檢查網路連線
- 確認 Civitai 服務狀態

#### 2. API 金鑰錯誤
**症狀**：收到 401 或 403 錯誤
**解決方案**：
- 檢查 API 金鑰設定
- 確認 API 金鑰有效性
- 檢查 API 配額是否用盡

#### 3. 下載失敗
**症狀**：檔案下載經常失敗
**解決方案**：
- 檢查磁碟空間
- 確認檔案寫入權限
- 增加重試次數

#### 4. 記憶體使用過高
**症狀**：應用程式記憶體使用量持續增長
**解決方案**：
- 啟用記憶體監控
- 調整下載塊大小
- 檢查是否有記憶體洩漏

### 除錯模式

```python
# 啟用詳細除錯輸出
import logging
logging.basicConfig(level=logging.DEBUG)

# 檢查 HTTP 客戶端統計
client = get_http_client()
print(f"Total requests: {client._stats['total_requests']}")
print(f"Failed requests: {client._stats['failed_requests']}")
print(f"Error counts: {client._stats['error_counts']}")
```
```

### 2. 建立使用者指南

#### 2.1 建立 `docs/user_guide.md`

**建立面向一般使用者的指南**：

```markdown
# Civitai Shortcut 使用者指南

## 網路設定與故障排除

### 基本設定

#### API 金鑰設定
1. 前往 [Civitai API 設定頁面](https://civitai.com/user/account)
2. 生成新的 API 金鑰
3. 在 Civitai Shortcut 設定中輸入 API 金鑰

#### 網路超時設定
- **預設值**：20 秒
- **建議值**：
  - 快速網路：15-20 秒
  - 一般網路：30-45 秒
  - 慢速網路：60-90 秒

#### 重試設定
- **預設值**：3 次重試
- **建議值**：
  - 穩定網路：3 次
  - 不穩定網路：5-7 次

### 常見問題解決

#### 「網路連線失敗」錯誤
**可能原因**：
- 網路連線中斷
- 防火牆阻擋
- DNS 解析問題

**解決方法**：
1. 檢查網路連線
2. 重新啟動路由器
3. 嘗試使用 VPN
4. 檢查防火牆設定

#### 「請求超時」錯誤
**可能原因**：
- 網路速度太慢
- Civitai 伺服器繁忙
- 超時設定太短

**解決方法**：
1. 增加超時時間設定
2. 稍後再試
3. 檢查網路速度

#### 「API 金鑰無效」錯誤
**可能原因**：
- API 金鑰錯誤
- API 金鑰已過期
- API 配額用盡

**解決方法**：
1. 重新檢查 API 金鑰
2. 生成新的 API 金鑰
3. 檢查 API 使用配額

#### 「下載失敗」錯誤
**可能原因**：
- 磁碟空間不足
- 檔案寫入權限問題
- 網路連線中斷

**解決方法**：
1. 清理磁碟空間
2. 檢查資料夾權限
3. 重新嘗試下載

### 效能最佳化建議

#### 下載設定最佳化
- **併發下載數**：建議 2-3 個
- **下載塊大小**：建議 1MB
- **啟用斷點續傳**：建議開啟

#### 快取設定
- **啟用快取**：建議開啟
- **快取大小**：建議 100-200MB
- **快取過期時間**：建議 1 小時

#### 記憶體最佳化
- **記憶體限制**：建議 200MB
- **記憶體監控**：建議開啟
- **大檔案模式**：自動開啟

### 監控和診斷

#### 效能監控面板
在 Civitai Shortcut 介面中可以找到「HTTP 客戶端監控」頁籤，提供：
- 即時請求統計
- 錯誤率監控
- 下載速度統計
- 頻寬使用情況

#### 常用診斷資訊
- **總請求數**：累計 API 請求次數
- **成功率**：請求成功的百分比
- **平均響應時間**：API 回應的平均時間
- **錯誤統計**：各類錯誤的發生次數

#### 效能指標說明
- **響應時間 < 1000ms**：良好
- **響應時間 1000-3000ms**：一般
- **響應時間 > 3000ms**：需要最佳化
- **錯誤率 < 5%**：良好
- **錯誤率 5-15%**：一般
- **錯誤率 > 15%**：需要檢查

### 進階設定

#### 自訂超時時間
```
設定 → 網路設定 → HTTP 超時時間：30 秒
```

#### 自訂重試次數
```
設定 → 網路設定 → 最大重試次數：5 次
```

#### 自訂下載路徑
```
設定 → 下載設定 → 下載資料夾：./downloads
```

#### 自訂快取設定
```
設定 → 快取設定 → 啟用快取：是
設定 → 快取設定 → 快取大小：100MB
設定 → 快取設定 → 快取過期時間：3600 秒
```

### 聯絡支援

如果遇到無法解決的問題，請提供以下資訊：
1. 錯誤訊息的完整文字
2. 操作步驟
3. 網路環境描述
4. 效能監控面板的截圖
5. 系統資訊（作業系統、Python 版本等）
```

### 3. 建立維護文件

#### 3.1 建立 `docs/maintenance_guide.md`

```markdown
# 維護指南

## 程式碼維護

### HTTP 客戶端擴展

#### 新增 API 端點支援
1. 在 `http_client.py` 中新增對應方法
2. 在相關模組中使用新方法
3. 新增對應的測試
4. 更新文件

**範例**：
```python
def get_user_info(self, user_id: str) -> Optional[Dict]:
    """Get user information by user ID."""
    url = f"{self.base_url}/users/{user_id}"
    return self.get_json(url)
```

#### 新增錯誤類型處理
1. 在 `_handle_http_error` 方法中新增處理邏輯
2. 新增對應的使用者友善訊息
3. 更新錯誤統計收集
4. 新增測試案例

#### 效能最佳化
1. 監控效能指標
2. 識別效能瓶頸
3. 實作最佳化方案
4. 驗證最佳化效果

### 錯誤處理維護

#### 新增錯誤類型
1. 識別新的錯誤情況
2. 實作錯誤處理邏輯
3. 新增使用者友善訊息
4. 更新測試覆蓋

#### 錯誤訊息本地化
1. 提取錯誤訊息到設定檔
2. 實作多語言支援
3. 更新訊息顯示邏輯
4. 測試不同語言版本

### 監控系統維護

#### 新增監控指標
1. 識別需要監控的新指標
2. 實作資料收集邏輯
3. 更新監控介面
4. 新增報告生成功能

#### 統計資料存儲
1. 實作統計資料持久化
2. 新增資料清理機制
3. 實作資料匯出功能
4. 新增資料分析工具

## 部署維護

### 設定檔管理
- 保持設定檔案的向後相容性
- 新增設定項目時提供預設值
- 文件化所有設定選項
- 實作設定驗證邏輯

### 相依性管理
- 定期更新相依套件
- 測試相依性更新的相容性
- 維護最小相依性要求
- 監控安全性更新

### 效能監控
- 定期檢查效能指標
- 監控記憶體使用情況
- 追蹤錯誤率變化
- 分析使用模式

## 故障排除

### 常見問題診斷

#### 記憶體洩漏
**症狀**：記憶體使用量持續增長
**診斷方法**：
1. 啟用記憶體監控
2. 分析記憶體使用模式
3. 檢查物件引用關係
4. 使用記憶體分析工具

**解決方法**：
1. 修復記憶體洩漏
2. 增加記憶體清理邏輯
3. 最佳化物件生命週期
4. 新增記憶體使用限制

#### 效能退化
**症狀**：響應時間變長
**診斷方法**：
1. 分析效能監控資料
2. 檢查網路連線品質
3. 分析 API 回應時間
4. 檢查系統資源使用

**解決方法**：
1. 最佳化網路設定
2. 增加快取使用
3. 調整連線池設定
4. 最佳化演算法邏輯

#### 連線問題
**症狀**：頻繁連線錯誤
**診斷方法**：
1. 檢查網路連線狀態
2. 分析錯誤類型分佈
3. 測試 DNS 解析
4. 檢查防火牆設定

**解決方法**：
1. 調整重試策略
2. 最佳化超時設定
3. 實作連線監控
4. 新增連線恢復機制

### 日誌分析

#### 錯誤日誌分析
```python
# 分析錯誤模式
import re
from collections import Counter

def analyze_error_logs(log_file):
    error_patterns = Counter()
    
    with open(log_file, 'r') as f:
        for line in f:
            if '[http_client]' in line and 'error' in line.lower():
                # 提取錯誤類型
                error_type = extract_error_type(line)
                error_patterns[error_type] += 1
    
    return error_patterns
```

#### 效能日誌分析
```python
# 分析效能趨勢
def analyze_performance_logs(log_file):
    response_times = []
    
    with open(log_file, 'r') as f:
        for line in f:
            if 'response_time' in line:
                time = extract_response_time(line)
                response_times.append(time)
    
    return {
        'avg_response_time': sum(response_times) / len(response_times),
        'max_response_time': max(response_times),
        'min_response_time': min(response_times)
    }
```

## 開發指南

### 新增功能開發流程
1. 需求分析和設計
2. 實作核心功能
3. 新增錯誤處理
4. 撰寫測試案例
5. 更新文件
6. 程式碼審查
7. 部署和監控

### 測試指南
- 單元測試涵蓋率應達到 85% 以上
- 整合測試應涵蓋主要使用情境
- 效能測試應包含負載測試
- 錯誤處理測試應涵蓋所有錯誤類型

### 程式碼品質標準
- 遵循 PEP 8 編碼規範
- 使用 black 進行程式碼格式化
- 使用 flake8 進行程式碼檢查
- 所有公開 API 都應有文件字串

### 版本發布流程
1. 功能開發完成
2. 所有測試通過
3. 文件更新完成
4. 版本號碼更新
5. 發布說明撰寫
6. 標籤建立和發布
7. 部署到生產環境
```

### 4. 建立部署指南

#### 4.1 建立 `docs/deployment_guide.md`

```markdown
# 部署指南

## 系統需求

### 基本需求
- Python 3.7 或更新版本
- 最低 4GB RAM
- 最低 10GB 可用磁碟空間
- 穩定的網路連線

### 建議需求
- Python 3.9 或更新版本
- 8GB 或更多 RAM
- 50GB 或更多可用磁碟空間
- 高速網路連線（10Mbps 或更快）

### 相依性套件
```bash
pip install -r requirements.txt
```

**必要套件**：
- requests >= 2.25.0
- gradio >= 3.41.2
- pillow >= 8.0.0
- tqdm >= 4.60.0

**可選套件**：
- psutil >= 5.8.0（記憶體監控）
- numpy >= 1.20.0（統計分析）

## 安裝步驟

### 1. 環境準備

#### 建立虛擬環境
```bash
python -m venv civitai_env
source civitai_env/bin/activate  # Linux/Mac
# 或
civitai_env\Scripts\activate  # Windows
```

#### 安裝相依性
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. 設定檔案準備

#### 複製預設設定
```bash
cp config/default_config.json config/user_config.json
```

#### 編輯設定檔案
```json
{
  "civitai_api_key": "your_api_key_here",
  "http_timeout": 30,
  "http_max_retries": 3,
  "download_path": "./downloads",
  "cache_enabled": true,
  "cache_size_mb": 100
}
```

### 3. 目錄結構建立

```bash
mkdir -p downloads
mkdir -p cache
mkdir -p logs
mkdir -p outputs
```

### 4. 權限設定

#### Linux/Mac
```bash
chmod +x start.sh
chmod 755 downloads cache logs outputs
```

#### Windows
確保應用程式對以下目錄有寫入權限：
- downloads
- cache
- logs
- outputs

## 設定最佳化

### HTTP 客戶端設定

#### 效能設定
```json
{
  "http_pool_connections": 10,
  "http_pool_maxsize": 20,
  "http_enable_chunked_download": true,
  "http_max_parallel_chunks": 4,
  "http_chunk_size": 1048576
}
```

#### 監控設定
```json
{
  "http_enable_monitoring": true,
  "http_stats_retention_hours": 24,
  "http_performance_log_level": "INFO"
}
```

#### 快取設定
```json
{
  "http_cache_enabled": true,
  "http_cache_max_size_mb": 100,
  "http_cache_default_ttl": 3600
}
```

### 記憶體管理設定

```json
{
  "http_max_memory_usage_mb": 200,
  "http_memory_monitor_enabled": true,
  "http_memory_check_interval": 10
}
```

## 啟動方式

### Standalone 模式
```bash
python main.py
```

### WebUI 擴展模式
1. 將專案複製到 WebUI 的 extensions 目錄
2. 重新啟動 WebUI
3. 在擴展頁籤中找到 Civitai Shortcut

### 背景服務模式

#### Linux (systemd)
建立服務檔案 `/etc/systemd/system/civitai-shortcut.service`：
```ini
[Unit]
Description=Civitai Shortcut Service
After=network.target

[Service]
Type=simple
User=civitai
WorkingDirectory=/path/to/civitai-shortcut
ExecStart=/path/to/civitai_env/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

啟動服務：
```bash
sudo systemctl enable civitai-shortcut
sudo systemctl start civitai-shortcut
```

#### Windows (Service)
使用 NSSM 或類似工具將應用程式註冊為 Windows 服務。

## 監控和維護

### 日誌檔案
- `logs/http_client.log`：HTTP 客戶端日誌
- `logs/application.log`：應用程式日誌
- `logs/error.log`：錯誤日誌

### 日誌輪轉設定
```python
import logging
from logging.handlers import RotatingFileHandler

# 設定日誌輪轉
handler = RotatingFileHandler(
    'logs/http_client.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

### 健康檢查
建立健康檢查端點：
```python
def health_check():
    """健康檢查端點"""
    status = {
        'http_client': 'ok',
        'cache': 'ok',
        'disk_space': 'ok',
        'memory': 'ok'
    }
    
    # 檢查 HTTP 客戶端狀態
    client = get_http_client()
    if hasattr(client, '_stats'):
        error_rate = client._stats['failed_requests'] / max(1, client._stats['total_requests'])
        if error_rate > 0.2:  # 20% 錯誤率
            status['http_client'] = 'warning'
    
    # 檢查磁碟空間
    import shutil
    disk_usage = shutil.disk_usage('.')
    free_space_gb = disk_usage.free / (1024**3)
    if free_space_gb < 5:  # 少於 5GB
        status['disk_space'] = 'warning'
    
    return status
```

### 效能監控
定期檢查以下指標：
- HTTP 請求成功率
- 平均響應時間
- 記憶體使用量
- 磁碟空間使用量
- 快取命中率

## 故障排除

### 啟動失敗

#### Python 版本問題
```bash
python --version  # 確認 Python 版本
pip list  # 檢查已安裝套件
```

#### 相依性問題
```bash
pip install --upgrade -r requirements.txt
```

#### 權限問題
```bash
# Linux/Mac
chmod 755 .
chmod 644 *.py
chmod +x start.sh

# Windows
# 以管理員身分執行
```

### 網路連線問題

#### DNS 解析問題
```bash
nslookup civitai.com
ping civitai.com
```

#### 防火牆問題
確保允許以下連線：
- civitai.com (443)
- image.civitai.com (443)
- api.civitai.com (443)

#### 代理設定
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

### 效能問題

#### 記憶體不足
- 減少併發下載數量
- 啟用記憶體監控
- 減少快取大小

#### 磁碟空間不足
- 清理下載檔案
- 增加磁碟空間
- 啟用自動清理

#### 網路速度慢
- 調整超時設定
- 減少併發連線數
- 啟用下載壓縮

## 更新和升級

### 應用程式更新
1. 備份設定檔案
2. 停止應用程式
3. 更新程式碼
4. 安裝新相依性
5. 更新設定檔案
6. 重新啟動應用程式
7. 驗證功能正常

### 設定檔案遷移
```python
def migrate_config(old_config, new_version):
    """遷移設定檔案到新版本"""
    # 實作設定檔案遷移邏輯
    pass
```

### 資料庫遷移
如果使用資料庫存儲統計資料：
```sql
-- 範例遷移腳本
ALTER TABLE http_stats ADD COLUMN new_field VARCHAR(255);
UPDATE http_stats SET new_field = 'default_value';
```

## 安全性考慮

### API 金鑰保護
- 使用環境變數存儲 API 金鑰
- 定期輪換 API 金鑰
- 監控 API 金鑰使用情況

### 檔案系統安全
- 限制檔案存取權限
- 驗證下載檔案路徑
- 防止目錄遍歷攻擊

### 網路安全
- 使用 HTTPS 連線
- 驗證 SSL 憑證
- 實作速率限制
```

### 5. 建立故障排除手冊

#### 5.1 建立 `docs/troubleshooting.md`

```markdown
# 故障排除手冊

## 快速診斷清單

### 第一步：基本檢查
- [ ] 網路連線正常
- [ ] Python 版本 >= 3.7
- [ ] 所有相依性已安裝
- [ ] API 金鑰設定正確
- [ ] 磁碟空間充足 (> 5GB)

### 第二步：日誌檢查
```bash
# 檢查最新的錯誤日誌
tail -n 50 logs/error.log

# 檢查 HTTP 客戶端日誌
tail -n 50 logs/http_client.log

# 檢查應用程式日誌
tail -n 50 logs/application.log
```

### 第三步：統計檢查
在監控面板中檢查：
- 錯誤率是否過高 (> 15%)
- 響應時間是否異常 (> 5000ms)
- 記憶體使用是否過高

## 常見錯誤及解決方案

### 網路連線錯誤

#### ConnectionError: Max retries exceeded
**症狀**：
```
[http_client] ConnectionError: HTTPSConnectionPool(host='civitai.com', port=443): 
Max retries exceeded with url: /api/v1/models/12345
```

**可能原因**：
1. 網路連線中斷
2. DNS 解析失敗
3. 防火牆阻擋
4. Civitai 服務中斷

**解決步驟**：
1. 檢查網路連線：`ping google.com`
2. 檢查 DNS 解析：`nslookup civitai.com`
3. 測試 HTTPS 連線：`curl -I https://civitai.com`
4. 檢查防火牆設定
5. 查看 Civitai 狀態頁面

**設定調整**：
```python
# 增加重試次數
http_max_retries = 5

# 增加超時時間
http_timeout = 60

# 調整重試延遲
http_retry_delay = 15
```

#### ReadTimeout: HTTPSConnectionPool read timed out
**症狀**：
```
[http_client] ReadTimeout: HTTPSConnectionPool(host='civitai.com', port=443): 
Read timed out. (read timeout=30)
```

**可能原因**：
1. 網路速度太慢
2. 伺服器回應慢
3. 超時設定太短

**解決步驟**：
1. 測試網路速度
2. 增加超時時間設定
3. 檢查是否在高峰時段

**設定調整**：
```python
# 針對不同操作設定不同超時時間
api_timeout = 45  # API 請求
download_timeout = 300  # 檔案下載
image_timeout = 60  # 圖片下載
```

### HTTP 狀態碼錯誤

#### 401 Unauthorized
**症狀**：
```
[http_client] HTTP 401 error for https://civitai.com/api/v1/models/12345
```

**可能原因**：
1. API 金鑰錯誤
2. API 金鑰已過期
3. API 金鑰權限不足

**解決步驟**：
1. 檢查 API 金鑰設定
2. 前往 Civitai 確認 API 金鑰狀態
3. 重新生成 API 金鑰

#### 403 Forbidden
**症狀**：
```
[http_client] HTTP 403 error for https://civitai.com/api/v1/models/12345
```

**可能原因**：
1. 模型為私人模型
2. 地區限制
3. API 配額用盡

**解決步驟**：
1. 確認模型是否為公開模型
2. 檢查 API 配額使用情況
3. 等待配額重置

#### 429 Too Many Requests
**症狀**：
```
[http_client] HTTP 429 error for https://civitai.com/api/v1/models/12345
```

**可能原因**：
1. 請求過於頻繁
2. API 速率限制

**解決步驟**：
1. 減少併發請求數量
2. 增加請求間隔
3. 等待速率限制重置

**設定調整**：
```python
# 減少併發請求
max_concurrent_requests = 2

# 增加請求間隔
request_delay = 1.0  # 秒

# 啟用智慧重試
enable_smart_retry = True
```

#### 500/502/503/504 Server Errors
**症狀**：
```
[http_client] HTTP 500 error for https://civitai.com/api/v1/models/12345
```

**可能原因**：
1. Civitai 伺服器問題
2. 維護中
3. 負載過高

**解決步驟**：
1. 等待一段時間後重試
2. 檢查 Civitai 狀態頁面
3. 增加重試次數和延遲

#### 524 Cloudflare Timeout
**症狀**：
```
[http_client] HTTP 524 error for https://civitai.com/api/v1/models/12345
```

**可能原因**：
1. Cloudflare 超時
2. 上游伺服器回應慢

**解決步驟**：
1. 等待後重試
2. 增加超時時間
3. 使用較小的請求批次

### 檔案下載錯誤

#### PermissionError: Permission denied
**症狀**：
```
PermissionError: [Errno 13] Permission denied: './downloads/model.safetensors'
```

**可能原因**：
1. 檔案權限問題
2. 目錄不存在
3. 磁碟唯讀

**解決步驟**：
```bash
# Linux/Mac
chmod 755 downloads/
ls -la downloads/

# Windows
# 檢查資料夾屬性和權限
```

#### OSError: No space left on device
**症狀**：
```
OSError: [Errno 28] No space left on device
```

**可能原因**：
1. 磁碟空間不足
2. 暫存空間不足

**解決步驟**：
```bash
# 檢查磁碟空間
df -h  # Linux/Mac
dir   # Windows

# 清理暫存檔案
rm -f downloads/*.tmp
rm -f cache/*.cache
```

#### FileNotFoundError: No such file or directory
**症狀**：
```
FileNotFoundError: [Errno 2] No such file or directory: './downloads'
```

**解決步驟**：
```bash
# 建立必要目錄
mkdir -p downloads cache logs outputs
```

### 記憶體相關錯誤

#### MemoryError: Unable to allocate memory
**症狀**：
```
MemoryError: Unable to allocate 1073741824 bytes
```

**可能原因**：
1. 可用記憶體不足
2. 下載檔案過大
3. 記憶體洩漏

**解決步驟**：
1. 關閉其他應用程式
2. 重新啟動應用程式
3. 啟用記憶體監控

**設定調整**：
```python
# 啟用記憶體限制
http_max_memory_usage_mb = 100

# 啟用記憶體監控
http_memory_monitor_enabled = True

# 減少塊大小
http_chunk_size = 65536  # 64KB
```

### 應用程式錯誤

#### ImportError: No module named 'requests'
**症狀**：
```
ImportError: No module named 'requests'
```

**解決步驟**：
```bash
# 安裝缺少的套件
pip install requests

# 或安裝所有相依性
pip install -r requirements.txt
```

#### ValueError: Invalid configuration
**症狀**：
```
ValueError: Invalid configuration in setting.py
```

**解決步驟**：
1. 檢查設定檔案語法
2. 確認所有必要設定項目
3. 重置為預設設定

**重置設定**：
```bash
# 備份現有設定
cp setting.py setting.py.backup

# 複製預設設定
cp config/default_config.json setting.py
```

## 進階診斷

### 網路診斷工具

#### 測試 API 連線
```bash
# 測試基本連線
curl -I https://civitai.com

# 測試 API 端點
curl -H "Authorization: Bearer YOUR_API_KEY" \
     "https://civitai.com/api/v1/models/12345"
```

#### 網路追蹤
```bash
# Linux/Mac
traceroute civitai.com

# Windows
tracert civitai.com
```

#### DNS 診斷
```bash
# 檢查 DNS 解析
nslookup civitai.com
dig civitai.com

# 嘗試不同的 DNS 伺服器
nslookup civitai.com 8.8.8.8
```

### 效能診斷

#### 記憶體使用分析
```python
import psutil
import os

def analyze_memory_usage():
    """分析記憶體使用情況"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    print(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")
    
    # 檢查系統記憶體
    system_memory = psutil.virtual_memory()
    print(f"System memory usage: {system_memory.percent}%")
```

#### 網路效能測試
```python
import time
import requests

def test_network_performance():
    """測試網路效能"""
    test_urls = [
        "https://civitai.com",
        "https://api.civitai.com",
        "https://image.civitai.com"
    ]
    
    for url in test_urls:
        start_time = time.time()
        try:
            response = requests.get(url, timeout=10)
            end_time = time.time()
            
            print(f"{url}: {response.status_code} "
                  f"({(end_time - start_time) * 1000:.1f}ms)")
        except Exception as e:
            print(f"{url}: Error - {e}")
```

### 日誌分析工具

#### 錯誤統計分析
```python
import re
from collections import Counter

def analyze_error_logs(log_file="logs/error.log"):
    """分析錯誤日誌"""
    error_counts = Counter()
    
    with open(log_file, 'r') as f:
        for line in f:
            # 提取錯誤類型
            if 'HTTP' in line and 'error' in line:
                match = re.search(r'HTTP (\d+)', line)
                if match:
                    status_code = match.group(1)
                    error_counts[f'HTTP_{status_code}'] += 1
            
            elif 'ConnectionError' in line:
                error_counts['ConnectionError'] += 1
            
            elif 'Timeout' in line:
                error_counts['Timeout'] += 1
    
    return error_counts
```

#### 效能趨勢分析
```python
def analyze_performance_trends(log_file="logs/http_client.log"):
    """分析效能趨勢"""
    response_times = []
    
    with open(log_file, 'r') as f:
        for line in f:
            # 提取響應時間
            match = re.search(r'response_time: ([\d.]+)', line)
            if match:
                response_time = float(match.group(1))
                response_times.append(response_time)
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"Average response time: {avg_time:.2f}ms")
        print(f"Max response time: {max_time:.2f}ms")
        print(f"Min response time: {min_time:.2f}ms")
```

## 聯絡支援

如果問題仍然無法解決，請收集以下資訊並聯絡技術支援：

### 必要資訊
1. **錯誤訊息**：完整的錯誤堆疊追蹤
2. **系統資訊**：作業系統、Python 版本
3. **網路環境**：ISP、是否使用代理
4. **重現步驟**：詳細的操作步驟
5. **日誌檔案**：相關的日誌片段

### 收集系統資訊
```python
import platform
import sys
import requests

def collect_system_info():
    """收集系統資訊"""
    info = {
        'platform': platform.platform(),
        'python_version': sys.version,
        'requests_version': requests.__version__,
        'architecture': platform.architecture(),
        'processor': platform.processor()
    }
    
    return info
```

### 聯絡方式
- GitHub Issues: https://github.com/your-repo/issues
- 電子郵件: support@example.com
- 文件網站: https://your-docs-site.com
```

## 驗收標準

### 1. 文件完整性

- [ ] 所有新功能都有對應的文件
- [ ] 架構變更已更新到文件中
- [ ] 使用者指南清楚易懂
- [ ] 維護指南詳細完整
- [ ] 部署指南可操作
- [ ] 故障排除手冊實用

### 2. 文件品質

- [ ] 所有文件使用正體中文撰寫（除程式碼範例）
- [ ] 程式碼範例正確且可執行
- [ ] 圖片和截圖清晰
- [ ] 連結和參考正確

### 3. 使用性測試

- [ ] 新使用者能按照指南成功部署
- [ ] 常見問題都有解決方案
- [ ] 故障排除步驟有效
- [ ] 維護指南可操作

### 4. 文件更新機制

- [ ] 建立文件更新流程
- [ ] 設定文件版本控制
- [ ] 建立文件審查機制
- [ ] 設定定期更新提醒

## 相關檔案

- **更新**：`docs/architecture_overview.md`
- **新建立**：`docs/http_client_guide.md`
- **新建立**：`docs/user_guide.md`
- **新建立**：`docs/maintenance_guide.md`
- **新建立**：`docs/deployment_guide.md`
- **新建立**：`docs/troubleshooting.md`
- **更新**：`README.md`

## 專案完成

完成此項目後，中央化 Civitai HTTP 客戶端的完整開發計劃就全部完成了。所有模組都已重構使用統一的 HTTP 處理機制，並且具備完整的文件和維護指南。
