"""A collection of common routines for Fontforge plugins"""

from .bezier import (
    getInterpolatedCoord,
)
from .hook import (
    addSystemHook,
    addFontGenerateHook,
    generationHookSetter,
    newFontWithoutHook,
    loadFontWithoutHook,
    exportWithoutHook,
    exportTtcWithoutHook,
)
from .translation import (
    Translations,
)

__all__ = [
    # bezier.py
    'getInterpolatedCoord',

    # hook.py
    'addSystemHook',
    'addFontGenerateHook',
    'generationHookSetter',
    'newFontWithoutHook',
    'loadFontWithoutHook',
    'exportWithoutHook',
    'exportTtcWithoutHook',

    # translation.py
    'Translations',
]
