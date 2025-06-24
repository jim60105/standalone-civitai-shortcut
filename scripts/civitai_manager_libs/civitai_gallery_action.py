"""
Civitai Gallery Action Module - Dual Mode Compatible.

This module has been modified to support both AUTOMATIC1111 and standalone modes
through the compatibility layer.
"""

import os
import shutil
import requests
import gradio as gr
import datetime
import time
import re
import threading
from PIL import Image

from .conditional_imports import import_manager

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda iterable, **kwargs: iterable  # noqa: E731

from . import util
from . import civitai
from . import setting
from . import ishortcut
from .compat.compat_layer import CompatibilityLayer

# Compatibility layer variables
_compat_layer = None

# Global variable to store current page's Civitai image metadata
_current_page_metadata = {}

# HTTP client factory for gallery operations
from .http_client import get_http_client


def _download_single_image(img_url: str, save_path: str) -> bool:
    """Download a single image with proper error handling."""
    client = get_http_client()
    util.printD(f"[civitai_gallery_action] Downloading image from: {img_url}")
    util.printD(f"[civitai_gallery_action] Saving to: {save_path}")
    success = client.download_file(img_url, save_path)
    if success:
        util.printD(f"[civitai_gallery_action] Successfully downloaded image: {save_path}")
    else:
        util.printD(f"[civitai_gallery_action] Failed to download image: {img_url}")
    return success


class GalleryDownloadManager:
    """Manage gallery image downloads with retry capability."""

    def __init__(self):
        self.failed_downloads = []
        self.client = get_http_client()

    def download_with_retry(self, img_url: str, save_path: str, max_retries: int = 2) -> bool:
        """Download image with retry on failure."""
        for attempt in range(max_retries + 1):
            if self.client.download_file(img_url, save_path):
                return True
            if attempt < max_retries:
                util.printD(f"[civitai_gallery_action] Retry {attempt + 1} for: {img_url}")
                time.sleep(1)
        self.failed_downloads.append((img_url, save_path))
        return False

    def retry_failed_downloads(self):
        """Retry all previously failed downloads."""
        if not self.failed_downloads:
            return

        util.printD(
            f"[civitai_gallery_action] Retrying {len(self.failed_downloads)} failed downloads"
        )

        retry_list = self.failed_downloads.copy()
        self.failed_downloads.clear()

        for img_url, save_path in retry_list:
            self.download_with_retry(img_url, save_path, max_retries=1)


def download_images_with_progress(dn_image_list: list, progress_callback=None):
    """Download images with progress tracking."""
    if not dn_image_list:
        return

    total = len(dn_image_list)
    completed = 0
    client = get_http_client()

    for img_url in dn_image_list:
        gallery_img_file = setting.get_image_url_to_gallery_file(img_url)
        if not os.path.isfile(gallery_img_file):
            client.download_file(img_url, gallery_img_file)
        completed += 1
        if progress_callback:
            progress_callback(completed, total, f"Downloading image {completed}/{total}")


def download_images_batch(
    dn_image_list: list, batch_size: int = setting.gallery_download_batch_size
):
    """Download images in batches to avoid overwhelming the server."""
    if not dn_image_list:
        return

    client = get_http_client()

    for i in range(0, len(dn_image_list), batch_size):
        batch = dn_image_list[i : i + batch_size]
        util.printD(
            f"[civitai_gallery_action] Processing batch {i//batch_size + 1}, {len(batch)} images"
        )
        for img_url in batch:
            gallery_img_file = setting.get_image_url_to_gallery_file(img_url)
            if not os.path.isfile(gallery_img_file):
                client.download_file(img_url, gallery_img_file)
        time.sleep(0.5)


def set_compatibility_layer(compat_layer):
    """Set compatibility layer."""
    global _compat_layer
    _compat_layer = compat_layer


