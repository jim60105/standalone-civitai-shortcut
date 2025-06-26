"""
downloader.py

Refactored file download logic integrating centralized HTTP client,
supporting resume capability, progress tracking, and error handling.
"""

import os
import time
import threading
import shutil
import gradio as gr

from . import util, setting, civitai

# Use centralized HTTP client and chunked downloader factories
from .http_client import get_http_client, get_chunked_downloader, ParallelImageDownloader


class DownloadNotifier:
    """Notify users of download status via UI and logs."""

    @staticmethod
    def notify_start(filename: str, file_size: int = None):
        """Notify download start using gr.Info and debug log."""
        try:
            size_str = f" ({util.format_file_size(file_size)})" if file_size else ""
            gr.Info(f"🚀 Starting download: {filename}{size_str}", duration=3)
        except Exception:
            pass
        util.printD(f"[downloader] Starting download: {filename}{size_str}")

    @staticmethod
    def notify_progress(filename: str, downloaded: int, total: int, speed: str = ""):
        """Log download progress."""
        if total and total > 0:
            percentage = (downloaded / total) * 100
            downloaded_str = util.format_file_size(downloaded)
            total_str = util.format_file_size(total)
            speed_str = f" at {speed}" if speed else ""
            util.printD(
                (
                    f"[downloader] Progress: {percentage:.1f}% "
                    f"({downloaded_str}/{total_str}){speed_str}"
                )
            )
        else:
            downloaded_str = util.format_file_size(downloaded)
            speed_str = f" at {speed}" if speed else ""
            util.printD(f"[downloader] Downloaded: {downloaded_str}{speed_str}")

    @staticmethod
    def notify_complete(filename: str, success: bool, error_msg: str = None):
        """Notify download completion or failure using UI and logs."""
        try:
            if success:
                gr.Info(f"✅ Download completed: {filename}", duration=5)
            else:
                error_detail = f" - {error_msg}" if error_msg else ""
                gr.Error(f"❌ Download failed: {filename}{error_detail}", duration=10)
        except Exception:
            pass
        status = "successfully" if success else f"failed{error_detail}"
        util.printD(f"[downloader] Download {status}: {filename}")


class DownloadTask:
    """Data structure for carrying download task parameters."""

    def __init__(self, fid, filename, url, path, total_size=None):
        self.fid = fid
        self.filename = filename
        self.url = url
        self.path = path
        self.total = total_size


def download_file_with_notifications(task: DownloadTask):
    """Download file with progress notifications."""

    def progress_callback(downloaded: int, total: int, speed: str = ""):
        DownloadNotifier.notify_progress(task.filename, downloaded, total, speed)

    try:
        success = get_http_client().download_file_with_resume(
            task.url, task.path, progress_callback=progress_callback
        )
        DownloadNotifier.notify_complete(task.filename, success)
    except Exception as e:
        DownloadNotifier.notify_complete(task.filename, False, str(e))


def download_image_file(model_name: str, image_urls: list, progress_gr=None):
    """Download model-related images with parallel processing."""
    if not model_name or not image_urls:
        return

    model_folder = util.make_download_image_folder(model_name)
    if not model_folder:
        return

    save_folder = os.path.join(model_folder, "images")
    os.makedirs(save_folder, exist_ok=True)

    # Prepare parallel download tasks
    image_tasks = []
    for index, img_url in enumerate(image_urls, start=1):
        if util.is_url_or_filepath(img_url) == "url":
            dest_name = f"image_{index:03d}.jpg"
            dest_path = os.path.join(save_folder, dest_name)
            image_tasks.append((img_url, dest_path))

    # Setup progress wrapper for Gradio
    def progress_wrapper(progress, desc):
        if progress_gr:
            progress_gr(progress, desc)

    # Execute parallel download
    downloader = ParallelImageDownloader(max_workers=10)
    success_count = downloader.download_images(image_tasks, progress_wrapper)

    # Handle final progress update
    total_count = len(image_urls)
    util.printD(
        f"[downloader] Parallel image download complete: {success_count}/{total_count} successful"
    )

    if progress_gr:
        msg = f"Downloaded {success_count}/{total_count} images"
        progress_gr(1.0, msg)


