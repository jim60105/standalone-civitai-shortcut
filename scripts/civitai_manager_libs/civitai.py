import os
import json
from . import util
from . import setting
from .logging_config import get_logger

logger = get_logger(__name__)

# Module-level HTTP client instance (use centralized factory)
from .http_client import get_http_client


# Set the URL for the API endpoint

url_dict = {
    "modelPage": "https://civitai.com/models/",
    "modelId": "https://civitai.com/api/v1/models/",
    "modelVersionId": "https://civitai.com/api/v1/model-versions/",
    "modelHash": "https://civitai.com/api/v1/model-versions/by-hash/",
    "imagePage": "https://civitai.com/api/v1/images",
}


def Url_Page():
    return url_dict["modelPage"]


def Url_ModelId():
    return url_dict["modelId"]


def Url_VersionId():
    return url_dict["modelVersionId"]


def Url_Hash():
    return url_dict["modelHash"]


def Url_ImagePage():
    return url_dict["imagePage"]


def request_models(api_url=None):
    """Request models from Civitai API with robust error handling."""
    logger.debug(f"request_models() called with api_url: {api_url}")
    if not api_url:
        logger.debug("request_models: api_url is None or empty")
        return {'items': [], 'metadata': {}}
    client = get_http_client()
    data = client.get_json(api_url)
    if data is None:
        logger.warning(f"request_models: Failed to get data from {api_url}")
        return {'items': [], 'metadata': {}}
    logger.debug(f"Response data loaded successfully from {api_url}")
    return data


def get_model_info(id: str) -> dict:
    """Get model information by model ID."""
    util.printD(f"[civitai] get_model_info() called with id: {id}")
    if not id:
        util.printD("[civitai] get_model_info: id is None or empty")
        return None
    url = Url_ModelId() + str(id)
    util.printD(f"[civitai] Requesting model info from URL: {url}")
    client = get_http_client()
    content = client.get_json(url)
    if content is None:
        util.printD(f"[civitai] get_model_info: Failed to get data for id {id}")
        return None
    if 'id' not in content:
        util.printD(f"[civitai] get_model_info: 'id' not in response content for id {id}")
        return None
    util.printD(f"[civitai] get_model_info: Successfully retrieved model info for id {id}")
    return content


# def get_model_info_by_version_id(version_id:str) -> dict:
#     if not version_id:
#         return

#     version_info = get_version_info_by_version_id(version_id)
#     return get_model_info_by_version_info(version_info)

# def get_model_info_by_version_info(version_info) -> dict:
#     if not version_info:
#         return
#     return get_model_info(version_info['modelId'])


def get_version_info_by_hash(hash_value) -> dict:
    """Get version information by hash value."""
    util.printD(f"[civitai] get_version_info_by_hash() called with hash: {hash_value}")
    if not hash_value:
        util.printD("[civitai] get_version_info_by_hash: hash is None or empty")
        return None
    url = f"{Url_Hash()}{hash_value}"
    util.printD(f"[civitai] Requesting version info by hash from URL: {url}")
    client = get_http_client()
    content = client.get_json(url)
    if content is None:
        logger.warning(f"get_version_info_by_hash: Failed to get data for hash {hash_value}")
        return None
    if 'id' not in content:
        logger.warning(
            f"get_version_info_by_hash: 'id' not in response content for hash {hash_value}"
        )
        return None
    logger.debug(
        f"get_version_info_by_hash: Successfully retrieved version info for hash {hash_value}"
    )
    return content


def get_version_info_by_version_id(version_id: str) -> dict:
    """Get version information by version ID."""
    logger.debug(f"get_version_info_by_version_id() called with version_id: {version_id}")
    if not version_id:
        logger.debug("get_version_info_by_version_id: version_id is None or empty")
        return None
    url = Url_VersionId() + str(version_id)
    logger.debug(f"Requesting version info from URL: {url}")
    client = get_http_client()
    content = client.get_json(url)
    if content is None:
        logger.warning(
            f"get_version_info_by_version_id: Failed to get data for version_id {version_id}"
        )
        return None
    if 'id' not in content:
        logger.warning(
            f"get_version_info_by_version_id: 'id' not in response content for "
            f"version_id {version_id}"
        )
        return None
    logger.debug(
        f"get_version_info_by_version_id: Successfully retrieved version info for "
        f"version_id {version_id}"
    )
    return content


