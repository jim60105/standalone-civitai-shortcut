import os
import json
import shutil
import gradio as gr
import datetime

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda iterable, **kwargs: iterable

from . import util
from . import setting
from . import civitai
from . import classification

from PIL import Image

thumbnail_max_size = (400, 400)

# Use centralized HTTP client factory
from .http_client import get_http_client


def get_model_information(modelid: str = None, versionid: str = None, ver_index: int = None):
    # 현재 모델의 정보를 가져온다.
    model_info = None
    version_info = None

    if modelid:
        model_info = get_model_info(modelid)
        version_info = dict()
        if model_info:
            if not versionid and not ver_index:
                if "modelVersions" in model_info.keys():
                    version_info = model_info["modelVersions"][0]
                    if version_info["id"]:
                        versionid = version_info["id"]
            elif versionid:
                if "modelVersions" in model_info.keys():
                    for ver in model_info["modelVersions"]:
                        if versionid == ver["id"]:
                            version_info = ver
            else:
                if "modelVersions" in model_info.keys():
                    if len(model_info["modelVersions"]) > 0:
                        version_info = model_info["modelVersions"][ver_index]
                        if version_info["id"]:
                            versionid = version_info["id"]

    # 존재 하는지 판별하고 있다면 내용을 얻어낸다.
    if model_info and version_info:
        version_name = version_info["name"]
        model_type = model_info['type']
        model_basemodels = version_info["baseModel"]
        versions_list = list()
        for ver in model_info['modelVersions']:
            versions_list.append(ver['name'])
            # model_basemodels.append(ver['baseModel'])

        dhtml, triger, files = get_version_description(version_info, model_info)

        return (
            model_info,
            version_info,
            versionid,
            version_name,
            model_type,
            model_basemodels,
            versions_list,
            dhtml,
            triger,
            files,
        )
    return None, None, None, None, None, None, None, None, None, None


def get_version_description_gallery(modelid, version_info):
    #    modelid = None
    versionid = None
    ver_images = dict()

    if not modelid:
        return None

    if not version_info:
        return None

    # if "modelId" in version_info.keys():
    #     modelid = str(version_info['modelId'])

    if "id" in version_info.keys():
        versionid = str(version_info['id'])

    if "images" in version_info.keys():
        ver_images = version_info['images']

    images_url = list()

    try:
        for img_dict in ver_images:
            description_img = setting.get_image_url_to_shortcut_file(
                modelid, versionid, img_dict['url']
            )
            # util.printD(modelid)
            # util.printD(description_img)

            # NSFW filtering ....
            if setting.NSFW_filtering_enable:
                # if not setting.NSFW_level[ver["nsfw"]]:

                img_nsfw_level = 1

                if "nsfw" in img_dict.keys():
                    img_nsfw_level = setting.NSFW_levels.index(img_dict["nsfw"])

                if "nsfwLevel" in img_dict.keys():
                    img_nsfw_level = img_dict["nsfwLevel"] - 1
                    if img_nsfw_level < 0:
                        img_nsfw_level = 0

                if img_nsfw_level > setting.NSFW_levels.index(setting.NSFW_level_user):
                    description_img = setting.nsfw_disable_image

            if os.path.isfile(description_img):
                images_url.append(description_img)
    except Exception as e:
        # util.printD("error :" + e)
        return None

    return images_url


def get_version_description(version_info: dict, model_info: dict = None):
    output_html = ""
    output_training = ""

    files = []

    html_typepart = ""
    html_creatorpart = ""
    html_trainingpart = ""
    html_modelpart = ""
    html_versionpart = ""
    html_descpart = ""
    html_dnurlpart = ""
    html_imgpart = ""
    html_modelurlpart = ""
    html_model_tags = ""

    model_id = None

    if version_info:
        if 'modelId' in version_info:
            model_id = version_info['modelId']
            if not model_info:
                model_info = get_model_info(model_id)

    if version_info and model_info:

        html_typepart = f"<br><b>Type: {model_info['type']}</b>"
        model_url = civitai.Url_Page() + str(model_id)

        html_modelpart = (
            f'<br><b>Model: <a href="{model_url}" target="_blank">{model_info["name"]}</a></b>'
        )
        html_modelurlpart = (
            f'<br><b><a href="{model_url}" target="_blank">Civitai Hompage << Here</a></b><br>'
        )

        model_version_name = version_info['name']

        if 'trainedWords' in version_info:
            output_training = ", ".join(version_info['trainedWords'])
            html_trainingpart = f'<br><b>Training Tags:</b> {output_training}'

        model_uploader = model_info['creator']['username']
        html_creatorpart = f"<br><b>Uploaded by:</b> {model_uploader}"

        html_descpart = f"<br><b>Version : {version_info['name']}</b><br> BaseModel : {version_info['baseModel']}<br>"

        if 'description' in version_info:
            if version_info['description']:
                html_descpart = (
                    html_descpart + f"<b>Description</b><br>{version_info['description']}<br>"
                )

        if 'tags' in model_info:
            model_tags = model_info["tags"]
            if len(model_tags) > 0:
                html_model_tags = "<br><b>Model Tags:</b>"
                for tag in model_tags:
                    html_model_tags = html_model_tags + f"<b> [{tag}]</b>"

        if 'description' in model_info:
            if model_info['description']:
                html_descpart = (
                    html_descpart + f"<br><b>Description</b><br>{model_info['description']}<br>"
                )

        html_versionpart = f"<br><b>Version:</b> {model_version_name}"

        if 'files' in version_info:
            for file in version_info['files']:
                files.append(file)
                html_dnurlpart = (
                    html_dnurlpart
                    + f"<br><a href={file['downloadUrl']}><b>Download << Here</b></a>"
                )

        output_html = (
            html_typepart
            + html_modelpart
            + html_versionpart
            + html_creatorpart
            + html_trainingpart
            + "<br>"
            + html_model_tags
            + "<br>"
            + html_modelurlpart
            + html_dnurlpart
            + "<br>"
            + html_descpart
            + "<br>"
            + html_imgpart
        )

        return output_html, output_training, files

    return "", None, None


