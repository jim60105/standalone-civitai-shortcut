import os
import json
import shutil

from . import util
from .conditional_imports import import_manager
from .compat.compat_layer import CompatibilityLayer

# Compatibility layer variables
_compat_layer = None

# Project-generated files root directory
SC_DATA_ROOT = "data_sc"
# Stable Diffusion files root directory
SD_DATA_ROOT = "data"

root_path = os.getcwd()


def set_compatibility_layer(compat_layer):
    """Set compatibility layer (called by main program)."""
    global _compat_layer

    util.printD("[setting] set_compatibility_layer: Setting compatibility layer.")
    _compat_layer = compat_layer
    _initialize_extension_base()


def _initialize_extension_base():
    """Initialize extension base path."""
    global extension_base

    util.printD("[setting] _initialize_extension_base: Initializing extension base path.")
    compat = CompatibilityLayer.get_compatibility_layer()
    if compat and hasattr(compat, 'path_manager'):
        extension_base = compat.path_manager.get_extension_path()

        util.printD(
            f"[setting] _initialize_extension_base: Set extension_base from compat.path_manager: "
            f"{extension_base}"
        )
    else:
        # Fallback to current directory structure
        current_dir = os.path.dirname(os.path.abspath(__file__))
        extension_base = os.path.dirname(os.path.dirname(current_dir))

        util.printD(
            f"[setting] _initialize_extension_base: Fallback extension_base: " f"{extension_base}"
        )


# Initialize extension_base
extension_base = ""
try:
    _initialize_extension_base()
except Exception:
    # Suppress initialization errors (e.g., missing dependencies in test environments)
    pass

headers = {
    'user-agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 '
        'Safari/537.36 Edg/112.0.1722.68'
    ),
    "Authorization": "",
}

civitai_api_key = ""

# HTTP client settings - adjusted for better connection stability
http_timeout = 60  # seconds - increased from 20 for long operations
http_max_retries = 3
http_retry_delay = 2  # seconds between retries - increased for better stability

# Download settings - extended timeouts for large files
download_timeout = 600  # 10 minutes for large files - increased from 300
download_max_retries = 5
download_retry_delay = 10  # seconds
download_chunk_size = 8192  # bytes
download_max_concurrent = 3  # maximum concurrent downloads
download_resume_enabled = True
download_verify_checksum = False  # future feature
Extensions_Name = "Civitai Shortcut"
Extensions_Version = "v1.6.7"

# HTTP Client Performance Settings
http_pool_connections = 10
http_pool_maxsize = 20
http_pool_block = False
http_enable_chunked_download = True
http_max_parallel_chunks = 4
http_chunk_size = 1024 * 1024  # 1MB

# Monitoring Settings (removed per centralized HTTP client migration)

# Cache Settings
http_cache_enabled = True
http_cache_max_size_mb = 100
http_cache_default_ttl = 3600  # 1 hour

PLACEHOLDER = "[No Select]"
NORESULT = "[No Result]"
NEWRECIPE = "[New Prompt Recipe]"
NEWCLASSIFICATION = "[New Classification]"

CREATE_MODEL_FOLDER = "Create a model folder to download the model"
# CREATE_MODEL_FOLDER = "Create a model folder with the model name"

model_exts = (".bin", ".pt", ".safetensors", ".ckpt")

# sd_version = ['SD1', 'SD2', 'SDXL', 'Unknown']
model_basemodels = {
    "SD 1.4": "SD1",
    "SD 1.5": "SD1",
    "SD 2.0": "SD2",
    "SD 2.0 768": "SD2",
    "SD 2.1": "SD2",
    "SD 2.1 768": "SD2",
    "SD 2.1 Unclip": "SD2",
    "SDXL 0.9": "SDXL",
    "SDXL 1.0": "SDXL",
    "SDXL 1.0 LCM": "SDXL",
    "SDXL Distilled": "SDXL",
    "SDXL Turbo": "SDXL",
    "SDXL Lightning": "SDXL",
    "Pony": "Pony",
    "SVD": "SVD",
    "SVD XT": "SVD",
    "Stable Cascade": "SC",
    "Playground V2": "PGV2",
    "PixArt A": "PixArtA",
    "Other": "Unknown",
}

