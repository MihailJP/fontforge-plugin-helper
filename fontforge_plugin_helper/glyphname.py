"""Glyph name related class for Fontforge plugins"""

import re


def escapeGlyphName(glyphname: str) -> str:
    """Escape a glyph name for case-insensitive file systems

    Escapes a glyph name in the similar way used in saving .sfdir files.
    """

    patterns = [
        (r'^uni([0-9A-F])([0-9A-F])([0-9A-F])([0-9A-F])', 'uni\ufdd0\\1\ufdd0\\2\ufdd0\\3\ufdd0\\4'),
        (r'^u([0-9A-F]|10)([0-9A-F])([0-9A-F])([0-9A-F])([0-9A-F])', 'u\ufdd0\\1\ufdd0\\2\ufdd0\\3\ufdd0\\4\ufdd0\\5'),
        (r'([A-Z_])', r'_\1'),
        ('\ufdd0_?', ''),
    ]
    glyphfilename = glyphname
    for pat, rpl in patterns:
        glyphfilename = re.sub(pat, rpl, glyphfilename)
    return glyphfilename