def sort_shortcut_by_value(ISC, key, reverse=False):
    sorted_data = sorted(ISC.items(), key=lambda x: x[1][key], reverse=reverse)
    return dict(sorted_data)


def sort_shortcut_by_modelid(ISC, reverse=False):
    sorted_data = {}
    for key in sorted(ISC.keys(), reverse=reverse):
        sorted_data[key] = ISC[key]
    return sorted_data


def get_tags():
    ISC = load()
    if not ISC:
        return

    result = []

    for item in ISC.values():
        name_values = set(tag['name'] for tag in item['tags'])
        result.extend(name_values)

    result = list(set(result))
    # util.printD(f"{len(result)}:{result}")
    return result


# 현재 소유한 버전에서 최신 버전을 얻는다.
def get_latest_version_info_by_model_id(id: str) -> dict:

    model_info = get_model_info(id)
    if not model_info:
        return

    if "modelVersions" not in model_info.keys():
        return

    def_version = model_info["modelVersions"][0]
    if not def_version:
        return

    if "id" not in def_version.keys():
        return

    return def_version


def get_model_filenames(modelid: str):

    model_info = get_model_info(modelid)
    if not model_info:
        return None

    filenames = []

    if "modelVersions" in model_info.keys():
        for ver in model_info["modelVersions"]:
            for ver_file in ver["files"]:
                filenames.append(ver_file["name"])

    return filenames


def is_baseModel(modelid: str, baseModels):

    model_info = get_model_info(modelid)
    if not model_info:
        return None

    if "modelVersions" in model_info.keys():
        for ver in model_info["modelVersions"]:
            try:
                # util.printD(ver["baseModel"])
                if ver["baseModel"] in baseModels:
                    return True
            except:
                pass

    return False


def get_model_info(modelid: str):
    if not modelid:
        return
    contents = None
    model_path = os.path.join(
        setting.shortcut_info_folder, modelid, f"{modelid}{setting.info_suffix}{setting.info_ext}"
    )
    try:
        with open(model_path, 'r') as f:
            contents = json.load(f)

        if 'id' not in contents.keys():
            return None
    except:
        return None

    return contents


def get_version_info(modelid: str, versionid: str):

    model_info = get_model_info(modelid)
    if not model_info:
        return None

    if "modelVersions" in model_info.keys():
        for ver in model_info["modelVersions"]:
            if str(versionid) == str(ver["id"]):
                return ver
    return None


def get_version_images(modelid: str, versionid: str):

    version_info = get_version_info(modelid, versionid)
    if not version_info:
        return None

    if "images" in version_info.keys():
        return version_info["images"]

    return None


def get_version_image_id(filename):
    version_image, ext = os.path.splitext(filename)

    ids = version_image.split("-")

    if len(ids) > 1:
        return ids

    return None


# 모델에 해당하는 shortcut에서 note를 변경한다.
def update_shortcut_model_note(modelid, note):
    if modelid:
        ISC = load()
        try:
            ISC[str(modelid)]["note"] = str(note)
            save(ISC)
        except:
            pass


# 모델에 해당하는 shortcut에서 note를 가져온다
def get_shortcut_model_note(modelid):
    if modelid:
        ISC = load()
        try:
            return ISC[str(modelid)]["note"]
        except:
            pass
    return None


# 모델에 해당하는 shortcut 을 가져온다
def get_shortcut_model(modelid):
    if modelid:
        ISC = load()
        try:
            return ISC[str(modelid)]
        except:
            pass
    return None


# 모델에 해당하는 shortcut 을 지운다
def delete_shortcut_model(modelid):
    if modelid:
        ISC = load()
        ISC = delete(ISC, modelid)
        save(ISC)