def on_ui(recipe_input):

    with gr.Column(scale=3):
        with gr.Accordion("#", open=True) as model_title_name:
            versions_list = gr.Dropdown(
                label="Model Version",
                choices=[setting.PLACEHOLDER],
                interactive=True,
                value=setting.PLACEHOLDER,
            )
        usergal_gallery = gr.Gallery(
            show_label=False,
            columns=setting.usergallery_images_column,
            height=setting.information_gallery_height,
            object_fit=setting.gallery_thumbnail_image_style,
        )
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Row():
                    first_btn = gr.Button(value="First Page")
                    prev_btn = gr.Button(value="Prev Page")
            with gr.Column(scale=1):
                page_slider = gr.Slider(
                    minimum=1, maximum=1, value=1, step=1, label='Total Pages', interactive=True
                )
            with gr.Column(scale=1):
                with gr.Row():
                    next_btn = gr.Button(value="Next Page")
                    end_btn = gr.Button(value="End Page")
        with gr.Row():
            download_images = gr.Button(value="Download Images")
            open_image_folder = gr.Button(value="Open Download Image Folder", visible=False)

    with gr.Column(scale=1):
        with gr.Tabs() as info_tabs:
            with gr.TabItem("Image Information", id="Image_Information"):
                with gr.Column():
                    img_file_info = gr.Textbox(
                        label="Generate Info",
                        interactive=True,
                        lines=6,
                        container=True,
                        show_copy_button=True,
                    )
                    try:
                        parameters_copypaste = import_manager.get_webui_module(
                            'extras', 'parameters_copypaste'
                        )
                        if parameters_copypaste:
                            send_to_buttons = parameters_copypaste.create_buttons(
                                ["txt2img", "img2img", "inpaint", "extras"]
                            )
                    except Exception:
                        pass
                    send_to_recipe = gr.Button(
                        value="Send To Recipe", variant="primary", visible=True
                    )

    with gr.Row(visible=False):
        selected_model_id = gr.Textbox()

        # user gallery information
        img_index = gr.Number(show_label=False)

        # 실재 로드된것
        usergal_images = gr.State()

        # 로드 해야 할것
        usergal_images_url = gr.State()

        # 트리거를 위한것
        hidden = gr.Image(type="pil")

        # 페이징 관련 정보
        paging_information = gr.State()

        usergal_page_url = gr.Textbox(value=None)

        refresh_information = gr.Textbox()

        refresh_gallery = gr.Textbox()

        # 미리 다음페이지를 로딩한다.
        pre_loading = gr.Textbox()

    try:
        parameters_copypaste = import_manager.get_webui_module('extras', 'parameters_copypaste')
        if parameters_copypaste and 'send_to_buttons' in locals():
            parameters_copypaste.bind_buttons(send_to_buttons, hidden, img_file_info)
    except Exception:
        pass

    usergal_gallery.select(
        on_gallery_select, usergal_images, [img_index, hidden, info_tabs, img_file_info]
    )
    # Note: hidden.change is commented out because we handle all PNG info extraction
    # in on_gallery_select
    # hidden.change(on_civitai_hidden_change, [hidden, img_index], [img_file_info])
    open_image_folder.click(on_open_image_folder_click, [selected_model_id], None)

    send_to_recipe.click(
        fn=on_send_to_recipe_click,
        inputs=[selected_model_id, img_file_info, img_index, usergal_images],
        outputs=[recipe_input],
    )

    download_images.click(
        fn=on_download_images_click,
        inputs=[usergal_page_url, usergal_images_url],
        outputs=[open_image_folder],
    )

    gallery = refresh_gallery.change(
        fn=on_refresh_gallery_change,
        inputs=[
            usergal_images_url,
        ],
        outputs=[usergal_gallery, usergal_images, pre_loading],
    )

    gallery_page = usergal_page_url.change(
        fn=on_usergal_page_url_change,
        inputs=[usergal_page_url, paging_information],
        outputs=[
            refresh_gallery,
            usergal_images_url,
            page_slider,
            img_file_info,
        ],
        cancels=gallery,
    )

    refresh_information.change(
        fn=on_usergal_page_url_change,
        inputs=[usergal_page_url, paging_information],
        outputs=[
            refresh_gallery,
            usergal_images_url,
            page_slider,
            img_file_info,
        ],
        cancels=gallery,
    )

    # civitai user gallery information start
    selected_model_id.change(
        fn=on_selected_model_id_change,
        inputs=[
            selected_model_id,
        ],
        outputs=[
            model_title_name,
            usergal_page_url,
            versions_list,
            page_slider,
            paging_information,
            open_image_folder,
        ],
        cancels=[gallery, gallery_page],
    )

    versions_list.select(
        fn=on_versions_list_select,
        inputs=[
            selected_model_id,
        ],
        outputs=[
            model_title_name,
            usergal_page_url,
            versions_list,
            page_slider,
            paging_information,
        ],
        cancels=[gallery, gallery_page],
    )

    pre_loading.change(
        fn=on_pre_loading_change, inputs=[usergal_page_url, paging_information], outputs=None
    )

    first_btn.click(
        fn=on_first_btn_click,
        inputs=[usergal_page_url, paging_information],
        outputs=[usergal_page_url],
    )

    end_btn.click(
        fn=on_end_btn_click,
        inputs=[usergal_page_url, paging_information],
        outputs=[usergal_page_url],
    )

    prev_btn.click(
        fn=on_prev_btn_click,
        inputs=[usergal_page_url, paging_information],
        outputs=[usergal_page_url],
    )

    next_btn.click(
        fn=on_next_btn_click,
        inputs=[usergal_page_url, paging_information],
        outputs=[usergal_page_url],
    )

    page_slider.release(
        fn=on_page_slider_release,
        inputs=[usergal_page_url, page_slider, paging_information],
        outputs=[usergal_page_url],
    )

    return selected_model_id, refresh_information


