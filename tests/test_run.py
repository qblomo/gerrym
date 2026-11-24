
import geopandas as gpd
import pandas as pd
import pytest

from gerrymander.data.projection import ANALYSIS_EPSG
from gerrymander.metrics.registry import GEOMETRIC_METRICS
from gerrymander.pipeline.run import build_district_metrics


def test_build_district_metrics_for_output_structure(us_states_gdf, write_shapefile):
    shp = write_shapefile(us_states_gdf)
    result = build_district_metrics(shp)
    assert isinstance(result, gpd.GeoDataFrame)
    assert result.crs.to_epsg() == ANALYSIS_EPSG
    expected = set(us_states_gdf.columns) | set(GEOMETRIC_METRICS)
    assert set(result.columns) == expected
    expected_codes = {"01", "04", "06"}  # Alabama, Arizona, California
    expected_index = us_states_gdf.index[us_states_gdf["STATEFP"].isin(expected_codes)]
    pd.testing.assert_index_equal(result.index, expected_index)


def test_build_district_metrics_raises_for_overlapping_columns(
    us_states_gdf, write_shapefile
):
    us_states_gdf["reock"] = 0.5
    shp = write_shapefile(us_states_gdf)
    with pytest.raises(
        ValueError, match="contains columns that overlap with the metrics mapping"
    ):
        build_district_metrics(shp)


def test_build_district_metrics_raises_for_no_crs(us_states_gdf, write_shapefile):
    us_states_gdf = us_states_gdf.set_crs(None, allow_override=True)
    shp = write_shapefile(us_states_gdf)
    with pytest.raises(ValueError, match="does not have a coordinate reference system"):
        build_district_metrics(shp)


def test_build_district_metrics_raises_for_wrong_crs(us_states_gdf, write_shapefile):
    us_states_gdf = us_states_gdf.to_crs(epsg=4326)  # Non-projected CRS
    shp = write_shapefile(us_states_gdf)
    with pytest.raises(ValueError, match="Expected CRS EPSG:"):
        build_district_metrics(shp)


def test_build_district_metrics_raises_for_missing_state_col(
    us_states_gdf, write_shapefile
):
    us_states_gdf = us_states_gdf.drop(columns="STATEFP")
    shp = write_shapefile(us_states_gdf)
    with pytest.raises(ValueError, match="Column 'STATEFP' not found"):
        build_district_metrics(shp)