# 이중으로 하지 않으면 gr.Progress 오류가 난다 아마도 중첩에서 에러가 나는것 같다. progress.tqdm
# 솟컷을 업데이트하며 없으면 해당 아이디의 모델을 새로 생성한다.
def update_shortcut(modelid, progress=None):
    if modelid:
        note = None
        date = datetime.datetime.now()
        date = date.strftime("%Y-%m-%d %H:%M:%S")

        add_ISC = add(None, str(modelid), False, progress)
        ISC = load()
        if ISC:
            if str(modelid) in ISC:

                # 만일 civitai 에서 정보를 가져올수 없다면 기존것을 그대로 사용한다.
                if str(modelid) not in add_ISC:
                    add_ISC[str(modelid)] = ISC[str(modelid)]

                # 기존의 개별적으로 저장한 정보를 가져온다.
                if "note" in ISC[str(modelid)]:
                    note = ISC[str(modelid)]["note"]

                # 기존의 등록날짜 정보를 가져온다.
                if "date" in ISC[str(modelid)]:
                    if ISC[str(modelid)]["date"]:
                        date = ISC[str(modelid)]["date"]

                add_ISC[str(modelid)]["note"] = str(note)
                add_ISC[str(modelid)]["date"] = date

                if 'nsfw' not in add_ISC[str(modelid)].keys():
                    add_ISC[str(modelid)]["nsfw"] = False

            ISC.update(add_ISC)
        else:
            ISC = add_ISC
        save(ISC)


def update_shortcut_models(modelid_list: list, progress):
    if not modelid_list:
        return

    for k in progress.tqdm(modelid_list, desc="Updating Shortcut"):
        update_shortcut(k, progress)


def update_shortcut_informations(modelid_list: list, progress):
    if not modelid_list:
        return

    # shortcut 의 데이터만 새로 갱신한다.
    # for modelid in progress.tqdm(modelid_list, desc="Updating Shortcut Information"):
    #     write_model_information(modelid, False, progress)

    for modelid in progress.tqdm(modelid_list, desc="Updating Models Information"):
        if modelid:
            note = None
            date = datetime.datetime.now()
            date = date.strftime("%Y-%m-%d %H:%M:%S")
            add_ISC = add(None, str(modelid), False, progress)

            ISC = load()

            if str(modelid) in ISC:

                # 만일 civitai 에서 정보를 가져올수 없다면 기존것을 그대로 사용한다.
                if str(modelid) not in add_ISC:
                    add_ISC[str(modelid)] = ISC[str(modelid)]

                # 개별적으로 저장한 정보를 가져온다.
                if "note" in ISC[str(modelid)]:
                    note = ISC[str(modelid)]["note"]

                # 기존의 등록날짜 정보를 가져온다.
                if "date" in ISC[str(modelid)]:
                    if ISC[str(modelid)]["date"]:
                        date = ISC[str(modelid)]["date"]

                add_ISC[str(modelid)]["note"] = str(note)
                add_ISC[str(modelid)]["date"] = date

                if 'nsfw' not in add_ISC[str(modelid)].keys():
                    add_ISC[str(modelid)]["nsfw"] = False

                # hot fix and delete model
                # civitiai 에서 제거된 모델때문임
                # tags 를 변경해줘야함
                # 이슈가 해결되면 제거할코드
                # ISC[str(modelid)]["tags"]=[]

            if ISC:
                ISC.update(add_ISC)
            else:
                ISC = add_ISC
            save(ISC)


def update_all_shortcut_informations(progress):
    preISC = load()
    if not preISC:
        return

    modelid_list = [k for k in preISC]
    update_shortcut_informations(modelid_list, progress)


def write_model_information(modelid: str, register_only_information=False, progress=None):
    """
    Write model information to local storage and optionally download images.

    Args:
        modelid: The model ID to process
        register_only_information: If True, skip image downloads
        progress: Progress callback for UI updates

    Returns:
        dict: Model information from Civitai API, or None if failed
    """
    util.printD(f"[ishortcut.write_model_information] Starting process for modelid: {modelid}")

    if not modelid:
        util.printD("[ishortcut.write_model_information] No modelid provided, aborting")
        return None

    # Fetch model information from Civitai API
    util.printD("[ishortcut.write_model_information] Fetching model info from Civitai API")
    model_info = civitai.get_model_info(modelid)

    if not model_info:
        util.printD(f"[ishortcut.write_model_information] Failed to get model info for {modelid}")
        return None

    util.printD("[ishortcut.write_model_information] Successfully fetched model info")

    # Process model versions and extract image information
    version_list = _extract_version_images(model_info, modelid)

    # Create model directory and save information
    model_path = _create_model_directory(modelid)
    if not model_path:
        return None

    if not _save_model_information(model_info, model_path, modelid):
        return None

    # Download images if requested
    if not register_only_information:
        _download_model_images(version_list, modelid, progress)
    else:
        util.printD(
            "[ishortcut.write_model_information] Skipping image downloads "
            "(register_only_information=True)"
        )

    util.printD(f"[ishortcut.write_model_information] Process completed successfully for {modelid}")
    return model_info