# civitai model type -> folder path
model_folders = {
    'Checkpoint': os.path.join("models", "Stable-diffusion"),
    'LORA': os.path.join("models", "Lora"),
    'LoCon': os.path.join("models", "LyCORIS"),
    'TextualInversion': os.path.join("embeddings"),
    'Hypernetwork': os.path.join("models", "hypernetworks"),
    'AestheticGradient': os.path.join(
        "extensions", "stable-diffusion-webui-aesthetic-gradients", "aesthetic_embeddings"
    ),
    'Controlnet': os.path.join("models", "ControlNet"),
    'Poses': os.path.join("models", "Poses"),
    'Wildcards': os.path.join("extensions", "sd-dynamic-prompts", "wildcards"),
    'Other': os.path.join("models", "Other"),
    'VAE': os.path.join("models", "VAE"),
    'ANLORA': os.path.join("extensions", "sd-webui-additional-networks", "models", "lora"),
    'Unknown': os.path.join("models", "Unknown"),
}

# UI 쪽에서 변환할때 쓰인다.
# UI model type -> civitai model type

# UI type 하나에 다중의 civitai type을 대입할때 대상이 되는것은
# get_ui_typename 함수와 ishortcut->get_image_list 와 get_list 뿐이다.
# 나머지는 key로만 쓰이기 때문에 value 값이 배열이라 해도문제가 안될듯한다.
# ishortcut 부분은 여기를
# tmp_types.append(setting.ui_typenames[sc_type])
# ->
# for type_name in setting.ui_typenames[sc_type]:
#     tmp_types.append(type_name)
# 이리 하면 될듯

# get_ui_typename는 이렇게 수정해도 문제 없을것 같다. 대신 모두 "" : ["",""] 형식으로 바꿔야 할듯(안해도 되나?)
# def get_ui_typename(model_type):
#     for k,v in ui_typenames.items():
#         if model_type in v:
#             return k
#     return model_type

ui_typenames = {
    "Checkpoint": 'Checkpoint',
    "LoRA": 'LORA',
    "LyCORIS": 'LoCon',
    "Textual Inversion": 'TextualInversion',
    "Hypernetwork": 'Hypernetwork',
    "Aesthetic Gradient": 'AestheticGradient',
    "Controlnet": 'Controlnet',
    "Poses": 'Poses',
    "Wildcards": 'Wildcards',
    "Other": 'Other',
}

# information tab
civitai_information_tab = 0
usergal_information_tab = 1
download_information_tab = 2

# civitai helper 호환성
info_ext = ".info"
info_suffix = ".civitai"

triger_ext = ".txt"
triger_suffix = ".triger"

preview_image_ext = ".png"
preview_image_suffix = ".preview"

# 임시설정

# 갤러리 height 설정
information_gallery_height = "auto"  # auto , fit

# 화면 분할 비율
shortcut_browser_screen_split_ratio = 3
shortcut_browser_screen_split_ratio_max = 10

shortcut_browser_search_up = False

# 갤러리 ui설정
# model browser 설정
shortcut_column = 5
shortcut_rows_per_page = 4
gallery_column = 7

# 유저 갤러리 설정
usergallery_images_column = 6
usergallery_images_rows_per_page = 2

# prompt recipe 설정
prompt_shortcut_column = 5
prompt_shortcut_rows_per_page = 4
prompt_reference_shortcut_column = 8
prompt_reference_shortcut_rows_per_page = 4

# classification 설정
classification_shortcut_column = 5
classification_shortcut_rows_per_page = 4

classification_gallery_column = 8
classification_gallery_rows_per_page = 4

shortcut_max_download_image_per_version = (
    0  # 버전당 최대 다운로드 이미지 수 , 0이면 전체다운 받는다
)
gallery_thumbnail_image_style = "scale-down"

# 다운로드 설정
download_images_folder = os.path.join(SD_DATA_ROOT, "output", "download-images")

# Image download settings
image_download_timeout = 30
image_download_max_retries = 3
image_download_cache_enabled = True
image_download_cache_max_age = 3600  # seconds
scan_timeout = 30
scan_max_retries = 2
preview_image_quality = 85  # JPEG quality for preview images

# Gallery download settings
gallery_download_batch_size = 5
gallery_download_timeout = 30
gallery_max_concurrent_downloads = 3

