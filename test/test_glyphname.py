import pytest

from fontforge_plugin_helper import glyphname


@pytest.mark.parametrize(('name', 'expected'), [
    ('spam', 'spam'),
    ('Ham', '_Ham'),
    ('EGGS', '_E_G_G_S'),
    ('uni1ED0', 'uni1ED0'),
    ('u1B0E5', 'u1B0E5'),
    ('f_j.liga', 'f__j.liga'),
    ('i_uni0307_uni0301.ccmp', 'i__uni0307__uni0301.ccmp'),
    ('uni0431.loclSRB', 'uni0431.locl_S_R_B'),
])
def test_escapeGlyphName(name, expected):
    assert glyphname.escapeGlyphName(name) == expected
