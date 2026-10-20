import geopandas as gpd
import pandas as pd
import pytest
from geopandas.testing import assert_geodataframe_equal
from pyproj import Geod
from shapely import box

from gerrymander.data.projection import ANALYSIS_EPSG, project_to_analysis_crs

PROJECTED_AREA_TOLERANCE = 1e-5
# Tolerance for area comparison between geodetic and projected area calculations.
# Max. measured difference between geodetic (Geod, GRS80) and projected area (EPSG:5070)
# 0.1 deg squares: 2.7e-7

LOCATIONS = {
    "Maine": box(-69.0, 44.8, -68.9, 44.9),
    "Florida": box(-81.5, 28.4, -81.4, 28.5),
    "Nebraska": box(-100, 40, -99.9, 40.1),
}


@pytest.fixture
def us_districts_gdf():
    return gpd.GeoDataFrame(
        {"GEOID": ["3030", "0101", "2020"]},
        geometry=list(LOCATIONS.values()),
        crs="EPSG:4269",
        index=list(LOCATIONS),
    )


def test_project_to_analysis_crs_raises_if_crs_is_missing():
    gdf = gpd.GeoDataFrame(geometry=[box(-100, 40, -99.9, 40.1)], crs=None)
    with pytest.raises(ValueError, match="does not have a coordinate reference system"):
        project_to_analysis_crs(gdf)


def test_project_to_analysis_crs_sets_target_crs(us_districts_gdf):
    projected_gdf = project_to_analysis_crs(us_districts_gdf)
    assert projected_gdf.crs.to_epsg() == ANALYSIS_EPSG


@pytest.mark.parametrize("crs", ["EPSG:4269", "EPSG:4326", "EPSG:5070"])
@pytest.mark.parametrize("location", LOCATIONS.keys())
def test_project_to_analysis_crs_preserves_area(us_districts_gdf, location, crs):
    gdf = us_districts_gdf.to_crs(crs)
    projected_gdf = project_to_analysis_crs(gdf)
    geod = Geod(ellps="GRS80")
    reference_area, _ = geod.geometry_area_perimeter(LOCATIONS[location])
    assert projected_gdf.geometry.area.loc[location] == pytest.approx(
        abs(reference_area), rel=PROJECTED_AREA_TOLERANCE
    )


def test_project_to_analysis_crs_preserves_attributes_and_row_order(us_districts_gdf):
    projected_gdf = project_to_analysis_crs(us_districts_gdf)
    pd.testing.assert_frame_equal(
        us_districts_gdf.drop(columns="geometry"),
        projected_gdf.drop(columns="geometry"),
    )


def test_project_to_analysis_crs_does_not_modify_input(us_districts_gdf):
    original = us_districts_gdf.copy()
    project_to_analysis_crs(us_districts_gdf)
    assert_geodataframe_equal(us_districts_gdf, original)


def test_project_to_analysis_crs_with_other_crs(us_districts_gdf):
    gdf_4326 = us_districts_gdf.to_crs(epsg=4326)
    projected_gdf = project_to_analysis_crs(gdf_4326)
    assert projected_gdf.crs.to_epsg() == ANALYSIS_EPSG


def test_project_to_analysis_crs_with_empty_geodataframe():
    empty_gdf = gpd.GeoDataFrame(columns=["GEOID"], geometry=[], crs="EPSG:4269")
    projected_gdf = project_to_analysis_crs(empty_gdf)
    assert projected_gdf.crs.to_epsg() == ANALYSIS_EPSG
    assert list(projected_gdf.columns) == list(empty_gdf.columns)
    assert len(projected_gdf) == 0