# def on_send_to_recipe_click(img_file_info, img_index, usergal_images):
#     try:
#         return usergal_images[int(img_index)]
#     except:
#         return gr.update(visible=False)


def on_send_to_recipe_click(model_id, img_file_info, img_index, civitai_images):
    util.printD("[CIVITAI_GALLERY] on_send_to_recipe_click called")
    util.printD(f"[CIVITAI_GALLERY]   model_id: {repr(model_id)}")
    util.printD(f"[CIVITAI_GALLERY]   img_file_info: {repr(img_file_info)}")
    util.printD(f"[CIVITAI_GALLERY]   img_index: {repr(img_index)}")
    util.printD(f"[CIVITAI_GALLERY]   civitai_images: {repr(civitai_images)}")

    try:
        # recipe_input의 넘어가는 데이터 형식을 [ shortcut_id:파일네임 ] 으로 하면
        # reference shortcut id를 넣어줄수 있다.
        recipe_image = setting.set_imagefn_and_shortcutid_for_recipe_image(
            model_id, civitai_images[int(img_index)]
        )
        util.printD(f"[CIVITAI_GALLERY]   recipe_image: {repr(recipe_image)}")

        # Pass parsed generation parameters directly when available
        if img_file_info:
            result = f"{recipe_image}\n{img_file_info}"
            util.printD(f"[CIVITAI_GALLERY] Returning combined data: {repr(result)}")
            return result
        else:
            util.printD(
                "[CIVITAI_GALLERY] No img_file_info, returning recipe_image only: "
                f"{repr(recipe_image)}"
            )
            return recipe_image
    except Exception as e:
        util.printD(f"[CIVITAI_GALLERY] Exception in on_send_to_recipe_click: {e}")
        return gr.update(visible=False)


def on_open_image_folder_click(modelid):
    if modelid:
        # model_info = civitai.get_model_info(modelid)
        model_info = ishortcut.get_model_info(modelid)
        if model_info:
            model_name = model_info['name']
            image_folder = util.get_download_image_folder(model_name)
            if image_folder:
                util.open_folder(image_folder)


def on_download_images_click(page_url, images_url):
    is_image_folder = False
    if page_url:
        modelid, versionid = extract_model_info(page_url)
        image_folder = download_user_gallery_images(modelid, images_url)
        if image_folder:
            is_image_folder = True
    return gr.update(visible=is_image_folder)


def on_page_slider_release(usergal_page_url, page_slider, paging_information):
    page_url = usergal_page_url

    if paging_information:
        if paging_information["totalPageUrls"]:
            totalPageUrls = paging_information["totalPageUrls"]
            page_url = totalPageUrls[page_slider - 1]

    return page_url


def on_first_btn_click(usergal_page_url, paging_information):
    page_url = usergal_page_url

    if paging_information:
        if paging_information["totalPageUrls"]:
            totalPageUrls = paging_information["totalPageUrls"]
            page_url = totalPageUrls[0]

    return page_url


def on_end_btn_click(usergal_page_url, paging_information):
    page_url = usergal_page_url

    if paging_information:
        if paging_information["totalPageUrls"]:
            totalPageUrls = paging_information["totalPageUrls"]
            page_url = totalPageUrls[-1]

    return page_url