def _extract_version_images(model_info: dict, modelid: str) -> list:
    """
    Extract image information from model versions.

    Args:
        model_info: Model information from Civitai API
        modelid: Model ID for debug logging

    Returns:
        list: List of image lists for each version
    """
    util.printD(f"[ishortcut._extract_version_images] Processing versions for model {modelid}")
    version_list = []

    if "modelVersions" not in model_info:
        util.printD(f"[ishortcut._extract_version_images] No modelVersions found for {modelid}")
        return version_list

    version_count = len(model_info["modelVersions"])
    util.printD(f"[ishortcut._extract_version_images] Found {version_count} versions")

    for idx, version_info in enumerate(model_info["modelVersions"]):
        version_id = version_info.get('id')
        util.printD(
            f"[ishortcut._extract_version_images] Processing version "
            f"{idx+1}/{version_count}, ID: {version_id}"
        )

        if not version_id:
            util.printD(f"[ishortcut._extract_version_images] Version {idx+1} has no ID, skipping")
            continue

        if "images" not in version_info:
            util.printD(f"[ishortcut._extract_version_images] Version {version_id} has no images")
            continue

        image_list = _process_version_images(version_info["images"], version_id)
        if image_list:
            version_list.append(image_list)
            util.printD(
                f"[ishortcut._extract_version_images] Added {len(image_list)} images "
                f"for version {version_id}"
            )
        else:
            util.printD(
                f"[ishortcut._extract_version_images] No valid images found "
                f"for version {version_id}"
            )

    util.printD(
        f"[ishortcut._extract_version_images] Processed {len(version_list)} versions with images"
    )
    return version_list


def _process_version_images(images: list, version_id: str) -> list:
    """
    Process images for a specific version.

    Args:
        images: List of image data from API
        version_id: Version ID for this set of images

    Returns:
        list: List of [version_id, img_url] pairs
    """
    image_list = []
    image_count = len(images)
    util.printD(
        f"[ishortcut._process_version_images] Processing {image_count} images "
        f"for version {version_id}"
    )

    for idx, img in enumerate(images):
        if "url" not in img:
            util.printD(
                f"[ishortcut._process_version_images] Image {idx+1}/{image_count} "
                f"has no URL, skipping"
            )
            continue

        img_url = img["url"]

        # Use max width if available
        if "width" in img and img["width"]:
            original_url = img_url
            img_url = util.change_width_from_image_url(img_url, img["width"])
            util.printD(
                f"[ishortcut._process_version_images] Adjusted image URL width: "
                f"{original_url} -> {img_url}"
            )

        image_list.append([version_id, img_url])
        util.printD(
            f"[ishortcut._process_version_images] Added image {idx+1}/{image_count}: {img_url}"
        )

    return image_list


def _create_model_directory(modelid: str) -> str:
    """
    Create directory for model information storage.

    Args:
        modelid: Model ID to create directory for

    Returns:
        str: Path to created directory, or None if failed
    """
    util.printD(f"[ishortcut._create_model_directory] Creating directory for model {modelid}")

    try:
        model_path = os.path.join(setting.shortcut_info_folder, modelid)
        util.printD(f"[ishortcut._create_model_directory] Target path: {model_path}")

        if os.path.exists(model_path):
            util.printD("[ishortcut._create_model_directory] Directory already exists")
        else:
            os.makedirs(model_path)
            util.printD("[ishortcut._create_model_directory] Directory created successfully")

        return model_path

    except Exception as e:
        util.printD(f"[ishortcut._create_model_directory] Failed to create directory: {str(e)}")
        return None


def _save_model_information(model_info: dict, model_path: str, modelid: str) -> bool:
    """
    Save model information to JSON file.

    Args:
        model_info: Model information to save
        model_path: Directory path to save in
        modelid: Model ID for filename

    Returns:
        bool: True if successful, False otherwise
    """
    util.printD(f"[ishortcut._save_model_information] Saving model info for {modelid}")

    try:
        tmp_info_file = os.path.join(model_path, f"tmp{setting.info_suffix}{setting.info_ext}")
        model_info_file = os.path.join(
            model_path, f"{modelid}{setting.info_suffix}{setting.info_ext}"
        )

        util.printD(f"[ishortcut._save_model_information] Temp file: {tmp_info_file}")
        util.printD(f"[ishortcut._save_model_information] Final file: {model_info_file}")

        # Write to temporary file first for atomic operation
        with open(tmp_info_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(model_info, indent=4, ensure_ascii=False))

        # Atomically replace the target file
        os.replace(tmp_info_file, model_info_file)
        util.printD("[ishortcut._save_model_information] Model info saved successfully")
        return True

    except Exception as e:
        util.printD(f"[ishortcut._save_model_information] Failed to save model info: {str(e)}")
        return False


