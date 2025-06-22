"""
downloader.py

Refactored file download logic integrating centralized HTTP client,
supporting resume capability, progress tracking, and error handling.
"""

import os
import re
import time
import threading
import shutil
import json

import requests
import gradio as gr
from tqdm import tqdm

from . import util, setting, civitai
from .http_client import CivitaiHttpClient


# Module-level download client instance
_download_client = None


def get_download_client() -> CivitaiHttpClient:
    """Get or create HTTP client instance optimized for large file downloads."""
    global _download_client
    if _download_client is None:
        _download_client = CivitaiHttpClient(
            api_key=setting.civitai_api_key,
            timeout=setting.download_timeout,
            max_retries=setting.download_max_retries,
            retry_delay=setting.download_retry_delay,
        )
    return _download_client


def download_image_file(model_name: str, image_urls: list, progress_gr=None):
    """Download model-related images with improved error handling."""
    if not model_name:
        util.printD("[downloader] download_image_file: model_name is empty")
        return

    model_folder = util.make_download_image_folder(model_name)
    if not model_folder:
        util.printD("[downloader] Failed to create download folder")
        return

    save_folder = os.path.join(model_folder, "images")
    os.makedirs(save_folder, exist_ok=True)

    if not image_urls:
        util.printD("[downloader] No image URLs to download")
        return

    client = get_download_client()
    success_count = 0
    total_count = len(image_urls)

    util.printD(f"[downloader] Starting download of {total_count} images for model: {model_name}")

    for index, img_url in enumerate(image_urls, start=1):
        if progress_gr:
            progress_gr((index - 1) / total_count, f"下載圖片 {index}/{total_count}")

        if util.is_url_or_filepath(img_url) == "filepath":
            dest = os.path.join(save_folder, os.path.basename(img_url))
            try:
                shutil.copyfile(img_url, dest)
                success_count += 1
            except Exception as e:
                util.printD(f"[downloader] Failed to copy image {img_url}: {e}")
        else:
            dest_name = f"image_{index:03d}.jpg"
            dest_path = os.path.join(save_folder, dest_name)
            if client.download_file_with_resume(
                img_url, dest_path, headers={"Authorization": f"Bearer {setting.civitai_api_key}"}
            ):
                success_count += 1
                util.printD(f"[downloader] Downloaded image: {dest_path}")
            else:
                util.printD(f"[downloader] Failed to download image: {img_url}")

    util.printD(f"[downloader] Image download complete: {success_count}/{total_count} successful")
    if progress_gr:
        msg = (
            f"圖片下載完成 ✅ ({success_count}/{total_count})"
            if success_count == total_count
            else f"部分圖片下載完成 ⚠️ ({success_count}/{total_count})"
        )
        progress_gr(1.0, msg)
    if success_count < total_count:
        gr.Error(f"部分圖片下載失敗 ({total_count - success_count} 個) 💥!", duration=5)


def download_file(url: str, file_path: str) -> bool:
    """Download large files with robust error handling and resume capability."""
    util.printD(f"[downloader] Starting download: {url} -> {file_path}")

    client = get_download_client()

    def progress_cb(downloaded, total, speed=""):
        percent = (downloaded / total * 100) if total else 0
        util.printD(f"[downloader] Progress: {percent:.1f}% ({downloaded}/{total}) {speed}")

    success = client.download_file_with_resume(
        url,
        file_path,
        progress_callback=progress_cb,
        headers={"Authorization": f"Bearer {setting.civitai_api_key}"},
    )
    if success:
        util.printD(f"[downloader] Successfully downloaded: {file_path}")
        print(f"{os.path.basename(file_path)} successfully downloaded.")
    else:
        util.printD(f"[downloader] Failed to download: {url}")
        print(f"Error: File download failed. {os.path.basename(file_path)}")
        gr.Error(f"檔案下載失敗 💥! {os.path.basename(file_path)}", duration=5)
    return success


def download_file_gr(url: str, file_path: str, progress_gr=None) -> bool:
    """Download files with Gradio progress bar integration."""
    util.printD(f"[downloader] Starting Gradio download: {url} -> {file_path}")

    client = get_download_client()

    def prog_cb(downloaded, total, speed=""):
        if progress_gr:
            progress_gr(
                downloaded / total if total else 0, f"下載中: {downloaded/total*100:.1f}% {speed}"
            )

    success = client.download_file_with_resume(
        url,
        file_path,
        progress_callback=prog_cb,
        headers={"Authorization": f"Bearer {setting.civitai_api_key}"},
    )
    if success:
        util.printD(f"[downloader] Gradio download completed: {file_path}")
        if progress_gr:
            progress_gr(1.0, "下載完成 ✅")
    else:
        util.printD(f"[downloader] Gradio download failed: {url}")
        if progress_gr:
            progress_gr(0, "下載失敗 ❌")
        gr.Error("檔案下載失敗 💥! 請檢查網路連線和存儲空間", duration=8)
    return success


