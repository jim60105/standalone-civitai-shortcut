"""
Gallery Actions Module

This module contains gallery related UI event handlers
migrated from ishortcut_action.py according to the design plan.
"""

import os
import gradio as gr
import io
from typing import Optional

from ..error_handler import with_error_handling
from ..exceptions import NetworkError, FileOperationError, ValidationError
from ..conditional_imports import import_manager
from ..logging_config import get_logger
from ..compat.compat_layer import CompatibilityLayer

logger = get_logger(__name__)

from .. import util
from .. import model
from .. import civitai
from .. import ishortcut
from .. import setting


@with_error_handling(
    fallback_value=(0, None, gr.update(), ""),
    exception_types=(FileOperationError, ValidationError),
    user_message="Failed to process gallery selection",
)
def on_gallery_select(evt, civitai_images, model_id):
    """Extract generation parameters from PNG info first, then fallback methods."""
    selected = civitai_images[evt.index]
    logger.debug(f"[gallery_actions] on_gallery_select: selected={selected}")

    # Get local file path if URL
    local_path = selected
    if isinstance(selected, str) and selected.startswith("http"):
        local_path = setting.get_image_url_to_gallery_file(selected)
        logger.debug(
            f"[gallery_actions] on_gallery_select: converted URL to local_path={local_path}"
        )

    # Extract generation parameters - try PNG info first
    png_info = ""
    try:
        if isinstance(local_path, str) and os.path.exists(local_path):
            # First try to extract PNG info from the image file itself
            logger.debug(f"[gallery_actions] Trying to extract PNG info from: {local_path}")

            from PIL import Image

            try:
                with Image.open(local_path) as img:
                    if hasattr(img, 'text') and img.text:
                        logger.debug(
                            f"[gallery_actions] Found PNG text info: {list(img.text.keys())}"
                        )
                        # Check for common PNG info keys
                        for key in [
                            'parameters',
                            'Parameters',
                            'generation_info',
                            'Generation Info',
                        ]:
                            if key in img.text:
                                png_info = img.text[key]
                                logger.debug(
                                    f"[gallery_actions] Extracted PNG info from key "
                                    f"'{key}': {len(png_info)} chars"
                                )
                                break
                    else:
                        logger.debug("[gallery_actions] No PNG text info found in image")
            except Exception as e:
                logger.debug(f"[gallery_actions] Error reading PNG info: {e}")

            # If no PNG info found, try compatibility layer fallback
            if not png_info:
                logger.debug("[gallery_actions] No PNG info found, trying compatibility layer")
                try:
                    compat = CompatibilityLayer.get_compatibility_layer()
                    if compat and hasattr(compat, 'metadata_processor'):
                        result = compat.metadata_processor.extract_png_info(local_path)
                        if result and result[0]:
                            png_info = result[0]
                            logger.debug(
                                f"[gallery_actions] Extracted via compatibility layer: "
                                f"{len(png_info)} chars"
                            )
                except ImportError as e:
                    logger.debug(f"[gallery_actions] Compatibility layer import error: {e}")
                except Exception as e:
                    logger.debug(f"[gallery_actions] Error with compatibility layer: {e}")

            # Final fallback: WebUI direct access
            if not png_info:
                logger.debug("[gallery_actions] Trying WebUI direct access")
                try:
                    try:
                        extras_module = import_manager.get_webui_module('extras')
                    except ImportError as e:
                        logger.debug(f"[gallery_actions] WebUI import error: {e}")
                        extras_module = None
                    if extras_module and hasattr(extras_module, 'run_pnginfo'):
                        info1, info2, info3 = extras_module.run_pnginfo(local_path)
                        if info1:
                            png_info = info1
                            logger.debug(
                                f"[gallery_actions] Extracted via WebUI: {len(png_info)} chars"
                            )
                except Exception as e:
                    logger.debug(f"[gallery_actions] Error with WebUI: {e}")

            # Last resort: Try Civitai API if we have model ID
            if not png_info and model_id:
                logger.debug("[gallery_actions] Trying Civitai API as final fallback")
                try:
                    # Always add nsfw param for info query
                    api_url = (
                        f"https://civitai.com/api/v1/images?limit=20&modelId={model_id}&nsfw=X"
                    )
                    logger.debug(f"[gallery_actions] Querying Civitai API: {api_url}")

                    response = civitai.request_models(api_url)
                    if response and 'items' in response:
                        logger.debug(
                            f"[gallery_actions] Found {len(response['items'])} images from API"
                        )
                        # Try to match by filename similarity or just use first image with meta
                        for item in response['items']:
                            if 'meta' in item and item['meta']:
                                meta = item['meta']
                                # Format generation parameters
                                params = []
                                if 'prompt' in meta:
                                    params.append(f"Prompt: {meta['prompt']}")
                                if 'negativePrompt' in meta:
                                    params.append(f"Negative prompt: {meta['negativePrompt']}")
                                if 'sampler' in meta:
                                    params.append(f"Sampler: {meta['sampler']}")
                                if 'cfgScale' in meta:
                                    params.append(f"CFG scale: {meta['cfgScale']}")
                                if 'steps' in meta:
                                    params.append(f"Steps: {meta['steps']}")
                                if 'seed' in meta:
                                    params.append(f"Seed: {meta['seed']}")
                                if 'Model' in meta:
                                    params.append(f"Model: {meta['Model']}")
                                if 'Size' in meta:
                                    params.append(f"Size: {meta['Size']}")

                                if params:
                                    png_info = (
                                        f"Generated using example parameters from Civitai:\n\n"
                                        f"{chr(10).join(params)}"
                                    )
                                    logger.debug(
                                        f"[gallery_actions] Using Civitai API fallback: "
                                        f"{len(png_info)} chars"
                                    )
                                    break
                except Exception as e:
                    logger.debug(f"[gallery_actions] Error with Civitai API fallback: {e}")

            if not png_info:
                png_info = "No generation parameters found in this image."
                logger.debug("[gallery_actions] No generation parameters found")
            else:
                logger.debug(f"[gallery_actions] Using PNG info: {len(png_info)} chars")
        else:
            logger.debug(
                f"[gallery_actions] local_path is not string or doesn't exist: {local_path}"
            )
            png_info = "Image file not accessible."
    except Exception as e:
        png_info = f"Error extracting generation parameters: {e}"
        logger.debug(f"[gallery_actions] Error: {e}")

    logger.debug(f"[gallery_actions] Final png_info length: {len(png_info)} chars")
    return (
        evt.index, 
        local_path, 
        gr.update(selected="Image_Information"), 
        png_info
    )


