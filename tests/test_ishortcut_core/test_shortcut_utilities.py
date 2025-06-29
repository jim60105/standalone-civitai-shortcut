from scripts.civitai_manager_libs.ishortcut_core.shortcut_utilities import ShortcutUtilities


def test_extract_version_image_id():
    assert ShortcutUtilities.extract_version_image_id('1-2.jpg') == ['1', '2']
    assert ShortcutUtilities.extract_version_image_id('nohyphen.png') is None


def test_generate_shortcut_name():
    assert ShortcutUtilities.generate_shortcut_name('Name', '3') == 'Name-3'
    assert ShortcutUtilities.generate_shortcut_name('', '3') == '3'
    assert ShortcutUtilities.generate_shortcut_name('X', '') == 'X'


def test_validate_model_id():
    assert ShortcutUtilities.validate_model_id('10') is True
    assert ShortcutUtilities.validate_model_id(20) is True
    # invalid cases
    assert ShortcutUtilities.validate_model_id('0') is False
    assert ShortcutUtilities.validate_model_id('abc') is False


def test_format_date_string():
    s = ShortcutUtilities.format_date_string()
    # expect format YYYYMMDD_HHMMSS length
    assert isinstance(s, str) and len(s) == len('YYYYMMDD_HHMMSS'.replace('Y', '0'))


def test_ensure_nsfw_field():
    d = {}
    res = ShortcutUtilities.ensure_nsfw_field(d)
    assert res.get('nsfw') is False
    # non-dict returns as is
    val = ShortcutUtilities.ensure_nsfw_field('str')
    assert val == 'str'
