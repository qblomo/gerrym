import logging
import math

import geopandas as gpd
import pandas as pd
import pytest
from geopandas.testing import assert_geodataframe_equal
from shapely.geometry import MultiPolygon, Point, Polygon, box

from gerrymander.data.projection import ANALYSIS_EPSG
from gerrymander.metrics.registry import GEOMETRIC_METRICS
from gerrymander.pipeline.compute import compute_geometric_metrics, logger

CIRCLE = Point(0, 0).buffer(1.0)  # Circle with radius 1 centered at (0, 0)
SQUARE = box(0, 0, 1, 1)  # Square with corners at (0,0), (1,0), (1,1), (0,1)


@pytest.fixture
def geometries_gdf():
    return gpd.GeoDataFrame(
        {
            "name": ["square", "two_squares", "l_shape"],
        },
        geometry=[
            SQUARE,
            MultiPolygon([box(0, 0, 1, 1), box(0, 2, 1, 3)]),
            Polygon([(0, 0), (2, 0), (2, 1), (1, 1), (1, 2), (0, 2)]),
        ],
        crs=ANALYSIS_EPSG,
        index=["b", "c", "a"],
    )


@pytest.fixture
def expected_metrics_df(geometries_gdf):
    return pd.DataFrame(
        {
            "convex_hull_ratio": [
                1.0,  # square equals its convex hull
                2
                / 3,  # convex hull adds a square with area 1 to the two squares with area 2
                3
                / (
                    3 + 0.5
                ),  # convex hull adds a triangle with area 0.5 to the l-shape with area 3
            ],
            "reock": [
                2
                / math.pi,  # bounding circle has area pi * (sqrt(2)/2)^2 = pi/2, area of square is 1
                4
                / (
                    5 * math.pi
                ),  # bounding circle has area pi * (sqrt(10)/2)^2 = 5pi/2, area of two squares is 2
                3
                / (
                    2 * math.pi
                ),  # bounding circle has area pi * (sqrt(8)/2)^2 = 2pi, area of l-shape is 3
            ],
            "polsby_popper": [
                math.pi
                / 4,  # area of square is 1, perimeter is 4, polsby-popper = 4*pi*1/4^2 = pi/4
                math.pi
                / 8,  # area of two squares is 2, perimeter is 8, polsby-popper = 4*pi*2/8^2 = pi/8
                (3 * math.pi)
                / 16,  # area of l-shape is 3, perimeter is 8, polsby-popper = 4*pi*3/8^2 = 3pi/16
            ],
        },
        index=geometries_gdf.index,
    )


def dummy_metric(geometry: Polygon | MultiPolygon) -> float:
    if geometry.equals(SQUARE):
        raise ValueError("Dummy error for testing")
    if geometry.equals(CIRCLE):
        raise TypeError("Dummy error for testing")
    return 1.0


@pytest.fixture
def metrics_with_dummy():
    return {"dummy_metric": dummy_metric, **GEOMETRIC_METRICS}


def test_compute_geometric_metrics_for_index_output_equal_index_input(geometries_gdf):
    metrics_df = compute_geometric_metrics(geometries_gdf)
    assert metrics_df.index.equals(geometries_gdf.index)


def test_compute_geometric_metrics_for_output_column_names(geometries_gdf):
    metrics_df = compute_geometric_metrics(geometries_gdf)
    assert set(metrics_df.columns) == set(GEOMETRIC_METRICS.keys())


def test_compute_geometric_metrics_for_output_format(geometries_gdf):
    metrics_df = compute_geometric_metrics(geometries_gdf)
    assert isinstance(metrics_df, pd.DataFrame)
    assert len(metrics_df) == len(geometries_gdf)


def test_compute_geometric_metrics_for_known_shapes(
    geometries_gdf, expected_metrics_df
):
    metrics_df = compute_geometric_metrics(geometries_gdf)
    pd.testing.assert_frame_equal(metrics_df, expected_metrics_df, check_like=True)


def test_compute_geometric_metrics_with_empty_geodataframe():
    empty_gdf = gpd.GeoDataFrame(
        columns=["geometry"], geometry="geometry", crs=ANALYSIS_EPSG
    )
    metrics_df = compute_geometric_metrics(empty_gdf)
    assert metrics_df.empty
    assert set(metrics_df.columns) == set(GEOMETRIC_METRICS.keys())


def test_compute_geometric_metrics_with_empty_metrics_mapping(geometries_gdf):
    empty_metrics = {}
    metrics_df = compute_geometric_metrics(geometries_gdf, metrics=empty_metrics)
    assert list(metrics_df.columns) == []
    assert metrics_df.index.equals(geometries_gdf.index)


def test_compute_geometric_metrics_with_non_projected_geodataframe(geometries_gdf):
    non_projected_gdf = geometries_gdf.set_crs(
        "EPSG:4326", allow_override=True
    )  # Convert to a non-projected CRS (WGS84)
    with pytest.raises(ValueError, match="Input GeoDataFrame must be projected"):
        compute_geometric_metrics(non_projected_gdf)