def _download_model_images(version_list: list, modelid: str, progress=None):
    """
    Download images for all model versions.

    Args:
        version_list: List of image lists for each version
        modelid: Model ID for debug logging
        progress: Progress callback for UI updates
    """
    if not version_list:
        util.printD(f"[ishortcut._download_model_images] No images to download for {modelid}")
        return

    util.printD(f"[ishortcut._download_model_images] Starting image downloads for model {modelid}")

    # Get HTTP client for downloads
    try:
        client = get_http_client()
        util.printD("[ishortcut._download_model_images] HTTP client obtained successfully")
    except Exception as e:
        util.printD(f"[ishortcut._download_model_images] Failed to get HTTP client: {str(e)}")
        return

    # Collect all images that need downloading
    all_images_to_download = _collect_images_to_download(version_list, modelid)

    if not all_images_to_download:
        util.printD(f"[ishortcut._download_model_images] No new images to download for {modelid}")
        return

    # Download images with progress tracking
    _perform_image_downloads(all_images_to_download, client, progress)
    util.printD(f"[ishortcut._download_model_images] Image downloads completed for {modelid}")


def _collect_images_to_download(version_list: list, modelid: str) -> list:
    """
    Collect images that need to be downloaded (don't already exist).

    Args:
        version_list: List of image lists for each version
        modelid: Model ID for debug logging

    Returns:
        list: List of (version_id, url, filepath) tuples to download
    """
    util.printD(f"[ishortcut._collect_images_to_download] Collecting images for {modelid}")
    all_images_to_download = []

    for version_idx, image_list in enumerate(version_list):
        util.printD(
            f"[ishortcut._collect_images_to_download] Processing version "
            f"{version_idx+1}/{len(version_list)}"
        )
        images_for_version = []

        for img_idx, (vid, url) in enumerate(image_list):
            description_img = setting.get_image_url_to_shortcut_file(modelid, vid, url)

            if os.path.exists(description_img):
                util.printD(
                    f"[ishortcut._collect_images_to_download] Image {img_idx+1} "
                    f"already exists: {description_img}"
                )
                continue

            images_for_version.append((vid, url, description_img))
            util.printD(
                f"[ishortcut._collect_images_to_download] Added image {img_idx+1} "
                f"for download: {url}"
            )

        # Apply per-version download limit
        if (
            setting.shortcut_max_download_image_per_version
            and len(images_for_version) > setting.shortcut_max_download_image_per_version
        ):

            original_count = len(images_for_version)
            images_for_version = images_for_version[
                : setting.shortcut_max_download_image_per_version
            ]
            util.printD(
                f"[ishortcut._collect_images_to_download] Limited images from "
                f"{original_count} to {len(images_for_version)} per version limit"
            )

        all_images_to_download.extend(images_for_version)

    util.printD(
        f"[ishortcut._collect_images_to_download] Total images to download: "
        f"{len(all_images_to_download)}"
    )
    return all_images_to_download


def _perform_image_downloads(all_images_to_download: list, client, progress=None):
    """
    Perform the actual image downloads with progress tracking.

    Args:
        all_images_to_download: List of (version_id, url, filepath) tuples
        client: HTTP client for downloads
        progress: Progress callback for UI updates
    """
    util.printD(
        f"[ishortcut._perform_image_downloads] Starting downloads for "
        f"{len(all_images_to_download)} images"
    )

    # Setup progress tracking
    iter_images = _setup_progress_tracking(all_images_to_download, progress)

    # Download each image
    success_count = 0
    for vid, url, description_img in iter_images:
        try:
            util.printD(
                f"[ishortcut._perform_image_downloads] Downloading: {url} -> {description_img}"
            )
            util.download_image_safe(url, description_img, client, show_error=True)
            success_count += 1
            util.printD(
                f"[ishortcut._perform_image_downloads] Successfully downloaded "
                f"image {success_count}"
            )
        except Exception as e:
            util.printD(f"[ishortcut._perform_image_downloads] Failed to download {url}: {str(e)}")

    util.printD(
        f"[ishortcut._perform_image_downloads] Downloads completed: "
        f"{success_count}/{len(all_images_to_download)} successful"
    )


def _setup_progress_tracking(all_images_to_download: list, progress=None):
    """
    Setup progress tracking for image downloads with connection keep-alive.

    Args:
        all_images_to_download: List of images to download
        progress: Progress callback

    Returns:
        Iterator with or without progress tracking
    """
    if progress is None:
        util.printD("[ishortcut._setup_progress_tracking] No progress callback provided")
        return all_images_to_download

    try:
        # Send initial progress signal to establish connection
        if hasattr(progress, 'progress'):
            progress.progress(0, desc="Preparing image downloads...")
        
        util.printD("[ishortcut._setup_progress_tracking] Setting up progress tracking")
        
        # Only use tqdm if we have images to download
        if hasattr(progress, 'tqdm') and all_images_to_download:
            return progress.tqdm(all_images_to_download, desc="downloading model images")
        else:
            return all_images_to_download
            
    except (IndexError, TypeError, AttributeError) as e:
        util.printD(
            f"[ishortcut._setup_progress_tracking] Failed to setup progress tracking: {str(e)}"
        )
        return all_images_to_download


def delete_model_information(modelid: str):
    if not modelid:
        return

    model_path = os.path.join(setting.shortcut_info_folder, modelid)
    if setting.shortcut_info_folder != model_path:
        if os.path.exists(model_path):
            shutil.rmtree(model_path)


