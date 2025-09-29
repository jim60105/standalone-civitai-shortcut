"""Constants used throughout the application."""

import os

# Project-generated files root directory
SC_DATA_ROOT = "data_sc"
# Stable Diffusion files root directory
SD_DATA_ROOT = "data"

# UI constants
PLACEHOLDER = "[No Select]"
NORESULT = "[No Result]"
NEWRECIPE = "[New Prompt Recipe]"
NEWCLASSIFICATION = "[New Classification]"
CREATE_MODEL_FOLDER = "Create a model folder to download the model"

# File extensions
MODEL_EXTS = (".bin", ".pt", ".safetensors", ".ckpt")
INFO_EXT = ".info"
INFO_SUFFIX = ".civitai"
TRIGER_EXT = ".txt"
TRIGER_SUFFIX = ".triger"
PREVIEW_IMAGE_EXT = ".png"
PREVIEW_IMAGE_SUFFIX = ".preview"

# NSFW levels
NSFW_LEVELS = ("None", "Soft", "Mature", "X", "XX")

# Model base models mapping
MODEL_BASEMODELS = {
    "SD 1.4": "SD1",
    "SD 1.5": "SD1",
    "SD 2.0": "SD2",
    "SD 2.0 768": "SD2",
    "SD 2.1": "SD2",
    "SD 2.1 768": "SD2",
    "SD 2.1 Unclip": "SD2",
    "SDXL 0.9": "SDXL",
    "SDXL 1.0": "SDXL",
    "SDXL 1.0 LCM": "SDXL",
    "SDXL Distilled": "SDXL",
    "SDXL Turbo": "SDXL",
    "SDXL Lightning": "SDXL",
    "Pony": "Pony",
    "SVD": "SVD",
    "SVD XT": "SVD",
    "Stable Cascade": "SC",
    "Playground V2": "PGV2",
    "PixArt A": "PixArtA",
    "Other": "Unknown",
}

# Default model folders mapping
DEFAULT_MODEL_FOLDERS = {
    'Checkpoint': os.path.join("models", "Stable-diffusion"),
    'LORA': os.path.join("models", "Lora"),
    'LoCon': os.path.join("models", "LyCORIS"),
    'TextualInversion': os.path.join("embeddings"),
    'Hypernetwork': os.path.join("models", "hypernetworks"),
    'AestheticGradient': os.path.join(
        "extensions", "stable-diffusion-webui-aesthetic-gradients", "aesthetic_embeddings"
    ),
    'Controlnet': os.path.join("models", "ControlNet"),
    'Poses': os.path.join("models", "Poses"),
    'Wildcards': os.path.join("extensions", "sd-dynamic-prompts", "wildcards"),
    'Other': os.path.join("models", "Other"),
    'VAE': os.path.join("models", "VAE"),
    'ANLORA': os.path.join("extensions", "sd-webui-additional-networks", "models", "lora"),
    'Unknown': os.path.join("models", "Unknown"),
}

# UI type names mapping
UI_TYPENAMES = {
    "Checkpoint": 'Checkpoint',
    "LoRA": 'LORA',
    "LyCORIS": 'LoCon',
    "Textual Inversion": 'TextualInversion',
    "Hypernetwork": 'Hypernetwork',
    "Aesthetic Gradient": 'AestheticGradient',
    "Controlnet": 'Controlnet',
    "Poses": 'Poses',
    "Wildcards": 'Wildcards',
    "Other": 'Other',
}

# Default headers for HTTP requests
DEFAULT_HEADERS = {
    'user-agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 '
        'Safari/537.36 Edg/112.0.1722.68'
    ),
    "Authorization": "",
}

# Image format constants
STATIC_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.avif']
DYNAMIC_IMAGE_EXTENSIONS = ['.gif', '.webm', '.mp4', '.mov']

# Default tab indices
DEFAULT_CIVITAI_INFORMATION_TAB = 0
DEFAULT_USERGAL_INFORMATION_TAB = 1
DEFAULT_DOWNLOAD_INFORMATION_TAB = 2
