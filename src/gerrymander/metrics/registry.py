from collections.abc import Callable

from shapely.geometry import MultiPolygon, Polygon

GeometricMetric = Callable[[Polygon | MultiPolygon], float]

from gerrymander.metrics.geometry import (
    convex_hull_ratio,
    polsby_popper_metric,
    reock_metric,
)

GEOMETRIC_METRICS: dict[str, GeometricMetric] = {
    "convex_hull_ratio": convex_hull_ratio,
    "polsby_popper": polsby_popper_metric,
    "reock": reock_metric,
}
