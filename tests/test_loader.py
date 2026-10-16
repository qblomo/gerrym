from gerrymander.data.loader import load_districts, EXPECTED_EPSG
import geopandas as gpd
import pytest
from shapely.geometry import box
from pathlib import Path


def _write_fake_districts(path: Path, crs: str | int | None) -> Path:
    gdf = gpd.GeoDataFrame(geometry=[box(0, 0, 1, 1)], crs=crs)
    gdf.to_file(path)
    return path

def test_load_districts_raises_if_crs_missing(tmp_path):
    shp = _write_fake_districts(tmp_path / "districts.shp", crs=None)
    with pytest.raises(ValueError, match="does not have a coordinate reference system"):
        load_districts(shp)

def test_load_districts_raises_if_crs_not_expected(tmp_path):
    shp = _write_fake_districts(tmp_path / "districts.shp", crs="EPSG:4326")
    with pytest.raises(ValueError, match="Expected CRS EPSG"):
        load_districts(shp)

def test_load_districts_happy_path(tmp_path):
    shp = _write_fake_districts(tmp_path / "districts.shp", crs=EXPECTED_EPSG)
    gdf = load_districts(shp)
    assert gdf.crs.to_epsg() == EXPECTED_EPSG
    assert len(gdf.index) == 1