from gerrymander.metrics.geometry import (
    convex_hull_ratio,
    polsby_popper_metric,
    reock_metric,
)

GEOMETRIC_METRICS = {
    "convex_hull_ratio": convex_hull_ratio,
    "reock": reock_metric,
    "polsby_popper": polsby_popper_metric,
}
