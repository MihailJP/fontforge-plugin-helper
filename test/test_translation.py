from locale import setlocale, LC_ALL

import pytest

from fontforge_plugin_helper import translation


@pytest.fixture
def locale_fr_FR():  # français (France)
    loc = setlocale(LC_ALL)
    setlocale(LC_ALL, 'fr_FR.utf8')
    yield
    setlocale(LC_ALL, loc)


@pytest.fixture
def locale_de_DE():  # Deutsch (Deutschland)
    loc = setlocale(LC_ALL)
    setlocale(LC_ALL, 'de_DE.utf8')
    yield
    setlocale(LC_ALL, loc)


@pytest.fixture
def locale_zh_TW():  # 繁體中文（台灣）
    loc = setlocale(LC_ALL)
    setlocale(LC_ALL, 'zh_TW.utf8')
    yield
    setlocale(LC_ALL, loc)


@pytest.fixture
def locale_zh_CN():  # 简体中文（大陆）
    loc = setlocale(LC_ALL)
    setlocale(LC_ALL, 'zh_CN.utf8')
    yield
    setlocale(LC_ALL, loc)


@pytest.fixture
def translationDict():
    tr = translation.Translations()

    tr.set('fr', 'Hello, font world', 'Bonjour, le monde de la typographie')
    tr.setTranslations('zh', {
        'Hello, font world': '你好，字體世界',
    })
    tr.setTranslations('zh_CN', {
        'Hello, font world': '你好，字体世界',
    })

    # For testing purpose, German translation is intentionally not included

    return tr


def test_locale_fr_FR(locale_fr_FR):
    assert translation._locale() == 'fr_FR'


def test_locale_zh_TW(locale_zh_TW):
    assert translation._locale() == 'zh_TW'


def test_locale_zh_CN(locale_zh_CN):
    assert translation._locale() == 'zh_CN'


def test_translation_fr_FR(locale_fr_FR, translationDict):
    assert translationDict.get('Hello, font world') == 'Bonjour, le monde de la typographie'


def test_translation_zh_TW(locale_zh_TW, translationDict):
    assert translationDict.get('Hello, font world') == '你好，字體世界'


def test_translation_zh_CN(locale_zh_CN, translationDict):
    assert translationDict.get('Hello, font world') == '你好，字体世界'


def test_translation_de_DE(locale_de_DE, translationDict):
    assert translationDict.get('Hello, font world') == 'Hello, font world'


def test_translation_untranslated(locale_fr_FR, translationDict):
    assert translationDict.get('Untranslated message') == 'Untranslated message'
