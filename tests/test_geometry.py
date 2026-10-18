import math

import pytest
from shapely import MultiPolygon, Point, Polygon, box

from gerrymander.metrics.registry import GEOMETRIC_METRICS

CIRCLE_QUAD_SEGS = 1024
# Number of segments to approximate the circles.
# Ensures standart tolerance of Pytest.approx is met for the tests.


@pytest.mark.parametrize("metric", GEOMETRIC_METRICS.values())
@pytest.mark.parametrize(
    "empty_geometry",
    [Polygon(), MultiPolygon()],
    ids=["Polygon", "MultiPolygon"],
)
def test_metric_raises_on_empty_geometry(metric, empty_geometry):
    with pytest.raises(ValueError, match="Geometry is empty"):
        metric(empty_geometry)


@pytest.mark.parametrize(
    "geometry, expected",
    [
        (Polygon([(0, 0), (2, 0), (2, 1), (0, 1)]), 1.0),
        (Point(0, 1).buffer(1, quad_segs=CIRCLE_QUAD_SEGS), 1.0),
        (Polygon([(0, 0), (1, 0), (0, 1)]), 1.0),
        (
            Polygon([(0, 0), (2, 0), (2, 1), (1, 1), (1, 2), (0, 2)]),
            3 / (3 + 0.5),
        ),  # convex hull adds a triangle with area 0.5
        (
            MultiPolygon([box(0, 0, 1, 1), box(0, 2, 1, 3)]),
            2 / 3,
        ),  # convex hull adds a square with area 1
        (
            Polygon(
                [(0, 0), (0, 2), (2, 2), (2, 0)],
                [[(0.5, 0.5), (1.5, 0.5), (1.5, 1.5), (0.5, 1.5)]],
            ),
            3 / 4,
        ),  # area of outer square is 4, area of hole is 1
    ],
    ids=[
        "rectangle",
        "circle",
        "triangle",
        "l_shape",
        "two_squares",
        "square_with_hole",
    ],
)
def test_convex_hull_with_known_shapes(geometry, expected):
    ratio = GEOMETRIC_METRICS["convex_hull_ratio"](geometry)
    assert ratio == pytest.approx(expected)


def test_convex_hull_ratio_with_zero_area_convex_hull():
    colinear_polygon = Polygon([(0, 0), (0, 1), (0, 2)])
    with pytest.raises(ValueError, match="Convex hull area is zero"):
        GEOMETRIC_METRICS["convex_hull_ratio"](colinear_polygon)


def test_reock_metric_with_zero_area_bounding_circle():
    degenerate_polygon = Polygon([(0, 0), (0, 0), (0, 0)])
    with pytest.raises(ValueError, match="Minimal bounding circle area is zero"):
        GEOMETRIC_METRICS["reock"](degenerate_polygon)


@pytest.mark.parametrize(
    "geometry, expected",
    [
        (Point(0, 1).buffer(1, quad_segs=CIRCLE_QUAD_SEGS), 1.0),
        (Point(0, 1).buffer(2, quad_segs=CIRCLE_QUAD_SEGS), 1.0),
        (
            Polygon([(0, 0), (1, 0), (0, 1)]),
            1 / math.pi,
        ),
        # area of triangle is 0.5, area of bounding circle is 0.5*pi
        (
            MultiPolygon(
                [
                    Point(0, 0).buffer(0.5, quad_segs=CIRCLE_QUAD_SEGS),
                    Point(1, 0).buffer(0.5, quad_segs=CIRCLE_QUAD_SEGS),
                ]
            ),
            0.5,
        ),
        # area of two circles is 2*pi*0.5^2 = pi/2, area of bounding circle is pi
        (
            Point(0, 0)
            .buffer(1, quad_segs=CIRCLE_QUAD_SEGS)
            .difference(Point(0, 0).buffer(0.5, quad_segs=CIRCLE_QUAD_SEGS)),
            3 / 4,
        ),
        # area of outer circle is pi, are of hole is pi*0.5^2 = pi/4, area of ring is 3*pi/4
        # area of bounding circle is pi
        (Polygon([(0, 0), (0, 1), (0, 2)]), 0.0),
        # area of line segment is 0, area of bounding circle is pi
    ],
    ids=[
        "circle",
        "circle_radius_two",
        "triangle",
        "two_circles",
        "circle_with_hole",
        "collinear_polygon",
    ],
)
def test_reock_metric_with_known_shapes(geometry, expected):
    reock = GEOMETRIC_METRICS["reock"](geometry)
    assert reock == pytest.approx(expected)


