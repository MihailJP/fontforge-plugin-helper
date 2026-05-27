"""A collection of common routines for Fontforge plugins"""

from os import PathLike
from typing import Literal, Callable, Optional, Sequence

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
    about to be appended.

    Use keyword-only parameters ``enableIfGUIMode`` and ``enableIfScriptMode``
    to control when the hook will be enabled."""

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
    about to be appended.

    If ``font.temporary`` is not a ``dict``, it is replaced with an empty ``dict`` first,
    then the hook is registered. In such case any previous content will be overwritten
    without warning.

    Use keyword-only parameters ``enableIfGUIMode`` and ``enableIfScriptMode``
    to control when the hook will be enabled."""

    if not isinstance(font.temporary, dict):
        font.temporary = {}
    if _checkEnabled(enableIfGUIMode, enableIfScriptMode):
        if name in font.temporary:
            currentHook = font.temporary[name]

            def chainHook(font: fontforge.font, target: str):
                currentHook(font, target)
                hook(font, target)

            font.temporary[name] = chainHook
        else:
            font.temporary[name] = hook


def generationHookSetter(
    generateFontPreHook: Optional[Callable[[fontforge.font, str], None]],
    generateFontPostHook: Optional[Callable[[fontforge.font, str], None]],
    *,
    enableIfGUIMode: bool = True,
    enableIfScriptMode: bool = True,
) -> Callable[[fontforge.font], None]:
    """Returns a function for ``newFontHook`` or ``loadFontHook`` which sets font generation hook

    Returns function for ``newFontHook`` or ``loadFontHook``
    which sets ``generateFontPreHook`` and/or ``generateFontPostHook``.
    A ``Callable`` object or ``None`` to leave untouched.

    Use keyword-only parameters ``enableIfGUIMode`` and ``enableIfScriptMode``
    to control when the hook will be enabled."""
    def hook(font: fontforge.font):
        if generateFontPreHook:
            addFontGenerateHook(
                font,
                'generateFontPreHook',
                generateFontPreHook,
                enableIfGUIMode=enableIfGUIMode,
                enableIfScriptMode=enableIfScriptMode,
            )
        if generateFontPostHook:
            addFontGenerateHook(
                font,
                'generateFontPostHook',
                generateFontPostHook,
                enableIfGUIMode=enableIfGUIMode,
                enableIfScriptMode=enableIfScriptMode,
            )
    return hook


def newFontWithoutHook() -> fontforge.font:
    """Creates a new font without executing ``fontforge.hooks['newFontHook']``"""
    hook = None
    if 'newFontHook' in fontforge.hooks:
        hook = fontforge.hooks['newFontHook']
        del fontforge.hooks['newFontHook']  # pyright: ignore[reportGeneralTypeIssues]
    font = fontforge.font()
    if hook:
        fontforge.hooks['newFontHook'] = hook
    font.changed = False
    return font


def loadFontWithoutHook(filename: str | PathLike, flags: tuple | int | None = None) -> fontforge.font:
    """Loads a font without executing ``fontforge.hooks['loadFontHook']``"""
    hook = None
    if 'loadFontHook' in fontforge.hooks:
        hook = fontforge.hooks['loadFontHook']
        del fontforge.hooks['loadFontHook']  # pyright: ignore[reportGeneralTypeIssues]
    font = fontforge.open(str(filename), flags)
    if hook:
        fontforge.hooks['loadFontHook'] = hook
    font.changed = False
    return font


def exportWithoutHook(font: fontforge.font, filename: str | PathLike, **options):
    """Call ``font.generate()`` without executing ``generateFontPreHook`` or ``generateFontPostHook``."""
    hooks = {}
    changed = font.changed
    for hook in ['generateFontPreHook', 'generateFontPostHook']:
        if isinstance(font.temporary, dict) and hook in font.temporary:
            hooks[hook] = font.temporary[hook]
            del font.temporary[hook]
    try:
        font.generate(str(filename), **options)
    finally:
        if isinstance(font.temporary, dict):
            for hook, hookfunc in hooks.items():
                font.temporary[hook] = hookfunc
        font.changed = changed


def exportTtcWithoutHook(
    font: fontforge.font,
    filename: str | PathLike,
    others: Sequence[fontforge.font] | fontforge.font | None,
    **options,
):
    """Call ``font.generateTtc()`` without executing ``generateFontPreHook`` or ``generateFontPostHook``."""
    hooks = {}
    changed = font.changed
    for hook in ['generateFontPreHook', 'generateFontPostHook']:
        if isinstance(font.temporary, dict) and hook in font.temporary:
            hooks[hook] = font.temporary[hook]
            del font.temporary[hook]
    try:
        font.generateTtc(str(filename), others, **options)
    finally:
        if isinstance(font.temporary, dict):
            for hook, hookfunc in hooks.items():
                font.temporary[hook] = hookfunc
        font.changed = changed