# background thread 설정
# shortcut_auto_update = True
shortcut_update_when_start = True
usergallery_preloading = False

# 생성되는 폴더 및 파일
shortcut = os.path.join(SC_DATA_ROOT, "CivitaiShortCut.json")
shortcut_setting = os.path.join(SC_DATA_ROOT, "CivitaiShortCutSetting.json")
shortcut_classification = os.path.join(SC_DATA_ROOT, "CivitaiShortCutClassification.json")
shortcut_civitai_internet_shortcut_url = os.path.join(SC_DATA_ROOT, "CivitaiShortCutBackupUrl.json")
shortcut_recipe = os.path.join(SC_DATA_ROOT, "CivitaiShortCutRecipeCollection.json")

# shortcut_thumbnail_folder =  "sc_thumb"
shortcut_thumbnail_folder = os.path.join(SC_DATA_ROOT, "sc_thumb_images")
shortcut_recipe_folder = os.path.join(SC_DATA_ROOT, "sc_recipes")
shortcut_info_folder = os.path.join(SC_DATA_ROOT, "sc_infos")
shortcut_gallery_folder = os.path.join(SC_DATA_ROOT, "sc_gallery")


def init_paths():
    """Initialize and create necessary directories."""
    dirs = [
        SC_DATA_ROOT,
        SD_DATA_ROOT,
        os.path.join(SD_DATA_ROOT, "models"),
        os.path.join(SD_DATA_ROOT, "output"),
        download_images_folder,
        shortcut_thumbnail_folder,
        shortcut_recipe_folder,
        shortcut_info_folder,
        shortcut_gallery_folder,
    ]
    for d in dirs:
        try:
            os.makedirs(d, exist_ok=True)
        except Exception as e:
            util.printD(f"[setting] init_paths: Failed to create directory {d}: {e}")


def migrate_existing_files():
    """Migrate existing files and folders in root to new data_sc structure."""
    mapping = {
        "CivitaiShortCut.json": shortcut,
        "CivitaiShortCutSetting.json": shortcut_setting,
        "CivitaiShortCutClassification.json": shortcut_classification,
        "CivitaiShortCutRecipeCollection.json": shortcut_recipe,
        "CivitaiShortCutBackupUrl.json": shortcut_civitai_internet_shortcut_url,
        "sc_gallery": shortcut_gallery_folder,
        "sc_thumb_images": shortcut_thumbnail_folder,
        "sc_infos": shortcut_info_folder,
        "sc_recipes": shortcut_recipe_folder,
    }
    for old, new in mapping.items():
        if os.path.exists(old) and not os.path.exists(new):
            try:
                shutil.move(old, new)
                util.printD(f"[setting] migrate_existing_files: Moved {old} to {new}")
            except Exception as e:
                util.printD(f"[setting] migrate_existing_files: Failed to move {old} to {new}: {e}")


no_card_preview_image = os.path.join(extension_base, "img", "card-no-preview.png")
nsfw_disable_image = os.path.join(extension_base, "img", "nsfw-no-preview.png")

NSFW_filtering_enable = True
# NSFW_level = { "None":True, "Soft":False, "Mature":False, "X":False } # None, Soft, Mature, X
NSFW_levels = ("None", "Soft", "Mature", "X", "XX")  # None, Soft, Mature, X
NSFW_level_user = "None"

shortcut_env = dict()


def set_NSFW(enable, level="None"):
    # global NSFW_level
    global NSFW_filtering_enable
    global NSFW_level_user
    util.printD(f"[setting] set_NSFW: Set NSFW_filtering_enable={enable}, NSFW_level_user={level}")
    NSFW_filtering_enable = enable
    NSFW_level_user = level


def save_NSFW():
    global NSFW_filtering_enable
    global NSFW_level_user
    util.printD(
        f"[setting] save_NSFW: Saving NSFW settings. Enable={NSFW_filtering_enable}, "
        f"Level={NSFW_level_user}"
    )
    environment = load()
    if not environment:
        environment = dict()

    nsfw_filter = dict()
    nsfw_filter['nsfw_filter_enable'] = NSFW_filtering_enable
    nsfw_filter['nsfw_level'] = NSFW_level_user
    environment['NSFW_filter'] = nsfw_filter

    save(environment)