def test_polsby_popper_metric_with_zero_perimeter():
    degenerate_polygon = Polygon([(0, 0), (0, 0), (0, 0)])
    with pytest.raises(ValueError, match="Perimeter is zero"):
        GEOMETRIC_METRICS["polsby_popper"](degenerate_polygon)


@pytest.mark.parametrize(
    "geometry, expected",
    [
        (Point(0, 1).buffer(1, quad_segs=CIRCLE_QUAD_SEGS), 1.0),
        (
            Polygon([(0, 0), (1, 0), (0, 1)]),
            2 * math.pi / (2 + math.sqrt(2)) ** 2,
        ),
        # area of triangle is 0.5, perimeter of triangle is 2+sqrt(2)
        # polsby-popper is 4*pi*0.5/(2+sqrt(2))^2 = 2*pi/(2+sqrt(2))^2
        (Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]), math.pi / 4),
        # area of square is 1, perimeter of square is 4
        # polsby-popper is 4*pi*1/4^2 = pi/4
        (
            MultiPolygon(
                [
                    Point(0, 0).buffer(0.5, quad_segs=CIRCLE_QUAD_SEGS),
                    Point(1, 0).buffer(0.5, quad_segs=CIRCLE_QUAD_SEGS),
                ]
            ),
            0.5,
        ),
        # area of two circles is 2*pi*0.5^2 = pi/2, perimeter is 2*2*pi*0.5 = 2*pi
        # polsby-popper is 4*pi*(pi/2)/(2*pi)^2 = 1/2
        (
            Point(0, 0)
            .buffer(1, quad_segs=CIRCLE_QUAD_SEGS)
            .difference(Point(0, 0).buffer(0.5, quad_segs=CIRCLE_QUAD_SEGS)),
            1 / 3,
        ),
        # area of ring is 3*pi/4, perimeter of ring is 2*pi + 2*pi*0.5 = 3*pi
        # polsby-popper is 4*pi*3*(pi/4)/(3*pi)^2 = 1/3
        (Polygon([(0, 0), (0, 1), (0, 2)]), 0.0),
        # area of line segment is 0, perimeter is 4,
        # polsby-popper is 4*pi*0 / 4^2 = 0
    ],
    ids=[
        "circle",
        "triangle",
        "square",
        "two_circles",
        "circle_with_hole",
        "collinear_polygon",
    ],
)
def test_polsby_popper_metric_with_known_shapes(geometry, expected):
    polsby_popper = GEOMETRIC_METRICS["polsby_popper"](geometry)
    assert polsby_popper == pytest.approx(expected)


@pytest.mark.parametrize("metric", GEOMETRIC_METRICS.values())
@pytest.mark.parametrize(
    "geometry",
    [
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        MultiPolygon([box(0, 0, 1, 1), box(0, 2, 1, 3)]),
        Polygon(
            [(0, 0), (0, 2), (2, 2), (2, 0)],
            [[(0.5, 0.5), (1.5, 0.5), (1.5, 1.5), (0.5, 1.5)]],
        ),
        Polygon([(0, 0), (2, 0), (2, 1), (0, 1)]),
        Point(0, 1).buffer(1, quad_segs=CIRCLE_QUAD_SEGS),
        Point(0, 1).buffer(2, quad_segs=CIRCLE_QUAD_SEGS),
        Point(0, 0)
        .buffer(1, quad_segs=CIRCLE_QUAD_SEGS)
        .difference(Point(0, 0).buffer(0.5, quad_segs=CIRCLE_QUAD_SEGS)),
        MultiPolygon(
            [
                Point(0, 0).buffer(0.5, quad_segs=CIRCLE_QUAD_SEGS),
                Point(1, 0).buffer(0.5, quad_segs=CIRCLE_QUAD_SEGS),
            ]
        ),
        Polygon([(0, 0), (1, 0), (0, 1)]),
        Polygon([(0, 0), (2, 0), (2, 1), (1, 1), (1, 2), (0, 2)]),
    ],
    ids=[
        "square",
        "two_squares",
        "square_with_hole",
        "rectangle",
        "circle",
        "circle_radius_two",
        "circle_with_hole",
        "two_circles",
        "triangle",
        "l_shape",
    ],
)
def test_metric_values_between_zero_and_one(metric, geometry):
    value = metric(geometry)
    assert 0 <= value <= 1 + 1e-9
    # tolerance with 1e-9 to account for circle approximations with finite number of segments
