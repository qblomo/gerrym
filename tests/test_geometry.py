import pytest
from shapely import MultiPolygon, Point, Polygon, box

from gerrymander.metrics.geometry import convex_hull_ratio


@pytest.mark.parametrize(
    "geometry, expected",
    [
        (Polygon([(0, 0), (2, 0), (2, 1), (0, 1)]), 1.0),
        (Point(0, 1).buffer(1), 1.0),
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
    ratio = convex_hull_ratio(geometry)
    assert ratio == pytest.approx(expected)


@pytest.mark.parametrize(
    "polygon_type",
    ["Polygon", "MultiPolygon"],
    ids=["Polygon", "MultiPolygon"],
)
def test_convex_hull_ratio_with_empty_geometry(polygon_type):
    if polygon_type == "Polygon":
        empty_geometry = Polygon()
    else:
        empty_geometry = MultiPolygon()
    with pytest.raises(ValueError, match="Geometry is empty"):
        convex_hull_ratio(empty_geometry)


def test_convex_hull_ratio_with_zero_area_convex_hull():
    colinear_polygon = Polygon([(0, 0), (0, 1), (0, 2)])
    with pytest.raises(ValueError, match="Convex hull area is zero"):
        convex_hull_ratio(colinear_polygon)