def update_thumbnail_images(progress):
    preISC = load()
    if not preISC:
        return

    # nsfw_levels = setting.NSFW_levels #[nsfw_level for nsfw_level in setting.NSFW_level.keys()]

    for k, v in progress.tqdm(preISC.items(), desc="Update Shortcut's Thumbnails"):
        if v:
            # 사이트에서 최신 정보를 가져온다.
            version_info = civitai.get_latest_version_info_by_model_id(v['id'])
            if not version_info:
                continue

            if 'images' not in version_info.keys():
                continue

            # if len(version_info['images']) > 0:
            #     v['imageurl'] = version_info['images'][0]['url']
            #     download_thumbnail_image(v['id'], v['imageurl'])

            # nsfw 검색해서 최대한 건전한 이미지를 골라낸다.
            if len(version_info["images"]) > 0:
                cur_nsfw_level = len(setting.NSFW_levels)
                def_image = None
                for img_dict in version_info["images"]:

                    img_nsfw_level = 1

                    if "nsfw" in img_dict.keys():
                        img_nsfw_level = setting.NSFW_levels.index(img_dict["nsfw"])

                    if "nsfwLevel" in img_dict.keys():
                        img_nsfw_level = img_dict["nsfwLevel"] - 1
                        if img_nsfw_level < 0:
                            img_nsfw_level = 0

                    if img_nsfw_level < cur_nsfw_level:
                        cur_nsfw_level = img_nsfw_level
                        def_image = img_dict["url"]

                if not def_image:
                    def_image = version_info["images"][0]["url"]

                v['imageurl'] = def_image
                download_thumbnail_image(v['id'], v['imageurl'])

    # 중간에 변동이 있을수 있으므로 병합한다.
    ISC = load()
    if ISC:
        ISC.update(preISC)
    else:
        ISC = preISC
    save(ISC)


def get_list(shortcut_types=None) -> str:

    ISC = load()
    if not ISC:
        return

    tmp_types = list()
    if shortcut_types:
        for sc_type in shortcut_types:
            try:
                tmp_types.append(setting.ui_typenames[sc_type])
            except:
                pass

    shotcutlist = list()
    for k, v in ISC.items():
        # util.printD(ISC[k])
        if v:
            if tmp_types:
                if v['type'] in tmp_types:
                    shotcutlist.append(setting.set_shortcutname(v['name'], v['id']))
            else:
                shotcutlist.append(setting.set_shortcutname(v['name'], v['id']))

    return shotcutlist


def get_image_list(
    shortcut_types=None, search=None, shortcut_basemodels=None, shortcut_classification=None
) -> str:

    ISC = load()
    if not ISC:
        return

    result_list = list()

    keys, tags, notes = util.get_search_keyword(search)
    # util.printD(f"keys:{keys} ,tags:{tags},notes:{notes}")

    # classification # and 연산으로 변경한다.
    if shortcut_classification:
        clfs_list = list()
        CISC = classification.load()
        if CISC:
            for name in shortcut_classification:
                name_list = classification.get_shortcut_list(CISC, name)
                if name_list:
                    if len(clfs_list) > 0:
                        clfs_list = list(set(clfs_list) & set(name_list))
                    else:
                        clfs_list = name_list
                else:
                    clfs_list = list()
                    # 결과가 없다면 교집합으로 나올수 있는것이 없으므로
                    break

            clfs_list = list(set(clfs_list))

        if len(clfs_list) > 0:
            for mid in clfs_list:
                if str(mid) in ISC.keys():
                    result_list.append(ISC[str(mid)])
    else:
        result_list = ISC.values()

    # filtering type
    tmp_types = list()
    if shortcut_types:
        for sc_type in shortcut_types:
            try:
                tmp_types.append(setting.ui_typenames[sc_type])
            except:
                pass

    if tmp_types:
        result_list = [v for v in result_list if v['type'] in tmp_types]

    # filtering key
    if keys:
        key_list = list()
        for v in result_list:
            if v:
                for key in keys:
                    if key in v['name'].lower():
                        key_list.append(v)
                        break
        result_list = key_list

    # filtering tags
    if tags:
        tags_list = list()
        for v in result_list:
            if v:
                if "tags" not in v.keys():
                    continue
                # v_tags = [tag["name"].lower() for tag in v["tags"]]
                v_tags = [tag.lower() for tag in v["tags"]]
                common_tags = set(v_tags) & set(tags)
                if common_tags:
                    tags_list.append(v)
        result_list = tags_list

    # filtering personal note key
    if notes:
        note_list = list()
        for v in result_list:
            if v:
                if "note" not in v.keys():
                    continue

                if not v['note']:
                    continue

                for note in notes:
                    if note in v['note'].lower():
                        note_list.append(v)
                        break
        result_list = note_list

    # basemodel 검색
    tmp_basemodels = list()
    if shortcut_basemodels:
        tmp_basemodels.extend(shortcut_basemodels)
        result_list = [v for v in result_list if is_baseModel(str(v['id']), tmp_basemodels)]

    # filename검색
    # if filenames:
    #     filenames_list = list()
    #     for v in result_list:
    #         if v:
    #             if "id" not in v.keys():
    #                 continue

    #             v_filenames = get_model_filenames(v["id"])
    #             common_filenames = set(v_filenames) & set(filenames)
    #             if common_filenames:
    #                 filenames_list.append(v)
    #     result_list = filenames_list

    return result_list


