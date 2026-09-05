"""A collection of Bézier-related routines for Fontforge plugins"""

from math import atan2, floor, pi, tau
from typing import Tuple, Union

import fontforge


def _coord(point: fontforge.point) -> Tuple[float, float]:
    return point.x, point.y


def _getPoint(contour: fontforge.contour, pointNumber: int) -> fontforge.point:
    if contour.closed:
        return contour[pointNumber % len(contour)]
    elif 0 <= pointNumber < len(contour):
        return contour[pointNumber]
    else:
        raise IndexError('index in open contour out of bounds')


def _linearInterpolate(x1: float, y1: float, x2: float, y2: float, fr: float) -> Tuple[float, float]:
    assert 0 <= fr <= 1
    return (
        x1 + (x2 - x1) * fr,
        y1 + (y2 - y1) * fr,
    )


def _quadraticInterpolate(
    x1: float, y1: float,
    x2: float, y2: float,
    x3: float, y3: float,
    fr: float,
) -> Tuple[float, float]:
    assert 0 <= fr <= 1
    ans = tuple(
        (a - 2 * b + c) * (fr ** 2) +
        2 * (b - a) * fr + a
        for (a, b, c) in ((x1, x2, x3), (y1, y2, y3))
    )
    assert len(ans) == 2
    return ans


def _cubicInterpolate(
    x1: float, y1: float,
    x2: float, y2: float,
    x3: float, y3: float,
    x4: float, y4: float,
    fr: float,
) -> Tuple[float, float]:
    assert 0 <= fr <= 1
    ans = tuple(
        (d - 3 * c + 3 * b - a) * (fr ** 3) +
        3 * (a - 2 * b + c) * (fr ** 2) +
        3 * (b - a) * fr + a
        for (a, b, c, d) in ((x1, x2, x3, x4), (y1, y2, y3, y4))
    )
    assert len(ans) == 2
    return ans


def _isInt(val: Union[int, float]) -> bool:  # compatibility for Python < 3.12
    try:
        return val.is_integer()
    except AttributeError:
        return isinstance(val, int)


def getInterpolatedCoord(contour: fontforge.contour, pointNumber: float) -> Tuple[float, float]:
    """Get Bézier interpolation of given contour

    If ``pointNumber`` is an integer and such point is on-curve, returns the coordinate of that point.
    Otherwise the interpolated coordinates will be returned.
    Either quadratic or cubic ``contour`` is accepted.

    For closed contours, point number also loops (interpreted as ``pointNumber % len(contour)``.)
    For open ones, raises ``IndexError`` if ``pointNumber`` is out of bounds.
    """

    def _point(offset: int = 0) -> fontforge.point:
        return _getPoint(contour, floor(pointNumber) + offset)

    if _isInt(pointNumber) and _point().on_curve:
        return _coord(_point())
    elif (p1 := _point()).on_curve and (p2 := _point(1)).on_curve:
        return _linearInterpolate(p1.x, p1.y, p2.x, p2.y, pointNumber % 1)
    elif (p1 := _point()).on_curve and (not (p2 := _point(1)).on_curve) and (p3 := _point(2)).on_curve:
        return _quadraticInterpolate(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, (pointNumber % 1) / 2)
    elif (p1 := _point(-1)).on_curve and (not (p2 := _point()).on_curve) and (p3 := _point(1)).on_curve:
        return _quadraticInterpolate(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, ((pointNumber % 1) + 1) / 2)
    elif (
        (p1 := _point()).on_curve and
        (not (p2 := _point(1)).on_curve) and
        (not (p3 := _point(2)).on_curve) and
        (p4 := _point(3)).on_curve
    ):
        return _cubicInterpolate(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, p4.x, p4.y, (pointNumber % 1) / 3)
    elif (
        (p1 := _point(-1)).on_curve and
        (not (p2 := _point()).on_curve) and
        (not (p3 := _point(1)).on_curve) and
        (p4 := _point(2)).on_curve
    ):
        return _cubicInterpolate(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, p4.x, p4.y, ((pointNumber % 1) + 1) / 3)
    elif (
        (p1 := _point(-2)).on_curve and
        (not (p2 := _point(-1)).on_curve) and
        (not (p3 := _point()).on_curve) and
        (p4 := _point(1)).on_curve
    ):
        return _cubicInterpolate(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, p4.x, p4.y, ((pointNumber % 1) + 2) / 3)
    else:
        raise RuntimeError('malformed contour')


##############################################################################


def _linearDelta(x1: float, y1: float, x2: float, y2: float, fr: float) -> Tuple[float, float]:
    assert 0 <= fr <= 1
    return (x2 - x1, y2 - y1)


def _quadraticDelta(
    x1: float, y1: float,
    x2: float, y2: float,
    x3: float, y3: float,
    fr: float,
) -> Tuple[float, float]:
    assert 0 <= fr <= 1
    ans = tuple(
        2 * (a - 2 * b + c) * fr +
        2 * (b - a)
        for (a, b, c) in ((x1, x2, x3), (y1, y2, y3))
    )
    assert len(ans) == 2
    return ans


def _cubicDelta(
    x1: float, y1: float,
    x2: float, y2: float,
    x3: float, y3: float,
    x4: float, y4: float,
    fr: float,
) -> Tuple[float, float]:
    assert 0 <= fr <= 1
    ans = tuple(
        3 * (d - 3 * c + 3 * b - a) * (fr ** 2) +
        6 * (a - 2 * b + c) * fr +
        3 * (b - a)
        for (a, b, c, d) in ((x1, x2, x3, x4), (y1, y2, y3, y4))
    )
    assert len(ans) == 2
    return ans