def on_next_btn_click(usergal_page_url, paging_information):
    page_url = usergal_page_url

    current_Page = get_current_page(paging_information, usergal_page_url)
    if paging_information:
        if paging_information["totalPageUrls"]:
            totalPageUrls = paging_information["totalPageUrls"]
            if len(totalPageUrls) > current_Page:
                page_url = totalPageUrls[current_Page]

    return page_url


def on_prev_btn_click(usergal_page_url, paging_information):
    page_url = usergal_page_url

    current_Page = get_current_page(paging_information, usergal_page_url)
    if paging_information:
        if paging_information["totalPageUrls"]:
            totalPageUrls = paging_information["totalPageUrls"]
            if current_Page > 1:
                page_url = totalPageUrls[current_Page - 2]

    return page_url


def on_civitai_hidden_change(hidden, index):
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
                util.printD(f"[civitai_gallery_action] Saved PIL Image to temp file: {temp_path}")
                result = compat.metadata_processor.extract_png_info(temp_path)
                if result and result[0]:
                    return result[0]
            elif isinstance(hidden, str) and os.path.isfile(hidden):
                result = compat.metadata_processor.extract_png_info(hidden)
                if result and result[0]:
                    return result[0]
            else:
                util.printD(
                    f"[civitai_gallery_action] Invalid hidden input for standalone: "
                    f"{type(hidden)} - {hidden if isinstance(hidden, str) else 'PIL Image'}"
                )
        # WebUI mode: pass through
        elif compat and hasattr(compat, 'metadata_processor'):
            result = compat.metadata_processor.extract_png_info(hidden)
            if result and result[0]:
                return result[0]
    except Exception as e:
        util.printD(f"Error processing PNG info through compatibility layer: {e}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            util.printD(f"[civitai_gallery_action] Cleaned up temp file: {temp_path}")

    # Fallback: Try WebUI direct access
    extras_module = import_manager.get_webui_module('extras')
    if extras_module and hasattr(extras_module, 'run_pnginfo'):
        try:
            info1, info2, info3 = extras_module.run_pnginfo(hidden)
            return info1  # Return the parameters string, not the dictionary
        except Exception as e:
            util.printD(f"Error processing PNG info through WebUI: {e}")

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
        util.printD(f"Error in PNG info fallback processing: {e}")

    return ""


def on_gallery_select(evt: gr.SelectData, civitai_images):
    """Extract generation parameters from PNG info first, then Civitai API metadata."""
    selected = civitai_images[evt.index]
    util.printD(f"[civitai_gallery_action] on_gallery_select: selected={selected}")

    # Get local file path if URL
    local_path = selected
    if isinstance(selected, str) and selected.startswith("http"):
        from . import setting

        local_path = setting.get_image_url_to_gallery_file(selected)
        util.printD(
            f"[civitai_gallery_action] on_gallery_select: converted URL to local_path={local_path}"
        )

    # Extract generation parameters - try PNG info first, then Civitai metadata
    png_info = ""
    try:
        if isinstance(local_path, str) and os.path.exists(local_path):
            # First try to extract PNG info from the image file itself
            util.printD(f"[civitai_gallery_action] Trying to extract PNG info from: {local_path}")

            from PIL import Image

            try:
                with Image.open(local_path) as img:
                    if hasattr(img, 'text') and img.text:
                        util.printD(
                            f"[civitai_gallery_action] Found PNG text info: {list(img.text.keys())}"
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
                                util.printD(
                                    f"[civitai_gallery_action] Extracted PNG info from key "
                                    f"'{key}': {len(png_info)} chars"
                                )
                                break
                    else:
                        util.printD("[civitai_gallery_action] No PNG text info found in image")
            except Exception as e:
                util.printD(f"[civitai_gallery_action] Error reading PNG info: {e}")

            # If no PNG info found, try Civitai API metadata
            if not png_info:
                util.printD(
                    "[civitai_gallery_action] No PNG info found, trying Civitai API metadata"
                )
                # Debug: Show available metadata keys
                util.printD(
                    f"[civitai_gallery_action] Current metadata keys: "
                    f"{list(_current_page_metadata.keys())}"
                )

                # Extract UUID from filename
                import re

                filename = os.path.basename(local_path)
                util.printD(f"[civitai_gallery_action] Processing filename: {filename}")
                uuid_match = re.search(
                    r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', filename
                )
                if uuid_match:
                    image_uuid = uuid_match.group(1)
                    util.printD(f"[civitai_gallery_action] Extracted UUID: {image_uuid}")

                    # Get metadata from global variable
                    if image_uuid in _current_page_metadata:
                        image_meta = _current_page_metadata[image_uuid]
                        util.printD(
                            f"[civitai_gallery_action] Found metadata for UUID: {image_uuid}"
                        )
                        util.printD(
                            f"[civitai_gallery_action] Metadata keys: {list(image_meta.keys())}"
                        )

                        if 'meta' in image_meta and image_meta['meta']:
                            meta = image_meta['meta']
                            util.printD(
                                f"[civitai_gallery_action] Meta fields: {list(meta.keys())}"
                            )
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

                            png_info = '\n'.join(params)
                            util.printD(
                                f"[civitai_gallery_action] Extracted Civitai metadata: "
                                f"{len(png_info)} chars"
                            )
                        else:
                            png_info = "No generation parameters available for this image."
                            util.printD("[civitai_gallery_action] No meta field in image data")
                    else:
                        png_info = "Image metadata not found in current page data."
                        util.printD(f"[civitai_gallery_action] UUID {image_uuid} not in metadata")
                else:
                    png_info = "Could not extract image ID from filename."
                    util.printD(f"[civitai_gallery_action] No UUID in filename: {filename}")
            else:
                util.printD(
                    f"[civitai_gallery_action] Using PNG info from file: {len(png_info)} chars"
                )
        else:
            util.printD(
                f"[civitai_gallery_action] local_path is not string or doesn't exist: {local_path}"
            )
    except Exception as e:
        png_info = f"Error extracting generation parameters: {e}"
        util.printD(f"[civitai_gallery_action] Error: {e}")

    util.printD(f"[civitai_gallery_action] Final png_info length: {len(png_info)} chars")
    return evt.index, local_path, gr.update(selected="Image_Information"), png_info


def on_selected_model_id_change(modelid):
    page_url = None
    versions_list = None
    title_name = None
    version_name = None
    paging_information = None
    is_image_folder = False
    if modelid:
        page_url = get_default_page_url(modelid, None, False)
        model_name, versions_list, version_name, paging_information = get_model_information(
            page_url
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
            choices=[setting.PLACEHOLDER] + versions_list if versions_list else None,
            value=version_name if version_name else setting.PLACEHOLDER,
        ),
        gr.update(
            minimum=1, maximum=total_page, value=1, step=1, label=f"Total {total_page} Pages"
        ),
        paging_information,
        gr.update(visible=is_image_folder),
    )


def on_versions_list_select(evt: gr.SelectData, modelid=None):
    page_url = None
    versions_list = None
    title_name = None
    version_name = None
    paging_information = None

    if modelid:
        if evt.index > 0:
            ver_index = evt.index - 1
            # model_info = civitai.get_model_info(modelid)
            model_info = ishortcut.get_model_info(modelid)
            version_info = dict()
            if model_info:
                if "modelVersions" in model_info.keys():
                    if len(model_info["modelVersions"]) > 0:
                        version_info = model_info["modelVersions"][ver_index]
                        if version_info["id"]:
                            versionid = version_info["id"]
                            page_url = get_default_page_url(modelid, versionid, False)
        else:
            page_url = get_default_page_url(modelid, None, False)

        model_name, versions_list, version_name, paging_information = get_model_information(
            page_url
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
            choices=[setting.PLACEHOLDER] + versions_list if versions_list else None,
            value=version_name if version_name else setting.PLACEHOLDER,
        ),
        gr.update(
            minimum=1, maximum=total_page, value=1, step=1, label=f"Total {total_page} Pages"
        ),
        paging_information,
    )


