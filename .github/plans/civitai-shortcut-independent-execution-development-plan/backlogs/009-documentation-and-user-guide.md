# Backlog 009: Docker 部署文件建立

## 優先級
**中 (Medium)** - 為獨立模式提供容器化部署文件

## 估算工作量
**1-2 工作天**

## 目標描述
建立專門的 Docker 部署文件，提供完整的容器化部署指南。專注於 Docker 相關的安裝和使用說明，包括從 Docker Registry 拉取映像和本地建置兩種方式。

## 接受標準 (Definition of Done)
1. ✅ Docker 部署文件建立完成
2. ✅ 包含 Docker Registry 拉取說明
3. ✅ 包含本地建置指南
4. ✅ Docker Compose 部署說明
5. ✅ 基本故障排除和維護指南
6. ✅ 所有指令經過測試驗證

## 詳細任務

### 任務 9.1: 建立 Docker 部署文件
**預估時間：1 天**

1. **建立 DOCKER_DEPLOYMENT.md 檔案**
   - 系統需求說明
   - Docker 和 Docker Compose 安裝指南
   - 三種部署方式的詳細說明
   - 設定和資料管理指南

2. **文件內容結構**
   ```markdown
   # Civitai Shortcut - Docker 部署指南

   ## 系統需求
   - Docker 20.10 或更高版本
   - Docker Compose 2.0 或更高版本（如使用 Compose 部署）
   - 至少 2GB 可用記憶體
   - 至少 10GB 可用硬碟空間

   ## 快速開始

   ### 準備工作
   在啟動容器之前，建議先建立必要的目錄結構：
   ```bash
   # 建立必要的目錄
   mkdir -p data models outputs
   
   # 設定適當的權限（Linux/macOS）
   chmod 755 data models outputs
   ```

   ### 方式一：使用預建映像（推薦）
   ```bash
   # 拉取最新映像
   docker pull ghcr.io/civitai/civitai-shortcut:latest
   
   # 啟動容器
   docker run -d \
     --name civitai-shortcut \
     -p 7860:7860 \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/models:/app/models \
     -v $(pwd)/outputs:/app/outputs \
     ghcr.io/civitai/civitai-shortcut:latest
   ```

   ### 方式二：使用 Docker Compose（推薦）
   ```bash
   # 下載 docker-compose.yml
   curl -O https://raw.githubusercontent.com/civitai/sd_civitai_extension/main/docker-compose.yml
   
   # 啟動服務
   docker-compose up -d
   ```

   ### 方式三：本地建置
   ```bash
   # 複製儲存庫
   git clone https://github.com/civitai/sd_civitai_extension.git
   cd sd_civitai_extension
   
   # 建置映像
   docker build -t civitai-shortcut:local .
   
   # 啟動容器（使用完整的 volume mount）
   docker run -d \
     --name civitai-shortcut \
     -p 7860:7860 \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/models:/app/models \
     -v $(pwd)/outputs:/app/outputs \
     civitai-shortcut:local
   ```

   ## 設定說明

   ### 環境變數
   - `CIVITAI_SHORTCUT_DATA_DIR`: 資料目錄路徑（預設：/app/data）
   - `CIVITAI_SHORTCUT_PORT`: 服務埠號（預設：7860）
   - `CIVITAI_SHORTCUT_HOST`: 綁定主機（預設：0.0.0.0）

   ### 資料目錄對應
   我們使用 Docker volume mount 將容器內的目錄對應到主機：
   - `./data` ↔ `/app/data`: 設定檔和應用程式資料
   - `./models` ↔ `/app/models`: 下載的模型檔案
   - `./outputs` ↔ `/app/outputs`: 輸出檔案和快取
   
   **優點**：
   - 容器重新建立後資料不會遺失
   - 可直接在主機上存取和管理檔案
   - 備份和還原操作簡單直接

   ### 自訂設定檔
   ```bash
   # 將本地設定檔對應到容器（使用完整的 volume mount）
   docker run -d \
     --name civitai-shortcut \
     -p 7860:7860 \
     -v $(pwd)/config.json:/app/config.json \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/models:/app/models \
     -v $(pwd)/outputs:/app/outputs \
     ghcr.io/civitai/civitai-shortcut:latest
   ```

### 任務 9.2: 文件測試與驗證
**預估時間：0.5 天**

1. **部署指南驗證**
   - 在乾淨環境中測試所有部署方式
   - 驗證 Docker 指令正確性
   - 測試故障排除步驟有效性

2. **跨平台測試**
   - 在不同作業系統測試（Linux, macOS, Windows）
   - 驗證 Docker Compose 設定
   - 確認資料持久化正常運作

### 任務 9.3: 文件最佳化
**預估時間：0.5 天**

1. **內容最佳化**
   - 確保指令格式正確
   - 新增必要的安全提醒
   - 完善故障排除章節

2. **使用者體驗改善**
   - 新增清晰的步驟編號
   - 提供複製友好的指令區塊
   - 新增重要提示和警告

## 交付物

1. **DOCKER_DEPLOYMENT.md**：完整的 Docker 部署指南
2. **docker-compose.yml 範例**：生產級 Compose 設定檔
3. **更新腳本範例**：自動化更新工具
4. **故障排除指南**：常見問題解決方案

## 成功指標

1. **部署成功率**：使用者能依照文件成功部署
2. **文件完整性**：涵蓋所有主要部署情境
3. **故障排除有效性**：常見問題都有解決方案
4. **跨平台相容性**：在不同系統上都能正常運作
