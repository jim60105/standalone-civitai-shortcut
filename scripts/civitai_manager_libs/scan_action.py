import os
import gradio as gr
import json

from .logging_config import get_logger

logger = get_logger(__name__)
from . import util

from . import model
from . import settings
from . import civitai
import scripts.civitai_manager_libs.ishortcut_core as ishortcut
from . import ishortcut_action
from .http import get_http_client

# Error handling imports
# Error handling imports
from .error_handler import with_error_handling
from .exceptions import (  # noqa: F401
    CivitaiShortcutError,  # noqa: F401
    NetworkError,  # noqa: F401
    FileOperationError,  # noqa: F401
    ConfigurationError,  # noqa: F401
    ValidationError,  # noqa: F401
    APIError,  # noqa: F401
)  # noqa: F401


@with_error_handling(
    fallback_value=False,
    exception_types=(NetworkError, FileOperationError),
    retry_count=3,
    retry_delay=2.0,
    user_message="Failed to download scan image",
)
def download_scan_image(url: str, save_path: str) -> bool:
    """Download image during scan operation."""
    logger.info(f"Downloading scan image: {url}")
    client = get_http_client()
    success = client.download_file(url, save_path)
    if success:
        logger.info(f"Scan image downloaded: {save_path}")
    else:
        logger.error(f"Failed to download scan image: {url}")
    return success


def on_scan_ui():
    with gr.Column():
        with gr.Row():
            with gr.Accordion("Scan models for Civitai", open=True):
                with gr.Row():
                    with gr.Column():
                        fix_information_filename = gr.Checkbox(
                            label="Fix version information filename", value=False, visible=False
                        )
                        scan_models_btn = gr.Button(value="Scan Models", variant="primary")
                        gr.Markdown(
                            value="This feature targets models that do not have information files available in the saved models. It calculates the hash value and searches for the model in Civitai, registering it as a shortcut. Calculating the hash value can take a significant amount of time.",
                            visible=True,
                        )
                        with gr.Group(elem_classes="cs_box", visible=False) as scanned_result:
                            with gr.Column():
                                scan_models_result = gr.CheckboxGroup(
                                    visible=True, container=True, label="Scanned Model List"
                                )
                                with gr.Row():
                                    unselect_scan_models_result_btn = gr.Button(
                                        value="Unselect All", variant="primary"
                                    )
                                    clear_scan_models_result_btn = gr.Button(
                                        value="Clear Results", variant="primary"
                                    )
                with gr.Row(visible=False) as update_information:
                    with gr.Column():
                        with gr.Row():
                            with gr.Column(scale=1):
                                scan_register_shortcut = gr.Checkbox(
                                    label="Register a shortcut when creating the model information file.",
                                    value=True,
                                )
                            with gr.Column(scale=1):
                                with gr.Row():
                                    scan_save_modelfolder = gr.Checkbox(
                                        label="Create a model folder corresponding to the model type.",
                                        value=False,
                                    )
                                    scan_save_vsfolder = gr.Checkbox(
                                        label="Create individual model version folder.",
                                        value=False,
                                        interactive=False,
                                    )
                        with gr.Row():
                            with gr.Column():
                                create_models_info_btn = gr.Button(
                                    value="Create Model Information", variant="primary"
                                )
        with gr.Row():
            with gr.Accordion("Update Shortcuts", open=True):
                with gr.Row():
                    with gr.Column():
                        scan_to_shortcut_btn = gr.Button(
                            value="Scan downloaded models for shortcut registration",
                            variant="primary",
                        )
                        scan_progress = gr.Markdown(
                            value="This feature scans for models that have information files available and registers a shortcut for them, downloading any necessary images in the process. If there is no information available for a particular model, please use the 'Scan Models' feature.",
                            visible=True,
                        )

                with gr.Row():
                    with gr.Column():
                        update_all_shortcuts_btn = gr.Button(
                            value="Update the model information for the shortcut", variant="primary"
                        )
                        update_progress = gr.Markdown(
                            value="This feature updates registered shortcuts with the latest information and downloads any new images if available.",
                            visible=True,
                        )
        with gr.Row():
            with gr.Accordion("Update Downloaded Model", open=True):
                with gr.Row():
                    with gr.Column():
                        update_lora_meta_for_downloaded_model_btn = gr.Button(
                            value="Create a Lora metadata file for a downloaded model without Lora metadata file.",
                            variant="primary",
                        )
                        update_lora_meta_progress = gr.Markdown(
                            value="This feature generates a Lora metadata file for a downloaded model without Lora metadata file.",
                            visible=True,
                        )

    unselect_scan_models_result_btn.click(
        fn=on_unselect_scan_models_result_btn_click, inputs=None, outputs=[scan_models_result]
    )

    clear_scan_models_result_btn.click(
        fn=on_clear_scan_models_result_btn_click,
        inputs=None,
        outputs=[
            scan_models_result,
            scanned_result,
            update_information,
        ],
    )

    scan_save_modelfolder.change(
        fn=on_scan_save_modelfolder_change,
        inputs=[scan_save_modelfolder],
        outputs=[scan_save_vsfolder],
    )

    create_models_info_btn.click(
        fn=on_create_models_info_btn_click,
        inputs=[
            scan_models_result,
            scan_save_modelfolder,
            scan_save_vsfolder,
            scan_register_shortcut,
        ],
        outputs=[scan_models_result, scanned_result, update_information],
    )

    scan_models_btn.click(
        fn=on_scan_models_btn_click,
        inputs=[fix_information_filename],
        outputs=[
            scan_models_result,
            scanned_result,
            update_information,
            scan_save_modelfolder,
            scan_save_vsfolder,
        ],
    )

    update_all_shortcuts_btn.click(
        fn=on_update_all_shortcuts_btn_click,
        inputs=None,
        outputs=[
            update_progress,
        ],
    )

    scan_to_shortcut_btn.click(
        fn=on_scan_to_shortcut_click,
        inputs=None,
        outputs=[
            scan_progress,
        ],
    )

    update_lora_meta_for_downloaded_model_btn.click(
        fn=on_update_lora_meta_for_downloaded_model_btn_click,
        inputs=None,
        outputs=[update_lora_meta_progress],
    )


