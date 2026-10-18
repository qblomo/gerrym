import math

from shapely import MultiPolygon, Polygon, minimum_bounding_radius


def convex_hull_ratio(geometry: Polygon | MultiPolygon) -> float:
    """Compute the ratio of the area of a geometrical object to the area of its convex hull.

    Args:
        geometry: The geometric object

    Returns:
        Ratio of area of the object to area of its convex hull with values in [0,1]

    Raises:
        ValueError: If the geometry is empty
        ValueError: If convex hull has area zero
    """
    if geometry.is_empty:
        raise ValueError("Geometry is empty")
    convex_hull_area = geometry.convex_hull.area
    if convex_hull_area == 0:
        raise ValueError("Convex hull area is zero, cannot compute ratio")
    return geometry.area / convex_hull_area


def reock_metric(geometry: Polygon | MultiPolygon) -> float:
    """Compute the Reock metric of a geometrical object.

    Args:
        geometry: The geometric object

    Returns:
        Reock metric of the object which is area of minimal bounding circle divided by area of the
        object with values in [0,1]

    Raises:
        ValueError: If the geometry is empty
        ValueError: If minimal bounding circle has area zero
    """
    if geometry.is_empty:
        raise ValueError("Geometry is empty")
    radius = minimum_bounding_radius(geometry)
    if radius == 0:
        raise ValueError(
            "Minimal bounding circle area is zero, cannot compute Reock metric"
        )
    bounding_circle_area = math.pi * radius**2
    return geometry.area / bounding_circle_area


def polsby_popper_metric(geometry: Polygon | MultiPolygon) -> float:
    """Compute the Polsby-Popper metric of a geometrical object.

    Args:
        geometry: The geometric object

    Returns:
        Polsby-Popper metric of the object which is 4 * pi * area of the object divided by
        the square of its perimeter (inner holes count towards perimeter) with values in [0,1]

    Raises:
        ValueError: If the geometry is empty
        ValueError: If the perimeter is zero
    """
    if geometry.is_empty:
        raise ValueError("Geometry is empty")
    perimeter = geometry.length
    if perimeter == 0:
        raise ValueError("Perimeter is zero, cannot compute Polsby-Popper metric")
    return (4 * math.pi * geometry.area) / (perimeter**2)
