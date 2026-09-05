from math import radians

import pytest
import fontforge

from fontforge_plugin_helper import bezier


@pytest.fixture
def contourFactory():
    def factory(quadratic: bool, closed: bool, dup: bool = False):
        contour = fontforge.contour()
        contour += fontforge.point(50, 50, True)
        if dup:
            contour += fontforge.point(50, 50, True)
            contour += fontforge.point(100, 150, True)
            contour += fontforge.point(100, 150, True)
            contour += fontforge.point(100, 150, True)
        contour += fontforge.point(100, 150, True)
        contour += fontforge.point(200, 150, False)
        if not quadratic:
            contour += fontforge.point(200, 100, False)
        contour += fontforge.point(200, 50, True)
        if dup and closed:
            contour += fontforge.point(50, 50, True)
            contour += fontforge.point(50, 50, True)
        if dup and not closed:
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


##############################################################################


@pytest.mark.parametrize(('pos', 'coord'), [
    (0, (50, 100)),
    (0.1, (50, 100)),
    (0.5, (50, 100)),
    (0.9, (50, 100)),
    (1, (50, 100)),
])
def test_linearDelta(contourFactory, pos, coord):
    contour = contourFactory(False, True)
    p1 = contour[0]
    p2 = contour[1]
    point = bezier._linearDelta(p1.x, p1.y, p2.x, p2.y, pos)
    assert point == pytest.approx(coord)


@pytest.mark.parametrize(('pos', 'coord'), [
    (0, (200, 0)),
    (0.1, (180, -20)),
    (0.5, (100, -100)),
    (0.9, (20, -180)),
    (1, (0, -200)),
])
def test_quadraticDelta(contourFactory, pos, coord):
    contour = contourFactory(True, True)
    p1 = contour[1]
    p2 = contour[2]
    p3 = contour[3]
    point = bezier._quadraticDelta(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, pos)
    assert point == pytest.approx(coord)


@pytest.mark.parametrize(('pos', 'coord'), [
    (0, (300, 0)),
    (0.1, (243, -28.5)),
    (0.5, (75, -112.5)),
    (0.9, (3, -148.5)),
    (1, (0, -150)),
])
def test_cubicDelta(contourFactory, pos, coord):
    contour = contourFactory(False, True)
    p1 = contour[1]
    p2 = contour[2]
    p3 = contour[3]
    p4 = contour[4]
    point = bezier._cubicDelta(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, p4.x, p4.y, pos)
    assert point == pytest.approx(coord)


@pytest.mark.parametrize(('x', 'leftOpen', 'result'), [
    (3.25, False, 0.25),
    (3.25, True, 0.25),
    (-1.75, False, 0.25),
    (-1.75, True, 0.25),
    (4.0, False, 1),
    (4.0, True, 0),
])
def test_fractionalPart(x, leftOpen, result):
    assert bezier._fractionalPart(x, leftOpen) == result


@pytest.mark.parametrize(('quadratic', 'closed', 'pointNo', 'vec1', 'vec2'), [
    (False, True, 0, (-150, 0), (50, 100)),
    (False, True, 0.5, (50, 100), (50, 100)),
    (False, True, 1, (50, 100), (300, 0)),
    (False, True, 1.3, (243, -28.5), (243, -28.5)),
    (False, True, 2.5, (75, -112.5), (75, -112.5)),
    (False, True, 3.7, (3, -148.5), (3, -148.5)),
    (False, True, 4, (0, -150), (-150, 0)),
    (False, True, 4.5, (-150, 0), (-150, 0)),

    (False, False, 0, (IndexError, 'index in open contour out of bounds'), (50, 100)),
    (False, False, 0.5, (50, 100), (50, 100)),
    (False, False, 1, (50, 100), (300, 0)),
    (False, False, 1.3, (243, -28.5), (243, -28.5)),
    (False, False, 2.5, (75, -112.5), (75, -112.5)),
    (False, False, 3.7, (3, -148.5), (3, -148.5)),
    (False, False, 4, (0, -150), (IndexError, 'index in open contour out of bounds')),
    (
        False, False, 4.5,
        (IndexError, 'index in open contour out of bounds'),
        (IndexError, 'index in open contour out of bounds'),
    ),

    (True, True, 0, (-150, 0), (50, 100)),
    (True, True, 0.5, (50, 100), (50, 100)),
    (True, True, 1, (50, 100), (200, 0)),
    (True, True, 1.2, (180, -20), (180, -20)),
    (True, True, 2, (100, -100), (100, -100)),
    (True, True, 2.8, (20, -180), (20, -180)),
    (True, True, 3, (0, -200), (-150, 0)),
    (True, True, 3.5, (-150, 0), (-150, 0)),

    (True, False, 0, (IndexError, 'index in open contour out of bounds'), (50, 100)),
    (True, False, 0.5, (50, 100), (50, 100)),
    (True, False, 1, (50, 100), (200, 0)),
    (True, False, 1.2, (180, -20), (180, -20)),
    (True, False, 2, (100, -100), (100, -100)),
    (True, False, 2.8, (20, -180), (20, -180)),
    (True, False, 3, (0, -200), (IndexError, 'index in open contour out of bounds')),
    (
        True, False, 3.5,
        (IndexError, 'index in open contour out of bounds'),
        (IndexError, 'index in open contour out of bounds'),
    ),
])
def test_tangentVector(contourFactory, quadratic, closed, pointNo, vec1, vec2):
    def check(coord, rightDiff):
        if isinstance(coord[0], type) and issubclass(coord[0], Exception):
            with pytest.raises(coord[0]) as e:
                bezier._tangentVector(contourFactory(quadratic, closed), pointNo, rightDiff)
            if isinstance(coord[1], str):
                assert str(e.value) == coord[1]
        else:
            point = bezier._tangentVector(contourFactory(quadratic, closed), pointNo, rightDiff)
            assert point == pytest.approx(coord)

    check(vec1, False)
    check(vec2, True)