def init():
    global extension_base
    util.printD(f"[setting] init: Initializing with extension_base={extension_base}")
    init_paths()
    migrate_existing_files()
    global shortcut
    global shortcut_setting
    global shortcut_classification
    global shortcut_civitai_internet_shortcut_url
    global shortcut_recipe

    global shortcut_thumbnail_folder
    global shortcut_recipe_folder
    global shortcut_info_folder
    global shortcut_gallery_folder

    shortcut = os.path.join(extension_base, shortcut)
    shortcut_setting = os.path.join(extension_base, shortcut_setting)
    shortcut_classification = os.path.join(extension_base, shortcut_classification)
    shortcut_recipe = os.path.join(extension_base, shortcut_recipe)
    shortcut_civitai_internet_shortcut_url = os.path.join(
        extension_base, shortcut_civitai_internet_shortcut_url
    )

    shortcut_thumbnail_folder = os.path.join(extension_base, shortcut_thumbnail_folder)
    shortcut_recipe_folder = os.path.join(extension_base, shortcut_recipe_folder)
    shortcut_info_folder = os.path.join(extension_base, shortcut_info_folder)
    shortcut_gallery_folder = os.path.join(extension_base, shortcut_gallery_folder)

    util.printD("[setting] init: Paths initialized. Loading data...")
    load_data()


