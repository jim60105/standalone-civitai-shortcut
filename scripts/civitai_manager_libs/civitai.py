import os
import json
from typing import Optional, Dict, Any
from . import settings
from .logging_config import get_logger

logger = get_logger(__name__)

# Module-level HTTP client instance (use centralized factory)
from .http_client import get_http_client
from .error_handler import with_error_handling
from .exceptions import (
    NetworkError,
    APIError,
    FileOperationError,
    CivitaiShortcutError,
    ValidationError,
    HTTPError,
    ModelNotAccessibleError,
    ModelNotFoundError,
)


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


@with_error_handling(
    fallback_value={'items': [], 'metadata': {}},
    exception_types=(NetworkError, APIError),
    retry_count=2,
    retry_delay=1.0,
    user_message="Failed to request models",
)
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


def get_model_info(model_id: str) -> Optional[Dict[str, Any]]:
    """Get model information by model ID."""
    logger.debug(f"get_model_info() called with model_id: {model_id}")
    if not model_id:
        logger.debug("get_model_info: model_id is None or empty")
        return None

    url = Url_ModelId() + str(model_id)
    logger.debug(f"Requesting model info from URL: {url}")
    client = get_http_client()

    # Use the unified client interface if available
    if hasattr(client, "get_json"):
        content = client.get_json(url)
        if content is None or "id" not in content:
            raise ModelNotFoundError(f"Model {model_id} not found", model_id=model_id)
    else:
        # Handle direct session usage for compatibility
        try:
            response = client.session.get(url, timeout=setting.http_timeout)
            client._handle_response_error(response)
            content = response.json()
        except HTTPError as e:
            if e.status_code == 404:
                raise ModelNotAccessibleError(
                    f"Model {model_id} is not accessible via API", model_id=model_id
                )
            raise APIError(
                f"Failed to retrieve model {model_id}: HTTP {e.status_code}",
                status_code=e.status_code,
                cause=e,
            )
        except Exception as e:
            raise APIError(
                f"Failed to retrieve model {model_id}: {e}",
                status_code=getattr(e, "status_code", None),
                cause=e,
            )

        if content is None or "id" not in content:
            raise ModelNotFoundError(f"Model {model_id} not found", model_id=model_id)

    logger.debug(f"get_model_info: Successfully retrieved model info for model_id {model_id}")
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


@with_error_handling(
    fallback_value=None,
    exception_types=(NetworkError, APIError),
    retry_count=2,
    retry_delay=1.0,
    user_message="Failed to get version info by hash",
)
def get_version_info_by_hash(hash_value) -> Optional[Dict[str, Any]]:
    """Get version information by hash value."""
    logger.debug(f"get_version_info_by_hash() called with hash: {hash_value}")
    if not hash_value:
        logger.debug("get_version_info_by_hash: hash is None or empty")
        return None
    url = f"{Url_Hash()}{hash_value}"
    logger.debug(f"Requesting version info by hash from URL: {url}")
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


@with_error_handling(
    fallback_value=None,
    exception_types=(NetworkError, APIError),
    retry_count=2,
    retry_delay=1.0,
    user_message="Failed to get version info by version ID",
)
def get_version_info_by_version_id(version_id: str) -> Optional[Dict[str, Any]]:
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


@with_error_handling(
    fallback_value=None,
    exception_types=(NetworkError, APIError),
    retry_count=2,
    retry_delay=1.0,
    user_message="Failed to get latest version info",
)
def get_latest_version_info_by_model_id(id: str) -> Optional[Dict[str, Any]]:
    logger.debug(f"get_latest_version_info_by_model_id() called with id: {id}")
    model_info = get_model_info(id)
    if not model_info:
        logger.debug(
            f"[civitai] get_latest_version_info_by_model_id: model_info not found for id {id}"
        )
        return None
    if "modelVersions" not in model_info:
        logger.debug(
            f"[civitai] get_latest_version_info_by_model_id: 'modelVersions' not in model_info for "
            f"id {id}"
        )
        return None
    def_version = model_info["modelVersions"][0]
    if not def_version:
        logger.debug(
            f"[civitai] get_latest_version_info_by_model_id: modelVersions[0] is None for id {id}"
        )
        return None
    if "id" not in def_version:
        logger.debug(
            f"[civitai] get_latest_version_info_by_model_id: 'id' not in def_version for id {id}"
        )
        return None
    version_id = def_version["id"]
    logger.debug(f" get_latest_version_info_by_model_id: latest version_id is {version_id}")
    version_info = get_version_info_by_version_id(str(version_id))
    logger.debug(
        f"[civitai] get_latest_version_info_by_model_id: version_info fetched for version_id "
        f"{version_id}"
    )
    return version_info