@pytest.mark.parametrize(('d1', 'd2', 'ans'), [
    (radians(75), radians(75), radians(75)),
    (radians(15), radians(45), radians(30)),
    (radians(150), radians(-90), radians(-150)),
    (radians(90), radians(-150), radians(150)),
    (radians(-150), radians(90), radians(150)),
    (radians(-90), radians(150), radians(-150)),
    (radians(120), radians(-120), radians(180)),
    (radians(-120), radians(120), radians(180)),
    (radians(90), radians(-90), radians(180)),
    (radians(-90), radians(90), radians(0)),
    (radians(60), radians(-60), radians(0)),
    (radians(-60), radians(60), radians(0)),
])
def test_averageDirection(d1, d2, ans):
    assert bezier._averageDirection(d1, d2) == pytest.approx(ans)


@pytest.mark.parametrize(('quadratic', 'closed'), [
    (False, True),
    (False, False),
    (True, True),
    (True, False),
])
def test_deduplicate_contour(contourFactory, quadratic, closed):
    contour1 = contourFactory(quadratic, closed, dup=True)
    contour2, _ = bezier._deduplicate(contour1, 0)
    contour3 = contourFactory(quadratic, closed)
    assert len(contour2) == len(contour3)
    assert contour2.closed == contour3.closed
    for i in range(len(contour3)):
        assert contour2[i].x == contour3[i].x
        assert contour2[i].y == contour3[i].y
        assert contour2[i].on_curve == contour3[i].on_curve


@pytest.mark.parametrize(('pointNo', 'fixedPointNo'), [
    (0, 0),
    (0.5, 0),
    (1, 0),
    (1.5, 0.5),
    (2, 1),
    (3.5, 1),
    (5, 1),
    (6, 2),
    (8, 4),
    (8.5, 4.5),
    (9, 0),
    (9.5, 0),
    (10.5, 0),
])
def test_deduplicate_pointNo(contourFactory, pointNo, fixedPointNo):
    contour = contourFactory(False, True, dup=True)
    _, pnum = bezier._deduplicate(contour, pointNo)
    assert pnum == fixedPointNo


@pytest.mark.parametrize(('pointNo', 'vec1', 'vec2'), [
    (0, (-150, 0), (50, 100)),
    (0.5, (50, 100), (50, 100)),
    (1, (50, 100), (300, 0)),
    (1.3, (243, -28.5), (243, -28.5)),
    (2.5, (75, -112.5), (75, -112.5)),
    (3.7, (3, -148.5), (3, -148.5)),
    (4, (0, -150), (-150, 0)),
    (4.5, (-150, 0), (-150, 0)),
])
def test_getTangentVector(contourFactory, pointNo, vec1, vec2):
    result1, result2 = bezier._getTangentVector(contourFactory(False, True), pointNo)
    assert result1 == pytest.approx(vec1)
    assert result2 == pytest.approx(vec2)


@pytest.mark.parametrize(('points', 'msg'), [
    (0, 'empty contour'),
    (1, 'contour consists of only one point'),
    (2, 'all points are at the same place'),
])
def test_getTangentVector_samepoint(points, msg):
    contour = fontforge.contour()
    for i in range(points):
        contour += fontforge.point(0, 0)
    with pytest.raises(ValueError) as e:
        bezier._getTangentVector(contour, 0)
    if isinstance(msg, str):
        assert str(e.value) == msg


@pytest.mark.parametrize(('closed', 'pointNo', 'angle'), [
    (True, 0, 2.12437068569194187),
    (True, 0.5, 1.1071487177940905),
    (True, 1, 0.55357435889704525),
    (True, 1.3, -0.11675057839306808),
    (True, 2.5, -0.98279372324732907),
    (True, 3.7, -1.55059705421382869),
    (True, 4, radians(-135)),
    (True, 4.5, radians(180)),
    (False, 0, 1.1071487177940905),
    (False, 0.5, 1.1071487177940905),
    (False, 1, 0.55357435889704525),
    (False, 1.3, -0.11675057839306808),
    (False, 2.5, -0.98279372324732907),
    (False, 3.7, -1.55059705421382869),
    (False, 4, radians(-90)),
])
def test_getTangentAngle(contourFactory, closed, pointNo, angle):
    result = bezier.getTangentAngle(contourFactory(False, closed), pointNo)
    assert result == pytest.approx(angle)