def _fractionalPart(x: Union[int, float], leftOpen: bool = False) -> float:
    if (not leftOpen) and _isInt(x):
        return 1.0
    else:
        return x % 1


def _tangentVector(contour: fontforge.contour, pointNumber: float, rightDiff: bool = True) -> Tuple[float, float]:
    def _point(offset: int = 0) -> fontforge.point:
        if (not rightDiff) and _isInt(pointNumber):
            return _getPoint(contour, int(pointNumber) + offset - 1)
        else:
            return _getPoint(contour, floor(pointNumber) + offset)

    def pnum() -> float:
        return _fractionalPart(pointNumber, rightDiff)

    if (p1 := _point()).on_curve and (p2 := _point(1)).on_curve:
        return _linearDelta(p1.x, p1.y, p2.x, p2.y, pnum())
    elif (p1 := _point()).on_curve and (not (p2 := _point(1)).on_curve) and (p3 := _point(2)).on_curve:
        return _quadraticDelta(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, pnum() / 2)
    elif (p1 := _point(-1)).on_curve and (not (p2 := _point()).on_curve) and (p3 := _point(1)).on_curve:
        return _quadraticDelta(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, (pnum() + 1) / 2)
    elif (
        (p1 := _point()).on_curve and
        (not (p2 := _point(1)).on_curve) and
        (not (p3 := _point(2)).on_curve) and
        (p4 := _point(3)).on_curve
    ):
        return _cubicDelta(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, p4.x, p4.y, pnum() / 3)
    elif (
        (p1 := _point(-1)).on_curve and
        (not (p2 := _point()).on_curve) and
        (not (p3 := _point(1)).on_curve) and
        (p4 := _point(2)).on_curve
    ):
        return _cubicDelta(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, p4.x, p4.y, (pnum() + 1) / 3)
    elif (
        (p1 := _point(-2)).on_curve and
        (not (p2 := _point(-1)).on_curve) and
        (not (p3 := _point()).on_curve) and
        (p4 := _point(1)).on_curve
    ):
        return _cubicDelta(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, p4.x, p4.y, (pnum() + 2) / 3)
    else:
        raise RuntimeError('malformed contour')


def _averageDirection(d1: float, d2: float) -> float:
    assert -pi < d1 <= pi
    assert -pi < d2 <= pi
    result = float(d1)

    if d1 == d2:
        result = d1
    elif abs(d1) == abs(d2) and abs(d1) > pi / 2:
        result = pi
    elif d2 - d1 > pi:
        result += pi + (d2 - d1) / 2
    elif d2 - d1 <= -pi:
        result += 0.5 * (d2 - d1) - pi
    else:
        result += 0.5 * (d2 - d1)

    if result > pi:
        return result - tau
    elif result <= -pi:
        return result + tau
    else:
        return result


def _deduplicate(contour: fontforge.contour, pointNumber: float) -> Tuple[fontforge.contour, float]:
    newPointNumber = float(pointNumber) % len(contour)
    newLen = len(contour)

    if contour.closed:
        while contour[newLen - 1].on_curve and (_coord(contour[newLen - 1]) == _coord(contour[0])):
            newLen -= 1
            if newPointNumber >= newLen:
                newPointNumber = 0.0

    newContour = fontforge.contour(bool(contour.is_quadratic))
    for i in range(newLen):
        if i > 0 and contour[i - 1].on_curve and contour[i].on_curve and _coord(contour[i - 1]) == _coord(contour[i]):
            if newPointNumber > len(newContour):
                newPointNumber -= 1
            elif newPointNumber > len(newContour) - 1:
                newPointNumber = float(len(newContour) - 1)
        else:
            newContour += contour[i]

    newContour.closed = contour.closed
    return newContour, newPointNumber


def _getTangentVector(contour: fontforge.contour, pointNumber: float) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    def _point(offset: int = 0) -> fontforge.point:
        return _getPoint(contour, floor(pointNumber) + offset)

    if len(contour) == 0:
        raise ValueError('empty contour')
    elif len(contour) == 1:
        raise ValueError('contour consists of only one point')
    elif len(set((p.x, p.y) for p in contour)) == 1:
        raise ValueError('all points are at the same place')

    fixedContour, fixedPointNumber = _deduplicate(contour, pointNumber)
    if not (_isInt(fixedPointNumber) and _point().on_curve):
        return _tangentVector(fixedContour, fixedPointNumber), _tangentVector(fixedContour, fixedPointNumber)
    elif (not fixedContour.closed) and fixedPointNumber == 0:
        return _tangentVector(fixedContour, fixedPointNumber, True), _tangentVector(fixedContour, fixedPointNumber, True)
    elif (not fixedContour.closed) and fixedPointNumber == len(fixedContour) - 1:
        return _tangentVector(fixedContour, fixedPointNumber, False), _tangentVector(fixedContour, fixedPointNumber, False)
    else:
        return _tangentVector(fixedContour, fixedPointNumber, False), _tangentVector(fixedContour, fixedPointNumber, True)


def getTangentAngle(contour: fontforge.contour, pointNumber: float) -> float:
    """Get direction of tangent in radians

    If ``pointNumber`` is an integer and such point is on-curve,
    returns "average direction" of backward and forward tangents.
    Either quadratic or cubic ``contour`` is accepted.

    For closed contours, point number also loops (interpreted as ``pointNumber % len(contour)``.)
    For open ones, raises ``IndexError`` if ``pointNumber`` is out of bounds.
    """

    return _averageDirection(
        *[atan2(y, x) for x, y in _getTangentVector(contour, pointNumber)]
    )