def load_data():
    global model_folders
    util.printD("[setting] load_data: Loading configuration data and environment settings.")
    global shortcut_column
    global shortcut_rows_per_page
    global gallery_column
    global classification_shortcut_column
    global classification_shortcut_rows_per_page
    global classification_gallery_column
    global classification_gallery_rows_per_page
    global usergallery_images_column
    global usergallery_images_rows_per_page

    global prompt_shortcut_column
    global prompt_shortcut_rows_per_page
    global prompt_reference_shortcut_column
    global prompt_reference_shortcut_rows_per_page

    global shortcut_max_download_image_per_version
    global gallery_thumbnail_image_style
    global shortcut_browser_search_up

    global download_images_folder
    global shortcut_browser_screen_split_ratio
    global information_gallery_height

    global shortcut_update_when_start
    global civitai_api_key

    # Load WebUI specific paths through compatibility layer
    compat = CompatibilityLayer.get_compatibility_layer()
    if compat and hasattr(compat, 'path_manager'):
        util.printD("[setting] load_data: Using compat.path_manager for model folders.")
        # Override default model folder paths directly without filesystem check
        embeddings_dir = compat.path_manager.get_model_path('embeddings')
        if embeddings_dir:
            util.printD(f"[setting] load_data: Set TextualInversion folder: {embeddings_dir}")
            model_folders['TextualInversion'] = embeddings_dir

        hypernetwork_dir = compat.path_manager.get_model_path('hypernetworks')
        if hypernetwork_dir:
            util.printD(f"[setting] load_data: Set Hypernetwork folder: {hypernetwork_dir}")
            model_folders['Hypernetwork'] = hypernetwork_dir

        ckpt_dir = compat.path_manager.get_model_path('checkpoints')
        if ckpt_dir:
            util.printD(f"[setting] load_data: Set Checkpoint folder: {ckpt_dir}")
            model_folders['Checkpoint'] = ckpt_dir

        lora_dir = compat.path_manager.get_model_path('lora')
        if lora_dir:
            util.printD(f"[setting] load_data: Set LORA folder: {lora_dir}")
            model_folders['LORA'] = lora_dir
    else:
        util.printD("[setting] load_data: Fallback to import_manager for model folders.")
        # Fallback: Try to get WebUI paths directly (for backward compatibility)
        shared = import_manager.get_webui_module('shared')
        if shared and hasattr(shared, 'cmd_opts'):
            cmd_opts = shared.cmd_opts
            if hasattr(cmd_opts, 'embeddings_dir') and cmd_opts.embeddings_dir:
                util.printD(
                    f"[setting] load_data: Set TextualInversion folder (fallback): "
                    f"{cmd_opts.embeddings_dir}"
                )
                model_folders['TextualInversion'] = cmd_opts.embeddings_dir
            if hasattr(cmd_opts, 'hypernetwork_dir') and cmd_opts.hypernetwork_dir:
                util.printD(
                    f"[setting] load_data: Set Hypernetwork folder (fallback): "
                    f"{cmd_opts.hypernetwork_dir}"
                )
                model_folders['Hypernetwork'] = cmd_opts.hypernetwork_dir
            if hasattr(cmd_opts, 'ckpt_dir') and cmd_opts.ckpt_dir:
                util.printD(
                    f"[setting] load_data: Set Checkpoint folder (fallback): {cmd_opts.ckpt_dir}"
                )
                model_folders['Checkpoint'] = cmd_opts.ckpt_dir
            if hasattr(cmd_opts, 'lora_dir') and cmd_opts.lora_dir:
                util.printD(f"[setting] load_data: Set LORA folder (fallback): {cmd_opts.lora_dir}")
                model_folders['LORA'] = cmd_opts.lora_dir

    environment = load()
    if environment:
        util.printD(f"[setting] load_data: Loaded environment: {environment}")
        if "NSFW_filter" in environment.keys():
            nsfw_filter = environment['NSFW_filter']
            filtering_enable = True
            if 'nsfw_filter_enable' in nsfw_filter.keys():
                filtering_enable = bool(nsfw_filter['nsfw_filter_enable'])

            if 'nsfw_level' in nsfw_filter.keys():
                util.printD(
                    f"[setting] load_data: Set NSFW from environment: enable={filtering_enable}, "
                    f"level={nsfw_filter['nsfw_level']}"
                )
                set_NSFW(filtering_enable, nsfw_filter['nsfw_level'])

        if "application_allow" in environment.keys():
            application_allow = environment['application_allow']

            if "civitai_api_key" in application_allow.keys():
                civitai_api_key = application_allow['civitai_api_key']
                util.printD("[setting] load_data: Set civitai_api_key from environment.")
            if "shortcut_update_when_start" in application_allow.keys():
                shortcut_update_when_start = bool(application_allow['shortcut_update_when_start'])
                util.printD(
                    f"[setting] load_data: Set shortcut_update_when_start: "
                    f"{shortcut_update_when_start}"
                )
            if "shortcut_max_download_image_per_version" in application_allow.keys():
                shortcut_max_download_image_per_version = int(
                    application_allow['shortcut_max_download_image_per_version']
                )
                util.printD(
                    f"[setting] load_data: Set shortcut_max_download_image_per_version: "
                    f"{shortcut_max_download_image_per_version}"
                )

        if "screen_style" in environment.keys():
            screen_style = environment['screen_style']

            if "shortcut_browser_screen_split_ratio" in screen_style.keys():
                shortcut_browser_screen_split_ratio = int(
                    screen_style['shortcut_browser_screen_split_ratio']
                )
                util.printD(
                    f"[setting] load_data: Set shortcut_browser_screen_split_ratio: "
                    f"{shortcut_browser_screen_split_ratio}"
                )
            if "information_gallery_height" in screen_style.keys():
                if screen_style['information_gallery_height'].strip():
                    information_gallery_height = screen_style['information_gallery_height']
                    util.printD(
                        f"[setting] load_data: Set information_gallery_height: "
                        f"{information_gallery_height}"
                    )
            if "gallery_thumbnail_image_style" in screen_style.keys():
                gallery_thumbnail_image_style = screen_style['gallery_thumbnail_image_style']
                util.printD(
                    f"[setting] load_data: Set gallery_thumbnail_image_style: "
                    f"{gallery_thumbnail_image_style}"
                )
            if "shortcut_browser_search_up" in screen_style.keys():
                shortcut_browser_search_up = bool(screen_style['shortcut_browser_search_up'])
                util.printD(
                    f"[setting] load_data: Set shortcut_browser_search_up: "
                    f"{shortcut_browser_search_up}"
                )

        if "image_style" in environment.keys():
            image_style = environment['image_style']

            if "shortcut_column" in image_style.keys():
                shortcut_column = int(image_style['shortcut_column'])
                util.printD(f"[setting] load_data: Set shortcut_column: {shortcut_column}")
            if "shortcut_rows_per_page" in image_style.keys():
                shortcut_rows_per_page = int(image_style['shortcut_rows_per_page'])
                util.printD(
                    f"[setting] load_data: Set shortcut_rows_per_page: {shortcut_rows_per_page}"
                )

            if "gallery_column" in image_style.keys():
                gallery_column = int(image_style['gallery_column'])
                util.printD(f"[setting] load_data: Set gallery_column: {gallery_column}")

            if "classification_shortcut_column" in image_style.keys():
                classification_shortcut_column = int(image_style['classification_shortcut_column'])
                util.printD(
                    f"[setting] load_data: Set classification_shortcut_column: "
                    f"{classification_shortcut_column}"
                )
            if "classification_shortcut_rows_per_page" in image_style.keys():
                classification_shortcut_rows_per_page = int(
                    image_style['classification_shortcut_rows_per_page']
                )
                util.printD(
                    f"[setting] load_data: Set classification_shortcut_rows_per_page: "
                    f"{classification_shortcut_rows_per_page}"
                )
            if "classification_gallery_column" in image_style.keys():
                classification_gallery_column = int(image_style['classification_gallery_column'])
                util.printD(
                    f"[setting] load_data: Set classification_gallery_column: "
                    f"{classification_gallery_column}"
                )
            if "classification_gallery_rows_per_page" in image_style.keys():
                classification_gallery_rows_per_page = int(
                    image_style['classification_gallery_rows_per_page']
                )
                util.printD(
                    f"[setting] load_data: Set classification_gallery_rows_per_page: "
                    f"{classification_gallery_rows_per_page}"
                )

            if "usergallery_images_column" in image_style.keys():
                usergallery_images_column = int(image_style['usergallery_images_column'])
                util.printD(
                    f"[setting] load_data: Set usergallery_images_column: "
                    f"{usergallery_images_column}"
                )
            if "usergallery_images_rows_per_page" in image_style.keys():
                usergallery_images_rows_per_page = int(
                    image_style['usergallery_images_rows_per_page']
                )
                util.printD(
                    f"[setting] load_data: Set usergallery_images_rows_per_page: "
                    f"{usergallery_images_rows_per_page}"
                )

            if "prompt_shortcut_column" in image_style.keys():
                prompt_shortcut_column = int(image_style['prompt_shortcut_column'])
                util.printD(
                    f"[setting] load_data: Set prompt_shortcut_column: {prompt_shortcut_column}"
                )
            if "prompt_shortcut_rows_per_page" in image_style.keys():
                prompt_shortcut_rows_per_page = int(image_style['prompt_shortcut_rows_per_page'])
                util.printD(
                    f"[setting] load_data: Set prompt_shortcut_rows_per_page: "
                    f"{prompt_shortcut_rows_per_page}"
                )
            if "prompt_reference_shortcut_column" in image_style.keys():
                prompt_reference_shortcut_column = int(
                    image_style['prompt_reference_shortcut_column']
                )
                util.printD(
                    f"[setting] load_data: Set prompt_reference_shortcut_column: "
                    f"{prompt_reference_shortcut_column}"
                )
            if "prompt_reference_shortcut_rows_per_page" in image_style.keys():
                prompt_reference_shortcut_rows_per_page = int(
                    image_style['prompt_reference_shortcut_rows_per_page']
                )
                util.printD(
                    f"[setting] load_data: Set prompt_reference_shortcut_rows_per_page: "
                    f"{prompt_reference_shortcut_rows_per_page}"
                )

        if "model_folders" in environment.keys():
            user_folders = environment['model_folders']

            if 'LoCon' in user_folders.keys():
                model_folders['LoCon'] = user_folders['LoCon']
                util.printD(f"[setting] load_data: Set LoCon folder: {user_folders['LoCon']}")

            if 'Wildcards' in user_folders.keys():
                model_folders['Wildcards'] = user_folders['Wildcards']
                util.printD(
                    f"[setting] load_data: Set Wildcards folder: {user_folders['Wildcards']}"
                )

            if 'Controlnet' in user_folders.keys():
                model_folders['Controlnet'] = user_folders['Controlnet']
                util.printD(
                    f"[setting] load_data: Set Controlnet folder: {user_folders['Controlnet']}"
                )

            if 'AestheticGradient' in user_folders.keys():
                model_folders['AestheticGradient'] = user_folders['AestheticGradient']
                util.printD(
                    f"[setting] load_data: Set AestheticGradient folder: "
                    f"{user_folders['AestheticGradient']}"
                )

            if 'Poses' in user_folders.keys():
                model_folders['Poses'] = user_folders['Poses']
                util.printD(f"[setting] load_data: Set Poses folder: {user_folders['Poses']}")

            if 'Other' in user_folders.keys():
                model_folders['Other'] = user_folders['Other']
                util.printD(f"[setting] load_data: Set Other folder: {user_folders['Other']}")

        if "download_folders" in environment.keys():
            download_folders = environment['download_folders']
            if 'download_images' in download_folders.keys():
                download_images_folder = download_folders['download_images']
                util.printD(
                    f"[setting] load_data: Set download_images_folder: {download_images_folder}"
                )

        if "temporary" in environment.keys():
            temporary = environment['temporary']
            util.printD(f"[setting] load_data: Loaded temporary section: {temporary}")


