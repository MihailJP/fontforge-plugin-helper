"""A collection of common routines for Fontforge plugins"""

from typing import Literal, Callable

import fontforge


def _checkEnabled(
    enableIfGUIMode: bool = True,
    enableIfScriptMode: bool = True,
) -> bool:
    if fontforge.hasUserInterface:
        return enableIfGUIMode
    else:
        return enableIfScriptMode


def addSystemHook(
    name: Literal['newFontHook', 'loadFontHook'],
    hook: Callable[[fontforge.font], None],
    *,
    enableIfGUIMode: bool = True,
    enableIfScriptMode: bool = True,
):
    """Add ``newFontHook`` or ``loadFontHook``

    If there is some function in already ``newFontHook`` or ``loadFontHook``,
    sets a new one which calls the existing one followed by the one
    about to be appended."""

    assert isinstance(fontforge.hooks, dict)
    if _checkEnabled(enableIfGUIMode, enableIfScriptMode):
        if name in fontforge.hooks:
            currentHook = fontforge.hooks[name]

            def chainHook(font: fontforge.font):
                currentHook(font)
                hook(font)

            fontforge.hooks[name] = chainHook
        else:
            fontforge.hooks[name] = hook


def addFontGenerateHook(
    font: fontforge.font,
    name: Literal['generateFontPreHook', 'generateFontPostHook'],
    hook: Callable[[fontforge.font, str], None],
    *,
    enableIfGUIMode: bool = True,
    enableIfScriptMode: bool = True,
):
    """Add ``generateFontPreHook`` or ``generateFontPostHook``

    If there is some function in already ``generateFontPreHook`` or ``generateFontPostHook``,
    sets a new one which calls the existing one followed by the one
    about to be appended."""

    assert isinstance(font.temporary, dict)
    if _checkEnabled(enableIfGUIMode, enableIfScriptMode):
        if name in font.temporary:
            currentHook = font.temporary[name]

            def chainHook(font: fontforge.font, target: str):
                currentHook(font, target)
                hook(font, target)

            font.temporary[name] = chainHook
        else:
            font.temporary[name] = hook