@with_error_handling(
    fallback_value=None,
    exception_types=(NetworkError, APIError, ValidationError),
    retry_count=1,
    retry_delay=1.0,
    user_message="Failed to get version ID by name",
)
def get_version_id_by_version_name(model_id: str, name: str) -> Optional[str]:
    logger.debug(
        f"[civitai] get_version_id_by_version_name() called with model_id: {model_id}, name: {name}"
    )
    version_id = None
    if not model_id:
        logger.debug(" get_version_id_by_version_name: model_id is None or empty")
        return None
    model_info = get_model_info(model_id)
    if not model_info:
        logger.debug(
            f"[civitai] get_version_id_by_version_name: model_info not found for model_id "
            f"{model_id}"
        )
        return None
    if "modelVersions" not in model_info:
        logger.debug(
            f"[civitai] get_version_id_by_version_name: 'modelVersions' not in model_info for "
            f"model_id {model_id}"
        )
        return None
    for version in model_info['modelVersions']:
        logger.debug(f" Checking version name: {version['name']}")
        if version['name'] == name:
            version_id = version['id']
            logger.debug(f" Found version_id: {version_id} for name: {name}")
            break
    if version_id is None:
        logger.debug(
            f"[civitai] get_version_id_by_version_name: No version_id found for name {name}"
        )
    return version_id