class DownloadManager:
    """Manage multiple download tasks with monitoring and control."""

    def __init__(self):
        self.active = {}
        self.history = []
        self.client = get_download_client()

    def start(self, url: str, file_path: str, progress_cb=None) -> str:
        task_id = f"download_{int(time.time())}_{len(self.active)}"

        def wrap(dl, tot, sp=""):
            if progress_cb:
                progress_cb(dl, tot, sp)
            self.active[task_id] = {
                "url": url,
                "path": file_path,
                "downloaded": dl,
                "total": tot,
                "speed": sp,
            }

        thread = threading.Thread(target=self._worker, args=(task_id, url, file_path, wrap))
        thread.daemon = True
        thread.start()
        return task_id

    def _worker(self, tid, url, path, prog):
        try:
            ok = self.client.download_file_with_resume(url, path, progress_callback=prog)
            info = self.active.pop(tid, {})
            info.update({"completed": True, "success": ok, "end": time.time()})
            self.history.append(info)
        except Exception as e:
            util.printD(f"[downloader] Worker error {tid}: {e}")
            self.active.pop(tid, None)

    def list_active(self):
        return dict(self.active)

    def cancel(self, tid) -> bool:
        return self.active.pop(tid, None) is not None


def add_number_to_duplicate_files(files: list) -> dict:
    counts, result = {}, {}
    for entry in files:
        if ":" not in entry:
            continue
        key, name = entry.split(":", 1)
        cnt = counts.get(name, 0)
        counts[name] = cnt + 1
        base, ext = os.path.splitext(name)
        new_name = f"{base} ({cnt}){ext}" if cnt else name
        result[key] = new_name
    return result


def get_save_base_name(version_info: dict) -> str:
    primary = civitai.get_primary_file_by_version_info(version_info)
    if primary:
        return os.path.splitext(primary["name"])[0]
    return setting.generate_version_foldername(
        version_info["model"]["name"], version_info["name"], version_info["id"]
    )


def download_preview_image(filepath: str, version_info: dict) -> bool:
    """Download preview image for a version into filepath."""
    if not version_info:
        return False
    images = version_info.get("images") or []
    if not images:
        return False
    img_dict = images[0]
    img_url = img_dict.get("url")
    if not img_url:
        return False
    # adjust width if specified
    width = img_dict.get("width")
    if width:
        img_url = util.change_width_from_image_url(img_url, width)
    try:
        client = get_download_client()
        return client.download_file_with_resume(
            img_url,
            filepath,
            headers={"Authorization": f"Bearer {setting.civitai_api_key}"},
        )
    except Exception as e:
        util.printD(f"[downloader] Failed to download preview image: {e}")
        return False


def download_file_thread(
    file_name, version_id, ms_folder, vs_folder, vs_foldername, cs_foldername, ms_foldername
):
    """Threaded download entry for UI."""
    if not file_name or not version_id:
        return
    vi = civitai.get_version_info_by_version_id(version_id)
    if not vi:
        return
    files = civitai.get_files_by_version_info(vi)
    folder = util.make_download_model_folder(
        vi, ms_folder, vs_folder, vs_foldername, cs_foldername, ms_foldername
    )
    if not folder:
        return
    savefile_base = None
    dup = add_number_to_duplicate_files(file_name)
    info_files = vi.get("files") or []
    for fid, fname in dup.items():
        url = files.get(str(fid), {}).get("downloadUrl")
        path = os.path.join(folder, fname)
        threading.Thread(target=download_file, args=(url, path)).start()
        # record primary file base name
        for info in info_files:
            if str(info.get('id')) == str(fid) and info.get('primary'):
                base, _ = os.path.splitext(fname)
                savefile_base = base
    # write version info and preview if primary file found
    if savefile_base:
        info_path = os.path.join(
            folder,
            f"{util.replace_filename(savefile_base)}{setting.info_suffix}{setting.info_ext}",
        )
        if civitai.write_version_info(info_path, vi):
            util.printD(f"[downloader] Wrote version info: {info_path}")
        preview_path = os.path.join(
            folder,
            f"{util.replace_filename(savefile_base)}{setting.preview_image_suffix}{setting.preview_image_ext}",
        )
        if download_preview_image(preview_path, vi):
            util.printD(f"[downloader] Wrote preview image: {preview_path}")
    return "Download started"
