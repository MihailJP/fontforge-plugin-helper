import pytest
import fontforge

from fontforge_plugin_helper import bezier


@pytest.fixture
def contourFactory():
    def factory(quadratic: bool, closed: bool):
        contour = fontforge.contour()
        contour += fontforge.point(50, 50, True)
        contour += fontforge.point(100, 150, True)
        contour += fontforge.point(200, 150, False)
        if not quadratic:
            contour += fontforge.point(200, 100, False)
        contour += fontforge.point(200, 50, True)
        contour.closed = closed
        return contour

    return factory


@pytest.mark.parametrize(('pointNo', 'coord'), [
    (0, (50, 50)),
    (1, (100, 150)),
    (2, (200, 150)),
    (3, (200, 100)),
    (4, (200, 50)),
])
def test_coord(contourFactory, pointNo, coord):
    assert bezier._coord(contourFactory(False, True)[pointNo]) == coord


@pytest.mark.parametrize(('quadratic', 'closed', 'pointNo', 'coord', 'on_curve'), [
    (False, True, 0, (50, 50), True),
    (False, True, 3, (200, 100), False),
    (False, True, 5, (50, 50), True),
    (False, True, -2, (200, 100), False),
    (False, False, 0, (50, 50), True),
    (False, False, 3, (200, 100), False),
    (False, False, 5, IndexError, 'index in open contour out of bounds'),
    (False, False, -2, IndexError, 'index in open contour out of bounds'),
    (True, True, 0, (50, 50), True),
    (True, True, 2, (200, 150), False),
    (True, True, 4, (50, 50), True),
    (True, True, -2, (200, 150), False),
    (True, False, 0, (50, 50), True),
    (True, False, 2, (200, 150), False),
    (True, False, 4, IndexError, 'index in open contour out of bounds'),
    (True, False, -2, IndexError, 'index in open contour out of bounds'),
])
def test_getPoint(contourFactory, quadratic, closed, pointNo, coord, on_curve):
    if isinstance(coord, type) and issubclass(coord, Exception):
        with pytest.raises(coord) as e:
            bezier._getPoint(contourFactory(quadratic, closed), pointNo)
        if isinstance(on_curve, str):
            assert str(e.value) == on_curve
    else:
        point = bezier._getPoint(contourFactory(quadratic, closed), pointNo)
        assert bezier._coord(point) == coord
        assert point.on_curve == on_curve


@pytest.mark.parametrize(('pos', 'coord'), [
    (0, (50, 50)),
    (0.1, (55, 60)),
    (0.5, (75, 100)),
    (0.9, (95, 140)),
    (1, (100, 150)),
])
def test_linearInterpolate(contourFactory, pos, coord):
    contour = contourFactory(False, True)
    p1 = contour[0]
    p2 = contour[1]
    point = bezier._linearInterpolate(p1.x, p1.y, p2.x, p2.y, pos)
    assert point == pytest.approx(coord)


@pytest.mark.parametrize(('pos', 'coord'), [
    (0, (100, 150)),
    (0.1, (119, 149)),
    (0.5, (175, 125)),
    (0.9, (199, 69)),
    (1, (200, 50)),
])
def test_quadraticInterpolate(contourFactory, pos, coord):
    contour = contourFactory(True, True)
    p1 = contour[1]
    p2 = contour[2]
    p3 = contour[3]
    point = bezier._quadraticInterpolate(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, pos)
    assert point == pytest.approx(coord)


@pytest.mark.parametrize(('pos', 'coord'), [
    (0, (100, 150)),
    (0.1, (127.1, 148.55)),
    (0.5, (187.5, 118.75)),
    (0.9, (199.9, 64.95)),
    (1, (200, 50)),
])
def test_cubicInterpolate(contourFactory, pos, coord):
    contour = contourFactory(False, True)
    p1 = contour[1]
    p2 = contour[2]
    p3 = contour[3]
    p4 = contour[4]
    point = bezier._cubicInterpolate(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, p4.x, p4.y, pos)
    assert point == pytest.approx(coord)


@pytest.mark.parametrize(('quadratic', 'closed', 'pointNo', 'coord'), [
    (False, True, 0, (50, 50)),
    (False, True, 0.5, (75, 100)),
    (False, True, 1, (100, 150)),
    (False, True, 1.3, (127.1, 148.55)),
    (False, True, 2.5, (187.5, 118.75)),
    (False, True, 3.7, (199.9, 64.95)),
    (False, True, 4, (200, 50)),
    (False, True, 4.5, (125, 50)),
    (False, False, 0, (50, 50)),
    (False, False, 0.5, (75, 100)),
    (False, False, 1, (100, 150)),
    (False, False, 1.3, (127.1, 148.55)),
    (False, False, 2.5, (187.5, 118.75)),
    (False, False, 3.7, (199.9, 64.95)),
    (False, False, 4, (200, 50)),
    (False, False, 4.5, (IndexError, 'index in open contour out of bounds')),
    (True, True, 0, (50, 50)),
    (True, True, 1, (100, 150)),
    (True, True, 1.2, (119, 149)),
    (True, True, 2, (175, 125)),
    (True, True, 2.8, (199, 69)),
    (True, True, 3, (200, 50)),
    (True, True, 3.5, (125, 50)),
    (True, False, 0, (50, 50)),
    (True, False, 1, (100, 150)),
    (True, False, 1.2, (119, 149)),
    (True, False, 2, (175, 125)),
    (True, False, 2.8, (199, 69)),
    (True, False, 3, (200, 50)),
    (True, False, 3.5, (IndexError, 'index in open contour out of bounds')),
])
def test_getInterpolatedCoord(contourFactory, quadratic, closed, pointNo, coord):
    if isinstance(coord[0], type) and issubclass(coord[0], Exception):
        with pytest.raises(coord[0]) as e:
            bezier.getInterpolatedCoord(contourFactory(quadratic, closed), pointNo)
        if isinstance(coord[1], str):
            assert str(e.value) == coord[1]
    else:
        point = bezier.getInterpolatedCoord(contourFactory(quadratic, closed), pointNo)
        assert point == pytest.approx(coord)