def get_model_information(page_url=None):
    model_info = None
    version_name = None
    modelid = None
    versionid = None

    if page_url:
        modelid, versionid = extract_model_info(page_url)

    if modelid:
        # model_info = civitai.get_model_info(modelid)
        model_info = ishortcut.get_model_info(modelid)

    if model_info:
        model_name = model_info['name']

        versions_list = list()
        if 'modelVersions' in model_info:
            for ver in model_info['modelVersions']:
                versions_list.append(ver['name'])
                if versionid:
                    if versionid == str(ver['id']):
                        version_name = ver['name']

        # 작업중 2023-07-14 여기서 페이지 정보를 가져오도록 변경한다.
        # paging_information = get_paging_information(modelid,versionid,False)
        paging_information = get_paging_information_working(modelid, versionid, False)

        return model_name, versions_list, version_name, paging_information
    return None, None, None, None


def on_usergal_page_url_change(usergal_page_url, paging_information):
    return load_gallery_page(usergal_page_url, paging_information)


def on_refresh_gallery_change(images_url, progress=gr.Progress()):
    return gallery_loading(images_url, progress)


def on_pre_loading_change(usergal_page_url, paging_information):
    if setting.usergallery_preloading:
        pre_loading(usergal_page_url, paging_information)


def pre_loading(usergal_page_url, paging_information):
    page_url = usergal_page_url

    current_Page = get_current_page(paging_information, usergal_page_url)

    if paging_information:
        if paging_information["totalPageUrls"]:
            totalPageUrls = paging_information["totalPageUrls"]
            if len(totalPageUrls) > current_Page:
                page_url = totalPageUrls[current_Page]

    if page_url:
        image_data = None
        json_data = civitai.request_models(fix_page_url_cursor(page_url))
        try:
            image_data = json_data['items']
        except Exception as e:
            util.printD(e)
            return

        dn_image_list = list()

        if image_data:
            for image_info in image_data:
                if "url" in image_info:
                    img_url = image_info['url']
                    gallery_img_file = setting.get_image_url_to_gallery_file(image_info['url'])
                    if not os.path.isfile(gallery_img_file):
                        dn_image_list.append(img_url)

        if len(dn_image_list) > 0:
            try:
                thread = threading.Thread(target=download_images, args=(dn_image_list,))
                thread.start()
            except Exception as e:
                util.printD(e)
                pass
    return


