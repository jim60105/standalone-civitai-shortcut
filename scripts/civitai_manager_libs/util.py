import re
import os
import json
import hashlib
import platform
import subprocess
import time
from .compat.environment_detector import EnvironmentDetector
from . import setting

import logging
from .logging_config import get_logger

# Module logger for standardized debug output (deprecated printD wrapper)
logger = get_logger(__name__)


EXTENSIONS_NAME = "Civitai Shortcut"

try:
    from tqdm import tqdm
except ImportError:

    def tqdm(iterable, **kwargs):  # type: ignore[misc,no-redef]
        return iterable


def printD(msg):
    """
    Legacy debug function - maintaining backward compatibility.
    Note: this function is deprecated; use logger.debug() instead.
    """
    logger.debug(msg)


def format_file_size(size_bytes: int) -> str:
    """Convert a file size in bytes to a human-readable string."""
    if size_bytes is None:
        return ""
    try:
        size = float(size_bytes)
    except (TypeError, ValueError):
        return ""
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):  # up to petabytes
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}EB"


def get_module_logger(module_name: str) -> logging.Logger:
    """Get a logger for specific module"""
    return get_logger(module_name)


def calculate_sha256(filname):
    """
    Calculate the SHA256 hash for a file.
    """
    block_size = 1024 * 1024  # 1MB
    length = 0
    with open(filname, 'rb') as file:
        hash = hashlib.sha256()
        for chunk in tqdm(
            iter(lambda: file.read(block_size), b""),
            total=(os.path.getsize(filname) // block_size) + 1,
        ):
            length += len(chunk)
            hash.update(chunk)

        hash_value = hash.hexdigest()
        printD("sha256: " + hash_value)
        printD("length: " + str(length))
        return hash_value


def is_url_or_filepath(input_string):
    if not input_string:
        return "unknown"

    if os.path.exists(input_string):
        return "filepath"
    elif input_string.lower().startswith("http://") or input_string.lower().startswith("https://"):
        return "url"
    else:
        return "unknown"


def convert_civitai_meta_to_stable_meta(meta: dict):
    meta_string = ""
    different_key = [
        'prompt',
        'negativePrompt',
        'steps',
        'sampler',
        'cfgScale',
        'seed',
        'resources',
        'hashes',
    ]
    if meta:
        if "prompt" in meta:
            meta_string = f"""{meta['prompt']}""" + "\n"
        if "negativePrompt" in meta:
            meta_string = meta_string + f"""Negative prompt:{meta['negativePrompt']}""" + "\n"
        if "steps" in meta:
            meta_string = meta_string + f",Steps:{meta['steps']}"
        if "sampler" in meta:
            meta_string = meta_string + f",Sampler:{meta['sampler']}"
        if "cfgScale" in meta:
            meta_string = meta_string + f",CFG scale:{meta['cfgScale']}"
        if "seed" in meta:
            meta_string = meta_string + f",Seed:{meta['seed']}"

        addistion_string = ','.join(
            [f'{key}:{value}' for key, value in meta.items() if key not in different_key]
        )
        meta_string = meta_string + "," + addistion_string

    return meta_string


def update_url(url, param_name, new_value):
    if param_name not in url:
        # If the parameter is not found in the URL, add it to the end with the new value
        if "?" in url:
            # If there are already parameters in the URL,
            # add the new parameter with "&" separator
            updated_url = url + "&" + param_name + "=" + str(new_value)
        else:
            # If there are no parameters in the URL,
            # add the new parameter with "?" separator
            updated_url = url + "?" + param_name + "=" + str(new_value)
    else:
        # If the parameter is found in the URL, update its value with the new value
        prefix, suffix = url.split(param_name + "=")
        if "&" in suffix:
            current_value, remainder = suffix.split("&", 1)
            updated_suffix = param_name + "=" + str(new_value) + "&" + remainder
        else:
            updated_suffix = param_name + "=" + str(new_value)
        updated_url = prefix + updated_suffix

    return updated_url


def add_number_to_duplicate_files(filenames) -> dict:
    counts = {}
    for i, filename in enumerate(filenames):
        if filename in counts:
            name, ext = os.path.splitext(filename)
            counts[filename] += 1
            filenames[i] = f"{name} ({counts[filename]}){ext}"
        else:
            counts[filename] = 0

    # 굳이 안해도 dict가 되네????
    # result = dict()
    # if filenames:
    #     for filename in filenames:
    #         file = filename[filename.lfind(':') + 1:]
    #         id = filename[:filename.lfind(':')]
    #         result[str(id)] = file
    #     return result

    return filenames


def open_folder(path):
    """
    Open the given folder in the system file explorer.
    Compatible with both WebUI and standalone modes.
    Returns True if successful, False otherwise.
    """
    try:
        if not os.path.exists(path):
            printD(f"[util.open_folder] Path does not exist: {path}")
            return False
        if EnvironmentDetector.is_webui_mode():
            try:
                import modules.shared as shared

                if hasattr(shared, "cmd_opts") and hasattr(shared.cmd_opts, "hide_ui_dir_config"):
                    if getattr(shared.cmd_opts, "hide_ui_dir_config", False):
                        printD(
                            "[util.open_folder] UI directory config is hidden by WebUI settings."
                        )
                        return False
            except Exception as e:
                printD(f"[util.open_folder] WebUI detection/import failed: {e}")
        system = platform.system()
        if system == "Windows":
            os.startfile(path)
        elif system == "Darwin":
            subprocess.Popen(["open", path])
        elif "microsoft-standard-WSL2" in platform.uname().release:
            subprocess.Popen(["wsl-open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        printD(f"[util.open_folder] Opened folder: {path}")
        return True
    except Exception as e:
        printD(f"[util.open_folder] Exception: {e} (path: {path})")
        return False


def get_search_keyword(search: str):
    tags = []
    keys = []
    notes = []

    if not search:
        return None, None, None

    for word in search.split(","):
        word = word.strip()
        if word.startswith("#"):
            if len(word) > 1:
                tag = word[1:].lower()
                if tag not in tags:
                    tags.append(tag)
        elif word.startswith("@"):
            if len(word) > 1:
                note = word[1:]
                if note not in notes:
                    notes.append(note)
        else:
            word = word.lower()
            if word not in keys:
                keys.append(word)

    return (
        keys if len(keys) > 0 else None,
        tags if len(tags) > 0 else None,
        notes if len(notes) > 0 else None,
    )


def read_json(path) -> dict:
    contents = None
    if not path:
        return None
    try:
        with open(path, 'r') as f:
            contents = json.load(f)
    except Exception:
        return None

    return contents


def write_json(contents, path):
    if not path:
        return

    if not contents:
        return

    try:
        with open(path, 'w') as f:
            f.write(json.dumps(contents, indent=4))
    except Exception:
        return


def scan_folder_for_info(folder):
    from . import setting

    info_list = search_file([folder], None, [setting.info_ext])

    if not info_list:
        return None

    return info_list


def get_download_image_folder(ms_foldername):

    if not ms_foldername:
        return

    from . import setting

    if not setting.download_images_folder:
        return

    model_folder = os.path.join(
        setting.download_images_folder.strip(), replace_dirname(ms_foldername.strip())
    )

    if not os.path.exists(model_folder):
        return None

    return model_folder


def make_download_image_folder(ms_foldername):

    if not ms_foldername:
        return

    from . import setting

    if not setting.download_images_folder:
        return

    model_folder = os.path.join(
        setting.download_images_folder.strip(), replace_dirname(ms_foldername.strip())
    )

    if not os.path.exists(model_folder):
        os.makedirs(model_folder)

    return model_folder


# 다정하면 임의의 분류뒤에 모델폴더를 생성하고 그뒤에 버전까지 생성가능
def make_download_model_folder(
    version_info,
    ms_folder=True,
    vs_folder=True,
    vs_foldername=None,
    cs_foldername=None,
    ms_foldername=None,
):

    if not version_info:
        return

    if "model" not in version_info.keys():
        return

    from . import setting

    content_type = version_info['model']['type']
    model_folder = setting.generate_type_basefolder(content_type)

    if not model_folder:
        return

    if not cs_foldername and not ms_folder:
        return

    if cs_foldername:
        model_folder = os.path.join(model_folder, replace_dirname(cs_foldername.strip()))

    if ms_folder:
        if not ms_foldername or len(ms_foldername.strip()) <= 0:
            ms_foldername = version_info['model']['name']

        model_folder = os.path.join(model_folder, replace_dirname(ms_foldername.strip()))

    if vs_folder:
        if not vs_foldername or len(vs_foldername.strip()) <= 0:
            from . import setting

            vs_foldername = setting.generate_version_foldername(
                ms_foldername, version_info['name'], version_info['id']
            )

        model_folder = os.path.join(model_folder, replace_dirname(vs_foldername.strip()))

    if not os.path.exists(model_folder):
        os.makedirs(model_folder)

    return model_folder


def replace_filename(file_name):
    if file_name and len(file_name.strip()) > 0:
        return (
            file_name.replace("*", "-")
            .replace("?", "-")
            .replace("\"", "-")
            .replace("|", "-")
            .replace(":", "-")
            .replace("/", "-")
            .replace("\\", "-")
            .replace("<", "-")
            .replace(">", "-")
        )
    return None


def replace_dirname(dir_name):
    if dir_name and len(dir_name.strip()) > 0:
        return (
            dir_name.replace("*", "-")
            .replace("?", "-")
            .replace("\"", "-")
            .replace("|", "-")
            .replace(":", "-")
            .replace("/", "-")
            .replace("\\", "-")
            .replace("<", "-")
            .replace(">", "-")
        )
    return None


def write_InternetShortcut(path, url):
    try:
        with open(path, 'w', newline='\r\n') as f:
            f.write(f"[InternetShortcut]\nURL={url}")
    except Exception:
        return False
    return True


def load_InternetShortcut(path) -> str:
    urls = list()
    try:
        with open(path, 'r') as f:
            content = f.read()
            # urls = re.findall("(?P<url>https?://[^\s]+)", content)
            urls = re.findall(r'(?P<url>https?://[^\s:"]+)', content)
    except Exception as e:
        printD(e)
        return
    # printD(urls)
    return urls


# get image with full size
# width is in number, not string
# 파일 인포가 있는 원본 이미지 주소이다.
def get_full_size_image_url(image_url, width):
    return re.sub(r'/width=\d+/', '/width=' + str(width) + '/', image_url)


def change_width_from_image_url(image_url, width):
    return re.sub(r'/width=\d+/', '/width=' + str(width) + '/', image_url)


def get_model_id_from_url(url):
    if not url:
        return ""

    if url.isnumeric():
        return str(url)

    s = url.split("/")
    if len(s) < 2:
        return ""

    for i in range(len(s)):
        if s[i] == "models" and i < len(s) - 1:
            id_str = s[i + 1].split("?")[0]
            if id_str.isnumeric():
                return id_str

    return ""


def search_file(root_dirs: list, base: list, exts: list) -> list:
    file_list = list()
    root_path = os.getcwd()

    for root_dir in root_dirs:
        for root, dirs, files in os.walk(os.path.join(root_path, root_dir)):
            if len(files) > 0:
                for file_name in files:
                    b, e = os.path.splitext(file_name)
                    if base and exts:
                        if e in exts and b in base:
                            file_list.append(os.path.join(root, file_name))
                    elif base:
                        if b in base:
                            file_list.append(os.path.join(root, file_name))
                    elif exts:
                        if e in exts:
                            file_list.append(os.path.join(root, file_name))
                    else:
                        file_list.append(os.path.join(root, file_name))

    return file_list if len(file_list) > 0 else None


# Image download helper functions
def download_image_safe(
    url: str,
    save_path: str,
    client=None,
    show_error: bool = True,
) -> bool:
    """Safely download image with consistent error handling."""
    if not url:
        printD("[util] download_image_safe: URL is empty")
        return False

    if os.path.exists(save_path):
        printD(f"[util] Image already exists: {save_path}")
        return True

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    if client is None:
        from .http_client import get_http_client

        client = get_http_client()

    try:
        success = client.download_file(url, save_path)
    except Exception as e:
        printD(f"[util] download_image_safe exception: {e}")
        success = False

    if success:
        printD(f"[util] Successfully downloaded image: {save_path}")
    else:
        printD(f"[util] Failed to download image: {url}")
        if show_error:
            try:
                import gradio as gr

                gr.Error("Image download failed 💥!", duration=3)
            except Exception:
                pass

    return success


def handle_image_download_error(
    error: Exception,
    url: str,
    context: str = "",
) -> None:
    """Handle image download errors specifically."""
    error_msg = ""

    import requests

    if isinstance(error, requests.exceptions.Timeout):
        error_msg = "Image download timed out"
    elif isinstance(error, requests.exceptions.ConnectionError):
        error_msg = "Network connection failed"
    elif hasattr(error, 'response') and error.response:
        status_code = error.response.status_code
        if status_code == 404:
            error_msg = "Image not found"
        elif status_code == 403:
            error_msg = "Image access denied"
        else:
            error_msg = f"Image download failed (HTTP {status_code})"
    else:
        error_msg = "Unknown image download error"

    printD(f"[image_download] {context}: {error_msg} - {url}")

    if context in ["preview", "model_image"]:
        try:
            import gradio as gr

            gr.Error(f"{error_msg} 💥!", duration=3)
        except Exception:
            pass


def download_with_cache_and_retry(
    url: str,
    cache_key: str,
    max_age: int = 3600,
) -> str:
    """Download with caching and retry logic."""
    cache_path = os.path.join(setting.cache_folder, f"{cache_key}.jpg")

    if os.path.exists(cache_path):
        if time.time() - os.path.getmtime(cache_path) < max_age:
            printD(f"[cache] Using cached image: {cache_path}")
            return cache_path

    from .http_client import get_http_client

    client = get_http_client()
    success = client.download_file(url, cache_path)

    if success:
        return cache_path
    if os.path.exists(cache_path):
        printD("[cache] Using stale cached image due to download failure")
        return cache_path
    return setting.no_card_preview_image


def optimize_downloaded_image(
    image_path: str,
    max_size: tuple = (800, 600),
    quality: int = 85,
) -> bool:
    """Optimize downloaded image size and quality."""
    try:
        from PIL import Image

        with Image.open(image_path) as img:
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            img.save(image_path, format='JPEG', quality=quality, optimize=True)

        printD(f"[image_optimize] Optimized image: {image_path}")
        return True
    except Exception as e:
        printD(f"[image_optimize] Failed to optimize {image_path}: {e}")
        return False
