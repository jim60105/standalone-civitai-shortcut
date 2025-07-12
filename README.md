# 🚀 Civitai Shortcut

**The ultimate dual-mode AI model management solution for Stable Diffusion**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: AGPLv3](https://img.shields.io/badge/License-AGPLv3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)
[![AUTOMATIC1111](https://img.shields.io/badge/AUTOMATIC1111-WebUI-orange)](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
[![Standalone](https://img.shields.io/badge/Standalone-Mode-green)](https://github.com/jim60105/standalone-civitai-shortcut)

> 🎯 **Effortlessly browse, download, and manage AI models from Civitai with intelligent dual-mode operation - works both as a WebUI extension and standalone application**

## ✨ Project Highlights

### 🔄 **Revolutionary Dual-Mode Architecture**
- **WebUI Integration**: Seamlessly integrates with AUTOMATIC1111/Forge WebUI as a native extension
- **Standalone Operation**: Runs independently with a dedicated Gradio interface - no WebUI required
- **Intelligent Detection**: Automatically adapts to your environment with zero configuration
- **Unified Experience**: Identical features and interface across both modes

### ⚡ **Advanced Model Management**
- **Smart Shortcuts**: Create and manage model shortcuts with rich metadata and previews
- **Batch Operations**: Download multiple models simultaneously with progress tracking
- **Version Monitoring**: Automatically detect and update to latest model versions
- **Intelligent Caching**: Optimized storage with thumbnail generation and metadata caching

### 🎨 **Professional Gallery System**
- **Rich Previews**: High-quality thumbnails with comprehensive model information
- **Advanced Filtering**: Search by tags, categories, NSFW status, and download state
- **Interactive Interface**: Drag-and-drop URL support for instant model registration
- **Gallery Integration**: Browse user galleries with one-click parameter extraction

### 📝 **Powerful Recipe System**
- **Prompt Templates**: Save and reuse your best prompt combinations
- **Parameter Extraction**: Automatically extract generation parameters from images
- **Recipe Gallery**: Visual recipe browser with instant preview and application
- **Smart Organization**: Categorize and manage recipes with custom classifications

## 🎬 Quick Start

### 🔧 Installation Options

#### Option 1: WebUI Extension (Recommended for WebUI users)
1. Open your AUTOMATIC1111 or Forge WebUI
2. Navigate to **Extensions** → **Install from URL**
3. Paste this URL: `https://github.com/jim60105/standalone-civitai-shortcut.git`
4. Click **Install** and restart your WebUI
5. Find the **Civitai Shortcut** tab in your interface

#### Option 2: Standalone Application
- **Linux/macOS:**
    ```bash
    # Clone the repository
git clone https://github.com/jim60105/standalone-civitai-shortcut.git
cd standalone-civitai-shortcut

# Start the application (auto-handles dependencies)
./start.sh
    ```
- **Windows:**
    ```bat
    REM Clone the repository
git clone https://github.com/jim60105/standalone-civitai-shortcut.git
cd standalone-civitai-shortcut

REM Start the application (auto-handles dependencies)
start.bat
    ```

#### Option 3: Docker
```bash
docker run -p 7860:7860 -v $(pwd)/data_sc:/app/data_sc ghcr.io/jim60105/standalone-civitai-shortcut:latest
```

### ⚡ First Steps
1. **Set your Civitai API key** (optional but recommended for full functionality)
2. **Import your first model** by dragging a Civitai URL to the upload area
3. **Browse your collection** in the Model Browser tab
4. **Create recipe templates** in the Prompt Recipe tab

---

## 📖 Features Overview

### 🏠 Model Browser
> *Discover, manage, and download AI models with ease*

- **Model Discovery**: Browse models with rich thumbnails and detailed information
- **Smart Downloads**: Queue multiple downloads with progress tracking
- **Version Management**: Automatically detect and update to latest versions
- **Metadata Viewing**: Comprehensive model information including tags, descriptions, and usage statistics
- **Send to Generation**: Direct integration with txt2img/img2img for seamless workflow

![Model Browser Demo](https://github.com/user-attachments/assets/0336259d-c5ab-4c0f-9122-2ba95736bc2c)

### 📝 Prompt Recipe System
> *Save, organize, and reuse your best prompt combinations*

- **Template Creation**: Save frequently used prompts as reusable templates
- **Parameter Extraction**: Automatically extract generation parameters from images
- **Visual Gallery**: Browse recipes with preview images and instant application
- **Smart Organization**: Categorize recipes with custom tags and classifications

![Recipe System](https://github.com/user-attachments/assets/6ea57fea-97be-48c7-8889-21d45f2ce283)

### 🔧 Advanced Tools
> *Powerful utilities for model management and organization*

#### Classification Management
- Organize models into custom categories
- Bulk operations for efficient management
- Hierarchical organization support

![Classification](https://github.com/user-attachments/assets/d3afb1d2-f186-4da1-846b-e7e4cc428776)

#### Scan & Update Tools
- **Model Scanner**: Automatically register existing models
- **Version Checker**: Bulk check for model updates
- **Metadata Sync**: Update model information with latest data
- **Orphan Detection**: Find and handle missing or moved models

![Scan Tools](https://github.com/user-attachments/assets/679f3050-fe3c-4b24-b8b1-45e6e0111e0e)

### ⚙️ Configuration
> *Customize your experience with comprehensive settings*

- **Gallery Layout**: Configure thumbnail sizes and column counts
- **Download Behavior**: Set default paths and concurrent download limits
- **API Configuration**: Manage Civitai API settings and rate limits
- **UI Preferences**: Customize interface appearance and behavior

![Settings](https://github.com/user-attachments/assets/1dd87b80-1593-40da-848c-c1ff0cb5e0c6)

---

## 💡 Usage Guide

### 🎯 Adding Models

#### Method 1: Drag & Drop URLs
Simply drag a Civitai model URL from your browser directly to the upload area:

![URL Drop Demo](https://github.com/user-attachments/assets/8affcc6e-3fd3-42c1-9449-4abbaa445b3c)

#### Method 2: Internet Shortcuts
Drag and drop saved `.url` shortcut files for batch import:

![Shortcut Drop Demo](https://github.com/user-attachments/assets/45471f2c-0352-4afd-bf81-c6dde13fcbe9)

#### Method 3: Bulk Import
Select multiple shortcuts and import them all at once for efficient collection building.

### 🔄 Model Management Workflow

1. **Import**: Add models via URL, shortcut files, or automatic scanning
2. **Organize**: Use classifications to categorize your models
3. **Update**: Regularly check for new versions and updates
4. **Generate**: Use models directly in your generation workflow
5. **Share**: Export recipes and share prompt templates

### 🎨 Recipe Workflow

1. **Create**: Generate an image with your preferred settings
2. **Extract**: Use "Send to Recipe" to capture parameters
3. **Save**: Store as a named template with preview image
4. **Reuse**: Apply saved recipes with one click
5. **Organize**: Categorize recipes for easy discovery

---

## 📁 Data Organization

The application creates a structured data directory (`data_sc/`) with the following organization:

```
data_sc/
├── 📄 CivitaiShortCutSetting.json          # Application configuration
├── 📄 CivitaiShortCut.json                 # Model shortcut registry
├── 📄 CivitaiShortCutClassification.json   # Category definitions
├── 📄 CivitaiShortCutRecipeCollection.json # Recipe templates
├── 📄 CivitaiShortCutBackupUrl.json        # URL backup during registration
├── 📁 sc_gallery/                          # Gallery image cache
├── 📁 sc_infos/                            # Model metadata and images
├── 📁 sc_recipes/                          # Recipe preview images
└── 📁 sc_thumb_images/                     # Generated thumbnails
```

---

## 🚀 Advanced Features

### 🔌 API Integration
- **Civitai API**: Full integration with official Civitai API
- **Rate Limiting**: Intelligent throttling to respect API limits
- **Authentication**: Secure API key management
- **Offline Mode**: Cached data available when API is unavailable

### ⚡ Performance Optimizations
- **Lazy Loading**: Components load only when needed
- **Smart Caching**: Efficient image and metadata caching
- **Parallel Downloads**: Concurrent operations for faster processing
- **Progress Tracking**: Real-time feedback for all operations

---

## 📜 License

<img src="https://github.com/user-attachments/assets/c297caf6-4dda-43fa-bbbb-ca7f6256d90e" alt="agplv3" width="300" />

[GNU AFFERO GENERAL PUBLIC LICENSE Version 3](/LICENSE)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

