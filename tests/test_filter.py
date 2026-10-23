import geopandas as gpd
import pytest
from geopandas.testing import assert_geodataframe_equal
from shapely.geometry import box

from gerrymander.data.filter import (
    CONTIGUOUS_STATE_FIPS_CODES,
    filter_contiguous_states,
)


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


@pytest.fixture
def reference_gdf():
    return gpd.GeoDataFrame(
        {"STATEFP": ["01", "06", "04"], "NAME": ["Alabama", "Kalifornien", "Arizona"]},
        geometry=[
            box(-86.3, 32.3, -86.2, 32.4),  # 01 Alabama (Montgomery)
            box(-121.5, 38.5, -121.4, 38.6),  # 06 Kalifornien (Sacramento)
            box(-112.1, 33.4, -112.0, 33.5),  # 04 Arizona (Phoenix)
        ],
        crs="EPSG:4269",
        index=[1, 4, 5],
    )


def test_filter_contiguous_does_not_modify_input(us_states_gdf):
    original_gdf = us_states_gdf.copy()
    _ = filter_contiguous_states(us_states_gdf, state_col="STATEFP")
    assert_geodataframe_equal(original_gdf, us_states_gdf)


def test_filter_contiguous_states_leaves_other_columns_and_rows_intact(
    us_states_gdf, reference_gdf
):
    filtered_gdf = filter_contiguous_states(us_states_gdf, state_col="STATEFP")
    assert_geodataframe_equal(filtered_gdf, reference_gdf)


def test_filter_contiguous_states_raises_if_state_col_missing(us_states_gdf):
    removed_col_gdf = us_states_gdf.drop(columns="STATEFP")
    with pytest.raises(
        ValueError, match="Column 'STATEFP' not found in the GeoDataFrame"
    ):
        filter_contiguous_states(removed_col_gdf, state_col="STATEFP")


def test_filter_contiguous_states_warns_if_empty():
    empty_gdf = gpd.GeoDataFrame(
        {"STATEFP": ["15", "02", "99"], "NAME": ["Hawaii", "Alaska", "Dummy"]},
        geometry=[
            box(-157.9, 21.3, -157.8, 21.4),  # 15 Hawaii (Honolulu)
            box(-150.0, 61.1, -149.9, 61.2),  # 02 Alaska (Anchorage)
            box(-1.0, -1.0, 1.0, 1.0),  # 99 Dummy state (not in WHITE_LIST)
        ],
        crs="EPSG:4269",
    )
    with pytest.warns(UserWarning, match="The filtered GeoDataFrame is empty"):
        filter_contiguous_states(empty_gdf, state_col="STATEFP")


def test_filter_contiguous_states_with_non_default_colum(us_states_gdf, reference_gdf):
    renamed_column = us_states_gdf.rename(columns={"STATEFP": "NEW_NAME"})
    renamed_reference = reference_gdf.rename(columns={"STATEFP": "NEW_NAME"})
    filtered_gdf = filter_contiguous_states(renamed_column, state_col="NEW_NAME")
    assert_geodataframe_equal(filtered_gdf, renamed_reference)


def test_contiguous_state_fips_codes_content_length():
    assert len(CONTIGUOUS_STATE_FIPS_CODES) == 48


def test_contiguous_state_fips_codes_does_not_contain_not_contiguous():
    not_contiguous = {"02", "11", "15"}
    assert not_contiguous.isdisjoint(CONTIGUOUS_STATE_FIPS_CODES)


def test_contiguous_state_fips_codes_content():
    assert all(
        isinstance(v, str) and len(v) == 2 and v.isdigit() and int(v) <= 60
        for v in CONTIGUOUS_STATE_FIPS_CODES
    )
