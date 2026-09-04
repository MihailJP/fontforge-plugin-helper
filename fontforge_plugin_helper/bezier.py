"""A collection of Bézier-related routines for Fontforge plugins"""

from math import floor
from typing import Any, Tuple

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


def _isInt(val: Any) -> bool:  # compatibility for Python < 3.12
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