def get_latest_version_info_by_model_id(id: str) -> dict:
    logger.debug(f"get_latest_version_info_by_model_id() called with id: {id}")
    model_info = get_model_info(id)
    if not model_info:
        util.printD(
            f"[civitai] get_latest_version_info_by_model_id: model_info not found for id {id}"
        )
        return None
    if "modelVersions" not in model_info:
        util.printD(
            f"[civitai] get_latest_version_info_by_model_id: 'modelVersions' not in model_info for "
            f"id {id}"
        )
        return None
    def_version = model_info["modelVersions"][0]
    if not def_version:
        util.printD(
            f"[civitai] get_latest_version_info_by_model_id: modelVersions[0] is None for id {id}"
        )
        return None
    if "id" not in def_version:
        util.printD(
            f"[civitai] get_latest_version_info_by_model_id: 'id' not in def_version for id {id}"
        )
        return None
    version_id = def_version["id"]
    util.printD(f"[civitai] get_latest_version_info_by_model_id: latest version_id is {version_id}")
    version_info = get_version_info_by_version_id(str(version_id))
    util.printD(
        f"[civitai] get_latest_version_info_by_model_id: version_info fetched for version_id "
        f"{version_id}"
    )
    return version_info


def get_version_id_by_version_name(model_id: str, name: str) -> str:
    util.printD(
        f"[civitai] get_version_id_by_version_name() called with model_id: {model_id}, name: {name}"
    )
    version_id = None
    if not model_id:
        util.printD("[civitai] get_version_id_by_version_name: model_id is None or empty")
        return None
    model_info = get_model_info(model_id)
    if not model_info:
        util.printD(
            f"[civitai] get_version_id_by_version_name: model_info not found for model_id "
            f"{model_id}"
        )
        return None
    if "modelVersions" not in model_info:
        util.printD(
            f"[civitai] get_version_id_by_version_name: 'modelVersions' not in model_info for "
            f"model_id {model_id}"
        )
        return None
    for version in model_info['modelVersions']:
        util.printD(f"[civitai] Checking version name: {version['name']}")
        if version['name'] == name:
            version_id = version['id']
            util.printD(f"[civitai] Found version_id: {version_id} for name: {name}")
            break
    if version_id is None:
        util.printD(
            f"[civitai] get_version_id_by_version_name: No version_id found for name {name}"
        )
    return version_id


def get_files_by_version_info(version_info: dict) -> dict:
    util.printD("[civitai] get_files_by_version_info() called")
    download_files = {}
    if not version_info:
        util.printD("[civitai] get_files_by_version_info: version_info is None or empty")
        return None
    for file in version_info['files']:
        util.printD(f"[civitai] Adding file id: {file['id']} to download_files")
        download_files[str(file['id'])] = file
    util.printD(f"[civitai] get_files_by_version_info: {len(download_files)} files found")
    return download_files


def get_files_by_version_id(version_id=None) -> dict:
    util.printD(f"[civitai] get_files_by_version_id() called with version_id: {version_id}")
    if not version_id:
        util.printD("[civitai] get_files_by_version_id: version_id is None or empty")
        return None
    version_info = get_version_info_by_version_id(version_id)
    return get_files_by_version_info(version_info)


def get_primary_file_by_version_info(version_info: dict) -> dict:
    util.printD("[civitai] get_primary_file_by_version_info() called")
    if not version_info:
        util.printD("[civitai] get_primary_file_by_version_info: version_info is None or empty")
        return None
    for file in version_info['files']:
        if 'primary' in file:
            util.printD(f"[civitai] Checking file id: {file['id']} primary: {file['primary']}")
            if file['primary']:
                util.printD(f"[civitai] Found primary file id: {file['id']}")
                return file
    util.printD("[civitai] get_primary_file_by_version_info: No primary file found")
    return None


def get_primary_file_by_version_id(version_id=None) -> dict:
    util.printD(f"[civitai] get_primary_file_by_version_id() called with version_id: {version_id}")
    if not version_id:
        util.printD("[civitai] get_primary_file_by_version_id: version_id is None or empty")
        return None
    version_info = get_version_info_by_version_id(version_id)
    return get_primary_file_by_version_info(version_info)


def get_images_by_version_id(version_id=None) -> dict:
    util.printD(f"[civitai] get_images_by_version_id() called with version_id: {version_id}")
    if not version_id:
        util.printD("[civitai] get_images_by_version_id: version_id is None or empty")
        return None
    version_info = get_version_info_by_version_id(version_id)
    return get_images_by_version_info(version_info)


def get_images_by_version_info(version_info: dict) -> dict:
    util.printD("[civitai] get_images_by_version_info() called")
    if not version_info:
        util.printD("[civitai] get_images_by_version_info: version_info is None or empty")
        return None
    return version_info["images"]


def get_triger_by_version_info(version_info: dict) -> str:
    util.printD("[civitai] get_triger_by_version_info() called")
    if not version_info:
        util.printD("[civitai] get_triger_by_version_info: version_info is None or empty")
        return None
    try:
        triger_words = ", ".join(version_info['trainedWords'])
        util.printD(f"[civitai] Trained words: {triger_words}")
        if len(triger_words.strip()) > 0:
            return triger_words
    except Exception as e:
        util.printD(f"[civitai] Exception in get_triger_by_version_info: {e}")
    return None