def create_thumbnail(model_id, input_image_path):
    global thumbnail_max_size

    if not model_id:
        return False

    thumbnail_path = os.path.join(
        setting.shortcut_thumbnail_folder, f"{model_id}{setting.preview_image_ext}"
    )
    # shutil.copy(input_image_path, thumbnail_path)
    try:
        with Image.open(input_image_path) as image:
            image.thumbnail(thumbnail_max_size)
            image.save(thumbnail_path)
    except Exception as e:
        return False

    return True


def delete_thumbnail_image(model_id):
    if is_sc_image(model_id):
        try:
            os.remove(
                os.path.join(
                    setting.shortcut_thumbnail_folder, f"{model_id}{setting.preview_image_ext}"
                )
            )
        except:
            return


def download_thumbnail_image(model_id, url):
    """Download and generate thumbnail for a shortcut image."""
    if not model_id or not url:
        return False

    os.makedirs(setting.shortcut_thumbnail_folder, exist_ok=True)
    thumbnail_path = os.path.join(
        setting.shortcut_thumbnail_folder, f"{model_id}{setting.preview_image_ext}"
    )
    client = get_http_client()
    if not util.download_image_safe(url, thumbnail_path, client, show_error=False):
        return False
    try:
        with Image.open(thumbnail_path) as image:
            image.thumbnail(thumbnail_max_size)
            image.save(thumbnail_path)
    except Exception as e:
        util.printD(f"[ishortcut] Thumbnail generation failed for {thumbnail_path}: {e}")
    return True


# 섬네일이 있는지 체크한다.
def is_sc_image(model_id):
    if not model_id:
        return False

    if os.path.isfile(
        os.path.join(setting.shortcut_thumbnail_folder, f"{model_id}{setting.preview_image_ext}")
    ):
        return True

    return False


def add(ISC: dict, model_id, register_information_only=False, progress=None) -> dict:

    if not model_id:
        return ISC

    if not ISC:
        ISC = dict()

    model_info = write_model_information(model_id, register_information_only, progress)

    def_id = None
    def_image = None

    if model_info:
        filenames = list()

        if "modelVersions" in model_info.keys() and len(model_info["modelVersions"]) > 0:
            def_version = model_info["modelVersions"][0]
            def_id = def_version['id']

            if 'images' in def_version.keys():
                # if len(def_version["images"]) > 0:
                #     def_image = def_version["images"][0]["url"]

                # nsfw 검색해서 최대한 건전한 이미지를 골라낸다.
                if len(def_version["images"]) > 0:
                    # nsfw_levels = [nsfw_level for nsfw_level in setting.NSFW_level.keys()]
                    cur_nsfw_level = len(setting.NSFW_levels)
                    def_image = None
                    for img_dict in def_version["images"]:

                        img_nsfw_level = 1

                        if "nsfw" in img_dict.keys():
                            img_nsfw_level = setting.NSFW_levels.index(img_dict["nsfw"])

                        if "nsfwLevel" in img_dict.keys():
                            img_nsfw_level = img_dict["nsfwLevel"] - 1
                            if img_nsfw_level < 0:
                                img_nsfw_level = 0

                        if img_nsfw_level < cur_nsfw_level:
                            cur_nsfw_level = img_nsfw_level
                            def_image = img_dict["url"]

                    if not def_image:
                        def_image = def_version["images"][0]["url"]

            # 현재 모델의 모델 파일 정보를 추출한다.
            # for ver in model_info["modelVersions"]:
            #     for ver_file in ver["files"]:
            #         filenames.append(ver_file["name"])

        # 모델정보가 바뀌어도 피해를 줄이기 위함
        tags = list()
        try:
            if model_info['tags']:
                tags = [tag for tag in model_info['tags']]
        except:
            pass

        date = datetime.datetime.now()
        ISC[str(model_id)] = {
            "id": model_info['id'],
            "type": model_info['type'],
            "name": model_info['name'],
            "tags": tags,
            "nsfw": model_info['nsfw'],
            "url": f"{civitai.Url_ModelId()}{model_id}",
            "versionid": def_id,
            "imageurl": def_image,
            "note": "",
            "date": date.strftime("%Y-%m-%d %H:%M:%S"),
        }

        cis_to_file(ISC[str(model_id)])

        # 섬네일이 없을때만 새로 다운받는다.
        if not is_sc_image(model_id):
            download_thumbnail_image(model_id, def_image)

        # download_thumbnail_image(model_id, def_image)

    return ISC


def delete(ISC: dict, model_id) -> dict:
    if not model_id:
        return

    if not ISC:
        return

    cis = ISC.pop(str(model_id), None)

    cis_to_file(cis)

    delete_thumbnail_image(model_id)

    delete_model_information(model_id)

    return ISC