def on_unselect_scan_models_result_btn_click():
    return gr.update(value=[], interactive=True)


def on_clear_scan_models_result_btn_click():
    return (
        gr.update(choices=[], value=[], interactive=True),
        gr.update(visible=False),
        gr.update(visible=False),
    )


def create_models_information(files, mfolder, vs_folder, register_shortcut, progress=gr.Progress()):

    non_list = list()
    if not files:
        return None

    for file_path in progress.tqdm(files, desc="Create Models Information"):
        if os.path.isfile(file_path):
            logger.debug(f"Generate SHA256: {file_path}")
            hash = util.calculate_sha256(file_path)
            version_info = civitai.get_version_info_by_hash(hash)

            if not version_info:
                # These models are not registered with Civitai.
                non_list.append(file_path)
                continue

            vfolder, vfile = os.path.split(file_path)
            basename, ext = os.path.splitext(vfile)

            # 저장할 폴더 생성
            if mfolder:
                model_folder = util.make_download_model_folder(version_info, True, vs_folder)
                # 다정하면 임의의 분류뒤에 모델폴더를 생성하고 그뒤에 버전까지 생성가능
                # model_folder = make_download_model_folder(version_info, ms_folder=True, vs_folder=True, vs_foldername=None, cs_foldername=None):
                # model_folder = util.make_version_folder(version_info, vs_folder)
            else:
                model_folder = vfolder

            # version info file name 으로 교체시
            # savefile_base = downloader.get_save_base_name(version_info)
            # basename = savefile_base
            # destination = os.path.join(model_folder, f"{basename}{ext}")

            # save info
            info_path = os.path.join(
                model_folder, f"{basename}{settings.INFO_SUFFIX}{settings.INFO_EXT}"
            )
            result = civitai.write_version_info(info_path, version_info)
            if result:
                logger.info(f"Wrote version info: {info_path}")

            # save preview
            if "images" in version_info.keys():
                img_dict = version_info["images"][0]
                img_url = img_dict.get("url")
                if img_url:
                    if img_dict.get("width"):
                        img_url = util.change_width_from_image_url(img_url, img_dict["width"])
                    description_img = os.path.join(
                        model_folder,
                        f"{basename}{settings.PREVIEW_IMAGE_SUFFIX}{settings.PREVIEW_IMAGE_EXT}",
                    )
                    download_scan_image(img_url, description_img)

            # 파일 이동
            if mfolder:
                destination = os.path.join(model_folder, vfile)
                if file_path != destination:
                    if not os.path.isfile(destination):
                        os.rename(file_path, destination)
                    else:
                        logger.warning(f"The target file already exists: {destination}")

            # 숏컷 추가
            if register_shortcut:
                if version_info['modelId']:
                    ishortcut.shortcutcollectionmanager.update_shortcut(version_info['modelId'], progress)
                    model.update_downloaded_model()

    return non_list


def is_filename_in_version_info_in_directory(directory, filename):

    file_list = []
    for file in os.listdir(directory):
        if file.endswith(f"{settings.INFO_SUFFIX}{settings.INFO_EXT}"):
            file_list.append(os.path.join(directory, file))

    if not file_list:
        return False

    for file in file_list:
        try:
            with open(file, 'r') as f:
                json_data = json.load(f)
                if "files" in json_data.keys():
                    files = json_data['files']
                    for file in files:
                        if file['name'] == filename:
                            return True
        except Exception:
            pass

    return False