def download_images(dn_image_list: list):
    """Download images for gallery with improved error handling."""
    if not dn_image_list:
        return

    client = get_http_client()
    util.printD(f"[civitai_gallery_action] Starting download of {len(dn_image_list)} images")

    success_count = 0
    failed_count = 0

    for img_url in dn_image_list:
        gallery_img_file = setting.get_image_url_to_gallery_file(img_url)

        if os.path.isfile(gallery_img_file):
            util.printD(f"[civitai_gallery_action] Image already exists: {gallery_img_file}")
            continue

        util.printD(f"[civitai_gallery_action] Downloading image: {img_url}")
        if client.download_file(img_url, gallery_img_file):
            success_count += 1
            util.printD(f"[civitai_gallery_action] Successfully downloaded: {gallery_img_file}")
        else:
            failed_count += 1
            util.printD(f"[civitai_gallery_action] Failed to download: {img_url}")

    util.printD(
        f"[civitai_gallery_action] Download complete: {success_count} success, {failed_count} failed"
    )

    if failed_count > 0:
        gr.Error(
            f"Some images failed to download ({failed_count} files), "
            "please check your network connection 💥!",
            duration=3,
        )


def load_gallery_page(usergal_page_url, paging_information):
    if usergal_page_url:
        images_url, images_list = get_gallery_information(usergal_page_url, False)

        current_Page = get_current_page(paging_information, usergal_page_url)

        current_time = datetime.datetime.now()

        return current_time, images_url, gr.update(value=current_Page), gr.update(value=None)

    return None, None, gr.update(minimum=1, maximum=1, value=1), None


def get_gallery_information(page_url=None, show_nsfw=False):
    modelid = None
    if page_url:
        modelid, versionid = extract_model_info(page_url)

    if modelid:
        images_url, images_list = get_user_gallery(modelid, page_url, show_nsfw)
        return images_url, images_list
    return None, None


