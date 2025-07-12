# 🚀 Civitai Shortcut

**The ultimate dual-mode AI model management solution for Stable Diffusion**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
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

### 🛡️ **Enterprise-Grade Reliability**
- **Robust Error Handling**: Comprehensive error recovery with user-friendly feedback
- **Rate Limiting**: Built-in API throttling to respect Civitai's limits
- **Offline Capability**: Full functionality with cached data when offline
- **Progress Tracking**: Real-time progress indicators for all operations

### ⚙️ **Developer-Friendly Design**
- **Modern Architecture**: Clean, modular codebase following SOLID principles
- **Comprehensive Testing**: 900+ test cases ensuring reliability and quality
- **Rich API**: Well-documented interfaces for extension and customization
- **Docker Ready**: Containerized deployment for consistent environments

## 🎬 Quick Start

## 🎬 Quick Start

### 🔧 Installation Options

#### Option 1: WebUI Extension (Recommended for WebUI users)
1. Open your AUTOMATIC1111 or Forge WebUI
2. Navigate to **Extensions** → **Install from URL**
3. Paste this URL: `https://github.com/jim60105/standalone-civitai-shortcut.git`
4. Click **Install** and restart your WebUI
5. Find the **Civitai Shortcut** tab in your interface

#### Option 2: Standalone Application
```bash
# Clone the repository
git clone https://github.com/jim60105/standalone-civitai-shortcut.git
cd standalone-civitai-shortcut

# Install dependencies (Python 3.11+ required)
pip install -r requirements.txt

# Launch standalone mode
python main.py
```

#### Option 3: Docker (Coming Soon)
```bash
docker run -p 7860:7860 -v ./data:/app/data jim60105/civitai-shortcut
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

![Model Browser Demo](https://github.com/sunnyark/civitai-shortcut/assets/40237431/fdac59c0-0ced-41fb-8faa-83029b3ffc3f)

### 📝 Prompt Recipe System
> *Save, organize, and reuse your best prompt combinations*

- **Template Creation**: Save frequently used prompts as reusable templates
- **Parameter Extraction**: Automatically extract generation parameters from images
- **Visual Gallery**: Browse recipes with preview images and instant application
- **Smart Organization**: Categorize recipes with custom tags and classifications

![Recipe System](https://github.com/sunnyark/civitai-shortcut/assets/40237431/d3d61c0a-c749-40ee-bc8c-69c35e9c6ba7)

### 🔧 Advanced Tools
> *Powerful utilities for model management and organization*

#### Classification Management
- Organize models into custom categories
- Bulk operations for efficient management
- Hierarchical organization support

![Classification](https://github.com/sunnyark/civitai-shortcut/assets/40237431/9003d94d-5a13-4613-9fa6-722b1e892874)

#### Scan & Update Tools
- **Model Scanner**: Automatically register existing models
- **Version Checker**: Bulk check for model updates
- **Metadata Sync**: Update model information with latest data
- **Orphan Detection**: Find and handle missing or moved models

![Scan Tools](https://github.com/sunnyark/civitai-shortcut/assets/40237431/7f200d24-a4ca-4e23-834a-71470590ee49)

### ⚙️ Configuration
> *Customize your experience with comprehensive settings*

- **Gallery Layout**: Configure thumbnail sizes and column counts
- **Download Behavior**: Set default paths and concurrent download limits
- **API Configuration**: Manage Civitai API settings and rate limits
- **UI Preferences**: Customize interface appearance and behavior

![Settings](https://github.com/sunnyark/civitai-shortcut/assets/40237431/67e2e7c5-0cd6-4917-a4c8-b9ffb45832f9)

---

## 💡 Usage Guide

### 🎯 Adding Models

#### Method 1: Drag & Drop URLs
Simply drag a Civitai model URL from your browser directly to the upload area:

![URL Drop Demo](https://github.com/sunnyark/civitai-shortcut/assets/40237431/c6db4ced-9cec-4488-ac3f-9a17fadb42b8)

#### Method 2: Internet Shortcuts
Drag and drop saved `.url` shortcut files for batch import:

![Shortcut Drop Demo](https://github.com/sunnyark/civitai-shortcut/assets/40237431/a18cc188-0d7a-4860-91fa-b9b2b27f4bdc)

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

### 🔒 Data Privacy & Security
- All data is stored locally on your machine
- No telemetry or analytics collection
- API keys are stored securely with proper encryption
- Full control over your model collection and recipes

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

### 🔧 Developer Features
- **Plugin Architecture**: Extensible design for custom additions
- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Error Recovery**: Automatic retry and fallback mechanisms
- **Testing Suite**: 900+ tests ensuring reliability

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### 🐛 Bug Reports
- Use the [Issue Tracker](https://github.com/jim60105/standalone-civitai-shortcut/issues)
- Include detailed reproduction steps
- Attach relevant log files from `logs/civitai_shortcut.log`

### 💡 Feature Requests
- Check existing issues before creating new ones
- Provide clear use cases and benefits
- Consider contributing the implementation

### 🔧 Development
```bash
# Set up development environment
git clone https://github.com/jim60105/standalone-civitai-shortcut.git
cd standalone-civitai-shortcut
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest --cov=scripts.civitai_manager_libs --cov-report=html

# Code formatting
black --line-length=100 --skip-string-normalization .
flake8 .
```

---

## 📋 Requirements

### System Requirements
- **Python**: 3.11 or higher
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 1GB free space for application and cache
- **Network**: Internet connection for API access and downloads

### WebUI Compatibility
- **AUTOMATIC1111**: Latest version recommended
- **Forge**: Full compatibility
- **Other WebUIs**: Standalone mode available

### Dependencies
All dependencies are automatically managed. Key packages include:
- `gradio` - Modern web interface
- `requests` - HTTP client for API communication
- `Pillow` - Image processing and thumbnails
- `rich` - Enhanced console output

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Civitai Team** - For providing the excellent model platform and API
- **AUTOMATIC1111** - For the foundational WebUI framework
- **Community Contributors** - For feedback, testing, and improvements
- **Open Source Libraries** - For the robust foundation this project builds upon

---

## 📞 Support

- **Documentation**: [Full documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/jim60105/standalone-civitai-shortcut/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jim60105/standalone-civitai-shortcut/discussions)

---

<div align="center">

**⭐ If you find this project useful, please consider giving it a star! ⭐**

Made with ❤️ for the Stable Diffusion community

</div>
