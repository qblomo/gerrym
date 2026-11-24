
import geopandas as gpd
import pytest
from shapely.geometry import box

from gerrymander.data.loader import EXPECTED_EPSG, load_districts


def test_load_districts_raises_if_crs_missing(write_shapefile):
    gdf = gpd.GeoDataFrame(geometry=[box(0, 0, 1, 1)], crs=None)
    shp = write_shapefile(gdf)
    with pytest.raises(ValueError, match="does not have a coordinate reference system"):
        load_districts(shp)


def test_load_districts_raises_if_crs_not_expected(write_shapefile):
    gdf = gpd.GeoDataFrame(geometry=[box(0, 0, 1, 1)], crs="EPSG:4326")
    shp = write_shapefile(gdf)
    with pytest.raises(ValueError, match="Expected CRS EPSG"):
        load_districts(shp)


def test_load_districts_happy_path(write_shapefile):
    gdf = gpd.GeoDataFrame(geometry=[box(0, 0, 1, 1)], crs=EXPECTED_EPSG)
    shp = write_shapefile(gdf)
    gdf = load_districts(shp)
    assert gdf.crs.to_epsg() == EXPECTED_EPSG
    assert len(gdf.index) == 1
