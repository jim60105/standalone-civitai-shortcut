# Backlog 008: Docker 容器化和 CI 建立

## 優先級
**中高 (Medium-High)** - 為獨立模式提供容器化部署選項

## 估算工作量
**2-3 工作天**

## 目標描述
為 Civitai Shortcut 獨立執行模式建立 Docker 容器化支援，並設定相關的 CI 流程來自動建置和發布 Docker 映像。專注於提供簡單、可靠的容器化部署方案。

## 接受標準 (Definition of Done)
1. ✅ Dockerfile 建立並測試完成
2. ✅ Docker Compose 檔案建立
3. ✅ GitHub Actions Docker CI 流程建立
4. ✅ 自動化 Docker 映像建置和推送
5. ✅ 多平台 Docker 映像支援（AMD64/ARM64）
6. ✅ 容器化部署驗證通過

## 詳細任務

### 任務 8.1: Dockerfile 建立
**預估時間：2 天**

1. **建立生產級 Dockerfile**
   ```dockerfile
   # Dockerfile
   FROM python:3.10-slim
   
   # 設定工作目錄
   WORKDIR /app
   
   # 安裝系統相依套件
   RUN apt-get update && apt-get install -y \
       git \
       curl \
       && rm -rf /var/lib/apt/lists/*
   
   # 複製相依套件檔案
   COPY requirements.txt .
   
   # 安裝 Python 相依套件
   RUN pip install --no-cache-dir -r requirements.txt
   
   # 複製應用程式程式碼
   COPY scripts/ ./scripts/
   COPY main.py .
   COPY style.css .
   COPY img/ ./img/
   
   # 建立資料目錄
   RUN mkdir -p /app/data /app/models /app/outputs
   
   # 設定環境變數
   ENV PYTHONPATH=/app
   ENV CIVITAI_SHORTCUT_DATA_DIR=/app/data
   
   # 暴露埠號
   EXPOSE 7860
   
   # 設定啟動指令
   CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "7860"]
   ```

2. **建立多階段 Dockerfile（最佳化）**
   ```dockerfile
   # Dockerfile.multi-stage
   FROM python:3.10-slim as builder
   
   WORKDIR /app
   
   # 安裝建置相依套件
   RUN apt-get update && apt-get install -y git
   
   # 複製並安裝 Python 相依套件
   COPY requirements.txt .
   RUN pip install --user --no-cache-dir -r requirements.txt
   
   # 生產階段
   FROM python:3.10-slim
   
   # 從建置階段複製 Python 套件
   COPY --from=builder /root/.local /root/.local
   
   WORKDIR /app
   
   # 複製應用程式
   COPY scripts/ ./scripts/
   COPY main.py .
   COPY style.css .
   COPY img/ ./img/
   
   # 建立必要目錄
   RUN mkdir -p /app/data /app/models /app/outputs
   
   # 設定 PATH
   ENV PATH=/root/.local/bin:$PATH
   ENV PYTHONPATH=/app
   
   EXPOSE 7860
   
   CMD ["python", "main.py", "--host", "0.0.0.0"]
   ```

3. **建立 .dockerignore 檔案**
   ```
   # .dockerignore
   .git
   .github
   .gitignore
   .vscode
   __pycache__
   *.pyc
   *.pyo
   *.pyd
   .Python
   env
   pip-log.txt
   pip-delete-this-directory.txt
   .tox
   .coverage
   .coverage.*
   .cache
   nosetests.xml
   coverage.xml
   *.cover
   *.log
   .DS_Store
   README*.md
   tests/
   docs/
   node_modules/
   .pytest_cache/
   ```

### 任務 8.2: Docker Compose 設定
**預估時間：1 天**

1. **建立 docker-compose.yml**
   ```yaml
   # docker-compose.yml
   version: '3.8'
   
   services:
     civitai-shortcut:
       build: .
       ports:
         - "7860:7860"
       volumes:
         - ./data:/app/data
         - ./models:/app/models
         - ./outputs:/app/outputs
       environment:
         - CIVITAI_SHORTCUT_DATA_DIR=/app/data
       restart: unless-stopped
       
     # 可選：使用預建映像
     # civitai-shortcut:
     #   image: civitai/civitai-shortcut:latest
     #   ports:
     #     - "7860:7860"
     #   volumes:
     #     - ./data:/app/data
     #     - ./models:/app/models
     #     - ./outputs:/app/outputs
     #   restart: unless-stopped
   ```