def get_triger_by_version_id(version_id=None) -> str:
    util.printD(f"[civitai] get_triger_by_version_id() called with version_id: {version_id}")
    if not version_id:
        util.printD("[civitai] get_triger_by_version_id: version_id is None or empty")
        return None
    version_info = get_version_info_by_version_id(version_id)
    return get_triger_by_version_info(version_info)


def write_model_info(file, model_info: dict) -> bool:
    util.printD(f"[civitai] write_model_info() called with file: {file}")
    if not model_info:
        util.printD("[civitai] write_model_info: model_info is None or empty")
        return False
    try:
        with open(file, 'w') as f:
            f.write(json.dumps(model_info, indent=4))
        util.printD(f"[civitai] write_model_info: Successfully wrote model info to {file}")
    except Exception as e:
        util.printD(f"[civitai] Exception in write_model_info: {e}")
        return False
    return True


def write_version_info(file, version_info: dict) -> bool:
    util.printD(f"[civitai] write_version_info() called with file: {file}")
    if not version_info:
        util.printD("[civitai] write_version_info: version_info is None or empty")
        return False
    try:
        with open(file, 'w') as f:
            f.write(json.dumps(version_info, indent=4))
        util.printD(f"[civitai] write_version_info: Successfully wrote version info to {file}")
    except Exception as e:
        util.printD(f"[civitai] Exception in write_version_info: {e}")
        return False
    return True


def write_triger_words_by_version_id(file, version_id: str) -> bool:
    util.printD(
        f"[civitai] write_triger_words_by_version_id() called with file: {file}, "
        f"version_id: {version_id}"
    )
    if not version_id:
        util.printD("[civitai] write_triger_words_by_version_id: version_id is None or empty")
        return False
    version_info = get_version_info_by_version_id(version_id)
    return write_triger_words(file, version_info)


def write_triger_words(file, version_info: dict) -> bool:
    util.printD(f"[civitai] write_triger_words() called with file: {file}")
    if not version_info:
        util.printD("[civitai] write_triger_words: version_info is None or empty")
        return False
    triger_words = get_triger_by_version_info(version_info)
    if not triger_words:
        util.printD("[civitai] write_triger_words: triger_words is None or empty")
        return False
    try:
        with open(file, 'w') as f:
            f.write(triger_words)
        util.printD(f"[civitai] write_triger_words: Successfully wrote trigger words to {file}")
    except Exception as e:
        util.printD(f"[civitai] Exception in write_triger_words: {e}")
        return False
    return True


def write_LoRa_metadata_by_version_id(file, version_id: str) -> bool:
    util.printD(
        f"[civitai] write_LoRa_metadata_by_version_id() called with file: {file}, "
        f"version_id: {version_id}"
    )
    if not version_id:
        util.printD("[civitai] write_LoRa_metadata_by_version_id: version_id is None or empty")
        return False
    version_info = get_version_info_by_version_id(version_id)
    return write_LoRa_metadata(file, version_info)


def write_LoRa_metadata(filepath, version_info) -> bool:
    util.printD(f"[civitai] write_LoRa_metadata() called with filepath: {filepath}")
    LoRa_metadata = {
        "description": None,
        "sd version": None,
        "activation text": None,
        "preferred weight": 0,
        "notes": None,
    }
    if not version_info:
        util.printD("[civitai] write_LoRa_metadata: version_info is None or empty")
        return False
    if os.path.isfile(filepath):
        util.printD(f"[civitai] write_LoRa_metadata: File already exists: {filepath}")
        return False
    if "description" in version_info:
        LoRa_metadata['description'] = version_info["description"]
    if "baseModel" in version_info:
        base_model = version_info["baseModel"]
        if base_model in setting.model_basemodels:
            LoRa_metadata['sd version'] = setting.model_basemodels[base_model]
        else:
            LoRa_metadata['sd version'] = 'Unknown'
    if "trainedWords" in version_info:
        LoRa_metadata['activation text'] = ", ".join(version_info['trainedWords'])
    notes = []
    if "modelId" in version_info:
        notes.append(f"{url_dict['modelPage']}{version_info['modelId']}")
    if "downloadUrl" in version_info:
        notes.append(version_info['downloadUrl'])
    if notes:
        LoRa_metadata['notes'] = ", ".join(notes)
    try:
        with open(filepath, 'w') as f:
            json.dump(LoRa_metadata, f, indent=4)
        util.printD(
            f"[civitai] write_LoRa_metadata: Successfully wrote LoRa metadata to {filepath}"
        )
    except Exception as e:
        util.printD(f"[civitai] Exception in write_LoRa_metadata: {e}")
        return False
    return True
