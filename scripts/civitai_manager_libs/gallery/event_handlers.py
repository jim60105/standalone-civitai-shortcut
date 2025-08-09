"""
Event Handlers Module

Handles all event processing, user interactions, and UI state management.
Extracted from civitai_gallery_action.py to follow SRP principles.
"""

import os
import tempfile
from typing import Optional, Tuple
from PIL import Image

import gradio as gr

from ..error_handler import with_error_handling
from ..exceptions import NetworkError, FileOperationError, ValidationError
from ..logging_config import get_logger
from ..conditional_imports import import_manager
from ..compat.compat_layer import CompatibilityLayer
from .. import settings
from .. import util

logger = get_logger(__name__)


class GalleryEventHandlers:
    """Gallery event handlers following error handling best practices."""

    def __init__(self, data_processor, download_manager, utilities):
        self.data_processor = data_processor
        self.download_manager = download_manager
        self.utilities = utilities

    def handle_recipe_integration(
        self, model_id: str, img_file_info: str, img_index: int, civitai_images: list
    ) -> str:
        """Handle send to recipe functionality."""
        logger.debug("handle_recipe_integration called")
        logger.debug(f"  model_id: {repr(model_id)}")
        logger.debug(f"  img_file_info: {repr(img_file_info)}")
        logger.debug(f"  img_index: {repr(img_index)}")
        logger.debug(f"  civitai_images: {repr(civitai_images)}")

        try:
            # recipe_input format: [shortcut_id:filename] to include reference shortcut id
            recipe_image = settings.set_imagefn_and_shortcutid_for_recipe_image(
                model_id, civitai_images[int(img_index)]
            )
            logger.debug(f"  recipe_image: {repr(recipe_image)}")

            # Pass parsed generation parameters directly when available
            if img_file_info:
                result = f"{recipe_image}\n{img_file_info}"
                logger.debug(f"Returning combined data: {repr(result)}")
                return result
            else:
                logger.debug(f"No img_file_info, returning recipe_image only: {repr(recipe_image)}")
                return recipe_image
        except Exception as e:
            logger.error(f"Exception in handle_recipe_integration: {e}")
            return gr.update(visible=False)

    def handle_open_image_folder(self, modelid: str) -> None:
        """Handle open image folder action."""
        if modelid:
            from ..ishortcut_core.model_processor import ModelProcessor

            modelprocessor = ModelProcessor()
            model_info = modelprocessor.get_model_info(modelid)
            if model_info:
                model_name = model_info['name']
                image_folder = util.get_download_image_folder(model_name)
                if image_folder:
                    util.open_folder(image_folder)

    @with_error_handling(
        fallback_value=gr.update(visible=False),
        exception_types=(NetworkError, FileOperationError),
        retry_count=2,
        retry_delay=3.0,
        user_message="Failed to download images",
    )
    def handle_download_click(self, page_url: str, images_url: list) -> gr.update:
        """Handle download button click."""
        is_image_folder = False
        if page_url:
            modelid, versionid = self.utilities.extract_model_info(page_url)
            image_folder = self.download_manager.download_user_gallery(modelid, images_url)
            if image_folder:
                is_image_folder = True
        # Add container environment detection for folder button visibility
        container_visibility = util.should_show_open_folder_buttons()
        final_visibility = is_image_folder and container_visibility
        # For empty page_url, tests expect explicit update dict
        if not page_url:
            return {"__type__": "update", "visible": False}
        # Otherwise return native gr.update
        return gr.update(visible=bool(final_visibility))

    def handle_page_slider_release(
        self, usergal_page_url: str, page_slider: int, paging_information: dict
    ) -> str:
        """Handle page slider release action."""
        page_url = usergal_page_url

        if paging_information:
            if paging_information["totalPageUrls"]:
                total_page_urls = paging_information["totalPageUrls"]
                page_url = total_page_urls[page_slider - 1]

        return page_url

    def handle_first_btn_click(self, usergal_page_url: str, paging_information: dict) -> str:
        """Handle first page button click."""
        page_url = usergal_page_url

        if paging_information:
            if paging_information["totalPageUrls"]:
                total_page_urls = paging_information["totalPageUrls"]
                page_url = total_page_urls[0]

        return page_url

    def handle_end_btn_click(self, usergal_page_url: str, paging_information: dict) -> str:
        """Handle end page button click."""
        page_url = usergal_page_url

        if paging_information:
            if paging_information["totalPageUrls"]:
                total_page_urls = paging_information["totalPageUrls"]
                page_url = total_page_urls[-1]

        return page_url

    @with_error_handling(
        fallback_value=gr.update(visible=False),
        exception_types=(NetworkError, ValidationError),
        user_message="Failed to navigate pages",
    )
    def handle_next_btn_click(self, usergal_page_url: str, paging_information: dict) -> str:
        """Handle next page button click."""
        page_url = usergal_page_url

        current_page = self.data_processor.calculate_current_page(
            paging_information, usergal_page_url
        )
        if paging_information:
            if paging_information["totalPageUrls"]:
                total_page_urls = paging_information["totalPageUrls"]
                if len(total_page_urls) > current_page:
                    page_url = total_page_urls[current_page]

        return page_url

    @with_error_handling(
        fallback_value=gr.update(visible=False),
        exception_types=(NetworkError, ValidationError),
        user_message="Failed to navigate pages",
    )
    def handle_prev_btn_click(self, usergal_page_url: str, paging_information: dict) -> str:
        """Handle previous page button click."""
        page_url = usergal_page_url

        current_page = self.data_processor.calculate_current_page(
            paging_information, usergal_page_url
        )
        if paging_information:
            if paging_information["totalPageUrls"]:
                total_page_urls = paging_information["totalPageUrls"]
                if current_page > 1:
                    page_url = total_page_urls[current_page - 2]

        return page_url

    @with_error_handling(
        fallback_value=(
            None,
            gr.update(visible=False),
            gr.update(selected=""),
            gr.update(visible=False),
        ),
        exception_types=(ValidationError, NetworkError),
        user_message="Failed to process gallery selection",
    )
    def handle_gallery_select(
        self, evt: gr.SelectData, civitai_images: list
    ) -> Tuple[int, str, gr.update, str]:
        """Extract generation parameters from PNG info first, then Civitai API metadata."""
        logger.debug(
            f"[GALLERY_EVENT] handle_gallery_select called with evt.index={evt.index}, "
            f"civitai_images type={type(civitai_images)}, "
            f"civitai_images length={len(civitai_images) if civitai_images else 'None'}"
        )

        if civitai_images is None:
            logger.error(
                "[GALLERY_EVENT] civitai_images is None! Cannot proceed with gallery selection."
            )
            return 0, "", gr.update(), "Error: No images data available"

        if evt.index >= len(civitai_images):
            logger.error(
                f"[GALLERY_EVENT] evt.index {evt.index} is out of range for civitai_images "
                f"with length {len(civitai_images)}"
            )
            return 0, "", gr.update(), "Error: Invalid image selection"

        selected = civitai_images[evt.index]
        logger.debug(f"[GALLERY_EVENT] handle_gallery_select: selected={selected}")

        # Get local file path if URL
        local_path = selected
        if isinstance(selected, str) and selected.startswith("http"):
            local_path = settings.get_image_url_to_gallery_file(selected)
            logger.debug(f"handle_gallery_select: converted URL to local_path={local_path}")

        # Extract generation parameters - try PNG info first, then Civitai metadata
        png_info = ""
        try:
            if isinstance(local_path, str) and os.path.exists(local_path):
                # First try to extract PNG info from the image file itself
                logger.debug(f"Trying to extract PNG info from: {local_path}")

                try:
                    with Image.open(local_path) as img:
                        if hasattr(img, 'text') and img.text:
                            logger.debug(f"Found PNG text info: {list(img.text.keys())}")
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
                                        f"Extracted PNG info from key '{key}': "
                                        f"{len(png_info)} chars"
                                    )
                                    break
                        else:
                            logger.debug("No PNG text info found in image")
                except Exception as e:
                    logger.debug(f"Error reading PNG info: {e}")

                # If no PNG info found, try Civitai API metadata
                if not png_info:
                    logger.debug("No PNG info found, trying Civitai API metadata")
                    png_info = self._extract_civitai_metadata(local_path)
                else:
                    logger.debug(f"Using PNG info from file: {len(png_info)} chars")
            else:
                logger.debug(f"local_path is not string or doesn't exist: {local_path}")
        except Exception as e:
            png_info = f"Error extracting generation parameters: {e}"
            logger.debug(f"Error: {e}")

        logger.debug(f"Final png_info length: {len(png_info)} chars")
        return evt.index, local_path, gr.update(selected="Image_Information"), png_info

    def _extract_civitai_metadata(self, local_path: str) -> str:
        """Extract metadata from Civitai API data."""
        # Debug: Show available metadata keys
        all_metadata = self.data_processor.get_all_stored_metadata()
        logger.debug(f"Current metadata keys: {list(all_metadata.keys())}")

        # Extract UUID from filename
        import re

        filename = os.path.basename(local_path)
        logger.debug(f"Processing filename: {filename}")
        uuid_match = re.search(
            r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', filename
        )
        if uuid_match:
            image_uuid = uuid_match.group(1)
            logger.debug(f"Extracted UUID: {image_uuid}")

            # Get metadata from global variable
            image_meta = self.data_processor.get_stored_metadata(image_uuid)
            if image_meta:
                logger.debug(f"Found metadata for UUID: {image_uuid}")
                logger.debug(f"Metadata keys: {list(image_meta.keys())}")

                if 'meta' in image_meta and image_meta['meta']:
                    meta = image_meta['meta']
                    logger.debug(f"Meta fields: {list(meta.keys())}")
                    # Format generation parameters using Auto1111 format
                    png_info = self.data_processor.format_metadata_to_auto1111(meta)
                    logger.debug(f"Extracted Civitai metadata: {len(png_info)} chars")
                    return png_info
                else:
                    logger.debug("No meta field in image data")
                    return "No generation parameters available for this image."
            else:
                logger.debug(f"UUID {image_uuid} not in metadata")
                return "Image metadata not found in current page data."
        else:
            logger.debug(f"No UUID in filename: {filename}")
            return "Could not extract image ID from filename."

    def handle_selected_model_id_change(
        self, modelid: str
    ) -> Tuple[gr.update, Optional[str], gr.update, gr.update, Optional[dict], gr.update]:
        """Handle model selection change."""
        page_url = None
        versions_list = None
        title_name = None
        version_name = None
        paging_information = None
        is_image_folder = False

        if modelid:
            page_url = self.utilities.build_default_page_url(modelid, None, False)
            model_name, versions_list, version_name, paging_information = (
                self.data_processor.get_model_information(page_url)
            )

            title_name = f"# {model_name}"
            if paging_information:
                total_page = paging_information["totalPages"]
            else:
                total_page = 0

            image_folder = util.get_download_image_folder(model_name)
            if image_folder:
                is_image_folder = True

        return (
            gr.update(label=title_name),
            page_url,
            gr.update(
                choices=[settings.PLACEHOLDER] + versions_list if versions_list else None,
                value=version_name if version_name else settings.PLACEHOLDER,
            ),
            gr.update(
                minimum=1, maximum=total_page, value=1, step=1, label=f"Total {total_page} Pages"
            ),
            paging_information,
            gr.update(visible=is_image_folder),
        )

    def handle_versions_list_select(
        self, evt: gr.SelectData, modelid: Optional[str] = None
    ) -> Tuple[gr.update, Optional[str], gr.update, gr.update, Optional[dict]]:
        """Handle version selection."""
        page_url = None
        versions_list = None
        title_name = None
        version_name = None
        paging_information = None
        total_page = 0

        if modelid:
            if evt.index > 0:
                ver_index = evt.index - 1
                from ..ishortcut_core.model_processor import ModelProcessor

                modelprocessor = ModelProcessor()
                model_info = modelprocessor.get_model_info(modelid)
                version_info = dict()
                if model_info:
                    if "modelVersions" in model_info.keys():
                        if len(model_info["modelVersions"]) > 0:
                            version_info = model_info["modelVersions"][ver_index]
                            if version_info["id"]:
                                versionid = version_info["id"]
                                page_url = self.utilities.build_default_page_url(
                                    modelid, versionid, False
                                )
            else:
                page_url = self.utilities.build_default_page_url(modelid, None, False)

            model_name, versions_list, version_name, paging_information = (
                self.data_processor.get_model_information(page_url)
            )
            title_name = f"# {model_name}"
            if paging_information:
                total_page = paging_information["totalPages"]
            else:
                total_page = 0

        return (
            gr.update(label=title_name),
            page_url,
            gr.update(
                choices=[settings.PLACEHOLDER] + versions_list if versions_list else None,
                value=version_name if version_name else settings.PLACEHOLDER,
            ),
            gr.update(
                minimum=1, maximum=total_page, value=1, step=1, label=f"Total {total_page} Pages"
            ),
            paging_information,
        )

    def handle_usergal_page_url_change(
        self, usergal_page_url: str, paging_information: dict
    ) -> Tuple:
        """Handle page URL change."""
        return self.data_processor.load_page_data(usergal_page_url, paging_information)

    def handle_refresh_gallery_change(self, images_url: list, progress=None) -> Tuple:
        """Handle refresh gallery action."""
        if progress is None:
            progress = gr.Progress()
        return self.download_manager.load_gallery_images(images_url, progress)

    def handle_pre_loading_change(self, usergal_page_url: str, paging_information: dict) -> None:
        """Handle pre-loading action."""
        return self.download_manager.preload_next_page(usergal_page_url, paging_information)

    def handle_civitai_hidden_change(self, hidden, index: int) -> str:
        """Process PNG info with compatibility layer support."""
        compat = CompatibilityLayer.get_compatibility_layer()

        temp_path = None
        try:
            # Standalone mode: ensure we pass a file path, not an Image object
            if compat and compat.is_standalone_mode():
                if isinstance(hidden, Image.Image):
                    fd, temp_path = tempfile.mkstemp(suffix=".png", prefix="civitai_hidden_")
                    os.close(fd)
                    hidden.save(temp_path, format="PNG")
                    logger.debug(f"Saved PIL Image to temp file: {temp_path}")
                    result = compat.metadata_processor.extract_png_info(temp_path)
                    if result and result[0]:
                        return result[0]
                elif isinstance(hidden, str) and os.path.isfile(hidden):
                    result = compat.metadata_processor.extract_png_info(hidden)
                    if result and result[0]:
                        return result[0]
                else:
                    logger.debug(
                        f"Invalid hidden input for standalone: "
                        f"{type(hidden)} - {hidden if isinstance(hidden, str) else 'PIL Image'}"
                    )
            # WebUI mode: pass through
            elif compat and hasattr(compat, 'metadata_processor'):
                result = compat.metadata_processor.extract_png_info(hidden)
                if result and result[0]:
                    return result[0]
        except Exception as e:
            logger.error(f"Error processing PNG info through compatibility layer: {e}")
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
                logger.debug(f"Cleaned up temp file: {temp_path}")

        # Fallback: Try WebUI direct access
        extras_module = import_manager.get_webui_module('extras')
        if extras_module and hasattr(extras_module, 'run_pnginfo'):
            try:
                info1, info2, info3 = extras_module.run_pnginfo(hidden)
                return info1  # Return the parameters string, not the dictionary
            except Exception as e:
                logger.error(f"Error processing PNG info through WebUI: {e}")

        # Final fallback: Try basic PIL extraction
        try:
            import io

            if isinstance(hidden, str):
                with Image.open(hidden) as img:
                    return img.text.get('parameters', '')
            elif hasattr(hidden, 'read'):
                with Image.open(io.BytesIO(hidden.read())) as img:
                    return img.text.get('parameters', '')
        except Exception as e:
            logger.error(f"Error in PNG info fallback processing: {e}")

        return ""
