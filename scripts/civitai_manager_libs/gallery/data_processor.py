"""
Data Processor Module

Handles data processing, API calls, pagination management, and metadata formatting.
Extracted from civitai_gallery_action.py to follow SRP principles.
"""

import datetime
import os
from typing import Optional, Tuple, Dict, List

import gradio as gr

from ..error_handler import with_error_handling
from ..exceptions import NetworkError, APIError, ValidationError
from ..logging_config import get_logger
from .. import civitai
from .. import settings
from .. import util
from .gallery_utilities import GalleryUtilities

logger = get_logger(__name__)

# Global variable to store current page's Civitai image metadata
_current_page_metadata = {}


class GalleryDataProcessor:
    """Gallery data processing and API management."""

    def __init__(self):
        self.current_page_metadata = {}
        from ..ishortcut_core.model_processor import ModelProcessor

        self.model_processor = ModelProcessor()

    @with_error_handling(
        fallback_value=(None, None, None, None),
        exception_types=(NetworkError, APIError),
        retry_count=2,
        user_message="Failed to fetch model information",
    )
    def get_model_information(
        self, page_url: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[List[str]], Optional[str], Optional[Dict]]:
        """Get model information from page URL."""
        model_info = None
        version_name = None
        modelid = None
        versionid = None

        if page_url:
            utilities = GalleryUtilities()
            modelid, versionid = utilities.extract_model_info(page_url)

        if modelid:
            model_info = self.model_processor.get_model_info(modelid)

        if model_info:
            model_name = model_info['name']

            versions_list = list()
            if 'modelVersions' in model_info:
                for ver in model_info['modelVersions']:
                    versions_list.append(ver['name'])
                    if versionid:
                        if versionid == str(ver['id']):
                            version_name = ver['name']

            paging_information = self.get_pagination_info(modelid, versionid, False)
            return model_name, versions_list, version_name, paging_information
        return None, None, None, None

    @with_error_handling(
        fallback_value=(None, None),
        exception_types=(NetworkError, ValidationError),
        retry_count=1,
        user_message="Failed to load gallery data",
    )
    def get_gallery_data(
        self, page_url: Optional[str] = None, show_nsfw: bool = False
    ) -> Tuple[Optional[List[str]], Optional[List[str]]]:
        """Get gallery data for model."""
        modelid = None
        if page_url:
            utilities = GalleryUtilities()
            modelid, versionid = utilities.extract_model_info(page_url)

        if modelid:
            images_url, images_list = self.get_user_gallery(modelid, page_url, show_nsfw)
            return images_url, images_list
        return None, None

    def get_user_gallery(
        self, modelid: str, page_url: str, show_nsfw: bool
    ) -> Tuple[Optional[List[str]], Optional[Dict]]:
        """Process user gallery data with metadata storage."""
        if not modelid:
            return None, None

        image_data = self.get_image_page_data(modelid, page_url, show_nsfw)

        images_list = {}
        images_url = []

        if image_data:
            for image_info in image_data:
                if "url" in image_info:
                    img_url = image_info['url']
                    gallery_img_file = settings.get_image_url_to_gallery_file(img_url)

                    # NSFW filtering
                    if settings.nsfw_filter_enable:
                        if settings.NSFW_LEVELS.index(
                            image_info["nsfwLevel"]
                        ) > settings.NSFW_LEVELS.index(settings.nsfw_level):
                            gallery_img_file = settings.get_nsfw_disable_image()

                    if os.path.isfile(gallery_img_file):
                        img_url = gallery_img_file

                    images_url.append(img_url)

            images_list = {image_info['id']: image_info for image_info in image_data}

            # Store metadata globally for later retrieval by filename
            self.store_page_metadata(image_data)

        return images_url, images_list

    def get_image_page_data(
        self, modelid: str, page_url: str, show_nsfw: bool = False
    ) -> Optional[List[Dict]]:
        """Fetch image page data from API."""
        json_data = {}
        utilities = GalleryUtilities()

        if not page_url:
            page_url = utilities.build_default_page_url(modelid, None, show_nsfw)

        json_data = civitai.request_models(utilities.fix_page_url_cursor(page_url))

        try:
            return json_data['items']
        except (TypeError, KeyError):
            return None

    def get_pagination_info(
        self, model_id: str, model_version_id: Optional[str] = None, show_nsfw: bool = False
    ) -> Dict:
        """Get comprehensive pagination information."""
        total_pages = 0
        utilities = GalleryUtilities()

        # Get up to 200 items at once (maximum allowed)
        page_url = utilities.build_default_page_url(model_id, model_version_id, show_nsfw, 200)

        item_list = list()
        total_page_urls = list()

        while page_url is not None:
            json_data = civitai.request_models(utilities.fix_page_url_cursor(page_url))
            try:
                item_list.extend(json_data['items'])
            except KeyError:
                pass

            try:
                page_url = json_data['metadata']['nextPage']
            except KeyError:
                page_url = None

        images_per_page = (
            settings.usergallery_images_column * settings.usergallery_images_rows_per_page
        )

        initial_url = utilities.build_default_page_url(model_id, model_version_id, show_nsfw)
        total_page_urls.append(initial_url)
        page_items = item_list[::images_per_page]
        total_pages = len(page_items)

        for index, item in enumerate(page_items):
            if index > 0:
                total_page_urls.append(util.update_url(initial_url, "cursor", item["id"]))

        paging_information = dict()
        paging_information["totalPages"] = total_pages
        paging_information["totalPageUrls"] = total_page_urls

        return paging_information

    def calculate_current_page(self, paging_information: Dict, page_url: str) -> int:
        """Calculate current page from pagination info and URL."""
        utilities = GalleryUtilities()
        current_cursor = utilities.extract_url_cursor(page_url)

        if paging_information:
            total_page_urls = paging_information["totalPageUrls"]
            for cur_page, p_url in enumerate(total_page_urls, start=1):
                p_cursor = utilities.extract_url_cursor(p_url)

                if not p_cursor:
                    continue

                if str(current_cursor) == str(p_cursor):
                    return cur_page
        return 1

    def load_page_data(
        self, usergal_page_url: str, paging_information: Dict
    ) -> Tuple[Optional[str], Optional[List[str]], gr.update, gr.update]:
        """Load data for specific page."""
        if usergal_page_url:
            images_url, images_list = self.get_gallery_data(usergal_page_url, False)
            current_page = self.calculate_current_page(paging_information, usergal_page_url)
            current_time = datetime.datetime.now()
            return current_time, images_url, gr.update(value=current_page), gr.update(value=None)

        return None, None, gr.update(minimum=1, maximum=1, value=1), None

    def format_metadata_to_auto1111(self, meta: Dict) -> str:
        """Format Civitai metadata to Auto1111 generation parameters format."""
        if not meta:
            return ""

        # Auto1111 format: prompt on first line, negative prompt on second line,
        # then all other parameters on third line separated by commas
        lines = []

        # First line: prompt (no prefix)
        if 'prompt' in meta and meta['prompt']:
            lines.append(meta['prompt'])

        # Second line: negative prompt (with prefix)
        if 'negativePrompt' in meta and meta['negativePrompt']:
            lines.append(f"Negative prompt: {meta['negativePrompt']}")

        # Third line: all other parameters separated by commas
        params = []

        # Order parameters according to Auto1111 format
        if 'steps' in meta:
            params.append(f"Steps: {meta['steps']}")
        if 'sampler' in meta:
            params.append(f"Sampler: {meta['sampler']}")
        if 'Schedule' in meta:
            params.append(f"Schedule type: {meta['Schedule']}")
        if 'cfgScale' in meta:
            params.append(f"CFG scale: {meta['cfgScale']}")
        if 'seed' in meta:
            params.append(f"Seed: {meta['seed']}")
        if 'Size' in meta:
            params.append(f"Size: {meta['Size']}")
        if 'Model hash' in meta:
            params.append(f"Model hash: {meta['Model hash']}")
        if 'Model' in meta:
            params.append(f"Model: {meta['Model']}")
        if 'Denoising strength' in meta:
            params.append(f"Denoising strength: {meta['Denoising strength']}")
        if 'Clip skip' in meta:
            params.append(f"Clip skip: {meta['Clip skip']}")

        # Add ADetailer parameters
        if 'ADetailer model' in meta:
            params.append(f"ADetailer model: {meta['ADetailer model']}")
        if 'ADetailer confidence' in meta:
            params.append(f"ADetailer confidence: {meta['ADetailer confidence']}")
        if 'ADetailer mask only top k largest' in meta:
            params.append(
                f"ADetailer mask only top k largest: {meta['ADetailer mask only top k largest']}"
            )
        if 'ADetailer dilate erode' in meta:
            params.append(f"ADetailer dilate erode: {meta['ADetailer dilate erode']}")
        if 'ADetailer mask blur' in meta:
            params.append(f"ADetailer mask blur: {meta['ADetailer mask blur']}")
        if 'ADetailer denoising strength' in meta:
            params.append(f"ADetailer denoising strength: {meta['ADetailer denoising strength']}")
        if 'ADetailer inpaint only masked' in meta:
            params.append(f"ADetailer inpaint only masked: {meta['ADetailer inpaint only masked']}")
        if 'ADetailer inpaint padding' in meta:
            params.append(f"ADetailer inpaint padding: {meta['ADetailer inpaint padding']}")
        if 'ADetailer version' in meta:
            params.append(f"ADetailer version: {meta['ADetailer version']}")

        # Add Hires parameters
        if 'Hires upscale' in meta:
            params.append(f"Hires upscale: {meta['Hires upscale']}")
        if 'Hires steps' in meta:
            params.append(f"Hires steps: {meta['Hires steps']}")
        if 'Hires upscaler' in meta:
            params.append(f"Hires upscaler: {meta['Hires upscaler']}")

        # Add Lora hashes
        if 'Lora hashes' in meta:
            params.append(f"Lora hashes: {meta['Lora hashes']}")

        # Add Version
        if 'Version' in meta:
            params.append(f"Version: {meta['Version']}")

        # Join parameters with commas and space
        if params:
            lines.append(', '.join(params))

        return '\n'.join(lines)

    def store_page_metadata(self, image_data: List[Dict]) -> None:
        """Store image metadata for current page."""
        global _current_page_metadata
        _current_page_metadata = {}

        if image_data:
            logger.debug(f"Storing metadata for {len(image_data)} images")
            for image_info in image_data:
                if "url" in image_info:
                    # Extract UUID from URL to create filename mapping
                    import re

                    url = image_info['url']
                    uuid_match = re.search(
                        r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', url
                    )
                    if uuid_match:
                        image_uuid = uuid_match.group(1)
                        _current_page_metadata[image_uuid] = image_info
                        logger.debug(f"Stored metadata for UUID: {image_uuid}")
                        # Debug: Check if meta field exists
                        if 'meta' in image_info:
                            logger.debug(f"UUID {image_uuid} has meta field")
                        else:
                            logger.debug(f"UUID {image_uuid} missing meta field")

            logger.debug(f"Total metadata stored: {len(_current_page_metadata)} items")

    def get_stored_metadata(self, image_uuid: str) -> Optional[Dict]:
        """Get stored metadata for image UUID."""
        global _current_page_metadata
        return _current_page_metadata.get(image_uuid)

    def get_all_stored_metadata(self) -> Dict:
        """Get all stored metadata."""
        global _current_page_metadata
        return _current_page_metadata.copy()