def cis_to_file(cis):
    if not cis:
        return

    if "name" in cis.keys() and 'id' in cis.keys():
        backup_cis(cis['name'], f"{civitai.Url_Page()}{cis['id']}")
        # if not os.path.exists(setting.shortcut_save_folder):
        #     os.makedirs(setting.shortcut_save_folder)
        # util.write_InternetShortcut(os.path.join(setting.shortcut_save_folder,f"{util.replace_filename(cis['name'])}.url"),f"{civitai.Url_Page()}{cis['id']}")


def backup_cis(name, url):

    if not name or not url:
        return

    backup_dict = None
    try:
        with open(setting.shortcut_civitai_internet_shortcut_url, 'r') as f:
            backup_dict = json.load(f)
    except:
        backup_dict = dict()

    backup_dict[f"url={url}"] = name

    try:
        with open(setting.shortcut_civitai_internet_shortcut_url, 'w') as f:
            json.dump(backup_dict, f, indent=4)
    except Exception as e:
        util.printD("Error when writing file:" + setting.shortcut_civitai_internet_shortcut_url)
        pass


def save(ISC: dict):
    # print("Saving Civitai Internet Shortcut to: " + setting.shortcut)

    output = ""

    # write to file
    try:
        with open(setting.shortcut, 'w') as f:
            json.dump(ISC, f, indent=4)
    except Exception as e:
        util.printD("Error when writing file:" + setting.shortcut)
        return output

    output = "Civitai Internet Shortcut saved to: " + setting.shortcut
    # util.printD(output)

    return output


def load() -> dict:
    # util.printD("Load Civitai Internet Shortcut from: " + setting.shortcut)

    if not os.path.isfile(setting.shortcut):
        util.printD("Unable to load the shortcut file. Starting with an empty file.")
        save({})
        return

    json_data = None
    try:
        with open(setting.shortcut, 'r') as f:
            json_data = json.load(f)
    except:
        return None

    # check error
    if not json_data:
        util.printD("There are no registered shortcuts.")
        return None

    # check for new key
    return json_data


def _get_preview_image_url(model_info) -> str:
    """Extract preview image URL from model info."""
    try:
        # Try to get from model versions
        if 'modelVersions' in model_info and model_info['modelVersions']:
            for version in model_info['modelVersions']:
                if 'images' in version and version['images']:
                    for image in version['images']:
                        url = image.get('url')
                        if url:
                            return url
        # Try to get from direct images
        if 'images' in model_info and model_info['images']:
            for image in model_info['images']:
                url = image.get('url')
                if url:
                    return url
        return None
    except Exception as e:
        util.printD(f"[ishortcut] Error extracting preview URL: {e}")
        return None


def _get_preview_image_path(model_info) -> str:
    """Generate local path for preview image."""
    try:
        model_id = model_info.get('id')
        if not model_id:
            return None
        preview_dir = setting.shortcut_thumbnail_folder
        os.makedirs(preview_dir, exist_ok=True)
        filename = f"model_{model_id}_preview.jpg"
        return os.path.join(preview_dir, filename)
    except Exception as e:
        util.printD(f"[ishortcut] Error generating image path: {e}")
        return None


def download_model_preview_image_by_model_info(model_info):
    """Download model preview image with improved error handling."""
    if not model_info:
        util.printD("[ishortcut] download_model_preview_image_by_model_info: model_info is None")
        return None
    model_id = model_info.get('id')
    if not model_id:
        util.printD("[ishortcut] download_model_preview_image_by_model_info: model_id not found")
        return None
    util.printD(f"[ishortcut] Downloading preview image for model: {model_id}")
    preview_url = _get_preview_image_url(model_info)
    if not preview_url:
        util.printD("[ishortcut] No preview image URL found")
        return None
    image_path = _get_preview_image_path(model_info)
    if not image_path:
        util.printD("[ishortcut] Failed to generate image path")
        return None
    if os.path.exists(image_path):
        util.printD(f"[ishortcut] Preview image already exists: {image_path}")
        return image_path
    client = get_http_client()
    success = util.download_image_safe(preview_url, image_path, client, show_error=False)
    if success:
        util.printD(f"[ishortcut] Successfully downloaded preview image: {image_path}")
        return image_path
    else:
        util.printD(f"[ishortcut] Failed to download preview image: {preview_url}")
        return None


def get_preview_image_by_model_info(model_info):
    """Get preview image, download if not exists."""
    if not model_info:
        util.printD("[ishortcut] get_preview_image_by_model_info: model_info is None")
        return setting.no_card_preview_image
    image_path = _get_preview_image_path(model_info)
    if image_path and os.path.exists(image_path):
        util.printD(f"[ishortcut] Using existing preview image: {image_path}")
        return image_path
    downloaded_path = download_model_preview_image_by_model_info(model_info)
    if downloaded_path:
        return downloaded_path
    util.printD("[ishortcut] Using fallback preview image")
    return setting.no_card_preview_image