def get_user_gallery(modelid, page_url, show_nsfw):
    if not modelid:
        return None, None

    image_data = get_image_page(modelid, page_url, show_nsfw)

    images_list = {}
    images_url = []

    if image_data:
        # util.printD("Gal:")
        # util.printD(len(image_data))
        for image_info in image_data:
            if "url" in image_info:
                img_url = image_info['url']
                gallery_img_file = setting.get_image_url_to_gallery_file(img_url)

                # NSFW filtering ....
                if setting.NSFW_filtering_enable:

                    # if not setting.NSFW_level[image_info["nsfwLevel"]]:
                    if setting.NSFW_levels.index(
                        image_info["nsfwLevel"]
                    ) > setting.NSFW_levels.index(setting.NSFW_level_user):
                        gallery_img_file = setting.nsfw_disable_image

                if os.path.isfile(gallery_img_file):
                    img_url = gallery_img_file

                images_url.append(img_url)

        images_list = {image_info['id']: image_info for image_info in image_data}

        # Store metadata globally for later retrieval by filename
        global _current_page_metadata
        _current_page_metadata = {}
        if image_data:
            util.printD(f"[civitai_gallery_action] Storing metadata for {len(image_data)} images")
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
                        util.printD(
                            f"[civitai_gallery_action] Stored metadata for UUID: {image_uuid}"
                        )
                        # Debug: Check if meta field exists
                        if 'meta' in image_info:
                            util.printD(
                                f"[civitai_gallery_action] UUID {image_uuid} has meta field"
                            )
                        else:
                            util.printD(
                                f"[civitai_gallery_action] UUID {image_uuid} missing meta field"
                            )

            util.printD(
                f"[civitai_gallery_action] Total metadata stored: "
                f"{len(_current_page_metadata)} items"
            )

    return images_url, images_list


def get_image_page(modelid, page_url, show_nsfw=False):
    json_data = {}

    if not page_url:
        page_url = get_default_page_url(modelid, None, show_nsfw)

    # util.printD(page_url)
    json_data = civitai.request_models(fix_page_url_cursor(page_url))
    # util.printD("here")

    try:
        json_data['items']
    except TypeError:
        return None, None

    return json_data['items']


def get_paging_information(modelId, modelVersionId=None, show_nsfw=False):
    totalPages = 0

    page_url = get_default_page_url(modelId, modelVersionId, show_nsfw)

    total_page_urls = list()
    while page_url is not None:
        total_page_urls.append(page_url)
        # util.printD(page_url)
        json_data = civitai.request_models(fix_page_url_cursor(page_url))

        try:
            page_url = json_data['metadata']['nextPage']
        except KeyError:
            page_url = None

        totalPages = totalPages + 1

    paging_information = dict()
    paging_information["totalPages"] = totalPages
    paging_information["totalPageUrls"] = total_page_urls

    return paging_information


# cursor로 쿼리를 보내면 그 다음것부터 검색되어 리턴되고 있다.
# 명확해 질때까지 대기....
# 페잊 수에 오류가 난다.
def get_paging_information_working(modelId, modelVersionId=None, show_nsfw=False):
    totalPages = 0

    # 한번에 가져올수 있는 최대량은 200 이다.
    page_url = get_default_page_url(modelId, modelVersionId, show_nsfw, 200)

    item_list = list()
    total_page_urls = list()

    while page_url is not None:
        json_data = civitai.request_models(fix_page_url_cursor(page_url))
        try:
            item_list.extend(json_data['items'])
        except KeyError:
            pass

        try:
            page_url = json_data['metadata']['nextPage']
        except KeyError:
            page_url = None

    images_per_page = setting.usergallery_images_column * setting.usergallery_images_rows_per_page

    initial_url = get_default_page_url(modelId, modelVersionId, show_nsfw)
    total_page_urls.append(initial_url)
    # page_items = item_list[::setting.usergallery_images_page_limit]
    page_items = item_list[::images_per_page]
    totalPages = len(page_items)

    for index, item in enumerate(page_items):
        if index > 0:
            total_page_urls.append(util.update_url(initial_url, "cursor", item["id"]))

    paging_information = dict()
    paging_information["totalPages"] = totalPages
    paging_information["totalPageUrls"] = total_page_urls

    return paging_information


# 현재 pageurl 의 cursor에서 page를 계산한다.
def get_current_page(paging_information, page_url):
    current_cursor = extract_url_cursor(page_url)
    # util.printD(f"current {current_cursor}")
    # util.printD(page_url)

    if paging_information:
        total_page_urls = paging_information["totalPageUrls"]
        for cur_page, p_url in enumerate(total_page_urls, start=1):
            p_cursor = extract_url_cursor(p_url)
            # util.printD(p_cursor)

            if not p_cursor:
                continue

            if str(current_cursor) == str(p_cursor):
                # util.printD(f"select {p_cursor}")
                return cur_page
    return 1