2. **建立 docker-compose.dev.yml（開發用）**
   ```yaml
   # docker-compose.dev.yml
   version: '3.8'
   
   services:
     civitai-shortcut-dev:
       build:
         context: .
         dockerfile: Dockerfile
       ports:
         - "7860:7860"
       volumes:
         - .:/app
         - ./data:/app/data
       environment:
         - PYTHONPATH=/app
         - CIVITAI_SHORTCUT_DEV=true
       command: python main.py --host 0.0.0.0 --reload
   ```

### 任務 8.3: GitHub Actions CI 建立
**預估時間：1 天**

1. **建立 Docker 建置和推送工作流程**
   ```yaml
   # .github/workflows/docker-build.yml
   name: Build and Push Docker Image
   
   on:
     push:
       branches: [ main, develop ]
       tags: [ 'v*' ]
     pull_request:
       branches: [ main ]
   
   env:
     REGISTRY: ghcr.io
     IMAGE_NAME: ${{ github.repository }}
   
   jobs:
     build-and-push:
       runs-on: ubuntu-latest
       permissions:
         contents: read
         packages: write
   
       steps:
       - name: Checkout repository
         uses: actions/checkout@v4
   
       - name: Set up Docker Buildx
         uses: docker/setup-buildx-action@v3
   
       - name: Log in to Container Registry
         if: github.event_name != 'pull_request'
         uses: docker/login-action@v3
         with:
           registry: ${{ env.REGISTRY }}
           username: ${{ github.actor }}
           password: ${{ secrets.GITHUB_TOKEN }}
   
       - name: Extract metadata
         id: meta
         uses: docker/metadata-action@v5
         with:
           images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
           tags: |
             type=ref,event=branch
             type=ref,event=pr
             type=semver,pattern={{version}}
             type=semver,pattern={{major}}.{{minor}}
             type=raw,value=latest,enable={{is_default_branch}}
   
       - name: Build and push Docker image
         uses: docker/build-push-action@v5
         with:
           context: .
           platforms: linux/amd64,linux/arm64
           push: ${{ github.event_name != 'pull_request' }}
           tags: ${{ steps.meta.outputs.tags }}
           labels: ${{ steps.meta.outputs.labels }}
           cache-from: type=gha
           cache-to: type=gha,mode=max
   ```

## 部署指南

### 使用 Docker 部署

1. **使用預建映像**
   ```bash
   docker pull ghcr.io/civitai/civitai-shortcut:latest
   docker run -d \
     -p 7860:7860 \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/models:/app/models \
     --name civitai-shortcut \
     ghcr.io/civitai/civitai-shortcut:latest
   ```

2. **使用 Docker Compose**
   ```bash
   curl -O https://raw.githubusercontent.com/civitai/sd_civitai_extension/main/docker-compose.yml
   docker-compose up -d
   ```

3. **從原始碼建置**
   ```bash
   git clone https://github.com/civitai/sd_civitai_extension.git
   cd sd_civitai_extension
   docker build -t civitai-shortcut .
   docker run -d -p 7860:7860 civitai-shortcut
   ```

## 維護和監控

### 日誌管理
```bash
# 查看容器日誌
docker logs civitai-shortcut

# 即時監控日誌
docker logs -f civitai-shortcut
```

### 資料備份
```bash
# 備份資料目錄（使用 volume mount，直接從主機目錄備份）
mkdir -p ./backup
cp -r ./data ./backup/data-$(date +%Y%m%d)
cp -r ./models ./backup/models-$(date +%Y%m%d)
cp -r ./outputs ./backup/outputs-$(date +%Y%m%d)
```

### 更新映像
```bash
# 更新到最新版本
docker pull ghcr.io/civitai/civitai-shortcut:latest
docker stop civitai-shortcut
docker rm civitai-shortcut
docker run -d \
  --name civitai-shortcut \
  -p 7860:7860 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/outputs:/app/outputs \
  ghcr.io/civitai/civitai-shortcut:latest
```

## 交付物

1. **Dockerfile**：生產級容器定義
2. **docker-compose.yml**：部署設定檔
3. **GitHub Actions**：自動化 CI 流程

## 成功指標

1. **功能性指標**
   - Docker 映像成功建置
   - 容器正常啟動和運作
   - 多平台映像支援（AMD64/ARM64）

2. **CI/CD 指標**
   - 自動化建置流程正常
   - Docker 映像自動推送成功

3. **使用性指標**
   - 部署文件清晰易懂
   - 使用者能順利部署容器

## 風險與限制

1. **平台限制**：專注於 Docker 容器化，不涉及其他部署方式
2. **功能範圍**：僅為獨立模式提供容器化支援
3. **維護成本**：需要持續維護 Docker 映像和 CI 流程
