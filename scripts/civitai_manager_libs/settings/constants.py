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
model_exts = (".bin", ".pt", ".safetensors", ".ckpt")
info_ext = ".info"
info_suffix = ".civitai"
triger_ext = ".txt"
triger_suffix = ".triger"
preview_image_ext = ".png"
preview_image_suffix = ".preview"

# NSFW levels
NSFW_levels = ("None", "Soft", "Mature", "X", "XX")

# Model base models mapping
model_basemodels = {
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
default_model_folders = {
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
ui_typenames = {
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