def gallery_loading(images_url, progress):
    if images_url:
        dn_image_list = []
        image_list = []

        if not os.path.exists(setting.shortcut_gallery_folder):
            os.makedirs(setting.shortcut_gallery_folder)

        for i, img_url in enumerate(progress.tqdm(images_url, desc="Civitai Images Loading")):
            result = util.is_url_or_filepath(img_url)
            description_img = setting.get_image_url_to_gallery_file(img_url)
            if result == "filepath":
                description_img = img_url
            elif result == "url":
                if not _download_single_image(img_url, description_img):
                    description_img = setting.no_card_preview_image
            else:
                description_img = setting.no_card_preview_image

            dn_image_list.append(description_img)
            image_list.append(description_img)

            current_time = datetime.datetime.now()
        return dn_image_list, image_list, current_time
    return None, None, gr.update(visible=False)


def download_user_gallery_images(model_id, image_urls):
    if not model_id:
        return None

    # model_info = civitai.get_model_info(model_id)
    model_info = ishortcut.get_model_info(model_id)

    if not model_info:
        return None

    image_folder = util.make_download_image_folder(model_info['name'])

    if not image_folder:
        return None

    save_folder = os.path.join(image_folder, "user_gallery_images")

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    if image_urls and len(image_urls) > 0:
        for image_count, img_url in enumerate(
            tqdm(image_urls, desc="Download user gallery image"), start=0
        ):

            result = util.is_url_or_filepath(img_url)
            if result == "filepath":
                if os.path.basename(img_url) != setting.no_card_preview_image:
                    description_img = os.path.join(save_folder, os.path.basename(img_url))
                    shutil.copyfile(img_url, description_img)
            elif result == "url":
                image_id, ext = os.path.splitext(os.path.basename(img_url))
                description_img = os.path.join(
                    save_folder,
                    f"{image_id}{setting.preview_image_suffix}{setting.preview_image_ext}",
                )
                _download_single_image(img_url, description_img)
    return image_folder


def extract_model_info(url):
    model_id_match = re.search(r'modelId=(\d+)', url)
    model_version_id_match = re.search(r'modelVersionId=(\d+)', url)

    model_id = model_id_match.group(1) if model_id_match else None
    model_version_id = model_version_id_match.group(1) if model_version_id_match else None

    return (model_id, model_version_id)


# def extract_url_page(url):
#     model_page_match = re.search(r'page=(\d+)', url)

#     page = int(model_page_match.group(1)) if model_page_match else 0

#     return (page)


def extract_url_cursor(url):
    model_cursor_match = re.search(r'cursor=(\d+)', url)

    cursor = int(model_cursor_match.group(1)) if model_cursor_match else 0

    return cursor


def get_default_page_url(modelId, modelVersionId=None, show_nsfw=False, limit=0):

    if limit <= 0:
        limit = setting.usergallery_images_rows_per_page * setting.usergallery_images_column

    # 200이 최대값이다
    if limit > 200:
        limit = 200

    page_url = f"{civitai.Url_ImagePage()}?limit={limit}&modelId={modelId}"

    if modelVersionId:
        page_url = f"{page_url}&modelVersionId={modelVersionId}"

    # 사실상 사용되지 않기에 주석처리
    # if not show_nsfw:
    #     page_url = f"{page_url}&nsfw=false"

    # Image api 에서 nsfw 필터링이 제대로 이뤄지지않고 있다. 테스트용 그래서 기본은 최고수준으로 허용해준다
    page_url = f"{page_url}&nsfw=X"

    page_url = f"{page_url}&sort=Newest"

    # util.printD(page_url)
    return page_url


# cursor + 1 로 만들어 준다
# civitai 에서 cursor 를 수정 한다면 필요 없다.
def fix_page_url_cursor(page_url, use=True):
    if not use:
        return page_url

    cursor = int(extract_url_cursor(page_url))
    if cursor > 0:
        page_url = util.update_url(page_url, "cursor", cursor + 1)
    return page_url
