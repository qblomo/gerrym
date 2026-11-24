import logging
import math
from collections.abc import Hashable, Mapping
from typing import cast

import geopandas as gpd
import pandas as pd
from shapely.geometry import MultiPolygon, Polygon

from gerrymander.metrics.registry import GEOMETRIC_METRICS, GeometricMetric

logger = logging.getLogger(__name__)


def compute_geometric_metrics(
    gdf: gpd.GeoDataFrame, metrics: Mapping[str, GeometricMetric] = GEOMETRIC_METRICS
) -> pd.DataFrame:
    """
    Compute geometric metrics for a GeoDataFrame.

    The input remains unchanged, and a new DataFrame is returned with the same indices in the same order.
    If a metric raises an ValueError for a geometry, the corresponding metric value will be NaN
    and a warning will be logged. Other Errors are raised as normal. An empty GeoDataFrame will return an empty DataFrame with the same columns as the metrics.
    An empty metrics mapping will return an empty DataFrame with the same indices as the input GeoDataFrame. The order of the columns
    is not guaranteed to match the order of the keys in the metrics mapping.


    Args:
        gdf: A GeoDataFrame containing geometries with a projected crs.
        metrics: A mapping of metrics to be calculated. Defaults to GEOMETRIC_METRICS which includes all metrics from the registry.

    Returns:
        A DataFrame containing the original indices and calculated metrics as new columns
        with one column per key of metrics.

    Raises:
        ValueError: If the input GeoDataFrame is not projected.
        ValueError: If the input GeoDataFrame does not have a defined CRS.
        ValueError: If the geom_type of input GeoDataFrame is not Polygon or MultiPolygon.
    """
    if gdf.crs is None:
        raise ValueError("Input GeoDataFrame must have crs defined")
    if not gdf.crs.is_projected:
        raise ValueError("Input GeoDataFrame must be projected")
    if gdf.geometry.isna().any():
        raise ValueError("Input GeoDataFrame contains NaN geometries")
    if not gdf.geom_type.isin({"Polygon", "MultiPolygon"}).all():
        raise ValueError("All geometries have to be of type Polygon or MultiPolygon")
    columns = {}
    for name, metric in metrics.items():
        columns[name] = [
            _apply_metric(metric, cast(Polygon | MultiPolygon, geometry), name, label)
            for label, geometry in gdf.geometry.items()
        ]
    return pd.DataFrame(columns, index=gdf.index)


def _apply_metric(
    metric: GeometricMetric,
    geometry: Polygon | MultiPolygon,
    name: str,
    index: Hashable,
) -> float:
    """
    Compute a single geometric metric for a single geometry.

    Args:
        metric: A geometric metric to compute.
        geometry: A shapely Polygon or MultiPolygon geometry.
        name: The name of the metric being computed.
        index: The index of the geometry in the original GeoDataFrame.

    Returns:
        The computed metric value as a float. If the metric raises a ValueError, NaN is returned and a warning is logged. Other Errors are raised as normal.
    """
    try:
        return metric(geometry)
    except ValueError as e:
        logger.warning(
            "Error computing metric %r for geometry at index %r: %s", name, index, e
        )
        return math.nan