def download_file(url: str, file_path: str) -> bool:
    """Download large files using chunked downloader."""
    downloader = get_chunked_downloader()
    return downloader.download_large_file(url, file_path)


def download_file_gr(url: str, file_path: str, progress_gr=None) -> bool:
    """Download files with Gradio progress integration."""
    # Use HTTP client for streaming download with progress callback
    client = get_http_client()

    def progress_wrapper(downloaded: int, total: int) -> None:
        if progress_gr:
            fraction = downloaded / total if total > 0 else 0
            progress_gr(fraction, "")

    return client.download_file(url, file_path, progress_callback=progress_wrapper)


class DownloadManager:
    """Manage multiple download tasks with monitoring and control."""

    def __init__(self):
        self.active = {}
        self.history = []
        self.client = get_http_client()

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
    """Generate unique filenames for duplicate entries keyed by identifier."""
    result: dict = {}
    used_names: set = set()

    for entry in files:
        if ":" not in entry:
            continue
        key, name = entry.split(":", 1)
        # Skip if key already processed
        if key in result:
            continue

        base, ext = os.path.splitext(name)
        new_name = name
        count = 1
        # Append number suffix until name is unique
        while new_name in used_names:
            new_name = f"{base} ({count}){ext}"
            count += 1

        result[key] = new_name
        used_names.add(new_name)
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
        client = get_http_client()
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
    """Threaded download entry for UI with enhanced notifications."""
    if not file_name or not version_id:
        return
    vi = civitai.get_version_info_by_version_id(version_id)
    if not vi:
        DownloadNotifier.notify_complete(str(file_name), False, "Failed to get version info")
        return
    files = civitai.get_files_by_version_info(vi)
    folder = util.make_download_model_folder(
        vi, ms_folder, vs_folder, vs_foldername, cs_foldername, ms_foldername
    )
    if not folder:
        DownloadNotifier.notify_complete(str(file_name), False, "Failed to create download folder")
        return

    savefile_base = None
    dup = add_number_to_duplicate_files(file_name)
    info_files = vi.get("files") or []
    # Start download tasks with notifications
    for fid, fname in dup.items():
        file_info = next((f for f in info_files if str(f.get('id')) == str(fid)), None)
        file_size = file_info.get('sizeKB', 0) * 1024 if file_info else None

        # Notify download start
        DownloadNotifier.notify_start(fname, file_size)

        url = files.get(str(fid), {}).get("downloadUrl")
        path = os.path.join(folder, fname)

        # Schedule download with progress notifications
        task = DownloadTask(fid, fname, url, path, file_size)
        threading.Thread(target=download_file_with_notifications, args=(task,)).start()

        # Record primary file base name
        if file_info and file_info.get('primary'):
            base, _ = os.path.splitext(fname)
            savefile_base = base

    # Write version info and preview image if primary file found
    if savefile_base:
        info_path = os.path.join(
            folder,
            f"{util.replace_filename(savefile_base)}{setting.info_suffix}{setting.info_ext}",
        )
        if civitai.write_version_info(info_path, vi):
            util.printD(f"[downloader] Wrote version info: {info_path}")
        preview_path = os.path.join(
            folder,
            f"{util.replace_filename(savefile_base)}"
            f"{setting.preview_image_suffix}{setting.preview_image_ext}",
        )
        if download_preview_image(preview_path, vi):
            util.printD(f"[downloader] Wrote preview image: {preview_path}")

        # Generate LoRa/LyCORIS metadata JSON file for LoRa models
        if vi and _is_lora_model(vi):
            metadata_path = os.path.join(folder, f"{util.replace_filename(savefile_base)}.json")
            if civitai.write_LoRa_metadata(metadata_path, vi):
                util.printD(f"[downloader] Wrote LoRa metadata: {metadata_path}")
    return "Download started with notifications"


def _is_lora_model(version_info: dict) -> bool:
    """Check if the model is a LoRa or LyCORIS model."""
    if not version_info or "model" not in version_info:
        return False

    model_type = version_info["model"].get("type", "").upper()
    return model_type in ["LORA", "LOCON", "LYCORIS"]
