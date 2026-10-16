from shapely import MultiPolygon, Polygon


def convex_hull_ratio(geometry: Polygon | MultiPolygon) -> float:
    """Compute the ratio of the area of a geometrical object to the area of its convex hull.

    Args:
        geometry: The geometric object

    Returns:
        Ratio of area of the object to area of its convex hull

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
