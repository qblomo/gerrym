from collections.abc import Mapping
from pathlib import Path

import geopandas as gpd

from gerrymander.data.filter import filter_contiguous_states
from gerrymander.data.loader import load_districts
from gerrymander.data.projection import project_to_analysis_crs
from gerrymander.metrics.registry import GEOMETRIC_METRICS, GeometricMetric
from gerrymander.pipeline.compute import compute_geometric_metrics


def build_district_metrics(
    path: Path, metrics: Mapping[str, GeometricMetric] = GEOMETRIC_METRICS
) -> gpd.GeoDataFrame:
    """
    Build a GeoDataFrame that contains district geometries in the ANALYSIS_EPSG
    projection and their corresponding geometric metrics. Geometries are filtered
    to contiguous US states. Errors are raised according to the called functions
    load_districts, filter_contiguous_states, project_to_analysis_crs, and
    compute_geometric_metrics.

    Args:
        path: Path to a shape file that contains US district geometries.
        metrics: A mapping of metrics to be calculated. Defaults to GEOMETRIC_METRICS
        which includes all metrics from the registry.

    Returns:
        A GeoDataFrame containing the geometries projected to ANALYSIS_EPSG and
        calculated metrics as new columns with one column per key of metrics.
        Index and order of rows and columns from the the filtered input GeoDataFrame
        are preserved with the metric columns added after.
    """
    gdf = load_districts(path)
    gdf = filter_contiguous_states(gdf)
    gdf = project_to_analysis_crs(gdf)
    overlap = set(gdf.columns) & set(metrics)
    if overlap:
        raise ValueError(
            f"Input GeoDataFrame contains columns that overlap with the metrics mapping: {sorted(overlap)}"
        )
    metrics_df = compute_geometric_metrics(gdf, metrics)
    return gdf.join(metrics_df)