@with_error_handling(
    fallback_value=None,
    exception_types=(CivitaiShortcutError,),
    retry_count=0,
    user_message="Failed to get files by version info",
)
def get_files_by_version_info(version_info: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    logger.debug(" get_files_by_version_info() called")
    download_files = {}
    if not version_info:
        logger.debug(" get_files_by_version_info: version_info is None or empty")
        return None
    for file in version_info['files']:
        logger.debug(f" Adding file id: {file['id']} to download_files")
        download_files[str(file['id'])] = file
    logger.debug(f" get_files_by_version_info: {len(download_files)} files found")
    return download_files


@with_error_handling(
    fallback_value=None,
    exception_types=(CivitaiShortcutError,),
    retry_count=0,
    user_message="Failed to get files by version ID",
)
def get_files_by_version_id(version_id=None) -> Optional[Dict[str, Any]]:
    logger.debug(f" get_files_by_version_id() called with version_id: {version_id}")
    if not version_id:
        logger.debug(" get_files_by_version_id: version_id is None or empty")
        return None
    version_info = get_version_info_by_version_id(version_id)
    if not version_info:
        return None
    return get_files_by_version_info(version_info)


@with_error_handling(
    fallback_value=None,
    exception_types=(CivitaiShortcutError,),
    retry_count=0,
    user_message="Failed to get primary file by version info",
)
def get_primary_file_by_version_info(
    version_info: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    logger.debug(" get_primary_file_by_version_info() called")
    if not version_info:
        logger.debug(" get_primary_file_by_version_info: version_info is None or empty")
        return None
    for file in version_info['files']:
        if 'primary' in file:
            logger.debug(f" Checking file id: {file['id']} primary: {file['primary']}")
            if file['primary']:
                logger.debug(f" Found primary file id: {file['id']}")
                return file
    logger.debug(" get_primary_file_by_version_info: No primary file found")
    return None


@with_error_handling(
    fallback_value=None,
    exception_types=(CivitaiShortcutError,),
    retry_count=0,
    user_message="Failed to get primary file by version ID",
)
def get_primary_file_by_version_id(version_id=None) -> Optional[Dict[str, Any]]:
    logger.debug(f" get_primary_file_by_version_id() called with version_id: {version_id}")
    if not version_id:
        logger.debug(" get_primary_file_by_version_id: version_id is None or empty")
        return None
    version_info = get_version_info_by_version_id(version_id)
    if not version_info:
        return None
    return get_primary_file_by_version_info(version_info)


@with_error_handling(
    fallback_value=None,
    exception_types=(CivitaiShortcutError,),
    retry_count=0,
    user_message="Failed to get images by version ID",
)
def get_images_by_version_id(version_id=None) -> Optional[Dict[str, Any]]:
    logger.debug(f" get_images_by_version_id() called with version_id: {version_id}")
    if not version_id:
        logger.debug(" get_images_by_version_id: version_id is None or empty")
        return None
    version_info = get_version_info_by_version_id(version_id)
    if not version_info:
        return None
    return get_images_by_version_info(version_info)


@with_error_handling(
    fallback_value=None,
    exception_types=(CivitaiShortcutError,),
    retry_count=0,
    user_message="Failed to get images by version info",
)
def get_images_by_version_info(version_info: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    logger.debug(" get_images_by_version_info() called")
    if not version_info:
        logger.debug(" get_images_by_version_info: version_info is None or empty")
        return None
    return version_info["images"]


@with_error_handling(
    fallback_value=None,
    exception_types=(CivitaiShortcutError,),
    retry_count=0,
    user_message="Failed to get trigger words by version info",
)
def get_triger_by_version_info(version_info: Optional[Dict[str, Any]]) -> Optional[str]:
    logger.debug(" get_triger_by_version_info() called")
    if not version_info:
        logger.debug(" get_triger_by_version_info: version_info is None or empty")
        return None
    try:
        triger_words = ", ".join(version_info['trainedWords'])
        logger.debug(f" Trained words: {triger_words}")
        if len(triger_words.strip()) > 0:
            return triger_words
    except Exception as e:
        logger.error(f" Exception in get_triger_by_version_info: {e}")
    return None


@with_error_handling(
    fallback_value=None,
    exception_types=(CivitaiShortcutError,),
    retry_count=0,
    user_message="Failed to get trigger words by version ID",
)
def get_triger_by_version_id(version_id=None) -> Optional[str]:
    logger.debug(f" get_triger_by_version_id() called with version_id: {version_id}")
    if not version_id:
        logger.debug(" get_triger_by_version_id: version_id is None or empty")
        return None
    version_info = get_version_info_by_version_id(version_id)
    if not version_info:
        return None
    return get_triger_by_version_info(version_info)


@with_error_handling(
    fallback_value=False,
    exception_types=(FileOperationError,),
    retry_count=1,
    user_message="Failed to write model info",
)
def write_model_info(file, model_info: dict) -> bool:
    logger.debug(f" write_model_info() called with file: {file}")
    if not model_info:
        logger.debug(" write_model_info: model_info is None or empty")
        return False
    try:
        with open(file, 'w') as f:
            f.write(json.dumps(model_info, indent=4))
        logger.debug(f" write_model_info: Successfully wrote model info to {file}")
    except Exception as e:
        logger.error(f" Exception in write_model_info: {e}")
        return False
    return True


@with_error_handling(
    fallback_value=False,
    exception_types=(FileOperationError,),
    retry_count=1,
    user_message="Failed to write version info",
)
def write_version_info(file, version_info: dict) -> bool:
    logger.debug(f" write_version_info() called with file: {file}")
    if not version_info:
        logger.debug(" write_version_info: version_info is None or empty")
        return False
    try:
        with open(file, 'w') as f:
            f.write(json.dumps(version_info, indent=4))
        logger.debug(f" write_version_info: Successfully wrote version info to {file}")
    except Exception as e:
        logger.error(f" Exception in write_version_info: {e}")
        return False
    return True


@with_error_handling(
    fallback_value=False,
    exception_types=(FileOperationError,),
    retry_count=1,
    user_message="Failed to write trigger words by version ID",
)
def write_triger_words_by_version_id(file, version_id: str) -> bool:
    logger.debug(
        f"[civitai] write_triger_words_by_version_id() called with file: {file}, "
        f"version_id: {version_id}"
    )
    if not version_id:
        logger.debug(" write_triger_words_by_version_id: version_id is None or empty")
        return False
    version_info = get_version_info_by_version_id(version_id)
    if not version_info:
        return False
    return write_triger_words(file, version_info)


@with_error_handling(
    fallback_value=False,
    exception_types=(FileOperationError,),
    retry_count=1,
    user_message="Failed to write trigger words",
)
def write_triger_words(file, version_info: Optional[Dict[str, Any]]) -> bool:
    logger.debug(f" write_triger_words() called with file: {file}")
    if not version_info:
        logger.debug(" write_triger_words: version_info is None or empty")
        return False
    triger_words = get_triger_by_version_info(version_info)
    if not triger_words:
        logger.debug(" write_triger_words: triger_words is None or empty")
        return False
    try:
        with open(file, 'w') as f:
            f.write(triger_words)
        logger.debug(f" write_triger_words: Successfully wrote trigger words to {file}")
    except Exception as e:
        logger.error(f" Exception in write_triger_words: {e}")
        return False
    return True


@with_error_handling(
    fallback_value=False,
    exception_types=(FileOperationError,),
    retry_count=1,
    user_message="Failed to write LoRa metadata by version ID",
)
def write_LoRa_metadata_by_version_id(file, version_id: str) -> bool:
    logger.debug(
        f"[civitai] write_LoRa_metadata_by_version_id() called with file: {file}, "
        f"version_id: {version_id}"
    )
    if not version_id:
        logger.debug(" write_LoRa_metadata_by_version_id: version_id is None or empty")
        return False
    version_info = get_version_info_by_version_id(version_id)
    return write_LoRa_metadata(file, version_info)


@with_error_handling(
    fallback_value=False,
    exception_types=(FileOperationError,),
    retry_count=1,
    user_message="Failed to write LoRa metadata",
)
def write_LoRa_metadata(filepath, version_info) -> bool:
    logger.debug(f" write_LoRa_metadata() called with filepath: {filepath}")
    LoRa_metadata = {
        "description": None,
        "sd version": None,
        "activation text": None,
        "preferred weight": 0,
        "notes": None,
    }
    if not version_info:
        logger.debug(" write_LoRa_metadata: version_info is None or empty")
        return False
    if os.path.isfile(filepath):
        logger.debug(f" write_LoRa_metadata: File already exists: {filepath}")
        return False
    if "description" in version_info:
        LoRa_metadata['description'] = version_info["description"]
    if "baseModel" in version_info:
        base_model = version_info["baseModel"]
        if base_model in settings.model_basemodels:
            LoRa_metadata['sd version'] = settings.model_basemodels[base_model]
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
        logger.debug(
            f"[civitai] write_LoRa_metadata: Successfully wrote LoRa metadata to {filepath}"
        )
    except Exception as e:
        logger.error(f" Exception in write_LoRa_metadata: {e}")
        return False
    return True
