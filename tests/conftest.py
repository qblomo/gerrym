import geopandas as gpd
import pytest
from shapely import box


@pytest.fixture
def write_shapefile(tmp_path):
    def _write(gdf, name="districts.shp"):
        path = tmp_path / name
        gdf.to_file(path)
        return path

    return _write


@pytest.fixture
def us_states_gdf():
    return gpd.GeoDataFrame(
        {
            "STATEFP": ["15", "01", "02", "99", "06", "04"],
            "NAME": ["Hawaii", "Alabama", "Alaska", "Dummy", "Kalifornien", "Arizona"],
        },
        geometry=[
            box(-157.9, 21.3, -157.8, 21.4),  # 15 Hawaii (Honolulu)
            box(-86.3, 32.3, -86.2, 32.4),  # 01 Alabama (Montgomery)
            box(-150.0, 61.1, -149.9, 61.2),  # 02 Alaska (Anchorage)
            box(-1.0, -1.0, 1.0, 1.0),  # 99 Dummy state (not in CONTIGUOUS_STATE_FIPS)
            box(-121.5, 38.5, -121.4, 38.6),  # 06 Kalifornien (Sacramento)
            box(-112.1, 33.4, -112.0, 33.5),  # 04 Arizona (Phoenix)
        ],
        crs="EPSG:4269",
    )
