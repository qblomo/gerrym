import warnings

import geopandas as gpd

# FIPS codes for 48 contiguous states, excluding Alaska, Hawaii and DC
CONTIGUOUS_STATE_FIPS = {
    "Alabama": "01",
    "Arizona": "04",
    "Arkansas": "05",
    "California": "06",
    "Colorado": "08",
    "Connecticut": "09",
    "Delaware": "10",
    "Florida": "12",
    "Georgia": "13",
    "Idaho": "16",
    "Illinois": "17",
    "Indiana": "18",
    "Iowa": "19",
    "Kansas": "20",
    "Kentucky": "21",
    "Louisiana": "22",
    "Maine": "23",
    "Maryland": "24",
    "Massachusetts": "25",
    "Michigan": "26",
    "Minnesota": "27",
    "Mississippi": "28",
    "Missouri": "29",
    "Montana": "30",
    "Nebraska": "31",
    "Nevada": "32",
    "New Hampshire": "33",
    "New Jersey": "34",
    "New Mexico": "35",
    "New York": "36",
    "North Carolina": "37",
    "North Dakota": "38",
    "Ohio": "39",
    "Oklahoma": "40",
    "Oregon": "41",
    "Pennsylvania": "42",
    "Rhode Island": "44",
    "South Carolina": "45",
    "South Dakota": "46",
    "Tennessee": "47",
    "Texas": "48",
    "Utah": "49",
    "Vermont": "50",
    "Virginia": "51",
    "Washington": "53",
    "West Virginia": "54",
    "Wisconsin": "55",
    "Wyoming": "56",
}
CONTIGUOUS_STATE_FIPS_CODES = frozenset(CONTIGUOUS_STATE_FIPS.values())


def filter_contiguous_states(
    gdf: gpd.GeoDataFrame, state_col: str = "STATEFP"
) -> gpd.GeoDataFrame:
    """
    Filter a GeoDataFrame to include only the states from CONTIGUOUS_STATE_FIPS.

    The index, order and other columns remain unchanged.

    Args:
        gdf: GeoDataFrame containing a column with state FIPS codes.
        state_col: Name of the column in gdf that contains state FIPS codes as a string with leading zero.

    Returns:
        A GeoDataFrame filtered to include only rows corresponding to the 48 contiguous states.

    Raises:
        ValueError: If the specified state_col does not exist in the GeoDataFrame.

    Warns:
        If no rows remain after filtering (or the GeoDataFrame is empty to begin with).
    """
    if state_col not in gdf.columns:
        raise ValueError(f"Column '{state_col}' not found in the GeoDataFrame.")
    filtered_gdf = gdf[gdf[state_col].isin(CONTIGUOUS_STATE_FIPS_CODES)]
    if filtered_gdf.empty:
        warnings.warn(
            "The filtered GeoDataFrame is empty",
            UserWarning,
            stacklevel=2,
        )
    return filtered_gdf
