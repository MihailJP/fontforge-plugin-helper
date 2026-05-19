"""A collection of common routines for Fontforge plugins"""

from typing import Literal, Callable

import fontforge


def addSystemHook(
    name: Literal['newFontHook', 'loadFontHook'],
    hook: Callable[[fontforge.font], None]
):
    """Add ``newFontHook`` or ``loadFontHook``

    If there is some function in already ``newFontHook`` or ``loadFontHook``,
    sets a new one which calls the existing one followed by the one
    about to be appended."""
    assert isinstance(fontforge.hooks, dict)
    if name in fontforge.hooks:
        currentHook = fontforge.hooks[name]

        def chainHook(font: fontforge.font):
            currentHook(font)
            hook(font)

        fontforge.hooks[name] = chainHook
    else:
        fontforge.hooks[name] = hook