def scan_models(fix_information_filename, progress=gr.Progress()):
    root_dirs = list(set(settings.model_folders.values()))
    file_list = util.search_file(root_dirs, None, settings.MODEL_EXTS)

    result = list()

    if fix_information_filename:
        # fix_version_information_filename()
        pass

    for file_path in progress.tqdm(file_list, desc="Scan Models for Civitai"):

        vfolder, vfile = os.path.split(file_path)
        basename, ext = os.path.splitext(vfile)
        info = os.path.join(vfolder, f"{basename}{settings.INFO_SUFFIX}{settings.INFO_EXT}")

        if not os.path.isfile(info):
            # result.append(file_path)
            if not is_filename_in_version_info_in_directory(vfolder, vfile):
                # logger.debug(f"{file_path} : {vfile}: no info")
                result.append(file_path)

    return result


# def fix_version_information_filename():
#     root_dirs = list(set(settings.model_folders.values()))
#     file_list = util.search_file(root_dirs,None,[settings.info_ext])

#     version_info = None
#     if not file_list:
#         return

#     for file_path in file_list:

#         try:
#             with open(file_path, 'r') as f:
#                 json_data = json.load(f)

#                 if 'id' in json_data.keys():
#                     version_info = json_data

#             file_path = file_path.strip()
#             vfolder , vfile = os.path.split(file_path)
#             savefile_base = downloader.get_save_base_name(version_info)
#             info_file = os.path.join(vfolder, f"{util.replace_filename(savefile_base)}{settings.info_suffix}{settings.info_ext}")

#             if file_path != info_file:
#                 if not os.path.isfile(info_file):
#                     os.rename(file_path, info_file)

#         except:
#             pass


@with_error_handling(
    fallback_value=(
        gr.update(choices=[], value=[]),
        gr.update(visible=False),
        gr.update(visible=False),
    ),
    exception_types=(NetworkError, FileOperationError),
    retry_count=1,
    user_message="Failed to create model information",
)
def on_create_models_info_btn_click(
    files, mfolder, vsfolder, register_shortcut, progress=gr.Progress()
):
    remain_files = create_models_information(files, mfolder, vsfolder, register_shortcut, progress)
    if remain_files and len(remain_files) > 0:
        return (
            gr.update(
                choices=remain_files,
                value=remain_files,
                interactive=True,
                label="These models are not registered with Civitai.",
            ),
            gr.update(visible=True),
            gr.update(visible=True),
        )
    return (
        gr.update(choices=[], value=[], interactive=True),
        gr.update(visible=False),
        gr.update(visible=False),
    )


@with_error_handling(
    fallback_value=(
        gr.update(choices=[], value=[]),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(value=False),
        gr.update(value=False),
    ),
    exception_types=(FileOperationError, NetworkError),
    user_message="Failed to scan models",
)
def on_scan_models_btn_click(fix_information_filename, progress=gr.Progress()):
    files = scan_models(fix_information_filename, progress)
    return (
        gr.update(choices=files, value=files, interactive=True, label="Scanned Model List"),
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(value=False, interactive=True),
        gr.update(value=False, interactive=False),
    )


@with_error_handling(
    fallback_value=gr.update(value="Scan failed"),
    exception_types=(NetworkError, FileOperationError),
    retry_count=1,
    user_message="Failed to scan shortcuts",
)
def on_scan_to_shortcut_click(progress=gr.Progress()):
    model.update_downloaded_model()
    ishortcut_action.scan_downloadedmodel_to_shortcut(progress)
    return gr.update(visible=True)


@with_error_handling(
    fallback_value=gr.update(value="Update failed"),
    exception_types=(NetworkError, FileOperationError),
    retry_count=1,
    user_message="Failed to update shortcuts",
)
def on_update_all_shortcuts_btn_click(progress=gr.Progress()):
    ishortcut.shortcutcollectionmanager.update_all_shortcuts(progress)
    return gr.update(visible=True)


def on_scan_save_modelfolder_change(scan_save_modelfolder):
    if scan_save_modelfolder:
        return gr.update(interactive=True)
    return gr.update(value=False, interactive=False)


def on_update_lora_meta_for_downloaded_model_btn_click(progress=gr.Progress()):
    model.update_downloaded_model()
    update_lora_meta(progress)
    return gr.update(visible=True)


def update_lora_meta(progress=gr.Progress()):

    for file_path, version_id in progress.tqdm(
        model.Downloaded_InfoPath.items(), desc="Create Lora metadata file for Downloaded Model"
    ):
        vfolder, vfile = os.path.split(file_path)
        basename, ext = os.path.splitext(vfile)
        basename, ext = os.path.splitext(basename)
        metafile = os.path.join(vfolder, f"{basename}.json")

        if not os.path.isfile(metafile):
            civitai.write_LoRa_metadata_by_version_id(metafile, str(version_id))