def generate_type_basefolder(content_type):

    if content_type in model_folders.keys():
        model_folder = model_folders[content_type]
    elif content_type:
        model_folder = os.path.join(model_folders['Unknown'], util.replace_dirname(content_type))
    else:
        model_folder = os.path.join(model_folders['Unknown'])

    return model_folder


def generate_version_foldername(model_name, ver_name, ver_id):
    return f"{model_name}-{ver_name}"


def get_model_folders():
    return model_folders.values()


def get_ui_typename(model_type):
    for k, v in ui_typenames.items():
        if v == model_type:
            return k
    return model_type


def get_imagefn_and_shortcutid_from_recipe_image(recipe_image):
    if recipe_image:
        result = recipe_image.split(":", 1)
        if len(result) > 1:
            return result[0], result[1]
        return None, None


def set_imagefn_and_shortcutid_for_recipe_image(shortcutid, image_fn):
    if image_fn and shortcutid:
        return f"{shortcutid}:{image_fn}"


def get_modelid_from_shortcutname(sc_name):
    """Extract model ID from shortcut name.

    Args:
        sc_name: Shortcut name in format "name:id", or list containing shortcut name

    Returns:
        str: Model ID if found, None otherwise
    """
    if not sc_name:
        return None

    # Handle case where sc_name is a list (from Gradio SelectData)
    if isinstance(sc_name, list):
        if len(sc_name) > 1:
            sc_name = sc_name[1]  # Use second element (shortcut name)
        elif len(sc_name) == 1:
            sc_name = sc_name[0]  # Use first element
        else:
            return None

    # Ensure sc_name is a string
    if not isinstance(sc_name, str):
        return None

    # Extract model ID from "name:id" format
    colon_pos = sc_name.rfind(':')
    if colon_pos != -1:
        return sc_name[colon_pos + 1 :]

    return None