@with_error_handling(
    fallback_value="",
    exception_types=(FileOperationError, ValidationError),
    user_message="Failed to process PNG info",
)
def on_civitai_hidden_change(hidden, index):
    """Process PNG info with compatibility layer support"""
    compat = CompatibilityLayer.get_compatibility_layer()

    if compat and hasattr(compat, 'metadata_processor'):
        try:
            # extract_png_info returns (geninfo, generation_params, info_text)
            # We need the first element (geninfo) which contains the parameters string
            result = compat.metadata_processor.extract_png_info(hidden)
            if result and result[0]:
                return result[0]
        except Exception as e:
            logger.debug(f"Error processing PNG info through compatibility layer: {e}")

    # Fallback: Try WebUI direct access
    extras_module = import_manager.get_webui_module('extras')
    if extras_module and hasattr(extras_module, 'run_pnginfo'):
        try:
            info1, info2, info3 = extras_module.run_pnginfo(hidden)
            return info1  # Return the parameters string, not the dictionary
        except Exception as e:
            logger.debug(f"Error processing PNG info through WebUI: {e}")

    # Final fallback: Try basic PIL extraction
    try:
        from PIL import Image

        if isinstance(hidden, str):
            with Image.open(hidden) as img:
                return img.text.get('parameters', '')
        elif hasattr(hidden, 'read'):
            with Image.open(io.BytesIO(hidden.read())) as img:
                return img.text.get('parameters', '')
    except Exception as e:
        logger.debug(f"Error in PNG info fallback processing: {e}")

    return ""