def test_compute_geometric_metrics_with_no_crs(geometries_gdf):
    no_crs_gdf = geometries_gdf.set_crs(None, allow_override=True)
    assert no_crs_gdf.crs is None
    with pytest.raises(ValueError, match="Input GeoDataFrame must have crs defined"):
        compute_geometric_metrics(no_crs_gdf)


def test_compute_geometric_metrics_with_metric_raising_error(
    geometries_gdf, metrics_with_dummy, expected_metrics_df
):
    metrics_df = compute_geometric_metrics(geometries_gdf, metrics=metrics_with_dummy)
    assert pd.isna(
        metrics_df.loc["b", "dummy_metric"]
    )  # The square geometry raises an error
    assert (
        metrics_df.loc["c", "dummy_metric"] == 1.0
    )  # The two squares geometry does not raise an error
    assert (
        metrics_df.loc["a", "dummy_metric"] == 1.0
    )  # The l-shape geometry does not raise an error
    pd.testing.assert_frame_equal(
        metrics_df.drop(columns="dummy_metric"), expected_metrics_df, check_like=True
    )  # Other metrics are unaffected


def test_compute_geometric_metrics_leaves_original_geodataframe_unchanged(
    geometries_gdf,
):
    original_gdf_copy = geometries_gdf.copy()
    compute_geometric_metrics(geometries_gdf)
    assert_geodataframe_equal(geometries_gdf, original_gdf_copy)


def test_compute_geometric_metrics_leaves_metrics_mapping_unchanged(
    geometries_gdf, metrics_with_dummy
):
    original_metrics_copy = metrics_with_dummy.copy()
    compute_geometric_metrics(geometries_gdf, metrics=metrics_with_dummy)
    assert metrics_with_dummy == original_metrics_copy


def test_compute_geometric_metrics_logs_warning_for_failing_metric(
    geometries_gdf, metrics_with_dummy, caplog
):
    caplog.set_level(logging.WARNING, logger=logger.name)
    compute_geometric_metrics(geometries_gdf, metrics=metrics_with_dummy)
    records = [r for r in caplog.records if r.name == logger.name]
    assert len(records) == 1
    assert records[0].levelno == logging.WARNING
    assert "dummy_metric" in records[0].getMessage()
    assert (
        records[0]
        .getMessage()
        .startswith("Error computing metric 'dummy_metric' for geometry at index 'b':")
    )


def test_compute_geometric_metrics_logs_no_warning_for_successful_metrics(
    geometries_gdf, caplog
):
    caplog.set_level(logging.WARNING, logger=logger.name)
    compute_geometric_metrics(geometries_gdf)
    records = [r for r in caplog.records if r.name == logger.name]
    assert len(records) == 0  # No warnings should be logged for successful metrics


def test_compute_geometric_metrics_with_metric_raising_non_value_error(
    metrics_with_dummy,
):
    geometries_with_circle_gdf = gpd.GeoDataFrame(
        {
            "name": ["circle"],
        },
        geometry=[CIRCLE],
        crs=ANALYSIS_EPSG,
    )
    with pytest.raises(TypeError, match="Dummy error for testing"):
        compute_geometric_metrics(
            geometries_with_circle_gdf, metrics=metrics_with_dummy
        )


def test_compute_geometric_metrics_with_empty_geometry():
    empty_geom_gdf = gpd.GeoDataFrame(
        {
            "name": ["empty"],
        },
        geometry=[Polygon()],  # Create an empty geometry
        crs=ANALYSIS_EPSG,
    )
    metrics_df = compute_geometric_metrics(empty_geom_gdf)
    assert len(metrics_df) == 1
    assert metrics_df.isna().all(axis=None)


def test_compute_geometric_metrics_with_nan_geometry():
    nan_geom_gdf = gpd.GeoDataFrame(
        {
            "name": ["nan"],
        },
        geometry=[None],  # Create a NaN geometry
        crs=ANALYSIS_EPSG,
    )
    with pytest.raises(ValueError, match="Input GeoDataFrame contains NaN geometries"):
        compute_geometric_metrics(nan_geom_gdf)


def compute_geometric_metrics_with_non_polygon_geometry():
    non_polygon_geom_gdf = gpd.GeoDataFrame(
        {
            "name": ["point"],
        },
        geometry=[Point(0, 0)],  # Create a Point geometry
        crs=ANALYSIS_EPSG,
    )
    with pytest.raises(
        ValueError, match="All geometries have to be of type Polygon or MultiPolygon"
    ):
        compute_geometric_metrics(non_polygon_geom_gdf)


def compute_geometric_metrics_with_mixed_geometry_types():
    mixed_geom_gdf = gpd.GeoDataFrame(
        {
            "name": ["square", "point"],
        },
        geometry=[SQUARE, Point(0, 0)],  # Create a mix of Polygon and Point geometries
        crs=ANALYSIS_EPSG,
    )
    with pytest.raises(
        ValueError, match="All geometries have to be of type Polygon or MultiPolygon"
    ):
        compute_geometric_metrics(mixed_geom_gdf)