def set_shortcutname(modelname, modelid):
    if modelname and modelid:
        return f"{modelname}:{modelid}"


def get_image_url_to_shortcut_file(modelid, versionid, image_url):
    if image_url:
        version_image_prefix = f"{versionid}-"
        model_path = os.path.join(shortcut_info_folder, str(modelid))
        image_id, ext = os.path.splitext(os.path.basename(image_url))
        description_img = os.path.join(
            model_path, f"{version_image_prefix}{image_id}{preview_image_ext}"
        )
        return description_img
    return None


def get_image_url_to_gallery_file(image_url):
    if image_url:
        image_id, ext = os.path.splitext(os.path.basename(image_url))
        description_img = os.path.join(shortcut_gallery_folder, f"{image_id}{preview_image_ext}")
        return description_img
    return None


def save(env):
    try:
        util.printD(f"[setting] save: Saving environment to {shortcut_setting}")
        with open(shortcut_setting, 'w') as f:
            json.dump(env, f, indent=4)
    except Exception as e:
        util.printD(f"[setting] save: Exception occurred while saving: {e}")
        return False

    util.printD("[setting] save: Save successful.")
    return True


def load():
    if not os.path.isfile(shortcut_setting):
        util.printD(f"[setting] load: {shortcut_setting} not found, creating new file.")
        save({})
        return

    json_data = None
    try:
        with open(shortcut_setting, 'r') as f:
            json_data = json.load(f)
        util.printD(f"[setting] load: Loaded data from {shortcut_setting}")
    except Exception as e:
        util.printD(f"[setting] load: Exception occurred while loading: {e}")
        pass

    return json_data
